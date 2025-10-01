# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Project Architecture

LEX TRI is a temporal debugging agent that operates across three synchronized timelines:
- **Valid Time (VT)**: When a state was supposed to hold true
- **Transaction Time (TT)**: When the system ingested or persisted it
- **Decision Time (DT)**: When an agent or process acted on it

The project consists of several integrated modules:

### Primary Modules
- `lextri_runner.py`: Main CLI entry point with argument validation and command routing
- `temporal_viz.py`: Core temporal visualization engine with anomaly detection algorithms
- `exo_integration.py`: Integration adapter for Exo platform observability
- `mcp_server.py` & `mcp_client.py`: Model Context Protocol implementation for AI client integration

### Key Classes
- `TemporalPoint`: Represents a single point in tri-temporal space with VT/TT/DT timestamps
- `TemporalTimeline`: Collection of temporal points with analysis capabilities
- `ExoTemporalAdapter`: Bridge between LEX TRI and Exo platform
- `LEXTRIMCPServer`: MCP server exposing temporal analysis as tools for AI clients

## Development Commands

### Running the Application
```bash
# Basic diagnostics mode (default)
python lextri_runner.py

# Generate example timeline with visualization
python lextri_runner.py --mode example --output sample_timeline

# Analyze existing timeline for anomalies
python lextri_runner.py --mode analyze --input timeline.json --output analysis.json

# Create visualization from timeline data
python lextri_runner.py --mode visualize --input timeline.json --output viz.png

# Publish to Exo platform (requires credentials)
python lextri_runner.py --mode exo-publish --input timeline.json --exo-integration --exo-api-key <key> --exo-project <project>
```

### Testing
```bash
# Run temporal visualization tests
python -m pytest test_temporal_viz.py -v

# Run Exo integration tests
python test_exo_integration.py

# Test MCP integration
python test_mcp_integration.py
```

### MCP Server Operations
```bash
# Start MCP server for AI client integration
python mcp_server.py

# Test MCP client functionality
python mcp_client.py
```

### Security & Validation
All command-line arguments undergo security validation in `validate_arguments()` function to prevent shell injection and path traversal attacks.

## Temporal Anomaly Detection

The system automatically detects common temporal anomalies:
- **Time Travel**: Transaction time before Valid time (TT < VT)
- **Premature Decisions**: Decision time before Transaction time (DT < TT)
- **Ingestion Lag**: Significant delay between Valid time and Transaction time
- **Out-of-Order Processing**: Events processed in wrong temporal sequence

## Integration Points

### GitHub Actions
Configure via `action.yml` with modes: diagnostics, visualize, analyze, example, exo-publish. Supports security-hardened execution with minimal permissions.

### MCP Protocol
Exposes temporal analysis capabilities to AI clients through:
- Tools: `generate_example_timeline`, `analyze_timeline_anomalies`, `visualize_timeline`, `publish_to_exo`
- Resources: Access to timeline JSON files
- Prompts: `analyze_temporal_anomalies`, `explain_temporal_analysis`, `temporal_debugging_guide`

### Exo Platform
Bidirectional integration for enhanced observability - publishes timelines and anomalies to Exo event streams.

## File Formats

### Timeline JSON Structure
```json
{
  "name": "Timeline Name",
  "description": "Description",
  "points": [
    {
      "event_id": "unique_id",
      "valid_time": "ISO8601_timestamp",
      "transaction_time": "ISO8601_timestamp",
      "decision_time": "ISO8601_timestamp",
      "event_type": "category",
      "data": {}
    }
  ]
}
```

## Dependencies

Core dependencies are security-pinned in `requirements.txt`. Key modules:
- `matplotlib`: For visualization (optional, graceful degradation)
- `rich`: For enhanced terminal output
- `mcp`: Model Context Protocol implementation
- `fastapi`/`pydantic`: For API structures
- `exo-platform-client`: Exo integration (placeholder)

## Security Considerations

- **Read-only by default**: Diagnostics mode only reads data
- **Guarded write mode**: Enabled only with `LEXTRI_WRITE_OK=true` environment variable
- **Sandboxed execution**: Debug hooks run in isolated containers
- **Argument validation**: All CLI inputs undergo security sanitization
- **Minimal permissions**: GitHub Action uses least-privilege access