#!/usr/bin/env python3
"""
Create research_results.json from research optimization journal
"""

import json
import re
from datetime import datetime
from pathlib import Path

def parse_research_journal():
    """Parse research optimization journal"""
    workspace = Path.home() / ".openclaw" / "workspace"
    research_path = workspace / "research_optimization_journal.md"
    
    if not research_path.exists():
        return []
    
    with open(research_path, 'r') as f:
        content = f.read()
    
    results = []
    
    # Look for the skipped/low grade tracking table
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for i, line in enumerate(lines):
        if "Skipped/Low Grade Tracking" in line or "skipped/low grade tracking" in line.lower():
            in_table = True
            continue
        
        if in_table and "|" in line and "Date" in line and "Ticker" in line:
            # Found header row
            headers = [h.strip() for h in line.split('|') if h.strip()]
            continue
        
        if in_table and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [v.strip() for v in line.split('|') if v.strip()]
            
            # Skip if not enough values or header row
            if len(values) < len(headers) or values[0] == "Date":
                continue
            
            # Create row dictionary
            row = {}
            for j, header in enumerate(headers):
                if j < len(values):
                    row[header] = values[j]
                else:
                    row[header] = ''
            
            # Convert to research result
            result = parse_research_row(row)
            if result:
                results.append(result)
    
    return results

def parse_research_row(row):
    """Convert a research table row to JSON format"""
    try:
        date = row.get("Date", "").strip()
        ticker = row.get("Ticker", "").strip()
        grade = row.get("Our Grade", "").strip()
        
        if not date or not ticker:
            return None
        
        # Parse expected move from grade (simplified)
        expected_move = None
        if "(" in grade and ")" in grade:
            # Extract score from format like "C+ (75/100)"
            match = re.search(r'\((\d+)', grade)
            if match:
                score = int(match.group(1))
                # Convert score to expected move (simplified)
                expected_move = score / 10.0
        
        # Parse actual outcome
        outcome = row.get("Actual Outcome", "").strip()
        within_em = row.get("Within EM?", "").strip()
        
        # Determine if trade was recommended (grade B or above)
        trade_recommended = False
        if grade and grade[0] in ['A', 'B']:
            trade_recommended = True
        
        # Determine if user traded (simplified - check if ticker appears in trades)
        user_traded = False
        
        # Parse calibration note
        calibration_note = row.get("Grade Accuracy", "").strip()
        
        return {
            "date": date,
            "ticker": ticker,
            "grade": grade.split()[0] if grade else None,  # Just the letter grade
            "expected_move": expected_move,
            "actual_move": None,  # Would need to parse from outcome
            "within_em": True if within_em and within_em.upper() == "YES" else False if within_em and within_em.upper() == "NO" else None,
            "trade_recommended": trade_recommended,
            "user_traded": user_traded,
            "outcome": outcome,
            "calibration_note": calibration_note
        }
    except Exception as e:
        print(f"Error parsing research row: {e}")
        return None

def main():
    """Main function"""
    print("Creating research_results.json...")
    
    # Parse research data
    results = parse_research_journal()
    
    # Create research JSON
    research_json = {
        "results": results
    }
    
    # Save to file
    workspace = Path.home() / ".openclaw" / "workspace"
    output_path = workspace / "data" / "research_results.json"
    
    with open(output_path, 'w') as f:
        json.dump(research_json, f, indent=2)
    
    print(f"✅ Research results created!")
    print(f"   Results: {len(results)}")
    print(f"   Output file: {output_path}")
    
    # Print sample
    if results:
        print("\nSample results:")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result['date']} {result['ticker']}: Grade {result.get('grade', 'N/A')}")

if __name__ == "__main__":
    main()