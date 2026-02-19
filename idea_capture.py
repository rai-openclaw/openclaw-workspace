#!/usr/bin/env python3
"""
Idea Capture Module - Extracts ideas from conversation text
Run this to check if a message contains an idea trigger and add to pipeline
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/raitsai/.openclaw/workspace")
IDEAS_FILE = WORKSPACE / "portfolio" / "data" / "ideas.json"

def extract_idea_from_text(text, source="conversation"):
    """
    Check if text contains an idea trigger and extract it
    
    Triggers:
    - "Idea: ..." or "Idea - ..."
    - "We should ..."
    - "Add to pipeline: ..."
    - "What if we ..."
    - "Could we ..."
    """
    text = text.strip()
    
    patterns = [
        r'(?:^|\W)Idea[:\-]\s*(.+?)(?:\n|$|\.\s)',
        r'(?:^|\W)Add to pipeline[:\-]\s*(.+?)(?:\n|$|\.\s)',
        r'(?:^|\W)(We should\s+.+?)(?:\n|$|\.\s)',
        r'(?:^|\W)(What if we\s+.+?)(?:\n|$|\.\s)',
        r'(?:^|\W)(Could we\s+.+?)(?:\n|$|\.\s)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            idea_text = match.group(1).strip()
            # Clean up the idea text
            idea_text = re.sub(r'^[\s\-]+', '', idea_text)
            idea_text = idea_text[:200]  # Limit length
            return {
                'title': idea_text,
                'category': infer_category(idea_text),
                'effort': 'Medium',  # Default, user can adjust
                'status': 'backlog',
                'source': source,
                'context': f'Captured from chat: "{text[:100]}..."' if len(text) > 100 else f'Captured from chat: "{text}"',
                'your_notes': '',
                'my_analysis': '',
                'created_date': datetime.now().isoformat(),
                'ai_generated': False,
                'priority': 'normal'
            }
    
    return None

def infer_category(idea_text):
    """Infer category from idea text"""
    text_lower = idea_text.lower()
    
    trading_keywords = ['trade', 'option', 'stock', 'earnings', 'put', 'call', 'portfolio', 'csp', 'price', 'market']
    automation_keywords = ['automate', 'script', 'cron', 'bot', 'scraper', 'parser', 'workflow']
    tech_keywords = ['app', 'dashboard', 'api', 'code', 'build', 'develop', 'software', 'system']
    personal_keywords = ['family', 'trip', 'schedule', 'kid', 'home', 'personal', 'health']
    
    if any(kw in text_lower for kw in trading_keywords):
        return 'Trading'
    elif any(kw in text_lower for kw in automation_keywords):
        return 'Automation'
    elif any(kw in text_lower for kw in tech_keywords):
        return 'Tech'
    elif any(kw in text_lower for kw in personal_keywords):
        return 'Personal'
    else:
        return 'Tech'  # Default

def load_ideas():
    """Load existing ideas"""
    if IDEAS_FILE.exists():
        try:
            with open(IDEAS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('ideas', [])
        except:
            return []
    return []

def save_idea(idea):
    """Save a new idea to the pipeline"""
    ideas = load_ideas()
    
    # Check for duplicates (similar title)
    for existing in ideas:
        if existing.get('title', '').lower() == idea['title'].lower():
            print(f"⚠️ Idea already exists: {idea['title'][:50]}...")
            return False
    
    # Generate ID
    idea['id'] = f"idea-{len(ideas) + 1:03d}"
    ideas.append(idea)
    
    # Save back
    IDEAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IDEAS_FILE, 'w') as f:
        json.dump({'ideas': ideas}, f, indent=2)
    
    return True

def main():
    """Test the idea capture"""
    test_messages = [
        "Idea: Create a position sizing calculator for CSP trades",
        "We should automate the earnings calendar scraping",
        "What if we built a voice-controlled trading assistant?",
        "Add to pipeline: Family ski trip planning for spring break",
        "Could we integrate with TradingView for better charts?",
        "This is just a regular message without an idea",
    ]
    
    print("=== Testing Idea Capture ===\n")
    for msg in test_messages:
        idea = extract_idea_from_text(msg)
        if idea:
            print(f"✅ Captured: {idea['title'][:60]}...")
            print(f"   Category: {idea['category']}, Source: {idea['source']}\n")
        else:
            print(f"❌ No idea found in: {msg[:50]}...\n")

if __name__ == '__main__':
    main()
