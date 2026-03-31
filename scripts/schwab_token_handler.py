#!/usr/bin/env python3
"""
Schwab Token Handler

Listens for messages matching: schwab_token: https://...
Extracts callback URL, exchanges for tokens, updates files.
"""

import re
import sys
import json
import base64
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs

WORKSPACE = Path.home() / ".openclaw" / "workspace"
TOKEN_FILE = WORKSPACE / "data" / "auth" / "schwab_tokens.json"
ENV_FILE = WORKSPACE / ".env"

SCHWAB_TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
CLIENT_ID = "49t48YF2P01BqLBBTyj6Qpb5GvoG6A8nskVs8bUPGvz8HBqH"
CLIENT_SECRET = "e5EXyqI6zX9s6AMh7OTVNLqwBqKKz0v9TNOAVTYxqmGZgR8kQKvT92DsTyxmTNdS"
REDIRECT_URI = "https://127.0.0.1:8182/callback"


def extract_code_from_url(callback_url: str) -> str:
    """Extract authorization code from callback URL."""
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]
    if not code:
        raise ValueError("No 'code' parameter found in callback URL")
    return code


def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access/refresh tokens."""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(SCHWAB_TOKEN_URL, headers=headers, data=data, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")
    
    return response.json()


def update_token_files(new_refresh_token: str):
    """Update both schwab_tokens.json and .env with new refresh token."""
    # Update schwab_tokens.json
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            token_data = json.load(f)
    else:
        token_data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    
    token_data["refresh_token"] = new_refresh_token
    token_data["updated_at"] = "2026-03-31"
    
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    
    # Update .env
    with open(ENV_FILE) as f:
        env_content = f.read()
    
    # Replace existing SCHWAB_REFRESH_TOKEN
    if "SCHWAB_REFRESH_TOKEN=" in env_content:
        import re
        pattern = r"SCHWAB_REFRESH_TOKEN=[^\n]+"
        replacement = f"SCHWAB_REFRESH_TOKEN={new_refresh_token}"
        env_content = re.sub(pattern, replacement, env_content)
    else:
        env_content += f"\nSCHWAB_REFRESH_TOKEN={new_refresh_token}\n"
    
    with open(ENV_FILE, "w") as f:
        f.write(env_content)


def handle_schwab_token_message(message: str) -> str:
    """Process a schwab_token message and return confirmation."""
    # Extract URL from message
    match = re.search(r"schwab_token:\s*(https://[^\s]+)", message)
    if not match:
        return "❌ Could not find callback URL. Expected: schwab_token: https://..."
    
    callback_url = match.group(1).strip()
    print(f"Extracted callback URL: {callback_url[:50]}...")
    
    # Extract code
    code = extract_code_from_url(callback_url)
    print(f"Extracted code: {code[:30]}...")
    
    # Exchange for tokens
    token_data = exchange_code_for_token(code)
    new_refresh_token = token_data.get("refresh_token")
    
    if not new_refresh_token:
        return "❌ Token exchange succeeded but no refresh_token in response"
    
    # Update files
    update_token_files(new_refresh_token)
    
    return f"✅ Schwab token updated successfully!\n- Saved to schwab_tokens.json\n- Updated .env\n- Token length: {len(new_refresh_token)} chars"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 schwab_token_handler.py 'schwab_token: https://...'")
        sys.exit(1)
    
    message = sys.argv[1]
    result = handle_schwab_token_message(message)
    print(result)
