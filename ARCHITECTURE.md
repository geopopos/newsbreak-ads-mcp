# NewsBreak Ads MCP Server - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Claude     │    │   Custom     │    │     Web      │ │
│  │   Desktop    │    │     MCP      │    │   Interface  │ │
│  │              │    │   Clients    │    │              │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼───────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    MCP Protocol (JSON-RPC)
                             │
┌────────────────────────────▼──────────────────────────────┐
│                  MCP SERVER LAYER                         │
│                    (server.py)                            │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              FastMCP Framework                   │    │
│  │  • Tool Registration                             │    │
│  │  • Resource Registration                         │    │
│  │  • Request Routing                               │    │
│  │  • Error Handling                                │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │     Tools     │  │   Resources   │  │  Utilities  │ │
│  │               │  │               │  │             │ │
│  │ • get_ad_     │  │ • accounts:// │  │ • get_      │ │
│  │   accounts    │  │ • campaigns://│  │   client()  │ │
│  │ • get_        │  │ • events://   │  │             │ │
│  │   campaigns   │  │               │  │             │ │
│  │ • get_        │  │               │  │             │ │
│  │   tracking_   │  │               │  │             │ │
│  │   events      │  │               │  │             │ │
│  │ • run_        │  │               │  │             │ │
│  │   performance_│  │               │  │             │ │
│  │   report      │  │               │  │             │ │
│  │ • get_        │  │               │  │             │ │
│  │   campaign_   │  │               │  │             │ │
│  │   summary     │  │               │  │             │ │
│  └───────┬───────┘  └───────┬───────┘  └─────────────┘ │
└──────────┼──────────────────┼──────────────────────────┘
           │                  │
           └──────────┬───────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│               API CLIENT LAYER                              │
│                  (client.py)                                │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │         NewsBreakClient (AsyncContext)           │     │
│  │                                                   │     │
│  │  Components:                                      │     │
│  │  • HTTPx AsyncClient                              │     │
│  │  • Rate Limiter (Token Bucket)                    │     │
│  │  • Authentication Headers                         │     │
│  │  • Retry Logic (Exponential Backoff)              │     │
│  │  • Error Handler                                  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  API Methods:                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐    │
│  │ get_ad_     │ │ get_        │ │ run_synchronous_ │    │
│  │ accounts()  │ │ campaigns() │ │ report()         │    │
│  └─────────────┘ └─────────────┘ └──────────────────┘    │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐    │
│  │ get_events()│ │ get_ad_     │ │ get_ads()        │    │
│  │             │ │ sets()      │ │                  │    │
│  └─────────────┘ └─────────────┘ └──────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    HTTPS/TLS
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                DATA MODELS LAYER                             │
│                   (models.py)                                │
│                                                              │
│  Pydantic Models for Type Safety:                           │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐     │
│  │ AdAccount   │ │ Campaign    │ │ Event            │     │
│  │ Organization│ │ AdSet       │ │ ReportRow        │     │
│  └─────────────┘ └─────────────┘ └──────────────────┘     │
│                                                              │
│  Response Wrappers:                                          │
│  ┌──────────────────────────────────────────────────┐      │
│  │ BaseResponse (code, errMsg, data)                │      │
│  │ • AdAccountsResponse                              │      │
│  │ • CampaignsResponse                               │      │
│  │ • EventsResponse                                  │      │
│  │ • ReportResponse                                  │      │
│  └──────────────────────────────────────────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                      Validation
                           │
┌──────────────────────────▼────────────────────────────────────┐
│                  EXTERNAL API LAYER                            │
│                                                                │
│          NewsBreak Business API (v1)                           │
│   https://business.newsbreak.com/business-api/v1              │
│                                                                │
│  Endpoints:                                                    │
│  • GET  /ad-account/getGroupsByOrgIds                         │
│  • GET  /campaign/getList                                     │
│  • GET  /event/getList/{adAccountId}                          │
│  • POST /report/runSync                                       │
│  • GET  /ad-set/getList                                       │
│  • GET  /ad/getList                                           │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Tool Invocation Flow

