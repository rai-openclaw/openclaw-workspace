#!/bin/bash
# Gemini OCR using direct REST API

IMAGE_PATH="$1"
API_KEY=$(cat /Users/raitsai/.openclaw/workspace/.gemini_api_key)

# Convert image to base64
IMAGE_BASE64=$(base64 -i "$IMAGE_PATH")

# Create JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "contents": [
    {
      "parts": [
        {"text": "Extract all stock positions, options positions, and cash from this brokerage statement. Format as clean text with tickers, shares, prices, and values."},
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "${IMAGE_BASE64}"
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "maxOutputTokens": 4096,
    "temperature": 0.1
  }
}
EOF
)

echo "Calling Gemini API..." >&2
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['candidates'][0]['content']['parts'][0]['text'])"
