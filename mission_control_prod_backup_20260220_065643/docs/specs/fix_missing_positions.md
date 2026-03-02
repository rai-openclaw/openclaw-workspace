# Technical Design Spec: Fix Missing Positions in API

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problem Statement

**Current Issue:**
API only returning 7 positions, but unified tracker has 30+ unique tickers.

**Expected:** 30+ positions (all unique tickers from all accounts)
**Actual:** 7 positions (only tickers appearing in multiple accounts)

**Example missing tickers:**
- CAKE (Robinhood only)
- LYFT (Robinhood only)  
- NIO (Robinhood only)
- CELH (SEP-IRA only)
- etc.

---

## Root Cause

The `api_portfolio()` function only iterates through `unified_data['overlaps']`, which only includes tickers held in **multiple accounts**. Single-account tickers are not included in the API response.

**Broken logic:**
```python
for ticker, overlap_data in unified_data['overlaps'].items():
    # Only processes tickers in overlaps (multi-account holdings)
```

---

## Solution

**Fix:** Iterate through ALL positions from ALL accounts, not just overlaps.

**New logic:**
```python
# Build complete position list (not just overlaps)
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
        # Aggregate data
        all_positions[ticker]['shares'] += pos['shares']
        all_positions[ticker]['cost_basis'] += pos.get('cost_basis', 0)
        all_positions[ticker]['return'] += pos.get('return', 0)
        all_positions[ticker]['value'] += pos['value']
        all_positions[ticker]['accounts'].append(f"{account_name}: {pos['shares']}")

# Convert to list and calculate return %
positions = []
for ticker, data in all_positions.items():
    data['return_pct'] = (data['return'] / data['cost_basis'] * 100) if data['cost_basis'] > 0 else 0
    positions.append(data)

positions.sort(key=lambda x: x['value'], reverse=True)
```

---

## Affected Files

| File | Path | Changes |
|------|------|---------|
| Server API | `server.py` | Replace overlap-based aggregation with complete position aggregation |

**Estimated Scope:** ~40 lines in 1 file

---

## Step-by-Step Implementation

### Step 1: Fix position aggregation
**File:** `server.py`  
**Lines:** ~40 modified  
**Change:** Replace overlap-only logic with complete position aggregation

### Step 2: Verify position count
**Verification:**
```bash
curl -s http://localhost:8080/api/portfolio | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Positions: {len(d[chr(39)+chr(112)+chr(111)+chr(115)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)])}')
# Should be 30+, not 7
"
```

### Step 3: Verify specific tickers
**Verification:**
- CAKE present
- LYFT present
- NIO present
- All SEP-IRA-only tickers present

### Step 4: Restart and verify dashboard
**Action:** `./mc.sh restart`  
**Verification:** Dashboard shows all positions

### Step 5: Update V1.3 backup
**Action:** Copy fixed server.py to backup

---

## Verification Checklist

- [ ] API returns 30+ positions (not 7)
- [ ] CAKE, LYFT, NIO present in response
- [ ] All SEP-IRA-only tickers present
- [ ] No duplicate tickers
- [ ] Dashboard displays all positions
- [ ] Aggregated values correct

---

**Awaiting Proceed command before implementation.**
