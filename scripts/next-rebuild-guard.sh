#!/bin/bash
# Next.js Build Cache Reset Script
# Resets the Next.js build cache to fix stale artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Next.js dev server..."
pkill -f "next dev" 2>/dev/null || true

echo "Removing .next build cache..."
rm -rf mission-control-next/.next

echo "Restarting Next.js dev server..."
cd mission-control-next
npm run dev &
sleep 5

echo "Next.js build cache reset complete"
