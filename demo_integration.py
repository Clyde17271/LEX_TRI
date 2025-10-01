#!/usr/bin/env python3
"""
LEX TRI Demonstration Script
Shows integration capabilities and temporal anomaly detection
"""

from datetime import datetime, timedelta
import json
from temporal_viz import TemporalPoint, TemporalTimeline, visualize_timeline
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def create_production_scenario():
    """Create a realistic production scenario with various temporal patterns."""

    console.print(Panel.fit("📊 LEX TRI Production Scenario Demo", style="bold green"))

    # Create timeline for a distributed system event flow
    timeline = TemporalTimeline(name="Distributed System Event Flow")
    base_time = datetime.now()

    # Scenario 1: Normal database transaction
    console.print("\n[cyan]Adding normal database transaction events...[/cyan]")
    timeline.add_point(TemporalPoint(
        valid_time=base_time,
        transaction_time=base_time + timedelta(milliseconds=50),
        decision_time=base_time + timedelta(milliseconds=100),
        event_data={"type": "db_write", "table": "users", "status": "success"},
        event_id="db_001"
    ))

    # Scenario 2: Cache invalidation event (normal)
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=1),
        transaction_time=base_time + timedelta(seconds=1, milliseconds=20),
        decision_time=base_time + timedelta(seconds=1, milliseconds=50),
        event_data={"type": "cache_invalidate", "key": "user:123", "status": "success"},
        event_id="cache_001"
    ))

    # Scenario 3: Network partition causing time travel anomaly
    console.print("[yellow]Simulating network partition event...[/yellow]")
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=5),
        transaction_time=base_time + timedelta(seconds=4),  # TT before VT!
        decision_time=base_time + timedelta(seconds=6),
        event_data={"type": "network_event", "status": "partition_detected", "severity": "high"},
        event_id="net_001"
    ))

    # Scenario 4: Premature decision in payment processing
    console.print("[red]Adding payment processing with premature decision...[/red]")
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=10),
        transaction_time=base_time + timedelta(seconds=10, milliseconds=500),
        decision_time=base_time + timedelta(seconds=10, milliseconds=200),  # DT before TT!
        event_data={"type": "payment", "amount": 150.00, "status": "processed_early", "risk": "high"},
        event_id="pay_001"
    ))

    # Scenario 5: Large ingestion lag from external API
    console.print("[magenta]Adding external API event with large lag...[/magenta]")
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=15),
        transaction_time=base_time + timedelta(seconds=20),  # 5 second lag
        decision_time=base_time + timedelta(seconds=21),
        event_data={"type": "api_webhook", "source": "external_partner", "status": "delayed"},
        event_id="api_001"
    ))

    # Scenario 6: Out-of-order message processing
    console.print("[blue]Adding out-of-order message queue events...[/blue]")
    # Message 1 - arrives later but has earlier valid time
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=25),
        transaction_time=base_time + timedelta(seconds=28),
        decision_time=base_time + timedelta(seconds=29),
        event_data={"type": "message", "queue": "orders", "seq": 1},
        event_id="msg_001"
    ))

    # Message 2 - arrives earlier but has later valid time
    timeline.add_point(TemporalPoint(
        valid_time=base_time + timedelta(seconds=27),
        transaction_time=base_time + timedelta(seconds=26),
        decision_time=base_time + timedelta(seconds=27),
        event_data={"type": "message", "queue": "orders", "seq": 2},
        event_id="msg_002"
    ))

    return timeline

def analyze_and_report(timeline):
    """Analyze timeline and generate detailed report."""

    console.print("\n" + "="*80)
    console.print(Panel.fit("🔍 Temporal Anomaly Analysis Report", style="bold yellow"))

    # Analyze anomalies
    anomalies = timeline.analyze_anomalies()

    if not anomalies:
        console.print("[green]✓ No temporal anomalies detected![/green]")
        return

    # Create summary table
    table = Table(title=f"Found {len(anomalies)} Temporal Anomalies")
    table.add_column("Type", style="red", width=20)
    table.add_column("Event ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Severity", style="yellow")
    table.add_column("Business Impact", style="magenta")

    # Map anomaly types to business impact
    impact_map = {
        "time_travel": "Data consistency risk - may indicate clock sync issues",
        "premature_decision": "Transaction integrity risk - action taken before confirmation",
        "ingestion_lag": "Performance degradation - delayed data processing",
        "out_of_order": "Sequence violation - may cause incorrect state transitions"
    }

    for anomaly in anomalies:
        event_id = anomaly.get("point", {}).get("event_id", "Unknown")
        impact = impact_map.get(anomaly["type"], "Unknown impact")

        table.add_row(
            anomaly["type"].replace("_", " ").title(),
            event_id,
            anomaly["description"][:50] + "..." if len(anomaly["description"]) > 50 else anomaly["description"],
            anomaly["severity"].upper(),
            impact
        )

    console.print(table)

    # Generate recommendations
    console.print("\n")
    console.print(Panel.fit("💡 Recommendations", style="bold green"))

    recommendations = []
    anomaly_types = set(a["type"] for a in anomalies)

    if "time_travel" in anomaly_types:
        recommendations.append("• Check NTP synchronization across all nodes")
        recommendations.append("• Implement logical clocks (Lamport timestamps)")

    if "premature_decision" in anomaly_types:
        recommendations.append("• Add transaction validation before decision points")
        recommendations.append("• Implement two-phase commit protocol")

    if "ingestion_lag" in anomaly_types:
        recommendations.append("• Scale ingestion pipeline capacity")
        recommendations.append("• Implement backpressure mechanisms")

    if "out_of_order" in anomaly_types:
        recommendations.append("• Use message sequencing with ordering guarantees")
        recommendations.append("• Implement event sourcing with proper ordering")

    for rec in recommendations:
        console.print(rec)

    return anomalies

def main():
    """Main demonstration function."""

    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "LEX TRI - Temporal Debugging Agent\nProduction Scenario Demonstration",
        style="bold blue"
    ))
    console.print("="*80)

    # Create production scenario
    timeline = create_production_scenario()

    # Save timeline
    console.print("\n[green]Saving timeline data...[/green]")
    timeline.save_to_json("production_timeline.json")

    # Analyze and report
    anomalies = analyze_and_report(timeline)

    # Generate visualization
    console.print("\n[green]Generating temporal visualization...[/green]")
    visualize_timeline(
        timeline,
        output_path="production_timeline.png",
        show_plot=False,
        highlight_anomalies=True
    )
    console.print("[green]✓ Visualization saved to production_timeline.png[/green]")

    # Save detailed analysis report
    report = {
        "timestamp": datetime.now().isoformat(),
        "timeline_name": timeline.name,
        "total_events": len(timeline.points),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "severity_distribution": {
            "critical": len([a for a in anomalies if a["severity"] == "critical"]),
            "high": len([a for a in anomalies if a["severity"] == "high"]),
            "medium": len([a for a in anomalies if a["severity"] == "medium"]),
            "low": len([a for a in anomalies if a["severity"] == "low"])
        }
    }

    with open("production_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    console.print("[green]✓ Detailed analysis saved to production_analysis.json[/green]")

    # Summary
    console.print("\n" + "="*80)
    console.print(Panel.fit("📈 Summary", style="bold green"))
    console.print(f"• Total Events Processed: {len(timeline.points)}")
    console.print(f"• Anomalies Detected: {len(anomalies)}")
    console.print(f"• Critical Issues: {report['severity_distribution']['critical']}")
    console.print(f"• High Priority Issues: {report['severity_distribution']['high']}")
    console.print("="*80 + "\n")

if __name__ == "__main__":
    main()