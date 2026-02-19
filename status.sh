#!/bin/bash
echo "=== Mission Control Status ==="
echo ""
echo "Production (port 8080):"
if curl -s http://localhost:8080/api/ideas > /dev/null 2>&1; then
    IDEAS=$(curl -s http://localhost:8080/api/ideas 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('ideas',[])))" 2>/dev/null)
    echo "  ✅ Running ($IDEAS ideas)"
else
    echo "  ❌ Not responding"
fi

echo ""
echo "Dev (port 8081):"
if curl -s http://localhost:8081/api/ideas > /dev/null 2>&1; then
    IDEAS=$(curl -s http://localhost:8081/api/ideas 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('ideas',[])))" 2>/dev/null)
    echo "  ✅ Running ($IDEAS ideas)"
else
    echo "  ❌ Not responding"
fi

echo ""
echo "Directories:"
echo "  Prod: ~/.openclaw/workspace/mission_control_prod"
echo "  Dev:  ~/.openclaw/workspace/mission_control_dev"
