#!/usr/bin/env python3
"""Check Gmail IMAP for trade confirmations and log to trading journal."""

import imaplib
import email
from email.header import decode_header
import re
import json
import os
from datetime import datetime
import ssl

# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Target senders
TARGET_SENDERS = [
    "donotreply@mail.schwab.com",
    "schwab.com",  # Broader match for Schwab
    "noreply@robinhood.com",
    "robinhood.com",  # Broader match
    "guanwu87@gmail.com"  # Forwarded trades
]

def decode_email_header(header_value):
    """Decode email header to string."""
    if not header_value:
        return ""
    decoded = decode_header(header_value)
    result = []
    for content, charset in decoded:
        if isinstance(content, bytes):
            result.append(content.decode(charset or 'utf-8', errors='ignore'))
        else:
            result.append(content)
    return ''.join(result)

def get_email_body(msg):
    """Extract email body as text."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except:
                    pass
            elif content_type == "text/html" and not body:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            pass
    return body

def parse_schwab_trade(body, subject):
    """Parse Schwab trade confirmation email."""
    trades = []
    
    # Look for options trade patterns
    # Pattern for "SOLD OPENING -20 NVDA 03/14/2025 $125.00 PUT"
    option_pattern = r'(?:SOLD|BOUGHT)\s+(OPENING|CLOSING)\s+([+-]?\d+)\s+([A-Z]+)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+\$?([\d.]+)\s+(PUT|CALL)'
    
    matches = re.findall(option_pattern, body, re.IGNORECASE)
    for match in matches:
        action, quantity, ticker, exp_date, strike, opt_type = match
        trades.append({
            'broker': 'Schwab',
            'action': action.upper(),
            'quantity': quantity,
            'ticker': ticker,
            'expiration': exp_date,
            'strike': strike,
            'type': opt_type.upper(),
            'strategy': 'Cash-Secured Put' if opt_type.upper() == 'PUT' and 'SOLD' in body.upper() else 'Long Call' if opt_type.upper() == 'CALL' and 'BOUGHT' in body.upper() else 'Option Trade'
        })
    
    return trades

def parse_robinhood_trade(body, subject):
    """Parse Robinhood trade confirmation email."""
    trades = []
    
    # Pattern for Robinhood option confirmations
    # "Your limit order to sell 2 contracts of WMT $116.00 Put 2/20"
    robinhood_pattern = r'Your\s+(?:limit\s+)?order\s+to\s+(sell|buy)\s+(\d+)\s+contracts?\s+of\s+([A-Z]+)\s+\$?([\d.]+)\s+(Put|Call)\s+(\d{1,2}/\d{1,2})'
    
    matches = re.findall(robinhood_pattern, body, re.IGNORECASE)
    for match in matches:
        action, quantity, ticker, strike, opt_type, exp_short = match
        # Add year to expiration
        exp_date = f"{exp_short}/2025"  # Assume current year
        trades.append({
            'broker': 'Robinhood',
            'action': action.upper(),
            'quantity': quantity,
            'ticker': ticker,
            'strike': strike,
            'expiration': exp_date,
            'type': opt_type.upper(),
            'strategy': 'Cash-Secured Put' if opt_type.upper() == 'PUT' and action.upper() == 'SOLD' else 'Option Trade'
        })
    
    return trades

def parse_trade_email(body, subject, sender):
    """Parse trade from email based on sender."""
    if 'schwab.com' in sender.lower():
        return parse_schwab_trade(body, subject)
    elif 'robinhood.com' in sender.lower():
        return parse_robinhood_trade(body, subject)
    else:
        # Try both parsers for forwarded emails
        schwab_trades = parse_schwab_trade(body, subject)
        if schwab_trades:
            return schwab_trades
        return parse_robinhood_trade(body, subject)

def load_processed_ids():
    """Load list of already processed message IDs."""
    state_file = "trading_email_state.json"
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return {'processed_ids': []}

def save_processed_ids(state):
    """Save processed message IDs."""
    state_file = "trading_email_state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f)

def log_trades_to_journal(trades):
    """Append trades to trading journal markdown file."""
    journal_file = "trading_journal.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(journal_file, 'a') as f:
        for trade in trades:
            f.write(f"\n## Trade Log - {timestamp}\n\n")
            f.write(f"- **Broker:** {trade.get('broker', 'Unknown')}\n")
            f.write(f"- **Ticker:** {trade.get('ticker', 'N/A')}\n")
            f.write(f"- **Strategy:** {trade.get('strategy', 'N/A')}\n")
            f.write(f"- **Action:** {trade.get('action', 'N/A')}\n")
            f.write(f"- **Quantity:** {trade.get('quantity', 'N/A')} contracts\n")
            f.write(f"- **Strike:** ${trade.get('strike', 'N/A')}\n")
            f.write(f"- **Expiration:** {trade.get('expiration', 'N/A')}\n")
            f.write(f"- **Type:** {trade.get('type', 'N/A')}\n")
            f.write("\n---\n")
    
    return journal_file

def main():
    # Get credentials from environment
    email_addr = os.environ.get('GMAIL_ADDRESS')
    password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not email_addr or not password:
        print("ERROR: GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables required")
        return 1
    
    # Load state
    state = load_processed_ids()
    processed_ids = set(state.get('processed_ids', []))
    
    try:
        # Connect to Gmail IMAP
        print(f"Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        all_new_trades = []
        new_message_ids = []
        
        # Search for each target sender
        for sender in TARGET_SENDERS:
            print(f"\nSearching for emails from: {sender}")
            
            # Search for emails from this sender (unseen only)
            search_criteria = f'(UNSEEN FROM "{sender}")'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK' or not messages[0]:
                print(f"  No new messages from {sender}")
                continue
            
            message_nums = messages[0].split()
            print(f"  Found {len(message_nums)} new message(s)")
            
            for num in message_nums:
                # Fetch email
                status, msg_data = mail.fetch(num, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Get message ID
                message_id = msg.get('Message-ID', '')
                if message_id in processed_ids:
                    print(f"  Skipping already processed: {message_id[:50]}...")
                    continue
                
                subject = decode_email_header(msg.get('Subject', ''))
                from_addr = decode_email_header(msg.get('From', ''))
                date = decode_email_header(msg.get('Date', ''))
                
                print(f"\n  Processing: {subject[:60]}...")
                print(f"  From: {from_addr}")
                
                # Extract body
                body = get_email_body(msg)
                
                # Parse trades
                trades = parse_trade_email(body, subject, from_addr)
                
                if trades:
                    print(f"  Found {len(trades)} trade(s)!")
                    for t in trades:
                        print(f"    - {t['ticker']} {t['type']} ${t['strike']} {t['expiration']}")
                    all_new_trades.extend(trades)
                else:
                    print(f"  No trades found in this email")
                
                new_message_ids.append(message_id)
        
        # Close connection
        mail.close()
        mail.logout()
        
        # Log results
        print(f"\n{'='*50}")
        print(f"SUMMARY")
        print(f"{'='*50}")
        print(f"Total new trades found: {len(all_new_trades)}")
        
        if all_new_trades:
            # Log to journal
            journal_file = log_trades_to_journal(all_new_trades)
            print(f"\nLogged to: {journal_file}")
            
            # Print summary for Telegram
            print("\n--- TELEGRAM SUMMARY ---")
            print(f"📊 Trade Check Complete - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            print(f"\nFound {len(all_new_trades)} new trade(s):\n")
            for t in all_new_trades:
                print(f"• {t['broker']}: {t['action']} {t['quantity']} {t['ticker']} ${t['strike']} {t['type']} exp {t['expiration']}")
            print(f"\n✅ Logged to trading_journal.md")
        else:
            print("\n--- TELEGRAM SUMMARY ---")
            print(f"📊 Trade Check Complete - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            print("\nNo new trade confirmations found.")
        
        # Update state
        state['processed_ids'].extend(new_message_ids)
        # Keep only last 1000 IDs to prevent file bloat
        state['processed_ids'] = state['processed_ids'][-1000:]
        save_processed_ids(state)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
