#!/bin/bash
# =============================================================================
# sync_chi_to_itba.sh
# Syncs EAM-CHI code and database schema to EAM-ITBA on the production server.
#
# What this script does:
#   1. Uploads local code changes to server's eam-chi and eam-itba
#   2. Preserves each instance's .env configuration
#   3. Runs alembic migrations on both databases
#   4. Rebuilds both frontends
#   5. Restarts all services
#
# Run from: /Users/marlonceniza/Documents/Composable/EAM-CHI/
# =============================================================================
set -e

# --- Server connection ---
SERVER="194.233.77.65"
PORT=2228
USER="cwadmin"
PASS='Cw@dm1n!2026Sec'
SSH_CMD="sshpass -p '$PASS' ssh -o ConnectTimeout=15 -o StrictHostKeyChecking=no -p $PORT $USER@$SERVER"
SCP_CMD="sshpass -p '$PASS' scp -o ConnectTimeout=15 -o StrictHostKeyChecking=no -P $PORT"
RSYNC_CMD="sshpass -p '$PASS' rsync -avz --progress -e 'ssh -o StrictHostKeyChecking=no -p $PORT'"

# --- Paths ---
LOCAL_CODE="$(cd "$(dirname "$0")" && pwd)/eam-chi"
REMOTE_BASE="/home/cwadmin/eam-tests"
CHI_REMOTE="$REMOTE_BASE/eam-chi"
ITBA_REMOTE="$REMOTE_BASE/eam-itba"

# --- Database ---
CHI_DB_USER="eam_chi_user"
CHI_DB_PASS="CwChiSec2026xP9"
CHI_DB_NAME="eam-chi"
ITBA_DB_USER="eam_itba_user"
ITBA_DB_PASS="CwItbaSec2026mR7"
ITBA_DB_NAME="eam-itba"

# --- Config that must be preserved per instance ---
# CHI: backend port 8015, frontend port 3015, domain chieam.cubeworksinnovation.com
# ITBA: backend port 8014, frontend port 3014, domain itbaeam.cubeworksinnovation.com

echo ""
echo "============================================================"
echo "  EAM-CHI → EAM-ITBA Sync Script"
echo "============================================================"
echo ""

# --- Pre-flight check ---
if ! command -v sshpass &> /dev/null; then
    echo "ERROR: sshpass is required. Install with: brew install sshpass"
    exit 1
fi

if [ ! -d "$LOCAL_CODE/backend" ] || [ ! -d "$LOCAL_CODE/frontend" ]; then
    echo "ERROR: Cannot find eam-chi/backend and eam-chi/frontend in $LOCAL_CODE"
    exit 1
fi

# =============================================================================
# STEP 1: Backup .env files from both instances on the server
# =============================================================================
echo "=== Step 1: Backing up .env files on server ==="
eval $SSH_CMD << 'REMOTE_BACKUP'
set -e
echo "Backing up CHI .env files..."
cp /home/cwadmin/eam-tests/eam-chi/backend/.env /tmp/eam-chi-backend.env.bak 2>/dev/null || true
cp /home/cwadmin/eam-tests/eam-chi/frontend/.env /tmp/eam-chi-frontend.env.bak 2>/dev/null || true
echo "Backing up ITBA .env files..."
cp /home/cwadmin/eam-tests/eam-itba/backend/.env /tmp/eam-itba-backend.env.bak 2>/dev/null || true
cp /home/cwadmin/eam-tests/eam-itba/frontend/.env /tmp/eam-itba-frontend.env.bak 2>/dev/null || true
echo "Backups saved to /tmp/"
REMOTE_BACKUP
echo "Done."

# =============================================================================
# STEP 2: Sync local code to server's eam-chi
# =============================================================================
echo ""
echo "=== Step 2: Syncing local code → server eam-chi ==="
eval $RSYNC_CMD \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='backend/venv/' \
    --exclude='backend/.env' \
    --exclude='frontend/node_modules/' \
    --exclude='frontend/.output/' \
    --exclude='frontend/.nuxt/' \
    --exclude='frontend/.env' \
    "$LOCAL_CODE/" "$USER@$SERVER:$CHI_REMOTE/"
