"""
MCP Server for LEX TRI Temporal Agent

This module implements a Model Context Protocol (MCP) server that exposes
LEX TRI temporal analysis capabilities to AI clients. It provides tools for
timeline visualization, anomaly detection, and temporal data analysis.
"""

import json
import os
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime
import asyncio

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ReadResourceResult,
    ListPromptsResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

# Import temporal functionality
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

# Import Exo integration
try:
    from exo_integration import ExoTemporalAdapter
    HAS_EXO = True
except ImportError:
    HAS_EXO = False


class LEXTRIMCPServer:
    """MCP Server for LEX TRI temporal analysis capabilities."""

    def __init__(self):
        self.server = Server("lextri-temporal-agent")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP protocol handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Return list of available tools."""
            tools = [
                Tool(
                    name="generate_example_timeline",
                    description="Generate an example temporal timeline with sample data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name for the timeline",
                                "default": "Example Timeline"
                            },
                            "num_points": {
                                "type": "integer",
                                "description": "Number of temporal points to generate",
                                "default": 50
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_timeline_anomalies",
                    description="Analyze a timeline for temporal anomalies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeline_json": {
                                "type": "string",
                                "description": "JSON string containing timeline data"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to JSON file containing timeline data (alternative to timeline_json)"
                            }
                        },
                        "oneOf": [
                            {"required": ["timeline_json"]},
                            {"required": ["file_path"]}
                        ]
                    }
                ),
                Tool(
                    name="visualize_timeline",
                    description="Create a visualization of a temporal timeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeline_json": {
                                "type": "string",
                                "description": "JSON string containing timeline data"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to JSON file containing timeline data (alternative to timeline_json)"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Path where to save the visualization"
                            },
                            "highlight_anomalies": {
                                "type": "boolean",
                                "description": "Whether to highlight anomalies in the visualization",
                                "default": True
                            }
                        },
                        "oneOf": [
                            {"required": ["timeline_json", "output_path"]},
                            {"required": ["file_path", "output_path"]}
                        ]
                    }
                ),
            ]

            # Add Exo integration tools if available
            if HAS_EXO:
                tools.append(Tool(
                    name="publish_to_exo",
                    description="Publish timeline data to Exo platform",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeline_json": {
                                "type": "string",
                                "description": "JSON string containing timeline data"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to JSON file containing timeline data (alternative to timeline_json)"
                            },
                            "api_key": {
                                "type": "string",
                                "description": "Exo platform API key"
                            },
                            "project": {
                                "type": "string",
                                "description": "Exo project ID or name"
                            },
                            "timeline_name": {
                                "type": "string",
                                "description": "Name for the timeline in Exo platform",
                                "default": "LEX TRI Temporal Analysis"
                            },
                            "publish_anomalies": {
                                "type": "boolean",
                                "description": "Whether to publish detected anomalies to Exo event stream",
                                "default": True
                            }
                        },
                        "required": ["api_key", "project"],
                        "oneOf": [
                            {"required": ["timeline_json"]},
                            {"required": ["file_path"]}
                        ]
                    }
                ))

            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> CallToolResult:
            """Handle tool calls."""
            arguments = arguments or {}

            try:
                if name == "generate_example_timeline":
                    return await self._handle_generate_example_timeline(arguments)
                elif name == "analyze_timeline_anomalies":
                    return await self._handle_analyze_timeline_anomalies(arguments)
                elif name == "visualize_timeline":
                    return await self._handle_visualize_timeline(arguments)
                elif name == "publish_to_exo" and HAS_EXO:
                    return await self._handle_publish_to_exo(arguments)
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )
                        ]
                    )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error executing tool {name}: {str(e)}"
                        )
                    ]
                )

        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """Return list of available resources."""
            resources = []

            # Look for existing timeline files
            current_dir = os.getcwd()
            json_files = [f for f in os.listdir(current_dir) if f.endswith('.json')]
            timeline_files = [f for f in json_files if 'timeline' in f.lower()]

            for file in timeline_files:
                resources.append(Resource(
                    uri=f"file://{os.path.join(current_dir, file)}",
                    name=f"Timeline: {file}",
                    description=f"Temporal timeline data from {file}",
                    mimeType="application/json"
                ))

            return ListResourcesResult(resources=resources)

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Return resource content."""
            if uri.startswith("file://"):
                file_path = uri[7:]  # Remove 'file://' prefix
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=content
                            )
                        ]
                    )
                except Exception as e:
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=f"Error reading file {file_path}: {str(e)}"
                            )
                        ]
                    )
            else:
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Unsupported URI: {uri}"
                        )
                    ]
                )

        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            """Return list of available prompts."""
            prompts = [
                Prompt(
                    name="analyze_temporal_anomalies",
                    description="Analyze temporal data for anomalies and patterns",
                    arguments=[
                        {
                            "name": "timeline_data",
                            "description": "Timeline data in JSON format",
                            "required": True
                        }
                    ]
                ),
                Prompt(
                    name="explain_temporal_analysis",
                    description="Explain temporal analysis results and methodology",
                    arguments=[
                        {
                            "name": "analysis_results",
                            "description": "Analysis results to explain",
                            "required": True
                        }
                    ]
                ),
                Prompt(
                    name="temporal_debugging_guide",
                    description="Get guidance for temporal debugging scenarios",
                    arguments=[
                        {
                            "name": "scenario",
                            "description": "Description of the temporal debugging scenario",
                            "required": True
                        }
                    ]
                )
            ]

            return ListPromptsResult(prompts=prompts)

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[Dict[str, str]] = None
        ) -> GetPromptResult:
            """Return prompt content."""
            arguments = arguments or {}

            if name == "analyze_temporal_anomalies":
                timeline_data = arguments.get("timeline_data", "")
                content = f"""
                Analyze the following temporal timeline data for anomalies, patterns, and insights:

                Timeline Data:
                {timeline_data}

                Please provide:
                1. Summary of temporal patterns observed
                2. Any anomalies or irregularities detected
                3. Potential causes or explanations for anomalies
                4. Recommendations for further investigation
                5. Temporal consistency analysis across VT/TT/DT dimensions
                """

            elif name == "explain_temporal_analysis":
                analysis_results = arguments.get("analysis_results", "")
                content = f"""
                Explain the following temporal analysis results in detail:

                Analysis Results:
                {analysis_results}

                Please provide:
                1. Clear explanation of each finding
                2. Technical context and significance
                3. Implications for system behavior
                4. Suggested remediation steps if issues are found
                5. How these results relate to tri-temporal debugging concepts
                """

            elif name == "temporal_debugging_guide":
                scenario = arguments.get("scenario", "")
                content = f"""
                Provide debugging guidance for the following temporal scenario:

                Scenario:
                {scenario}

                Please provide:
                1. Relevant temporal debugging techniques
                2. Key metrics and data points to examine
                3. Common patterns that might indicate specific issues
                4. Step-by-step debugging approach
                5. Tools and methods for temporal analysis
                6. How to interpret VT (Valid Time), TT (Transaction Time), and DT (Decision Time) relationships
                """

            else:
                content = f"Unknown prompt: {name}"

            return GetPromptResult(
                description=f"Prompt for {name}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=content
                        )
                    )
                ]
            )

    async def _handle_generate_example_timeline(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle generate_example_timeline tool call."""
        if not HAS_VIZ:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Temporal visualization module not available. Install matplotlib to use this feature."
                    )
                ]
            )

        name = arguments.get("name", "Example Timeline")
        num_points = arguments.get("num_points", 50)

        # Generate timeline
        timeline = generate_example_timeline()
        timeline.name = name

        # Limit points if requested
        if num_points < len(timeline.points):
            timeline.points = timeline.points[:num_points]

        # Convert to JSON
        timeline_data = timeline.to_dict()

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Generated example timeline '{name}' with {len(timeline.points)} points:\n\n{json.dumps(timeline_data, indent=2)}"
                )
            ]
        )

    async def _handle_analyze_timeline_anomalies(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle analyze_timeline_anomalies tool call."""
        if not HAS_VIZ:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Temporal visualization module not available. Install matplotlib to use this feature."
                    )
                ]
            )

        timeline = await self._load_timeline(arguments)
        if not timeline:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Failed to load timeline data"
                    )
                ]
            )

        # Analyze anomalies
        anomalies = timeline.analyze_anomalies()

        if not anomalies:
            result_text = f"No anomalies detected in timeline '{timeline.name}' with {len(timeline.points)} points."
        else:
            result_text = f"Found {len(anomalies)} anomalies in timeline '{timeline.name}':\n\n"
            for i, anomaly in enumerate(anomalies, 1):
                event_id = anomaly.get("point", {}).get("event_id", "Unknown")
                result_text += f"{i}. {anomaly['type'].replace('_', ' ').title()}\n"
                result_text += f"   Description: {anomaly['description']}\n"
                result_text += f"   Severity: {anomaly['severity'].upper()}\n"
                result_text += f"   Event ID: {event_id}\n\n"

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )

    async def _handle_visualize_timeline(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle visualize_timeline tool call."""
        if not HAS_VIZ:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Temporal visualization module not available. Install matplotlib to use this feature."
                    )
                ]
            )

        timeline = await self._load_timeline(arguments)
        if not timeline:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Failed to load timeline data"
                    )
                ]
            )

        output_path = arguments.get("output_path")
        highlight_anomalies = arguments.get("highlight_anomalies", True)

        if not output_path:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Output path is required for visualization"
                    )
                ]
            )

        # Create visualization
        visualize_timeline(
            timeline,
            output_path=output_path,
            show_plot=False,
            highlight_anomalies=highlight_anomalies
        )

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Timeline visualization saved to {output_path}"
                )
            ]
        )

    async def _handle_publish_to_exo(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle publish_to_exo tool call."""
        if not HAS_EXO:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Exo integration module not available."
                    )
                ]
            )

        timeline = await self._load_timeline(arguments)
        if not timeline:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Failed to load timeline data"
                    )
                ]
            )

        api_key = arguments.get("api_key")
        project = arguments.get("project")
        timeline_name = arguments.get("timeline_name", "LEX TRI Temporal Analysis")
        publish_anomalies = arguments.get("publish_anomalies", True)

        if not api_key or not project:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="API key and project are required for Exo integration"
                    )
                ]
            )

        try:
            # Configure Exo adapter
            exo_config = {
                "api_key": api_key,
                "project": project,
                "timeline_name": timeline_name,
                "publish_anomalies": publish_anomalies
            }

            # Create adapter and publish timeline
            adapter = ExoTemporalAdapter(config=exo_config)
            result = adapter.publish_timeline(timeline)

            result_text = f"Timeline '{timeline.name}' published to Exo platform\n"
            result_text += f"Exo timeline ID: {result.get('timeline_id', 'N/A')}\n"

            # If anomalies were published, show count
            if publish_anomalies:
                anomalies = timeline.analyze_anomalies()
                if anomalies:
                    result_text += f"Published {len(anomalies)} anomalies to Exo event stream\n"

            # Display Exo dashboard URL if available
            dashboard_url = result.get('dashboard_url')
            if dashboard_url:
                result_text += f"Exo Dashboard URL: {dashboard_url}"

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error publishing to Exo: {str(e)}"
                    )
                ]
            )

    async def _load_timeline(self, arguments: Dict[str, Any]) -> Optional[TemporalTimeline]:
        """Load timeline from arguments (either JSON string or file path)."""
        timeline_json = arguments.get("timeline_json")
        file_path = arguments.get("file_path")

        if timeline_json:
            try:
                timeline_data = json.loads(timeline_json)
                timeline = TemporalTimeline.from_dict(timeline_data)
                return timeline
            except Exception as e:
                return None
        elif file_path:
            try:
                if os.path.exists(file_path):
                    timeline = TemporalTimeline.load_from_json(file_path)
                    return timeline
            except Exception as e:
                return None

        return None

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="lextri-temporal-agent",
                    server_version="1.0.0",
                    capabilities={}
                )
            )


async def main():
    """Main entry point for the MCP server."""
    server = LEXTRIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())