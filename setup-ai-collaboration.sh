#!/bin/bash

# AI Collaboration Setup - Claude + ChatGPT Working Together
# This script configures both AI assistants for optimal collaboration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running in VS Code terminal
check_vscode_terminal() {
    if [[ -n "${TERM_PROGRAM:-}" ]] && [[ "$TERM_PROGRAM" == "vscode" ]]; then
        log_success "Running in VS Code terminal"
        return 0
    else
        log_warning "Not running in VS Code terminal - some features may not work"
        return 1
    fi
}

# Install ChatGPT CLI if needed
install_chatgpt_cli() {
    log_info "Checking ChatGPT CLI..."

    if ! command -v chatgpt &> /dev/null; then
        log_warning "ChatGPT CLI not found. Installing..."

        # Check for npm
        if ! command -v npm &> /dev/null; then
            log_error "npm not found. Please install Node.js first"
            echo "Visit: https://nodejs.org/"
            exit 1
        fi

        # Install ChatGPT CLI globally
        npm install -g chatgpt-cli

        if command -v chatgpt &> /dev/null; then
            log_success "ChatGPT CLI installed at: $(which chatgpt)"
        else
            log_error "Installation failed. Try: sudo npm install -g chatgpt-cli"
            exit 1
        fi
    else
        log_success "ChatGPT CLI found at: $(which chatgpt)"
    fi
}

# Configure API keys
configure_api_keys() {
    log_info "Configuring API keys..."

    # Check for existing keys
    local has_openai=false
    local has_anthropic=false

    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        log_success "OpenAI API key found in environment"
        has_openai=true
    fi

    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log_success "Anthropic API key found in environment"
        has_anthropic=true
    fi

    # Load from secure storage if available
    if [[ -f ~/.ai-keys/env_vars ]]; then
        source ~/.ai-keys/env_vars
        log_info "Loaded keys from secure storage"

        [[ -n "${OPENAI_API_KEY:-}" ]] && has_openai=true
        [[ -n "${ANTHROPIC_API_KEY:-}" ]] && has_anthropic=true
    fi

    # Prompt for missing keys
    if [[ "$has_openai" == false ]]; then
        log_warning "OpenAI API key not found"
        echo ""
        echo "To get your OpenAI API key:"
        echo "1. Visit: https://platform.openai.com/api-keys"
        echo "2. Create a new API key"
        echo ""
        read -sp "Enter your OpenAI API key (or press Enter to skip): " openai_key
        echo ""

        if [[ -n "$openai_key" ]]; then
            export OPENAI_API_KEY="$openai_key"
            has_openai=true
        fi
    fi

    if [[ "$has_anthropic" == false ]]; then
        log_warning "Anthropic API key not found"
        echo ""
        echo "To get your Anthropic API key:"
        echo "1. Visit: https://console.anthropic.com/settings/keys"
        echo "2. Create a new API key"
        echo ""
        read -sp "Enter your Anthropic API key (or press Enter to skip): " anthropic_key
        echo ""

        if [[ -n "$anthropic_key" ]]; then
            export ANTHROPIC_API_KEY="$anthropic_key"
            has_anthropic=true
        fi
    fi

    # Save keys if provided
    if [[ "$has_openai" == true ]] || [[ "$has_anthropic" == true ]]; then
        mkdir -p ~/.ai-keys
        chmod 700 ~/.ai-keys

        cat > ~/.ai-keys/env_vars << EOF
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
EOF
        chmod 600 ~/.ai-keys/env_vars

        # Add to shell profile if not already there
        if ! grep -q "source ~/.ai-keys/env_vars" ~/.zshrc 2>/dev/null; then
            echo "" >> ~/.zshrc
            echo "# AI API Keys" >> ~/.zshrc
            echo "[ -f ~/.ai-keys/env_vars ] && source ~/.ai-keys/env_vars" >> ~/.zshrc
            log_success "Added key loader to ~/.zshrc"
        fi
    fi
}

# Test ChatGPT CLI
test_chatgpt_cli() {
    log_info "Testing ChatGPT CLI..."

    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
        log_warning "Skipping ChatGPT test (no API key)"
        return
    fi

    # Test with a simple query
    echo "Testing ChatGPT CLI. Please respond with 'OK'" | timeout 10 chatgpt 2>/dev/null | head -n 5

    if [[ ${PIPESTATUS[1]} -eq 0 ]]; then
        log_success "ChatGPT CLI is working"
    else
        log_warning "ChatGPT CLI test failed - check your API key"
    fi
}

