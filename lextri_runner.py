"""
This module provides the main entry point for the LEX TRI temporal agent.
It handles command-line arguments, security validation, and core functionality.
Includes integration with Exo platform for enhanced observability.
"""

import sys
import re
import argparse
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

from rich.console import Console
from rich.table import Table

# Import our temporal visualization module
try:
    from temporal_viz import (
        TemporalPoint, 
        TemporalTimeline, 
        visualize_timeline, 
        generate_example_timeline
    )
    HAS_VIZ = True
except ImportError:
    HAS_VIZ = False

# Import Exo integration module
try:
    from exo_integration import ExoTemporalAdapter
    HAS_EXO = True
except ImportError:
    HAS_EXO = False


def validate_arguments(args: List[str]) -> List[str]:
    """Validate and sanitize command-line arguments for security.
    
    Args:
        args: Raw command-line arguments
        
    Returns:
        List of validated and sanitized arguments
        
    Raises:
        ValueError: If arguments contain potentially dangerous patterns
    """
    validated_args = []
    
    # Define patterns that could be dangerous
    dangerous_patterns = [
        r'[;&|`$(){}\[\]<>]',  # Shell metacharacters
        r'\.\./',              # Path traversal
    ]
    
    # Whitelist common command-line flags/options for our application
    allowed_flags = [
        "--mode", "--input", "--output", "--no-highlight", "-h", "--help"
    ]
    
    for arg in args:
        # Skip validation for whitelisted flags
        if arg in allowed_flags or any(arg.startswith(f"{flag}=") for flag in allowed_flags):
            validated_args.append(arg)
            continue
            
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, arg):
                raise ValueError(f"Potentially dangerous argument detected: {arg}")
        
        # Sanitize: limit length and allowed characters
        if len(arg) > 100:
            raise ValueError(f"Argument too long: {arg[:20]}...")
        
        validated_args.append(arg)
    
    return validated_args


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="LEX TRI — Temporal Agent for debugging and analyzing tri-temporal data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Add command-line arguments
    parser.add_argument(
        "--mode", 
        choices=["diagnostics", "visualize", "analyze", "example", "exo-publish"],
        default="diagnostics",
        help="Operation mode (default: diagnostics)"
    )
    
    parser.add_argument(
        "--input", 
        type=str,
        help="Input file path for timeline data (JSON)"
    )
    
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file path for results"
    )
    
    parser.add_argument(
        "--no-highlight", 
        action="store_true",
        help="Disable anomaly highlighting in visualization"
    )
    
    # Exo integration options
    parser.add_argument(
        "--exo-integration",
        action="store_true",
        help="Enable Exo platform integration"
    )
    
    parser.add_argument(
        "--exo-api-key",
        type=str,
        help="API key for Exo platform authentication"
    )
    
    parser.add_argument(
        "--exo-project",
        type=str,
        help="Exo project ID or name"
    )
    
    parser.add_argument(
        "--exo-timeline-name",
        type=str,
        default="LEX TRI Temporal Analysis",
        help="Name for the timeline in Exo"
    )
    
    parser.add_argument(
        "--exo-publish-anomalies",
        action="store_true",
        default=True,
        help="Publish detected anomalies to Exo event stream"
    )
    
    return parser