```
1. User Request → Claude
   Example: "Get campaigns for account 12345"

2. Claude → MCP Server (via JSON-RPC)
   {
     "method": "tools/call",
     "params": {
       "name": "get_campaigns",
       "arguments": {
         "ad_account_id": "12345"
       }
     }
   }

3. MCP Server → Tool Function
   @mcp.tool()
   async def get_campaigns(ad_account_id: str, ...)

4. Tool → API Client
   async with get_client() as client:
       response = await client.get_campaigns(...)

5. API Client → Rate Limiter
   await self.rate_limiter.acquire()

6. API Client → NewsBreak API (HTTPS)
   GET /v1/campaign/getList?adAccountId=12345
   Headers: { "Access-Token": "..." }

7. NewsBreak API → Response
   {
     "code": 0,
     "data": {
       "list": [...],
       "pageNo": 1,
       "total": 42
     }
   }

8. API Client → Pydantic Model Validation
   response = CampaignsResponse(**data)

9. Tool → JSON Formatting
   return json.dumps(result, indent=2)

10. MCP Server → Claude (JSON-RPC Response)
    {
      "result": {
        "content": [{
          "type": "text",
          "text": "{ \"campaigns\": [...] }"
        }]
      }
    }

11. Claude → User
    Natural language response with data
```

### Resource Access Flow

```
1. Claude reads resource: "campaigns://12345/active"

2. MCP Server routes to resource handler
   @mcp.resource("campaigns://{ad_account_id}/active")

3. Resource handler calls API client
   Similar flow to tools (steps 4-8)

4. Returns formatted data
   Direct return of JSON string
```

## Component Details

### 1. Server Layer (server.py)

**Responsibilities:**
- Initialize FastMCP server
- Register tools and resources
- Handle MCP protocol communication
- Manage tool execution
- Format responses

**Key Components:**
- `FastMCP()` instance
- Tool decorators (`@mcp.tool()`)
- Resource decorators (`@mcp.resource()`)
- Helper function: `get_client()`

### 2. API Client Layer (client.py)

**Responsibilities:**
- HTTP communication with NewsBreak API
- Authentication management
- Rate limiting
- Retry logic
- Error handling

**Key Classes:**
- `NewsBreakClient`: Main API client
- `RateLimiter`: Token bucket rate limiter
- `NewsBreakAPIError`: Custom exception

**Features:**
- Async context manager (`async with`)
- Connection pooling (httpx.AsyncClient)
- Automatic retries with exponential backoff
- Rate limiting (10 req/s default)

### 3. Data Models Layer (models.py)

**Responsibilities:**
- Type safety and validation
- Request/response schemas
- Data transformation
- Enum definitions

**Key Models:**
- `BaseResponse`: Base for all API responses
- Entity models: `Campaign`, `AdAccount`, `Event`, etc.
- Response models: `CampaignsResponse`, etc.
- Enums: `OnlineStatus`, `OSType`, etc.

## Error Handling Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Error Sources                          │
└───────────┬──────────────────────────────────────────────┘
            │
            ├─── Network Errors (httpx.HTTPError)
            │    └─► Retry with exponential backoff (3x)
            │
            ├─── API Errors (code != 0)
            │    └─► NewsBreakAPIError → ToolError
            │
            ├─── Validation Errors (Pydantic)
            │    └─► ValidationError → ToolError
            │
            └─── Rate Limit Exceeded
                 └─► Automatic throttling
```

## Rate Limiting Strategy

```
Token Bucket Algorithm:
┌────────────────────────────────┐
│   Bucket Capacity: 10 tokens   │
│   Refill Rate: 10 tokens/sec   │
└────────────────────────────────┘

Request Flow:
1. Request arrives
2. acquire() called
3. Check if token available
4. If yes: consume token, proceed
5. If no: wait until token available
6. Execute request

Implementation:
- AsyncIO locks for thread safety
- High-resolution timing
- Configurable limits per client
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│  Environment Variable: NEWSBREAK_ACCESS_TOKEN           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  NewsBreakClient.__init__(access_token)                 │
│  • Validates token exists                               │
│  • Stores token                                         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  httpx.AsyncClient(headers={                            │
│    "Access-Token": token,                               │
│    "Content-Type": "application/json"                   │
│  })                                                     │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  All API requests include Access-Token header           │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Local STDIO Deployment

```
┌─────────────────────────────┐
│    Claude Desktop Process    │
│                             │
│  Spawns subprocess:         │
│  python server.py           │
└──────────┬──────────────────┘
           │ STDIO
           │ (stdin/stdout)
┌──────────▼──────────────────┐
│   MCP Server Process        │
│   • Reads from stdin        │
│   • Writes to stdout        │
│   • Logs to stderr          │
└─────────────────────────────┘
```

