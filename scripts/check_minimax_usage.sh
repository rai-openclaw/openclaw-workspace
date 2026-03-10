#!/bin/bash
# Check MiniMax Coding Plan usage
# Usage: ./check_minimax_usage.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../.env" 2>/dev/null

TOKEN="${MINIMAX_TOKEN}"

if [ -z "$TOKEN" ]; then
    echo "Error: MINIMAX_TOKEN not set in .env"
    exit 1
fi

response=$(curl -s -X GET "https://www.minimax.io/v1/api/openplatform/coding_plan/remains" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$response" | grep -q "status_code\":0"; then
    total=$(echo "$response" | grep -o '"current_interval_total_count":[0-9]*' | head -1 | cut -d':' -f2)
    used=$(echo "$response" | grep -o '"current_interval_usage_count":[0-9]*' | head -1 | cut -d':' -f2)
    remains_time=$(echo "$response" | grep -o '"remains_time":[0-9]*' | head -1 | cut -d':' -f2)
    remaining=$((total - used))
    percent=$((used * 100 / total))
    reset_minutes=$((remains_time / 1000 / 60))
    
    echo "📊 MiniMax Coding Plan Usage"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total:  $total prompts / 5hr"
    echo "Used:   $used"
    echo "Left:   $remaining"
    echo "Usage:  ${percent}%"
    echo "Resets: ~${reset_minutes} min"
    
    if [ $remaining -lt 100 ]; then
        echo ""
        echo "⚠️  WARNING: Less than 100 prompts remaining!"
    elif [ $percent -gt 90 ]; then
        echo ""
        echo "⚡ Usage above 90%"
    fi
else
    echo "Error checking usage:"
    echo "$response" | grep -o '"status_msg":"[^"]*"' | cut -d'"' -f4
fi
