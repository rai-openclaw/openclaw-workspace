# Technical Design Spec: Fix Index Funds Parsing

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Data Inconsistency Confirmed

**The Problem:**
- Dashboard shows Account Total: $1,662,256.29
- Dashboard shows Stocks: $901,276.32
- **Gap: $760,979.97 unaccounted for in breakdown**

**Root Cause:**
Parser reads "Stock Positions" tables but ignores "Index Funds (Collateral)" tables.

---

## Where the Numbers Come From

### Account Total ($1.66M)
Parsed from markdown headers (correct):
- Robinhood: $300,124
- SEP-IRA: $393,728.73
- Schwab CSP: $687,464.15
- Schwab #2: $211,632.15
- Roth IRA: $69,307.26
- **Sum: $1,662,256.29** ✅

### Stocks ($901k) 
Parsed from "Stock Positions" tables only (incomplete):
- Missing Index Funds: ~$658k
- Results in data inconsistency

---

## Missing Data

**Schwab CSP Index Funds (Collateral):**
| Ticker | Value |
|--------|-------|
| VSEQX | $231,573.34 |
| VTCLX | $157,218.75 |
| VTMSX | $269,576.06 |
| **Total Missing** | **$658,368.15** |

---

## Solution

Parse "Index Funds (Collateral)" tables and include in positions.

---

## Implementation

**File:** `server.py`  
**Function:** `parse_unified_tracker()`  
**Lines:** ~15 lines added

Add after parsing Stock Positions:
```python
# Parse Index Funds (Collateral) if present
index_funds = parse_markdown_table(section, 'Index Funds (Collateral)')
for row in index_funds:
    ticker = row.get('Ticker', '')
    if ticker:
        shares = parse_number(row.get('Shares', '0'))
        price = parse_number(row.get('Current Price', '0').replace('$', ''))
        value = parse_number(row.get('Current Value', '0').replace('$', '').replace(',', ''))
        
        account_data['positions'].append({
            'ticker': ticker,
            'company': row.get('Fund Name', ''),
            'shares': shares,
            'price': price,
            'value': value,
            'cost_basis': 0,
            'return': 0
        })
```

---

## Verification

After fix:
- Positions should include VSEQX, VTCLX, VTMSX
- Stocks total should be ~$1.56M (not $901k)
- Breakdown: Stocks ($1.56M) + Cash ($76k) + ETH ($32k) + Options (-$44k) = ~$1.62M
- Close to account total $1.66M (small diff from rounding/cash)

---

**Awaiting Proceed.**