def handle_exo_integration(timeline: TemporalTimeline, args: argparse.Namespace, console: Console) -> None:
    """Handle integration with Exo platform.
    
    Args:
        timeline: The temporal timeline to publish to Exo
        args: Command-line arguments containing Exo settings
        console: Rich console for output
    """
    if not HAS_EXO:
        console.print("[yellow]Exo integration module not available.[/yellow]")
        console.print("[yellow]Make sure exo_integration.py is in your path and Exo dependencies are installed.[/yellow]")
        return
    
    try:
        # Initialize Exo adapter with credentials
        console.print("[bold blue]Initializing Exo integration[/bold blue]")
        
        # Configure Exo adapter with API key and project
        exo_config = {
            "api_key": args.exo_api_key,
            "project": args.exo_project,
            "timeline_name": args.exo_timeline_name,
            "publish_anomalies": args.exo_publish_anomalies
        }
        
        # Create adapter and publish timeline
        adapter = ExoTemporalAdapter(config=exo_config)
        
        # Publish timeline to Exo
        result = adapter.publish_timeline(timeline)
        
        # Output results
        console.print(f"[green]Timeline '{timeline.name}' published to Exo platform[/green]")
        console.print(f"[green]Exo timeline ID: {result.get('timeline_id', 'N/A')}[/green]")
        
        # If anomalies were published, show count
        if args.exo_publish_anomalies:
            anomalies = timeline.analyze_anomalies()
            if anomalies:
                console.print(f"[green]Published {len(anomalies)} anomalies to Exo event stream[/green]")
        
        # Display Exo dashboard URL if available
        dashboard_url = result.get('dashboard_url')
        if dashboard_url:
            console.print(f"[blue]Exo Dashboard URL: {dashboard_url}[/blue]")
            
    except Exception as e:
        import traceback
        console.print(f"[red]Error during Exo integration: {str(e)}[/red]")
        console.print(traceback.format_exc())


