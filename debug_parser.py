#!/usr/bin/env python3
"""
Debug script to understand markdown structure
"""

from pathlib import Path

workspace = Path.home() / ".openclaw" / "workspace"
journal_2026_path = workspace / "trading_journal_2026.md"

with open(journal_2026_path, 'r') as f:
    content = f.read()

lines = content.split('\n')
print("Looking for 'Realized P&L Detail' section...")
for i, line in enumerate(lines):
    if "Realized P&L Detail" in line:
        print(f"Found at line {i}: {line}")
        # Print next 20 lines
        for j in range(i+1, min(i+21, len(lines))):
            print(f"  {j}: {lines[j]}")
        break

print("\n\nLooking for 'Open Positions' section...")
for i, line in enumerate(lines):
    if "Open Positions" in line:
        print(f"Found at line {i}: {line}")
        # Print next 20 lines
        for j in range(i+1, min(i+21, len(lines))):
            print(f"  {j}: {lines[j]}")
        break