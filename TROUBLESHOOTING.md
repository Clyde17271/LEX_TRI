# LEX TRI Connection & Spawn Error Solutions

This document provides comprehensive solutions for the most common LEX TRI errors: "spawn node ENOENT" and "503 upstream connect error".

## Quick Fix

For immediate resolution of both spawn and connection errors:

```bash
./troubleshoot-lextri.sh
```

## Common Errors and Solutions

### 1. "Failed to spawn Claude Code process: spawn node ENOENT"

**Cause**: Node.js is not installed or not in the system PATH.

**Quick Fix**:
```bash
./fix-node-spawn-error.sh
```

**Manual Fix**:
1. Install Node.js from https://nodejs.org/
2. Or use Homebrew: `brew install node`
3. Restart your terminal
4. Verify: `node --version`

### 2. "503 upstream connect error"

**Cause**: Network connectivity issues, API service downtime, or firewall blocking.

**Quick Fix**:
```bash
./fix-connection-errors.sh
```

**Manual Steps**:
1. Check internet connectivity
2. Verify API service status:
   - OpenAI: https://status.openai.com/
   - Anthropic: https://status.anthropic.com/
3. Test with different network/VPN
4. Check firewall settings

### 3. ChatGPT CLI Issues

**Quick Fix**:
```bash
./fix-codex.sh
```

**Manual Installation**:
```bash
npm install -g chatgpt-cli
```

## Troubleshooting Scripts

### Main Troubleshooter
```bash
./troubleshoot-lextri.sh [OPTIONS]
```

**Options:**
- `--help`: Show help message
- `--quick`: Quick diagnostics only
- `--node-only`: Fix only Node.js issues
- `--connection-only`: Fix only connection issues
- `--report-only`: Generate diagnostic report

### Specialized Scripts

1. **Node.js & Spawn Errors**: `./fix-node-spawn-error.sh`
2. **Connection & 503 Errors**: `./fix-connection-errors.sh`
3. **Codex Integration**: `./fix-codex.sh`

## Environment Setup

### API Keys
Set your API keys securely:
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Persistent Setup
Add to your shell profile (~/.bashrc, ~/.zshrc):
```bash
echo 'export OPENAI_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

## Diagnostic Reports

Generate comprehensive diagnostic information:
```bash
./troubleshoot-lextri.sh --report-only
```

This creates `lextri-comprehensive-diagnostic.txt` with:
- System configuration
- Node.js environment details
- Network connectivity status
- API accessibility tests
- Recommendations for fixes

## Connection Retry Utilities

For intermittent connection issues, use the retry wrapper:
```bash
./retry-connection.sh chatgpt "your question"
./retry-connection.sh curl https://api.openai.com
```

## VS Code Integration

After running fixes:
1. Restart VS Code: `Cmd+Shift+P` → `Developer: Reload Window`
2. Test ChatGPT commands: `Cmd+Shift+P` → `ChatGPT: Ask ChatGPT`
3. Verify terminal integration works

## Common Patterns

### Error Pattern: spawn node ENOENT
```
Error: Failed to spawn Claude Code process: spawn node ENOENT
```
**Solution**: Run `./fix-node-spawn-error.sh`

### Error Pattern: 503 upstream connect error
```
503 upstream connect error or service unavailable
```
**Solution**: Run `./fix-connection-errors.sh`

### Error Pattern: command not found: chatgpt
```
chatgpt: command not found
```
**Solution**: Run `./fix-codex.sh`

## Advanced Troubleshooting

### Check Node.js Installation
```bash
which node
node --version
echo $PATH | grep node
```

### Test API Connectivity
```bash
curl -I https://api.openai.com
curl -I https://api.anthropic.com
```

### Debug npm Global Packages
```bash
npm list -g --depth=0
npm config get prefix
```

### Check DNS Resolution
```bash
nslookup api.openai.com
nslookup api.anthropic.com
```

## Prevention

### Regular Health Checks
Run periodic diagnostics:
```bash
./troubleshoot-lextri.sh --quick
```

### Environment Validation
Before important work sessions:
```bash
# Quick validation
node --version && npm --version && chatgpt --version
```

### Update Dependencies
Keep Node.js and packages current:
```bash
# Update Node.js via Homebrew
brew upgrade node

# Update ChatGPT CLI
npm update -g chatgpt-cli
```

## Support Escalation

If automated fixes don't resolve issues:

1. **Generate diagnostic report**:
   ```bash
   ./troubleshoot-lextri.sh --report-only
   ```

2. **Check service status pages**:
   - OpenAI: https://status.openai.com/
   - Anthropic: https://status.anthropic.com/

3. **Test from different environment**:
   - Different network
   - Different machine
   - Different API keys

4. **Contact support** with diagnostic report

## File Structure

```
LEX_TRI/
├── troubleshoot-lextri.sh          # Master troubleshooter
├── fix-node-spawn-error.sh         # Node.js spawn error fixes
├── fix-connection-errors.sh        # Connection error fixes  
├── fix-codex.sh                     # Enhanced Codex integration
├── setup-chatgpt-cli.sh            # Enhanced setup script
└── TROUBLESHOOTING.md               # This documentation
```

## Version Compatibility

- **Node.js**: v16+ recommended
- **npm**: Included with Node.js
- **VS Code**: Latest version
- **ChatGPT CLI**: Latest from npm

## Security Notes

- API keys are handled securely
- No credentials stored in scripts
- Environment variable validation
- Secure key storage in ~/.ai-keys/

---

*This troubleshooting guide is maintained as part of the LEX TRI project. For updates and additional support, see the main README.md.*