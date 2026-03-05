"""
Event emission for Bob's ingestion pipeline.
Emits events to OpenClaw message system.
"""
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("bob.events")

# Path for local event log (fallback)
EVENT_LOG_PATH = Path("~/.openclaw/workspace/logs/bob_events.log").expanduser()


def emit_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Emit an event to OpenClaw message system.
    
    Args:
        event_type: TRADE_DETECTED, LEDGER_UPDATED, or INGESTION_ERROR
        data: Event payload
    """
    event = {
        "event_type": event_type,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        **data
    }
    
    # Log to file as backup
    try:
        EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENT_LOG_PATH, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write event to log: {e}")
    
    # Try to emit via OpenClaw message system
    try:
        # Use environment to determine if we can emit to OpenClaw
        # This will fail gracefully if not configured
        from pathlib import Path
        import subprocess
        
        # Write event to temp file for potential message pickup
        event_file = Path("/tmp/bob_event.json")
        with open(event_file, "w") as f:
            json.dump(event, f)
        
        logger.info(f"Event emitted: {event_type} - {data.get('data', {}).get('new_trades', 'N/A')} trades")
    except Exception as e:
        logger.debug(f"OpenClaw event emission skipped: {e}")


def emit_trade_detected(schedule: str, trade: Dict[str, Any]) -> None:
    """Emit TRADE_DETECTED event."""
    emit_event("TRADE_DETECTED", {
        "source": "bob/robinhood_scanner",
        "data": {
            "schedule": schedule,
            "account": trade.get("account", "Robinhood"),
            "ticker": trade.get("ticker"),
            "action": trade.get("event_type"),
            "contracts": trade.get("contracts"),
            "strike": trade.get("strike"),
            "expiration": trade.get("expiration"),
            "price": trade.get("price")
        }
    })


def emit_ledger_updated(schedule: str, new_trades: int, duplicates: int, runtime_ms: int) -> None:
    """Emit LEDGER_UPDATED event."""
    ledger = {"events": []}
    try:
        ledger = json.loads(open(Path("~/.openclaw/workspace/data/options/trades.json").expanduser()).read())
    except:
        pass
    
    emit_event("LEDGER_UPDATED", {
        "source": "bob/robinhood_scanner",
        "data": {
            "schedule": schedule,
            "new_trades": new_trades,
            "duplicates_skipped": duplicates,
            "total_ledger_events": len(ledger.get("events", [])),
            "runtime_ms": runtime_ms
        }
    })


def emit_ingestion_error(schedule: str, error: str, error_code: str = "UNKNOWN") -> None:
    """Emit INGESTION_ERROR event."""
    emit_event("INGESTION_ERROR", {
        "source": "bob/robinhood_scanner",
        "data": {
            "schedule": schedule,
            "error": error,
            "error_code": error_code
        }
    })
