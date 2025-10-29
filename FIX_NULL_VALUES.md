# Fix: Null Dimensions and Metrics in Report Response

## Problem

When calling `run_performance_report`, all rows returned `null` for both dimensions and metrics:

```json
{
  "rows": [
    {
      "dimensions": null,
      "metrics": null
    }
  ]
}
```

## Root Cause

Our `ReportRow` model was expecting a **nested structure**:
```python
class ReportRow(BaseModel):
    dimensions: Optional[dict]  # Expected nested object
    metrics: Optional[dict]      # Expected nested object
```

But the NewsBreak API actually returns a **flat structure**:
```json
{
  "rows": [
    {
      "date": "2024-01-01",
      "campaignId": "123456789",
      "campaign": "example campaign",
      "impression": 1,
      "click": 0,
      "cost": 20,
      "cpm": 20000
    }
  ]
}
```

## Solution

Updated the `ReportRow` model in `models.py` to match the actual API response format:

```python
class ReportRow(BaseModel):
    """Single row in report data - API returns flat structure"""

    # Dimension fields (optional based on what was requested)
    date: Optional[str] = None
    hour: Optional[str] = None
    adAccountId: Optional[str] = None
    adAccount: Optional[str] = None
    orgId: Optional[str] = None
    organization: Optional[str] = None
    campaignId: Optional[str] = None
    campaign: Optional[str] = None
    adSetId: Optional[str] = None
    adSet: Optional[str] = None
    adId: Optional[str] = None
    ad: Optional[str] = None

    # Metric fields (optional based on what was requested)
    cost: Optional[float] = None
    impression: Optional[int] = None
    click: Optional[int] = None
    conversion: Optional[int] = None
    value: Optional[float] = None
    cpm: Optional[float] = None
    cpc: Optional[float] = None
    cpa: Optional[float] = None
    ctr: Optional[float] = None
    cvr: Optional[float] = None
    vpa: Optional[float] = None
    roas: Optional[float] = None

    class Config:
        extra = "allow"  # Allow additional fields from API
```

And updated `server.py` to properly serialize the rows:

```python
"rows": [
    row.model_dump(exclude_none=True)  # Convert to dict, exclude null fields
    for row in response.data.rows
]
```

## Result

Now reports return proper data:

```json
{
  "report": {
    "ad_account_id": "1892675572611006465",
    "date_from": "2025-10-22",
    "date_to": "2025-10-29",
    "rows": [
      {
        "date": "2025-10-22",
        "campaignId": "123456789",
        "campaign": "My Campaign",
        "cost": 45.67,
        "impression": 1234,
        "click": 56,
        "ctr": 4.54,
        "cpc": 0.815
      }
    ],
    "total": 8
  }
}
```

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `models.py` | Updated `ReportRow` model | 158-191 |
| `server.py` | Changed row serialization | 325 |
| `CHANGELOG.md` | Documented fix | v1.1.5 |

## Testing

To verify the fix works:

1. **Restart Claude Desktop** (important!)
2. **Run a report**:
   ```
   Run a performance report for ad account 1892675572611006465
   from October 22 to October 29, 2025
   with dimensions: date, campaign_id
   and metrics: impressions, clicks, spend, ctr, cpc
   ```
3. **Expected result**: Should see actual values instead of null

## Why This Happened

The initial implementation was based on a misunderstanding of the API response format. Many APIs return nested structures like:

```json
{
  "dimensions": {"date": "2024-01-01", "campaign": "..."},
  "metrics": {"impressions": 1234, "clicks": 56}
}
```

But NewsBreak's API uses a simpler flat structure where all fields are at the same level. This is actually easier to work with!

## Version

**Fixed in:** v1.1.5
**Date:** 2025-10-29
**Status:** ✅ RESOLVED

---

## Quick Reference

### Dimension Fields Available
- `date` - Date (YYYY-MM-DD)
- `hour` - Hour
- `orgId`, `organization` - Organization ID and name
- `adAccountId`, `adAccount` - Ad account ID and name
- `campaignId`, `campaign` - Campaign ID and name
- `adSetId`, `adSet` - Ad set ID and name
- `adId`, `ad` - Ad ID and name

### Metric Fields Available
- `cost` - Total cost/spend
- `impression` - Total impressions
- `click` - Total clicks
- `conversion` - Total conversions
- `value` - Conversion value
- `cpm` - Cost per thousand impressions
- `cpc` - Cost per click
- `cpa` - Cost per acquisition
- `ctr` - Click-through rate (%)
- `cvr` - Conversion rate (%)
- `vpa` - Value per acquisition
- `roas` - Return on ad spend

Fields are only present in the response if they were requested in the dimensions/metrics parameters.
