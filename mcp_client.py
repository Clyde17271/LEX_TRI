"""
MCP Client for LEX TRI Temporal Agent

This module implements a Model Context Protocol (MCP) client that can connect
to MCP servers and use their temporal analysis capabilities. It demonstrates
how to integrate LEX TRI functionality into AI applications.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
# MCP client types are handled internally by the session


class LEXTRIMCPClient:
    """MCP Client for LEX TRI temporal analysis."""

    def __init__(self):
        self.session: Optional[ClientSession] = None

    async def connect(self, server_script_path: str):
        """Connect to MCP server."""
        try:
            # Create stdio client connection
            async with stdio_client([
                sys.executable,
                server_script_path
            ]) as (read, write):

                async with ClientSession(read, write) as session:
                    self.session = session

                    # Initialize the session
                    await session.initialize()

                    print("Connected to LEX TRI MCP Server")
                    return session

        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return None

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from the server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.list_tools()

        tools_info = []
        for tool in result.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })

        return tools_info

    async def list_available_resources(self) -> List[Dict[str, Any]]:
        """List all available resources from the server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.list_resources()

        resources_info = []
        for resource in result.resources:
            resources_info.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mimeType
            })

        return resources_info

    async def list_available_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts from the server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.list_prompts()

        prompts_info = []
        for prompt in result.prompts:
            prompts_info.append({
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments
            })

        return prompts_info

    async def generate_example_timeline(self, name: str = "Example Timeline", num_points: int = 50) -> Dict[str, Any]:
        """Generate an example timeline using the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "generate_example_timeline",
            arguments={
                "name": name,
                "num_points": num_points
            }
        )

        if result.content:
            return {"success": True, "content": result.content[0].text}
        else:
            return {"success": False, "error": "No content returned"}

    async def analyze_timeline_anomalies(self, timeline_data: Optional[str] = None, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze timeline for anomalies."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        arguments = {}
        if timeline_data:
            arguments["timeline_json"] = timeline_data
        elif file_path:
            arguments["file_path"] = file_path
        else:
            raise ValueError("Either timeline_data or file_path must be provided")

        result = await self.session.call_tool(
            "analyze_timeline_anomalies",
            arguments=arguments
        )

        if result.content:
            return {"success": True, "content": result.content[0].text}
        else:
            return {"success": False, "error": "No content returned"}

    async def visualize_timeline(self, output_path: str, timeline_data: Optional[str] = None,
                               file_path: Optional[str] = None, highlight_anomalies: bool = True) -> Dict[str, Any]:
        """Create a visualization of a timeline."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        arguments = {
            "output_path": output_path,
            "highlight_anomalies": highlight_anomalies
        }

        if timeline_data:
            arguments["timeline_json"] = timeline_data
        elif file_path:
            arguments["file_path"] = file_path
        else:
            raise ValueError("Either timeline_data or file_path must be provided")

        result = await self.session.call_tool(
            "visualize_timeline",
            arguments=arguments
        )

        if result.content:
            return {"success": True, "content": result.content[0].text}
        else:
            return {"success": False, "error": "No content returned"}

    async def publish_to_exo(self, api_key: str, project: str, timeline_data: Optional[str] = None,
                           file_path: Optional[str] = None, timeline_name: str = "LEX TRI Temporal Analysis",
                           publish_anomalies: bool = True) -> Dict[str, Any]:
        """Publish timeline to Exo platform."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        arguments = {
            "api_key": api_key,
            "project": project,
            "timeline_name": timeline_name,
            "publish_anomalies": publish_anomalies
        }

        if timeline_data:
            arguments["timeline_json"] = timeline_data
        elif file_path:
            arguments["file_path"] = file_path
        else:
            raise ValueError("Either timeline_data or file_path must be provided")

        result = await self.session.call_tool(
            "publish_to_exo",
            arguments=arguments
        )

        if result.content:
            return {"success": True, "content": result.content[0].text}
        else:
            return {"success": False, "error": "No content returned"}

    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Get resource content from the server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.get_resource(uri)

        if result.contents:
            return {"success": True, "content": result.contents[0].text}
        else:
            return {"success": False, "error": "No content returned"}

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get prompt from the server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.get_prompt(name, arguments or {})

        if result.messages:
            return {"success": True, "messages": result.messages, "description": result.description}
        else:
            return {"success": False, "error": "No messages returned"}


async def demo_client():
    """Demonstrate MCP client functionality."""
    client = LEXTRIMCPClient()

    # Connect to the MCP server
    server_script_path = "mcp_server.py"

    try:
        # For demonstration, we'll show how to use the client methods
        # In practice, you would connect to a running server
        print("LEX TRI MCP Client Demo")
        print("=" * 40)

        print("\nAvailable client methods:")
        print("- connect(server_script_path)")
        print("- list_available_tools()")
        print("- list_available_resources()")
        print("- list_available_prompts()")
        print("- generate_example_timeline(name, num_points)")
        print("- analyze_timeline_anomalies(timeline_data/file_path)")
        print("- visualize_timeline(output_path, timeline_data/file_path)")
        print("- publish_to_exo(api_key, project, timeline_data/file_path)")
        print("- get_resource(uri)")
        print("- get_prompt(name, arguments)")

        print("\nTo use the client:")
        print("1. Start the MCP server: python mcp_server.py")
        print("2. Connect from your application using: client.connect('mcp_server.py')")
        print("3. Use the available methods to interact with LEX TRI functionality")

        # Example usage (commented out since server isn't running in demo)
        """
        # Connect to server
        session = await client.connect(server_script_path)

        if session:
            # List available tools
            tools = await client.list_available_tools()
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(f"- {tool['name']}: {tool['description']}")

            # Generate example timeline
            result = await client.generate_example_timeline("Demo Timeline", 30)
            if result["success"]:
                print("Generated timeline successfully")

            # Analyze for anomalies
            analysis = await client.analyze_timeline_anomalies(file_path="sample_timeline.json")
            if analysis["success"]:
                print("Anomaly analysis completed")
                print(analysis["content"])
        """

    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(demo_client())