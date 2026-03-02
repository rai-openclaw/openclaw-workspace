# TDS: Data Validation Layer

**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## What the Validation Layer Does

Catches data problems BEFORE they break the UI or cause confusion.

---

## Validation Checks

### 1. Source Data Validation
**Checks on `unified_portfolio_tracker.md`:**

- [ ] All required columns present (Ticker, Shares, Cost Basis)
- [ ] No duplicate tickers in same account
- [ ] Shares > 0 for all positions
- [ ] Cost basis >= 0
- [ ] Cash & Equivalents section exists for each account
- [ ] No SGOV in Stocks section (prevents double count)

### 2. Price Cache Validation
**Checks on `price_cache.json`:**

- [ ] All tickers from source have prices
- [ ] No prices = 0 (unless flagged as unavailable)
- [ ] Prices updated within last 30 days
- [ ] Price source recorded (finnhub/yahoo/cached)

### 3. Calculation Validation
**After parsing:**

- [ ] Stocks total + Options total + Cash total + Misc total = Grand total
- [ ] All aggregated shares match sum of account shares
- [ ] No negative values where not expected
- [ ] Return % calculable (cost basis > 0)

### 4. Cross-Reference Validation
**Account-level checks:**

- [ ] Each account's positions sum to reasonable total
- [ ] Cash amounts are positive
- [ ] Options contracts match expected format

---

## Implementation

### File: `portfolio/data_validator.py` (NEW)
```python
def validate_source_data(filepath):
    """Validate unified_portfolio_tracker.md"""
    errors = []
    warnings = []
    
    # Parse file
    accounts = parse_unified_tracker(filepath)
    
    for account_name, data in accounts.items():
        # Check for duplicate tickers
        tickers = [s['ticker'] for s in data['stocks']]
        duplicates = find_duplicates(tickers)
        if duplicates:
            errors.append(f"{account_name}: Duplicate tickers: {duplicates}")
        
        # Check SGOV not in stocks
        for stock in data['stocks']:
            if stock['ticker'] == 'SGOV':
                errors.append(f"{account_name}: SGOV should be in Cash section, not Stocks")
        
        # Check positive shares
        for stock in data['stocks']:
            if stock['shares'] <= 0:
                errors.append(f"{account_name}: {stock['ticker']} has invalid shares: {stock['shares']}")
        
        # Check cost basis present
        for stock in data['stocks']:
            if stock['cost_basis'] < 0:
                errors.append(f"{account_name}: {stock['ticker']} has negative cost basis")
    
    return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}


def validate_price_cache(accounts, price_cache):
    """Validate all tickers have prices"""
    errors = []
    warnings = []
    
    # Collect all tickers
    all_tickers = set()
    for account in accounts.values():
        for stock in account['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                all_tickers.add(stock['ticker'])
    
    # Check each ticker has price
    for ticker in all_tickers:
        if ticker not in price_cache:
            errors.append(f"No price for {ticker}")
        elif price_cache[ticker].get('price', 0) == 0:
            warnings.append(f"{ticker} has zero price")
        elif price_cache[ticker].get('source') == 'cached':
            # Check age
            last_updated = price_cache[ticker].get('last_updated')
            if last_updated:
                age_days = (datetime.now() - datetime.fromisoformat(last_updated)).days
                if age_days > 30:
                    warnings.append(f"{ticker} price is {age_days} days old")
    
    return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}


def validate_calculations(portfolio_data):
    """Validate totals add up"""
    errors = []
    
    stocks_total = sum(s['total_value'] for s in portfolio_data['stocks'])
    options_total = sum(o['current_value'] for o in portfolio_data['options'])
    cash_total = portfolio_data['cash']['Cash']['total'] + portfolio_data['cash']['SGOV']['total']
    misc_total = sum(m['total_value'] for m in portfolio_data['misc'])
    
    calculated_grand = stocks_total + options_total + cash_total + misc_total
    reported_grand = portfolio_data['totals']['grand_total']
    
    if abs(calculated_grand - reported_grand) > 1:
        errors.append(f"Grand total mismatch: calculated={calculated_grand}, reported={reported_grand}")
    
    return {'valid': len(errors) == 0, 'errors': errors}
```

### Integration in server.py
```python
@app.route('/api/portfolio')
def api_portfolio():
    """Return portfolio data with validation"""
    # Load data
    accounts = parse_unified_tracker_v2(PORTFOLIO_FILE)
    load_price_cache()
    
    # Validate
    validation_results = {
        'source': validate_source_data(PORTFOLIO_FILE),
        'prices': validate_price_cache(accounts, price_cache),
    }
    
    # Build portfolio data
    portfolio_data = build_portfolio_data(accounts, price_cache)
    
    # Validate calculations
    validation_results['calculations'] = validate_calculations(portfolio_data)
    
    # Return data + validation results
    return jsonify({
        **portfolio_data,
        'validation': validation_results,
        'has_issues': not all(v['valid'] for v in validation_results.values())
    })
```

### Dashboard UI for Validation Errors
```javascript
// Show validation warnings at top of portfolio
if (data.has_issues) {
    let warningsHtml = '<div class="validation-warnings">';
    
    if (data.validation.source.errors.length > 0) {
        warningsHtml += '<div class="error"><strong>Data Errors:</strong><ul>';
        data.validation.source.errors.forEach(e => {
            warningsHtml += `<li>${e}</li>`;
        });
        warningsHtml += '</ul></div>';
    }
    
    if (data.validation.prices.warnings.length > 0) {
        warningsHtml += '<div class="warning"><strong>Price Warnings:</strong><ul>';
        data.validation.prices.warnings.forEach(w => {
            warningsHtml += `<li>${w}</li>`;
        });
        warningsHtml += '</ul></div>';
    }
    
    warningsHtml += '</div>';
    document.getElementById('portfolio-content').insertAdjacentHTML('afterbegin', warningsHtml);
}
```

---

## Files to Create/Modify

| File | Action | Lines |
|------|--------|-------|
| `portfolio/data_validator.py` | Create new | ~150 lines |
| `server.py` | Add validation calls | ~20 lines |
| `dashboard.html` | Add warning display | ~30 lines |

---

## What This Prevents

| Issue | Caught By | User Sees |
|-------|-----------|-----------|
| SGOV in Stocks | Source validation | "SGOV should be in Cash section" |
| Missing price | Price validation | "No price for XYZ" |
| Duplicate tickers | Source validation | "Duplicate tickers: AAPL" |
| Negative shares | Source validation | "Invalid shares: -100" |
| Totals don't add up | Calc validation | "Grand total mismatch" |
| Stale prices (>30d) | Price validation | "XYZ price is 45 days old" |

---

**Proceed with validation layer implementation?**
