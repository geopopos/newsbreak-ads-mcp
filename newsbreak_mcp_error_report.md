# NewsBreak Ads MCP Server - Error Report

## Issue Summary
The `run_performance_report` tool in the NewsBreak Ads MCP server is consistently failing with a Pydantic validation error across all reporting levels (campaign, ad_set, ad).

## Error Details

### Error Message
```
Unexpected error: 1 validation error for ReportResponse
code
  Field required [type=missing, input_value={'timestamp': '2025-10-29...-api/v1/report/runSync'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

### Error Type
Pydantic validation error - missing required field `code` in the API response

### API Endpoint
`/v1/report/runSync` (NewsBreak Business API)

## Reproduction Steps

1. **Working Tools** (for context):
   - `get_ad_accounts` - Successfully retrieved 12 ad accounts
   - `get_campaign_summary` - Successfully retrieved campaign overview
   - `get_campaigns` - Successfully retrieved campaign details

2. **Failing Tool Calls**:

   **Attempt 1: Campaign Level**
   ```json
   {
     "ad_account_id": "1892675572611006465",
     "date_from": "2025-10-22",
     "date_to": "2025-10-29",
     "dimensions": ["date"],
     "metrics": ["impressions", "clicks", "spend", "conversions"],
     "level": "campaign"
   }
   ```
   **Result**: Validation error

   **Attempt 2: Campaign Level (minimal params)**
   ```json
   {
     "ad_account_id": "1892675572611006465",
     "date_from": "2025-10-22",
     "date_to": "2025-10-29",
     "level": "campaign"
   }
   ```
   **Result**: Validation error

   **Attempt 3: Ad Set Level**
   ```json
   {
     "ad_account_id": "1892675572611006465",
     "date_from": "2025-10-22",
     "date_to": "2025-10-29",
     "level": "ad_set"
   }
   ```
   **Result**: Validation error

   **Attempt 4: Ad Level**
   ```json
   {
     "ad_account_id": "1892675572611006465",
     "date_from": "2025-10-22",
     "date_to": "2025-10-29",
     "level": "ad"
   }
   ```
   **Result**: Validation error

## Analysis

### Expected Behavior
The `ReportResponse` Pydantic model expects a response with a `code` field, likely structured something like:
```json
{
  "code": 0,
  "data": { ... },
  "message": "success"
}
```

### Actual Response
The partial response shown in the error indicates the API is returning:
```json
{
  "timestamp": "2025-10-29...",
  "url": ".../v1/report/runSync"
  // Missing 'code' field
}
```

### Root Cause Hypotheses
1. **API Response Format Changed**: NewsBreak may have updated their API response structure
2. **Error Response Format**: The API might be returning an error response in a different format than expected
3. **Empty Data Scenario**: The API might use a different response format when no data is available
4. **API Version Mismatch**: The MCP server might be targeting an outdated API version
5. **Authentication Issue**: The API might be returning an error response due to auth/permissions

## Test Account Details
- **Organization**: Volume Up Agency (ID: 1892675430723272706)
- **Ad Account**: Covenant Roofing - Cocoa (ID: 1892675572611006465)
- **Campaign**: Roof Replacement Financing (ID: 1892677995358437378)
- **Campaign Status**: ACTIVE
- **Date Range Tested**: 2025-10-22 to 2025-10-29

## Debugging Recommendations

1. **Add Response Logging**:
   - Log the full raw API response before Pydantic validation
   - Check what the actual response structure looks like

2. **Check API Documentation**:
   - Verify the current NewsBreak Business API documentation for `/v1/report/runSync`
   - Confirm the expected response format

3. **Update ReportResponse Model**:
   - Make `code` field optional: `code: Optional[int] = None`
   - Or add response format detection to handle different response types

4. **Error Response Handling**:
   - Add specific handling for error responses from the API
   - Check if the API returns different structures for errors vs. success

5. **Add Fallback Logic**:
   - Consider catching validation errors and inspecting the raw response
   - Provide more meaningful error messages to users

6. **Test with Different Parameters**:
   - Try different date ranges (e.g., last 30 days, last month)
   - Test with accounts that definitely have data/spend

## Priority
**HIGH** - This is a core functionality that prevents users from accessing performance metrics, which is a primary use case for the MCP server.

## Environment
- **Date of Issue**: October 29, 2025
- **MCP Server**: newsbreak-ads-mcp-server
- **Tool Name**: `run_performance_report`
- **Related Working Tools**: `get_campaign_summary`, `get_campaigns`, `get_ad_accounts`

## Additional Context
The `get_campaign_summary` tool works successfully and returns a note: "Use run_performance_report for detailed metrics and conversions", indicating that `run_performance_report` is the intended tool for detailed performance data.
