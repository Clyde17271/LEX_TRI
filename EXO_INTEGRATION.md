# LEX TRI - Exo Platform Integration

This document describes how to use the LEX TRI temporal agent with the Exo platform for enhanced observability and analysis capabilities.

## Overview

The LEX TRI (Temporal Reasoning Infrastructure) agent provides tri-temporal visualization and analysis capabilities. It can track and visualize three types of time:

1. **Valid Time (VT)**: When an event conceptually occurs in the domain
2. **Transaction Time (TT)**: When the event is recorded in the system
3. **Decision Time (DT)**: When decisions are made based on the event

With Exo integration, LEX TRI can publish timelines, visualizations, and anomaly detection results directly to the Exo observability platform.

## Features

- **Timeline Publishing**: Send temporal data to Exo for long-term storage and shared access
- **Anomaly Detection**: Automatically detect and publish temporal anomalies to Exo event streams
- **Dashboard Integration**: View temporal visualizations directly in Exo dashboards
- **Collaborative Analysis**: Share analysis results with your team through Exo
- **Observability**: Integrate with Exo's broader observability ecosystem

## Prerequisites

1. An Exo platform account with appropriate access permissions
2. API key for Exo platform authentication
3. Project configured in Exo for receiving timeline data

## Command-line Usage

To use LEX TRI with Exo integration via the command line:

```bash
python lextri_runner.py \
  --mode=visualize \
  --input=timeline.json \
  --output=results \
  --exo-integration \
  --exo-api-key=YOUR_API_KEY \
  --exo-project=YOUR_PROJECT \
  --exo-timeline-name="My Temporal Analysis"
```

### Available Exo Options

- `--exo-integration`: Enable Exo platform integration
- `--exo-api-key`: API key for authentication with Exo
- `--exo-project`: Project ID or name in Exo
- `--exo-timeline-name`: Name for the timeline in Exo (default: "LEX TRI Temporal Analysis")
- `--exo-publish-anomalies`: Publish detected anomalies to Exo event stream (default: true)

## GitHub Action Integration

You can use the LEX TRI GitHub Action with Exo integration in your workflows:

```yaml
- name: Run LEX TRI temporal analysis
  uses: elliptichive/lex-tri@main
  with:
    mode: visualize
    input_file: ./data/timeline.json
    output_file: ./results/analysis
    exo_integration: true
    exo_api_key: ${{ secrets.EXO_API_KEY }}
    exo_project: my-project
    exo_timeline_name: CI Pipeline Analysis
```

## Exo Dashboard Integration

Once data is published to Exo, you can:

1. Access the timeline in your Exo dashboard
2. View anomaly events in the event stream
3. Share visualizations with your team
4. Set up alerts based on detected anomalies
5. Correlate temporal anomalies with other system metrics

## Development and Testing

For local development without an Exo connection, the system will operate in mock mode, simulating the Exo integration without making actual API calls.

To run in mock mode, simply omit the `--exo-api-key` parameter:

```bash
python lextri_runner.py --mode=example --output=test_results --exo-integration
```

## Troubleshooting

If you encounter issues with the Exo integration:

1. Verify your API key and project settings
2. Check network connectivity to the Exo platform
3. Ensure your account has appropriate permissions
4. Check the LEX TRI logs for detailed error messages
5. Verify your timeline data follows the expected format

## Further Resources

- [LEX TRI Documentation](LEXTRI_FULL.md)
- [Temporal Visualization Guide](TEMPORAL_VIZ.md)
- [Exo Platform Documentation](https://exo-platform.example.com/docs)