#!/usr/bin/env python3
"""
risk_explainer_llm.py - LLM explanation layer for risk flags
Adds human-readable explanations for risk flags.
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_final.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_final.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

# OpenAI config
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] LLM: {msg}\n")
    print(f"[{timestamp}] {msg}")

def load_analysis():
    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return []
    with open(INPUT_FILE) as f:
        return json.load(f)

def call_llm(prompt):
    """Call LLM for explanation"""
    if not OPENAI_KEY:
        log("No OPENAI_API_KEY - skipping LLM")
        return None
    
    try:
        import requests
        
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            log(f"LLM error: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"LLM exception: {e}")
        return None

def explain_flag(ticker, flag_type, context):
    """Get LLM explanation for a flag"""
    
    prompts = {
        "recent_drift": f"Why might {ticker}'s recent price drift matter for an earnings options trade? Context: {context}. Provide 1-3 sentences.",
        "sector_stress": f"Why might sector weakness matter for {ticker} earnings options? Context: {context}. Provide 1-3 sentences.",
        "market_regime": f"Why does high VIX ({context}) matter for {ticker} earnings options? Provide 1-3 sentences.",
        "macro_event_nearby": f"Why does the nearby macro event matter for {ticker} earnings options? Context: {context}. Provide 1-3 sentences."
    }
    
    prompt = prompts.get(flag_type, f"Explain {flag_type} for {ticker}")
    
    explanation = call_llm(prompt)
    
    if explanation:
        return explanation.strip()
    return None

def process_tickers(analysis_data):
    """Process each ticker and add explanations"""
    
    explained_count = 0
    
    for item in analysis_data:
        ticker = item.get("ticker")
        risk_flags = item.get("risk_flags", {})
        
        if not any(risk_flags.values()):
            # No flags - skip
            item["risk_explanations"] = {}
            continue
        
        explanations = {}
        
        # Get market context
        vix = 18.6  # Would be passed from risk filter
        
        # Explain each true flag
        for flag_type, is_flagged in risk_flags.items():
            if not is_flagged:
                continue
            
            context = ""
            if flag_type == "market_regime":
                context = f"VIX={vix}"
            elif flag_type == "recent_drift":
                market = item.get("market", {})
                context = f"price=${market.get('price')}"
            else:
                context = "current conditions"
            
            explanation = explain_flag(ticker, flag_type, context)
            if explanation:
                explanations[flag_type] = explanation
        
        item["risk_explanations"] = explanations
        
        if explanations:
            explained_count += 1
            log(f"  {ticker}: {list(explanations.keys())}")
    
    return analysis_data, explained_count

def main():
    log("=== Starting risk_explainer_llm.py ===")
    
    # Load analysis
    analysis_data = load_analysis()
    
    if not analysis_data:
        log("No analysis data - exiting")
        return
    
    log(f"Loaded {len(analysis_data)} tickers")
    
    # Process
    results, explained_count = process_tickers(analysis_data)
    
    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    log(f"Added explanations to {explained_count} tickers")
    log(f"Wrote to {OUTPUT_FILE}")
    
    # Print sample
    print("\n=== Sample Output ===")
    for item in results[:2]:
        print(f"{item.get('ticker')}: {item.get('risk_explanations', {})}")
    
    log("=== Completed ===")
    return explained_count

if __name__ == "__main__":
    main()
