#!/bin/bash

# Enhanced Codex Activation Fix
# Fixes "spawn node ENOENT" errors and ensures ChatGPT CLI works with VS Code

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
    echo -e "${GREEN}[✅]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌]${NC} $1"
}

echo "🔧 Enhanced Codex Integration Fix..."
echo ""

# Pre-flight checks for Node.js environment
check_node_environment() {
    log_info "Checking Node.js environment..."
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found! This causes 'spawn node ENOENT' errors."
        log_warning "Running Node.js environment repair utility..."
        
        if [[ -f ./fix-node-spawn-error.sh ]]; then
            ./fix-node-spawn-error.sh
        else
            log_error "Node.js repair utility not found."
            log_info "Please install Node.js manually from https://nodejs.org/"
            log_info "Or run: brew install node (on macOS)"
            return 1
        fi
    else
        log_success "Node.js found: $(node --version)"
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        log_error "npm not found!"
        return 1
    else
        log_success "npm found: $(npm --version)"
    fi
    
    return 0
}

# Enhanced ChatGPT CLI check with error handling
check_chatgpt_cli() {
    log_info "Checking ChatGPT CLI installation..."
    
    if ! command -v chatgpt &> /dev/null; then
        log_warning "ChatGPT CLI not found. This causes spawn errors."
        log_info "Attempting to install ChatGPT CLI..."
        
        # Try to install with better error handling
        if npm install -g chatgpt-cli 2>/dev/null; then
            log_success "ChatGPT CLI installed successfully"
        else
            log_warning "Global installation failed. Trying local installation..."
            if npm install chatgpt-cli 2>/dev/null; then
                log_success "ChatGPT CLI installed locally"
                # Add to PATH for current session
                export PATH="$PWD/node_modules/.bin:$PATH"
                log_info "Added local node_modules to PATH"
            else
                log_error "ChatGPT CLI installation failed"
                log_info "You can try: sudo npm install -g chatgpt-cli"
                return 1
            fi
        fi
    else
        log_success "ChatGPT CLI found at: $(which chatgpt)"
    fi
    
    return 0
}

# Test connectivity and API access
test_connectivity() {
    log_info "Testing API connectivity..."
    
    # Test basic internet connectivity
    if timeout 5 curl -s https://api.openai.com > /dev/null 2>&1; then
        log_success "OpenAI API endpoint accessible"
    else
        log_warning "OpenAI API endpoint not accessible (may cause 503 errors)"
        log_info "Check your internet connection or VPN settings"
    fi
}

# Run pre-flight checks
if ! check_node_environment; then
    log_error "Node.js environment issues detected"
    log_info "Please fix Node.js installation before continuing"
    exit 1
fi

if ! check_chatgpt_cli; then
    log_error "ChatGPT CLI issues detected"
    log_info "You may encounter spawn errors until this is resolved"
fi

test_connectivity

echo ""
log_info "Loading API keys..."

# 1. Check if API key exists in secure storage
if [[ -f ~/.ai-keys/env_vars ]]; then
    source ~/.ai-keys/env_vars
    log_success "Loaded API keys from secure storage"
fi

# 2. Export for current session
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    export OPENAI_API_KEY
    log_success "OpenAI API key is set"

    # Enhanced ChatGPT CLI test with error handling
    log_info "Testing ChatGPT CLI functionality..."
    if command -v chatgpt &> /dev/null; then
        if echo "Say 'CLI Working'" | timeout 10 chatgpt 2>/dev/null | head -n 3; then
            log_success "ChatGPT CLI is working properly"
        else
            log_warning "ChatGPT CLI test failed - check API key or connectivity"
        fi
    else
        log_error "ChatGPT CLI not available for testing"
    fi

    echo ""
    log_success "Codex should now be active!"
    echo ""
    echo "To use in VS Code:"
    echo "1. Open Command Palette: Cmd+Shift+P"
    echo "2. Type: 'ChatGPT: Ask ChatGPT'"
    echo "3. Or use terminal: chatgpt 'your question'"
else
    log_error "No OpenAI API key found!"
    echo ""
    echo "Run this to set it up:"
    echo "  ./secure-setup-keys.sh"
    echo ""
    echo "Or set manually:"
    echo "  export OPENAI_API_KEY='your-key-here'"
fi

echo ""
echo "🤝 For best collaboration:"
echo "• Use Claude (me) for complex coding & architecture"
echo "• Use ChatGPT for quick checks & alternative solutions"
echo "• We work better together!"
echo ""

# Final status check
if command -v node &> /dev/null && command -v chatgpt &> /dev/null && [[ -n "${OPENAI_API_KEY:-}" ]]; then
    log_success "All systems ready! No more spawn errors expected."
else
    log_warning "Some issues remain. Check the messages above for guidance."
    echo ""
    echo "🔧 For troubleshooting, run: ./fix-node-spawn-error.sh"
fi