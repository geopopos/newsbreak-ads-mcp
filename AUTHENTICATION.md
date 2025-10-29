# Authentication Guide - NewsBreak Ads MCP Server

This guide explains all available methods for providing your NewsBreak API access token to the MCP server.

## Authentication Methods

The server supports **three** authentication methods, checked in this priority order:

1. **Command-line argument** (`--token`) - Highest priority
2. **Environment variable** (`NEWSBREAK_ACCESS_TOKEN`)
3. **Not configured** - Server will exit with error

## Method 1: Command-Line Argument (Recommended)

Pass the token directly as a command-line argument.

### Advantages
✅ Explicit and clear
✅ Easy to test different tokens
✅ Works well with Claude Desktop config
✅ No need for .env file

### Usage

**Standalone:**
```bash
python server.py --token YOUR_ACCESS_TOKEN_HERE
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/path/to/server.py",
        "--token",
        "YOUR_ACCESS_TOKEN_HERE"
      ]
    }
  }
}
```

**HTTP Server:**
```bash
python server.py --token YOUR_TOKEN --transport http --port 8000
```

### When to Use
- Testing with different tokens
- Claude Desktop integration
- Deployment where env vars are inconvenient
- Quick one-off runs

---

## Method 2: Environment Variable

Store the token in the `NEWSBREAK_ACCESS_TOKEN` environment variable.

### Advantages
✅ Token not visible in command history
✅ Standard practice for secrets
✅ Works with .env files
✅ Can be set at system level

### Usage

**Using .env file (recommended for development):**

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit `.env`:
```
NEWSBREAK_ACCESS_TOKEN=your_access_token_here
```

3. Run server:
```bash
python server.py
```

**Using system environment variable:**
```bash
# macOS/Linux
export NEWSBREAK_ACCESS_TOKEN=your_token
python server.py

# Windows (PowerShell)
$env:NEWSBREAK_ACCESS_TOKEN="your_token"
python server.py
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "NEWSBREAK_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### When to Use
- Local development
- CI/CD pipelines
- Production deployments
- When you don't want token in command history

---

## Method 3: .env File Only (Most Secure for Claude Desktop)

Use a `.env` file and don't put the token in Claude Desktop config.

### Advantages
✅ **Most secure** - token never in config files
✅ Same token for multiple MCP servers
✅ Easy to update without editing config
✅ Good for shared computers

### Usage

1. Create `.env` file in project directory:
```bash
NEWSBREAK_ACCESS_TOKEN=your_access_token_here
```

2. Claude Desktop config (NO token):
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

3. Server automatically loads from `.env`

### When to Use
- Shared development machines
- When multiple users use same config
- Maximum security posture
- Don't want token in version-controlled configs

---

## Security Best Practices

### ✅ DO

- **Use .env files** for local development
- **Add .env to .gitignore** (already configured)
- **Rotate tokens** regularly
- **Use different tokens** for dev/staging/production
- **Limit token permissions** to minimum required
- **Use --token argument** for testing only

### ❌ DON'T

- **Never commit** `.env` files
- **Never commit** tokens in code or configs
- **Never share** tokens in screenshots or logs
- **Never log** the full token value
- **Don't use** production tokens in development

---

## Troubleshooting

### "ERROR: No access token provided"

**Cause:** Server couldn't find token in any location.

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Check if env var is set
echo $NEWSBREAK_ACCESS_TOKEN

# Provide token explicitly
python server.py --token YOUR_TOKEN
```

### "NewsBreak API error: Invalid token"

**Cause:** Token is invalid or expired.

**Solution:**
1. Log in to NewsBreak for Business
2. Go to Settings → API
3. Generate a new access token
4. Update your .env file or command

### Token visible in process list

**Cause:** Using --token argument exposes token in `ps` output.

**Solution:** Use environment variable instead:
```bash
# Instead of this (visible in ps):
python server.py --token secret123

# Do this (not visible in ps):
export NEWSBREAK_ACCESS_TOKEN=secret123
python server.py
```

### Token in Claude Desktop config

**Consideration:** Tokens in config files are stored in plain text.

**Options:**
1. **Most secure:** Use .env file, leave token out of config
2. **Acceptable:** Use config for development only
3. **Least secure:** Production tokens in config (avoid)

---

## Getting Your Access Token

### Via NewsBreak UI

1. Go to https://business.newsbreak.com
2. Log in to your account
3. Navigate to **Settings** → **API**
4. Click **Generate Access Token** or copy existing token
5. Store it securely

### Finding Your Token

Your token:
- Should start with a specific prefix (check NewsBreak docs)
- Is a long alphanumeric string
- Has no spaces or special characters
- Should be kept confidential

---

## Command-Line Options Reference

```bash
python server.py --help

usage: server.py [-h] [--token TOKEN] [--transport {stdio,http,sse}]
                 [--host HOST] [--port PORT] [--version]

Options:
  --token TOKEN         NewsBreak API access token
  --transport {stdio,http,sse}
                        Transport method (default: stdio)
  --host HOST          Host for HTTP/SSE (default: localhost)
  --port PORT          Port for HTTP/SSE (default: 8000)
  --version            Show version and exit
  -h, --help           Show this help message
```

---

## Examples by Use Case

### Development / Testing

```bash
# Quick test with token
python server.py --token test_token_123

# Use .env file
echo "NEWSBREAK_ACCESS_TOKEN=dev_token" > .env
python server.py
```

### Claude Desktop (Personal)

```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/Users/yourname/mcp-servers/newsbreak-ads/server.py",
        "--token",
        "your_personal_token"
      ]
    }
  }
}
```

### Claude Desktop (Secure)

```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/Users/yourname/mcp-servers/newsbreak-ads/server.py"
      ]
    }
  }
}
```
Note: Requires `.env` file in server directory

### Production HTTP Server

```bash
# Using environment variable set by deployment system
export NEWSBREAK_ACCESS_TOKEN=prod_token_from_secrets_manager
python server.py --transport http --host 0.0.0.0 --port 8000
```

### Docker Container

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Token passed at runtime via env var
ENV NEWSBREAK_ACCESS_TOKEN=""

CMD ["python", "server.py", "--transport", "http", "--host", "0.0.0.0"]
```

```bash
docker run -e NEWSBREAK_ACCESS_TOKEN=your_token newsbreak-mcp
```

---

## Priority Order (Summary)

When multiple methods are configured:

```
1. --token argument    (if provided)
   ↓ if not found
2. NEWSBREAK_ACCESS_TOKEN env var
   ↓ if not found
3. ERROR: No token configured
```

**Example:**
```bash
# .env file has: NEWSBREAK_ACCESS_TOKEN=env_token
# Command: python server.py --token cli_token

# Result: Uses cli_token (--token takes priority)
```

---

## Quick Reference

| Method | Command | Security | Best For |
|--------|---------|----------|----------|
| CLI arg | `--token ABC` | ⚠️ Low | Testing |
| Env var | `$NEWSBREAK_ACCESS_TOKEN` | ✅ Good | Production |
| .env file | From `.env` | ✅ Best | Development |
| MCP config | In `args` | ⚠️ Medium | Personal use |
| MCP env | In `env` | ✅ Good | Teams |

---

## Related Documentation

- [QUICK_START.md](QUICK_START.md) - Setup guide
- [README.md](README.md) - Full documentation
- [.env.example](.env.example) - Environment template
- [claude_desktop_config_examples.json](claude_desktop_config_examples.json) - Config examples

---

**Version:** 1.1.0
**Last Updated:** 2025-10-29
**Server:** NewsBreak Ads MCP Server
