#!/usr/bin/env python3
"""
grading_engine_v1.py - Deterministic grading engine
Calculates grades based on probabilities, fundamentals, and risk.
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_DIR = WORKSPACE / "config"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_with_risk.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_final.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] GRADE: {msg}\n")
    print(f"[{timestamp}] GRADE: {msg}")

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def load_analysis():
    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return []
    with open(INPUT_FILE) as f:
        return json.load(f)

def load_rules():
    rules_file = CONFIG_DIR / "grading_rules.json"
    return load_json(rules_file)

def calculate_em_respect_score(probs, weights):
    """Score based on probability of staying within EM"""
    if not probs:
        return 0, "No probability data"
    
    p1 = probs.get("down_1x", 0) or 0
    p1_5 = probs.get("down_1_5x", 0) or 0
    
    # If P(↓1.5x) > 85%, full points
    if p1_5 >= 0.85:
        score = weights["em_respect"]
        reason = f"P(↓1.5x)={p1_5:.0%} - Excellent EM respect"
    # If P(↓1.5x) > 70%, partial
    elif p1_5 >= 0.70:
        score = int(weights["em_respect"] * 0.7)
        reason = f"P(↓1.5x)={p1_5:.0%} - Good EM respect"
    else:
        score = int(weights["em_respect"] * 0.4)
        reason = f"P(↓1.5x)={p1_5:.0%} - Weak EM respect"
    
    return score, reason

def calculate_predictability_score(em, weights):
    """Placeholder: based on EM consistency"""
    # For now, give partial points if EM exists
    if em and em > 0:
        return int(weights["predictability"] * 0.5), "Placeholder - awaiting historical data"
    return 0, "No EM data"

def calculate_premium_score(em, market_price, weights):
    """Placeholder: based on EM vs historical"""
    if em and em > 0 and market_price:
        # Higher EM = more premium = higher score
        score = min(int(weights["premium"] * (em * 5)), weights["premium"])
        reason = f"EM={em:.1f}% - Moderate premium"
        return score, reason
    return 0, "No EM data"

def calculate_assignment_score(market_price, weights):
    """Score based on assignment desirability"""
    if not market_price:
        return 0, "No price data"
    
    # Higher priced stocks = better assignment
    if market_price >= 50:
        score = weights["assignment"]
        reason = f"Price=${market_price} - Good assignment potential"
    elif market_price >= 20:
        score = int(weights["assignment"] * 0.7)
        reason = f"Price=${market_price} - Moderate assignment"
    else:
        score = int(weights["assignment"] * 0.4)
        reason = f"Price=${market_price} - Lower assignment appeal"
    
    return score, reason

def calculate_liquidity_score(market_price, weights):
    """Placeholder for liquidity"""
    # Simple placeholder
    if market_price and market_price >= 20:
        return weights["liquidity"], "Placeholder - assuming liquidity"
    return int(weights["liquidity"] * 0.5), "Lower price may limit liquidity"

def get_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"

def get_risk_severity(risk_flags):
    """Determine risk severity level"""
    true_count = sum(1 for v in risk_flags.values() if v)
    
    if true_count == 0:
        return "NORMAL"
    elif true_count == 1:
        return "MILD"
    elif true_count == 2:
        return "ELEVATED"
    else:
        return "HIGH"

def process_tickers(analysis_data):
    """Process each ticker and calculate grades"""
    
    rules = load_rules()
    weights = rules.get("weights", {})
    
    graded_count = 0
    
    for item in analysis_data:
        ticker = item.get("ticker")
        
        # Get data
        options = item.get("options", {})
        market = item.get("market", {})
        probabilities = item.get("probabilities", {})
        risk_flags = item.get("risk_flags", {})
        
        print(f"DEBUG GRADING INPUT: {ticker} - probs={probabilities}, risk_flags={risk_flags}")
        
        em = options.get("em_percent")
        price = market.get("price")
        
        # Calculate component scores
        em_score, em_reason = calculate_em_respect_score(probabilities, weights)
        pred_score, pred_reason = calculate_predictability_score(em, weights)
        prem_score, prem_reason = calculate_premium_score(em, price, weights)
        assign_score, assign_reason = calculate_assignment_score(price, weights)
        liq_score, liq_reason = calculate_liquidity_score(price, weights)
        
        # Total score
        total_score = em_score + pred_score + prem_score + assign_score + liq_score
        
        # Get grade
        # If no EM data, set to PENDING
        if not em:
            grade = "PENDING"
            total_score = None
            risk_severity = get_risk_severity(risk_flags)
            
            item["grading"] = {
                "grade": grade,
                "score_total": total_score,
                "risk_severity": risk_severity,
                "data_ready": False,
                "components": {
                    "em_respect": { "score": 0, "reason": "No EM data" },
                    "predictability": { "score": 0, "reason": "No EM data" },
                    "premium_yield": { "score": 0, "reason": "No EM data" },
                    "assignment_desirability": { "score": 0, "reason": "No EM data" },
                    "liquidity": { "score": 0, "reason": "No EM data" }
                }
            }
            
            log(f"  {ticker}: PENDING (awaiting options data) - {risk_severity}")
            graded_count += 1
            continue
        
        # Normal grading
        grade = get_grade(total_score)
        
        # Risk severity
        risk_severity = get_risk_severity(risk_flags)
        
        # Update item
        item["grading"] = {
            "grade": grade,
            "score_total": total_score,
            "risk_severity": risk_severity,
            "data_ready": True,
            "components": {
                "em_respect": {
                    "score": em_score,
                    "reason": em_reason
                },
                "predictability": {
                    "score": pred_score,
                    "reason": pred_reason
                },
                "premium_yield": {
                    "score": prem_score,
                    "reason": prem_reason
                },
                "assignment_desirability": {
                    "score": assign_score,
                    "reason": assign_reason
                },
                "liquidity": {
                    "score": liq_score,
                    "reason": liq_reason
                }
            }
        }
        
        log(f"  {ticker}: {grade} ({total_score} pts) - {risk_severity}")
        graded_count += 1
    
    return analysis_data, graded_count

def main():
    log("=== Starting grading_engine_v1.py ===")
    
    # Load analysis
    analysis_data = load_analysis()
    
    if not analysis_data:
        log("No analysis data - exiting")
        return
    
    log(f"Loaded {len(analysis_data)} tickers")
    
    # Process
    results, graded_count = process_tickers(analysis_data)
    
    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    log(f"Graded {graded_count} tickers")
    log(f"Wrote to {OUTPUT_FILE}")
    
    # Archive to history (immutable storage)
    history_dir = OUTPUT_FILE.parent / "history"
    history_dir.mkdir(exist_ok=True)
    
    # Get date from first ticker
    if results:
        report_date = results[0].get("report", {}).get("date", datetime.now().strftime("%Y-%m-%d"))
        history_file = history_dir / f"analysis_{report_date}.json"
        
        with open(history_file, "w") as f:
            json.dump(results, f, indent=2)
        
        log(f"ARCHIVE: Saved report to history/analysis_{report_date}.json")
    
    # Print sample
    print("\n=== Sample Output ===")
    for item in results[:2]:
        grading = item.get("grading", {})
        print(f"{item.get('ticker')}: {grading.get('grade')} ({grading.get('score_total')}) - {grading.get('risk_severity')}")
    
    log("=== Completed ===")
    return graded_count

if __name__ == "__main__":
    main()
