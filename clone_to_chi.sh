#!/bin/bash
set -e

SUDO_PASS="Cw@dm1n!2026Sec"
SRC_DB_USER="eam_itba_user"
SRC_DB_PASS="CwItbaSec2026mR7"
SRC_DB_NAME="eam-itba"

CHI_DB_USER="eam_chi_user"
CHI_DB_PASS="CwChiSec2026xP9"
CHI_DB_NAME="eam-chi"
CHI_SECRET_KEY="5DTosvnyl9QrCx7U-Xp_Lcc8RPR3OOzhXTOijP0A_0FxsT0suTB2zk2iwZHuxBuf"

FRONTEND_PORT=3015
BACKEND_PORT=8015
DOMAIN="chieam.cubeworksinnovation.com"

run_psql_super() {
    echo "$SUDO_PASS" | sudo -S -u postgres psql "$@" 2>/dev/null
}

echo "=== Step 1: Clone folder eam-itba to eam-chi ==="
cd /home/cwadmin/eam-tests
if [ -d "eam-chi" ]; then
    echo "eam-chi already exists, removing..."
    rm -rf eam-chi
fi
cp -a eam-itba eam-chi
echo "Folder cloned successfully."

echo ""
echo "=== Step 2: Create CHI database user ==="
USER_EXISTS=$(run_psql_super -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname = '$CHI_DB_USER';" | tr -d ' ')
if [ "$USER_EXISTS" = "1" ]; then
    echo "User $CHI_DB_USER already exists."
else
    run_psql_super -d postgres -c "CREATE ROLE $CHI_DB_USER WITH LOGIN PASSWORD '$CHI_DB_PASS';"
    echo "User $CHI_DB_USER created."
fi

echo ""
echo "=== Step 3: Clone database ==="
run_psql_super -d postgres -c "DROP DATABASE IF EXISTS \"$CHI_DB_NAME\";"
run_psql_super -d postgres -c "CREATE DATABASE \"$CHI_DB_NAME\" OWNER $CHI_DB_USER;"
echo "Database $CHI_DB_NAME created."

echo "Dumping $SRC_DB_NAME..."
PGPASSWORD=$SRC_DB_PASS pg_dump -U $SRC_DB_USER -h localhost "$SRC_DB_NAME" > /tmp/eam-itba-dump.sql
echo "Restoring to $CHI_DB_NAME..."
PGPASSWORD=$CHI_DB_PASS psql -U $CHI_DB_USER -h localhost -d "$CHI_DB_NAME" < /tmp/eam-itba-dump.sql > /tmp/eam-chi-restore.log 2>&1
echo "Database cloned."

run_psql_super -d "$CHI_DB_NAME" -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO $CHI_DB_USER;"
run_psql_super -d "$CHI_DB_NAME" -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $CHI_DB_USER;"
run_psql_super -d "$CHI_DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $CHI_DB_USER;"
run_psql_super -d "$CHI_DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $CHI_DB_USER;"
echo "Permissions granted."
rm -f /tmp/eam-itba-dump.sql

echo ""
echo "=== Step 4: Update CHI backend .env ==="
cat > /home/cwadmin/eam-tests/eam-chi/backend/.env << 'ENVEOF'
DATABASE_URL=postgresql+asyncpg://eam_chi_user:CwChiSec2026xP9@localhost:5432/eam-chi
SECRET_KEY=5DTosvnyl9QrCx7U-Xp_Lcc8RPR3OOzhXTOijP0A_0FxsT0suTB2zk2iwZHuxBuf
RUN_SEEDS=false
CORS_ORIGINS=["http://127.0.0.1:3015","http://localhost:3015","http://194.233.77.65:3015","https://chieam.cubeworksinnovation.com","http://chieam.cubeworksinnovation.com"]
SOCKETIO_CORS_ORIGINS=["http://127.0.0.1:3015","http://localhost:3015","http://194.233.77.65:3015","https://chieam.cubeworksinnovation.com","http://chieam.cubeworksinnovation.com"]
ENVEOF
echo "Backend .env updated."

echo ""
echo "=== Step 5: Update CHI frontend .env ==="
cat > /home/cwadmin/eam-tests/eam-chi/frontend/.env << 'ENVEOF'
NODE_ENV=production
HOST=0.0.0.0
PORT=3015
NUXT_PUBLIC_API_URL=/api
NUXT_PUBLIC_WS_URL=
ENVEOF
echo "Frontend .env updated."

echo ""
echo "=== Step 6: Cleanup ==="
rm -f /home/cwadmin/eam-tests/eam-chi/frontend/app/layouts/default.vue.bak

echo ""
echo "=== Step 7: Rebuild CHI frontend ==="
cd /home/cwadmin/eam-tests/eam-chi/frontend
export NVM_DIR=/home/cwadmin/.nvm
source "$NVM_DIR/nvm.sh"
nvm use 20 >/dev/null 2>&1
echo "Building frontend (this takes ~2 min)..."
npx nuxt build > /tmp/nuxt_chi_build.log 2>&1
BUILD_EXIT=$?
if [ $BUILD_EXIT -eq 0 ]; then
    echo "Frontend built successfully."
else
    echo "Frontend build FAILED (exit code $BUILD_EXIT)."
    tail -20 /tmp/nuxt_chi_build.log
    exit 1
fi

echo ""
echo "=== Step 8: Create systemd services ==="
echo "$SUDO_PASS" | sudo -S tee /etc/systemd/system/eam-chi-backend.service > /dev/null << 'SVCEOF'
[Unit]
Description=EAM CHI Backend API
After=network.target

[Service]
Type=simple
User=cwadmin
WorkingDirectory=/home/cwadmin/eam-tests/eam-chi/backend
Environment=PATH=/home/cwadmin/eam-tests/eam-chi/backend/venv/bin
Environment=RUN_SEEDS=false
EnvironmentFile=-/home/cwadmin/eam-tests/eam-chi/backend/.env
ExecStart=/home/cwadmin/eam-tests/eam-chi/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8015
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

echo "$SUDO_PASS" | sudo -S tee /etc/systemd/system/eam-chi-frontend.service > /dev/null << 'SVCEOF'
[Unit]
Description=EAM CHI Frontend
After=network.target

[Service]
Type=simple
User=cwadmin
WorkingDirectory=/home/cwadmin/eam-tests/eam-chi/frontend
Environment=NODE_ENV=production
Environment=NODE_OPTIONS=--max-old-space-size=4096
Environment=HOST=0.0.0.0
Environment=PORT=3015
Environment=NVM_DIR=/home/cwadmin/.nvm
EnvironmentFile=-/home/cwadmin/eam-tests/eam-chi/frontend/.env
ExecStart=/bin/bash -lc 'source "$NVM_DIR/nvm.sh" && nvm use 20 >/dev/null && node .output/server/index.mjs'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF
echo "Systemd services created."

echo ""
echo "=== Step 9: Create nginx config ==="
echo "$SUDO_PASS" | sudo -S tee /etc/nginx/sites-available/chieam.cubeworksinnovation.com > /dev/null << 'NGXEOF'
server {
    listen 80;
    listen [::]:80;
    server_name chieam.cubeworksinnovation.com;

    location / {
        proxy_pass http://127.0.0.1:3015;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8015;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:8015;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600;
        proxy_send_timeout 3600;
    }
}
NGXEOF

echo "$SUDO_PASS" | sudo -S ln -sf /etc/nginx/sites-available/chieam.cubeworksinnovation.com /etc/nginx/sites-enabled/chieam.cubeworksinnovation.com
echo "Nginx config created and enabled."
echo "$SUDO_PASS" | sudo -S nginx -t 2>&1

echo ""
echo "=== Step 10: Start services ==="
echo "$SUDO_PASS" | sudo -S systemctl daemon-reload 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl enable eam-chi-backend eam-chi-frontend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-chi-backend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl start eam-chi-frontend 2>/dev/null
echo "$SUDO_PASS" | sudo -S systemctl reload nginx 2>/dev/null
sleep 3

echo ""
echo "=== Verifying ==="
echo "Backend: $(echo $SUDO_PASS | sudo -S systemctl is-active eam-chi-backend 2>/dev/null)"
echo "Frontend: $(echo $SUDO_PASS | sudo -S systemctl is-active eam-chi-frontend 2>/dev/null)"
sleep 2
curl -s -o /dev/null -w "Frontend HTTP: %{http_code}\n" http://localhost:3015/ 2>/dev/null
curl -s -o /dev/null -w "Backend HTTP: %{http_code}\n" http://localhost:8015/api/docs 2>/dev/null

echo ""
echo "=============================================="
echo "  CHI EAM Clone Complete!"
echo "=============================================="
echo "  URL:      https://chieam.cubeworksinnovation.com"
echo "  Frontend: port 3015"
echo "  Backend:  port 8015"
echo "  Database: eam-chi (user: eam_chi_user)"
echo "  Folder:   /home/cwadmin/eam-tests/eam-chi"
echo "=============================================="
