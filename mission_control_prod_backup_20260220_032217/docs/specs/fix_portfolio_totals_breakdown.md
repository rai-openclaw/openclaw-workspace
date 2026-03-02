# Technical Design Spec: Fix Portfolio Holdings Breakdown

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problem Confirmed

**API Returns:**
- Account Total: $1,662,256.29
- Stocks: $901,276.32
- Cash & SGOV: $76,017.68
- ETH: $32,004.00
- Options: -$43,949.50
- **Calculated Total: $965,348.50**
- **Missing: $696,907.79**

**Expected:** Stocks + Cash + ETH + Options should equal Account Total

---

## Investigation Needed

### Possible Causes:
1. Some positions missing from positions list
2. Options calculation incorrect (showing negative value)
3. Cash equivalents under-counted
4. Positions not aggregating correctly

### Data to Check:
- Are all 30 positions accounted for in total_value?
- What's the sum of all position values vs total_value field?
- Are options values calculated correctly?
- Is cash/SGOV being parsed from all accounts?

---

## Files to Examine

| File | Purpose |
|------|---------|
| `server.py` | `api_portfolio()` function - check calculations |
| `portfolio/unified_portfolio_tracker.md` | Source data - verify totals |

---

## Verification Plan

Before fixing, confirm exactly where the discrepancy is:

### Step 1: Compare API data to source file
```python
# Sum all positions from API
positions_value = sum(p['value'] for p in api_data['positions'])
print(f"Sum of position values: ${positions_value}")
print(f"API total_value: ${api_data['total_value']}")
```

### Step 2: Check unified tracker source
Sum the value column in unified tracker and compare to API.

### Step 3: Identify the gap
Determine which category (stocks, cash, options) has the error.

---

## Proposed Fix

**TBD after investigation** - Cannot determine fix until root cause is confirmed.

Possible fixes:
- If positions missing: Fix aggregation logic
- If options wrong: Fix options value calculation
- If cash wrong: Fix cash/SGOV parsing

---

## Awaiting Proceed to Investigate

Will not modify code until exact cause is identified.
