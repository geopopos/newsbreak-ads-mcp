# Quick Start Guide - NewsBreak Ads MCP Server

Get up and running with the NewsBreak Ads MCP server in 5 minutes.

## Prerequisites

- Python 3.10+
- NewsBreak for Business account with API access
- Access token from NewsBreak

## Installation Steps

### 1. Install Dependencies

```bash
cd newsbreak-ads-mcp-server
pip install -r requirements.txt
```

### 2. Configure Access Token

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```
NEWSBREAK_ACCESS_TOKEN=your_actual_token_here
```

### 3. Test the Server

Run locally to verify setup:

```bash
python server.py
```

You should see the server start without errors.

## Using with Claude Desktop

### macOS

1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add this configuration:

```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/Users/YOUR_USERNAME/mcps/newsbreak-ads-mcp-server/server.py"
      ],
      "env": {
        "NEWSBREAK_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

3. **Important**: Replace `/Users/YOUR_USERNAME/mcps/newsbreak-ads-mcp-server/server.py` with your actual path

4. Restart Claude Desktop

### Windows

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add similar configuration with Windows paths:

```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "C:\\path\\to\\newsbreak-ads-mcp-server\\server.py"
      ],
      "env": {
        "NEWSBREAK_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

3. Restart Claude Desktop

## First Commands to Try

Once connected to Claude Desktop, try these:

### 1. Get Your Ad Accounts

```
Get my ad accounts for organization ID 123456789
```

Claude will use: `get_ad_accounts(org_ids=["123456789"])`

### 2. List Active Campaigns

```
Show me all active campaigns for ad account 987654321
```

Claude will use: `get_campaigns(ad_account_id="987654321", online_status="ACTIVE")`

### 3. Run a Performance Report

```
Generate a performance report for ad account 987654321 from January 1 to January 31, 2024,
showing impressions, clicks, and spend by campaign
```

Claude will use: `run_performance_report(...)`

### 4. Get Campaign Summary

```
Give me a summary of campaign performance for the last 7 days for account 987654321
```

Claude will use: `get_campaign_summary(ad_account_id="987654321", days=7)`

## Troubleshooting

### Server won't start

**Error**: "NEWSBREAK_ACCESS_TOKEN environment variable not set"

**Fix**: Make sure `.env` file exists and contains your token

### Authentication fails

**Error**: "NewsBreak API error: Invalid token"

**Fix**:
1. Check your token is correct
2. Generate a new token from NewsBreak for Business
3. Update `.env` file

### Claude Desktop doesn't see the server

**Fix**:
1. Verify the path to `server.py` is correct in config
2. Make sure Python is in your PATH
3. Restart Claude Desktop after config changes
4. Check Claude Desktop logs for errors

### Permission errors

**macOS/Linux**: Make sure the run script is executable:
```bash
chmod +x run_server.sh
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) for technical details
- Check [NewsBreak API docs](https://business.newsbreak.com/business-api-doc/docs/overview/) for API reference

## Getting Your NewsBreak Access Token

1. Go to https://business.newsbreak.com
2. Log in to your account
3. Navigate to Settings → API
4. Generate or copy your access token
5. Add it to your `.env` file

## Available Tools

Quick reference of available MCP tools:

- `get_ad_accounts` - Get ad accounts by organization
- `get_campaigns` - List campaigns with filters
- `get_tracking_events` - Get tracking pixels/postbacks
- `run_performance_report` - Generate performance reports
- `get_campaign_summary` - Quick campaign overview

## Available Resources

Access via URI in Claude:

- `accounts://{org_id}/ad-accounts`
- `campaigns://{ad_account_id}/active`
- `events://{ad_account_id}/tracking`

## Support

- GitHub Issues: For server issues
- NewsBreak Support: For API/account issues
- FastMCP Docs: https://github.com/jlowin/fastmcp

---

**Ready to go!** Start asking Claude about your NewsBreak campaigns and analytics.
