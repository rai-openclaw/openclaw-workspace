#!/usr/bin/env python3
"""
Daily Summary Email Generator for Rai
Sends HTML email with portfolio snapshot, decisions, and action items
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

def load_json(filepath):
    """Load JSON file safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def format_currency(value):
    """Format number as currency"""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"

def format_number(num):
    """Format large numbers"""
    if num >= 1000000:
        return f"${num/1000000:.2f}M"
    elif num >= 1000:
        return f"${num/1000:.0f}k"
    return f"${num:.0f}"

def generate_portfolio_summary(holdings):
    """Generate portfolio summary from holdings data"""
    if not holdings or 'accounts' not in holdings:
        return "<p>Portfolio data unavailable</p>"
    
    total_cost_basis = 0
    account_summaries = []
    
    for account in holdings['accounts']:
        account_cost = 0
        
        # Sum stocks/ETFs cost basis
        for stock in account.get('stocks_etfs', []):
            if stock.get('Cost Basis'):
                account_cost += stock['Cost Basis']
        
        # Sum crypto cost basis
        for crypto in account.get('misc', []):
            if crypto.get('Cost Basis'):
                account_cost += crypto['Cost Basis']
        
        # Sum options cost basis (absolute value for sold options)
        for option in account.get('options', []):
            if option.get('Entry Premium'):
                account_cost += abs(option['Entry Premium']) * abs(option.get('Contracts', 0)) * 100
        
        total_cost_basis += account_cost
        account_summaries.append({
            'name': account['name'],
            'type': account['type'],
            'cost_basis': account_cost
        })
    
    html = f"""
    <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin: 15px 0;">
        <h3 style="color: #64ffda; margin-top: 0;">📊 Portfolio Overview</h3>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="background: #0d1117; padding: 15px; border-radius: 8px; min-width: 150px;">
                <div style="font-size: 12px; color: #8b949e;">Total Cost Basis</div>
                <div style="font-size: 24px; font-weight: bold; color: #fff;">{format_number(total_cost_basis)}</div>
            </div>
            <div style="background: #0d1117; padding: 15px; border-radius: 8px; min-width: 150px;">
                <div style="font-size: 12px; color: #8b949e;">Number of Accounts</div>
                <div style="font-size: 24px; font-weight: bold; color: #fff;">{len(holdings['accounts'])}</div>
            </div>
        </div>
        <h4 style="color: #c9d1d9; margin: 20px 0 10px;">Account Breakdown</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #21262d;">
                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 12px;">Account</th>
                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 12px;">Type</th>
                <th style="padding: 10px; text-align: right; color: #8b949e; font-size: 12px;">Cost Basis</th>
            </tr>
    """
    
    for acc in account_summaries:
        html += f"""
            <tr style="border-bottom: 1px solid #21262d;">
                <td style="padding: 10px; color: #fff;">{acc['name']}</td>
                <td style="padding: 10px; color: #8b949e;">{acc['type']}</td>
                <td style="padding: 10px; text-align: right; color: #fff;">{format_number(acc['cost_basis'])}</td>
            </tr>
        """
    
    html += "</table></div>"
    return html

def generate_ideas_summary(ideas):
    """Generate ideas pipeline summary"""
    if not ideas or 'ideas' not in ideas:
        return "<p>Ideas data unavailable</p>"
    
    status_counts = {'backlog': 0, 'discussing': 0, 'approved': 0, 'in_progress': 0, 'done': 0}
    high_priority = []
    
    for idea in ideas['ideas']:
        status = idea.get('status', 'backlog')
        status_counts[status] = status_counts.get(status, 0) + 1
        if idea.get('priority') == 'high' and status != 'done':
            high_priority.append(idea)
    
    html = f"""
    <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin: 15px 0;">
        <h3 style="color: #64ffda; margin-top: 0;">💡 Ideas Pipeline</h3>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;">
            <span style="background: #3d3d3d; color: #fff; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Backlog: {status_counts['backlog']}</span>
            <span style="background: #1e3a5f; color: #58a6ff; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Discussing: {status_counts['discussing']}</span>
            <span style="background: #2d1b4e; color: #a371f7; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Approved: {status_counts['approved']}</span>
            <span style="background: #1e4620; color: #3fb950; padding: 5px 12px; border-radius: 15px; font-size: 12px;">In Progress: {status_counts['in_progress']}</span>
            <span style="background: #1e4620; color: #3fb950; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Done: {status_counts['done']}</span>
        </div>
    """
    
    if high_priority:
        html += "<h4 style='color: #f0883e; margin: 15px 0 10px;'>🔥 High Priority Active</h4><ul style='color: #c9d1d9;'>"
        for idea in high_priority[:3]:
            html += f"<li><strong>{idea['title']}</strong> ({idea.get('status', 'backlog')})</li>"
        html += "</ul>"
    
    html += "</div>"
    return html

