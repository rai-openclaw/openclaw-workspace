#!/usr/bin/env python3
"""
Gemini Flash 2.5 OCR Tool
Extracts text from images using Google's Gemini API
"""

import sys
import os
import google.generativeai as genai
from PIL import Image

def get_api_key():
    """Read API key from file"""
    key_path = os.path.expanduser("~/.openclaw/workspace/.gemini_api_key")
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()
    except:
        print("Error: API key not found at ~/.openclaw/workspace/.gemini_api_key", file=sys.stderr)
        sys.exit(1)

def ocr_image(image_path):
    """Extract text from image using Gemini Flash 2.5"""
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    # Use Gemini 2.5 Flash (latest fast model)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Load image
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Prompt for structured extraction
    prompt = """Extract all text from this image. If this is a brokerage statement or portfolio screenshot, extract:
1. Account type (e.g., SEP-IRA, Roth IRA, Taxable)
2. Broker name (e.g., Schwab, Fidelity, Robinhood)
3. Stock positions with: Ticker, Shares, Current Price, Current Value
4. Cash balance
5. Total account value

Format the output as clean text with clear sections."""
    
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gemini_ocr.py <image_path>", file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = ocr_image(image_path)
    print(result)
