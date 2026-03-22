#!/bin/bash

# Semi-Frappe Development Server Launcher
# Starts both backend (FastAPI) and frontend (Nuxt) servers

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Semi-Frappe Development Servers${NC}"
echo "============================================"

# Kill existing processes on ports 8000 and 3000
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start Backend
echo -e "${GREEN}Starting Backend (FastAPI) on port 8000...${NC}"
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --port 8000 \
  --reload-exclude 'backups/*' \
  --reload-exclude 'alembic/versions/*' \
  --reload-exclude '*/models/*.py' &
BACKEND_PID=$!

# Start Frontend
echo -e "${GREEN}Starting Frontend (Nuxt) on port 3000...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Servers started successfully!${NC}"
echo -e "  Backend:  ${YELLOW}http://localhost:8000${NC}"
echo -e "  Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "  API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop all servers"

# Trap Ctrl+C to kill both processes
trap "echo -e '\n${RED}Stopping servers...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for processes
wait
