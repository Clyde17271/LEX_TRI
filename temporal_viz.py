"""
Temporal Visualization Module for LEX_TRI

This module provides functions to visualize Valid Time (VT), Transaction Time (TT),
and Decision Time (DT) timelines for debugging and analysis purposes.
"""

from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple, Union
import os

# Import visualization libraries conditionally
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Import Rich Console
try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


def safe_print(message: str, style: str = "") -> None:
    """Print message using Rich console if available, otherwise use standard print."""
    if console:
        if style:
            console.print(f"[{style}]{message}[/{style}]")
        else:
            console.print(message)
    else:
        print(message)

class TemporalPoint:
    """Represents a point in tri-temporal time."""
    
    def __init__(
        self,
        valid_time: datetime,
        transaction_time: datetime,
        decision_time: Optional[datetime] = None,
        event_data: Optional[Dict] = None,
        event_id: Optional[str] = None
    ):
        self.valid_time = valid_time
        self.transaction_time = transaction_time
        self.decision_time = decision_time
        self.event_data = event_data or {}
        self.event_id = event_id or f"evt_{valid_time.timestamp()}"
    
    def __repr__(self) -> str:
        return (
            f"TemporalPoint(vt={self.valid_time.isoformat()}, "
            f"tt={self.transaction_time.isoformat()}, "
            f"dt={self.decision_time.isoformat() if self.decision_time else 'None'})"
        )
    
    def to_dict(self) -> Dict:
        """Convert TemporalPoint to dictionary."""
        return {
            "event_id": self.event_id,
            "valid_time": self.valid_time.isoformat(),
            "transaction_time": self.transaction_time.isoformat(),
            "decision_time": self.decision_time.isoformat() if self.decision_time else None,
            "data": self.event_data
        }


