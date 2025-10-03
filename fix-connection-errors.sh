#!/bin/bash

# LEX TRI Connection Error Handler
# Fixes "503 upstream connect error" and connection issues

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MAX_RETRIES=5
RETRY_DELAY=2
TIMEOUT_DURATION=10

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
    echo -e "${MAGENTA}  LEX TRI Connection Error Handler${NC}"
    echo -e "${MAGENTA}  Fixing 503 Upstream Connect Errors${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════${NC}"
    echo ""
}

# Test connection to a URL with retry logic
test_connection_with_retry() {
    local url="$1"
    local description="$2"
    local attempt=1
    
    log_info "Testing connection to $description..."
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        log_debug "Attempt $attempt/$MAX_RETRIES for $description"
        
        if timeout $TIMEOUT_DURATION curl -s --head "$url" > /dev/null 2>&1; then
            log_success "✓ $description is accessible"
            return 0
        else
            log_warning "✗ Attempt $attempt failed for $description"
            
            if [[ $attempt -eq $MAX_RETRIES ]]; then
                log_error "✗ All attempts failed for $description"
                return 1
            fi
            
            log_debug "Waiting ${RETRY_DELAY}s before retry..."
            sleep $RETRY_DELAY
            ((attempt++))
        fi
    done
}

# Test multiple connection endpoints
test_api_endpoints() {
    log_info "Testing API endpoint connectivity..."
    
    local endpoints=(
        "https://api.openai.com|OpenAI API"
        "https://api.anthropic.com|Anthropic API"
        "https://registry.npmjs.org|NPM Registry"
        "https://nodejs.org|Node.js Official Site"
        "https://github.com|GitHub"
        "https://api.github.com|GitHub API"
    )
    
    local failed_count=0
    local total_count=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        IFS='|' read -r url description <<< "$endpoint"
        
        if ! test_connection_with_retry "$url" "$description"; then
            ((failed_count++))
        fi
        echo ""
    done
    
    echo -e "${BLUE}Connection Test Summary:${NC}"
    echo "- Successful: $((total_count - failed_count))/$total_count"
    echo "- Failed: $failed_count/$total_count"
    
    if [[ $failed_count -eq 0 ]]; then
        log_success "All endpoints are accessible"
        return 0
    elif [[ $failed_count -lt $total_count ]]; then
        log_warning "Some endpoints failed ($failed_count/$total_count)"
        return 1
    else
        log_error "All endpoints failed"
        return 2
    fi
}

# Check DNS resolution
check_dns_resolution() {
    log_info "Checking DNS resolution..."
    
    local test_domains=(
        "api.openai.com"
        "api.anthropic.com"
        "registry.npmjs.org"
        "github.com"
    )
    
    local dns_issues=0
    
    for domain in "${test_domains[@]}"; do
        if timeout 5 nslookup "$domain" > /dev/null 2>&1; then
            log_success "✓ DNS resolution for $domain"
        else
            log_error "✗ DNS resolution failed for $domain"
            ((dns_issues++))
        fi
    done
    
    if [[ $dns_issues -eq 0 ]]; then
        log_success "DNS resolution is working properly"
        return 0
    else
        log_error "DNS issues detected ($dns_issues domains failed)"
        return 1
    fi
}

# Check network configuration
check_network_config() {
    log_info "Checking network configuration..."
    
    # Check if connected to internet
    if timeout 5 ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_success "✓ Internet connectivity (ping to 8.8.8.8)"
    else
        log_error "✗ No internet connectivity"
        return 1
    fi
    
    # Check HTTP proxy settings
    if [[ -n "${HTTP_PROXY:-}" ]] || [[ -n "${HTTPS_PROXY:-}" ]]; then
        log_warning "Proxy settings detected:"
        [[ -n "${HTTP_PROXY:-}" ]] && echo "  HTTP_PROXY: $HTTP_PROXY"
        [[ -n "${HTTPS_PROXY:-}" ]] && echo "  HTTPS_PROXY: $HTTPS_PROXY"
        log_info "Proxy settings may affect API connectivity"
    else
        log_success "✓ No proxy settings detected"
    fi
    
    # Check for common firewall ports
    local common_ports=(80 443 22)
    local blocked_ports=0
    
    for port in "${common_ports[@]}"; do
        if timeout 3 nc -z google.com "$port" > /dev/null 2>&1; then
            log_success "✓ Port $port is accessible"
        else
            log_warning "✗ Port $port may be blocked"
            ((blocked_ports++))
        fi
    done
    
    if [[ $blocked_ports -gt 0 ]]; then
        log_warning "Some ports appear blocked - check firewall settings"
    fi
    
    return 0
}

