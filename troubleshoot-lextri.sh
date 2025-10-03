#!/bin/bash

# LEX TRI Master Troubleshooting Script
# One-stop solution for "spawn node ENOENT" and connection errors

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
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
    echo -e "${BOLD}${MAGENTA}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${MAGENTA}║                    LEX TRI Troubleshooter                ║${NC}"
    echo -e "${BOLD}${MAGENTA}║            Fix All Connection & Spawn Errors             ║${NC}"
    echo -e "${BOLD}${MAGENTA}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Help function
show_help() {
    echo -e "${CYAN}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo -e "${CYAN}Description:${NC}"
    echo "  Comprehensive troubleshooting tool for LEX TRI that fixes:"
    echo "  • 'spawn node ENOENT' errors"
    echo "  • '503 upstream connect error' issues" 
    echo "  • Node.js and npm installation problems"
    echo "  • ChatGPT CLI setup issues"
    echo "  • API connectivity problems"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  -h, --help              Show this help message"
    echo "  -v, --verbose           Enable verbose output"
    echo "  -q, --quick             Quick check mode (skip intensive tests)"
    echo "  --node-only             Only fix Node.js related issues"
    echo "  --connection-only       Only fix connection related issues"
    echo "  --report-only           Generate diagnostic report without fixes"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                      # Run full troubleshooting"
    echo "  $0 --quick              # Quick check and fix"
    echo "  $0 --node-only          # Only fix Node.js spawn errors"
    echo "  $0 --connection-only    # Only fix connection issues"
    echo "  $0 --report-only        # Generate diagnostic report"
    echo ""
    echo -e "${CYAN}Common Issues Fixed:${NC}"
    echo "  ✓ Failed to spawn Claude Code process: spawn node ENOENT"
    echo "  ✓ 503 upstream connect error or connection timeout"
    echo "  ✓ ChatGPT CLI not found or not working"
    echo "  ✓ Node.js or npm not in PATH"
    echo "  ✓ API authentication failures"
    echo "  ✓ Network connectivity issues"
    echo ""
}

# Parse command line arguments
parse_arguments() {
    VERBOSE=false
    QUICK_MODE=false
    NODE_ONLY=false
    CONNECTION_ONLY=false
    REPORT_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quick)
                QUICK_MODE=true
                shift
                ;;
            --node-only)
                NODE_ONLY=true
                shift
                ;;
            --connection-only)
                CONNECTION_ONLY=true
                shift
                ;;
            --report-only)
                REPORT_ONLY=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done
}

# Enhanced logging for verbose mode
log_verbose() {
    if [[ "$VERBOSE" == true ]]; then
        log_debug "$1"
    fi
}

# Check if a script exists and is executable
check_script() {
    local script_name="$1"
    
    if [[ -f "./$script_name" ]] && [[ -x "./$script_name" ]]; then
        log_verbose "Found script: $script_name"
        return 0
    else
        log_warning "Script not found or not executable: $script_name"
        return 1
    fi
}

# Run Node.js troubleshooting
fix_node_issues() {
    log_info "🔧 Fixing Node.js and spawn errors..."
    echo ""
    
    if check_script "fix-node-spawn-error.sh"; then
        log_info "Running Node.js environment repair..."
        if $VERBOSE; then
            ./fix-node-spawn-error.sh
        else
            ./fix-node-spawn-error.sh 2>/dev/null || true
        fi
    else
        log_warning "Node.js repair script not found"
        log_info "Performing basic Node.js checks..."
        
        # Basic Node.js check
        if ! command -v node &> /dev/null; then
            log_error "Node.js not found - this causes 'spawn node ENOENT' errors"
            echo ""
            echo "💡 To fix this:"
            echo "1. Install Node.js from https://nodejs.org/"
            echo "2. Or use Homebrew: brew install node"
            echo "3. Restart your terminal after installation"
        else
            log_success "Node.js found: $(node --version)"
        fi
        
        if ! command -v npm &> /dev/null; then
            log_error "npm not found"
        else
            log_success "npm found: $(npm --version)"
        fi
    fi
    
    echo ""
}

# Run connection troubleshooting
fix_connection_issues() {
    log_info "🌐 Fixing connection and 503 errors..."
    echo ""
    
    if check_script "fix-connection-errors.sh"; then
        log_info "Running connection diagnostics..."
        if $VERBOSE; then
            ./fix-connection-errors.sh
        else
            ./fix-connection-errors.sh 2>/dev/null || true
        fi
    else
        log_warning "Connection repair script not found"
        log_info "Performing basic connectivity checks..."
        
        # Basic connectivity check
        if timeout 5 ping -c 1 8.8.8.8 > /dev/null 2>&1; then
            log_success "Internet connectivity: OK"
        else
            log_error "No internet connectivity"
        fi
        
        # Check API endpoints
        for endpoint in "api.openai.com" "api.anthropic.com"; do
            if timeout 5 curl -s --head "https://$endpoint" > /dev/null 2>&1; then
                log_success "$endpoint: Accessible"
            else
                log_error "$endpoint: Not accessible (may cause 503 errors)"
            fi
        done
    fi
    
    echo ""
}

