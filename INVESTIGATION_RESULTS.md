# Investigation Results - MCP Tool vs Direct API Call

## Summary

The `run_performance_report` tool fails when called through Claude/MCP but **works perfectly** when called directly via Python.

## What Works

### ✅ Direct Python Client Call
```python
async with NewsBreakClient() as client:
    response = await client.run_synchronous_report(
        ad_account_id="1892675572611006465",
        date_from="2025-10-22",
        date_to="2025-10-29",
        dimensions=None,
        metrics=None,
        level="campaign",
    )
# Result: SUCCESS - Returns {"code": 0, "data": {"rows": [...]}}
```

### ✅ Direct curl Call
```bash
curl -X POST https://business.newsbreak.com/business-api/v1/reports/getIntegratedReport \
  -H "Content-Type: application/json" \
  -H "Access-Token: YOUR_TOKEN" \
  -d '{
    "name": "report_2025-10-22_2025-10-29",
    "dateRange": "FIXED",
    "startDate": "2025-10-22",
    "endDate": "2025-10-29",
    "dimensions": ["DATE", "CAMPAIGN"],
    "metrics": ["COST", "IMPRESSION", "CLICK", "CTR", "CPC"],
    "filter": "AD_ACCOUNT",
    "filterIds": [1892675572611006465],
    "dataSource": "HOURLY"
  }'
# Result: SUCCESS - Returns {"code":0,"data":{"rows":[],"aggregateData":[]}}
```

## What Fails

### ❌ MCP Tool Call Through Claude
```
run_performance_report(
  ad_account_id: "1892675572611006465",
  date_from: "2025-10-22",
  date_to: "2025-10-29",
  level: "campaign"
)
# Result: FAILURE - "illegal format of name, metrics, dateRange, dimensions"
```

## Testing Performed

1. **Test with January dates** → ✅ Works
2. **Test with October dates** → ✅ Works
3. **Test with level="campaign"** → ✅ Works
4. **Test with level=None** → ✅ Works
5. **Exact same parameters as Claude used** → ✅ Works when called directly

## Conclusion

The issue is **NOT** with:
- ❌ API endpoint URL
- ❌ Request format
- ❌ Date validation
- ❌ Parameter mapping
- ❌ Python client code
- ❌ Dimension/metric enum values

The issue **IS** with:
- ✅ How parameters are passed from Claude → MCP → Server
- ✅ Possible parameter transformation in MCP layer
- ✅ Unknown difference in execution environment

## Next Steps

### 1. Enhanced Debug Logging (DONE)

I've added comprehensive debug logging to `server.py` that will log:
- Exact parameters received by the MCP tool
- Parameter types
- Parameter values with repr() for inspection

### 2. Test Again Through Claude (YOU NEED TO DO THIS)

**IMPORTANT:** You need to restart Claude Desktop to pick up the new debug logging.

**Steps:**
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Run the report command again:
   ```
   Run a performance report for ad account 1892675572611006465
   from October 22 to October 29, 2025
   ```
4. Check the debug logs

### 3. Check Debug Logs

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Look for:**
```
=== MCP TOOL CALLED: run_performance_report ===
DEBUG: Received parameters:
  ad_account_id: '1892675572611006465' (type: str)
  date_from: '2025-10-22' (type: str)
  date_to: '2025-10-29' (type: str)
  dimensions: None (type: NoneType)
  metrics: None (type: NoneType)
  level: 'campaign' (type: str)
================================================

DEBUG: Sending report request:
DEBUG: Request body: {
  "name": "report_2025-10-22_2025-10-29",
  ...
}
```

### 4. Compare Outputs

Compare what the MCP tool receives vs what our direct test sends.

**If they match:** The issue is somewhere between the MCP tool and the API client (unlikely based on our testing)

**If they differ:** We've found the problem - Claude or FastMCP is transforming the parameters

## Hypothesis

Based on testing, I believe one of these is happening:

1. **MCP protocol issue**: FastMCP might be transforming parameters in an unexpected way
2. **Claude parameter passing**: Claude might be passing additional parameters or formatting them differently
3. **Environment difference**: The MCP server runs in a different environment with different settings
4. **Caching issue**: The old buggy code might be cached somewhere

## What We Know For Sure

- The API format is 100% correct (proven by direct Python and curl tests)
- The client code works perfectly (proven by `test_api_directly.py`)
- The server code looks correct (just passes parameters through)
- The error happens somewhere in the MCP communication layer

## Files Updated

| File | Change | Reason |
|------|--------|--------|
| `server.py` | Added debug logging at lines 270-279 | Log exact parameters received by MCP tool |
| `test_api_directly.py` | Updated dates to October 22-29 | Match what Claude used |
| `test_api_directly.py` | Changed level to "campaign" | Match what Claude used |

## Version

**Current version:** 1.1.3 (Enhanced Debugging)
**Date:** 2025-10-29
**Status:** Investigation in progress - waiting for MCP debug logs

---

## Action Required

🚨 **RESTART CLAUDE DESKTOP** and run the report again, then share the debug logs from `~/Library/Logs/Claude/mcp*.log`

The debug output will show us exactly what's different between the MCP call and our direct test.