# Test specific API functionality
test_api_functionality() {
    log_info "Testing API functionality..."
    
    # Test OpenAI API if key is available
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        log_info "Testing OpenAI API with key..."
        
        local response=$(timeout 15 curl -s -w "%{http_code}" \
            -H "Authorization: Bearer $OPENAI_API_KEY" \
            -H "Content-Type: application/json" \
            https://api.openai.com/v1/models \
            -o /dev/null 2>/dev/null || echo "000")
        
        case "$response" in
            "200")
                log_success "✓ OpenAI API is working (HTTP 200)"
                ;;
            "401")
                log_error "✗ OpenAI API authentication failed (HTTP 401)"
                log_info "Check your OPENAI_API_KEY"
                ;;
            "503")
                log_error "✗ OpenAI API service unavailable (HTTP 503)"
                log_info "This is the '503 upstream connect error' - try again later"
                ;;
            "000"|"timeout")
                log_error "✗ OpenAI API connection timeout"
                log_info "Check network connectivity and firewall settings"
                ;;
            *)
                log_warning "✗ OpenAI API returned HTTP $response"
                ;;
        esac
    else
        log_warning "OpenAI API key not set - skipping API test"
    fi
    
    echo ""
    
    # Test Anthropic API if key is available
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log_info "Testing Anthropic API with key..."
        
        local response=$(timeout 15 curl -s -w "%{http_code}" \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "Content-Type: application/json" \
            https://api.anthropic.com/v1/models \
            -o /dev/null 2>/dev/null || echo "000")
        
        case "$response" in
            "200")
                log_success "✓ Anthropic API is working (HTTP 200)"
                ;;
            "401")
                log_error "✗ Anthropic API authentication failed (HTTP 401)"
                log_info "Check your ANTHROPIC_API_KEY"
                ;;
            "503")
                log_error "✗ Anthropic API service unavailable (HTTP 503)"
                log_info "This is the '503 upstream connect error' - try again later"
                ;;
            "000"|"timeout")
                log_error "✗ Anthropic API connection timeout"
                log_info "Check network connectivity and firewall settings"
                ;;
            *)
                log_warning "✗ Anthropic API returned HTTP $response"
                ;;
        esac
    else
        log_warning "Anthropic API key not set - skipping API test"
    fi
}

# Generate connection diagnostic report
generate_connection_report() {
    log_info "Generating connection diagnostic report..."
    
    local report_file="connection-diagnostic-report.txt"
    
    {
        echo "LEX TRI Connection Diagnostic Report"
        echo "Generated: $(date)"
        echo "===================================="
        echo ""
        
        echo "Network Configuration:"
        echo "- Default Gateway: $(route -n get default 2>/dev/null | grep 'gateway:' | awk '{print $2}' || echo 'Unknown')"
        echo "- DNS Servers: $(cat /etc/resolv.conf 2>/dev/null | grep nameserver | awk '{print $2}' | tr '\n' ' ' || echo 'Unknown')"
        echo "- Network Interfaces:"
        ifconfig 2>/dev/null | grep -E '^[a-z]' | cut -d: -f1 | while read interface; do
            echo "  - $interface"
        done
        echo ""
        
        echo "Proxy Configuration:"
        echo "- HTTP_PROXY: ${HTTP_PROXY:-Not set}"
        echo "- HTTPS_PROXY: ${HTTPS_PROXY:-Not set}"
        echo "- NO_PROXY: ${NO_PROXY:-Not set}"
        echo ""
        
        echo "Environment Variables:"
        echo "- OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}" 
        echo "- ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
        echo ""
        
        echo "Recent Connection Attempts:"
        echo "- Timestamp: $(date)"
        echo "- Test Results: See above output"
        
    } > "$report_file"
    
    log_success "Connection diagnostic report saved to: $report_file"
}

# Provide connection troubleshooting tips
show_connection_troubleshooting() {
    echo ""
    echo -e "${MAGENTA}Connection Troubleshooting Guide:${NC}"
    echo "================================="
    echo ""
    echo -e "${YELLOW}For '503 upstream connect error':${NC}"
    echo ""
    echo "1. Wait and retry - service may be temporarily unavailable"
    echo "2. Check API service status pages:"
    echo "   - OpenAI: https://status.openai.com/"
    echo "   - Anthropic: https://status.anthropic.com/"
    echo ""
    echo "3. Try different network (mobile hotspot, different WiFi)"
    echo "4. Check for corporate firewall/proxy blocking API calls"
    echo "5. Verify API keys are correct and have proper permissions"
    echo ""
    echo -e "${YELLOW}For persistent connection issues:${NC}"
    echo ""
    echo "1. Check DNS settings (try 8.8.8.8 or 1.1.1.1)"
    echo "2. Disable VPN temporarily to test"
    echo "3. Test from different location/network"
    echo "4. Contact your network administrator"
    echo ""
    echo -e "${YELLOW}For API authentication errors:${NC}"
    echo ""
    echo "1. Verify API keys are correctly set:"
    echo "   echo \$OPENAI_API_KEY"
    echo "   echo \$ANTHROPIC_API_KEY"
    echo ""
    echo "2. Check API key permissions and usage limits"
    echo "3. Regenerate API keys if necessary"
    echo ""
    echo -e "${YELLOW}Retry strategies:${NC}"
    echo ""
    echo "1. Exponential backoff (wait 1s, 2s, 4s, 8s between retries)"
    echo "2. Circuit breaker pattern (stop retrying after repeated failures)"
    echo "3. Fallback to alternative services when available"
    echo ""
}

