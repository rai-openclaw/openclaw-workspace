# Technical Design Spec: Remove Manual Totals - Full Refactor

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Current State (Problematic)

**Source Data (unified_portfolio_tracker.md):**
- Manual header totals: `**Total Value:** $300,124` ← FAKE DATA
- Stock tables with calculated values: `| $18.68 | $26,152.00 |` ← Can be derived from shares × price

**Parser Behavior:**
- Reads header totals → `account_data['total_value']` ← WRONG
- Reads position values from tables
- Dashboard shows header totals ← WRONG

**Result:** Data doesn't add up when prices change or trades happen

---

## Target State (Correct)

**Source Data (minimal truth):**
- Positions: ticker, shares, cost basis only
- Cash: dollar amounts
- SGOV: share count
- ETH: amount
- Options: contracts, strikes, etc.

**NO calculated values, NO totals**

**Parser Behavior:**
- Calculate position value = shares × live price (from API)
- Calculate account total = sum(positions) + cash + SGOV + ETH + options
- Calculate grand total = sum(account totals)

**Result:** Always correct, always up-to-date

---

## Impact Analysis

### What Changes

| Component | Current | Target |
|-----------|---------|--------|
| **Source Data** | Has totals & calculated values | Has only raw data (shares, cost basis) |
| **Parser** | Reads totals from headers | Calculates totals from raw data |
| **Price Source** | Static prices in tables | Live prices from API (Finnhub) |
| **Value Calculation** | Static from tables | Dynamic: shares × live price |

### API Contract Changes

**Current API returns:**
```json
{
  "account_total": 1662256.29,  // From header (fake)
  "total_value": 1559644.47,     // Sum of position values from tables
  "positions": [...]
}
```

**New API returns:**
```json
{
  "account_total": 1662256.29,  // CALCULATED: sum of all components
  "total_value": 1559644.47,     // CALCULATED: sum of position values (shares × live price)
  "positions": [...]              // Each has shares, cost_basis, live_price, calculated_value
}
```

**Dashboard impact:** NONE - same fields, same format

---

## Implementation Plan

### Phase 1: Modify Parser (server.py)

**Changes:**
1. Remove header total parsing
2. Calculate position values: `shares × live_price` (not from table)
3. Calculate account totals: sum of all components
4. Fetch live prices from Finnhub for all tickers

**Functions modified:**
- `parse_unified_tracker()` - remove total_value from header parsing
- `api_portfolio()` - calculate totals dynamically

### Phase 2: Modify Source Data (unified_portfolio_tracker.md)

**Simplify tables to only raw data:**

**Before:**
```markdown
| Ticker | Shares | Current Price | Current Value | Cost Basis |
|--------|--------|---------------|---------------|------------|
| AAPL   | 100    | $150.00       | $15,000.00    | $12,000    |
```

**After:**
```markdown
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| AAPL   | 100    | $12,000    |
```

**Remove:**
- All header totals
- All calculated columns (Current Price, Current Value from tables)
- Keep only: shares, cost basis (for returns calculation)

### Phase 3: Add Live Price Fetching

**New function:** `fetch_live_prices(tickers)`
- Query Finnhub for current prices
- Cache for 5 minutes
- Calculate position values dynamically

---

## Rollback Safety

**This is a breaking change to source data format.**

**Safety measures:**
1. Create backup of current unified_portfolio_tracker.md
2. Test parser with new format before deploying
3. Dashboard remains unchanged (same API contract)

---

## Files to Modify

| File | Changes |
|------|---------|
| `server.py` | Remove header total parsing, add live price fetching, calculate totals dynamically |
| `portfolio/unified_portfolio_tracker.md` | Remove totals, simplify to raw data only |

---

## Verification

After implementation:
- Change AAPL price in Finnhub → portfolio updates automatically
- Add trade → update shares, total recalculates automatically
- No manual total updates ever needed
- Gap = $0 always

---

**Awaiting Proceed.**
