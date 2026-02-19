#!/usr/bin/env python3
"""
Conversation Trigger Monitor - Detects when user wants to capture an idea
This runs as part of the main agent's message processing
"""

import re
from smart_capture import add_smart_idea, infer_category_from_text, estimate_effort

TRIGGER_PATTERNS = [
    r'turn (?:that|this|it) into an idea',
    r'make (?:that|this|it) an idea',
    r'add (?:that|this|it) to (?:the )?pipeline',
    r'can you (?:turn|make|create) (?:that|this|it)',
    r'^idea:\s*.+',
    r'^add idea:\s*.+',
    r'capture (?:that|this|it)',
    r'save (?:that|this|it) as an idea',
]

def check_for_trigger(message):
    """Check if message contains a trigger phrase"""
    message_lower = message.lower().strip()
    
    for pattern in TRIGGER_PATTERNS:
        if re.search(pattern, message_lower):
            return True
    return False

def extract_idea_from_context(conversation_history, trigger_message):
    """
    Extract the idea concept from conversation context
    conversation_history: list of recent messages
    trigger_message: the message that triggered capture
    """
    
    # If trigger message has content after trigger phrase, use that
    # e.g., "Idea: Build a trading bot" → "Build a trading bot"
    explicit_match = re.search(r'^idea:\s*(.+)', trigger_message, re.IGNORECASE)
    if explicit_match:
        return explicit_match.group(1).strip()
    
    # Otherwise, look at recent conversation for the subject
    # Get the last non-trigger message from user
    for msg in reversed(conversation_history[:-1]):  # Exclude trigger message
        if msg.get('role') == 'user' and not check_for_trigger(msg.get('content', '')):
            content = msg.get('content', '').strip()
            # Take first sentence or first 100 chars
            first_sentence = content.split('.')[0][:100]
            return first_sentence
    
    return None

def generate_analysis(conversation_history, idea_title):
    """Generate analysis based on conversation context"""
    # Look for implementation details or concerns mentioned
    analysis_points = []
    
    for msg in conversation_history:
        content = msg.get('content', '').lower()
        
        if any(word in content for word in ['however', 'but', 'concern', 'issue', 'problem']):
            analysis_points.append("Potential challenges mentioned in discussion")
        if any(word in content for word in ['api', 'integration', 'connect']):
            analysis_points.append("May require API integrations")
        if any(word in content for word in ['simple', 'easy', 'quick']):
            analysis_points.append("Appears to be straightforward implementation")
    
    if analysis_points:
        return " ".join(analysis_points)
    else:
        return "Auto-captured from conversation. Review and refine details before starting work."

def process_trigger(conversation_history, trigger_message):
    """
    Main entry point - process a trigger and create idea
    Returns: (success, idea_data, confirmation_message)
    """
    
    # Extract the idea title/concept
    idea_title = extract_idea_from_context(conversation_history, trigger_message)
    
    if not idea_title:
        return False, None, "❌ Couldn't extract idea from context. Try saying 'Idea: [your idea here]' explicitly."
    
    # Build context from recent conversation
    context_parts = []
    for msg in conversation_history[-5:]:  # Last 5 messages
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if not check_for_trigger(content):
                context_parts.append(content[:150])
    
    context = " → ".join(context_parts) if context_parts else "Captured from conversation"
    
    # Generate analysis
    my_analysis = generate_analysis(conversation_history, idea_title)
    
    # Auto-detect category and effort
    combined_text = idea_title + " " + context
    category = infer_category_from_text(combined_text)
    effort = estimate_effort(combined_text)
    
    # Create the idea
    idea = add_smart_idea(
        title=idea_title,
        context=context,
        my_analysis=my_analysis,
        category=category,
        effort=effort
    )
    
    # Format confirmation message
    confirmation = f"""✅ **Idea Created: {idea['id']}**

**{idea['title']}**
📁 Category: {idea['category']}
⏱️ Effort: {idea['effort']}
📍 Status: {idea['status'].replace('_', ' ').title()}

Added to your pipeline. View it at: http://192.168.50.170:8080"""
    
    return True, idea, confirmation

# For testing
if __name__ == '__main__':
    # Simulate conversation
    test_history = [
        {'role': 'user', 'content': 'What if we built a voice-controlled trading assistant?'},
        {'role': 'assistant', 'content': 'That could be interesting. How would it work?'},
        {'role': 'user', 'content': 'Turn that into an idea'},
    ]
    
    trigger_msg = 'Turn that into an idea'
    
    if check_for_trigger(trigger_msg):
        success, idea, msg = process_trigger(test_history, trigger_msg)
        print(msg)
    else:
        print("No trigger detected")