def generate_daily_summary():
    """Generate the complete daily summary HTML email"""
    
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    # Load data
    holdings = load_json('/Users/raitsai/.openclaw/workspace/portfolio/data/holdings.json')
    ideas = load_json('/Users/raitsai/.openclaw/workspace/portfolio/data/ideas.json')
    earnings = load_json('/Users/raitsai/.openclaw/workspace/portfolio/data/earnings.json')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Summary - {today}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0d1117; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table width="700" cellpadding="0" cellspacing="0" border="0" style="max-width: 700px;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                            <h1 style="color: #fff; margin: 0; font-size: 28px;">📬 Daily Summary</h1>
                            <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0; font-size: 16px;">{today}</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="background: #161b22; padding: 30px; border-radius: 0 0 12px 12px;">
                            
                            <!-- Key Decisions -->
                            <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #58a6ff;">
                                <h2 style="color: #58a6ff; margin-top: 0;">🎯 Today's Key Decisions</h2>
                                <ul style="color: #c9d1d9; line-height: 1.8; padding-left: 20px;">
                                    <li><strong>Mission Control Docker Migration:</strong> Confirmed Thursday session to containerize Flask app. Will delete GitHub/Netlify workarounds and run pure Docker on port 8080.</li>
                                    <li><strong>Cost Optimization:</strong> Approved migration to DeepSeek V3 (94% cost savings). Awaiting API key to begin parallel testing.</li>
                                    <li><strong>RKT Earnings Play:</strong> Grade B+ with expected move 8.5%. Action: Trim position before Feb 26 earnings.</li>
                                </ul>
                            </div>
                            
                            <!-- What We Worked On -->
                            <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #3fb950;">
                                <h2 style="color: #3fb950; margin-top: 0;">✅ What We Worked On</h2>
                                <ul style="color: #c9d1d9; line-height: 1.8; padding-left: 20px;">
                                    <li>Finalized Docker migration plan for Mission Control dashboard</li>
                                    <li>Documented lessons learned from failed GitHub Pages/Netlify attempts</li>
                                    <li>Updated MEMORY.md with comprehensive handoff for Thursday implementation</li>
                                    <li>Analyzed RKT earnings setup (IV Rank 72/100, 8.5% expected move)</li>
                                    <li>Cost analysis: Kimi K2.5 ($9.62/mo) vs DeepSeek V3 ($1.46/mo) - 94% savings</li>
                                </ul>
                            </div>
                            
                            <!-- Action Items -->
                            <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #f0883e;">
                                <h2 style="color: #f0883e; margin-top: 0;">📋 Action Items for Tomorrow</h2>
                                <table style="width: 100%; color: #c9d1d9;">
                                    <tr style="background: #21262d;">
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Priority</th>
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Task</th>
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Owner</th>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #21262d;">
                                        <td style="padding: 10px;"><span style="background: #da3633; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px;">HIGH</span></td>
                                        <td style="padding: 10px;">Install Docker Desktop on Mac Mini</td>
                                        <td style="padding: 10px;">Rai</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #21262d;">
                                        <td style="padding: 10px;"><span style="background: #da3633; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px;">HIGH</span></td>
                                        <td style="padding: 10px;">Create ~/mission-control folder</td>
                                        <td style="padding: 10px;">Rai</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #21262d;">
                                        <td style="padding: 10px;"><span style="background: #d29922; color: #000; padding: 2px 8px; border-radius: 10px; font-size: 11px;">MED</span></td>
                                        <td style="padding: 10px;">Get DeepSeek API key</td>
                                        <td style="padding: 10px;">Rai</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px;"><span style="background: #238636; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px;">LOW</span></td>
                                        <td style="padding: 10px;">Review RKT position sizing for earnings</td>
                                        <td style="padding: 10px;">Rai</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Upcoming Events -->
                            <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #a371f7;">
                                <h2 style="color: #a371f7; margin-top: 0;">📅 Upcoming Events</h2>
                                <table style="width: 100%; color: #c9d1d9;">
                                    <tr style="background: #21262d;">
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Date</th>
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Event</th>
                                        <th style="padding: 10px; text-align: left; font-size: 12px; color: #8b949e;">Details</th>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #21262d;">
                                        <td style="padding: 10px; color: #f0883e; font-weight: bold;">Thu, Feb 19</td>
                                        <td style="padding: 10px;">🐳 Docker Migration Session</td>
                                        <td style="padding: 10px; color: #8b949e;">Full day implementation</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #21262d;">
                                        <td style="padding: 10px; color: #f0883e; font-weight: bold;">Wed, Feb 26</td>
                                        <td style="padding: 10px;">📊 RKT Earnings</td>
                                        <td style="padding: 10px; color: #8b949e;">Expected move: 8.5%</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; color: #f0883e; font-weight: bold;">Fri, Feb 20</td>
                                        <td style="padding: 10px;">⚠️ Options Expiration</td>
                                        <td style="padding: 10px; color: #8b949e;">PYPL $45P, FIGR calls</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Portfolio Snapshot -->
                            <h2 style="color: #64ffda; margin: 30px 0 15px;">💼 Portfolio Snapshot</h2>
                            {generate_portfolio_summary(holdings)}
                            
                            <!-- Ideas Pipeline -->
                            {generate_ideas_summary(ideas)}
                            
                            <!-- Earnings Watch -->
                            <div style="background: #1a1f2e; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #da3633;">
                                <h3 style="color: #da3633; margin-top: 0;">⚠️ Earnings Watch</h3>
                                <p style="color: #c9d1d9;"><strong>RKT</strong> — Feb 26 | Grade: B+ | Expected Move: 8.5% | IV Rank: 72/100</p>
                                <p style="color: #8b949e; font-size: 13px;">Action: Trim position before earnings. High IV favorable for premium selling if taking new positions.</p>
                            </div>
                            
                            <!-- Footer -->
                            <div style="border-top: 1px solid #30363d; margin-top: 30px; padding-top: 20px; text-align: center; color: #8b949e; font-size: 12px;">
                                <p>Generated by OpenClaw Daily Summary System</p>
                                <p>Rai's Mission Control Dashboard</p>
                            </div>
                            
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html