# Create connection retry wrapper function
create_retry_wrapper() {
    log_info "Creating connection retry wrapper..."
    
    cat > ./retry-connection.sh << 'EOF'
#!/bin/bash

# Connection Retry Wrapper
# Usage: ./retry-connection.sh <command>

MAX_RETRIES=3
RETRY_DELAY=2

command="$*"
attempt=1

echo "🔄 Running with connection retry: $command"

while [[ $attempt -le $MAX_RETRIES ]]; do
    echo "Attempt $attempt/$MAX_RETRIES..."
    
    if eval "$command"; then
        echo "✅ Command succeeded on attempt $attempt"
        exit 0
    else
        exit_code=$?
        echo "❌ Command failed on attempt $attempt (exit code: $exit_code)"
        
        if [[ $attempt -eq $MAX_RETRIES ]]; then
            echo "💥 All attempts failed"
            exit $exit_code
        fi
        
        echo "⏳ Waiting ${RETRY_DELAY}s before retry..."
        sleep $RETRY_DELAY
        ((attempt++))
        
        # Exponential backoff
        RETRY_DELAY=$((RETRY_DELAY * 2))
    fi
done
EOF
    
    chmod +x ./retry-connection.sh
    log_success "Created retry-connection.sh wrapper"
    echo ""
    echo "Usage examples:"
    echo "  ./retry-connection.sh chatgpt 'test message'"
    echo "  ./retry-connection.sh curl https://api.openai.com"
    echo ""
}

# Main execution function
main() {
    show_banner
    
    local exit_code=0
    
    # Load API keys if available
    if [[ -f ~/.ai-keys/env_vars ]]; then
        source ~/.ai-keys/env_vars
        log_info "Loaded API keys from secure storage"
    fi
    
    # Step 1: Basic network connectivity
    log_info "Step 1: Basic Network Connectivity"
    echo "=================================="
    if ! check_network_config; then
        log_error "Basic network issues detected"
        exit_code=1
    fi
    echo ""
    
    # Step 2: DNS resolution
    log_info "Step 2: DNS Resolution"
    echo "======================"
    if ! check_dns_resolution; then
        log_error "DNS resolution issues detected"
        exit_code=1
    fi
    echo ""
    
    # Step 3: API endpoints
    log_info "Step 3: API Endpoint Connectivity"
    echo "=================================="
    local endpoint_result
    test_api_endpoints
    endpoint_result=$?
    
    if [[ $endpoint_result -eq 2 ]]; then
        log_error "All API endpoints failed"
        exit_code=1
    elif [[ $endpoint_result -eq 1 ]]; then
        log_warning "Some API endpoints failed"
    fi
    echo ""
    
    # Step 4: API functionality (if keys available)
    if [[ -n "${OPENAI_API_KEY:-}" ]] || [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log_info "Step 4: API Functionality"
        echo "=========================="
        test_api_functionality
        echo ""
    fi
    
    # Step 5: Generate diagnostic report
    generate_connection_report
    echo ""
    
    # Step 6: Create retry utilities
    create_retry_wrapper
    
    # Step 7: Show troubleshooting tips
    show_connection_troubleshooting
    
    # Final status
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}═══════════════════════════════════════${NC}"
        echo -e "${GREEN}  Connection Diagnostics Complete! ✅${NC}"
        echo -e "${GREEN}═══════════════════════════════════════${NC}"
        echo ""
        log_success "Network connectivity appears healthy"
        echo ""
        echo -e "${BLUE}If you still see 503 errors:${NC}"
        echo "• The service may be temporarily down"
        echo "• Use the retry wrapper: ./retry-connection.sh <command>"
        echo "• Check service status pages"
    else
        echo -e "${RED}═══════════════════════════════════════${NC}"
        echo -e "${RED}  Connection Issues Detected ⚠️${NC}"
        echo -e "${RED}═══════════════════════════════════════${NC}"
        echo ""
        log_warning "Network connectivity issues found"
        echo ""
        echo -e "${BLUE}Recommended actions:${NC}"
        echo "1. Review the diagnostic report: cat connection-diagnostic-report.txt"
        echo "2. Follow troubleshooting guide above"
        echo "3. Contact network administrator if issues persist"
    fi
    
    echo ""
    exit $exit_code
}

# Execute main function with all arguments
main "$@"