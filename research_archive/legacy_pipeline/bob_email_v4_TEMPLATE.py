#!/usr/bin/env python3
"""Generate HTML email with v4.0 downside EM format - CORRECTED"""
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === ADAPTER LAYER ===
# Converts current research schema → email template schema
def adapt_research_schema(analysis_file):
    """Adapter: Convert current Bob research schema to email template schema.
    
    Current (dict): {"stocks": {"CODI": {"grade": {"total_grade": 60}}}}
    Expected (dict): {"stocks": {"CODI": {"grade": "B", "total_score": 60}}}
    """
    with open(analysis_file) as f:
        data = json.load(f)
    
    # Check if already in expected format
    stocks = data.get('stocks', {})
    if stocks:
        sample = list(stocks.values())[0] if stocks else {}
        if 'grade' in sample and isinstance(sample.get('grade'), str):
            return data  # Already in expected format
    
    # Convert current format → expected format
    converted_stocks = {}
    for ticker, stock in stocks.items():
        grade_obj = stock.get('grade', {})
        total_score = grade_obj.get('total_grade', 0) if isinstance(grade_obj, dict) else 0
        
        # Convert numeric score → letter grade
        if total_score >= 80:
            letter_grade = 'A+'
        elif total_score >= 70:
            letter_grade = 'A'
        elif total_score >= 65:
            letter_grade = 'A-'
        elif total_score >= 60:
            letter_grade = 'B+'
        elif total_score >= 55:
            letter_grade = 'B'
        elif total_score >= 50:
            letter_grade = 'B-'
        elif total_score >= 45:
            letter_grade = 'C+'
        elif total_score >= 40:
            letter_grade = 'C'
        else:
            letter_grade = 'D'
        
        # Get expected move
        exp_move = stock.get('options_implied_EM_pct') or stock.get('historical_EM_pct') or 0
        
        # Build converted entry matching email template expectations
        converted_stocks[ticker] = {
            'grade': letter_grade,
            'total_score': total_score,
            'expected_move': exp_move,
            'recommendation': 'Trade' if total_score >= 50 else 'Skip',
            'key_insight': f"IV: {stock.get('iv', 0):.2f}, Price: ${stock.get('price', 0):.2f}",
            'bottom_line': f"At {stock.get('pct_from_3y_low', 0):.0f}% from 3Y low",
            'grade_components': {},
            'trade_setup': {},
            'risk_factors': []
        }
    
    return {
        'date': data.get('date', ''),
        'stocks': converted_stocks
    }

