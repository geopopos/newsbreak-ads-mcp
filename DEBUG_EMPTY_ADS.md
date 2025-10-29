# Debugging Empty Ads Response

## Problem

The `get_ads()` tool returns empty rows even though pagination shows 113 total ads exist:

```json
{
  "ads": {
    "rows": [],
    "pagination": {
      "total": 113
    }
  }
}
```

## Possible Causes

1. **API returns data in unexpected format** - Field names or structure different than documented
2. **Pydantic validation failing silently** - Model can't parse the data and returns empty objects
3. **Data serialization bug** - MCP tool not properly converting model objects to JSON
4. **Permissions issue** - API returns count but not actual data due to access restrictions

## Debug Logging Added

I've added comprehensive debug logging at two layers:

### Layer 1: API Client (`client.py` line 465-477)
Logs the raw API response:
- Response code
- Whether data field exists
- Data structure keys
- Total count from API
- Actual rows count
- Sample of first row (raw JSON)

### Layer 2: MCP Tool (`server.py` line 465-481)
Logs the parsed Pydantic models:
- Response code after parsing
- Whether data object exists
- Rows count after Pydantic validation
- Pagination info
- First ad basic fields (id, name)
- Whether creative object exists

## How to Debug

### Step 1: Restart Claude Desktop

**IMPORTANT:** You must restart Claude Desktop to pick up the debug logging.

```bash
# Quit Claude Desktop completely
# Then reopen it
```

### Step 2: Run get_ads Again

In Claude, run:
```
Get ads for ad account 1892675572611006465
```

### Step 3: Check Debug Logs

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Step 4: Analyze the Output

Look for these debug sections:

#### At API Client Layer:
```
=== DEBUG: get_ads API Response ===
DEBUG: Response code: 0
DEBUG: Has data field: True
DEBUG: Data keys: ['rows', 'pageNo', 'pageSize', 'total', 'hasNext']
DEBUG: Total ads: 113
DEBUG: Rows count: 50  <-- SHOULD MATCH TOTAL OR PAGE SIZE
DEBUG: First row sample: {
  "id": "...",
  "name": "...",
  "creative": {...}
}
===================================
```

**Key Question:** Does "Rows count" show 50 (or page_size), or does it show 0?

#### At MCP Tool Layer:
```
=== DEBUG: get_ads MCP Tool ===
DEBUG: Response code: 0
DEBUG: Has data: True
DEBUG: Data rows count: 50  <-- SHOULD MATCH API LAYER
DEBUG: Data total: 113
DEBUG: First ad id: 123456789
DEBUG: First ad name: My Ad
DEBUG: First ad has creative: True
===============================
```

**Key Question:** Does "Data rows count" match the count from the API layer?

## Diagnostic Scenarios

### Scenario 1: API Returns 0 Rows

```
DEBUG: Rows count: 0  <-- At API layer
```

**Diagnosis:** API is not returning data despite total=113

**Possible Causes:**
- Permissions issue - can see count but not content
- API bug or rate limiting
- Account-level restriction

**Next Step:** Try with a different page number or smaller page size

### Scenario 2: API Returns Rows, MCP Tool Shows 0

```
DEBUG: Rows count: 50  <-- At API layer (has data)
DEBUG: Data rows count: 0  <-- At MCP layer (lost data)
```

**Diagnosis:** Pydantic validation is failing to parse the rows

**Possible Causes:**
- API response structure doesn't match our models
- Required fields are missing in API response
- Field type mismatches (e.g., expecting string, got int)

**Next Step:** Check the "First row sample" JSON to see actual structure

### Scenario 3: MCP Tool Has Rows, Output Shows Empty

```
DEBUG: Data rows count: 50  <-- Has data in MCP tool
...but final JSON shows empty rows[]
```

**Diagnosis:** Serialization bug in the formatting loop

**Possible Causes:**
- Bug in the `for ad in response.data.rows` loop
- Exception during serialization not being caught
- Field access causing AttributeError

**Next Step:** Look for any error messages after the debug output

### Scenario 4: All Counts Match But Content Is Null

```
DEBUG: Rows count: 50
DEBUG: First ad id: 123456789
DEBUG: First ad name: My Ad
DEBUG: First ad has creative: False  <-- No creative data
```

**Diagnosis:** Ads exist but creative content is missing/null

**Possible Causes:**
- Ads don't have creative assets attached yet
- Different creative structure than expected
- Creative data requires additional API call

**Next Step:** This might be expected - check if first row sample shows creative field

## Common Issues & Solutions

### Issue: "Field required" ValidationError

If you see:
```
ValidationError: 1 validation error for Ad
fieldName
  Field required
```

**Solution:** The API response is missing a required field. We need to make that field optional in the model.

### Issue: "Input should be..." ValidationError

If you see:
```
ValidationError: Input should be 'str' [type=string_type, input_value=123, input_type=int]
```

**Solution:** The API returns a different type than our model expects. We need to adjust the field type.

### Issue: Empty creative.content

If creative exists but content is None:

**Solution:** Creative might be in draft state or pending approval. This could be normal.

## What to Share

After running the test, please share:

1. **The complete DEBUG output** from both layers
2. **The final JSON response** that shows empty rows
3. **Any error messages** you see in the logs

This will tell us exactly where the data is being lost.

## Temporary Workaround

While debugging, you can try:

1. **Smaller page size:**
   ```
   Get ads for account 1892675572611006465 with page size 5
   ```

2. **Filter by status:**
   ```
   Get ACTIVE ads for account 1892675572611006465
   ```

3. **Different page:**
   ```
   Get ads for account 1892675572611006465 page 2
   ```

This might help narrow down if it's a specific ad causing issues.

---

**Status:** 🔍 Awaiting debug logs
**Next Action:** Restart Claude Desktop and share debug output
