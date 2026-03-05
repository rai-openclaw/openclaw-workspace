#!/usr/bin/env python3
"""
Full Robinhood Email Trade Ingestion
Connects to Gmail, parses option order emails, and appends to ledger.
"""
import imaplib
import email
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
from email.message import Message

# Gmail credentials
import os
GMAIL_USER = os.environ.get("GMAIL_USER", "raito09726@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "aezf bxcw xmdo zcxi")

# Import the parser from scripts directory
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
from robinhood_email_ingest import parse_robinhood_email, append_trade

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


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
        search_query = f'SUBJECT "{subject}"'
        print(f"🔍 Searching: {subject}...")
        status, messages = mail.search(None, search_query)
        
        if status != "OK":
            print(f"⚠️ Search failed for: {subject}")
            continue
        
        email_ids = messages[0].split()
        print(f"   Found {len(email_ids)} emails")
        all_emails.extend(email_ids)
    
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


def get_existing_trade_ids() -> set:
    """Get all existing trade IDs from the ledger."""
    if not LEDGER_PATH.exists():
        return set()
    
    with open(LEDGER_PATH, "r") as f:
        data = json.load(f)
        return {e.get("id") for e in data.get("events", [])}


def main():
    print("=" * 60)
    print("ROBINHOOD EMAIL INGESTION - FULL RUN")
    print("=" * 60)
    
    # Connect to Gmail
    mail = connect_gmail()
    
    # Search for Robinhood emails
    email_ids = search_robinhood_emails(mail)
    
    print(f"\n📧 Total emails to process: {len(email_ids)}")
    
    # Get existing trade IDs to check for duplicates
    existing_ids = get_existing_trade_ids()
    print(f"📚 Existing trades in ledger: {len(existing_ids)}")
    
    # Process each email
    total_scanned = 0
    parse_failures = 0
    duplicates_skipped = 0
    trades_appended = 0
    
    timestamps = []
    
    for eid in email_ids:
        total_scanned += 1
        
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = get_email_body(msg)
                
                # Parse using the Robinhood parser
                event = parse_robinhood_email(body)
                
                if event:
                    # Check for duplicates
                    if event["id"] in existing_ids:
                        duplicates_skipped += 1
                        print(f"⚠️ Duplicate skipped: {event['ticker']} {event['contracts']} contracts @ ${event['price']}")
                    else:
                        # Append to ledger
                        if append_trade(event):
                            trades_appended += 1
                            existing_ids.add(event["id"])  # Add to local set to prevent dupes in same run
                            timestamps.append(event['timestamp'])
                else:
                    parse_failures += 1
    
    # Close connection
    mail.close()
    mail.logout()
    
    # Get final ledger stats
    with open(LEDGER_PATH, "r") as f:
        data = json.load(f)
        total_events = len(data.get("events", []))
        
        # Get Robinhood events only
        robinhood_events = [e for e in data.get("events", []) if e.get("account") == "Robinhood"]
        
        if robinhood_events:
            robinhood_timestamps = [e['timestamp'] for e in robinhood_events]
            earliest = min(robinhood_timestamps)
            latest = max(robinhood_timestamps)
        else:
            earliest = None
            latest = None
    
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"📧 Total emails scanned: {total_scanned}")
    print(f"✅ Trades appended: {trades_appended}")
    print(f"⚠️ Duplicates skipped: {duplicates_skipped}")
    print(f"❌ Parse failures: {parse_failures}")
    print(f"\n📊 Ledger Stats:")
    print(f"   - Total events in ledger: {total_events}")
    print(f"   - Total Robinhood events: {len(robinhood_events)}")
    if earliest:
        print(f"   - Earliest Robinhood trade: {earliest}")
    if latest:
        print(f"   - Latest Robinhood trade: {latest}")
    print("=" * 60)
    
    return {
        "total_emails_scanned": total_scanned,
        "trades_appended": trades_appended,
        "duplicates_skipped": duplicates_skipped,
        "parse_failures": parse_failures,
        "total_robinhood_events": len(robinhood_events),
        "earliest_robinhood_trade": earliest,
        "latest_robinhood_trade": latest
    }


if __name__ == "__main__":
    main()
