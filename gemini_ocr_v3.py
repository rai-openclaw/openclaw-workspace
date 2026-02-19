#!/usr/bin/env python3
"""
Gemini OCR - Extract text from images using Gemini API
Usage: python3 gemini_ocr_v3.py <image_path>
"""

import base64
import json
import sys
import os
import urllib.request
import urllib.error

def extract_from_image(image_path):
    """Extract text from image using Gemini Flash."""
    
    # Read API key
    api_key_path = os.path.expanduser("~/.openclaw/workspace/.gemini_api_key")
    try:
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()
    except:
        print(f"Error: Cannot read API key from {api_key_path}")
        sys.exit(1)
    
    # Read image
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)
    
    # Prepare request - use gemini-2.0-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": "Extract all stock and options trades from this brokerage statement. List each trade with action (buy/sell), quantity, ticker, strike price (for options), expiration, and premium. Format as a simple readable list."},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": 0.1
        }
    }
    
    # Make request with timeout
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Extract text from response
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                return text
            else:
                print(f"Error: Unexpected response format: {json.dumps(data, indent=2)}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gemini_ocr_v3.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = extract_from_image(image_path)
    
    if result:
        print(result)
    else:
        sys.exit(1)
