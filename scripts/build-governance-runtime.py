#!/usr/bin/env python3
"""Build governance runtime by concatenating all governance files."""

import os
from pathlib import Path

WORKSPACE = Path("/Users/raitsai/.openclaw/workspace")
GOVERNANCE_DIR = WORKSPACE / "governance"
OUTPUT_FILE = GOVERNANCE_DIR / "RUNTIME.md"

# Order matters - this is the governance hierarchy
GOVERNANCE_FILES = [
    "CONSTITUTION.md",
    "ROLES.md",
    "VALIDATION.md",
    "AIP.md",
    "AEF.md",
    "PROTECTED_SURFACES.md",
    "SCP.md",
    "RPP.md",
]

def build_runtime():
    """Concatenate governance files into RUNTIME.md."""
    output_lines = [
        "# OpenClaw Governance Runtime",
        "",
        "This file is auto-generated. Do not edit manually.",
        "Source files in: /governance/",
        "",
    ]
    
    for filename in GOVERNANCE_FILES:
        filepath = GOVERNANCE_DIR / filename
        
        if not filepath.exists():
            print(f"Warning: {filename} not found, skipping")
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Add section header
        section_name = filename.replace('.md', '')
        output_lines.extend([
            f"## {section_name}",
            "",
            content,
            "",
        ])
    
    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Created: {OUTPUT_FILE}")
    print(f"Files combined: {len(GOVERNANCE_FILES)}")

if __name__ == "__main__":
    build_runtime()
