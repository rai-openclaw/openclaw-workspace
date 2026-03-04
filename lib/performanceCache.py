"""
Performance Cache Library

Provides caching functionality for the performance-v2 API endpoint.
Cache key includes context + date range: weekly, monthly, yearly, custom-START-END
"""

import json
import os
import threading
from datetime import datetime, date
from typing import Dict, Any, Optional

# Cache storage
_performance_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()

# Cache file path
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CACHE_FILE = os.path.join(CACHE_DIR, 'performance_cache.json')


def generate_cache_key(context: str, start_date: Optional[str] = None, end_date: Optional[str] = None, month_offset: int = 0) -> str:
    """
    Generate cache key based on context and date range.
    
    Key formats:
    - weekly → weekly context
    - monthly-YYYY-MM → monthly context with offset
    - yearly → yearly context
    - custom-YYYY-MM-DD-YYYY-MM-DD → custom date range
    """
    if context == 'weekly':
        return 'weekly'
    elif context == 'monthly':
        # Calculate the month based on offset
        today = date.today()
        target_month = today.month - month_offset
        target_year = today.year
        
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        return f'monthly-{target_year}-{target_month:02d}'
    elif context == 'yearly':
        return 'yearly'
    elif context == 'custom' and start_date and end_date:
        return f'custom-{start_date}-{end_date}'
    else:
        return context


def get_performance_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Get cached performance data for the given key.
    
    Args:
        key: Cache key (weekly, monthly-YYYY-MM, yearly, custom-YYYY-MM-DD-YYYY-MM-DD)
    
    Returns:
        Cached data dict or None if not found
    """
    with _cache_lock:
        return _performance_cache.get(key)


def set_performance_cache(key: str, data: Dict[str, Any]) -> None:
    """
    Store performance data in cache.
    
    Args:
        key: Cache key
        data: Performance data to cache
    """
    with _cache_lock:
        _performance_cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }


def clear_performance_cache() -> None:
    """
    Clear all performance cache entries.
    Called when trade events are added/deleted.
    """
    with _cache_lock:
        _performance_cache.clear()


def load_performance_cache_from_file() -> None:
    """Load cache from persistent file if available."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                _performance_cache.update(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass  # Start with empty cache if file is invalid


def save_performance_cache_to_file() -> None:
    """Save cache to persistent file."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(_performance_cache, f, indent=2)
    except IOError:
        pass  # Silently fail if unable to write


def get_quote_timestamp() -> str:
    """
    Get the quote timestamp from quote cache.
    
    Returns:
        ISO format timestamp string from quote cache
    """
    quote_cache_file = os.path.join(CACHE_DIR, 'quote_cache.json')
    try:
        if os.path.exists(quote_cache_file):
            with open(quote_cache_file, 'r') as f:
                quote_data = json.load(f)
                return quote_data.get('lastQuoteUpdate', datetime.now().isoformat())
    except (json.JSONDecodeError, IOError):
        pass
    return datetime.now().isoformat()
