#!/usr/bin/env python3
"""
Example script demonstrating LEX TRI integration with Exo platform.
This creates an example timeline, visualizes it, and publishes to Exo.
"""

import os
import argparse
from datetime import datetime

from temporal_viz import (
    TemporalPoint, 
    TemporalTimeline, 
    visualize_timeline, 
    generate_example_timeline
)

from exo_integration import ExoTemporalAdapter

def main():
    """Run example integration with Exo platform."""
    parser = argparse.ArgumentParser(
        description="LEX TRI - Exo integration example"
    )
    
    parser.add_argument(
        "--api-key", 
        type=str,
        help="Exo API key for authentication"
    )
    
    parser.add_argument(
        "--project", 
        type=str,
        default="default",
        help="Exo project ID or name"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str,
        default="./output",
        help="Directory for output files"
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=== LEX TRI - Exo Integration Example ===")
    
    # Generate example timeline
    print("Generating example timeline...")
    timeline = generate_example_timeline()
    
    # Save timeline to JSON
    json_path = os.path.join(args.output_dir, "example_timeline.json")
    timeline.save_to_json(json_path)
    print(f"Timeline saved to {json_path}")
    
    # Generate visualization
    vis_path = os.path.join(args.output_dir, "example_timeline.png")
    visualize_timeline(
        timeline,
        output_path=vis_path,
        show_plot=False,
        highlight_anomalies=True
    )
    print(f"Visualization saved to {vis_path}")
    
    # Publish to Exo if API key provided
    if args.api_key:
        print("Publishing to Exo platform...")
        
        exo_config = {
            "api_key": args.api_key,
            "project": args.project,
            "timeline_name": "LEX TRI Example Timeline",
            "publish_anomalies": True
        }
        
        adapter = ExoTemporalAdapter(config=exo_config)
        result = adapter.publish_timeline(timeline)
        
        if "error" in result:
            print(f"Error publishing to Exo: {result['error']}")
        else:
            print(f"Successfully published to Exo!")
            print(f"Timeline ID: {result.get('timeline_id', 'N/A')}")
            print(f"Point count: {result.get('point_count', 0)}")
            print(f"Anomaly count: {result.get('anomaly_count', 0)}")
            
            # Display dashboard URL if available
            dashboard_url = result.get('dashboard_url')
            if dashboard_url:
                print(f"Exo Dashboard URL: {dashboard_url}")
    else:
        print("No Exo API key provided, skipping Exo integration.")
    
    print("\nExample complete!")
    print("For more information on Exo integration, see EXO_INTEGRATION.md")

if __name__ == "__main__":
    main()