# Claude Integration with LEX TRI

This document explains how to use Claude with the LEX TRI temporal agent system.

## Setup

1. Ensure you have completed the `secure-setup-keys.sh` script to securely store your Anthropic API key
2. Run `source ~/.zshrc` to load environment variables and aliases

## Claude CLI Commands for LEX TRI

The following aliases are available:

- `lex-temporal`: Start Claude with LEX TRI temporal debugging context
- `lex-analyze`: Run the timeline analyzer and pipe results to Claude
- `lex-visualize`: Visualize the timeline (opens matplotlib display)
- `lex-debug`: Start Claude in debugging mode for temporal issues
- `lex-exo`: Run the Exo platform integration and pipe results to Claude

## VS Code Integration

Claude is set as the default AI assistant for this workspace. Use the following features:

1. **Tasks**: Press Ctrl+Shift+P and type "Tasks: Run Task" to access LEX TRI tasks
2. **Claude Chat**: The Claude chat panel opens automatically when opening the workspace
3. **Debug with Claude**: Use the debug configurations with Claude for assistance

## Temporal Debugging with Claude

Claude has been specially configured to understand tri-temporal concepts:

- **Valid Time (VT)**: When an event conceptually occurred in the domain
- **Transaction Time (TT)**: When the system ingested/persisted the event
- **Decision Time (DT)**: When an agent/process acted on the event

When asking Claude about temporal anomalies, it will automatically analyze for:
- Time travel (TT before VT)
- Premature decisions (DT before TT)
- Ingestion lag (large gap between VT and TT)
- Out-of-order processing

## Example Prompts for Claude

1. "Analyze the patterns in this timeline for anomalies"
2. "Explain why we're seeing a premature decision anomaly at point X"
3. "Help me optimize the temporal visualization code"
4. "How can I extend the Exo integration for better observability?"

## Best Practices

1. Always provide Claude with context about the timeline you're examining
2. Use the `--stream` flag to get real-time responses
3. For complex code tasks, use the system prompt to specify Claude's role
4. When debugging, share both the code and the temporal data with Claude

For more information, see `LEXTRI_FULL.md` and `EXO_INTEGRATION.md`.
