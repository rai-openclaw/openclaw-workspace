#!/usr/bin/env python3
"""
Gmail IMAP Query for Robinhood Option Trade Emails
DRY RUN - Does NOT modify trades.json
"""
import imaplib
import email
import email.header
import json
import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional, Any, List
from email.message import Message

# Gmail credentials - use environment variables if available, else fall back to config
import os
GMAIL_USER = os.environ.get("GMAIL_USER", "raito09726@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "aezf bxcw xmdo zcxi")

# Import the parser from scripts directory
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
from robinhood_email_ingest import parse_robinhood_email

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def generate_trade_id(event: dict) -> str:
    """Generate deterministic ID from trade parameters."""
    event_id_input = f"{event['timestamp']}{event.get('ticker', '')}{event.get('strike', '')}{event.get('expiration', '')}{event.get('contracts', '')}{event.get('price', '')}{event.get('event_type', '')}"
    return hashlib.sha1(event_id_input.encode()).hexdigest()[:16]


def get_existing_trade_ids() -> set:
    """Get all existing trade IDs from the ledger."""
    if not LEDGER_PATH.exists():
        return set()
    
    with open(LEDGER_PATH, "r") as f:
        data = json.load(f)
        return {e.get("id") for e in data.get("events", [])}


def connect_gmail():
    """Connect to Gmail via IMAP."""
    print("🔌 Connecting to Gmail...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD.replace(" ", ""))
    print("✅ Connected!")
    return mail


def search_robinhood_emails(mail) -> List[Message]:
    """Search for Robinhood option order emails."""
    mail.select("INBOX")
    
    # Search for both subject types
    subjects = ["Option order executed", "Option order partially executed"]
    all_emails = []
    
    for subject in subjects:
        # Search for this subject
        search_query = f'SUBJECT "{subject}"'
        print(f"🔍 Searching: {subject}...")
        status, messages = mail.search(None, search_query)
        
        if status != "OK":
            print(f"⚠️ Search failed for: {subject}")
            continue
        
        email_ids = messages[0].split()
        print(f"   Found {len(email_ids)} emails")
        
        # Fetch each email
        for eid in email_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    all_emails.append(msg)
    
    return all_emails


def get_email_body(msg: Message) -> str:
    """Extract plain text body from email."""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                    break
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
        except:
            body = str(msg.get_payload())
    
    return body


def main():
    print("=" * 60)
    print("ROBINHOOD EMAIL GMAIL QUERY - DRY RUN")
    print("=" * 60)
    
    # Connect to Gmail
    mail = connect_gmail()
    
    # Search for Robinhood emails
    emails = search_robinhood_emails(mail)
    
    # Close connection
    mail.close()
    mail.logout()
    
    print(f"\n📧 Total emails scanned: {len(emails)}")
    
    # Get existing trade IDs to check for duplicates
    existing_ids = get_existing_trade_ids()
    print(f"📚 Existing trades in ledger: {len(existing_ids)}")
    
    # Parse each email
    valid_trades = []
    parse_failures = []
    
    for msg in emails:
        body = get_email_body(msg)
        
        # Parse using the Robinhood parser
        event = parse_robinhood_email(body)
        
        if event:
            valid_trades.append({
                "event": event,
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", "")
            })
        else:
            parse_failures.append({
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", "")
            })
    
    print(f"✅ Valid trades parsed: {len(valid_trades)}")
    print(f"⚠️ Parse failures: {len(parse_failures)}")
    
    # Check for duplicates vs new trades
    duplicates = []
    new_trades = []
    
    for trade in valid_trades:
        event = trade["event"]
        if event["id"] in existing_ids:
            duplicates.append(trade)
        else:
            new_trades.append(trade)
    
    print(f"\n📊 Results:")
    print(f"   - Duplicates (already in ledger): {len(duplicates)}")
    print(f"   - New trades (would be added): {len(new_trades)}")
    
    # Show first 5 parsed trades as examples
    print(f"\n📝 First 5 parsed trades (examples):")
    print("-" * 60)
    
    for i, trade in enumerate(valid_trades[:5], 1):
        event = trade["event"]
        status = "DUPLICATE" if event["id"] in existing_ids else "NEW"
        
        print(f"\n{i}. [{status}]")
        print(f"   Ticker: {event['ticker']}")
        print(f"   Type: {event['option_type']} ${event['strike']}")
        print(f"   Expiration: {event['expiration']}")
        print(f"   Contracts: {event['contracts']}")
        print(f"   Price: ${event['price']}")
        print(f"   Event Type: {event['event_type']}")
        print(f"   Timestamp: {event['timestamp']}")
        print(f"   ID: {event['id']}")
    
    print("\n" + "=" * 60)
    print("DRY RUN COMPLETE - No files were modified")
    print("=" * 60)
    
    # Return summary for programmatic use
    return {
        "total_emails_scanned": len(emails),
        "valid_trades_parsed": len(valid_trades),
        "parse_failures": len(parse_failures),
        "duplicates": len(duplicates),
        "new_trades": len(new_trades),
        "example_trades": valid_trades[:5]
    }


if __name__ == "__main__":
    main()
