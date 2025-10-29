# Debugging NewsBreak Performance Reports

## Current Status

The `run_performance_report` tool has been updated with enhanced debug logging to help diagnose the "illegal format" errors you're experiencing.

## What Was Added

### 1. Enhanced Debug Logging

The server now logs the EXACT request being sent to the API, including:
- Full request body in JSON format
- Original parameters (what you passed in)
- Mapped parameters (what gets sent to API)
- All dimensions and metrics after conversion

### 2. Extended Dimension Mappings

Added support for common aliases:
```python
"campaign_id" → "CAMPAIGN"
"ad_set_id" → "AD_SET"
"ad_id" → "AD"
"ad_account_id" → "AD_ACCOUNT"
"organization" → "ORG"
```

## How to Debug

### Step 1: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
# Then reopen it
```

### Step 2: Try Your Report Again

In Claude, run:
```
Run a performance report for ad account 1892675572611006465
from January 20 to January 26, 2025
```

### Step 3: Check the Debug Logs

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Look for:**
```
DEBUG: Sending report request:
DEBUG: Request body: {
  "name": "MCP_Report_...",
  "timezone": "America/Los_Angeles",
  "dateRange": "FIXED",
  "startDate": "2025-01-20",
  "endDate": "2025-01-26",
  ...
}
DEBUG: Original params - date_from: 2025-01-20, date_to: 2025-01-26
DEBUG: Original dimensions: ['date', 'campaign_id'], metrics: ['impressions', 'clicks']
DEBUG: Mapped dimensions: ['DATE', 'CAMPAIGN'], metrics: ['IMPRESSION', 'CLICK']
```

### Step 4: Analyze the Debug Output

Check these things in the debug log:

#### ✅ Correct Date Format
```json
"startDate": "2025-01-20",  // Should be YYYY-MM-DD
"endDate": "2025-01-26"
```

#### ✅ Correct Dimension Format
```json
"dimensions": ["DATE", "CAMPAIGN"]  // Should be UPPERCASE
```

#### ✅ Correct Metrics Format
```json
"metrics": ["IMPRESSION", "CLICK", "COST"]  // Should be UPPERCASE
```

#### ✅ Correct Filter Format
```json
"filter": "AD_ACCOUNT",
"filterIds": [1892675572611006465]  // Should be integer, not string
```

## Common Issues & Solutions

### Issue 1: Date Format Error

**Symptom:** `illegal format of dateRange`

**Possible Causes:**
- Date not in YYYY-MM-DD format
- Date values are invalid
- startDate is after endDate

**Solution:**
Check debug log for:
```
DEBUG: Original params - date_from: 2025-01-20, date_to: 2025-01-26
```

Make sure:
- Format is exactly `YYYY-MM-DD`
- Dates are valid (not future dates if API doesn't allow)
- Start date is before end date

### Issue 2: Dimension Format Error

**Symptom:** `illegal format of dimensions`

**Possible Causes:**
- Dimension value not in allowed list
- Not uppercase
- Typo in dimension name

**Valid Dimensions:**
```
DATE, HOUR, ORG, AD_ACCOUNT, CAMPAIGN, AD_SET, AD
```

**Solution:**
Check debug log for:
```
DEBUG: Mapped dimensions: ['DATE', 'CAMPAIGN']
```

Make sure all values are in the valid list above.

### Issue 3: Metrics Format Error

**Symptom:** `illegal format of metrics`

**Possible Causes:**
- Metric value not in allowed list
- Not uppercase
- Typo in metric name

**Valid Metrics:**
```
COST, IMPRESSION, CLICK, CONVERSION, VALUE, COUNT,
CPM, CPC, CPA, CTR, CVR, VPA,
COMPLETE_PAYMENT_ROAS, SALE_ROAS, APP_PURCHASE_ROAS
```

**Solution:**
Check debug log for:
```
DEBUG: Mapped metrics: ['IMPRESSION', 'CLICK', 'COST']
```

Make sure all values are in the valid list above.

### Issue 4: Name Format Error

**Symptom:** `illegal format of name`

**Possible Causes:**
- Name contains special characters
- Name is too long
- Name format not accepted

**Current Format:**
```
MCP_Report_{ad_account_id}_{date_from}_{date_to}
```

**Example:**
```
MCP_Report_1892675572611006465_2025-01-20_2025-01-26
```

**Possible Solution:**
Try a simpler name format. Let me know if this is the issue from the debug logs.

## Testing Workflow

### Test 1: Minimal Parameters

Try with just the required parameters:
```
Run a performance report for ad account 1892675572611006465
from January 20 to January 26, 2025
```

This uses defaults:
- dimensions: `["DATE", "CAMPAIGN"]`
- metrics: `["COST", "IMPRESSION", "CLICK", "CTR", "CPC"]`

### Test 2: Custom Dimensions

Try specifying dimensions:
```
Run a performance report for ad account 1892675572611006465
from January 20 to January 26
with dimensions: date, campaign
```

### Test 3: Custom Metrics

Try specifying metrics:
```
Run a performance report for ad account 1892675572611006465
from January 20 to January 26
with metrics: impressions, clicks, spend
```

## Share Debug Output

After running the tests above, please share:

1. **The exact command** you used in Claude
2. **The error message** you received
3. **The DEBUG output** from the logs showing:
   - The request body being sent
   - The mapped dimensions/metrics
   - Any error response from the API

This will help me identify exactly what the API doesn't like about the request format.

## Current Request Format

Based on the official documentation, we're sending:

```json
{
  "name": "MCP_Report_1892675572611006465_2025-01-20_2025-01-26",
  "timezone": "America/Los_Angeles",
  "dateRange": "FIXED",
  "startDate": "2025-01-20",
  "endDate": "2025-01-26",
  "dimensions": ["DATE", "CAMPAIGN"],
  "metrics": ["COST", "IMPRESSION", "CLICK", "CTR", "CPC"],
  "filter": "AD_ACCOUNT",
  "filterIds": [1892675572611006465],
  "dataSource": "HOURLY"
}
```

This matches the official API documentation format. If it's still failing, the debug logs will show us what might be different or wrong.

## Next Steps

1. **Restart Claude Desktop** (important!)
2. **Try the report again**
3. **Check the debug logs** at `~/Library/Logs/Claude/mcp*.log`
4. **Share the DEBUG output** with me

The debug output will tell us EXACTLY what's being sent and help identify the issue.

## Alternative: Test with curl

If you want to test the API directly:

```bash
curl -X POST https://business.newsbreak.com/business-api/v1/reports/getIntegratedReport \
  -H "Content-Type: application/json" \
  -H "Access-Token: YOUR_TOKEN" \
  -d '{
    "name": "test_report",
    "timezone": "America/Los_Angeles",
    "dateRange": "FIXED",
    "startDate": "2025-01-20",
    "endDate": "2025-01-26",
    "dimensions": ["DATE", "CAMPAIGN"],
    "metrics": ["COST", "IMPRESSION", "CLICK"],
    "filter": "AD_ACCOUNT",
    "filterIds": [1892675572611006465],
    "dataSource": "HOURLY"
  }'
```

This will show you the raw API response and help determine if it's an API issue or a client issue.

---

**Version:** 1.1.3 (Debug Enhanced)
**Status:** Ready for debugging
**Action Required:** Restart Claude Desktop and check logs
