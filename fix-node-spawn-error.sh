#!/bin/bash

# LEX TRI Node.js Environment Repair Utility
# Fixes "spawn node ENOENT" errors and connection issues

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
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

log_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
}

# Banner
show_banner() {
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  LEX TRI Node.js Environment Repair${NC}"
    echo -e "${MAGENTA}  Fixing 'spawn node ENOENT' Errors${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════${NC}"
    echo ""
}

# Check if Node.js is installed and accessible
check_nodejs_installation() {
    log_info "Checking Node.js installation..."
    
    local node_version=""
    local npm_version=""
    local node_path=""
    local npm_path=""
    
    # Check if node command exists
    if command -v node &> /dev/null; then
        node_version=$(node --version 2>/dev/null || echo "unknown")
        node_path=$(which node 2>/dev/null || echo "not found")
        log_success "Node.js found: $node_version at $node_path"
    else
        log_error "Node.js not found in PATH"
        return 1
    fi
    
    # Check if npm command exists
    if command -v npm &> /dev/null; then
        npm_version=$(npm --version 2>/dev/null || echo "unknown")
        npm_path=$(which npm 2>/dev/null || echo "not found")
        log_success "npm found: $npm_version at $npm_path"
    else
        log_error "npm not found in PATH"
        return 1
    fi
    
    # Check Node.js version compatibility
    local major_version=$(echo "$node_version" | sed 's/v\([0-9]*\)\..*/\1/')
    if [[ "$major_version" -ge 16 ]]; then
        log_success "Node.js version $node_version is compatible"
    else
        log_warning "Node.js version $node_version may be too old (recommended: v16+)"
    fi
    
    return 0
}

# Install Node.js using available package managers
install_nodejs() {
    log_info "Installing Node.js..."
    
    # Detect OS
    local os_type=""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os_type="linux"
    else
        log_error "Unsupported OS: $OSTYPE"
        return 1
    fi
    
    # Install based on OS and available package managers
    case "$os_type" in
        "macos")
            if command -v brew &> /dev/null; then
                log_info "Installing Node.js via Homebrew..."
                brew install node
            else
                log_error "Homebrew not found. Please install Node.js manually from https://nodejs.org/"
                return 1
            fi
            ;;
        "linux")
            # Try different package managers
            if command -v apt &> /dev/null; then
                log_info "Installing Node.js via apt..."
                sudo apt update
                sudo apt install -y nodejs npm
            elif command -v yum &> /dev/null; then
                log_info "Installing Node.js via yum..."
                sudo yum install -y nodejs npm
            elif command -v dnf &> /dev/null; then
                log_info "Installing Node.js via dnf..."
                sudo dnf install -y nodejs npm
            else
                log_error "No supported package manager found. Please install Node.js manually."
                return 1
            fi
            ;;
    esac
    
    # Verify installation
    if check_nodejs_installation; then
        log_success "Node.js installation completed successfully"
        return 0
    else
        log_error "Node.js installation failed"
        return 1
    fi
}

# Check and fix PATH issues
check_and_fix_path() {
    log_info "Checking PATH configuration..."
    
    local common_node_paths=(
        "/usr/local/bin"
        "/opt/homebrew/bin"
        "/usr/bin"
        "$HOME/.local/bin"
        "$HOME/.nvm/versions/node/*/bin"
    )
    
    local found_node_path=""
    
    # Look for Node.js in common locations
    for path in "${common_node_paths[@]}"; do
        if [[ -f "$path/node" ]]; then
            found_node_path="$path"
            log_debug "Found Node.js at: $found_node_path"
            break
        fi
    done
    
    if [[ -n "$found_node_path" ]]; then
        # Check if it's in PATH
        if echo "$PATH" | grep -q "$found_node_path"; then
            log_success "Node.js path is already in PATH"
        else
            log_warning "Node.js found but not in PATH. Adding to current session..."
            export PATH="$found_node_path:$PATH"
            log_success "Added $found_node_path to PATH for current session"
            
            # Suggest permanent addition
            echo ""
            log_info "To make this permanent, add the following to your shell profile:"
            echo -e "${CYAN}echo 'export PATH=\"$found_node_path:\$PATH\"' >> ~/.bashrc${NC}"
            echo -e "${CYAN}source ~/.bashrc${NC}"
            echo ""
        fi
    else
        log_error "Node.js not found in common locations"
        return 1
    fi
    
    return 0
}