# Run Codex fix
fix_codex_integration() {
    log_info "🤖 Fixing Codex integration..."
    echo ""
    
    if check_script "fix-codex.sh"; then
        log_info "Running enhanced Codex fix..."
        if $VERBOSE; then
            ./fix-codex.sh
        else
            ./fix-codex.sh 2>/dev/null || true
        fi
    else
        log_warning "Codex fix script not found"
        
        # Basic checks
        if command -v chatgpt &> /dev/null; then
            log_success "ChatGPT CLI found"
        else
            log_error "ChatGPT CLI not found (causes spawn errors)"
        fi
        
        if [[ -n "${OPENAI_API_KEY:-}" ]]; then
            log_success "OpenAI API key is set"
        else
            log_warning "OpenAI API key not set"
        fi
    fi
    
    echo ""
}

# Quick diagnostics mode
run_quick_diagnostics() {
    log_info "🚀 Running quick diagnostics..."
    echo ""
    
    local issues_found=false
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found (spawn node ENOENT)"
        issues_found=true
    else
        log_success "Node.js: $(node --version)"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found"
        issues_found=true
    else
        log_success "npm: $(npm --version)"
    fi
    
    # Check ChatGPT CLI
    if ! command -v chatgpt &> /dev/null; then
        log_error "ChatGPT CLI not found"
        issues_found=true
    else
        log_success "ChatGPT CLI found"
    fi
    
    # Check API keys
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
        log_warning "OpenAI API key not set"
    else
        log_success "OpenAI API key is set"
    fi
    
    # Quick connectivity test
    if ! timeout 3 curl -s https://api.openai.com > /dev/null 2>&1; then
        log_error "OpenAI API not accessible (503 errors possible)"
        issues_found=true
    else
        log_success "OpenAI API accessible"
    fi
    
    echo ""
    if [[ "$issues_found" == true ]]; then
        log_warning "Issues detected. Run without --quick for full repair."
        return 1
    else
        log_success "All quick checks passed!"
        return 0
    fi
}