class TemporalTimeline:
    """Manages a collection of temporal points for visualization and analysis."""
    
    def __init__(self, name: str = "Unnamed Timeline"):
        self.name = name
        self.points: List[TemporalPoint] = []
    
    def add_point(self, point: TemporalPoint) -> None:
        """Add a temporal point to the timeline."""
        self.points.append(point)
    
    def save_to_json(self, filepath: str) -> None:
        """Save timeline to JSON file."""
        data = {
            "name": self.name,
            "points": [point.to_dict() for point in self.points],
            "metadata": {
                "created": datetime.now().isoformat(),
                "point_count": len(self.points)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"Timeline saved to {filepath}") if console else print(f"Timeline saved to {filepath}")
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'TemporalTimeline':
        """Load timeline from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        timeline = cls(name=data.get("name", "Loaded Timeline"))
        
        for point_data in data.get("points", []):
            point = TemporalPoint(
                valid_time=datetime.fromisoformat(point_data["valid_time"]),
                transaction_time=datetime.fromisoformat(point_data["transaction_time"]),
                decision_time=datetime.fromisoformat(point_data["decision_time"]) 
                    if point_data.get("decision_time") else None,
                event_data=point_data.get("data", {}),
                event_id=point_data.get("event_id")
            )
            timeline.add_point(point)
        
        return timeline
    
    def analyze_anomalies(self) -> List[Dict]:
        """Analyze timeline for temporal anomalies."""
        anomalies = []
        
        # Sort points by valid time for analysis
        sorted_points = sorted(self.points, key=lambda p: p.valid_time)
        
        for i, point in enumerate(sorted_points):
            # Check for transaction time before valid time (impossible in normal flow)
            if point.transaction_time < point.valid_time:
                anomalies.append({
                    "type": "time_travel",
                    "description": f"Transaction time precedes valid time for event {point.event_id}",
                    "severity": "critical",
                    "point": point.to_dict()
                })
            
            # Check for decision time before transaction time (premature decision)
            if point.decision_time and point.decision_time < point.transaction_time:
                anomalies.append({
                    "type": "premature_decision",
                    "description": f"Decision made before transaction recorded for event {point.event_id}",
                    "severity": "high",
                    "point": point.to_dict()
                })
            
            # Check for large gaps between valid and transaction time (lag)
            vt_tt_diff = (point.transaction_time - point.valid_time).total_seconds()
            if vt_tt_diff > 60:  # More than 1 minute lag
                anomalies.append({
                    "type": "ingestion_lag",
                    "description": f"Lag of {vt_tt_diff:.2f} seconds between valid and transaction time",
                    "severity": "medium" if vt_tt_diff < 300 else "high",
                    "point": point.to_dict()
                })
            
            # Check for out-of-order processing
            if i > 0:
                prev_point = sorted_points[i-1]
                if point.valid_time > prev_point.valid_time and point.transaction_time < prev_point.transaction_time:
                    anomalies.append({
                        "type": "out_of_order",
                        "description": f"Events processed out of order: {prev_point.event_id} and {point.event_id}",
                        "severity": "high",
                        "points": [prev_point.to_dict(), point.to_dict()]
                    })
        
        return anomalies


def visualize_timeline(
    timeline: TemporalTimeline,
    output_path: Optional[str] = None,
    show_plot: bool = True,
    highlight_anomalies: bool = True
) -> Optional[str]:
    """
    Visualize a temporal timeline with VT, TT, and DT points.
    
    Args:
        timeline: The TemporalTimeline to visualize
        output_path: Optional path to save the visualization
        show_plot: Whether to display the plot interactively
        highlight_anomalies: Whether to highlight detected anomalies
        
    Returns:
        Path to saved visualization file if output_path is provided
    """
    if not HAS_MATPLOTLIB:
        print("Matplotlib is required for visualization. Install with 'pip install matplotlib'") if not console else console.print("[yellow]Matplotlib is required for visualization. Install with 'pip install matplotlib'[/yellow]")
        return None
    
    if not timeline.points:
        print("Timeline contains no points to visualize") if not console else console.print("[yellow]Timeline contains no points to visualize[/yellow]")
        return None
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort points by valid time
    sorted_points = sorted(timeline.points, key=lambda p: p.valid_time)
    
    # Extract times for plotting
    valid_times = [p.valid_time for p in sorted_points]
    transaction_times = [p.transaction_time for p in sorted_points]
    decision_times = [p.decision_time for p in sorted_points if p.decision_time]
    
    # Event IDs for labels
    event_ids = [p.event_id for p in sorted_points]
    
    # Plot VT timeline (reference time)
    ax.plot(valid_times, range(len(valid_times)), 'bo-', label='Valid Time (VT)')
    
    # Plot TT timeline
    ax.plot(transaction_times, range(len(transaction_times)), 'ro-', label='Transaction Time (TT)')
    
    # Plot DT timeline if available
    if decision_times:
        # Need to match decision times with original indices
        dt_indices = [i for i, p in enumerate(sorted_points) if p.decision_time]
        ax.plot([sorted_points[i].decision_time for i in dt_indices], dt_indices, 'go-', label='Decision Time (DT)')
    
    # Highlight anomalies if requested
    if highlight_anomalies:
        anomalies = timeline.analyze_anomalies()
        for anomaly in anomalies:
            if anomaly["type"] == "time_travel":
                # Find index of the anomalous point
                event_id = anomaly["point"]["event_id"]
                if event_id in event_ids:
                    idx = event_ids.index(event_id)
                    ax.plot(valid_times[idx], idx, 'r*', markersize=15, 
                            label='Time Travel Anomaly' if 'Time Travel' not in [l.get_label() for l in ax.get_lines()] else "")
            
            elif anomaly["type"] == "premature_decision":
                event_id = anomaly["point"]["event_id"]
                if event_id in event_ids:
                    idx = event_ids.index(event_id)
                    ax.plot(sorted_points[idx].decision_time, idx, 'y*', markersize=15,
                            label='Premature Decision' if 'Premature Decision' not in [l.get_label() for l in ax.get_lines()] else "")
    
    # Format the plot
    ax.set_yticks(range(len(sorted_points)))
    ax.set_yticklabels([p.event_id for p in sorted_points])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    
    plt.title(f"Temporal Timeline: {timeline.name}")
    plt.xlabel("Time")
    plt.ylabel("Event")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    # Save if output path is provided
    if output_path:
        # Make sure directory exists, handle case where dirname returns empty string
        output_dir = os.path.dirname(output_path)
        if output_dir:  # If there's a directory component
            os.makedirs(output_dir, exist_ok=True)
            
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_path}") if not console else console.print(f"[green]Visualization saved to {output_path}[/green]")
    
    # Show if requested
    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    
    return output_path if output_path else None


def generate_example_timeline() -> TemporalTimeline:
    """Generate an example timeline for demonstration purposes."""
    from datetime import timedelta
    
    now = datetime.now()
    timeline = TemporalTimeline(name="Example Timeline")
    
    # Normal events
    for i in range(5):
        vt = now + timedelta(minutes=i*10)
        tt = vt + timedelta(seconds=30)  # Small lag
        dt = tt + timedelta(seconds=15)  # Decision shortly after
        
        timeline.add_point(TemporalPoint(
            valid_time=vt,
            transaction_time=tt,
            decision_time=dt,
            event_data={"status": "normal", "value": i*100},
            event_id=f"evt_{i+1}"
        ))
    
    # Add an anomaly - transaction time before valid time (time travel)
    timeline.add_point(TemporalPoint(
        valid_time=now + timedelta(minutes=60),
        transaction_time=now + timedelta(minutes=55),  # TT before VT
        decision_time=now + timedelta(minutes=65),
        event_data={"status": "anomaly", "type": "time_travel"},
        event_id="evt_anomaly_1"
    ))
    
    # Add an anomaly - decision before transaction (premature decision)
    timeline.add_point(TemporalPoint(
        valid_time=now + timedelta(minutes=70),
        transaction_time=now + timedelta(minutes=80),
        decision_time=now + timedelta(minutes=75),  # DT before TT
        event_data={"status": "anomaly", "type": "premature_decision"},
        event_id="evt_anomaly_2"
    ))
    
    # Add an anomaly - large lag
    timeline.add_point(TemporalPoint(
        valid_time=now + timedelta(minutes=90),
        transaction_time=now + timedelta(minutes=95, seconds=30),  # 5.5 minute lag
        decision_time=now + timedelta(minutes=96),
        event_data={"status": "anomaly", "type": "large_lag"},
        event_id="evt_anomaly_3"
    ))
    
    return timeline


if __name__ == "__main__":
    # Generate an example timeline
    example_timeline = generate_example_timeline()
    
    # Save to JSON
    example_timeline.save_to_json("example_timeline.json")
    
    # Visualize
    if HAS_MATPLOTLIB:
        visualize_timeline(example_timeline, "example_visualization.png")
        print("Example visualization created!") if not console else console.print("[green]Example visualization created![/green]")
    else:
        print("Matplotlib is required for visualization.") if not console else console.print("[yellow]Matplotlib is required for visualization.[/yellow]")
    
    # Analyze anomalies
    anomalies = example_timeline.analyze_anomalies()
    print(f"Detected {len(anomalies)} anomalies:") if not console else console.print(f"[bold]Detected {len(anomalies)} anomalies:[/bold]")
    for anomaly in anomalies:
        msg = f"{anomaly['type'].upper()}: {anomaly['description']} (Severity: {anomaly['severity']})"
        print(msg) if not console else console.print(f"[red]{anomaly['type'].upper()}[/red]: {anomaly['description']} (Severity: {anomaly['severity']})")