def generate_v4_email(analysis_file, date_str):
    # Use adapter to convert current schema → email template schema
    data = adapt_research_schema(analysis_file)
    
    # Sort tickers by score descending (A at top)
    stocks = data.get('stocks', {})
    sorted_tickers = sorted(stocks.items(), key=lambda x: x[1].get('total_score', 0), reverse=True)
    
    # Build summary table with CORRECT columns
    table_rows = ""
    for ticker, stock in sorted_tickers:
        exp_move = stock.get('expected_move', 0)
        grade = stock.get('grade', '')
        score = stock.get('total_score', 0)
        rec = stock.get('recommendation', '')
        
        # Get EM percentages from grade_components (may be empty for adapted data)
        gc = stock.get('grade_components', {})
        downside = gc.get('downside_em_respect', {})
        em_1x = downside.get('respect_1x_down', {}).get('rate', 0)
        em_1_5x = downside.get('respect_1_5x_down', {}).get('rate', 0)
        em_2x = downside.get('respect_2x_down', {}).get('rate', 0)
        
        # Use key_insight + bottom_line for rich Key Analysis
        key_insight = stock.get('key_insight', '')
        bottom_line = stock.get('bottom_line', '')
        
        # Combine for Key Analysis column
        key_analysis = f"{key_insight} {bottom_line}"[:300]
        
        # Color by grade
        if grade.startswith('A'):
            grade_color = '#2e7d32'
        elif grade.startswith('B'):
            grade_color = '#689f38'
        elif grade.startswith('C'):
            grade_color = '#f57c00'
        else:
            grade_color = '#c62828'
        
        table_rows += f"""
        <tr>
            <td><strong>{ticker}</strong></td>
            <td>±{exp_move}%</td>
            <td>{em_1x}%</td>
            <td>{em_1_5x}%</td>
            <td>{em_2x}%</td>
            <td style="background:{grade_color};color:white;padding:4px 8px;border-radius:4px;font-weight:bold;">{grade}</td>
            <td>{rec}</td>
            <td style="font-size:10px;color:#333;width:40%;line-height:1.3;">{key_analysis}</td>
        </tr>
        """
    
    # Build detailed sections (also sorted)
    detailed_sections = ""
    for ticker, stock in sorted_tickers:
        exp_move = stock.get('expected_move', 0)
        grade = stock.get('grade', '')
        score = stock.get('total_score', 0)
        rec = stock.get('recommendation', '')
        
        gc = stock.get('grade_components', {})
        downside = gc.get('downside_em_respect', {})
        em_1x = downside.get('respect_1x_down', {}).get('rate', 0)
        em_1_5x = downside.get('respect_1_5x_down', {}).get('rate', 0)
        em_2x = downside.get('respect_2x_down', {}).get('rate', 0)
        
        earnings_pred = gc.get('earnings_predictability', {})
        assign_desir = gc.get('assignment_desirability', {})
        prem_yield = gc.get('premium_yield', {})
        binary_risk = gc.get('binary_risk', {})
        
        key_insight = stock.get('key_insight', '')
        trade = stock.get('trade_setup', {})
        risks = stock.get('risk_factors', [])
        bottom_line = stock.get('bottom_line', '')
        
        risk_list = ""
        for r in risks[:3]:
            risk_list += f"<li>{r.get('risk', '')}: {r.get('impact', '')} ({r.get('probability', '')})</li>"
        
        detailed_sections += f"""
        <div style="margin:30px 0;padding:20px;background:#f8f8f8;border-left:4px solid #1e3a5f;">
        <h3 style="margin-top:0;">{ticker} - {grade} ({score}/100)</h3>
        <p><strong>Expected Move:</strong> ±{exp_move}% | ↓1x: {em_1x}% | ↓1.5x: {em_1_5x}% | ↓2x: {em_2x}%</p>
        
        <h4>WHY THIS GRADE - Component Analysis:</h4>
        <ul>
        <li><strong>Earnings Predictability ({earnings_pred.get('score',0)}/30):</strong> {earnings_pred.get('reason','')}</li>
        <li><strong>Downside EM Respect ({downside.get('score',0)}/25):</strong> {downside.get('reason','')}</li>
        <li><strong>Assignment Desirability ({assign_desir.get('score',0)}/20):</strong> {assign_desir.get('reason','')}</li>
        <li><strong>Premium Yield ({prem_yield.get('score',0)}/20):</strong> {prem_yield.get('reason','')}</li>
        <li><strong>Binary Risk:</strong> {binary_risk.get('reason','')}</li>
        </ul>
        
        <h4>KEY INSIGHT:</h4>
        <p>{key_insight}</p>
        
        <h4>SPECIFIC TRADE SETUP:</h4>
        <ul>
        <li><strong>Strategy:</strong> {trade.get('strategy','')}</li>
        <li><strong>Strike(s):</strong> {trade.get('strikes','')}</li>
        <li><strong>Premium:</strong> {trade.get('premium_target','')}</li>
        <li><strong>Expiration:</strong> {trade.get('expiration','')}</li>
        <li><strong>Annualized Return:</strong> {trade.get('annualized_return','')}</li>
        </ul>
        
        <h4>RISK FACTORS:</h4>
        <ul>{risk_list}</ul>
        
        <p><strong>BOTTOM LINE:</strong> {bottom_line}</p>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th {{ background: #1e3a5f; color: white; padding: 10px; text-align: left; }}
td {{ padding: 8px; border-bottom: 1px solid #ddd; vertical-align: top; }}
</style>
</head>
<body>
<h2>DAILY STOCKS RECOMMENDATION REPORT - {date_str}</h2>

<h3>EXECUTIVE SUMMARY</h3>
<table>
<tr>
<th>Ticker</th><th>Exp Move</th><th>↓1x EM</th><th>↓1.5x EM</th><th>↓2x EM</th><th>Grade</th><th>Rec</th><th style="width:40%;">Key Analysis</th>
</tr>
{table_rows}
</table>

<h3>DETAILED ANALYSIS</h3>
{detailed_sections}
</body>
</html>"""
    
    return html

def send_email(html_content, subject, to_email):
    sender = os.environ.get('GMAIL_USER', 'raito09726@gmail.com')
    password = os.environ.get('GMAIL_APP_PASSWORD')
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    
    part = MIMEText(html_content, 'html')
    msg.attach(part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    print(f"✅ Email sent to {to_email}")

if __name__ == '__main__':
    import sys
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    analysis_file = os.path.expanduser(f'~/.openclaw/workspace/data/analysis/analysis_{date_str}.json')
    
    print(f"Generating email from {analysis_file}...")
    html = generate_v4_email(analysis_file, date_str)
    subject = f"Daily Stocks Recommendation Report - {date_str}"
    send_email(html, subject, 'guanwu87@gmail.com')
