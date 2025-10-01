"""
Exo Integration Module for LEX TRI Temporal Visualization

This module provides integration between the LEX TRI Temporal Agent and Exo platform,
allowing visualization and analysis of temporal data within Exo's observability framework.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import Exo SDK components (placeholder - replace with actual imports)
try:
    from exo.platform import ObservabilityInterface, EventStream, TimelineVisualization
    from exo.temporal import TemporalEvent, EventContext
    HAS_EXO = True
except ImportError:
    HAS_EXO = False
    # Create stub classes for development without Exo
    class ObservabilityInterface:
        def __init__(self): pass
        def register_visualization(self, *args, **kwargs): pass
    
    class EventStream:
        def __init__(self): pass
        def publish_event(self, *args, **kwargs): pass
    
    class TimelineVisualization:
        def __init__(self): pass
        def render(self, *args, **kwargs): return {}

    class TemporalEvent:
        def __init__(self): pass
    
    class EventContext:
        def __init__(self): pass

# Import LEX TRI components
from temporal_viz import TemporalPoint, TemporalTimeline, visualize_timeline

class ExoTemporalAdapter:
    """Adapter class to integrate LEX TRI's temporal visualization with Exo platform."""
    
    def __init__(self, exo_interface: Optional[ObservabilityInterface] = None, config: Optional[Dict] = None):
        """
        Initialize the adapter with an optional Exo interface and configuration.
        
        Args:
            exo_interface: Optional pre-configured Exo interface
            config: Dictionary containing Exo configuration parameters:
                - api_key: API key for authentication
                - project: Project ID or name
                - timeline_name: Name for the timeline in Exo
                - publish_anomalies: Whether to publish anomalies to event stream
        """
        # Store configuration
        self.config = config or {}
        
        # Initialize Exo interface
        if exo_interface:
            self.exo = exo_interface
        elif HAS_EXO:
            # Create interface with API key if provided
            api_key = self.config.get("api_key")
            project = self.config.get("project")
            self.exo = ObservabilityInterface(api_key=api_key, project=project)
        else:
            self.exo = ObservabilityInterface()
            
        # Initialize event stream
        self.event_stream = EventStream()
        
        # Register visualizations with Exo
        if HAS_EXO:
            self.register_visualizations()
    
    def register_visualizations(self) -> None:
        """Register LEX TRI visualizations with Exo platform."""
        self.exo.register_visualization(
            name="tri_temporal_timeline",
            description="Tri-temporal (VT/TT/DT) timeline visualization",
            renderer=self.render_temporal_timeline,
            supported_types=["temporal_event", "anomaly_detection"]
        )
    
    def exo_event_to_temporal_point(self, event: Any) -> TemporalPoint:
        """Convert an Exo event to a LEX TRI TemporalPoint."""
        # Extract timestamps from Exo event
        # This implementation will vary based on Exo's actual event structure
        valid_time = datetime.fromisoformat(event.valid_time) if hasattr(event, 'valid_time') else datetime.now()
        transaction_time = datetime.fromisoformat(event.transaction_time) if hasattr(event, 'transaction_time') else datetime.now()
        decision_time = None
        if hasattr(event, 'decision_time') and event.decision_time:
            decision_time = datetime.fromisoformat(event.decision_time)
        
        # Extract event data
        event_data = event.data if hasattr(event, 'data') else {}
        event_id = event.id if hasattr(event, 'id') else f"evt_{valid_time.timestamp()}"
        
        # Create TemporalPoint
        return TemporalPoint(
            valid_time=valid_time,
            transaction_time=transaction_time,
            decision_time=decision_time,
            event_data=event_data,
            event_id=event_id
        )
    
    def temporal_point_to_exo_event(self, point: TemporalPoint) -> Dict:
        """Convert a LEX TRI TemporalPoint to an Exo event structure."""
        event = {
            "id": point.event_id,
            "valid_time": point.valid_time.isoformat(),
            "transaction_time": point.transaction_time.isoformat(),
            "data": point.event_data,
            "type": "temporal_event"
        }
        
        if point.decision_time:
            event["decision_time"] = point.decision_time.isoformat()
        
        return event
    
    def create_timeline_from_exo_events(self, events: List[Any], name: str = "Exo Timeline") -> TemporalTimeline:
        """Create a LEX TRI TemporalTimeline from Exo events."""
        timeline = TemporalTimeline(name=name)
        
        for event in events:
            point = self.exo_event_to_temporal_point(event)
            timeline.add_point(point)
        
        return timeline
    
    def publish_anomalies_to_exo(self, anomalies: List[Dict], timeline_name: str) -> None:
        """Publish detected anomalies to Exo event stream."""
        if not HAS_EXO:
            print("Exo integration not available. Anomalies not published.")
            return
        
        for anomaly in anomalies:
            # Create event context
            context = EventContext(
                source="lextri.temporal_viz",
                severity=anomaly["severity"],
                category="temporal_anomaly",
                timeline=timeline_name
            )
            
            # Create and publish event
            event = {
                "type": f"anomaly.{anomaly['type']}",
                "description": anomaly["description"],
                "point_id": anomaly.get("point", {}).get("event_id", "unknown"),
                "detected_at": datetime.now().isoformat(),
                "metadata": {
                    "anomaly_type": anomaly["type"],
                    "severity": anomaly["severity"]
                }
            }
            
            self.event_stream.publish_event(event, context)
    
    def publish_timeline(self, timeline: TemporalTimeline) -> Dict:
        """
        Publish a LEX TRI timeline to Exo platform.
        
        This method sends the timeline data to Exo, creates a visualization,
        and optionally publishes detected anomalies to the event stream.
        
        Args:
            timeline: The TemporalTimeline to publish
            
        Returns:
            Dictionary with results of the publish operation
        """
        if not HAS_EXO:
            return {"error": "Exo integration not available"}
        
        try:
            # Extract configuration
            timeline_name = self.config.get("timeline_name", timeline.name)
            publish_anomalies = self.config.get("publish_anomalies", True)
            
            # Convert timeline points to Exo events
            exo_events = [self.temporal_point_to_exo_event(p) for p in timeline.points]
            
            # Register timeline in Exo
            timeline_id = self.exo.register_timeline(
                name=timeline_name,
                description=f"LEX TRI temporal timeline with {len(timeline.points)} points",
                source="lextri.temporal_viz",
                metadata={
                    "point_count": len(timeline.points),
                    "created": datetime.now().isoformat(),
                    "source": "lex_tri_agent"
                }
            )
            
            # Publish events to timeline
            for event in exo_events:
                self.exo.add_event_to_timeline(timeline_id, event)
            
            # Analyze anomalies
            anomalies = timeline.analyze_anomalies()
            
            # Publish anomalies if enabled
            if publish_anomalies and anomalies:
                self.publish_anomalies_to_exo(anomalies, timeline_name)
            
            # Generate dashboard URL
            dashboard_url = None
            if hasattr(self.exo, 'get_timeline_dashboard_url'):
                dashboard_url = self.exo.get_timeline_dashboard_url(timeline_id)
            
            # Return result
            return {
                "timeline_id": timeline_id,
                "timeline_name": timeline_name,
                "point_count": len(timeline.points),
                "anomaly_count": len(anomalies),
                "dashboard_url": dashboard_url
            }
        
        except Exception as e:
            import traceback
            print(f"Error publishing timeline to Exo: {str(e)}")
            print(traceback.format_exc())
            return {"error": str(e)}

    def render_temporal_timeline(self, data: Dict, config: Dict) -> Dict:
        """
        Render temporal timeline visualization for Exo.
        
        This function adapts LEX TRI's visualization to Exo's visualization format.
        """
        # Extract events from data
        events = data.get("events", [])
        
        # Create timeline
        timeline_name = config.get("name", "Temporal Timeline")
        timeline = self.create_timeline_from_exo_events(events, name=timeline_name)
        
        # Analyze anomalies
        anomalies = timeline.analyze_anomalies()
        
        # Publish anomalies if enabled
        if config.get("publish_anomalies", True):
            self.publish_anomalies_to_exo(anomalies, timeline_name)
        
        # Generate visualization
        # For Exo integration, we generate both image and structured data
        output_path = config.get("output_path")
        if output_path:
            visualize_timeline(
                timeline,
                output_path=output_path,
                show_plot=False,
                highlight_anomalies=config.get("highlight_anomalies", True)
            )
        
        # Return structured data for Exo's visualization system
        return {
            "timeline_name": timeline_name,
            "points_count": len(timeline.points),
            "time_range": {
                "start": min(p.valid_time for p in timeline.points).isoformat() if timeline.points else None,
                "end": max(p.valid_time for p in timeline.points).isoformat() if timeline.points else None
            },
            "anomalies": anomalies,
            "visualization_path": output_path if output_path else None,
            "events": [self.temporal_point_to_exo_event(p) for p in timeline.points]
        }


