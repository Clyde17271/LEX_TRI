#!/bin/bash

# Setup Claude-first environment for LEX TRI
# This script configures Claude as the primary AI assistant for all tasks

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}[CLAUDE]${NC} Setting up Claude-first environment for LEX TRI"
echo "=================================================="
echo ""

# Check for required tools
echo -e "${BLUE}[INFO]${NC} Checking prerequisites..."

if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} Claude CLI not found. Please run setup-claude-cli.sh first."
    exit 1
fi

# Create Claude shortcuts for common LEX TRI tasks
echo -e "${BLUE}[INFO]${NC} Creating Claude shortcuts for LEX TRI..."

ALIASES="
# Claude LEX TRI shortcuts
alias lex-temporal='cd \"/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI\" && claude --stream --system \"You are a temporal debugging expert working with the LEX TRI system, which tracks events across Valid Time (VT), Transaction Time (TT), and Decision Time (DT). Help debug temporal anomalies in the system.\"'
alias lex-analyze='cd \"/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI\" && python lextri_runner.py --mode analyze --input test_timeline.json | claude --stream --system \"You are a temporal analysis expert. Analyze the LEX TRI output and identify anomalies, patterns, and insights.\"'
alias lex-visualize='cd \"/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI\" && python lextri_runner.py --mode visualize --input test_timeline.json'
alias lex-debug='claude --stream --system \"You are a tri-temporal debugging expert. Help diagnose issues in the LEX TRI system by examining code and temporal relationships between events.\"'
alias lex-exo='cd \"/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI\" && python lextri_runner.py --mode exo-publish --input test_timeline.json | claude --stream --system \"You are an Exo platform integration expert. Help interpret and optimize the integration of LEX TRI with Exo observability platform.\"'
"

echo "$ALIASES" >> ~/.zshrc_lextri_aliases

# Add to .zshrc if not already there
if ! grep -q "source ~/.zshrc_lextri_aliases" ~/.zshrc; then
    echo "" >> ~/.zshrc
    echo "# LEX TRI Claude aliases" >> ~/.zshrc
    echo "[ -f ~/.zshrc_lextri_aliases ] && source ~/.zshrc_lextri_aliases" >> ~/.zshrc
    echo -e "${GREEN}[SUCCESS]${NC} Added LEX TRI Claude aliases to ~/.zshrc"
else
    echo -e "${BLUE}[INFO]${NC} LEX TRI aliases already in ~/.zshrc"
fi

# Create VS Code tasks for LEX TRI with Claude
echo -e "${BLUE}[INFO]${NC} Creating VS Code tasks for LEX TRI with Claude..."

mkdir -p "/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI/.vscode"

cat > "/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI/.vscode/tasks.json" << EOF
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "LEX TRI: Generate Example Timeline",
            "type": "shell",
            "command": "python lextri_runner.py --mode example --output test_timeline",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "LEX TRI: Analyze Timeline",
            "type": "shell",
            "command": "python lextri_runner.py --mode analyze --input test_timeline.json",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            }
        },
        {
            "label": "LEX TRI: Visualize Timeline",
            "type": "shell",
            "command": "python lextri_runner.py --mode visualize --input test_timeline.json",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            }
        },
        {
            "label": "LEX TRI: Ask Claude",
            "type": "shell",
            "command": "cd \"\${workspaceFolder}\" && echo \"\${input:claudeQuery}\" | claude --stream --system \"You are a temporal debugging expert working with the LEX TRI system, which tracks events across Valid Time (VT), Transaction Time (TT), and Decision Time (DT).\"",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            }
        },
        {
            "label": "LEX TRI: Exo Integration",
            "type": "shell",
            "command": "python lextri_runner.py --mode exo-publish --input test_timeline.json",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            }
        }
    ],
    "inputs": [
        {
            "id": "claudeQuery",
            "description": "What would you like to ask Claude about LEX TRI?",
            "default": "Explain how to identify temporal anomalies in the system",
            "type": "promptString"
        }
    ]
}
EOF

echo -e "${GREEN}[SUCCESS]${NC} Created VS Code tasks for LEX TRI"

# Create launch.json for debugging with Claude assistance
cat > "/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI/.vscode/launch.json" << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "LEX TRI: Run with Python",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/lextri_runner.py",
            "args": ["--mode", "diagnostics"],
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "LEX TRI: Generate Example",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/lextri_runner.py",
            "args": ["--mode", "example", "--output", "test_timeline"],
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "LEX TRI: Analyze Timeline",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/lextri_runner.py",
            "args": ["--mode", "analyze", "--input", "test_timeline.json"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
EOF

echo -e "${GREEN}[SUCCESS]${NC} Created VS Code launch configurations for debugging"

# Create settings.json to prioritize Claude
cat > "/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI/.vscode/settings.json" << EOF
{
    "chat.preferredService": "claude-desktop",
    "chat.defaultModel": "claude-3-5-sonnet",
    "gitlens.ai.vscode.model": "claude:claude-3.5-sonnet",
    "python.analysis.extraPaths": ["."],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "claude.desktop.openOnStartup": true
}
EOF

echo -e "${GREEN}[SUCCESS]${NC} Created workspace settings to prioritize Claude"

# Create README specifically for Claude integration
cat > "/Users/cr/Desktop/EllipticHive_ AGI/Enhancements/Enhancement System Attachments/LEX_TRI/CLAUDE_INTEGRATION.md" << EOF
# Claude Integration with LEX TRI

This document explains how to use Claude with the LEX TRI temporal agent system.

## Setup

1. Ensure you have completed the \`secure-setup-keys.sh\` script to securely store your Anthropic API key
2. Run \`source ~/.zshrc\` to load environment variables and aliases

## Claude CLI Commands for LEX TRI

The following aliases are available:

- \`lex-temporal\`: Start Claude with LEX TRI temporal debugging context
- \`lex-analyze\`: Run the timeline analyzer and pipe results to Claude
- \`lex-visualize\`: Visualize the timeline (opens matplotlib display)
- \`lex-debug\`: Start Claude in debugging mode for temporal issues
- \`lex-exo\`: Run the Exo platform integration and pipe results to Claude

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
2. Use the \`--stream\` flag to get real-time responses
3. For complex code tasks, use the system prompt to specify Claude's role
4. When debugging, share both the code and the temporal data with Claude

For more information, see \`LEXTRI_FULL.md\` and \`EXO_INTEGRATION.md\`.
EOF

echo -e "${GREEN}[SUCCESS]${NC} Created CLAUDE_INTEGRATION.md documentation"

# Final success message
echo ""
echo -e "${PURPLE}[CLAUDE]${NC} Claude-first environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Open a new terminal to load the new aliases"
echo "2. Try the new LEX TRI Claude commands:"
echo "   - lex-temporal"
echo "   - lex-analyze"
echo "   - lex-debug"
echo "3. In VS Code, press Ctrl+Shift+P and try 'Tasks: Run Task' -> 'LEX TRI: Ask Claude'"
echo "4. Read CLAUDE_INTEGRATION.md for more details"
echo ""
echo -e "${GREEN}[SUCCESS]${NC} Setup complete! Claude is now your primary assistant for all LEX TRI tasks."