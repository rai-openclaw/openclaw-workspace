#!/bin/bash
echo "🚨 EMERGENCY ROLLBACK 🚨"
echo "Restoring to v2.1-stable..."

cd "$(dirname "$0")

cp server.py.v2.1-stable server.py
cp templates/dashboard.html.v2.1-stable templates/dashboard.html

./mc.sh restart

echo "✅ Rolled back to v2.1-stable"
echo "Test: http://localhost:8080"
