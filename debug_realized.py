#!/usr/bin/env python3
"""
Debug realized trades parsing
"""

from pathlib import Path

workspace = Path.home() / ".openclaw" / "workspace"
journal_2026_path = workspace / "trading_journal_2026.md"

with open(journal_2026_path, 'r') as f:
    content = f.read()

def extract_table_from_markdown(content, start_marker, end_marker=None):
    """Extract table data from markdown between markers"""
    lines = content.split('\n')
    in_table = False
    headers = []
    rows = []
    
    for i, line in enumerate(lines):
        # Check for start marker
        if start_marker in line:
            print(f"Found start marker at line {i}: {line}")
            in_table = True
            continue
        
        # Check for end marker
        if end_marker and end_marker in line and in_table:
            print(f"Found end marker at line {i}: {line}")
            break
        
        if in_table:
            # Skip separator lines
            if '---' in line and '|' in line:
                print(f"  Skipping separator line {i}: {line}")
                continue
            
            # Parse header row
            if '|' in line and not headers and any(h in line for h in ['Ticker', 'Account', 'Date']):
                headers = [h.strip() for h in line.split('|') if h.strip()]
                print(f"  Found headers at line {i}: {headers}")
                continue
            
            # Parse data rows
            if '|' in line and headers and line.strip().startswith('|'):
                print(f"  Processing data line {i}: {line}")
                # Clean the line
                line = line.strip()
                if line.startswith('|'):
                    line = line[1:]
                if line.endswith('|'):
                    line = line[:-1]
                
                values = [v.strip() for v in line.split('|')]
                print(f"    Values: {values}")
                
                # Skip total rows
                if values and values[0] and 'TOTAL' in values[0]:
                    print(f"    Skipping TOTAL row")
                    continue
                
                # Create row dictionary
                if len(values) >= len(headers) - 1:  # Allow for missing last column
                    row = {}
                    for j, header in enumerate(headers):
                        if j < len(values):
                            row[header] = values[j]
                        else:
                            row[header] = ''
                    rows.append(row)
                    print(f"    Added row: {row}")
    
    return headers, rows

print("Testing realized trades extraction...")
headers, rows = extract_table_from_markdown(content, "Realized P&L Detail", "---")
print(f"\nHeaders: {headers}")
print(f"Rows found: {len(rows)}")
for i, row in enumerate(rows):
    print(f"Row {i}: {row}")