# LEX TRI Temporal Agent - AI Coding Instructions

## Architecture Overview

LEX TRI is a **tri-temporal debugging agent** that tracks events across three synchronized timelines:

- **Valid Time (VT)**: When an event conceptually occurred in the domain
- **Transaction Time (TT)**: When the system ingested/persisted the event
- **Decision Time (DT)**: When an agent/process acted on the event

This separation helps identify whether issues stem from stale data, ingestion lag, or premature decision-making.

## Core Components

### 1. Main Entry Point (`lextri_runner.py`)

- **Security-first design**: All CLI args validated via `validate_arguments()` to prevent injection attacks
- **Multi-mode operation**: `diagnostics` (default), `example`, `visualize`, `analyze`, `exo-publish`
- **Rich CLI output**: Uses `rich.Console` for colored, structured terminal output
- **Graceful degradation**: Features work with/without optional dependencies (matplotlib, exo)

### 2. Temporal Visualization (`temporal_viz.py`)

- **Core classes**: `TemporalPoint` (single event) and `TemporalTimeline` (collection of events)
- **JSON persistence**: Timeline data serialized/deserialized for sharing and CI/CD integration
- **Anomaly detection**: Automated detection of time travel, premature decisions, ingestion lag, out-of-order processing
- **Matplotlib integration**: Conditional import pattern - functionality available without visualization

### 3. Exo Platform Integration (`exo_integration.py`)

- **Adapter pattern**: `ExoTemporalAdapter` bridges LEX TRI and Exo observability platform
- **Mock development**: Stub classes enable development without Exo platform access
- **Event conversion**: Bidirectional conversion between LEX TRI and Exo event formats

## Development Patterns

### Dependency Management

```python
# Pattern used throughout codebase
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Then check before using features
if not HAS_MATPLOTLIB:
    console.print("[yellow]Feature requires matplotlib[/yellow]")
    return
```

### CLI Command Patterns

```bash
# Generate example with anomalies
python lextri_runner.py --mode example --output test_timeline

# Analyze existing timeline
python lextri_runner.py --mode analyze --input timeline.json --output analysis.json

# Visualize with Exo integration
python lextri_runner.py --mode visualize --input timeline.json --exo-integration --exo-api-key=KEY
```

### GitHub Action Integration

- **Containerized**: Runs in Docker with non-root user for security
- **Input validation**: GitHub Action inputs map to CLI arguments with security validation
- **Output artifacts**: Can generate JSON analysis, PNG visualizations, and Exo dashboard links

## Testing Strategy

- **Unit tests**: Comprehensive coverage in `test_temporal_viz.py` and `test_exo_integration.py`
- **Conditional testing**: Tests adapt based on available dependencies
- **File I/O testing**: Uses `tempfile` for safe temporary file testing
- **Example-driven**: Tests use `generate_example_timeline()` for consistent test data

## Key Configuration

### Security Settings (`lextri_config.yml`)

```yaml
paths:
  allow_list: # Restrict operations to specific paths
    - apps/**
    - services/**
    - tests/**
modes:
  default: diagnostics # Read-only by default
  guarded_write: false # Requires explicit opt-in for mutations
```

### Docker Security

- Non-root user execution (`appuser:appuser`)
- Minimal base image (`python:3.11-slim`)
- Security-pinned dependencies with exact versions

## Working with Temporal Data

### Timeline JSON Format

```json
{
  "name": "Timeline Name",
  "points": [
    {
      "event_id": "evt_1",
      "valid_time": "2023-05-01T10:00:00",
      "transaction_time": "2023-05-01T10:00:30",
      "decision_time": "2023-05-01T10:00:45",
      "data": { "status": "normal", "value": 100 }
    }
  ]
}
```

### Anomaly Types Detected

- **time_travel**: Transaction time before valid time (critical)
- **premature_decision**: Decision before transaction (high severity)
- **ingestion_lag**: >60s gap between VT and TT (medium/high)
- **out_of_order**: Events processed out of valid time sequence

## Knowledge Sources Priority

1. GitHub Docs (primary reference)
2. Coinbase Advanced Trade API docs
3. Python/Rust standard libraries
4. FastAPI documentation
5. Docker/Kubernetes references

When implementing features, follow the established patterns of conditional imports, security validation, rich CLI output, and comprehensive error handling.
