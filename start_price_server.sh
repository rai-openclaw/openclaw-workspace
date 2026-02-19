#!/bin/bash
# Start the FastAPI price server

cd ~/.openclaw/workspace

# Check if FINNHUB_API_KEY is set
if [ -z "$FINNHUB_API_KEY" ]; then
    echo "⚠️  Warning: FINNHUB_API_KEY not set"
    echo "Set it with: export FINNHUB_API_KEY='your_key_here'"
    echo "Continuing anyway (Yahoo Finance will be used as fallback)..."
fi

# Install dependencies if needed
pip3 install fastapi uvicorn requests -q 2>/dev/null

echo "🚀 Starting Price API Server..."
echo "URL: http://localhost:8080"
echo ""
echo "Test endpoints:"
echo "  curl http://localhost:8080/health"
echo "  curl http://localhost:8080/api/tickers"
echo "  curl http://localhost:8080/api/prices"
echo ""

# Start server with uvicorn
uvicorn price_server:app --host 0.0.0.0 --port 8080 --reload
