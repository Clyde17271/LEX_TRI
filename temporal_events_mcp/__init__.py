"""
Temporal Events MCP Module
==========================

This module provides Model Context Protocol (MCP) server functionality
for LEX TRI temporal event analysis and debugging.
"""

from .server import LEXTRIMCPServer, main

__version__ = "1.0.0"
__all__ = ["LEXTRIMCPServer", "main"]