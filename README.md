# NewsBreak Ads MCP Server

A Model Context Protocol (MCP) server for the NewsBreak Business API, built with FastMCP. This server provides tools and resources for analytics, reporting, and campaign management through the NewsBreak advertising platform.

## Features

### MCP Tools

The server provides the following tools for interacting with NewsBreak's advertising API:

#### Analytics & Reporting (Primary Focus)

- **`get_ad_accounts`** - Retrieve ad accounts for specified organization IDs
- **`get_campaigns`** - List campaigns with filtering and pagination support
- **`get_tracking_events`** - Access pixel and postback tracking events
- **`run_performance_report`** - Generate synchronous performance reports with custom metrics and dimensions
- **`get_campaign_summary`** - Quick overview of recent campaign performance

### MCP Resources

Read-only resources available through URI templates:

- **`accounts://{org_id}/ad-accounts`** - Ad accounts for an organization
- **`campaigns://{ad_account_id}/active`** - Active campaigns for an ad account
- **`events://{ad_account_id}/tracking`** - Tracking events for an ad account

## Prerequisites

- Python 3.10 or higher
- NewsBreak for Business account
- NewsBreak API Access Token

## Installation

1. **Clone or download this repository**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your NewsBreak access token:

```
NEWSBREAK_ACCESS_TOKEN=your_access_token_here
```

### Obtaining Your Access Token

1. Log in to [NewsBreak for Business](https://business.newsbreak.com)
2. Navigate to your account settings
3. Go to the API section
4. Generate or copy your access token

## Usage

The server supports multiple authentication methods and transport options.

### Command-Line Options

```bash
python server.py --help

Options:
  --token TOKEN        NewsBreak API access token (overrides environment variable)
  --transport {stdio,http,sse}
                       Transport method (default: stdio)
  --host HOST         Host for HTTP/SSE transport (default: localhost)
  --port PORT         Port for HTTP/SSE transport (default: 8000)
  --version           Show version and exit
```

### Option 1: Local Development (STDIO)

**Method 1A: Using command-line argument (RECOMMENDED)**
```bash
python server.py --token YOUR_ACCESS_TOKEN
```

**Method 1B: Using environment variable**
```bash
# Ensure .env file has NEWSBREAK_ACCESS_TOKEN set
python server.py
```

**Method 1C: Using the run script**
```bash
./run_server.sh
```

### Option 2: Claude Desktop Integration

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Method 2A: Pass token via command-line argument (RECOMMENDED - more secure)**
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/path/to/newsbreak-ads-mcp-server/server.py",
        "--token",
        "your_access_token_here"
      ]
    }
  }
}
```

**Method 2B: Pass token via environment variable**
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/path/to/newsbreak-ads-mcp-server/server.py"
      ],
      "env": {
        "NEWSBREAK_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

**Method 2C: Use .env file (most secure - no token in config)**
```json
{
  "mcpServers": {
    "newsbreak-ads": {
      "command": "python",
      "args": [
        "/path/to/newsbreak-ads-mcp-server/server.py"
      ]
    }
  }
}
```
Note: Requires `.env` file with `NEWSBREAK_ACCESS_TOKEN` in the project directory

Restart Claude Desktop after updating the configuration.

### Option 3: HTTP Server

Run as an HTTP server for remote access:

```bash
# Using command-line token
python server.py --token YOUR_TOKEN --transport http --port 8000

# Or using environment variable
python server.py --transport http --port 8000 --host 0.0.0.0

# Or using fastmcp CLI
fastmcp run server.py --transport http --port 8000
```

Server will be available at: `http://localhost:8000/mcp`

### Option 4: FastMCP Cloud

Deploy to FastMCP Cloud for instant HTTPS endpoints:

```bash
# Make sure to set NEWSBREAK_ACCESS_TOKEN in cloud environment
fastmcp deploy --config fastmcp_cloud.json
```

## Example Usage

### Get Ad Accounts

```python
# In Claude or through MCP client
use_mcp_tool(
    server="newsbreak-ads",
    tool="get_ad_accounts",
    arguments={
        "org_ids": ["123456789"]
    }
)
```

### Run Performance Report

```python
use_mcp_tool(
    server="newsbreak-ads",
    tool="run_performance_report",
    arguments={
        "ad_account_id": "987654321",
        "date_from": "2024-01-01",
        "date_to": "2024-01-31",
        "dimensions": ["date", "campaign_id"],
        "metrics": ["impressions", "clicks", "spend", "conversions"],
        "level": "campaign"
    }
)
```

### Get Campaign Summary

```python
use_mcp_tool(
    server="newsbreak-ads",
    tool="get_campaign_summary",
    arguments={
        "ad_account_id": "987654321",
        "days": 7
    }
)
```

### Access Resource

```python
read_resource(
    uri="campaigns://987654321/active"
)
```

## Available Tools

### `get_ad_accounts(org_ids: List[str])`

Retrieves all ad accounts for specified organization IDs.

**Parameters:**
- `org_ids`: List of organization IDs

**Returns:** JSON with organizations and their ad accounts

