#!/bin/bash
# Soft Reset Script - Graceful session cleanup and gateway restart

set -e

echo "=== Soft Reset Starting ==="

# Assumes memory has already been written by Jarvis before this script runs

# 1. Commit and push workspace
cd /Users/raitsai/.openclaw/workspace
git add -A
git commit -m "[System] Soft reset checkpoint"
git push origin dev

# 2. Commit and push mission-control-next
cd /Users/raitsai/.openclaw/workspace/mission-control-next
git add -A
git commit -m "[System] Soft reset checkpoint"
git push origin dev

# 3. Restart gateway
echo "🔄 Restarting gateway..."
openclaw gateway restart

echo "=== Soft Reset Complete ==="
echo "Start a fresh conversation to continue."
