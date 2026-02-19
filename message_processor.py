#!/usr/bin/env python3
"""
Message Processor - Integrates smart capture into main conversation flow
This module is used by the main agent to process incoming messages
"""

import sys
import os

# Add workspace to path
workspace = os.path.expanduser("~/.openclaw/workspace")
if workspace not in sys.path:
    sys.path.insert(0, workspace)

from smart_capture import detect_smart_capture_trigger, infer_category_from_text, estimate_effort, add_smart_idea
from trigger_monitor import extract_idea_from_context, generate_analysis

class MessageProcessor:
    """Processes incoming messages and detects idea capture triggers"""
    
    def __init__(self):
        self.conversation_buffer = []  # Recent messages for context
        self.max_buffer_size = 10
    
    def add_to_buffer(self, role, content):
        """Add message to conversation buffer"""
        self.conversation_buffer.append({
            'role': role,
            'content': content,
            'timestamp': None  # Could add timestamps if needed
        })
        
        # Keep buffer size limited
        if len(self.conversation_buffer) > self.max_buffer_size:
            self.conversation_buffer.pop(0)
    
    def process_message(self, user_message):
        """
        Process user message and check for idea capture triggers
        
        Returns:
            (should_capture, idea_data, confirmation_message) or (False, None, None)
        """
        # Add to buffer
        self.add_to_buffer('user', user_message)
        
        # Check for trigger
        if not detect_smart_capture_trigger(user_message):
            return False, None, None
        
        # Trigger detected! Extract idea details
        idea_title = extract_idea_from_context(self.conversation_buffer, user_message)
        
        if not idea_title:
            return False, None, "❌ Couldn't extract idea from context. Try saying 'Idea: [your idea here]' explicitly."
        
        # Build context from recent conversation
        context_parts = []
        for msg in self.conversation_buffer[-5:]:  # Last 5 messages
            if msg['role'] == 'user':
                content = msg['content']
                if not detect_smart_capture_trigger(content):
                    context_parts.append(content[:150])
        
        context = " → ".join(context_parts) if context_parts else "Captured from conversation"
        
        # Auto-categorize and estimate
        category = infer_category_from_text(idea_title + " " + context)
        effort = estimate_effort(idea_title + " " + context)
        
        # Generate analysis
        my_analysis = generate_analysis(self.conversation_buffer, idea_title)
        
        # Create the idea
        idea = add_smart_idea(
            title=idea_title,
            context=context,
            my_analysis=my_analysis,
            category=category,
            effort=effort
        )
        
        # Format confirmation
        confirmation = f"""✅ **Idea Created: {idea['id']}**

**{idea['title']}**
📁 Category: {idea['category']}
⏱️ Effort: {idea['effort']}
📍 Status: Backlog

Added to your pipeline. View it at: http://192.168.50.170:8080"""
        
        return True, idea, confirmation
    
    def get_buffer_context(self):
        """Get current conversation context for other uses"""
        return self.conversation_buffer.copy()

# Global processor instance
_processor = None

def get_processor():
    """Get or create the global message processor"""
    global _processor
    if _processor is None:
        _processor = MessageProcessor()
    return _processor

def process_user_message(message):
    """
    Main entry point - process a user message
    
    Usage in main agent:
        from message_processor import process_user_message
        
        should_capture, idea, confirmation = process_user_message(user_input)
        if should_capture:
            # Send confirmation to user
            return confirmation
    """
    processor = get_processor()
    return processor.process_message(message)

if __name__ == '__main__':
    # Test
    print("Message processor ready")
    
    # Simulate conversation
    test_msgs = [
        ("user", "What if we built a crypto price alert system?"),
        ("assistant", "That could be useful. How would it work?"),
        ("user", "Turn that into an idea"),
    ]
    
    processor = MessageProcessor()
    for role, msg in test_msgs:
        if role == 'user':
            captured, idea, confirmation = processor.process_message(msg)
            if captured:
                print(f"\nCaptured: {idea['title']}")
                print(f"Category: {idea['category']}")
                print(f"Confirmation:\n{confirmation}")
