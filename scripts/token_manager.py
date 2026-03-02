#!/usr/bin/env python3
"""
Schwab API Token Manager

Handles OAuth token refresh for Schwab API access.
"""

import os
import base64
import logging
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from workspace root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging to pipeline.log
LOG_FILE = Path.home() / ".openclaw" / "workspace" / "logs" / "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Schwab API configuration
SCHWAB_TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"

# Token cache
_cached_token = None
_token_expiry = 0


def get_access_token() -> str:
    """
    Refresh the access token using the refresh token grant.
    Uses caching to avoid unnecessary refreshes.
    
    Returns:
        access_token string
        
    Raises:
        Exception: If the token refresh fails
    """
    global _cached_token, _token_expiry
    
    current_time = int(time.time())
    
    # Check if we have a valid cached token (with 60 second buffer)
    if _cached_token is not None and current_time < _token_expiry - 60:
        logger.info("TOKEN: Using cached token")
        return _cached_token
    
    # Load environment variables
    client_id = os.environ.get("SCHWAB_CLIENT_ID")
    client_secret = os.environ.get("SCHWAB_CLIENT_SECRET")
    refresh_token = os.environ.get("SCHWAB_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        raise Exception("Missing required environment variables: SCHWAB_CLIENT_ID, SCHWAB_CLIENT_SECRET, SCHWAB_REFRESH_TOKEN")
    
    logger.info("TOKEN: Refreshing token")
    
    # Create basic auth header (client_id:client_secret base64 encoded)
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(SCHWAB_TOKEN_URL, headers=headers, data=data)
        
        if response.status_code != 200:
            logger.error(f"TOKEN: Failed - Status {response.status_code}: {response.text}")
            raise Exception(f"Token refresh failed with status {response.status_code}: {response.text}")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            logger.error("TOKEN: Failed - No access_token in response")
            raise Exception("No access_token returned from Schwab API")
        
        # Cache the token with expiry time
        expires_in = token_data.get("expires_in", 1800)  # Default 30 minutes
        _cached_token = access_token
        _token_expiry = int(time.time()) + expires_in
        
        logger.info("TOKEN: Success - token cached")
        return access_token
        
    except requests.RequestException as e:
        logger.error(f"TOKEN: Failed - Request error: {str(e)}")
        raise Exception(f"Request error: {str(e)}")


if __name__ == "__main__":
    # Test the token manager
    try:
        token = get_access_token()
        print(f"Success! Token starts with: {token[:20]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