# Check ChatGPT CLI installation and fix issues
check_chatgpt_cli() {
    log_info "Checking ChatGPT CLI installation..."
    
    if command -v chatgpt &> /dev/null; then
        local chatgpt_path=$(which chatgpt)
        log_success "ChatGPT CLI found at: $chatgpt_path"
        
        # Test if it can run without errors
        if timeout 5 chatgpt --version &> /dev/null; then
            log_success "ChatGPT CLI is functional"
        else
            log_warning "ChatGPT CLI found but may have issues"
        fi
    else
        log_warning "ChatGPT CLI not found. Attempting installation..."
        install_chatgpt_cli
    fi
}

# Install ChatGPT CLI with error handling
install_chatgpt_cli() {
    log_info "Installing ChatGPT CLI..."
    
    # Ensure npm is available
    if ! command -v npm &> /dev/null; then
        log_error "npm not available. Cannot install ChatGPT CLI."
        return 1
    fi
    
    # Try global installation
    if npm install -g chatgpt-cli; then
        log_success "ChatGPT CLI installed successfully"
    else
        log_warning "Global installation failed. Trying alternative method..."
        
        # Try local installation
        if npm install chatgpt-cli; then
            log_success "ChatGPT CLI installed locally"
            
            # Add local node_modules to PATH for current session
            export PATH="$PWD/node_modules/.bin:$PATH"
            log_info "Added local node_modules to PATH for current session"
        else
            log_error "ChatGPT CLI installation failed"
            return 1
        fi
    fi
    
    # Verify installation
    if command -v chatgpt &> /dev/null; then
        log_success "ChatGPT CLI is now available"
    else
        log_error "ChatGPT CLI installation verification failed"
        return 1
    fi
}

