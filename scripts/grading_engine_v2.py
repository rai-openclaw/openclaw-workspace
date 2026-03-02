#!/usr/bin/env python3
"""
grading_engine_v2.py - Deterministic grading engine (Refined Safe Version)
Survivability + EM Tension + Assignment + Liquidity scoring model.
"""

import json
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_with_risk.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_final.json"
HISTORY_DIR = DATA_DIR / "history"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

# Weights (unchanged)
WEIGHTS = {
    "survivability": 45,
    "em_tension": 25,
    "assignment": 15,
    "liquidity": 10,
    "risk_penalty": 5
}


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] GRADE: {msg}\n")
    print(f"[{timestamp}] GRADE: {msg}")


# ===============================
# COMPONENT SCORING
# ===============================

def calculate_survivability_score(down_1_5x):
    if down_1_5x is None:
        return 0, "No probability data"

    pct = down_1_5x * 100

    if pct >= 95:
        return 45, f"Survival {pct:.0f}%"
    elif pct >= 90:
        return 38, f"Survival {pct:.0f}%"
    elif pct >= 85:
        return 30, f"Survival {pct:.0f}%"
    elif pct >= 80:
        return 20, f"Survival {pct:.0f}%"
    else:
        return 5, f"Survival {pct:.0f}%"


def calculate_em_tension_score(em_percent, median_move):
    if em_percent is None:
        return 5, "No EM data"

    if median_move is not None:
        median_pct = median_move * 100

        if em_percent >= median_pct * 1.2:
            return 25, f"EM {em_percent:.1f}% ≥1.2x median {median_pct:.1f}%"
        elif em_percent >= median_pct:
            return 18, f"EM {em_percent:.1f}% ≥ median {median_pct:.1f}%"
        else:
            return 5, f"EM {em_percent:.1f}% < median {median_pct:.1f}%"

    if em_percent < 3:
        return 5, f"Low EM {em_percent:.1f}%"
    elif em_percent < 5:
        return 10, f"EM {em_percent:.1f}%"
    elif em_percent < 8:
        return 18, f"EM {em_percent:.1f}%"
    elif em_percent <= 15:
        return 25, f"Strong EM {em_percent:.1f}%"
    else:
        return 15, f"Extreme EM {em_percent:.1f}%"


def calculate_assignment_score(market_price):
    if market_price is None:
        return 3, "No price data"

    if market_price >= 100:
        return 15, f"Price ${market_price}"
    elif market_price >= 50:
        return 12, f"Price ${market_price}"
    elif market_price >= 20:
        return 8, f"Price ${market_price}"
    else:
        return 3, f"Price ${market_price}"


def calculate_liquidity_score(volume):
    if volume is None or volume == 0:
        return 2, "No volume data"

    if volume >= 3_000_000:
        return 10, f"Vol {volume/1e6:.1f}M"
    elif volume >= 2_000_000:
        return 8, f"Vol {volume/1e6:.1f}M"
    elif volume >= 1_000_000:
        return 6, f"Vol {volume/1e6:.1f}M"
    elif volume >= 500_000:
        return 4, f"Vol {volume/1e6:.1f}M"
    else:
        return 2, f"Vol {volume/1e6:.1f}M"


def get_grade(score):
    if score >= 85:
        return "A"
    elif score >= 75:
        return "B+"
    elif score >= 65:
        return "B"
    elif score >= 55:
        return "C"
    else:
        return "D"


# ===============================
# PROCESSING
# ===============================

def process_tickers(analysis_data):
    results = []
    graded_count = 0

    for item in analysis_data:
        ticker = item.get("ticker")

        options = item.get("options", {})
        market = item.get("market", {})
        probabilities = item.get("probabilities", {})
        risk_flags = item.get("risk_flags", {})

        em = options.get("em_percent")
        price = market.get("price")

        volume = market.get("volume") or item.get("meta", {}).get("volume")

        down_1_5x = probabilities.get("down_1_5x")
        median_move = probabilities.get("median_move")

        surv_score, surv_reason = calculate_survivability_score(down_1_5x)
        em_score, em_reason = calculate_em_tension_score(em, median_move)
        assign_score, assign_reason = calculate_assignment_score(price)
        liq_score, liq_reason = calculate_liquidity_score(volume)

        risk_penalty = 0
        if risk_flags.get("recent_drift"):
            risk_penalty += WEIGHTS["risk_penalty"]
        if risk_flags.get("sector_stress"):
            risk_penalty += WEIGHTS["risk_penalty"]
        if risk_flags.get("market_regime"):
            risk_penalty += WEIGHTS["risk_penalty"]
        if risk_flags.get("macro_event_nearby"):
            risk_penalty += WEIGHTS["risk_penalty"]

        risk_penalty = min(risk_penalty, 10)

        total_score = max(0, surv_score + em_score + assign_score + liq_score - risk_penalty)

        grade = get_grade(total_score)

        risk_severity = (
            "NORMAL" if risk_penalty == 0
            else "ELEVATED" if risk_penalty <= 5
            else "HIGH"
        )

        item["grading"] = {
            "grade": grade,
            "score_total": total_score,
            "risk_severity": risk_severity,
            "data_ready": True,
            "components": {
                "survivability": {"score": surv_score, "reason": surv_reason},
                "em_tension": {"score": em_score, "reason": em_reason},
                "assignment": {"score": assign_score, "reason": assign_reason},
                "liquidity": {"score": liq_score, "reason": liq_reason}
            },
            "risk_penalty": risk_penalty
        }

        log(f"  {ticker}: {grade} ({total_score} pts) - {risk_severity}")
        graded_count += 1
        results.append(item)

    return results, graded_count


def main():
    log("=== Starting grading_engine_v2.py ===")

    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE) as f:
        analysis_data = json.load(f)

    if not analysis_data:
        log("No analysis data - exiting")
        return

    log(f"Loaded {len(analysis_data)} tickers")

    results, graded_count = process_tickers(analysis_data)

    results.sort(
        key=lambda x: x.get("grading", {}).get("score_total") or 0,
        reverse=True
    )

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    log(f"Graded {graded_count} tickers")
    log(f"Wrote to {OUTPUT_FILE}")

    # ===== DAILY ARCHIVE =====
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    if results:
        report_date = results[0].get("report", {}).get("date")
        if not report_date:
            report_date = datetime.now().strftime("%Y-%m-%d")

        history_file = HISTORY_DIR / f"analysis_{report_date}.json"

        with open(history_file, "w") as f:
            json.dump(results, f, indent=2)

        log(f"ARCHIVE: Saved report to {history_file}")

    print("\n=== Sample Output ===")
    for item in results[:3]:
        grading = item.get("grading", {})
        print(f"{item.get('ticker')}: {grading.get('grade')} ({grading.get('score_total')} pts)")

    log("=== Completed ===")


if __name__ == "__main__":
    main()