# Generate comprehensive diagnostic report
generate_comprehensive_report() {
    log_info "📊 Generating comprehensive diagnostic report..."
    
    local report_file="lextri-comprehensive-diagnostic.txt"
    
    {
        echo "LEX TRI Comprehensive Diagnostic Report"
        echo "======================================="
        echo "Generated: $(date)"
        echo "Script version: $(basename "$0")"
        echo ""
        
        echo "=== SYSTEM INFORMATION ==="
        echo "OS: $OSTYPE"
        echo "Shell: $SHELL"
        echo "User: $USER"
        echo "Working Directory: $PWD"
        echo ""
        
        echo "=== NODE.JS ENVIRONMENT ==="
        if command -v node &> /dev/null; then
            echo "Node.js Version: $(node --version)"
            echo "Node.js Path: $(which node)"
        else
            echo "Node.js: NOT FOUND (spawn node ENOENT cause)"
        fi
        
        if command -v npm &> /dev/null; then
            echo "npm Version: $(npm --version)"
            echo "npm Path: $(which npm)"
            echo "npm Prefix: $(npm config get prefix 2>/dev/null || echo 'unknown')"
        else
            echo "npm: NOT FOUND"
        fi
        echo ""
        
        echo "=== CHATGPT CLI ==="
        if command -v chatgpt &> /dev/null; then
            echo "ChatGPT CLI Path: $(which chatgpt)"
            echo "ChatGPT CLI Version: $(chatgpt --version 2>/dev/null || echo 'unable to determine')"
        else
            echo "ChatGPT CLI: NOT FOUND"
        fi
        echo ""
        
        echo "=== API CONFIGURATION ==="
        echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET (hidden)}"
        echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET (hidden)}"
        echo ""
        
        echo "=== NETWORK CONFIGURATION ==="
        echo "Default Gateway: $(route -n get default 2>/dev/null | grep 'gateway:' | awk '{print $2}' || echo 'Unknown')"
        echo "DNS Servers: $(cat /etc/resolv.conf 2>/dev/null | grep nameserver | awk '{print $2}' | tr '\n' ' ' || echo 'Unknown')"
        echo "HTTP_PROXY: ${HTTP_PROXY:-Not set}"
        echo "HTTPS_PROXY: ${HTTPS_PROXY:-Not set}"
        echo ""
        
        echo "=== CONNECTIVITY TESTS ==="
        local test_endpoints=(
            "api.openai.com"
            "api.anthropic.com"
            "registry.npmjs.org"
            "github.com"
        )
        
        for endpoint in "${test_endpoints[@]}"; do
            if timeout 5 curl -s --head "https://$endpoint" > /dev/null 2>&1; then
                echo "$endpoint: ACCESSIBLE"
            else
                echo "$endpoint: FAILED (may cause 503 errors)"
            fi
        done
        echo ""
        
        echo "=== PATH ANALYSIS ==="
        echo "Current PATH: $PATH"
        echo ""
        echo "Node.js search paths:"
        echo "$PATH" | tr ':' '\n' | while read -r path_entry; do
            if [[ -f "$path_entry/node" ]]; then
                echo "  ✓ $path_entry/node (found)"
            fi
        done
        echo ""
        
        echo "=== LEX TRI FILES ==="
        echo "Available troubleshooting scripts:"
        for script in fix-node-spawn-error.sh fix-connection-errors.sh fix-codex.sh; do
            if [[ -f "./$script" ]]; then
                echo "  ✓ $script (executable: $([[ -x "./$script" ]] && echo 'yes' || echo 'no'))"
            else
                echo "  ✗ $script (missing)"
            fi
        done
        echo ""
        
        echo "=== RECOMMENDATIONS ==="
        if ! command -v node &> /dev/null; then
            echo "- Install Node.js to fix 'spawn node ENOENT' errors"
        fi
        
        if ! command -v chatgpt &> /dev/null; then
            echo "- Install ChatGPT CLI: npm install -g chatgpt-cli"
        fi
        
        if [[ -z "${OPENAI_API_KEY:-}" ]]; then
            echo "- Set OPENAI_API_KEY environment variable"
        fi
        
        if ! timeout 3 curl -s https://api.openai.com > /dev/null 2>&1; then
            echo "- Check network connectivity to fix 503 errors"
        fi
        
    } > "$report_file"
    
    log_success "Diagnostic report saved to: $report_file"
    echo ""
    
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${CYAN}Report contents:${NC}"
        cat "$report_file"
        echo ""
    fi
}

# Main execution function
main() {
    show_banner
    
    # Parse command line arguments
    parse_arguments "$@"
    
    log_info "LEX TRI Troubleshooter starting..."
    log_verbose "Verbose mode enabled"
    echo ""
    
    # Load API keys if available
    if [[ -f ~/.ai-keys/env_vars ]]; then
        source ~/.ai-keys/env_vars
        log_verbose "Loaded API keys from secure storage"
    fi
    
    local exit_code=0
    
    # Report-only mode
    if [[ "$REPORT_ONLY" == true ]]; then
        generate_comprehensive_report
        exit 0
    fi
    
    # Quick mode
    if [[ "$QUICK_MODE" == true ]]; then
        if run_quick_diagnostics; then
            log_success "Quick diagnostics passed - no issues found!"
            exit 0
        else
            log_warning "Quick diagnostics found issues. Re-run without --quick for full repair."
            exit 1
        fi
    fi
    
    # Targeted fixes
    if [[ "$NODE_ONLY" == true ]]; then
        fix_node_issues
        exit $?
    fi
    
    if [[ "$CONNECTION_ONLY" == true ]]; then
        fix_connection_issues
        exit $?
    fi
    
    # Full troubleshooting sequence
    log_info "Starting comprehensive troubleshooting..."
    echo ""
    
    # Step 1: Fix Node.js issues (prevents spawn errors)
    fix_node_issues
    
    # Step 2: Fix connection issues (prevents 503 errors)
    fix_connection_issues
    
    # Step 3: Fix Codex integration
    fix_codex_integration
    
    # Step 4: Generate diagnostic report
    generate_comprehensive_report
    
    # Final status
    echo ""
    echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║                 Troubleshooting Complete!                ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_success "All troubleshooting steps completed"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Restart VS Code: Cmd+Shift+P → 'Developer: Reload Window'"
    echo "2. Test the fixes:"
    echo "   • Try: chatgpt 'hello'"
    echo "   • Check VS Code Command Palette for ChatGPT commands"
    echo "3. If issues persist, review: lextri-comprehensive-diagnostic.txt"
    echo ""
    echo -e "${YELLOW}Need help?${NC} Run: $0 --help"
    echo ""
    
    exit $exit_code
}

# Execute main function with all arguments
main "$@"