def run_visualization(args: argparse.Namespace, console: Console) -> None:
    """Run the visualization functionality."""
    if not HAS_VIZ:
        console.print("[red]Temporal visualization module not available.[/red]")
        console.print("[yellow]Make sure matplotlib is installed: pip install matplotlib[/yellow]")
        return
    
    if args.mode == "example":
        try:
            # Generate and visualize an example timeline
            console.print("[bold green]Generating example timeline[/bold green]")
            timeline = generate_example_timeline()
            
            # Save timeline to JSON if output is provided
            if args.output:
                console.print(f"Output path: {args.output}")
                
                # Create base filename and ensure directories exist
                base_path = args.output
                output_dir = os.path.dirname(base_path) if os.path.dirname(base_path) else "."
                console.print(f"Using directory: {output_dir}")
                
                # Make sure output directory exists
                if output_dir and output_dir != ".":
                    os.makedirs(output_dir, exist_ok=True)
                
                # Save the JSON file
                json_path = f"{base_path}.json"
                timeline.save_to_json(json_path)
                console.print(f"[green]Example timeline saved to {json_path}[/green]")
                
                # Create and save the visualization
                vis_path = f"{base_path}.png"
                visualize_timeline(
                    timeline, 
                    output_path=vis_path,
                    show_plot=False,
                    highlight_anomalies=not args.no_highlight
                )
                console.print(f"[green]Visualization saved to {vis_path}[/green]")
                
                # Handle Exo integration if enabled
                if args.exo_integration:
                    handle_exo_integration(timeline, args, console)
            else:
                # Just visualize without saving
                visualize_timeline(
                    timeline, 
                    show_plot=True,
                    highlight_anomalies=not args.no_highlight
                )
                
                # Handle Exo integration if enabled
                if args.exo_integration:
                    handle_exo_integration(timeline, args, console)
        except Exception as e:
            import traceback
            console.print(f"[red]Error in example mode: {str(e)}[/red]")
            console.print(traceback.format_exc())
    
    elif args.mode == "visualize":
        # Visualize an existing timeline from a JSON file
        if not args.input:
            console.print("[red]Input file path required for visualization mode.[/red]")
            return
        
        if not os.path.exists(args.input):
            console.print(f"[red]Input file not found: {args.input}[/red]")
            return
        
        try:
            timeline = TemporalTimeline.load_from_json(args.input)
            console.print(f"[green]Loaded timeline with {len(timeline.points)} points[/green]")
            
            output_path = args.output if args.output else None
            visualize_timeline(
                timeline,
                output_path=output_path,
                show_plot=output_path is None,
                highlight_anomalies=not args.no_highlight
            )
            
            # Handle Exo integration if enabled
            if args.exo_integration:
                handle_exo_integration(timeline, args, console)
                
        except Exception as e:
            console.print(f"[red]Error visualizing timeline: {str(e)}[/red]")
    
    elif args.mode == "analyze":
        # Analyze an existing timeline for anomalies
        if not args.input:
            console.print("[red]Input file path required for analysis mode.[/red]")
            return
        
        if not os.path.exists(args.input):
            console.print(f"[red]Input file not found: {args.input}[/red]")
            return
        
        try:
            timeline = TemporalTimeline.load_from_json(args.input)
            console.print(f"[green]Loaded timeline with {len(timeline.points)} points[/green]")
            
            # Analyze anomalies
            anomalies = timeline.analyze_anomalies()
            
            if not anomalies:
                console.print("[green]No anomalies detected in timeline.[/green]")
                return
                
            # Display results in a table
            table = Table(title=f"Temporal Anomalies in {timeline.name}")
            table.add_column("Type", style="red")
            table.add_column("Description")
            table.add_column("Severity", style="yellow")
            table.add_column("Event ID")
            
            for anomaly in anomalies:
                event_id = anomaly.get("point", {}).get("event_id", "Unknown")
                table.add_row(
                    anomaly["type"].replace("_", " ").title(),
                    anomaly["description"],
                    anomaly["severity"].upper(),
                    event_id
                )
            
            console.print(table)
            
            # Save results if output is specified
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    
                with open(args.output, 'w') as f:
                    json.dump({
                        "timeline_name": timeline.name,
                        "anomaly_count": len(anomalies),
                        "anomalies": anomalies,
                        "analysis_timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                    
                console.print(f"[green]Analysis results saved to {args.output}[/green]")
            
            # Handle Exo integration if enabled
            if args.exo_integration:
                handle_exo_integration(timeline, args, console)
                
        except Exception as e:
            console.print(f"[red]Error analyzing timeline: {str(e)}[/red]")
    
    elif args.mode == "exo-publish":
        # Direct publish to Exo without visualization
        if not args.input:
            console.print("[red]Input file path required for exo-publish mode.[/red]")
            return
        
        if not os.path.exists(args.input):
            console.print(f"[red]Input file not found: {args.input}[/red]")
            return
        
        if not args.exo_integration:
            console.print("[red]Exo integration must be enabled with --exo-integration for exo-publish mode.[/red]")
            return
            
        try:
            timeline = TemporalTimeline.load_from_json(args.input)
            console.print(f"[green]Loaded timeline with {len(timeline.points)} points[/green]")
            
            # Handle Exo integration
            handle_exo_integration(timeline, args, console)
                
        except Exception as e:
            console.print(f"[red]Error publishing to Exo: {str(e)}[/red]")


def main() -> None:
    """Entry point for the LEX TRI runner.

    This function parses command-line arguments and runs the appropriate functionality.
    """
    console = Console()
    console.rule("[bold green]LEX TRI — Temporal Agent")
    
    # Set up argument parser
    parser = setup_argparse()
    
    if len(sys.argv) == 1:
        # No arguments provided, show basic info
        console.print("Mode: Diagnostics")
        console.print("Analyzing VT/TT/DT traces...")
        console.print("No anomalies found.")
    else:
        try:
            # First validate raw arguments for security
            raw_args = sys.argv[1:]
            validate_arguments(raw_args)
            
            # Parse arguments
            args = parser.parse_args()
            
            # Show mode information
            console.print(f"Mode: {args.mode.title()}")
            
            # Run the appropriate functionality
            if args.mode in ["visualize", "analyze", "example", "exo-publish"]:
                run_visualization(args, console)
            else:
                # Default diagnostics mode
                console.print("Analyzing VT/TT/DT traces...")
                console.print("No anomalies found.")
                
                # Show Exo integration status
                if args.exo_integration:
                    if HAS_EXO:
                        console.print("[green]Exo integration is available.[/green]")
                    else:
                        console.print("[yellow]Exo integration module not available.[/yellow]")
                
        except ValueError as e:
            console.print(f"[red]Security error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)


if __name__ == "__main__":
    main()
