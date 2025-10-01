#!/usr/bin/env python3
"""
Test script for LEX TRI MCP integration

This script tests the MCP server and client functionality to ensure
proper integration with the Model Context Protocol.
"""

import asyncio
import json
import os
import sys
import tempfile
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp_client import LEXTRIMCPClient
    HAS_MCP_CLIENT = True
except ImportError as e:
    print(f"Warning: Could not import MCP client: {e}")
    HAS_MCP_CLIENT = False

try:
    from mcp_server import LEXTRIMCPServer
    HAS_MCP_SERVER = True
except ImportError as e:
    print(f"Warning: Could not import MCP server: {e}")
    HAS_MCP_SERVER = False


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    # Test MCP imports
    try:
        import mcp
        print("✓ mcp module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mcp: {e}")
        return False

    # Test server imports
    if HAS_MCP_SERVER:
        print("✓ MCP server module imported successfully")
    else:
        print("✗ Failed to import MCP server module")
        return False

    # Test client imports
    if HAS_MCP_CLIENT:
        print("✓ MCP client module imported successfully")
    else:
        print("✗ Failed to import MCP client module")
        return False

    # Test temporal viz imports
    try:
        from temporal_viz import TemporalTimeline, TemporalPoint
        print("✓ Temporal visualization module imported successfully")
    except ImportError as e:
        print(f"⚠ Temporal visualization module not available: {e}")

    # Test exo integration imports
    try:
        from exo_integration import ExoTemporalAdapter
        print("✓ Exo integration module imported successfully")
    except ImportError as e:
        print(f"⚠ Exo integration module not available: {e}")

    return True


def test_server_creation():
    """Test that MCP server can be created."""
    print("\nTesting MCP server creation...")

    if not HAS_MCP_SERVER:
        print("✗ MCP server module not available")
        return False

    try:
        server = LEXTRIMCPServer()
        print("✓ MCP server created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create MCP server: {e}")
        return False


def test_client_creation():
    """Test that MCP client can be created."""
    print("\nTesting MCP client creation...")

    if not HAS_MCP_CLIENT:
        print("✗ MCP client module not available")
        return False

    try:
        client = LEXTRIMCPClient()
        print("✓ MCP client created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create MCP client: {e}")
        return False


def test_configuration_file():
    """Test that MCP configuration file is valid."""
    print("\nTesting MCP configuration...")

    config_path = "mcp_config.json"
    if not os.path.exists(config_path):
        print(f"✗ Configuration file not found: {config_path}")
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check required configuration sections
        required_sections = ["mcpServers", "server_info", "installation", "documentation"]
        for section in required_sections:
            if section not in config:
                print(f"✗ Missing configuration section: {section}")
                return False

        # Check server configuration
        if "lextri-temporal-agent" not in config["mcpServers"]:
            print("✗ LEX TRI server not found in configuration")
            return False

        server_config = config["mcpServers"]["lextri-temporal-agent"]
        if "command" not in server_config or "args" not in server_config:
            print("✗ Invalid server configuration")
            return False

        print("✓ MCP configuration file is valid")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading configuration file: {e}")
        return False


def create_test_timeline():
    """Create a test timeline for testing purposes."""
    test_timeline = {
        "name": "Test Timeline",
        "description": "Timeline for MCP integration testing",
        "points": [
            {
                "event_id": "test_001",
                "valid_time": "2024-01-01T10:00:00Z",
                "transaction_time": "2024-01-01T10:00:05Z",
                "decision_time": "2024-01-01T10:00:10Z",
                "event_type": "system_start",
                "data": {"status": "initialized", "component": "test_system"}
            },
            {
                "event_id": "test_002",
                "valid_time": "2024-01-01T10:01:00Z",
                "transaction_time": "2024-01-01T10:01:02Z",
                "decision_time": "2024-01-01T10:01:05Z",
                "event_type": "process_event",
                "data": {"value": 42, "component": "test_processor"}
            },
            {
                "event_id": "test_003",
                "valid_time": "2024-01-01T10:02:00Z",
                "transaction_time": "2024-01-01T10:02:15Z",
                "decision_time": "2024-01-01T10:02:20Z",
                "event_type": "anomaly_event",
                "data": {"anomaly_type": "temporal_drift", "severity": "high"}
            }
        ]
    }
    return test_timeline


async def test_server_functionality():
    """Test MCP server functionality (if possible)."""
    print("\nTesting MCP server functionality...")

    if not HAS_MCP_SERVER:
        print("⚠ Skipping server functionality test - server module not available")
        return True

    try:
        # This is a basic test that the server can be instantiated and configured
        server = LEXTRIMCPServer()

        # Test that handlers are set up
        if hasattr(server.server, '_handlers'):
            print("✓ Server handlers configured")

        print("✓ Basic server functionality test passed")
        return True

    except Exception as e:
        print(f"✗ Server functionality test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files are present."""
    print("\nTesting file structure...")

    required_files = [
        "mcp_server.py",
        "mcp_client.py",
        "mcp_config.json",
        "requirements.txt"
    ]

    missing_files = []
    for filename in required_files:
        if not os.path.exists(filename):
            missing_files.append(filename)

    if missing_files:
        print(f"✗ Missing required files: {', '.join(missing_files)}")
        return False

    print("✓ All required files present")
    return True


def test_requirements():
    """Test that requirements.txt includes MCP dependencies."""
    print("\nTesting requirements...")

    if not os.path.exists("requirements.txt"):
        print("✗ requirements.txt not found")
        return False

    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read().lower()

        # Check for MCP dependency
        if "mcp" not in requirements:
            print("✗ MCP dependency not found in requirements.txt")
            return False

        print("✓ MCP dependency found in requirements.txt")
        return True

    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False


def generate_integration_report(test_results: Dict[str, bool]):
    """Generate a comprehensive integration report."""
    print("\n" + "="*60)
    print("LEX TRI MCP INTEGRATION TEST REPORT")
    print("="*60)

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    print(f"\nTest Summary: {passed_tests}/{total_tests} tests passed")
    print("-" * 40)

    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")

    print("\nIntegration Status:")
    if passed_tests == total_tests:
        print("🎉 MCP integration is ready!")
        print("You can now use LEX TRI with MCP-compatible AI clients.")
    elif passed_tests >= total_tests * 0.7:  # 70% or more tests passed
        print("⚠ MCP integration is partially ready.")
        print("Some optional features may not be available.")
    else:
        print("❌ MCP integration needs attention.")
        print("Please resolve the failing tests before using MCP features.")

    print("\nNext Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start MCP server: python mcp_server.py")
    print("3. Test with client: python mcp_client.py")
    print("4. Configure with Claude Desktop or other MCP clients")

    print("\nConfiguration for Claude Desktop:")
    print("Add to ~/Library/Application Support/Claude/claude_desktop_config.json:")
    print(json.dumps({
        "mcpServers": {
            "lextri-temporal-agent": {
                "command": "python",
                "args": [os.path.abspath("mcp_server.py")],
                "env": {}
            }
        }
    }, indent=2))


async def main():
    """Main test function."""
    print("LEX TRI MCP Integration Test Suite")
    print("="*50)

    # Run all tests
    test_results = {
        "File Structure": test_file_structure(),
        "Requirements": test_requirements(),
        "Imports": test_imports(),
        "Configuration": test_configuration_file(),
        "Server Creation": test_server_creation(),
        "Client Creation": test_client_creation(),
        "Server Functionality": await test_server_functionality(),
    }

    # Generate report
    generate_integration_report(test_results)

    # Return overall success
    return all(test_results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)