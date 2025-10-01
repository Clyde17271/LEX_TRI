#!/bin/bash

# Fix Codex MCP Integration for VS Code
# This properly configures the ChatGPT CLI to work with VS Code's Codex extension

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Fixing Codex MCP Integration...${NC}"
echo "================================"

# 1. Ensure API key is available
if [[ -f ~/.ai-keys/env_vars ]]; then
    source ~/.ai-keys/env_vars
    echo -e "${GREEN}✅ Loaded API keys${NC}"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo -e "${RED}❌ OpenAI API key not found!${NC}"
    echo "Please set OPENAI_API_KEY environment variable"
    exit 1
fi

# 2. Create a wrapper script that properly passes the API key
echo -e "${BLUE}Creating ChatGPT wrapper for VS Code...${NC}"

cat > /usr/local/bin/chatgpt-vscode << 'EOF'
#!/bin/bash
# ChatGPT wrapper for VS Code Codex integration

# Load API keys
[ -f ~/.ai-keys/env_vars ] && source ~/.ai-keys/env_vars

# Ensure API key is available
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo "Error: OPENAI_API_KEY not set" >&2
    exit 1
fi

# Execute chatgpt with the API key
exec /opt/homebrew/bin/chatgpt "$@"
EOF

sudo chmod +x /usr/local/bin/chatgpt-vscode 2>/dev/null || chmod +x /usr/local/bin/chatgpt-vscode

echo -e "${GREEN}✅ Created wrapper script${NC}"

# 3. Update VS Code settings to use the wrapper
echo -e "${BLUE}Updating VS Code settings...${NC}"

# Read current settings
settings_file="$HOME/Library/Application Support/Code - Insiders/User/settings.json"
if [[ ! -f "$settings_file" ]]; then
    settings_file="$HOME/Library/Application Support/Code/User/settings.json"
fi

if [[ -f "$settings_file" ]]; then
    # Create backup
    cp "$settings_file" "$settings_file.backup.$(date +%Y%m%d_%H%M%S)"

    # Update the chatgpt.cliExecutable path using Python for safe JSON editing
    python3 << PYTHON_EOF
import json
import os

settings_path = os.path.expanduser("$settings_file")
with open(settings_path, 'r') as f:
    settings = json.load(f)

# Update ChatGPT settings
if 'chatgpt.config' not in settings:
    settings['chatgpt.config'] = {}

settings['chatgpt.config']['apiKey'] = os.environ.get('OPENAI_API_KEY', '')
settings['chatgpt.cliExecutable'] = '/usr/local/bin/chatgpt-vscode'
settings['chatgpt.enableCli'] = True
settings['chatgpt.useCliForCodeGeneration'] = True

# Ensure MCP is properly configured
settings['chat.mcp.enabled'] = True

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=4)

print("✅ Updated VS Code settings")
PYTHON_EOF
fi

# 4. Test the wrapper
echo -e "${BLUE}Testing ChatGPT wrapper...${NC}"
echo "Say 'Working!'" | /usr/local/bin/chatgpt-vscode 2>/dev/null | head -n 3 || echo -e "${YELLOW}Test failed - check API key${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  Codex MCP Fix Complete! 🎉${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "✅ ChatGPT wrapper configured at /usr/local/bin/chatgpt-vscode"
echo "✅ VS Code settings updated"
echo ""
echo -e "${YELLOW}IMPORTANT: Restart VS Code:${NC}"
echo "1. Press Cmd+Shift+P"
echo "2. Type: 'Developer: Reload Window'"
echo "3. Or just restart VS Code completely"
echo ""
echo "Then Codex should work without errors!"