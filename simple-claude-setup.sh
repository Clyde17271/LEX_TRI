#!/bin/bash

# Simple Claude API Setup Script
# Sets up the Anthropic API key for Claude

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}[CLAUDE]${NC} Setting up Anthropic API key"
echo "============================="
echo ""

# Ask for Claude API Key
echo "Enter your Anthropic API key (sk-ant-api...): "
read CLAUDE_KEY

# Set key in current environment
export ANTHROPIC_API_KEY="$CLAUDE_KEY"
echo -e "${GREEN}[SUCCESS]${NC} Anthropic API key set in current environment"

# Add to .zshrc
echo "" >> ~/.zshrc
echo "# Anthropic Claude API key" >> ~/.zshrc
echo "export ANTHROPIC_API_KEY=\"$CLAUDE_KEY\"" >> ~/.zshrc
echo -e "${GREEN}[SUCCESS]${NC} Added API key to ~/.zshrc"

# Update Claude aliases
echo "" >> ~/.zshrc
echo "# Claude AI CLI shortcuts" >> ~/.zshrc
echo "alias claude-code='claude --system \"You are an expert programmer. Provide clean, efficient code with explanations.\"'" >> ~/.zshrc
echo "alias claude-debug='claude --system \"You are a debugging expert. Help identify and fix code issues.\"'" >> ~/.zshrc
echo "alias claude-explain='claude --system \"You are a technical educator. Explain concepts clearly and thoroughly.\"'" >> ~/.zshrc
echo "alias claude-review='claude --system \"You are a code reviewer. Provide constructive feedback and suggestions.\"'" >> ~/.zshrc
echo "alias claude-stream='claude --stream'" >> ~/.zshrc
echo "alias claude-sonnet='claude --model claude-3-5-sonnet-20241022'" >> ~/.zshrc
echo "alias claude-haiku='claude --model claude-3-haiku-20240307'" >> ~/.zshrc
echo -e "${GREEN}[SUCCESS]${NC} Added Claude aliases to ~/.zshrc"

# Source .zshrc to apply changes
source ~/.zshrc 2>/dev/null || true

echo ""
echo -e "${GREEN}[SUCCESS]${NC} Claude API key setup completed!"
echo ""
echo "Next steps:"
echo "1. Open a new terminal to load the updated environment variables"
echo "2. Restart VS Code: Cmd+Shift+P → 'Developer: Reload Window'"
echo "3. Run the Claude CLI setup script again:"
echo "   ./setup-claude-cli.sh"
echo ""
echo "To test your key in terminal:"
echo "- claude 'Hello'"
echo "- claude-code 'Write a Python function'"
echo "- claude-stream 'Explain a concept'"
echo ""
echo -e "${PURPLE}[CLAUDE]${NC} Claude is now your primary AI assistant!"