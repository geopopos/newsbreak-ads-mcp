# Changelog

All notable changes to the NewsBreak Ads MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2025-10-29

### Added
- **CRITICAL DEBUG**: Enhanced MCP tool parameter logging
  - Added comprehensive debug logging at MCP tool entry point
  - Logs exact parameters received from Claude/MCP (values and types)
  - Helps diagnose parameter transformation issues
  - Located at server.py lines 270-279

### Investigation
- Direct Python client tests: ✅ API calls work perfectly
- Direct curl tests: ✅ API calls work perfectly
- MCP tool calls through Claude: ❌ Still failing with "illegal format" error
- **Conclusion**: Issue is NOT with API format or client code
- **Hypothesis**: Parameter transformation in MCP/FastMCP layer
- See INVESTIGATION_RESULTS.md for full details

### Testing
- Created test_api_directly.py to verify client works independently
- Tested with January dates (2025-01-22 to 2025-01-29): ✅ SUCCESS
- Tested with October dates (2025-10-22 to 2025-10-29): ✅ SUCCESS
- Tested with level="campaign" parameter: ✅ SUCCESS
- All tests return valid data from API

## [1.1.3] - 2025-10-29

### Fixed
- **CRITICAL**: Removed `timezone` parameter from report request
  - Official API example doesn't include timezone parameter
  - Simplified report name format to match API documentation
  - Request now matches exact format from official docs

### Added
- Enhanced debug logging to troubleshoot format errors
- Extended dimension/metric mappings with common aliases
- Comprehensive debugging guide (DEBUGGING_REPORTS.md)

## [1.1.2] - 2025-10-29

### Fixed
- **CRITICAL**: Updated to use OFFICIAL NewsBreak API format from documentation
  - Now uses UPPERCASE enum values (DATE, CAMPAIGN, COST, IMPRESSION, etc.)
  - Added proper parameter mapping for user-friendly names
  - Includes required parameters: dateRange, filter, filterIds, dataSource
  - Uses HOURLY dataSource (official settlement basis)
  - filterIds now correctly passes ad_account_id as integer
  - Added dimension/metric aliases (spend→COST, impressions→IMPRESSION, etc.)

## [1.1.1] - 2025-10-29

### Fixed
- **CRITICAL**: Fixed 404 error in `run_performance_report`
  - Changed endpoint from `/report/runSync` to `/reports/getIntegratedReport`
  - The original endpoint URL was incorrect
  - Now uses the correct NewsBreak API reporting endpoint
- Fixed request format (intermediate attempt before finding official docs)

## [1.1.0] - 2025-10-29

### Added
- Command-line argument support for access token (`--token`)
- Multiple transport options (`--transport`, `--host`, `--port`)
- Version flag (`--version`)
- Help flag (`--help`)
- Comprehensive authentication guide (AUTHENTICATION.md)
- Example Claude Desktop configurations (claude_desktop_config_examples.json)
- Debug logging for report API responses

### Changed
- **BREAKING FIX**: Made `code` field optional in `BaseResponse` model
- Enhanced error handling for different API response formats
- Updated client to detect error responses without `code` field
- Improved error messages with more context
- Updated README.md with command-line options
- Updated QUICK_START.md with multiple authentication methods

### Fixed
- **Critical**: Fixed `run_performance_report` Pydantic validation error
- Fixed handling of API error responses with non-standard formats
- Added HTTP status code checking before response parsing
- Added detection for error responses with `timestamp` + `url` format

### Security
- Added option to pass token via command-line for better flexibility
- Documented secure authentication practices
- Token handling priority: CLI arg > environment variable

## [1.0.0] - 2025-10-29

### Added
- Initial release of NewsBreak Ads MCP Server
- 5 MCP tools for analytics and reporting
  - `get_ad_accounts`
  - `get_campaigns`
  - `get_tracking_events`
  - `run_performance_report`
  - `get_campaign_summary`
