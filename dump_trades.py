#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta

EMAIL = "raito09726@gmail.com"
PASSWORD = "aezf bxcw xmdo zcxi"

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, PASSWORD.replace(" ", ""))
mail.select("inbox")

yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
status, messages = mail.search(None, f'(SINCE "{yesterday}")')
email_ids = messages[0].split()

trades = []

for email_id in email_ids:
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            from_addr = msg.get("From", "")
            
            is_from_guan = "guanwu87@gmail.com" in from_addr
            has_trade = any(kw in subject.upper() for kw in ["TRADE", "CONFIRMATION", "EXECUTED", "FILLED", "ORDER", "SCHWAB", "OPTION"])
            
            if is_from_guan or has_trade:
                print(f"\n{'='*70}")
                print(f"SUBJECT: {subject}")
                print(f"FROM: {from_addr}")
                print(f"{'='*70}")
                
                # Get body
                body = ""
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
                                    body += decoded
                                elif content_type == "text/html" and not body:
                                    body = decoded
                        except:
                            pass
                else:
                    try:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                    except:
                        pass
                
                # Print first 3000 chars of body
                print(body[:3000])
                print("\n" + "="*70)
                
                # Try to extract key info
                full = (subject + " " + body).upper()
                
                # Find ticker with PUT/CALL
                m = re.search(r'\b([A-Z]{1,5})\s+(?:PUT|CALL)\b', full)
                ticker = m.group(1) if m else None
                
                # Find strike price
                strike = None
                m = re.search(r'\$([\d\.]+)\s+(?:PUT|CALL)', full)
                if m:
                    strike = m.group(1)
                
                # Find expiration
                exp = None
                m = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(?:PUT|CALL)', full)
                if m:
                    exp = m.group(1)
                
                # Find premium/price
                premium = None
                m = re.search(r'PRICE.*?\$?([\d\.]+)', full)
                if m:
                    premium = m.group(1)
                
                print(f"EXTRACTED -> Ticker: {ticker}, Strike: ${strike if strike else '?'}, Exp: {exp if exp else '?'}, Premium: ${premium if premium else '?'}")
                
                if ticker:
                    trades.append({
                        "ticker": ticker,
                        "strike": strike,
                        "expiration": exp,
                        "premium": premium,
                        "strategy": "Cash-Secured Put" if "PUT" in full else ("Covered Call" if "CALL" in full else "Unknown"),
                        "action": "SOLD TO OPEN" if "SOLD" in full and "OPEN" in full else ("BOUGHT TO CLOSE" if "BOUGHT" in full else "Unknown"),
                        "notes": subject
                    })

mail.logout()

print(f"\n\n{'='*70}")
print(f"FOUND {len(trades)} TRADE(S):")
for t in trades:
    print(f"  {t}")

import json
with open('/Users/raitsai/.openclaw/workspace/trades_found.json', 'w') as f:
    json.dump(trades, f, indent=2)
