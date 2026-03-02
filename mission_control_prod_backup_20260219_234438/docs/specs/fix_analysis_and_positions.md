# Technical Design Spec: Fix Analysis Archive + Missing Positions

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Issue 1: Stock Analysis Archive Click Shows No Data

### Problem
Clicking analysis cards shows empty/missing data. Dashboard expects `analysis.full_text` but API only returns `summary`.

### Root Cause
`api_analysis_archive()` returns:
```json
{
  "ticker": "RKT",
  "summary": "Analysis available",  // Only summary
  // Missing "full_text" field
}
```

Dashboard looks for:
```javascript
let content = analysis.full_text;  // undefined!
```

### Solution
Add `full_text` field to API response with complete analysis content from `portfolio_tracker.md`.

---

## Issue 2: Missing Positions in API (Only 7 instead of 30+)

### Problem
API only returns 7 positions (tickers in multiple accounts). Missing 25+ single-account tickers (CAKE, LYFT, NIO, CELH, etc.).

### Root Cause
`api_portfolio()` only iterates through `unified_data['overlaps']` (multi-account tickers).

### Solution
Iterate through ALL positions from ALL accounts, aggregate by ticker (no duplicates).

---

## Affected Files

| File | Path | Changes |
|------|------|---------|
| Server API | `server.py` | Fix analysis archive (add full_text) + Fix position aggregation (all tickers) |
| Dashboard | `templates/dashboard.html` | (May need update for analysis display) |

**Estimated Scope:** ~60 lines across 2 files

---

## Implementation Details

### Fix 1: Analysis Archive API

**Current:**
```python
analyses.append({
    'ticker': ticker,
    'company': row.get('Company', ''),
    'grade': 'B+',
    'date': date,
    'summary': summary[:200]  # Truncated
})
```

**Fixed:**
```python
# Extract FULL section content for full_text
full_text = '\n'.join(lines[1:])  # All content after header

analyses.append({
    'ticker': ticker,
    'company': row.get('Company', ''),
    'grade': 'B+',
    'date': date,
    'summary': summary[:200],
    'full_text': full_text  # ADD THIS
})
```

### Fix 2: Position Aggregation

**Current:**
```python
for ticker, overlap_data in unified_data['overlaps'].items():
    # Only multi-account tickers
```

**Fixed:**
```python
# Aggregate ALL positions (single + multi account)
all_positions = {}

for account_name, account_data in unified_data['accounts'].items():
    for pos in account_data['positions']:
        ticker = pos['ticker']
        if ticker not in all_positions:
            all_positions[ticker] = {
                'ticker': ticker,
                'company': pos['company'],
                'shares': 0,
                'cost_basis': 0,
                'return': 0,
                'value': 0,
                'price': pos['price'],
                'accounts': []
            }
        # Aggregate
        all_positions[ticker]['shares'] += pos['shares']
        all_positions[ticker]['cost_basis'] += pos.get('cost_basis', 0)
        all_positions[ticker]['return'] += pos.get('return', 0)
        all_positions[ticker]['value'] += pos['value']
        all_positions[ticker]['accounts'].append(f"{account_name}: {pos['shares']}")

# Calculate return %
positions = []
for ticker, data in all_positions.items():
    data['return_pct'] = (data['return'] / data['cost_basis'] * 100) if data['cost_basis'] > 0 else 0
    positions.append(data)

positions.sort(key=lambda x: x['value'], reverse=True)
```

---

## Step-by-Step Implementation

### Step 1: Fix analysis archive API
**File:** `server.py`  
**Lines:** ~10 modified  
**Add:** `full_text` field to analysis response

### Step 2: Fix position aggregation
**File:** `server.py`  
**Lines:** ~40 modified  
**Replace:** Overlap-only logic with complete position aggregation

### Step 3: Test analysis archive
**Verification:**
```bash
curl -s http://localhost:8080/api/analysis-archive | python3 -c "
import json,sys
d=json.load(sys.stdin)
a = d[0]
print(f'Ticker: {a[chr(39)+chr(116)+chr(105)+chr(99)+chr(107)+chr(101)+chr(114)]}')
print(f'Has full_text: {chr(39)+chr(102)+chr(117)+chr(108)+chr(108)+chr(95)+chr(116)+chr(101)+chr(120)+chr(116) in a}')
print(f'Full text length: {len(a.get(chr(39)+chr(102)+chr(117)+chr(108)+chr(108)+chr(95)+chr(116)+chr(101)+chr(120)+chr(116), chr(34)+chr(34)))}')
"
```

### Step 4: Test position count
**Verification:**
```bash
curl -s http://localhost:8080/api/portfolio | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Positions: {len(d[chr(39)+chr(112)+chr(111)+chr(115)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)])}')  # Should be 30+
tickers = [p[chr(39)+chr(116)+chr(105)+chr(99)+chr(107)+chr(101)+chr(114)] for p in d[chr(39)+chr(112)+chr(111)+chr(115)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]]
print(f'CAKE present: {chr(34)+chr(67)+chr(65)+chr(75)+chr(69) in tickers}')
print(f'LYFT present: {chr(34)+chr(76)+chr(89)+chr(70)+chr(84) in tickers}')
"
```

### Step 5: Restart and full verification
**Action:** `./mc.sh restart`  
**Verify:**
- Analysis cards show full content when clicked
- Portfolio shows 30+ positions
- No duplicate tickers
- All returns calculate correctly

### Step 6: Update V1.3 backup
**Action:** Copy fixed files to backup

---

## Verification Checklist

### Analysis Archive
- [ ] API returns `full_text` field
- [ ] Clicking analysis card shows full content
- [ ] RKT analysis displays properly
- [ ] LDI analysis displays properly

### Positions
- [ ] API returns 30+ positions (not 7)
- [ ] CAKE, LYFT, NIO present in response
- [ ] No duplicate tickers
- [ ] Aggregated values correct (shares, cost basis, returns)
- [ ] RKT shows 4,700 total shares

### Dashboard
- [ ] All positions display in holdings
- [ ] Analysis archive clickable
- [ ] Options table shows cost basis

---

## Rollback Strategy

If fixes fail:
1. Restore server.py from backup
2. Restart server
3. Verify issues return (confirming rollback)

---

**Awaiting Proceed command before implementing BOTH fixes.**
