#!/bin/bash
# reset-and-start.sh - Nuclear option: Kill everything, start fresh

echo "🧨 NUCLEAR RESET"
echo ""

# Kill ALL Python
pkill -9 -f "Python" 2>/dev/null
pkill -9 -f "python" 2>/dev/null
sleep 2

# Verify clean
PYTHON_COUNT=$(ps aux | grep -i python | grep -v grep | wc -l)
if [ "$PYTHON_COUNT" -gt 0 ]; then
    echo "❌ Python still running!"
    exit 1
fi

# Verify ports free
for port in 8080 8081; do
    if lsof -i :$port 2>/dev/null | grep -q .; then
        echo "❌ Port $port in use!"
        exit 1
    fi
    echo "✓ Port $port free"
done

# Start from correct directory
cd ~/.openclaw/workspace/mission_control || exit 1
echo "✓ Directory: $PWD"

# Start production
echo ""
echo "🚀 Production (8080)..."
python3 server.py 8080 > /tmp/mc-prod.log 2>&1 &
sleep 3
curl -s http://localhost:8080/ > /dev/null || { echo "❌ Failed"; exit 1; }
echo "✓ Running"

# Start dev
echo ""
echo "🚀 Dev (8081)..."
python3 server.py 8081 > /tmp/mc-dev.log 2>&1 &
sleep 3
curl -s http://localhost:8081/ > /dev/null || { echo "❌ Failed"; exit 1; }
echo "✓ Running"

# Verify identical
echo ""
echo "🔍 Verifying..."
PROD=$(curl -s http://localhost:8080/api/ideas 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('ideas',[])))" 2>/dev/null)
DEV=$(curl -s http://localhost:8081/api/ideas 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('ideas',[])))" 2>/dev/null)

if [ "$PROD" = "$DEV" ]; then
    echo "✅ Both servers identical ($PROD ideas)"
    echo ""
    echo "Production: http://localhost:8080/"
    echo "Dev:        http://localhost:8081/"
else
    echo "❌ MISMATCH: Prod=$PROD, Dev=$DEV"
    exit 1
fi
