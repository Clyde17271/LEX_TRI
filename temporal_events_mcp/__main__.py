"""
Entry point for temporal_events_mcp module when run with python -m
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())