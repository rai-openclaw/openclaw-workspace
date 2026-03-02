#!/bin/bash

# Kill any existing python processes on our ports
pkill -f "python3.*server" 2>/dev/null
sleep 2

# Start server on port 8080
cd "$(dirname "$0")"
python3 -B server.py > server.log 2>&1 &
SERVER_PID=$!

echo "Server started on port 8080 (PID: $SERVER_PID)"
echo "Dashboard: http://localhost:8080"
echo ""
echo "To stop: kill $SERVER_PID"