# Example usage
if __name__ == "__main__":
    # This is a demonstration of how to use the adapter
    # In a real implementation, Exo would instantiate and use this adapter
    
    adapter = ExoTemporalAdapter()
    
    # Example of creating a timeline from Exo events
    # In real usage, these would come from Exo's event system
    class MockExoEvent:
        def __init__(self, vt, tt, dt=None, data=None, event_id=None):
            self.valid_time = vt
            self.transaction_time = tt
            self.decision_time = dt
            self.data = data or {}
            self.id = event_id
    
    # Create some mock events
    now = datetime.now().isoformat()
    events = [
        MockExoEvent(now, now, data={"status": "normal"}, event_id="evt_1"),
        MockExoEvent(
            (datetime.now().replace(minute=datetime.now().minute + 5)).isoformat(), 
            now, 
            data={"status": "anomaly"}, 
            event_id="evt_2"
        )
    ]
    
    # Create timeline
    timeline = adapter.create_timeline_from_exo_events(events, "Mock Exo Timeline")
    
    # Analyze and output
    anomalies = timeline.analyze_anomalies()
    print(f"Detected {len(anomalies)} anomalies")
    for anomaly in anomalies:
        print(f"- {anomaly['type']}: {anomaly['description']} (Severity: {anomaly['severity']})")
    
    # Example of rendering
    result = adapter.render_temporal_timeline(
        {"events": events}, 
        {"name": "Test Timeline", "output_path": "exo_integration_test.png"}
    )
    
    print("\nVisualization result:")
    print(json.dumps(result, indent=2))