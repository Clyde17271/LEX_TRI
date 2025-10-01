"""
MCP Server for Temporal Events Analysis
"""

import sys
import os

# Add parent directory to path so we can import the actual LEX TRI modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual MCP server implementation
from mcp_server import LEXTRIMCPServer, main

__all__ = ["LEXTRIMCPServer", "main"]