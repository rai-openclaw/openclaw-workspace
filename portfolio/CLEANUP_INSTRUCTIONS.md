# Source Data Cleanup Instructions

## Changes Needed in unified_portfolio_tracker.md

### 1. Remove Header Totals
Delete lines like:
```
**Total Value:** $300,124
```

### 2. Simplify Stock Position Tables

**BEFORE:**
```markdown
| Ticker | Company | Shares | Current Price | Current Value | Cost Basis | Total Return | Return % |
|--------|---------|--------|---------------|---------------|------------|--------------|----------|
| AAPL   | Apple   | 100    | $150.00       | $15,000.00    | $12,000    | +$3,000      | +25%     |
```

**AFTER:**
```markdown
| Ticker | Company | Shares | Cost Basis |
|--------|---------|--------|------------|
| AAPL   | Apple   | 100    | $12,000    |
```

### 3. Simplify Index Funds Tables

**BEFORE:**
```markdown
| Ticker | Fund Name | Shares | Current Price | Current Value |
|--------|-----------|--------|---------------|---------------|
| VSEQX  | Vanguard  | 1000   | $39.46        | $39,460.00    |
```

**AFTER:**
```markdown
| Ticker | Fund Name | Shares |
|--------|-----------|--------|
| VSEQX  | Vanguard  | 1000   |
```

### 4. Keep Cash & Equivalents (raw data)
```markdown
| Position | Shares | Value |
|----------|--------|-------|
| SGOV     | 201.20 | $20,224.62 |
| Cash     | -      | $11,432.00 |
```

### 5. Keep Crypto (raw data)
```markdown
| Asset | Amount |
|-------|--------|
| ETH   | 11.43  |
```

### 6. Keep Options (raw data)
```markdown
| Ticker | Type | Strike | Expiration | Quantity | Price |
|--------|------|--------|------------|----------|-------|
| PYPL   | PUT  | $45.00 | Feb 20     | -10      | $4.50 |
```

## Result
- All calculated values removed
- All totals removed
- Only raw, input data remains
- System calculates everything dynamically
