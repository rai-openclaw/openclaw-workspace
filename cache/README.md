# Earnings Data Cache System

## How It Works

**1. Morning Fetch (6 AM PT)**
- Fetch all earnings data for the day
- Store in `cache/daily_earnings_YYYY-MM-DD.json`
- Set timestamp of fetch

**2. Report Generation**
- Telegram summary → reads from cache
- Email report → reads from cache  
- Any template fixes → reads from cache (NO new fetches)

**3. Refresh Rules**
Only fetch new data if:
- ✅ New day (date changed)
- ✅ User explicitly requests: "Refresh AAPL data" or "Get real-time data"
- ✅ Market hours changed significantly (price moved >5%)
- ❌ NOT for template/formatting changes

## Cache Structure

```json
{
  "fetchDate": "2026-02-17",
  "fetchTime": "06:00:00 PST",
  "lastUpdated": "2026-02-17T06:00:00-08:00",
  "companies": [
    {
      "ticker": "AAPL",
      "company": "Apple Inc.",
      "price": 185.50,
      "expectedMove": 4.5,
      "expMoveRange": ["177.00", "194.00"],
      "iv": 38,
      "premiumEM": 1.20,
      "premium2xEM": 0.40,
      "financials": {
        "revenue2025": 402000000000,
        "netIncome2025": 105000000000,
        "eps2025": 6.85,
        "debtEquity": 0.15
      },
      "earningsHistory": [...],
      "technicals": {...},
      "grade": "A-",
      "gradeScore": 82
    }
  ]
}
```

## Commands

**Force Refresh:**
- "Refresh all data" → Clear cache, fetch new
- "Update AAPL price" → Refresh just AAPL
- "Get real-time data for F" → Fresh fetch for Ford

**Check Cache Status:**
- "What data do you have cached?" → Show companies + last update time
- "Is AAPL data fresh?" → Show age of data

## Token Savings

**Before (no cache):**
- Generate email report: ~70k tokens (fetch + format)
- Fix template: ~70k tokens (re-fetch + re-format)
- Fix again: ~70k tokens
- **Total: ~210k tokens for 3 iterations**

**After (with cache):**
- Morning fetch: ~40k tokens (fetch once)
- Generate email: ~5k tokens (format only)
- Fix template: ~5k tokens (format only)
- Fix again: ~5k tokens
- **Total: ~55k tokens (74% savings)**
