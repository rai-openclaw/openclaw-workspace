#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime, timedelta

EMAIL = "raito09726@gmail.com"
PASSWORD = "aezf bxcw xmdo zcxi"

def check_new_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD.replace(" ", ""))
    mail.select("inbox")
    
    # Check last 12 hours
    since_date = (datetime.now() - timedelta(hours=12)).strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(SINCE "{since_date}")')
    email_ids = messages[0].split()
    
    new_trades = []
    
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_addr = msg.get("From", "")
                date_str = msg.get("Date", "")
                
                # Check if from guanwu87@gmail.com or has trade keywords
                is_from_guan = "guanwu87@gmail.com" in from_addr
                has_trade_kw = any(kw in subject.upper() for kw in ["TRADE", "CONFIRMATION", "EXECUTED", "FILLED", "ORDER", "SCHWAB", "OPTION", "ROBINHOOD"])
                
                if is_from_guan or has_trade_kw:
                    new_trades.append({
                        "from": from_addr,
                        "subject": subject,
                        "date": date_str
                    })
    
    mail.logout()
    return new_trades

if __name__ == "__main__":
    trades = check_new_emails()
    print(f"Found {len(trades)} trade-related email(s) in last 12 hours:")
    for t in trades:
        print(f"  - {t['subject'][:60]}...")
    
    # Save for reference
    with open('/Users/raitsai/.openclaw/workspace/latest_check.json', 'w') as f:
        json.dump({
            "checked_at": datetime.now().isoformat(),
            "emails_found": trades
        }, f, indent=2)
