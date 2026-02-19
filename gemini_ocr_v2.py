#!/usr/bin/env python3
"""
Gemini OCR Tool - Using new google.genai library
"""

import sys
import os
from google import genai
from PIL import Image

def get_api_key():
    key_path = "/Users/raitsai/.openclaw/workspace/.gemini_api_key"
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}", file=sys.stderr)
        sys.exit(1)

def ocr_image(image_path):
    print(f"Loading image: {image_path}", file=sys.stderr)
    
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load image
    try:
        image = Image.open(image_path)
        print(f"Image loaded: {image.size[0]}x{image.size[1]} pixels", file=sys.stderr)
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Configure client
    api_key = get_api_key()
    print(f"Initializing Gemini client...", file=sys.stderr)
    client = genai.Client(api_key=api_key)
    
    prompt = """Extract all text from this brokerage statement.

List:
1. All stock positions: Ticker, Shares, Price, Value
2. All options positions (calls/puts): Ticker, Type, Strike, Expiration, Quantity
3. Cash/money market positions
4. Any SGOV or similar ETF positions

Format as clean structured text."""
    
    print("Sending to Gemini API...", file=sys.stderr)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )
        print("Response received!", file=sys.stderr)
        return response.text
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gemini_ocr_v2.py <image_path>", file=sys.stderr)
        sys.exit(1)
    
    result = ocr_image(sys.argv[1])
    print(result)
