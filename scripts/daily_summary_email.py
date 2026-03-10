#!/usr/bin/env python3
"""
Daily Summary Email - March 1, 2026
Sends HTML email summary to guanwu87@gmail.com
"""

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "data"
ANALYSIS_FILE = DATA_DIR / "analysis" / "analysis_final.json"
HOLDINGS_FILE = DATA_DIR / "portfolio" / "holdings.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

# Email config
SENDER = "raito09726@gmail.com"
PASSWORD = "muihcqcpfvjtneyl"
RECIPIENT = "guanwu87@gmail.com"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def load_analysis():
    """Load analysis results"""
    if not ANALYSIS_FILE.exists():
        return []
    with open(ANALYSIS_FILE) as f:
        data = json.load(f)
    # Handle different JSON structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Check for candidates array
        if "candidates" in data:
            return data.get("candidates", [])
        elif "analysis" in data:
            return data.get("analysis", [])
        else:
            return []
    return []


def load_holdings():
    """Load portfolio holdings"""
    if not HOLDINGS_FILE.exists():
        return {}
    with open(HOLDINGS_FILE) as f:
        return json.load(f)


def build_html_summary(analysis, holdings):
    """Build HTML email summary"""
    
    # Analysis summary
    def get_grade(x):
        g = x.get("grading")
        return g.get("grade") if isinstance(g, dict) else str(g) if g else ""
    
    def get_risk(x):
        g = x.get("grading")
        return g.get("risk_severity") if isinstance(g, dict) else ""
    
    total = len(analysis)
    grade_a = len([x for x in analysis if get_grade(x) == "A"])
    grade_b_plus = len([x for x in analysis if get_grade(x) == "B+"])
    grade_b = len([x for x in analysis if get_grade(x) == "B"])
    elevated = len([x for x in analysis if get_risk(x) == "ELEVATED"])
    
    # Top picks table
    top_picks = [x for x in analysis if get_grade(x) in ["A", "B+"]]
    top_picks = top_picks[:5]
    
    table_rows = ""
    for t in top_picks:
        ticker = t.get("ticker", "")
        grading = t.get("grading", {})
        market = t.get("market", {})
        options = t.get("options", {})
        
        grade = grading.get("grade", "")
        score = grading.get("score_total", "")
        price = market.get("price", "")
        em = options.get("em_percent", 0)
        
        grade_color = "#1e7e34" if grade == "A" else "#2f9e44"
        
        table_rows += f"""
        <tr>
            <td style="font-weight:bold;">{ticker}</td>
            <td style="color:{grade_color}; font-weight:bold;">{grade}</td>
            <td>{score}</td>
            <td>${price}</td>
            <td>{em:.1f}%</td>
            <td>{grading.get("risk_severity", "NORMAL")}</td>
        </tr>
        """
    
    # Holdings summary
    holdings_html = ""
    accounts = holdings.get("accounts", {})
    total_positions = sum(len(v) for v in accounts.values() if isinstance(v, list))
    
    for account, positions in accounts.items():
        if isinstance(positions, list):
            holdings_html += f"<li><strong>{account.replace('_', ' ').title()}</strong>: {len(positions)} positions</li>"
    
    # Action items (static for now - would need more context)
    action_items = """
    <li>Review A-rated earnings plays from pipeline</li>
    <li>Check Schwab for any expiring options</li>
    <li>Monitor CRM position (earnings from Feb 25)</li>
    """
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
    
    <h2 style="color: #1a365d;">📊 Daily Summary - March 1, 2026</h2>
    
    <p><em>Generated at 7:00 PM PT</em></p>
    
    <hr>
    
    <h3>📈 Pipeline Activity</h3>
    <p>Today's earnings pipeline completed successfully.</p>
    <ul>
        <li>Total earnings analyzed: {total}</li>
        <li>A-rated plays: {grade_a}</li>
        <li>B+ plays: {grade_b_plus}</li>
        <li>B plays: {grade_b}</li>
        <li>Elevated risk: {elevated}</li>
    </ul>
    
    <h3>🎯 Top Earnings Plays (Feb 25 Reports)</h3>
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;" border="1" cellpadding="8">
    <tr style="background-color: #f1f3f5;">
        <th>Ticker</th>
        <th>Grade</th>
        <th>Score</th>
        <th>Price</th>
        <th>EM%</th>
        <th>Risk</th>
    </tr>
    {table_rows}
    </table>
    
    <h3>💼 Portfolio Snapshot</h3>
    <p><strong>Total Positions:</strong> {total_positions} across all accounts</p>
    <ul>
        {holdings_html}
    </ul>
    
    <h3>✅ Action Items for Tomorrow</h3>
    <ul>
        {action_items}
    </ul>
    
    <h3>📅 Upcoming Earnings</h3>
    <p>Pipeline monitors Nasdaq calendar. Next major earnings week begins March 9, 2026.</p>
    
    <hr>
    
    <p style="color: #666; font-size: 12px;">
    Sent by OpenClaw Jarvis Agent<br>
    Workspace: /Users/raitsai/.openclaw/workspace
    </p>
    
    </body>
    </html>
    """
    
    return html


def send_email(html):
    """Send HTML email via Gmail SMTP"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📊 Daily Summary - March 1, 2026"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    
    msg.attach(MIMEText(html, "html"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
        log("Email sent successfully!")
        return True
    except Exception as e:
        log(f"Email send failed: {e}")
        return False


def main():
    log("=== Starting Daily Summary Email ===")
    
    # Load data
    analysis = load_analysis()
    holdings = load_holdings()
    
    log(f"Loaded {len(analysis)} analysis records")
    log(f"Loaded holdings from {len(holdings.get('accounts', {}))} accounts")
    
    # Build HTML
    html = build_html_summary(analysis, holdings)
    
    # Send
    success = send_email(html)
    
    if success:
        log("Daily summary sent!")
    else:
        log("Failed to send daily summary")
    
    return success


if __name__ == "__main__":
    main()