- 3 MCP resources for read-only data access
  - `accounts://{org_id}/ad-accounts`
  - `campaigns://{ad_account_id}/active`
  - `events://{ad_account_id}/tracking`
- Full async API client with rate limiting (10 req/s)
- Type-safe Pydantic models for all API entities
- Comprehensive error handling and retry logic
- Multiple deployment options (STDIO, HTTP, Cloud)
- Complete documentation suite
  - README.md
  - QUICK_START.md
  - PROJECT_REQUIREMENTS.md
  - ARCHITECTURE.md
  - PROJECT_SUMMARY.txt
  - INDEX.md
- Configuration files for all deployment methods
- Helper scripts (run_server.sh, test_connection.py, find_my_ids.py)

### Technical Details
- Built with FastMCP v2.13.0
- Python 3.10+ required
- NewsBreak Business API v1 integration
- Access-Token based authentication
- Automatic retry with exponential backoff
- Connection pooling with httpx.AsyncClient

---

## Issue Fixes

### [1.1.0] - run_performance_report Validation Error

**Issue**: The `run_performance_report` tool was failing with Pydantic validation error:
```
Unexpected error: 1 validation error for ReportResponse
code
  Field required [type=missing, input_value={'timestamp': '2025-10-29...
```

**Root Cause**: The NewsBreak API was returning error responses with a different format than expected:
- Standard response: `{ "code": 0, "data": {...} }`
- Error response: `{ "timestamp": "...", "url": "...", "message": "..." }`

The `BaseResponse` model required the `code` field, but error responses didn't include it.

**Fix**:
1. Made `code` field optional in `BaseResponse` model
2. Added additional optional fields for error responses (`message`, `error`, `timestamp`, `url`)
3. Enhanced client error detection to:
   - Check HTTP status codes first (>=400 = error)
   - Detect error responses with `timestamp` + `url` format
   - Handle responses with or without `code` field
4. Added debug logging to report responses for troubleshooting
5. Better error messages with full context

**Testing**: After applying this fix, the server should:
- Handle both successful and error responses correctly
- Provide clear error messages from the API
- Log raw responses for debugging when needed
- Not crash on validation errors

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

**No breaking changes for existing deployments**, but you can now take advantage of new features:

1. **Command-line arguments** (optional):
   ```bash
   # Old way (still works)
   python server.py

   # New way (more flexible)
   python server.py --token YOUR_TOKEN
   python server.py --transport http --port 8000
   ```

2. **Claude Desktop config** (optional enhancement):
   ```json
   {
     "mcpServers": {
       "newsbreak-ads": {
         "command": "python",
         "args": [
           "/path/to/server.py",
           "--token",
           "your_token_here"
         ]
       }
     }
   }
   ```

3. **Update your code** (if you cloned the repo):
   ```bash
   git pull
   # No dependency changes, no reinstall needed
   ```

4. **Check for issues**:
   - If `run_performance_report` was failing, it should now work
   - Check Claude Desktop logs (stderr) for DEBUG messages if issues persist

---

## Known Issues

### v1.1.0
- None currently

### v1.0.0
- ~~`run_performance_report` fails with Pydantic validation error~~ (Fixed in 1.1.0)

---

## Future Enhancements

See [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) for full roadmap.

**High Priority:**
- [ ] Asynchronous report support
- [ ] Custom report templates
- [ ] Comprehensive test suite

**Medium Priority:**
- [ ] Ad set and ad management tools
- [ ] Response caching
- [ ] Webhook support

**Low Priority:**
- [ ] Batch operations
- [ ] Trend analysis
- [ ] Performance optimizations

---

## Links

- [GitHub Repository](https://github.com/yourusername/newsbreak-ads-mcp-server)
- [NewsBreak API Docs](https://business.newsbreak.com/business-api-doc/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Report Issues](https://github.com/yourusername/newsbreak-ads-mcp-server/issues)
