# Technical Design Spec: Fix Per-Account Position Parsing

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problem Confirmed

**Robinhood Parsed Wrong:**
- Header says: $300,124
- Parsed shows: $382,150 (WRONG - $82k over)

**Root Cause:**
Position aggregation mixes per-account shares with total values.

**Example - RKT:**
- Robinhood: 1,400 shares @ $18.68 = **$26,152**
- SEP-IRA: 2,500 shares @ $18.68 = $47,200
- Roth IRA: 800 shares @ $18.68 = $14,944
- **Total: 4,700 shares = $88,296**

**Current (Broken) API:**
```json
{
  "ticker": "RKT",
  "shares": 4700,
  "value": 88296,  // <-- TOTAL VALUE
  "accounts": ["Robinhood: 1400", "SEP-IRA: 2500", "Roth IRA: 800"]
}
```

This shows RKT as $88,296 value but lists Robinhood as having it, causing Robinhood's total to be overstated by $62,144.

---

## Solution

**Fix:** Parse positions per-account first, then aggregate separately.

Each position in account should have its actual per-account value, not total.

---

## Implementation

**File:** `server.py`  
**Function:** `parse_unified_tracker()` - Rewrite position storage  
**Lines:** ~30 lines modified

**Change:** Store per-account positions with per-account values:
```python
# Per-account position (correct)
{
  'ticker': 'RKT',
  'shares': 1400,  # Robinhood's shares
  'value': 26152,   # Robinhood's value (1400 * $18.68)
  'account': 'Robinhood'
}

# SEP-IRA position (correct)
{
  'ticker': 'RKT', 
  'shares': 2500,  # SEP-IRA's shares
  'value': 47200,   # SEP-IRA's value (2500 * $18.68)
  'account': 'SEP-IRA'
}
```

Then aggregate for total portfolio view:
```python
# Aggregated for portfolio totals only
{
  'ticker': 'RKT',
  'shares': 4700,  # Total
  'value': 88296    # Total
}
```

---

## Verification

After fix:
- Robinhood positions sum to $300,124 (matches header)
- SEP-IRA positions sum to $393,728.73 (matches header)
- Each account's parsed total equals its header total
- Aggregated portfolio total = sum of account totals

---

## Affected Files

| File | Changes |
|------|---------|
| `server.py` | Rewrite position parsing to store per-account values |
| `templates/dashboard.html` | Update to handle per-account position display |

**Total:** ~50 lines across 2 files

---

**Awaiting Proceed.**
