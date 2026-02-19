#!/usr/bin/env python3
"""
Gemini Flash 2.5 OCR Tool - Debug Version
"""

import sys
import os
import google.generativeai as genai
from PIL import Image
import socket

# Set timeout for all socket operations
socket.setdefaulttimeout(60)

def get_api_key():
    key_path = os.path.expanduser("~/.openclaw/workspace/.gemini_api_key")
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}", file=sys.stderr)
        sys.exit(1)

def ocr_image(image_path):
    print(f"Loading image: {image_path}", file=sys.stderr)
    
    # Verify file exists
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load and verify image
    try:
        image = Image.open(image_path)
        print(f"Image loaded: {image.size[0]}x{image.size[1]} pixels", file=sys.stderr)
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Configure API
    api_key = get_api_key()
    print(f"API key loaded (length: {len(api_key)})", file=sys.stderr)
    genai.configure(api_key=api_key, transport='rest')
    
    # Create model with timeout settings
    print("Creating model...", file=sys.stderr)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Error creating model: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Simpler prompt for faster response
    prompt = "Extract all text from this brokerage statement. List all stock positions with ticker, shares, price, and value. List options positions separately. Note any cash or SGOV positions."
    
    print("Calling Gemini API...", file=sys.stderr)
    try:
        # Use generation config for faster response
        response = model.generate_content(
            [prompt, image],
            generation_config={
                'max_output_tokens': 4096,
                'temperature': 0.1,
            },
            request_options={'timeout': 45}
        )
        print("Response received", file=sys.stderr)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gemini_ocr.py <image_path>", file=sys.stderr)
        sys.exit(1)
    
    result = ocr_image(sys.argv[1])
    print(result)
