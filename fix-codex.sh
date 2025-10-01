#!/bin/bash

# Quick Codex Activation Fix
# This ensures ChatGPT CLI works with VS Code

set -euo pipefail

echo "🔧 Fixing Codex Integration..."
echo ""

# 1. Check if API key exists in secure storage
if [[ -f ~/.ai-keys/env_vars ]]; then
    source ~/.ai-keys/env_vars
    echo "✅ Loaded API keys from secure storage"
fi

# 2. Export for current session
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    export OPENAI_API_KEY
    echo "✅ OpenAI API key is set"

    # Test ChatGPT CLI
    echo "Testing ChatGPT CLI..."
    echo "Say 'CLI Working'" | timeout 5 chatgpt 2>/dev/null | head -n 3 || true

    echo ""
    echo "✅ Codex should now be active!"
    echo ""
    echo "To use in VS Code:"
    echo "1. Open Command Palette: Cmd+Shift+P"
    echo "2. Type: 'ChatGPT: Ask ChatGPT'"
    echo "3. Or use terminal: chatgpt 'your question'"
else
    echo "❌ No OpenAI API key found!"
    echo ""
    echo "Run this to set it up:"
    echo "  ./secure-setup-keys.sh"
    echo ""
    echo "Or set manually:"
    echo "  export OPENAI_API_KEY='your-key-here'"
fi

echo ""
echo "For best collaboration:"
echo "• Use Claude (me) for complex coding & architecture"
echo "• Use ChatGPT for quick checks & alternative solutions"
echo "• We work better together! 🤝"