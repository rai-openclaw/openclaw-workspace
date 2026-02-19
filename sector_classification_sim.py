#!/usr/bin/env python3
import json

# Simulated sector database (for demonstration)
SECTOR_DB = {
    "KGC": "Materials",  # Kinross Gold - Materials
    "CVNA": "Consumer Discretionary",  # Carvana - Consumer Discretionary
    "CDE": "Materials",  # Coeur Mining - Materials
    "PAAS": "Materials",  # Pan American Silver - Materials
    "DASH": "Consumer Discretionary",  # DoorDash - Consumer Discretionary
    "RGLD": "Materials",  # Royal Gold - Materials (Precious Metals)
    "EQX": "Materials",  # Equinox Gold - Materials
    "EBAY": "Consumer Discretionary",  # eBay - Consumer Discretionary
    "RELY": "Technology"  # Remitly - Technology (FinTech)
}

# Sectors to exclude
EXCLUDED_SECTORS = ["Real Estate", "Utilities", "Consumer Staples"]

def apply_sector_filter(stocks):
    """Apply sector filter to list of stocks."""
    filtered = []
    excluded = []
    
    for stock in stocks:
        sector = SECTOR_DB.get(stock, "Unknown")
        
        if sector in EXCLUDED_SECTORS:
            excluded.append((stock, sector))
        else:
            filtered.append((stock, sector))
    
    return filtered, excluded

def main():
    # Load earnings schedule
    with open('weekly_earnings_schedule.json', 'r') as f:
        earnings = json.load(f)
    
    target_stocks = earnings['schedule']['2026-02-18']['AMC']
    
    print("=== SECTOR FILTER SIMULATION ===")
    print(f"Target stocks: {target_stocks}")
    print(f"Excluded sectors: {EXCLUDED_SECTORS}")
    print()
    
    filtered, excluded = apply_sector_filter(target_stocks)
    
    print("=== FILTER RESULTS ===")
    print(f"Stocks passing filter ({len(filtered)}):")
    for stock, sector in filtered:
        print(f"  {stock}: {sector}")
    
    print()
    print(f"Stocks excluded ({len(excluded)}):")
    for stock, sector in excluded:
        print(f"  {stock}: {sector} (excluded sector)")
    
    print()
    print("=== SUMMARY ===")
    print(f"Total stocks: {len(target_stocks)}")
    print(f"Passed filter: {len(filtered)}")
    print(f"Excluded: {len(excluded)}")
    
    # Save filtered results
    filtered_stocks = [stock for stock, _ in filtered]
    result = {
        "date": "2026-02-18",
        "time_slot": "AMC",
        "original_count": len(target_stocks),
        "filtered_count": len(filtered),
        "excluded_count": len(excluded),
        "filtered_stocks": filtered_stocks,
        "excluded_stocks": [{"stock": stock, "sector": sector} for stock, sector in excluded],
        "filter_applied": "Sector filter (exclude REITs, Utilities, Consumer Staples)",
        "always_include_bypass": "None"
    }
    
    with open('phase2_filter_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nResults saved to phase2_filter_results.json")

if __name__ == "__main__":
    main()