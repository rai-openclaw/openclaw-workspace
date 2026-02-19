#!/bin/bash
cd "$(dirname "$0")"
pkill -9 python3 2>/dev/null
sleep 2
python3 -B server.py 2>&1 | sed 's/port=8080/port=6060/g' &
echo "Starting on port 6060..."
sleep 3
echo "Dashboard: http://localhost:6060"