### `get_campaigns(ad_account_id: str, page_no: int = 1, page_size: int = 50, search: Optional[str] = None, online_status: Optional[str] = None)`

Lists campaigns with optional filtering and pagination.

**Parameters:**
- `ad_account_id`: Target ad account ID
- `page_no`: Page number (default: 1)
- `page_size`: Results per page - options: 5, 10, 20, 50, 100, 200, 500 (default: 50)
- `search`: Optional search query
- `online_status`: Filter by status (WARNING, INACTIVE, ACTIVE, DELETED)

**Returns:** JSON with campaigns and pagination info

### `get_tracking_events(ad_account_id: str, os_filter: Optional[str] = None)`

Retrieves tracking events (pixels and postbacks) for an ad account.

**Parameters:**
- `ad_account_id`: Target ad account ID
- `os_filter`: Optional OS filter ("IOS", "ANDROID", or "" for web)

**Returns:** JSON with tracking events

### `run_performance_report(ad_account_id: str, date_from: str, date_to: str, dimensions: Optional[List[str]] = None, metrics: Optional[List[str]] = None, level: Optional[str] = None)`

Generates a synchronous performance report.

**Parameters:**
- `ad_account_id`: Target ad account ID
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `dimensions`: Optional dimensions (e.g., ["date", "campaign_id"])
- `metrics`: Optional metrics (e.g., ["impressions", "clicks", "spend"])
- `level`: Report level ("campaign", "ad_set", "ad")

**Returns:** JSON with report data

### `get_campaign_summary(ad_account_id: str, days: int = 7)`

Quick summary of recent campaign performance.

**Parameters:**
- `ad_account_id`: Target ad account ID
- `days`: Number of days to look back (default: 7)

**Returns:** JSON with campaign summary

## Architecture

The server is built with the following components:

- **`server.py`** - Main FastMCP server with tools and resources
- **`client.py`** - NewsBreak API client wrapper with authentication and rate limiting
- **`models.py`** - Pydantic data models for type safety and validation
- **`fastmcp.json`** - FastMCP deployment configuration
- **`.env`** - Environment variables (not committed to git)

### Key Features

- **Rate Limiting**: Built-in rate limiter (10 requests/second by default)
- **Error Handling**: Automatic retry with exponential backoff
- **Type Safety**: Full Pydantic model validation
- **Async/Await**: High-performance async operations
- **Environment-based Config**: Secure credential management

## API Reference

This server implements the following NewsBreak Business API endpoints:

- `GET /v1/ad-account/getGroupsByOrgIds` - Get ad accounts
- `GET /v1/campaign/getList` - List campaigns
- `GET /v1/event/getList/{adAccountId}` - Get tracking events
- `POST /v1/report/runSync` - Run synchronous report

**Base URL**: `https://business.newsbreak.com/business-api/v1`

**Authentication**: Access-Token header

For complete API documentation, visit: https://business.newsbreak.com/business-api-doc/docs/overview/

## Troubleshooting

### "NEWSBREAK_ACCESS_TOKEN environment variable not set"

Make sure you've created a `.env` file with your access token or set it in your environment:

```bash
export NEWSBREAK_ACCESS_TOKEN=your_token_here
```

### "NewsBreak API error: Invalid token"

Your access token may be expired or invalid. Generate a new one from your NewsBreak for Business account.

### Rate Limiting

The client includes built-in rate limiting (10 req/s). If you need to adjust this:

```python
client = NewsBreakClient(access_token="...", rate_limit=5)  # 5 requests per second
```

### Connection Timeouts

Default timeout is 30 seconds. Adjust if needed:

```python
client = NewsBreakClient(access_token="...", timeout=60.0)  # 60 seconds
```

## Development

### Project Structure

```
newsbreak-ads-mcp-server/
├── server.py                   # Main MCP server
├── client.py                   # API client wrapper
├── models.py                   # Pydantic models
├── requirements.txt            # Python dependencies
├── fastmcp.json               # STDIO deployment config
├── fastmcp_cloud.json         # Cloud deployment config
├── claude_desktop_config.json # Claude Desktop example
├── run_server.sh              # Local run script
├── .env.example               # Environment template
├── .env                       # Your credentials (gitignored)
├── .gitignore
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Add support for asynchronous reports
- [ ] Implement custom report creation
- [ ] Add ad set and ad management tools
- [ ] Create comprehensive test suite
- [ ] Add more resource templates
- [ ] Implement webhook support
- [ ] Add caching layer for frequently accessed data

## License

MIT License - feel free to use and modify as needed.

## Support

For issues with:
- **This MCP server**: Open an issue in this repository
- **NewsBreak API**: Contact NewsBreak support through your business account
- **FastMCP framework**: Visit https://github.com/jlowin/fastmcp

## Links

- [NewsBreak for Business](https://business.newsbreak.com)
- [NewsBreak API Documentation](https://business.newsbreak.com/business-api-doc/docs/overview/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

Built with [FastMCP](https://github.com/jlowin/fastmcp) v2.13.0
