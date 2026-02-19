#!/bin/bash
cd "$(dirname "$0")"
python3 server.py > server.log 2>&1 &
echo "Mission Control starting on port 8080..."
echo "If port 8080 fails, try: python3 -c \"from server import app; app.run(port=5050)\""
sleep 2
echo "Dashboard: http://localhost:8080"
