#!/bin/bash
echo "=== Mission Control Status ==="
echo ""
echo "Production (8080):"
curl -s http://localhost:8080/ 2>&1 | head -1
echo ""
echo "Dev (8081):"
curl -s http://localhost:8081/ 2>&1 | head -1
echo ""
echo "PIDs:"
ps aux | grep "server.py" | grep -v grep | awk '{print $2, $11, $12}'
