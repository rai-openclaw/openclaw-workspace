#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import json

EMAIL = "raito09726@gmail.com"
PASSWORD = "aezf bxcw xmdo zcxi"

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, PASSWORD.replace(" ", ""))
mail.select("inbox")

yesterday = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
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
            date_str = msg.get("Date", "")
            
            is_from_guan = "guanwu87@gmail.com" in from_addr
            has_trade = any(kw in subject.upper() for kw in ["TRADE", "CONFIRMATION", "EXECUTED", "FILLED", "ORDER", "SCHWAB", "OPTION"])
            
            if (is_from_guan or has_trade) and "Gmail Forwarding" not in subject:
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
                
                full_text = subject + " " + body
                full_upper = full_text.upper()
                
                print(f"Processing: {subject}")
                
                # Special handling for Robinhood option emails
                if "robinhood" in from_addr.lower() or "robinhood" in body.lower():
                    # Pattern: buy/sell X contracts of TICKER $STRIKE Put/Call MM/DD
                    m = re.search(r'(BUY|SELL)\s+(\d+)\s+CONTRACTS?\s+OF\s+(\w+)\s+\$?([\d\.]+)\s+(PUT|CALL)\s+(\d{1,2}/\d{1,2})', full_upper)
                    if m:
                        action = m.group(1)
                        qty = m.group(2)
                        ticker = m.group(3)
                        strike = m.group(4)
                        option_type = m.group(5)
                        exp = m.group(6)
                        
                        # Find price
                        price_m = re.search(r'executed at an average price of \$?([\d\.]+)', full_text, re.IGNORECASE)
                        premium = price_m.group(1) if price_m else None
                        
                        trade = {
                            "ticker": ticker,
                            "strategy": "Cash-Secured Put" if option_type == "PUT" else "Covered Call",
                            "entry": f"Strike: ${strike}, Premium: ${premium}" if premium else f"Strike: ${strike}",
                            "exit": "OPEN" if action == "SELL" else "CLOSED" if action == "BUY" else "Unknown",
                            "pnl": None,
                            "notes": f"{action} {qty} contracts | Exp: {exp}/26 | Source: Robinhood",
                            "date": date_str,
                            "broker": "Robinhood"
                        }
                        trades.append(trade)
                        print(f"  ✓ Extracted: {ticker} {option_type} ${strike}")
                        continue
                
                # Generic extraction for other emails
                m = re.search(r'\b([A-Z]{1,5})\s+(?:PUT|CALL)\b', full_upper)
                if m:
                    ticker = m.group(1)
                    strategy = "Cash-Secured Put" if "PUT" in full_upper else ("Covered Call" if "CALL" in full_upper else "Unknown")
                    
                    m2 = re.search(r'\$([\d\.]+)\s+(?:PUT|CALL)', full_upper)
                    strike = m2.group(1) if m2 else None
                    
                    m3 = re.search(r'(\d{1,2}/\d{1,2})/?\d{0,4}\s+(?:PUT|CALL)', full_upper)
                    exp = m3.group(1) if m3 else None
                    
                    m4 = re.search(r'PRICE.*?\$?([\d\.]+)', full_upper)
                    premium = m4.group(1) if m4 else None
                    
                    action = "SOLD TO OPEN" if "SOLD" in full_upper and "OPEN" in full_upper else ("BOUGHT TO CLOSE" if "BOUGHT" in full_upper else "Unknown")
                    
                    trade = {
                        "ticker": ticker,
                        "strategy": strategy,
                        "entry": f"Strike: ${strike}" if strike else None,
                        "exit": "OPEN" if "SOLD" in full_upper else ("CLOSED" if "BOUGHT" in full_upper else None),
                        "pnl": None,
                        "notes": f"{action} | Exp: {exp}" if exp else action,
                        "date": date_str,
                        "broker": "Schwab" if "schwab" in full_lower else "Unknown"
                    }
                    trades.append(trade)
                    print(f"  ✓ Extracted: {ticker} {strategy}")
                elif "schwab" in full_text.lower() and "confirmation" in full_text.lower():
                    # Schwab confirmation without details
                    trades.append({
                        "ticker": "MANUAL_REVIEW",
                        "strategy": "See Schwab.com",
                        "entry": "Login to schwab.com/reports",
                        "exit": None,
                        "pnl": None,
                        "notes": f"Schwab trade confirmation available | {subject}",
                        "date": date_str,
                        "broker": "Schwab"
                    })
                    print(f"  ! Schwab confirmation - needs manual review")

mail.logout()

# Save trades
with open('/Users/raitsai/.openclaw/workspace/trades_found.json', 'w') as f:
    json.dump(trades, f, indent=2)

print(f"\n{'='*60}")
print(f"FOUND {len(trades)} TRADE(S):")
for t in trades:
    print(f"\n  Ticker: {t['ticker']}")
    print(f"  Strategy: {t['strategy']}")
    print(f"  Entry: {t['entry']}")
    print(f"  Notes: {t['notes']}")
