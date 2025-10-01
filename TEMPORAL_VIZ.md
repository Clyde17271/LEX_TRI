# LEX TRI Temporal Visualization

## Overview

LEX TRI Temporal Visualization is a powerful extension to the LEX TRI Temporal Agent that provides advanced visualization and analysis capabilities for tri-temporal data. This module enables users to visualize the relationships between Valid Time (VT), Transaction Time (TT), and Decision Time (DT), making it easier to identify temporal anomalies and understand their impact on system behavior.

## Core Features

### 1. Timeline Visualization

Visualize temporal data across all three time dimensions (VT, TT, DT) to quickly spot:

- Transaction lag (gap between VT and TT)
- Decision lag (gap between TT and DT)
- Temporal anomalies (time travel, premature decisions, etc.)

### 2. Anomaly Detection

Automatically identify common temporal anomalies:

- **Time Travel**: Transaction time precedes valid time (impossible in normal flow)
- **Premature Decisions**: Decisions made before transaction recorded
- **Ingestion Lag**: Excessive delay between valid and transaction time
- **Out-of-Order Processing**: Events processed in a different order than they occurred

### 3. JSON Import/Export

- Save temporal timelines to JSON for sharing and future analysis
- Load timelines from JSON to continue analysis or compare with new data

## Getting Started

### Installation

The temporal visualization module requires `matplotlib` for generating visualizations:

```bash
pip install matplotlib
```

All dependencies are now included in the project's `requirements.txt`.

### Basic Usage

#### Example Timeline Generation

Generate an example timeline with intentional anomalies to understand the visualization:

```bash
python lextri_runner.py --mode example --output example_timeline
```

This will create:

- `example_timeline.json`: The timeline data
- `example_timeline.png`: Visualization of the timeline with anomalies highlighted

#### Analyzing Your Own Data

1. Create a timeline JSON file with your temporal data (see format below)
2. Run analysis to detect anomalies:

```bash
python lextri_runner.py --mode analyze --input my_timeline.json --output analysis_results.json
```

Then:

1. Visualize the timeline:

```bash
python lextri_runner.py --mode visualize --input my_timeline.json --output timeline_viz.png
```

### Timeline JSON Format

```json
{
  "name": "My Timeline",
  "points": [
    {
      "event_id": "evt_1",
      "valid_time": "2023-05-01T10:00:00",
      "transaction_time": "2023-05-01T10:00:30",
      "decision_time": "2023-05-01T10:00:45",
      "data": { "status": "normal", "value": 100 }
    },
    {
      "event_id": "evt_2",
      "valid_time": "2023-05-01T10:10:00",
      "transaction_time": "2023-05-01T10:10:30",
      "decision_time": "2023-05-01T10:10:45",
      "data": { "status": "normal", "value": 200 }
    }
  ],
  "metadata": {
    "created": "2023-05-01T12:00:00",
    "point_count": 2
  }
}
```

## Command-Line Options

```bash
usage: lextri_runner.py [-h] [--mode {diagnostics,visualize,analyze,example}] [--input INPUT] [--output OUTPUT] [--no-highlight]

LEX TRI — Temporal Agent for debugging and analyzing tri-temporal data

optional arguments:
  -h, --help            show this help message and exit
  --mode {diagnostics,visualize,analyze,example}
                        Operation mode (default: diagnostics)
  --input INPUT         Input file path for timeline data (JSON)
  --output OUTPUT       Output file path for results
  --no-highlight        Disable anomaly highlighting in visualization
```

## Integration with CI/CD

The visualization module can be integrated into CI/CD pipelines to automatically detect temporal anomalies:

```yaml
- name: Run Temporal Analysis
  run: |
    python lextri_runner.py --mode analyze --input timeline.json --output analysis.json
    
- name: Check for Anomalies
  run: |
    ANOMALY_COUNT=$(jq '.anomaly_count' analysis.json)
    if [ "$ANOMALY_COUNT" -gt 0 ]; then
      echo "::warning::Detected $ANOMALY_COUNT temporal anomalies!"
    fi
```

## Future Enhancements

1. **Interactive Web Visualization**: Browser-based interactive timeline visualizations
2. **Real-time Monitoring**: Live tracking of temporal anomalies
3. **Machine Learning Integration**: Predictive anomaly detection based on historical patterns
4. **Custom Anomaly Rules**: User-defined rules for domain-specific temporal anomaly detection
5. **Distributed Timeline Analysis**: Support for analyzing timelines across distributed systems