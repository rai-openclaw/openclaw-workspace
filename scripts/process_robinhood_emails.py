"""
Robinhood Email Processing Integration
Processes Robinhood emails and adds trades to the ledger.

Can be run manually or integrated with an email polling service.

Usage:
    python -m scripts.process_robinhood_emails --email "Your limit order to buy..."
    python -m scripts.process_robinhood_emails --file emails.txt
    python -m scripts.process_robinhood_emails --check-expiration
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import date

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.robinhood_email_ingest import parse_robinhood_email, append_trade
from lib.expiration_checker import run_expiration_check


def process_email_body(body: str) -> bool:
    """
    Process a Robinhood email body.
    
    Returns True if trade was added, False otherwise
    """
    event = parse_robinhood_email(body)
    
    if event:
        return append_trade(event)
    
    return False


def process_email_file(filepath: str) -> int:
    """Process all emails in a file (one email per line or block)."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by "Your limit order" to separate emails
    emails = content.split("Your limit order")
    
    processed = 0
    for email in emails:
        if not email.strip():
            continue
        
        # Add back the prefix we split on
        email = "Your limit order" + email
        
        if process_email_body(email):
            processed += 1
    
    return processed


def main():
    parser = argparse.ArgumentParser(description="Robinhood Email Trade Ingestion")
    parser.add_argument("--email", type=str, help="Email body to process")
    parser.add_argument("--file", type=str, help="File containing emails to process")
    parser.add_argument("--check-expiration", action="store_true", help="Run expiration check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.check_expiration:
        print("Running expiration check...")
        count = run_expiration_check()
        print(f"Processed {count} expired positions")
        return
    
    if args.email:
        if args.verbose:
            print(f"Processing email: {args.email[:100]}...")
        success = process_email_body(args.email)
        if success:
            print("✅ Trade added to ledger")
        else:
            print("⚠️ No trade found in email or duplicate")
        return
    
    if args.file:
        count = process_email_file(args.file)
        print(f"Processed {count} emails")
        return
    
    # Demo with example
    example = """Your limit order to sell 10 contracts of OKTA $59.00 Put 3/6 
    executed at an average price of $31.00 per contract on March 4, 2026 at 3:24 PM ET."""
    
    print("Example usage:")
    print(f"  python -m scripts.process_robinhood_emails --email '{example[:60]}...'")
    print(f"  python -m scripts.process_robinhood_emails --check-expiration")
    
    # Test parsing
    event = parse_robinhood_email(example)
    if event:
        print("\nExample parsed event:")
        print(json.dumps(event, indent=2))


if __name__ == "__main__":
    main()