def send_email():
    """Send the daily summary email via Gmail SMTP"""
    import os
    
    # Email configuration
    sender_email = os.environ.get('GMAIL_USER', 'raito09726@gmail.com')
    receiver_email = "guanwu87@gmail.com"
    subject = f"Daily Summary - {datetime.now().strftime('%A, %B %d, %Y')}"
    
    # Generate HTML content
    html_content = generate_daily_summary()
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            # Note: For Gmail, you'll need an App Password if 2FA is enabled
            # This will prompt for password or use environment variable
            password = os.environ.get('GMAIL_APP_PASSWORD', '').replace(' ', '')
            if not password:
                print("ERROR: GMAIL_APP_PASSWORD environment variable not set")
                print("Please set it with: export GMAIL_APP_PASSWORD='your_app_password'")
                return False
            
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"✅ Email sent successfully to {receiver_email}")
            return True
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def generate_text_summary():
    """Generate a plain text version of the summary for console output"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    summary = f"""
{'='*60}
📬 DAILY SUMMARY - {today}
{'='*60}

🎯 TODAY'S KEY DECISIONS
1. Mission Control Docker Migration
   → Thursday session confirmed to containerize Flask app
   → Will delete GitHub/Netlify workarounds
   → Pure Docker on port 8080

2. Cost Optimization  
   → Approved DeepSeek V3 migration (94% cost savings)
   → $9.62/mo (Kimi) → $1.46/mo (DeepSeek)
   → Awaiting API key for parallel testing

3. RKT Earnings Play
   → Grade: B+, Expected move: 8.5%
   → IV Rank: 72/100
   → Action: Trim position before Feb 26 earnings

✅ WHAT WE WORKED ON
• Finalized Docker migration plan for Mission Control dashboard
• Documented lessons from failed GitHub Pages/Netlify attempts
• Updated MEMORY.md with comprehensive handoff docs
• Analyzed RKT earnings setup (high IV environment)
• Cost analysis: Kimi vs DeepSeek pricing comparison

📋 ACTION ITEMS FOR TOMORROW
[HIGH] Install Docker Desktop on Mac Mini
[HIGH] Create ~/mission-control folder  
[MED]  Get DeepSeek API key
[LOW]  Review RKT position sizing for earnings

📅 UPCOMING EVENTS
• Thu, Feb 19 - 🐳 Docker Migration Session (Full day)
• Fri, Feb 20 - ⚠️ Options Expiration (PYPL $45P, FIGR calls)
• Wed, Feb 26 - 📊 RKT Earnings (Expected move: 8.5%)

💼 PORTFOLIO SNAPSHOT
• 5 accounts: Robinhood, SEP-IRA, Schwab CSP, Schwab #2, Roth IRA
• Total cost basis: ~$650k+ across all positions
• Major holdings: VSEQX, VTCLX, VTMSX (index funds), CRM, AMD, HOOD
• Active options: PYPL puts, FIGR calls, SOFI calls, ELF/AMD CSPs

💡 IDEAS PIPELINE
• In Progress: AI-Powered Trade Journal (high priority)
• Approved: Knowledge Management System, DeepSeek Migration
• Done: Ideas Kanban, Smart Conversation Capture, Corporate Dashboard
• Backlog: Options Backtester

⚠️ EARNINGS WATCH
• RKT (Feb 26) - Grade B+, 8.5% expected move, IV Rank 72/100
• Recommendation: Trim before earnings

{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PT')}
{'='*60}
"""
    return summary

if __name__ == "__main__":
    # Print text summary to console
    print(generate_text_summary())
    
    # Generate HTML file for preview
    html = generate_daily_summary()
    with open('/tmp/daily_summary.html', 'w') as f:
        f.write(html)
    print("\n📄 HTML preview saved to: /tmp/daily_summary.html")
    
    # Send email
    print("\n📧 Attempting to send email...")
    success = send_email()
    
    if not success:
        print("\n⚠️  Email failed - but HTML version is saved above.")
        print("   To fix: Verify GMAIL_APP_PASSWORD is correct app password from Google Account settings.")
