#!/bin/bash
# Sync dev changes to production - ONLY after verification

echo "⚠️  WARNING: This will copy dev changes to production!"
echo "Make sure you tested on http://localhost:8081 first!"
read -p "Type YES to proceed: " confirm

if [ "$confirm" != "YES" ]; then
    echo "Cancelled"
    exit 1
fi

cd "$(dirname "$0")"

# Backup production first
cp server.py server.py.pre-sync.$(date +%Y%m%d_%H%M%S)
cp templates/dashboard.html templates/dashboard.html.pre-sync.$(date +%Y%m%d_%H%M%S)

# Copy dev to prod
cp server.py server.py.prod
cp templates/dashboard.html templates/dashboard.html.prod

echo "✅ Synced to production backups"
echo "Restart production server with: ./prod-server.sh"
