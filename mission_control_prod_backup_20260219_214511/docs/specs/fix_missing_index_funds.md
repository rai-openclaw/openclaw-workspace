# Technical Design Spec: Fix Missing Index Funds in Portfolio

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problem Confirmed

**API Returns:**
- Account Total: $1,662,256.29
- Stocks: $901,276.32
- **Missing: ~$658,000 from Index Funds**

**Schwab CSP Specific:**
- Account Value: $687,464.15
- Parsed Positions: $56,236 (ELF + TTD only)
- **Missing: $631,228.15**

---

## Root Cause Confirmed

Parser only reads "Stock Positions" tables, ignores "Index Funds (Collateral)" tables.

**Source Data (in unified_portfolio_tracker.md):**
```markdown
### Index Funds (Collateral)
| Ticker | Fund Name | Shares | Current Price | Current Value |
|--------|-----------|--------|---------------|---------------|
| VSEQX | Vanguard Extended Market | 5,860.559 | $39.46 | $231,573.34 |
| VTCLX | Vanguard Tax-Managed Capital | 446.53 | $352.09 | $157,218.75 |
| VTMSX | Vanguard Tax-Managed Small Cap | 2,514.233 | $107.22 | $269,576.06 |
```

**Total Missing from Index Funds: $658,368.15**

---

## Solution

Modify `parse_unified_tracker()` to also parse "Index Funds (Collateral)" tables and add them to positions.

---

## Implementation

**File:** `server.py`  
**Function:** `parse_unified_tracker()`  
**Lines:** ~10 lines added  

**Changes:**
1. After parsing "Stock Positions" table, also parse "Index Funds (Collateral)" table
2. Add index funds to the same positions list with proper account attribution
3. Include them in aggregations and totals

**Code Addition:**
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
            'cost_basis': 0,  # Not tracked for index funds
            'return': 0
        })
```

---

## Verification

### Step 1: Apply fix to server.py

### Step 2: Restart server
```bash
./mc.sh restart
```

### Step 3: Verify API includes index funds
```bash
curl -s http://localhost:8080/api/portfolio | python3 -c "
import json,sys
d=json.load(sys.stdin)
positions = d.get('positions', [])
tickers = [p['ticker'] for p in positions]
print(f'VSEQX present: {chr(34)+chr(86)+chr(83)+chr(69)+chr(81)+chr(88) in tickers}')
print(f'VTCLX present: {chr(34)+chr(86)+chr(84)+chr(67)+chr(76)+chr(88) in tickers}')
print(f'VTMSX present: {chr(34)+chr(86)+chr(84)+chr(77)+chr(83)+chr(88) in tickers}')
print(f'Total positions: {len(positions)}')
"
```

### Step 4: Verify totals add up
Schwab CSP positions should now be ~$687k (stocks + index funds + options)

### Step 5: Update V1.3 backup

---

## Affected Files

| File | Changes |
|------|---------|
| `server.py` | Add Index Funds parsing in `parse_unified_tracker()` |

---

**Awaiting Proceed command.**
