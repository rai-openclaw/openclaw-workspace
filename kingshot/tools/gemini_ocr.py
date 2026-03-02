#!/usr/bin/env python3
"""
Gemini OCR Tool for Raibot
Usage: python3 gemini_ocr.py <image_path> [prompt]

Uses Google Gemini 2.0 Flash for OCR and image analysis.
API key is hardcoded for now.
"""

import base64
import json
import sys
import urllib.request
import urllib.error

API_KEY = "AIzaSyChqdl1-jA8UOnJ3h43IP7USUcRxQ8qTn4"
MODEL = "gemini-2.0-flash"

def ocr_image(image_path, prompt="Extract all text from this image."):
    """Send image to Gemini and return extracted text."""
    
    # Read and encode image
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    # API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_data}}
            ]
        }]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"Error: {result}"
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.read().decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_ocr.py <image_path> [prompt]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Extract all text from this image."
    
    result = ocr_image(image_path, prompt)
    print(result)
