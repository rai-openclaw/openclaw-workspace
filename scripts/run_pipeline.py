#!/usr/bin/env python3
"""
run_pipeline.py - Master Earnings Pipeline Orchestrator

Deterministic execution order:

1. pull_earnings_today.py
2. research_engine.py
3. bob_research_overlay.py
4. probability_engine_v1.py
5. risk_filter_engine_v1.py
6. grading_engine_v2.py
7. send_email.py

All intermediate JSON files are overwritten.
analysis_final.json is archived inside grading_engine_v2.py.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ===============================
# PATHS
# ===============================

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
LOG_DIR = WORKSPACE / "data" / "logs"
LOG_FILE = LOG_DIR / "pipeline.log"


# ===============================
# LOGGING
# ===============================

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] PIPELINE: {msg}"
    print(line)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ===============================
# EXECUTION ORDER
# ===============================

STEPS = [
    "pull_earnings_today.py",
    "research_engine.py",
    "bob_research_overlay.py",
    "probability_engine_v1.py",
    "risk_filter_engine_v1.py",
    "grading_engine_v2.py",
    "send_email.py",
]


def run_step(script_name):
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")

    log(f"Starting {script_name}")

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=str(WORKSPACE),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Stream output live
    for line in process.stdout:
        print(line.rstrip())

    process.wait()

    if process.returncode != 0:
        log(f"FAILED {script_name} (code {process.returncode})")
        raise RuntimeError(f"{script_name} failed")

    log(f"Completed {script_name}")


# ===============================
# MAIN
# ===============================

def main():
    log("=== PIPELINE START ===")

    try:
        for step in STEPS:
            run_step(step)

        log("SUCCESS - All stages completed")
        log("=== PIPELINE END ===")

    except Exception as e:
        log(f"PIPELINE FAILED: {str(e)}")
        log("=== PIPELINE END (FAILED) ===")
        sys.exit(1)


if __name__ == "__main__":
    main()