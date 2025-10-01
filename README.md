# LEX TRI - Temporal Debugging Agent

[![CI/CD](https://github.com/Clyde17271/LEX_TRI/actions/workflows/ci.yml/badge.svg)](https://github.com/Clyde17271/LEX_TRI/actions/workflows/ci.yml)
[![Docker](https://github.com/Clyde17271/LEX_TRI/actions/workflows/docker.yml/badge.svg)](https://github.com/Clyde17271/LEX_TRI/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LEX TRI is a sophisticated temporal debugging agent that operates across three synchronized timelines to detect anomalies, track state changes, and provide deep insights into distributed system behavior. It integrates seamlessly with the [Exo platform](https://github.com/exo-explore/exo) for enhanced observability and distributed AI model orchestration.

## 🌟 Key Features

- **Tri-Temporal Analysis**: Tracks Valid Time (VT), Transaction Time (TT), and Decision Time (DT) for comprehensive temporal debugging
- **Anomaly Detection**: Automatically identifies temporal inconsistencies like time travel, premature decisions, and out-of-order processing
- **Visual Timeline Generation**: Creates intuitive visualizations of temporal relationships
- **Exo Platform Integration**: Bidirectional sync with Exo for distributed system monitoring
- **MCP Protocol Support**: AI-native integration through Model Context Protocol for Claude and other LLMs
- **Docker Containerization**: Production-ready deployment with multi-container orchestration

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- Exo platform credentials (for integration features)

### Installation

```bash
# Clone the repository
git clone https://github.com/Clyde17271/LEX_TRI.git
cd LEX_TRI

# Install dependencies
pip install -r requirements.txt

# Run diagnostics
python lextri_runner.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# - Temporal Server: http://localhost:8080
# - MCP Server: http://localhost:8081
# - Exo Bridge: http://localhost:8082
```

## 🔗 Exo Platform Integration

LEX TRI provides deep integration with the [Exo platform](https://github.com/exo-explore/exo) for distributed AI model orchestration and observability.

### Integration Features

1. **Event Stream Publishing**: Automatically publishes temporal anomalies to Exo event streams
2. **Distributed Tracing**: Correlates temporal events across Exo's distributed nodes
3. **Model Performance Monitoring**: Tracks decision timing for AI model inference
4. **Resource Optimization**: Identifies temporal bottlenecks in distributed processing

### Configuration

Create a `.env` file with your Exo credentials:

```bash
EXO_API_KEY=your-api-key-here
EXO_API_SECRET=your-secret-here
EXO_PROJECT_ID=your-project-id
EXO_ENDPOINT=https://api.exo.com  # Optional, defaults to production
```

### Publishing to Exo

```bash
# Analyze local timeline and publish to Exo
python lextri_runner.py --mode exo-publish \
  --input timeline.json \
  --exo-integration \
  --exo-project your-project-id

# Stream real-time events to Exo
python exo_lextri_bridge.py --stream
```

### Exo Integration Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   LEX TRI Core  │────▶│  Exo Bridge  │────▶│ Exo Platform│
│                 │     │              │     │             │
│ • Temporal Viz  │     │ • Adapter    │     │ • Events    │
│ • Anomaly Det.  │     │ • Transform  │     │ • Tracing   │
│ • MCP Server    │◀────│ • Sync       │◀────│ • Analytics │
└─────────────────┘     └──────────────┘     └─────────────┘
```

### Exo-Specific Workflows

LEX TRI enhances Exo workflows by:

1. **Model Deployment Tracking**: Monitor when models are deployed vs. when they become active
2. **Inference Pipeline Analysis**: Track request flow through Exo's distributed inference pipeline
3. **Resource Allocation Timing**: Identify delays in GPU/CPU resource allocation
4. **Cross-Node Synchronization**: Detect timing issues in distributed model sharding

## 📊 Temporal Analysis Modes

### 1. Diagnostics Mode (Default)
```bash
python lextri_runner.py
```

### 2. Timeline Generation
```bash
python lextri_runner.py --mode example --output sample_timeline
```

### 3. Anomaly Analysis
```bash
python lextri_runner.py --mode analyze --input timeline.json --output analysis.json
```

### 4. Visualization
```bash
python lextri_runner.py --mode visualize --input timeline.json --output viz.png
```

## 🤖 AI Integration (MCP)

LEX TRI exposes its capabilities through Model Context Protocol for seamless AI integration:

```bash
# Start MCP server
python mcp_server.py

# Test with client
python mcp_client.py
```

Available MCP tools:
- `generate_example_timeline`
- `analyze_timeline_anomalies`
- `visualize_timeline`
- `publish_to_exo`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suites
python test_temporal_viz.py
python test_exo_integration.py
python test_mcp_integration.py
```

## 📐 Architecture

LEX TRI consists of several integrated modules:

- **Core Engine** (`temporal_viz.py`): Temporal analysis and anomaly detection
- **CLI Runner** (`lextri_runner.py`): Command-line interface and argument validation
- **Exo Integration** (`exo_integration.py`, `exo_lextri_bridge.py`): Bidirectional Exo sync
- **MCP Server** (`mcp_server.py`): AI client integration
- **Database** (`temporal_database.py`): Persistence layer for temporal data
- **Visualization** (`temporal_viz.py`): Timeline rendering and graphics

## 🔒 Security

- All CLI inputs undergo security validation to prevent injection attacks
- API keys should be stored in environment variables or `.env` files
- Docker containers run with minimal privileges
- Sensitive files are excluded via `.gitignore`

## 📚 Documentation

- [TEMPORAL_VIZ.md](TEMPORAL_VIZ.md) - Temporal visualization details
- [EXO_INTEGRATION.md](EXO_INTEGRATION.md) - Complete Exo integration guide
- [CLAUDE.md](CLAUDE.md) - AI assistant integration instructions
- [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md) - Claude-specific features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Exo Platform](https://github.com/exo-explore/exo) for distributed AI infrastructure
- Anthropic for Claude and MCP protocol
- The temporal database research community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Clyde17271/LEX_TRI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Clyde17271/LEX_TRI/discussions)
- **Email**: clyde17271@github.com

---

Built with ❤️ for the distributed AI community