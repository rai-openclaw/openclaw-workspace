#!/usr/bin/env python3
"""
Migration Script: Convert Markdown Portfolio Data to JSON

Converts various markdown tracking files into structured JSON format
for easier programmatic access and data management.

Author: AI Assistant
Date: 2026-02-16
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MarkdownToJsonMigration:
    """Handles migration of markdown portfolio data to JSON format."""
    
    def __init__(self, base_dir: str = "/Users/raitsai/.openclaw/workspace/portfolio"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.analyses_dir = self.data_dir / "analyses"
        
        # Ensure output directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "success": [],
            "skipped": [],
            "errors": []
        }
    
    def log(self, message: str, level: str = "info"):
        """Print formatted log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
    
    def parse_markdown_table(self, table_text: str) -> List[Dict[str, Any]]:
        """Parse a markdown table into a list of dictionaries."""
        lines = [line for line in table_text.strip().split('\n') if line.strip()]
        
        if len(lines) < 2:
            return []
        
        # Extract headers from first line - keep empty cells to preserve alignment
        headers = [h.strip() for h in lines[0].split('|')]
        # Remove leading/trailing empty strings from split
        while headers and not headers[0]:
            headers = headers[1:]
        while headers and not headers[-1]:
            headers = headers[:-1]
        
        num_headers = len(headers)
        
        # Skip separator line (second line with dashes)
        data_lines = lines[2:] if len(lines) > 2 else []
        
        results = []
        for line in data_lines:
            # Skip separator lines
            if re.match(r'^[\s|\-:]+$', line):
                continue
            
            # Check if it's a divider line
            if set(line.strip().replace('|', '').replace('-', '').replace(':', '').replace(' ', '')) == set():
                continue
                
            # Split cells while preserving empty cells
            cells = [c.strip() for c in line.split('|')]
            # Remove leading/trailing empty strings from split
            while cells and not cells[0]:
                cells = cells[1:]
            while cells and not cells[-1]:
                cells = cells[:-1]
            
            # Pad cells to match headers length (for rows with empty trailing cells)
            while len(cells) < num_headers:
                cells.append('')
            
            if len(cells) >= num_headers:
                row = {}
                for i, header in enumerate(headers):
                    if header:  # Only process non-empty headers
                        value = cells[i] if i < len(cells) else ""
                        # Clean up values
                        value = self._clean_value(value)
                        row[header] = value
                
                # Only add row if it has at least one meaningful value
                if any(v is not None for v in row.values()):
                    results.append(row)
        
        return results
    
    def _clean_value(self, value: str) -> Any:
        """Clean and convert a string value to appropriate type."""
        if value == "—" or value == "-" or value == "" or value == "N/A":
            return None
        
        # Try to convert to number
        # Remove $ and commas
        clean_str = value.replace('$', '').replace(',', '').replace('%', '')
        
        # Try integer
        try:
            return int(clean_str)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(clean_str)
        except ValueError:
            pass
        
        return value
    
    def extract_section_tables(self, content: str, section_name: str) -> List[Dict]:
        """Extract tables from a specific section."""
        pattern = rf"### {re.escape(section_name)}.*?\n\n(.*?)(?=\n###|\n---|$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section_content = match.group(1)
            # Find table in section
            table_match = re.search(r'\|.*\|.*\n\|[-:\|\s]+\n(?:\|.*\|.*\n?)+', section_content, re.DOTALL)
            if table_match:
                return self.parse_markdown_table(table_match.group(0))
        
        return []
    
    def extract_table_after_header(self, content: str, start_pos: int) -> List[Dict]:
        """Extract the first table that appears after a given position."""
        # Look for table pattern starting after start_pos
        subsection = content[start_pos:]
        
        # Find first table in this subsection (ends at next ### or --- or end)
        # Table: | header | header |
        #        |--------|--------|
        #        | data   | data   |
        table_pattern = r'\|[^\n]+\|\n\|[-:\|\s]+\|\n(?:\|[^\n]+\|\n?)+'
        match = re.search(table_pattern, subsection)
        
        if match:
            return self.parse_markdown_table(match.group(0))
        return []
    
    def parse_account_sections(self, content: str) -> Dict[str, Any]:
        """Parse unified portfolio tracker into account sections."""
        accounts = []
        
        # Split content by account headers - find all account sections
        account_starts = list(re.finditer(r'## Account: (.+?)\n', content))
        
        for i, match in enumerate(account_starts):
            account_name = match.group(1).strip()
            
            # Extract section range
            start_pos = match.start()
            if i + 1 < len(account_starts):
                end_pos = account_starts[i + 1].start()
                account_block = content[start_pos:end_pos]
            else:
                account_block = content[start_pos:]
            
            # Parse account metadata
            type_match = re.search(r'\*\*Type:\*\* (.+?)(?=\n)', account_block)
            broker_match = re.search(r'\*\*Broker:\*\* (.+?)(?=\n)', account_block)
            
            account_type = type_match.group(1).strip() if type_match else "Unknown"
            broker = broker_match.group(1).strip() if broker_match else "Unknown"
            
            # Extract data by finding each subsection and its table
            stocks_etfs = []
            options = []
            cash = []
            misc = []
            
            # Find each subsection
            stocks_match = re.search(r'### Stocks & ETFs\b', account_block)
            options_match = re.search(r'### Options Positions\b', account_block)
            cash_match = re.search(r'### Cash & Cash Equivalents\b', account_block)
            misc_match = re.search(r'### Misc\b', account_block)
            
            if stocks_match:
                stocks_etfs = self.extract_table_after_header(account_block, stocks_match.end())
            if options_match:
                options = self.extract_table_after_header(account_block, options_match.end())
            if cash_match:
                cash = self.extract_table_after_header(account_block, cash_match.end())
            if misc_match:
                misc = self.extract_table_after_header(account_block, misc_match.end())
            
            account_data = {
                "name": account_name,
                "type": account_type,
                "broker": broker,
                "stocks_etfs": stocks_etfs,
                "options": options,
                "cash": cash,
                "misc": misc
            }
            
            accounts.append(account_data)
        
        return {"accounts": accounts, "version": "2.0", "migrated_at": datetime.now().isoformat()}
    
    def parse_analysis_sections(self, content: str) -> Dict[str, Any]:
        """Parse portfolio tracker analysis sections into separate analyses."""
        analyses = {}
        
        # Find all detailed analysis section headers
        analysis_headers = list(re.finditer(r'## (\w+) Detailed Analysis', content))
        
        for i, match in enumerate(analysis_headers):
            ticker = match.group(1)
            start_pos = match.start()
            
            # Find the end of this section (next ## heading or end of file)
            if i + 1 < len(analysis_headers):
                end_pos = analysis_headers[i + 1].start()
            else:
                # Look for next major section or end
                next_section = re.search(r'\n## [^#]', content[start_pos + 10:])
                if next_section:
                    end_pos = start_pos + 10 + next_section.start()
                else:
                    end_pos = len(content)
            
            full_section = content[start_pos:end_pos].strip()
            
            # Parse structured data from the analysis
            analysis_data = {
                "ticker": ticker,
                "content": full_section,
                "extracted_data": self._extract_analysis_data(full_section),
                "migrated_at": datetime.now().isoformat()
            }
            analyses[ticker] = analysis_data
        
        return analyses
    
    def _extract_analysis_data(self, content: str) -> Dict[str, Any]:
        """Extract structured data from an analysis section."""
        data = {}
        
        # Extract current status fields
        status_patterns = {
            "entry": r'\*\*Entry:\*\* (.+?)(?=\n|$)',
            "current": r'\*\*Current:\*\* (.+?)(?=\n|$)',
            "position_size": r'\*\*Position Size:\*\* (.+?)(?=\n|$)',
            "action": r'\*\*Action:\*\* (.+?)(?=\n|$)',
            "thesis": r'\*\*Thesis:\*\* (.+?)(?=\n|$)',
        }
        
        for key, pattern in status_patterns.items():
            match = re.search(pattern, content)
            if match:
                data[key] = match.group(1).strip()
        
        # Extract price targets table
        targets = []
        target_pattern = r'\| (\w+) \| (.+?)%? \| (.+?) \| (.+?)%? \|'
        for match in re.finditer(target_pattern, content):
            targets.append({
                "scenario": match.group(1),
                "probability": match.group(2),
                "target": match.group(3),
                "return": match.group(4)
            })
        
        if targets:
            data["price_targets"] = targets
        
        return data
    
    def migrate_unified_portfolio(self):
        """Migrate unified_portfolio_tracker.md to data/holdings.json"""
        source = self.base_dir / "unified_portfolio_tracker.md"
        target = self.data_dir / "holdings.json"
        
        self.log(f"Migrating {source.name} → {target.name}")
        
        if not source.exists():
            self.log(f"Source file not found: {source}", "warning")
            self.results["skipped"].append(str(source))
            return
        
        try:
            content = source.read_text()
            data = self.parse_account_sections(content)
            
            with open(target, 'w') as f:
                json.dump(data, f, indent=2)
            
            account_count = len(data.get("accounts", []))
            self.log(f"✓ Migrated {account_count} accounts", "success")
            self.results["success"].append(str(target))
            
        except Exception as e:
            self.log(f"Error migrating unified portfolio: {e}", "error")
            self.results["errors"].append((str(source), str(e)))
    
    def migrate_portfolio_tracker(self):
        """Migrate portfolio_tracker.md analyses to data/analyses/*.json"""
        source = self.base_dir / "portfolio_tracker.md"
        
        self.log(f"Migrating analyses from {source.name} → data/analyses/")
        
        if not source.exists():
            self.log(f"Source file not found: {source}", "warning")
            self.results["skipped"].append(str(source))
            return
        
        try:
            content = source.read_text()
            analyses = self.parse_analysis_sections(content)
            
            count = 0
            for ticker, data in analyses.items():
                target = self.analyses_dir / f"{ticker.lower()}.json"
                with open(target, 'w') as f:
                    json.dump(data, f, indent=2)
                count += 1
            
            self.log(f"✓ Migrated {count} analyses", "success")
            self.results["success"].append(f"data/analyses/ ({count} files)")
            
        except Exception as e:
            self.log(f"Error migrating portfolio tracker: {e}", "error")
            self.results["errors"].append((str(source), str(e)))
    
    def migrate_simple_markdown(self, source_name: str, target_name: str, parser=None):
        """Generic migration for simple markdown files."""
        source = self.base_dir / source_name
        target = self.data_dir / target_name
        
        self.log(f"Migrating {source.name} → {target.name}")
        
        if not source.exists():
            self.log(f"Source file not found: {source} (creating empty template)", "warning")
            # Create empty template
            data = {
                "source": source_name,
                "data": [],
                "migrated_at": datetime.now().isoformat(),
                "note": "Source file not found - empty template created"
            }
            with open(target, 'w') as f:
                json.dump(data, f, indent=2)
            self.results["skipped"].append(f"{source_name} (empty template created)")
            return
        
        try:
            content = source.read_text()
            
            if parser:
                data = parser(content)
            else:
                # Default: extract tables
                tables = []
                for table_match in re.finditer(r'\|.*\|.*\n\|[-:\|\s]+\n(?:\|.*\|.*\n?)+', content, re.DOTALL):
                    tables.append(self.parse_markdown_table(table_match.group(0)))
                
                data = {
                    "source": source_name,
                    "tables": tables,
                    "raw_content": content,
                    "migrated_at": datetime.now().isoformat()
                }
            
            with open(target, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.log(f"✓ Migrated {source.name}", "success")
            self.results["success"].append(str(target))
            
        except Exception as e:
            self.log(f"Error migrating {source_name}: {e}", "error")
            self.results["errors"].append((source_name, str(e)))
    
    def migrate_earnings(self):
        """Migrate daily_earnings_research.md to data/earnings.json"""
        self.migrate_simple_markdown("daily_earnings_research.md", "earnings.json")
    
    def migrate_schedule(self):
        """Migrate son_schedule.md to data/schedule.json"""
        self.migrate_simple_markdown("son_schedule.md", "schedule.json")
    
    def migrate_ideas(self):
        """Migrate ideas/NOTES.md to data/ideas.json"""
        self.migrate_simple_markdown("ideas/NOTES.md", "ideas.json")
    
    def migrate_corporate(self):
        """Migrate corporate_structure.md to data/corporate.json"""
        self.migrate_simple_markdown("corporate_structure.md", "corporate.json")
    
    def print_summary(self):
        """Print migration summary."""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successful: {len(self.results['success'])}")
        for item in self.results['success']:
            print(f"   • {item}")
        
        print(f"\n⚠️  Skipped: {len(self.results['skipped'])}")
        for item in self.results['skipped']:
            print(f"   • {item}")
        
        print(f"\n❌ Errors: {len(self.results['errors'])}")
        for item, error in self.results['errors']:
            print(f"   • {item}: {error}")
        
        print("\n" + "="*60)
    
    def run(self):
        """Run all migrations."""
        print("\n" + "="*60)
        print("PORTFOLIO MARKDOWN → JSON MIGRATION")
        print("="*60 + "\n")
        
        self.migrate_unified_portfolio()
        print()
        self.migrate_portfolio_tracker()
        print()
        self.migrate_earnings()
        print()
        self.migrate_schedule()
        print()
        self.migrate_ideas()
        print()
        self.migrate_corporate()
        
        self.print_summary()


def main():
    """Main entry point."""
    try:
        migrator = MarkdownToJsonMigration()
        migrator.run()
        
        # Exit with appropriate code
        if migrator.results['errors']:
            sys.exit(1)
        else:
            print("\n🎉 Migration completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
