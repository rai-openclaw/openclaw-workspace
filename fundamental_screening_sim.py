#!/usr/bin/env python3
import json
import random

# Load filtered stocks from Phase 2
with open('phase2_filter_results.json', 'r') as f:
    phase2_results = json.load(f)

filtered_stocks = phase2_results['filtered_stocks']

# Fundamental screening criteria (simulated)
SCREENING_CRITERIA = {
    "min_market_cap": 1.0,  # $1B minimum
    "max_debt_to_equity": 2.0,  # Maximum debt/equity ratio
    "min_revenue_growth": 0.05,  # 5% minimum revenue growth
    "max_volatility": 0.40,  # Maximum 40% annual volatility
    "min_analyst_coverage": 3,  # Minimum 3 analysts covering
}

def simulate_fundamental_data(stock):
    """Simulate fundamental data for demonstration."""
    # Different stocks get different simulated profiles
    seed = sum(ord(c) for c in stock)  # Deterministic based on ticker
    
    random.seed(seed)
    
    return {
        "market_cap_bil": round(random.uniform(0.5, 50.0), 2),
        "debt_to_equity": round(random.uniform(0.1, 3.0), 2),
        "revenue_growth": round(random.uniform(-0.10, 0.30), 3),
        "volatility": round(random.uniform(0.20, 0.60), 3),
        "analyst_coverage": random.randint(1, 20),
        "profit_margin": round(random.uniform(-0.20, 0.40), 3),
    }

def apply_fundamental_screening(stock, data):
    """Apply fundamental screening criteria."""
    failures = []
    
    if data["market_cap_bil"] < SCREENING_CRITERIA["min_market_cap"]:
        failures.append(f"Market cap ${data['market_cap_bil']}B < ${SCREENING_CRITERIA['min_market_cap']}B")
    
    if data["debt_to_equity"] > SCREENING_CRITERIA["max_debt_to_equity"]:
        failures.append(f"Debt/Equity {data['debt_to_equity']} > {SCREENING_CRITERIA['max_debt_to_equity']}")
    
    if data["revenue_growth"] < SCREENING_CRITERIA["min_revenue_growth"]:
        failures.append(f"Revenue growth {data['revenue_growth']:.1%} < {SCREENING_CRITERIA['min_revenue_growth']:.1%}")
    
    if data["volatility"] > SCREENING_CRITERIA["max_volatility"]:
        failures.append(f"Volatility {data['volatility']:.1%} > {SCREENING_CRITERIA['max_volatility']:.1%}")
    
    if data["analyst_coverage"] < SCREENING_CRITERIA["min_analyst_coverage"]:
        failures.append(f"Analyst coverage {data['analyst_coverage']} < {SCREENING_CRITERIA['min_analyst_coverage']}")
    
    return failures

def main():
    print("=== FUNDAMENTAL SCREENING SIMULATION ===")
    print(f"Screening {len(filtered_stocks)} stocks from Phase 2")
    print("Criteria:")
    for key, value in SCREENING_CRITERIA.items():
        print(f"  {key}: {value}")
    print()
    
    passed_stocks = []
    failed_stocks = []
    
    print("=== STOCK-BY-STOCK ANALYSIS ===")
    for stock in filtered_stocks:
        data = simulate_fundamental_data(stock)
        failures = apply_fundamental_screening(stock, data)
        
        print(f"\n{stock}:")
        print(f"  Market Cap: ${data['market_cap_bil']}B")
        print(f"  Debt/Equity: {data['debt_to_equity']}")
        print(f"  Revenue Growth: {data['revenue_growth']:.1%}")
        print(f"  Volatility: {data['volatility']:.1%}")
        print(f"  Analyst Coverage: {data['analyst_coverage']}")
        print(f"  Profit Margin: {data['profit_margin']:.1%}")
        
        if failures:
            print(f"  ❌ FAILED: {', '.join(failures)}")
            failed_stocks.append({
                "stock": stock,
                "data": data,
                "failures": failures
            })
        else:
            print(f"  ✅ PASSED all criteria")
            passed_stocks.append({
                "stock": stock,
                "data": data
            })
    
    print("\n=== SCREENING RESULTS ===")
    print(f"Total screened: {len(filtered_stocks)}")
    print(f"Passed: {len(passed_stocks)}")
    print(f"Failed: {len(failed_stocks)}")
    
    # Save results
    result = {
        "date": "2026-02-18",
        "screening_criteria": SCREENING_CRITERIA,
        "total_screened": len(filtered_stocks),
        "passed_count": len(passed_stocks),
        "failed_count": len(failed_stocks),
        "passed_stocks": [item["stock"] for item in passed_stocks],
        "failed_stocks": failed_stocks,
        "phase2_input": phase2_results
    }
    
    with open('phase3_screening_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to phase3_screening_results.json")
    
    return passed_stocks

if __name__ == "__main__":
    main()