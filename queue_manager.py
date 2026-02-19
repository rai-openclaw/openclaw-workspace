#!/usr/bin/env python3
"""
Queue manager for ideas pending execution
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
QUEUE_FILE = WORKSPACE / "portfolio" / "data" / "queue.json"

def load_queue():
    """Load queued ideas"""
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'queued_ideas': [], 'last_checked': None}
    return {'queued_ideas': [], 'last_checked': None}

def save_queue(queue_data):
    """Save queue data"""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue_data, f, indent=2)

def add_to_queue(idea_id, idea_title, idea_description=""):
    """Add an idea to the execution queue"""
    queue = load_queue()
    
    # Check if already queued
    for item in queue['queued_ideas']:
        if item['id'] == idea_id:
            return False, "Already queued"
    
    queue['queued_ideas'].append({
        'id': idea_id,
        'title': idea_title,
        'description': idea_description,
        'queued_at': datetime.now().isoformat(),
        'status': 'pending_notification'
    })
    
    save_queue(queue)
    return True, "Added to queue"

def get_pending_ideas():
    """Get ideas that need notification"""
    queue = load_queue()
    pending = [i for i in queue['queued_ideas'] if i['status'] == 'pending_notification']
    return pending

def mark_notified(idea_id):
    """Mark an idea as notified"""
    queue = load_queue()
    for item in queue['queued_ideas']:
        if item['id'] == idea_id:
            item['status'] = 'notified'
            item['notified_at'] = datetime.now().isoformat()
    save_queue(queue)

def clear_queue():
    """Clear all notified items from queue"""
    queue = load_queue()
    queue['queued_ideas'] = [i for i in queue['queued_ideas'] if i['status'] != 'notified']
    queue['last_checked'] = datetime.now().isoformat()
    save_queue(queue)

def format_queue_message():
    """Format queued ideas for notification message"""
    pending = get_pending_ideas()
    
    if not pending:
        return None
    
    count = len(pending)
    message = f"🚀 **{count} Idea{'s' if count > 1 else ''} Queued for Work**\n\n"
    
    for i, idea in enumerate(pending, 1):
        message += f"{i}. **{idea['title']}**\n"
        message += f"   ID: `{idea['id']}`\n"
        if idea.get('description'):
            message += f"   {idea['description'][:100]}...\n"
        message += "\n"
    
    message += "Reply with the idea ID to start work (e.g., 'Start idea-004')\n"
    message += "Or say 'priority order' and I'll suggest which to tackle first."
    
    return message

if __name__ == '__main__':
    # Test
    print("Queue manager ready")
    print(f"Queue file: {QUEUE_FILE}")
    print(f"Pending ideas: {len(get_pending_ideas())}")