echo "CHI code synced."

# =============================================================================
# STEP 3: Copy code from eam-chi to eam-itba on the server (preserve ITBA .env)
# =============================================================================
echo ""
echo "=== Step 3: Syncing code eam-chi → eam-itba on server ==="
eval $SSH_CMD << 'REMOTE_COPY'
set -e
echo "Syncing backend code..."
rsync -a --delete \
    --exclude='venv/' \
    --exclude='.env' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    /home/cwadmin/eam-tests/eam-chi/backend/ /home/cwadmin/eam-tests/eam-itba/backend/

echo "Syncing frontend code..."
rsync -a --delete \
    --exclude='node_modules/' \
    --exclude='.output/' \
    --exclude='.nuxt/' \
    --exclude='.env' \
    /home/cwadmin/eam-tests/eam-chi/frontend/ /home/cwadmin/eam-tests/eam-itba/frontend/

echo "Code synced to ITBA."
REMOTE_COPY
echo "Done."

# =============================================================================
# STEP 4: Restore .env files
# =============================================================================
echo ""
echo "=== Step 4: Restoring .env files ==="
eval $SSH_CMD << 'REMOTE_RESTORE'
set -e
cp /tmp/eam-chi-backend.env.bak /home/cwadmin/eam-tests/eam-chi/backend/.env 2>/dev/null || true
cp /tmp/eam-chi-frontend.env.bak /home/cwadmin/eam-tests/eam-chi/frontend/.env 2>/dev/null || true
cp /tmp/eam-itba-backend.env.bak /home/cwadmin/eam-tests/eam-itba/backend/.env 2>/dev/null || true
cp /tmp/eam-itba-frontend.env.bak /home/cwadmin/eam-tests/eam-itba/frontend/.env 2>/dev/null || true
echo ".env files restored."
REMOTE_RESTORE
echo "Done."

# =============================================================================
# STEP 5: Stop services before DB migration
# =============================================================================
echo ""
echo "=== Step 5: Stopping services ==="
eval $SSH_CMD << 'REMOTE_STOP'
set -e
SUDO_PASS="Cw@dm1n!2026Sec"
echo "$SUDO_PASS" | sudo -S systemctl stop eam-chi-backend 2>/dev/null || true
echo "$SUDO_PASS" | sudo -S systemctl stop eam-chi-frontend 2>/dev/null || true
echo "$SUDO_PASS" | sudo -S systemctl stop eam-itba-backend 2>/dev/null || true
echo "$SUDO_PASS" | sudo -S systemctl stop eam-itba-frontend 2>/dev/null || true
echo "All EAM services stopped."
REMOTE_STOP
echo "Done."

# =============================================================================
# STEP 6: Run database migrations on both instances
# =============================================================================
echo ""
echo "=== Step 6: Running database migrations ==="
eval $SSH_CMD << 'REMOTE_MIGRATE'
set -e

echo "--- CHI Database ---"
cd /home/cwadmin/eam-tests/eam-chi/backend
source venv/bin/activate

# Stamp current DB state (all existing schema is already applied)
echo "Stamping CHI DB at afd998d01c9f..."
alembic stamp afd998d01c9f 2>&1 || true

# Upgrade to head (applies gap migrations + merge)
echo "Running alembic upgrade head on CHI..."
alembic upgrade head 2>&1

echo "CHI DB migration complete."
deactivate

echo ""
echo "--- ITBA Database ---"
cd /home/cwadmin/eam-tests/eam-itba/backend
source venv/bin/activate

# Stamp current DB state
echo "Stamping ITBA DB at afd998d01c9f..."
alembic stamp afd998d01c9f 2>&1 || true

# Upgrade to head
echo "Running alembic upgrade head on ITBA..."
alembic upgrade head 2>&1

echo "ITBA DB migration complete."
deactivate
REMOTE_MIGRATE
echo "Done."

