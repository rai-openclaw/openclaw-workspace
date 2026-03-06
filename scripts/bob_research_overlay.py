#!/usr/bin/env python3
"""
bob_research_overlay.py - Qualitative research overlay using Bob agent
Reads analysis_raw.json, calls Bob for each ticker, adds research field.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_raw.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_with_research.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

MAX_TICKERS = 20

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] BOB: {msg}\n")
    print(f"[{timestamp}] BOB: {msg}")

def call_bob(ticker, price, em, report_date):
    """Call Bob agent for qualitative research."""
    prompt = f"""You are generating concise structured earnings notes for a quantitative options system. Analyze upcoming earnings for {ticker}.

Context:
- Price: ${price}
- Implied move (EM): {em}%
- Report date: {report_date}

Instructions:
- Briefly state what the company does (1 sentence)
- Identify specific business drivers relevant to this earnings
- Do NOT restate the EM unless materially relevant
- Avoid generic statements about volatility
- Focus on business catalysts and real risks
- Be concise

Return STRICT JSON:
{{
  "short_note": "...",
  "summary": "...",
  "catalysts": ["..."],
  "risks": ["..."],
  "tone": "bullish | neutral | risky"
}}

Constraints:
- short_note: max 120 characters
- summary: max 3 sentences
- max 3 catalysts
- max 3 risks
- no extra commentary"""

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--agent", "bob", "--message", prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE)
        )
        
        if result.returncode != 0:
            log(f"  {ticker}: Bob call failed: {result.stderr[:100]}")
            return None
        
        # Parse JSON from response
        output = result.stdout.strip()
        
        # Try to find JSON in output
        if "{" in output and "}" in output:
            start = output.find("{")
            end = output.rfind("}") + 1
            json_str = output[start:end]
            research = json.loads(json_str)
            
            # Validate required fields
            if all(k in research for k in ["short_note", "summary", "catalysts", "risks", "tone"]):
                log(f"  {ticker}: Research added ({research.get('tone', 'neutral')})")
                return research
        
        log(f"  {ticker}: Invalid JSON response")
        return None
        
    except subprocess.TimeoutExpired:
        log(f"  {ticker}: Timeout")
        return None
    except json.JSONDecodeError as e:
        log(f"  {ticker}: JSON parse error: {str(e)[:50]}")
        return None
    except Exception as e:
        log(f"  {ticker}: Error: {str(e)[:50]}")
        return None

def main():
    log("=== Starting bob_research_overlay.py ===")
    
    # Load analysis
    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return
    
    with open(INPUT_FILE) as f:
        input_data = json.load(f)
    
    # Handle both old format (array) and new format (object with metadata)
    if isinstance(input_data, dict) and "candidates" in input_data:
        metadata = input_data.get("metadata", {})
        analysis_data = input_data.get("candidates", [])
    else:
        metadata = {}
        analysis_data = input_data
    
    # Always write output file, even if empty - prevents stale data bug
    if not analysis_data:
        log("No candidates — writing empty research output")
        output_data = {
            "metadata": metadata,
            "candidates": []
        }
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f, indent=2)
        log(f"Wrote empty output to {OUTPUT_FILE}")
        log("=== Completed ===")
        return
    
    log(f"Loaded {len(analysis_data)} tickers")
    
    # Limit to max tickers
    to_process = analysis_data[:MAX_TICKERS]
    log(f"Processing up to {len(to_process)} tickers...")
    
    processed = 0
    succeeded = 0
    
    for item in to_process:
        ticker = item.get("ticker")
        
        # Get context
        market = item.get("market", {})
        options = item.get("options", {})
        report = item.get("report", {})
        
        price = market.get("price")
        em = options.get("em_percent")
        report_date = report.get("date")
        
        if not ticker:
            continue
        
        # Call Bob
        research = call_bob(ticker, price, em, report_date)
        
        if research:
            # Add research field
            item["research"] = research
            succeeded += 1
        else:
            # Add empty research on failure
            item["research"] = {
                "short_note": "Research unavailable",
                "summary": "Could not generate research.",
                "catalysts": [],
                "risks": [],
                "tone": "neutral"
            }
        
        processed += 1
    
    # Write output with metadata preserved
    output_data = {
        "metadata": metadata,
        "candidates": analysis_data
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)
    
    log(f"Processed {processed} tickers, added research to {succeeded}")
    log(f"Wrote to {OUTPUT_FILE}")
    log("=== Completed ===")

if __name__ == "__main__":
    main()
