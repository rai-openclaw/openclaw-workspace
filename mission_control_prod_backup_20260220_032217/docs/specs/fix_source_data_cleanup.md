# Technical Design Spec: Fix Source Data - Remove Manual/Fake Data

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problems Identified

### 1. Missing Cash & Equivalents Sections
**Schwab CSP** - Has SGOV $6,607.06 in source but no "Cash & Equivalents" table to parse it from
**Schwab #2** - Has SGOV $6,607.06 in source but no "Cash & Equivalents" table

### 2. Outdated Header Totals
**Robinhood header** says $300,124 but actual table sum is $255,200
This is fake/manual data that doesn't match the tables.

### 3. Wrong Account Values in Headers
Multiple account headers have outdated/incorrect totals that don't match their table data.

---

## Solution

### Fix 1: Add Missing Cash & Equivalents Tables
Add "### Cash & Equivalents" sections to:
- Schwab CSP (with SGOV $6,607.06)
- Schwab #2 (with SGOV $6,607.06)

### Fix 2: Recalculate All Header Totals
Remove fake header totals and calculate from actual table data:
- Sum all Stock Positions
- Sum all Index Funds
- Sum all Cash & Equivalents  
- Sum all Options
- Sum all Crypto
- Total = sum of all above

### Fix 3: Update Cross-Account Summary
Grand total should be sum of all account calculated totals (not manual headers).

---

## Files to Modify

| File | Changes |
|------|---------|
| `portfolio/unified_portfolio_tracker.md` | Add Cash tables, fix header totals, remove fake data |

---

## Implementation Steps

### Step 1: Add Cash & Equivalents to Schwab CSP
Insert after CSP Positions:
```markdown
### Cash & Equivalents
| Position | Shares | Price | Value |
|----------|--------|-------|-------|
| SGOV | 65.7288 | $100.52 | $6,607.06 |
```

### Step 2: Add Cash & Equivalents to Schwab #2
Insert after CSP Positions:
```markdown
### Cash & Equivalents
| Position | Shares | Price | Value |
|----------|--------|-------|-------|
| SGOV | 65.7288 | $100.52 | $6,607.06 |
```

### Step 3: Recalculate Robinhood Header
Sum from tables:
- Stocks: $236,539.75
- Cash: $11,432
- SGOV: $20,224.62
- ETH: $32,004
- Options: -$45,000
- **New Total: $255,200.37**

### Step 4: Recalculate All Account Headers
Do same for SEP-IRA, Schwab CSP, Schwab #2, Roth IRA

### Step 5: Update Cross-Account Summary
Grand Total = sum of all account calculated totals

---

## Verification

After fix:
- All accounts have Cash & Equivalents tables
- All header totals match sum of their tables
- No manual/fake data remaining
- API totals match calculated totals exactly
- Gap = $0

---

**Awaiting Proceed.**
