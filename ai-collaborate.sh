#!/bin/bash

# AI Collaboration Helper - Use both Claude and ChatGPT efficiently
# This helps reduce token usage by choosing the right AI for each task

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Load API keys
[ -f ~/.ai-keys/env_vars ] && source ~/.ai-keys/env_vars

show_help() {
    echo -e "${MAGENTA}AI Collaboration Helper${NC}"
    echo "========================"
    echo ""
    echo "Usage: ./ai-collaborate.sh [option] 'your question'"
    echo ""
    echo "Options:"
    echo "  -c, --chatgpt     Use ChatGPT only"
    echo "  -a, --claude      Use Claude only (via VS Code)"
    echo "  -b, --both        Query both AIs (default)"
    echo "  -q, --quick       Quick mode (ChatGPT for simple queries)"
    echo "  -d, --deep        Deep mode (Claude for complex tasks)"
    echo "  -h, --help        Show this help"
    echo ""
    echo -e "${BLUE}Token-Saving Tips:${NC}"
    echo "• Use --quick for simple questions (saves Claude tokens)"
    echo "• Use --deep for architecture/complex code (Claude is better)"
    echo "• Use --both only when you need comparison"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./ai-collaborate.sh --quick 'What is the grep command?'"
    echo "  ./ai-collaborate.sh --deep 'Design a microservices architecture'"
    echo "  ./ai-collaborate.sh --both 'Compare React vs Vue for this project'"
}

query_chatgpt() {
    local query="$1"
    echo -e "${BLUE}🤖 ChatGPT Response:${NC}"
    echo "===================="
    echo "$query" | OPENAI_API_KEY="${OPENAI_API_KEY}" chatgpt 2>/dev/null | tee chatgpt_response.txt
    echo ""
    echo -e "${GREEN}✅ Response saved to: chatgpt_response.txt${NC}"
}

suggest_claude() {
    local query="$1"
    echo -e "${MAGENTA}🧠 For Claude's perspective:${NC}"
    echo "=========================="
    echo "1. Copy this query to Claude in VS Code:"
    echo ""
    echo "$query"
    echo ""
    echo "2. Claude excels at:"
    echo "   • Complex architectural decisions"
    echo "   • Multi-file refactoring"
    echo "   • Deep code analysis"
    echo "   • Security considerations"
}

main() {
    # Default mode
    local mode="both"
    local query=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--chatgpt)
                mode="chatgpt"
                shift
                ;;
            -a|--claude)
                mode="claude"
                shift
                ;;
            -b|--both)
                mode="both"
                shift
                ;;
            -q|--quick)
                mode="quick"
                shift
                ;;
            -d|--deep)
                mode="deep"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                query="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$query" ]]; then
        show_help
        exit 1
    fi

    case $mode in
        chatgpt|quick)
            query_chatgpt "$query"
            ;;
        claude|deep)
            suggest_claude "$query"
            ;;
        both)
            query_chatgpt "$query"
            echo ""
            suggest_claude "$query"
            ;;
    esac

    echo ""
    echo -e "${GREEN}💡 Token Usage Tip:${NC}"
    echo "Next time, consider using:"
    echo "• --quick for simple queries (saves tokens)"
    echo "• --deep for complex tasks (better quality)"
}

# Check if API key is available
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo -e "${YELLOW}⚠️  OpenAI API key not found${NC}"
    echo "Run: source ~/.zshrc"
    echo "Or: export OPENAI_API_KEY='your-key'"
    exit 1
fi

main "$@"