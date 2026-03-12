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
import os
from pathlib import Path
from datetime import datetime
import time

# Add lib to path for run registry
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "lib"))
from runRegistry import create_run, complete_run


# ===============================
# PATHS
# ===============================

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
LOG_DIR = WORKSPACE / "data" / "logs"
LOG_FILE = LOG_DIR / "pipeline.log"
LOCK_FILE = Path("/tmp/pipeline.lock")
LOCK_STALE_SECONDS = 7200  # 2 hours


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
# LOCK MANAGEMENT
# ===============================

def acquire_lock():
    """Acquire pipeline lock, returns True if acquired, False if already running."""
    if LOCK_FILE.exists():
        lock_age = time.time() - LOCK_FILE.stat().st_mtime
        if lock_age > LOCK_STALE_SECONDS:
            log(f"Removing stale lock (age: {lock_age/3600:.1f} hours)")
            LOCK_FILE.unlink()
        else:
            log("Pipeline already running - exiting")
            return False
    LOCK_FILE.write_text(str(os.getpid()))
    log(f"Pipeline lock acquired (PID: {os.getpid()})")
    return True


def release_lock():
    """Always remove the lock file."""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        log("Pipeline lock released")


# ===============================
# OUTPUT VALIDATION
# ===============================

STAGE_OUTPUTS = {
    "pull_earnings_today.py": "data/cache/todays_candidates.json",
    "research_engine.py": "data/analysis/analysis_raw.json",
    "probability_engine_v1.py": "data/analysis/analysis_with_probs.json",
    "analysis_batch.py": "data/analysis/analysis_raw.json",  # Enriches same file
    "send_email.py": None,
}


def validate_output(script_name):
    """Validate that the stage produced valid output."""
    output_path = STAGE_OUTPUTS.get(script_name)
    if output_path is None:
        return
    full_path = WORKSPACE / output_path
    if not full_path.exists():
        raise FileNotFoundError(f"Validation FAILED for {script_name}: Output file not found: {output_path}")
    if full_path.stat().st_size == 0:
        raise ValueError(f"Validation FAILED for {script_name}: Output file is empty: {output_path}")
    try:
        import json
        with open(full_path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Validation FAILED for {script_name}: Invalid JSON in {output_path}: {e}")
    log(f"Validated {output_path} - OK")


# ===============================
# EXECUTION ORDER
# ===============================

STEPS = [
    "pull_earnings_today.py",
    "research_engine.py",  # Filters candidates by price/sector
    "probability_engine_v1.py",  # Generates probability data for historical_volatility
    "analysis_batch.py",    # Calls analyze_batch() directly (not subprocess)
    "send_email.py",
]


def run_step(script_name):
    script_path = SCRIPTS_DIR / script_name
    print(f"\n--- Running {script_name} ---\n")
    
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=str(WORKSPACE),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=os.environ
    )
    
    try:
        # Stream output live
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
        
        # Wait for completion with timeout
        process.wait(timeout=1800)  # 30 minute limit per step
    except subprocess.TimeoutExpired:
        process.kill()
        raise RuntimeError(f"{script_name} exceeded 30 minute timeout")
    
    if process.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {process.returncode}")


# ===============================
# MAIN
# ===============================

def main():
    # Create run entry for tracking
    run_id = create_run("earnings-pipeline", "alex")
    
    if not acquire_lock():
        complete_run(run_id, "failed", "Pipeline already running - could not acquire lock")
        sys.exit(1)
    
    try:
        log("=== PIPELINE START ===")

        try:
            for step in STEPS:
                run_step(step)
                validate_output(step)

            log("SUCCESS - All stages completed")
            log("=== PIPELINE END ===")
            complete_run(run_id, "success", "All pipeline stages completed successfully")

        except Exception as e:
            log(f"PIPELINE FAILED: {str(e)}")
            log("=== PIPELINE END (FAILED) ===")
            complete_run(run_id, "failed", f"Pipeline failed: {str(e)}")
            raise

    finally:
        release_lock()


if __name__ == "__main__":
    main()