# =============================================================================
# STEP 7: Rebuild both frontends
# =============================================================================
echo ""
echo "=== Step 7: Rebuilding frontends (this takes a few minutes) ==="
eval $SSH_CMD << 'REMOTE_BUILD'
set -e
export NVM_DIR=/home/cwadmin/.nvm
source "$NVM_DIR/nvm.sh"
nvm use 20 >/dev/null 2>&1

echo "Building CHI frontend..."
cd /home/cwadmin/eam-tests/eam-chi/frontend
npx nuxt build > /tmp/nuxt_chi_build.log 2>&1
BUILD_EXIT=$?
if [ $BUILD_EXIT -eq 0 ]; then
    echo "CHI frontend built successfully."
else
    echo "CHI frontend build FAILED (exit code $BUILD_EXIT)."
    tail -20 /tmp/nuxt_chi_build.log
fi

echo ""
echo "Building ITBA frontend..."
cd /home/cwadmin/eam-tests/eam-itba/frontend
npx nuxt build > /tmp/nuxt_itba_build.log 2>&1
BUILD_EXIT=$?
if [ $BUILD_EXIT -eq 0 ]; then
    echo "ITBA frontend built successfully."
else
    echo "ITBA frontend build FAILED (exit code $BUILD_EXIT)."
    tail -20 /tmp/nuxt_itba_build.log
fi
REMOTE_BUILD
echo "Done."

# =============================================================================
# STEP 8: Restart all services
# =============================================================================
echo ""
echo "=== Step 8: Restarting services ==="
eval $SSH_CMD << 'REMOTE_START'
set -e
SUDO_PASS="Cw@dm1n!2026Sec"
echo "$SUDO_PASS" | sudo -S systemctl daemon-reload 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-chi-backend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-chi-frontend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-itba-backend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-itba-frontend 2>/dev/null
sleep 3
echo "Service Status:"
echo "  CHI Backend:  $(echo $SUDO_PASS | sudo -S systemctl is-active eam-chi-backend 2>/dev/null)"
echo "  CHI Frontend: $(echo $SUDO_PASS | sudo -S systemctl is-active eam-chi-frontend 2>/dev/null)"
echo "  ITBA Backend: $(echo $SUDO_PASS | sudo -S systemctl is-active eam-itba-backend 2>/dev/null)"
echo "  ITBA Frontend:$(echo $SUDO_PASS | sudo -S systemctl is-active eam-itba-frontend 2>/dev/null)"
REMOTE_START
echo "Done."

# =============================================================================
# STEP 9: Verify endpoints
# =============================================================================
echo ""
echo "=== Step 9: Verifying endpoints ==="
eval $SSH_CMD << 'REMOTE_VERIFY'
sleep 2
echo "CHI:"
curl -s -o /dev/null -w "  Frontend (3015): HTTP %{http_code}\n" http://localhost:3015/ 2>/dev/null || echo "  Frontend: unreachable"
curl -s -o /dev/null -w "  Backend  (8015): HTTP %{http_code}\n" http://localhost:8015/api/docs 2>/dev/null || echo "  Backend: unreachable"
echo ""
echo "ITBA:"
curl -s -o /dev/null -w "  Frontend (3014): HTTP %{http_code}\n" http://localhost:3014/ 2>/dev/null || echo "  Frontend: unreachable"
curl -s -o /dev/null -w "  Backend  (8014): HTTP %{http_code}\n" http://localhost:8014/api/docs 2>/dev/null || echo "  Backend: unreachable"
REMOTE_VERIFY

echo ""
echo "============================================================"
echo "  Sync Complete!"
echo "============================================================"
echo "  CHI:  https://chieam.cubeworksinnovation.com"
echo "        Frontend: 3015 | Backend: 8015 | DB: eam-chi"
echo ""
echo "  ITBA: https://itbaeam.cubeworksinnovation.com"
echo "        Frontend: 3014 | Backend: 8014 | DB: eam-itba"
echo "============================================================"