# Configure VS Code settings
configure_vscode_integration() {
    log_info "Configuring VS Code integration..."

    local settings_file="$HOME/Library/Application Support/Code/User/settings.json"
    local insiders_settings="$HOME/Library/Application Support/Code - Insiders/User/settings.json"

    # Check which VS Code is installed
    local vscode_settings=""
    if [[ -f "$insiders_settings" ]]; then
        vscode_settings="$insiders_settings"
        log_info "Found VS Code Insiders settings"
    elif [[ -f "$settings_file" ]]; then
        vscode_settings="$settings_file"
        log_info "Found VS Code settings"
    else
        log_warning "VS Code settings not found"
        return
    fi

    echo ""
    echo -e "${MAGENTA}VS Code Configuration Instructions:${NC}"
    echo "=================================="
    echo ""
    echo "1. Open VS Code settings: Cmd+Shift+P → 'Preferences: Open User Settings (JSON)'"
    echo ""
    echo "2. Add/update these sections:"
    echo ""
    echo -e "${BLUE}For Claude integration:${NC}"
    echo '  "claude-desktop.apiKey": "${ANTHROPIC_API_KEY}",'
    echo '  "claude-desktop.model": "claude-3-5-sonnet",'
    echo ""
    echo -e "${BLUE}For ChatGPT integration:${NC}"
    echo '  "chatgpt.apiKey": "${OPENAI_API_KEY}",'
    echo '  "chatgpt.model": "gpt-4-turbo-preview",'
    echo '  "chatgpt.cli.executable": "/opt/homebrew/bin/chatgpt",'
    echo ""
    echo -e "${BLUE}For terminal integration:${NC}"
    echo '  "terminal.integrated.env.osx": {'
    echo '    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}",'
    echo '    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"'
    echo '  },'
    echo ""
}

# Create collaboration helper script
create_collaboration_helper() {
    log_info "Creating AI collaboration helper..."

    cat > ai-collaborate.sh << 'EOF'
#!/bin/bash

# AI Collaboration Helper - Use both Claude and ChatGPT efficiently

# Usage: ./ai-collaborate.sh "your question here"

QUERY="$1"

if [[ -z "$QUERY" ]]; then
    echo "Usage: ./ai-collaborate.sh 'your question'"
    exit 1
fi

echo "🤖 Getting response from ChatGPT..."
echo "$QUERY" | chatgpt --stream 2>/dev/null | tee chatgpt_response.txt

echo ""
echo "🧠 For Claude's perspective:"
echo "1. Copy the query to Claude in VS Code"
echo "2. Compare responses for best solution"
echo ""
echo "ChatGPT response saved to: chatgpt_response.txt"
EOF

    chmod +x ai-collaborate.sh
    log_success "Created ai-collaborate.sh helper script"
}

# Main execution
main() {
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  AI Collaboration Setup - Claude + ChatGPT${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════${NC}"
    echo ""

    check_vscode_terminal || true
    install_chatgpt_cli
    configure_api_keys
    test_chatgpt_cli
    configure_vscode_integration
    create_collaboration_helper

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Setup Complete! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo "✅ Both AI assistants are configured"
    echo ""
    echo -e "${BLUE}How to use them together:${NC}"
    echo "1. Claude: Use Claude Code extension in VS Code (primary)"
    echo "2. ChatGPT: Use 'chatgpt' command in terminal or Codex extension"
    echo "3. Collaborate: Run './ai-collaborate.sh \"your question\"'"
    echo ""
    echo -e "${YELLOW}Tips for efficient token usage:${NC}"
    echo "• Use Claude for complex coding tasks and architecture"
    echo "• Use ChatGPT for quick queries and alternative perspectives"
    echo "• Compare responses when uncertain"
    echo "• Use the collaboration script to query both at once"
    echo ""
    echo "Restart VS Code to apply all settings: Cmd+Shift+P → 'Developer: Reload Window'"
    echo ""
}

# Run main function
main "$@"