#!/usr/bin/env python3
"""
Run Registry - Python wrapper for tracking job runs
Writes to the same run_history.json file as the TypeScript version.
"""
import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

RUN_HISTORY_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "run_history.json"


def _read_history() -> dict:
    """Read run history from JSON file."""
    if not RUN_HISTORY_PATH.exists():
        return {"runs": []}
    try:
        with open(RUN_HISTORY_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"runs": []}


def _write_history(history: dict) -> None:
    """Write run history to JSON file."""
    RUN_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def create_run(job_name: str, agent: str) -> str:
    """
    Creates a new run entry with status "running"
    
    Args:
        job_name: Name of the job/agent being run
        agent: Agent identifier (e.g., "subagent", "main", "cron", "pipeline")
    
    Returns:
        The runId of the newly created run
    """
    run_id = str(uuid.uuid4())
    history = _read_history()
    
    new_run = {
        "runId": run_id,
        "jobName": job_name,
        "agent": agent,
        "startTime": datetime.now().isoformat(),
        "status": "running",
        "artifacts": []
    }
    
    # Add to beginning (most recent first)
    history["runs"].insert(0, new_run)
    _write_history(history)
    
    return run_id


def complete_run(run_id: str, status: str, summary: str) -> None:
    """
    Completes a run with the given status and summary
    
    Args:
        run_id: The runId returned from create_run
        status: "success", "failed", or "timeout"
        summary: Summary text describing the outcome
    """
    history = _read_history()
    
    run = None
    for r in history.get("runs", []):
        if r.get("runId") == run_id:
            run = r
            break
    
    if not run:
        print(f"Run not found: {run_id}")
        return
    
    run["status"] = status
    run["endTime"] = datetime.now().isoformat()
    run["summary"] = summary
    
    _write_history(history)


def get_runs(limit: int = 50) -> list:
    """
    Gets all runs from history
    
    Args:
        limit: Maximum number of runs to return (default 50)
    
    Returns:
        Array of run entries
    """
    history = _read_history()
    return history.get("runs", [])[:limit]


def get_run(run_id: str) -> Optional[dict]:
    """
    Gets a specific run by ID
    
    Args:
        run_id: The run ID to find
    
    Returns:
        The run entry or None if not found
    """
    history = _read_history()
    for r in history.get("runs", []):
        if r.get("runId") == run_id:
            return r
    return None