# Test network connectivity
test_connectivity() {
    log_info "Testing network connectivity..."
    
    local test_urls=(
        "https://api.openai.com"
        "https://api.anthropic.com"
        "https://registry.npmjs.org"
        "https://nodejs.org"
    )
    
    local failed_connections=0
    
    for url in "${test_urls[@]}"; do
        log_debug "Testing connection to $url..."
        if timeout 10 curl -s --head "$url" > /dev/null 2>&1; then
            log_success "✓ Connection to $url successful"
        else
            log_error "✗ Connection to $url failed"
            ((failed_connections++))
        fi
    done
    
    if [[ $failed_connections -eq 0 ]]; then
        log_success "All connectivity tests passed"
    elif [[ $failed_connections -lt ${#test_urls[@]} ]]; then
        log_warning "Some connectivity issues detected ($failed_connections/${#test_urls[@]} failed)"
    else
        log_error "All connectivity tests failed. Check network configuration."
        return 1
    fi
    
    return 0
}

# Generate diagnostic report
generate_diagnostic_report() {
    log_info "Generating diagnostic report..."
    
    local report_file="node-spawn-diagnostic-report.txt"
    
    {
        echo "LEX TRI Node.js Environment Diagnostic Report"
        echo "Generated: $(date)"
        echo "============================================="
        echo ""
        
        echo "System Information:"
        echo "- OS: $OSTYPE"
        echo "- Shell: $SHELL"
        echo "- PATH: $PATH"
        echo ""
        
        echo "Node.js Information:"
        if command -v node &> /dev/null; then
            echo "- Node.js Version: $(node --version)"
            echo "- Node.js Path: $(which node)"
        else
            echo "- Node.js: NOT FOUND"
        fi
        
        if command -v npm &> /dev/null; then
            echo "- npm Version: $(npm --version)"
            echo "- npm Path: $(which npm)"
        else
            echo "- npm: NOT FOUND"
        fi
        echo ""
        
        echo "ChatGPT CLI Information:"
        if command -v chatgpt &> /dev/null; then
            echo "- ChatGPT CLI Path: $(which chatgpt)"
            echo "- ChatGPT CLI Version: $(chatgpt --version 2>/dev/null || echo 'unable to determine')"
        else
            echo "- ChatGPT CLI: NOT FOUND"
        fi
        echo ""
        
        echo "Environment Variables:"
        echo "- OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}" 
        echo "- ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
        echo "- NODE_PATH: ${NODE_PATH:-NOT SET}"
        echo ""
        
        echo "Installed Global npm Packages:"
        npm list -g --depth=0 2>/dev/null || echo "Unable to list global packages"
        
    } > "$report_file"
    
    log_success "Diagnostic report saved to: $report_file"
    echo ""
    echo -e "${CYAN}Report contents:${NC}"
    cat "$report_file"
}

# Provide troubleshooting recommendations
show_troubleshooting_tips() {
    echo ""
    echo -e "${MAGENTA}Troubleshooting Tips:${NC}"
    echo "====================="
    echo ""
    echo -e "${YELLOW}If you continue to see 'spawn node ENOENT' errors:${NC}"
    echo ""
    echo "1. Restart your terminal/VS Code completely"
    echo "2. Check if Node.js is in your PATH:"
    echo "   which node"
    echo ""
    echo "3. Verify npm global packages directory:"
    echo "   npm config get prefix"
    echo ""
    echo "4. Manually add Node.js to PATH (replace with your path):"
    echo "   export PATH=\"/opt/homebrew/bin:\$PATH\""
    echo ""
    echo "5. For persistent setup, add to your shell profile:"
    echo "   echo 'export PATH=\"/opt/homebrew/bin:\$PATH\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo ""
    echo -e "${YELLOW}For connection errors (503 upstream connect error):${NC}"
    echo ""
    echo "1. Check your internet connection"
    echo "2. Verify API keys are correctly set"
    echo "3. Try using a different network/VPN"
    echo "4. Check if corporate firewall is blocking API calls"
    echo ""
    echo -e "${YELLOW}Alternative ChatGPT CLI installation methods:${NC}"
    echo ""
    echo "1. Using npx (no global install needed):"
    echo "   npx chatgpt-cli 'your question'"
    echo ""
    echo "2. Using yarn instead of npm:"
    echo "   yarn global add chatgpt-cli"
    echo ""
    echo "3. Install in project directory:"
    echo "   npm install chatgpt-cli"
    echo "   ./node_modules/.bin/chatgpt 'your question'"
    echo ""
}

# Main execution function
main() {
    show_banner
    
    local exit_code=0
    
    # Step 1: Check Node.js installation
    if ! check_nodejs_installation; then
        log_warning "Node.js issues detected. Attempting repair..."
        
        # Try to fix PATH first
        if check_and_fix_path; then
            # Re-check after PATH fix
            if ! check_nodejs_installation; then
                log_warning "PATH fix didn't resolve issue. Attempting Node.js installation..."
                if ! install_nodejs; then
                    log_error "Failed to install Node.js"
                    exit_code=1
                fi
            fi
        else
            log_warning "PATH fix failed. Attempting Node.js installation..."
            if ! install_nodejs; then
                log_error "Failed to install Node.js"
                exit_code=1
            fi
        fi
    fi
    
    # Step 2: Check ChatGPT CLI
    if [[ $exit_code -eq 0 ]]; then
        check_chatgpt_cli || exit_code=1
    fi
    
    # Step 3: Test connectivity
    if [[ $exit_code -eq 0 ]]; then
        test_connectivity || log_warning "Connectivity issues detected"
    fi
    
    # Step 4: Generate diagnostic report
    generate_diagnostic_report
    
    # Step 5: Show troubleshooting tips
    show_troubleshooting_tips
    
    # Final status
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Node.js Environment Repair Complete! ✅${NC}"
        echo -e "${GREEN}════════════════════════════════════════${NC}"
        echo ""
        log_success "All checks passed. The 'spawn node ENOENT' error should be resolved."
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Restart your terminal/VS Code: Cmd+Shift+P → 'Developer: Reload Window'"
        echo "2. Try running the ChatGPT CLI: chatgpt --version"
        echo "3. Test LEX TRI integration: ./fix-codex.sh"
    else
        echo -e "${RED}═══════════════════════════════════════${NC}"
        echo -e "${RED}  Some Issues Remain ⚠️${NC}"
        echo -e "${RED}═══════════════════════════════════════${NC}"
        echo ""
        log_warning "Some issues were detected. Check the diagnostic report above."
        echo ""
        echo -e "${BLUE}Recommended actions:${NC}"
        echo "1. Review the diagnostic report: cat node-spawn-diagnostic-report.txt"
        echo "2. Follow the troubleshooting tips above"
        echo "3. Consider manual Node.js installation from https://nodejs.org/"
    fi
    
    echo ""
    exit $exit_code
}

# Execute main function with all arguments
main "$@"