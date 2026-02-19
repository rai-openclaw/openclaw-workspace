#!/bin/bash
# Dev server on port 8081 for testing

cd "$(dirname "$0")"

# Kill any existing dev server
pkill -f "server.py 8081" 2>/dev/null

# Start dev server
echo "Starting DEV server on http://localhost:8081"
python3 server.py 8081 > /tmp/mc-dev.log 2>&1 &
DEV_PID=$!
echo $DEV_PID > /tmp/mc-dev.pid

echo "Dev server PID: $DEV_PID"
echo "Logs: tail -f /tmp/mc-dev.log"
echo "URL: http://localhost:8081"
