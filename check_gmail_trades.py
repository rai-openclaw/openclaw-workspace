#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta

# Gmail credentials
EMAIL = "raito09726@gmail.com"
PASSWORD = "aezf bxcw xmdo zcxi"

def connect_gmail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD.replace(" ", ""))
    return mail

def get_recent_emails(mail, hours=24):
    mail.select("inbox")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(SINCE "{yesterday}")')
    return messages[0].split()

def parse_email_full(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            from_addr = msg.get("From", "")
            date_str = msg.get("Date", "")
            
            body_plain = ""
            body_html = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    if "attachment" in content_disposition:
                        continue
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            decoded = payload.decode("utf-8", errors="ignore")
                            if content_type == "text/plain":
                                body_plain += decoded
                            elif content_type == "text/html":
                                body_html += decoded
                    except:
                        pass
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body_plain = payload.decode("utf-8", errors="ignore")
                except:
                    pass
            
            return {
                "subject": subject,
                "from": from_addr,
                "date": date_str,
                "body": body_plain if body_plain else body_html,
            }
    return None

def extract_trade_info_detailed(email_data):
    """Extract detailed trade information from email"""
    subject = email_data["subject"]
    body = email_data["body"]
    full_text = (subject + " " + body).upper()
    
    trade = {
        "ticker": None,
        "strategy": None,
        "entry": None,
        "exit": None,
        "pnl": None,
        "notes": subject,
        "date": email_data["date"],
        "raw_body": body[:2000]
    }
    
    # Extract ticker - look for common patterns
    # First try to find ticker before PUT/CALL
    match = re.search(r'\b([A-Z]{1,5})\s+(?:PUT|CALL)\b', full_text)
    if match:
        ticker = match.group(1)
        if ticker not in ['THE', 'AND', 'FOR', 'PUT', 'CALL', 'SOLD', 'BOUGHT', 'OPEN', 'CLOSE']:
            trade["ticker"] = ticker
    
    # If still no ticker, try other patterns
    if not trade["ticker"]:
        schwab_patterns = [
            r'DESCRIPTION\s*\n?\s*(\w{2,5})\s+\d',
            r'SYMBOL\s*[:/]\s*(\w{1,5})',
            r'\b(RKT|NVDA|TSLA|AAPL|MSFT|GOOGL|AMZN|AMD|INTC|COIN|MSTR|HOOD|RGTI|QUBT|AFRM|KO|DIS|PLTR)\b',
        ]
        for pattern in schwab_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                ticker = match.group(1).upper()
                if len(ticker) <= 5 and ticker not in ['THE', 'AND', 'FOR', 'PUT', 'CALL', 'SOLD', 'BOUGHT', 'OPEN', 'CLOSE']:
                    trade["ticker"] = ticker
                    break
    
    # Look for option indicators
    if 'PUT' in full_text:
        trade["strategy"] = "Cash-Secured Put"
    elif 'CALL' in full_text:
        trade["strategy"] = "Covered Call"
    
    # Extract strike price
    strike_patterns = [
        r'\$([\d,]+)\s+(?:PUT|CALL)',
        r'STRIKE\s*[:\s]*\$?([\d,]+)',
        r'(?:PUT|CALL)\s+\$?([\d,]+)',
    ]
    
    for pattern in strike_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            trade["entry"] = f"Strike: ${match.group(1)}"
            break
    
    # Extract premium/price
    price_patterns = [
        r'PRICE\s*[:\s]*\$?([\d,]+\.\d{2})',
        r'@\s*\$?([\d,]+\.\d{2})',
        r'EXECUTION\s*PRICE\s*[:\s]*\$?([\d,]+\.\d{2})',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            price = match.group(1)
            if trade["entry"]:
                trade["entry"] += f", Premium: ${price}"
            else:
                trade["entry"] = f"Premium: ${price}"
            break
    
    # Look for "SOLD TO OPEN" or "BOUGHT TO CLOSE"
    if 'SOLD TO OPEN' in full_text or 'YOU SOLD' in full_text:
        trade["notes"] += " | SOLD TO OPEN"
        trade["exit"] = "OPEN"
    elif 'BOUGHT TO CLOSE' in full_text or 'YOU BOUGHT' in full_text:
        trade["notes"] += " | BOUGHT TO CLOSE"
        trade["exit"] = "CLOSED"
    
    # Extract quantity
    qty_match = re.search(r'QUANTITY\s*[:\s]*(\d+)', full_text, re.IGNORECASE)
    if qty_match:
        trade["notes"] += f" | Qty: {qty_match.group(1)}"
    
    # Extract expiration date
    exp_patterns = [
        r'EXP\w*[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})',
        r'EXPIR\w*[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})',
        r'\b(\d{1,2}/\d{1,2}/\d{2,4})\s+(?:PUT|CALL)',
    ]
    for pattern in exp_patterns:
        exp_match = re.search(pattern, full_text, re.IGNORECASE)
        if exp_match:
            trade["notes"] += f" | Exp: {exp_match.group(1)}"
            break
    
    return trade

def main():
    print("Connecting to Gmail...")
    mail = connect_gmail()
    
    print("Getting recent emails (last 24 hours)...")
    email_ids = get_recent_emails(mail)
    print(f"Found {len(email_ids)} recent emails\n")
    
    trades = []
    
    for email_id in email_ids:
        email_data = parse_email_full(mail, email_id)
        
        if email_data:
            is_from_guan = "guanwu87@gmail.com" in email_data["from"]
            has_trade_keyword = any(kw in email_data["subject"].upper() for kw in ["TRADE", "CONFIRMATION", "EXECUTED", "FILLED", "ORDER", "SCHWAB", "OPTION"])
            
            if is_from_guan or has_trade_keyword:
                print(f"{'='*60}")
                print(f"Processing: {email_data['subject']}")
                
                trade = extract_trade_info_detailed(email_data)
                if trade and trade['ticker']:
                    trades.append(trade)
                    print(f"✓ Trade extracted:")
                    print(f"  Ticker: {trade['ticker']}")
                    print(f"  Strategy: {trade['strategy']}")
                    print(f"  Entry: {trade['entry']}")
                    print(f"  Exit: {trade['exit']}")
                    print(f"  Notes: {trade['notes']}")
    
    mail.logout()
    return trades

if __name__ == "__main__":
    trades = main()
    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {len(trades)} trade(s)")
    
    import json
    with open('/Users/raitsai/.openclaw/workspace/trades_found.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"Saved to trades_found.json")
