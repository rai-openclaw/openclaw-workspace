#!/bin/bash
# deploy-to-prod.sh - Deploy dev changes to production
# Usage: ./deploy-to-prod.sh

set -e  # Exit on any error

echo "🚀 Deploying dev to production"
echo ""

# 1. Verify dev works
echo "Step 1: Testing dev server..."
cd ~/.openclaw/workspace/mission_control_dev
./mc.sh restart > /dev/null 2>&1
sleep 3
if ! curl -s http://localhost:8081/api/ideas > /dev/null 2>&1; then
    echo "❌ Dev server not responding! Fix before deploying."
    exit 1
fi
echo "✓ Dev server working"

# 2. Backup production
echo ""
echo "Step 2: Backing up production..."
cd ~/.openclaw/workspace
BACKUP_NAME="mission_control_prod_backup_$(date +%Y%m%d_%H%M%S)"
cp -r mission_control_prod "$BACKUP_NAME"
echo "✓ Backed up to: $BACKUP_NAME"

# 3. Stop both servers
echo ""
echo "Step 3: Stopping servers..."
pkill -f "server.py" 2>/dev/null || true
sleep 2
echo "✓ Servers stopped"

# 4. Sync dev to prod (except port config)
echo ""
echo "Step 4: Syncing dev → prod..."
cd ~/.openclaw/workspace

# Copy everything except port configs
rsync -av --exclude='server.py' --exclude='mc.sh' --exclude='*.log' --exclude='__pycache__' mission_control_dev/ mission_control_prod/

# Copy server.py but fix port to 8080
sed 's/8081/8080/g' mission_control_dev/server.py > mission_control_prod/server.py
echo "✓ Synced (port adjusted for prod)"

# 5. Restart production
echo ""
echo "Step 5: Starting production..."
cd mission_control_prod
./mc.sh restart > /dev/null 2>&1
sleep 3

if ! curl -s http://localhost:8080/api/ideas > /dev/null 2>&1; then
    echo "❌ Production failed to start! Rolling back..."
    cd ~/.openclaw/workspace
    rm -rf mission_control_prod
    mv "$BACKUP_NAME" mission_control_prod
    cd mission_control_prod
    ./mc.sh restart
    echo "✓ Rolled back to backup"
    exit 1
fi

echo "✓ Production running"

# 6. Restart dev
echo ""
echo "Step 6: Restarting dev..."
cd ~/.openclaw/workspace/mission_control_dev
./mc.sh restart > /dev/null 2>&1
sleep 2

echo ""
echo "========================================"
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "========================================"
echo ""
echo "Production: http://localhost:8080/"
echo "Dev:        http://localhost:8081/"
echo ""
echo "Backup: $BACKUP_NAME"
