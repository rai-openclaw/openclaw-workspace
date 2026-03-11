#!/usr/bin/env python3
"""Reset Jarvis sessions by deleting all session files."""

import os
import shutil
from pathlib import Path

JARVIS_SESSIONS = Path("/Users/raitsai/.openclaw/agents/jarvis/sessions")

def reset_jarvis_sessions():
    """Delete all files in Jarvis sessions directory."""
    if not JARVIS_SESSIONS.exists():
        print(f"Error: {JARVIS_SESSIONS} does not exist")
        return False
    
    # Count files before deletion
    files = list(JARVIS_SESSIONS.glob("*.jsonl"))
    count = len(files)
    
    if count == 0:
        print("No session files to delete")
        return True
    
    # Delete all jsonl files (keep directory)
    for f in files:
        try:
            f.unlink()
            print(f"Deleted: {f.name}")
        except Exception as e:
            print(f"Error deleting {f.name}: {e}")
    
    print(f"Reset complete: {count} session(s) deleted")
    return True

if __name__ == "__main__":
    reset_jarvis_sessions()
