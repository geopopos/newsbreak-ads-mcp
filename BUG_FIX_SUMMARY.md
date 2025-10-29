# Bug Fix Summary - run_performance_report Validation Error

## What Was Fixed

The `run_performance_report` tool was consistently failing with a Pydantic validation error. This has been fixed in version 1.1.0.

## The Problem

### Error Message
```
Unexpected error: 1 validation error for ReportResponse
code
  Field required [type=missing, input_value={'timestamp': '2025-10-29...-api/v1/report/runSync'}, input_type=dict]
```

### Root Cause
The NewsBreak API returns **two different response formats**:

**Successful Response:**
```json
{
  "code": 0,
  "data": {
    "rows": [...]
  }
}
```

**Error Response:**
```json
{
  "timestamp": "2025-10-29T...",
  "url": "/v1/report/runSync",
  "message": "Error message here"
}
```

Our code was expecting the `code` field to **always** be present, but error responses don't include it, causing validation failures.

## The Solution

### Changes Made

#### 1. Updated `models.py` - Made `code` field optional
```python
# Before
class BaseResponse(BaseModel):
    code: int = Field(description="Status code, 0 for success")
    errMsg: Optional[str] = Field(None, description="Error message")

# After
class BaseResponse(BaseModel):
    code: Optional[int] = Field(None, description="Status code")
    errMsg: Optional[str] = Field(None, description="Error message")
    message: Optional[str] = Field(None, description="Alternative error field")
    error: Optional[str] = Field(None, description="Another error field")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    url: Optional[str] = Field(None, description="Request URL")
```

#### 2. Enhanced `client.py` - Better error detection
- Check HTTP status codes first (4xx/5xx = error)
- Detect error responses with `timestamp` + `url` fields
- Handle responses with or without `code` field
- Added debug logging for troubleshooting

#### 3. Added debug logging
- Logs raw API responses to stderr when validation fails
- Helps diagnose future issues quickly

## How to Update

### If You Cloned the Repo

```bash
cd newsbreak-ads-mcp-server
git pull
# No need to reinstall dependencies - models and client only changed
```

### If You're Using Claude Desktop

1. **No changes needed** - just restart Claude Desktop to pick up the new code
2. The server will automatically use the updated files

### If You Copied the Files

Replace these files with the new versions:
- `client.py`
- `models.py`

## How to Test

### 1. Update your local copy
```bash
git pull
```

### 2. Restart Claude Desktop
Quit and reopen Claude Desktop

### 3. Try run_performance_report again

Ask Claude:
```
Run a performance report for ad account 1892675572611006465
from October 22 to October 29, 2025
```

### 4. What to Expect

**If the API has data:**
- You'll get a report with impressions, clicks, spend, etc.

**If the API returns an error:**
- You'll get a clear error message explaining what went wrong
- Check Claude Desktop logs (stderr) for DEBUG output with full API response

**What changed:**
- ❌ Before: "Validation error: code field required" (cryptic)
- ✅ After: Clear error message from the API

## Debugging

If you still encounter issues:

### 1. Check Claude Desktop Logs

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Look for:**
```
DEBUG: Raw API response for /report/runSync:
DEBUG: { ... full response ... }
DEBUG: Validation error: ...
```

### 2. Test with curl

You can test the API directly to see what it returns:

```bash
curl -X POST https://business.newsbreak.com/business-api/v1/report/runSync \
  -H "Content-Type: application/json" \
  -H "Access-Token: YOUR_TOKEN" \
  -d '{
    "adAccountId": "1892675572611006465",
    "dateFrom": "2025-10-22",
    "dateTo": "2025-10-29",
    "level": "campaign"
  }'
```

### 3. Common Issues & Solutions

**Issue: "API returned error response"**
- This means the API is rejecting your request
- Check the error message for details
- Common causes:
  - Invalid date range
  - Account has no data for that period
  - Permissions issue
  - API endpoint or parameters changed

**Issue: "Failed to parse report response"**
- The API returned an unexpected format
- Check DEBUG logs for the raw response
- Share the logs in a bug report

**Issue: Still getting validation errors**
- Make sure you pulled the latest code
- Check that `models.py` has `code: Optional[int]`
- Restart Claude Desktop

## What Changed (Technical Details)

### Error Detection Flow (New)

```
1. Make API request
2. Check HTTP status code
   ├─ 4xx/5xx → Parse error response
   └─ 2xx → Continue
3. Parse JSON response
4. Check response format
   ├─ Has 'code' field?
   │  ├─ code == 0 → Success
   │  └─ code != 0 → Error from API
   ├─ Has 'timestamp' + 'url' (no 'code')?
   │  └─ Error response format → Convert to error
   └─ Other format → Return as-is
5. Validate with Pydantic
   ├─ Success → Return data
   └─ Fail → Log raw response, raise error
```

### Files Changed

| File | Changes | Lines |
|------|---------|-------|
| `client.py` | Enhanced error handling | +45 |
| `models.py` | Optional `code` field | +5 |
| `CHANGELOG.md` | Version history | +304 (new) |

### Backward Compatibility

✅ **Fully backward compatible**
- Existing code continues to work
- New error handling is additive
- No breaking changes to API calls

## Testing Checklist

Use this checklist to verify the fix:

- [ ] Pulled latest code (`git pull`)
- [ ] Restarted Claude Desktop
- [ ] Tested `run_performance_report` with valid date range
- [ ] Tested with different reporting levels (campaign, ad_set, ad)
- [ ] Checked Claude Desktop logs for DEBUG output
- [ ] Verified error messages are clear and helpful
- [ ] No more "code field required" validation errors

## Still Having Issues?

### 1. Check Your Setup
```bash
# Verify you have the latest code
cd newsbreak-ads-mcp-server
git log --oneline -1
# Should show: "Fix critical bug: run_performance_report..."

# Check the model
grep -A 3 "class BaseResponse" models.py
# Should show: code: Optional[int]
```

### 2. Enable Debug Mode

The debug logging is always enabled now. Just check stderr:

**macOS Claude Desktop logs:**
```bash
tail -f ~/Library/Logs/Claude/mcp-server-newsbreak-ads.log
```

### 3. Report the Issue

If it's still not working, create an issue with:

1. **Command you ran** (what you asked Claude)
2. **Full error message**
3. **DEBUG logs** from stderr (if available)
4. **curl test results** (if you tried direct API call)
5. **Git commit hash** (`git log --oneline -1`)

## Summary

| Before | After |
|--------|-------|
| ❌ Validation error on all report calls | ✅ Clear error messages from API |
| ❌ No visibility into API response | ✅ DEBUG logs show full response |
| ❌ Required 'code' field | ✅ Optional 'code' field |
| ❌ Single error format expected | ✅ Multiple error formats handled |

**Status:** 🟢 **FIXED** in version 1.1.0

---

**Version:** 1.1.0
**Date:** 2025-10-29
**Commit:** 7acd545
**Fixed By:** Claude Code
