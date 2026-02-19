# Single Source Protocol — Earnings Whispers

## Decision
Use **Earnings Whispers** (earningswhispers.com) as the single source of truth for earnings dates and times.

## Rationale
- Every data source has errors (Finnhub, TipRanks, Benzinga, company IR)
- Cross-referencing is slow and still yields conflicts
- Better to be consistently wrong together than randomly wrong separately
- Earnings Whispers has been reliable in user's experience

## Protocol

### Primary Source
**Website:** https://earningswhispers.com
**Alternative:** https://unusualwhales.com (same data, different UI)

### API/Scraping
Since Earnings Whispers doesn't have a public API:
1. Use web search to query: "[TICKER] earnings date earnings whispers"
2. Extract date and time from search results
3. Mark source: "Per Earnings Whispers"

### Bob's Updated Instructions

```
RESEARCH TASK — SINGLE SOURCE RULE

1. Use ONLY Earnings Whispers for earnings dates/times
2. Query format: "[TICKER] earnings earningswhispers"
3. Extract: Date + Time (BMO/AMC/TBA)
4. Note in report: "Per Earnings Whispers"
5. If date unclear, mark: "TBA — verify manually"

NEVER cross-reference with:
- Finnhub
- TipRanks
- Company IR pages
- Yahoo Finance

If Earnings Whispers is wrong, we're wrong together.
```

### Date Verification

Still use Python for date math:
```python
from datetime import datetime, timedelta

# Calculate from today
today = datetime.now()
target_date = today + timedelta(days=X)
```

But get the earnings DATE from Earnings Whispers only.

### Report Format

```markdown
## Wednesday Feb 19 Earnings

**Source:** Earnings Whispers

| Ticker | Time | Market Cap | Notes |
|--------|------|------------|-------|
| CVNA | AMC | $X.XB | Per EW |
| DASH | AMC | $X.XB | Per EW |
| LMND | BMO | $X.XB | Per EW |
| W | BMO | $X.XB | Per EW |

**Actionable Today (Trade Wed before 4 PM):**
- CVNA, DASH (Wed AMC)
- LMND, W (Thu BMO)

**Actionable Tomorrow:**
- [None or list]
```

### When Data is Missing

If Earnings Whispers doesn't have a date:
1. Mark as "Date TBA — not on EW"
2. Don't research further
3. Skip for that week

### Accepting Errors

If Earnings Whispers has wrong date:
- We both miss it together
- Log in optimization journal
- Note: "EW had wrong date for [TICKER]"
- Don't switch sources

## Consistency Over Accuracy

Better to miss the same stocks consistently than to have random errors from mixing sources.

---

**Effective:** Immediately  
**Source:** earningswhispers.com  
**Backup:** unusualwhales.com  
**Cross-referencing:** DISABLED