### HTTP Server Deployment

```
┌─────────────────────────────┐
│      MCP Clients            │
│  (Any HTTP client)          │
└──────────┬──────────────────┘
           │ HTTP/HTTPS
           │ POST /mcp
┌──────────▼──────────────────┐
│   FastMCP HTTP Server       │
│   • Listens on port 8000    │
│   • Handles HTTP requests   │
│   • Converts to MCP calls   │
└─────────────────────────────┘
```

### FastMCP Cloud Deployment

```
┌─────────────────────────────┐
│      MCP Clients            │
└──────────┬──────────────────┘
           │ HTTPS
┌──────────▼──────────────────┐
│   FastMCP Cloud Gateway     │
│   • HTTPS endpoint          │
│   • Authentication          │
│   • Load balancing          │
└──────────┬──────────────────┘
           │
┌──────────▼──────────────────┐
│   Your MCP Server           │
│   (Managed container)       │
└─────────────────────────────┘
```

## Scalability Considerations

### Current Design (Single Instance)
- Async I/O for concurrency
- Rate limiting prevents overload
- Suitable for: Individual users, small teams

### Future Scaling Options

1. **Horizontal Scaling**
   ```
   Load Balancer
        │
        ├─► MCP Server Instance 1
        ├─► MCP Server Instance 2
        └─► MCP Server Instance 3

   Challenges:
   - Shared rate limiting (use Redis)
   - Token management
   ```

2. **Caching Layer**
   ```
   MCP Server → Redis Cache → NewsBreak API

   Cache Strategy:
   - Campaign list: 5 min TTL
   - Events: 1 hour TTL
   - Reports: No cache (always fresh)
   ```

3. **Queue-based Processing**
   ```
   MCP Server → Task Queue → Workers → API

   Use case:
   - Async reports
   - Batch operations
   - Long-running tasks
   ```

## Security Architecture

### Threat Model & Mitigations

| Threat | Mitigation |
|--------|-----------|
| Token exposure | Environment variables, .gitignore |
| API abuse | Rate limiting, timeout |
| Man-in-the-middle | HTTPS only |
| Token theft | No logging of credentials |
| Injection attacks | Pydantic validation |
| DoS | Rate limiting, timeouts |

### Security Layers

```
┌────────────────────────────────────────┐
│  Application Layer                      │
│  • Input validation (Pydantic)         │
│  • Output sanitization                 │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│  Transport Layer                        │
│  • HTTPS/TLS 1.3                       │
│  • Certificate validation              │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│  Authentication Layer                   │
│  • Token-based auth                    │
│  • No credential storage               │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│  Configuration Layer                    │
│  • Environment variables               │
│  • Secure defaults                     │
└────────────────────────────────────────┘
```

## Monitoring & Observability

### Current Implementation
- Error logging to stderr
- FastMCP built-in logging
- Exception propagation

### Recommended Additions

```
Metrics to Track:
- Request rate (per tool)
- Response time (per endpoint)
- Error rate (by type)
- Rate limit hits
- Token validation failures

Tools:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking
- CloudWatch/DataDog for cloud
```

## Testing Strategy

### Unit Tests (Planned)
```
tests/
├── test_models.py      # Pydantic model validation
├── test_client.py      # API client with mocks
└── test_server.py      # MCP tools/resources
```

### Integration Tests (Planned)
```
tests/integration/
├── test_api_calls.py   # Real API calls (sandbox)
└── test_mcp_flow.py    # End-to-end MCP flow
```

### Manual Testing (Current)
- `test_connection.py` script
- Direct tool invocation
- Claude Desktop integration

## Performance Characteristics

### Latency Budget

```
Component                    Latency
─────────────────────────────────────
MCP Protocol Overhead        < 10ms
Tool Execution              < 50ms
API Client Overhead         < 20ms
Network (to NewsBreak)      100-500ms
API Processing              200-1000ms
Response Parsing            < 10ms
─────────────────────────────────────
Total (typical)             300-1600ms
```

### Throughput

```
Rate Limiting: 10 req/s
Concurrent requests: Limited by async I/O (100+)
Bottleneck: NewsBreak API rate limits
```

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Type safety throughout
- ✅ Scalable async design
- ✅ Comprehensive error handling
- ✅ Security best practices
- ✅ Multiple deployment options
- ✅ Extensibility for future features

The modular design allows easy addition of new tools, resources, and API endpoints while maintaining code quality and reliability.
