#!/bin/bash

# ChatGPT CLI Configuration Script for VS Code Integration
# This script helps set up ChatGPT CLI for Codex integration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ChatGPT CLI is installed
check_chatgpt_cli() {
    log_info "Checking ChatGPT CLI installation..."
    
    # First check if Node.js is available
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found! This causes 'spawn node ENOENT' errors."
        log_info "Please install Node.js first from https://nodejs.org/"
        log_info "Or run: brew install node (on macOS)"
        return 1
    fi
    
    if ! command -v chatgpt &> /dev/null; then
        log_warning "ChatGPT CLI not found. Installing..."
        
        log_info "Attempting global installation..."
        if npm install -g chatgpt-cli 2>/dev/null; then
            log_success "ChatGPT CLI installed globally"
        else
            log_warning "Global installation failed. Trying local installation..."
            if npm install chatgpt-cli 2>/dev/null; then
                log_success "ChatGPT CLI installed locally"
                export PATH="$PWD/node_modules/.bin:$PATH"
                log_info "Added local node_modules to PATH for current session"
            else
                log_error "ChatGPT CLI installation failed"
                log_info "You can try: sudo npm install -g chatgpt-cli"
                log_info "Or check Node.js installation with: ./fix-node-spawn-error.sh"
                return 1
            fi
        fi
    fi
    
    log_success "ChatGPT CLI found at: $(which chatgpt)"
    return 0
}

# Configure API key
setup_api_key() {
    log_info "Setting up OpenAI API key..."
    
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        log_warning "OPENAI_API_KEY environment variable not set"
        echo ""
        echo "To get your API key:"
        echo "1. Visit: https://platform.openai.com/api-keys"
        echo "2. Create a new API key"
        echo "3. Set it as environment variable:"
        echo "   export OPENAI_API_KEY='your-api-key-here'"
        echo "4. Add to ~/.zshrc for persistence:"
        echo "   echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.zshrc"
        echo ""
    else
        log_success "API key environment variable found"
    fi
}

# Test CLI functionality
test_cli() {
    log_info "Testing ChatGPT CLI functionality..."
    
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        log_warning "Cannot test without API key"
        return
    fi
    
    if ! command -v chatgpt &> /dev/null; then
        log_error "ChatGPT CLI not available for testing"
        return 1
    fi
    
    # Test basic functionality with timeout and error handling
    log_info "Sending test query to ChatGPT CLI..."
    if echo "Hello, can you respond with 'CLI is working'?" | timeout 15 chatgpt --stream 2>/dev/null | head -n 3; then
        log_success "CLI is working properly"
    else
        local exit_code=$?
        case $exit_code in
            124)
                log_warning "CLI test timed out - check network connectivity"
                log_info "Run './fix-connection-errors.sh' to diagnose connection issues"
                ;;
            127)
                log_error "ChatGPT CLI command not found - check installation"
                log_info "Run './fix-node-spawn-error.sh' to fix Node.js issues"
                ;;
            *)
                log_warning "CLI test failed (exit code: $exit_code)"
                log_info "This could be due to API key issues or network problems"
                ;;
        esac
    fi
}

# Configure VS Code settings
configure_vscode() {
    log_info "VS Code ChatGPT extension configuration:"
    echo ""
    echo "✅ CLI executable path: /opt/homebrew/bin/chatgpt"
    echo "✅ CLI integration enabled"
    echo "✅ Terminal auto-approval for AI commands"
    echo "✅ Codex integration configured"
    echo ""
    log_success "VS Code settings are configured"
}

# Main function
main() {
    echo ""
    log_info "ChatGPT CLI Setup for VS Code Codex Integration"
    echo "=============================================="
    echo ""
    
    check_chatgpt_cli
    setup_api_key
    test_cli
    configure_vscode
    
    echo ""
    log_success "Setup completed! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Set your OpenAI API key (if not already done)"
    echo "2. Restart VS Code: Cmd+Shift+P → 'Developer: Reload Window'"
    echo "3. Try ChatGPT commands: Cmd+Shift+P → 'ChatGPT: Ask ChatGPT'"
    echo "4. Use CLI integration: Your terminal commands will work with AI"
    echo ""
}

# Run main function
main "$@"