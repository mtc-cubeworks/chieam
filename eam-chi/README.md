# EAM System

A metadata-driven **Enterprise Asset Management** system built with **FastAPI + SQLAlchemy** (backend) and **Nuxt 4 + Nuxt UI** (frontend), following Clean Architecture principles.

## Features

- **Metadata-driven** — Entity definitions (`.json`) drive models, API, forms, and validation automatically.
- **Clean Architecture** — Domain → Application → Infrastructure → API layers with protocol-based DI.
- **Modular** — Entities grouped into domain modules (`core_eam`, `asset_management`, `maintenance_mgmt`, `work_mgmt`, `purchasing_stores`).
- **Generic CRUD API** — Single router set (`/api/entity/{name}`) handles all entities.
- **Workflow Engine** — State-machine workflows with role-based transition control.
- **RBAC** — Role-based entity-level permissions (read/create/update/delete/select/export/import).
- **Forge CLI** — Code generation, migrations, and system management from the terminal.
- **First-Run Setup** — On fresh install, the frontend redirects to a setup wizard to create the first admin account.

## Prerequisites

| Dependency | Version | Notes                   |
| ---------- | ------- | ----------------------- |
| Python     | ≥ 3.10  |                         |
| Node.js    | ≥ 20    | via nvm recommended     |
| pnpm       | ≥ 10    | `npm i -g pnpm`         |
| PostgreSQL | ≥ 14    | Required for production |

## Quick Start

### 1. Clone & configure

```bash
git clone <repo-url> eam-system && cd eam-system
cp .env.example backend/.env
# Edit backend/.env — set DATABASE_URL and SECRET_KEY at minimum
```

### 2. PostgreSQL setup

Create the role and database (run as Postgres admin):

```sql
CREATE ROLE eam_user LOGIN PASSWORD 'eam_password';
CREATE DATABASE eam_db OWNER eam_user;
\c eam_db
GRANT ALL ON SCHEMA public TO eam_user;
```

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Apply database migrations
python -m app.forge migrate --apply-only

# Start the server (default port 8010)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

### 4. Frontend

```bash
cd frontend
pnpm install

# Development (default port 3000)
NUXT_PUBLIC_API_URL=http://localhost:8010/api pnpm dev
```

### 5. First-run setup

Open `http://localhost:3000` in your browser. On a fresh database (no users), you will be automatically redirected to the **Setup Wizard** where you create your administrator account. After setup, you can log in normally.

### Production build

```bash
cd frontend
pnpm build
# Start the production server
node .output/server/index.mjs
```

## Project Structure

```
eam-system/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routes (Clean Architecture)
│   │   │   ├── routes/         # Entity CRUD, list, workflow, setup, etc.
│   │   │   └── dependencies.py # DI factories
│   │   ├── application/        # Use-case orchestration
│   │   │   ├── services/       # EntityService, AuthService, etc.
│   │   │   └── hooks/          # Lifecycle hook registry
│   │   ├── domain/             # Protocols & exceptions
│   │   ├── infrastructure/     # DB repos, auth, email, realtime
│   │   ├── modules/            # Domain modules
│   │   │   └── {module}/
│   │   │       ├── models/     # SQLAlchemy models
│   │   │       ├── entities/   # JSON metadata
│   │   │       ├── apis/       # Business logic handlers
│   │   │       ├── hooks.py    # Lifecycle hooks
│   │   │       └── workflow_router.py
│   │   ├── core/               # Config, DB, security, loader
│   │   ├── routers/            # Legacy routes (auth, admin, workflow)
│   │   └── services/           # Shared services (RBAC, document, etc.)
│   ├── alembic/                # Database migrations
│   ├── scripts/
│   │   └── seeds/              # Data seeding scripts
│   ├── tests/                  # Pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/         # UI components
│   │   ├── composables/        # Shared logic (useAuth, useApi, etc.)
│   │   ├── pages/              # Nuxt file-based routing
│   │   ├── stores/             # Pinia stores
│   │   ├── middleware/         # Auth middleware
│   │   └── plugins/            # Socket.IO, etc.
│   ├── nuxt.config.ts
│   └── package.json
├── docs/                       # Architecture & guides
├── masterfiles/                # Excel seed data
├── records/                    # Excel record data
└── .env.example                # Environment template
```

## Forge CLI

Run from the `backend/` directory with the virtualenv active:

```bash
# Sync models + generate + apply migration (one command)
python -m app.forge sync

# Generate a new entity
python -m app.forge new-entity my_entity --module my_module --fields "name:string,status:select"

# Migration management
python -m app.forge migrate --status
python -m app.forge migrate --apply-only
python -m app.forge migrate --rollback 1

# System status
python -m app.forge status
```

## Data Seeding

Seed scripts live in `backend/scripts/seeds/`. Run from the `backend/` directory:

```bash
# 1. Seed masterfiles from Excel
python scripts/seeds/seed_masterfiles_workbooks.py

# 2. Reset workflow catalog
python scripts/seeds/reset_workflow_catalog.py

# 3. Seed workflows from Excel
python scripts/seeds/seed_workflows_from_excel.py

# 4. Seed roles & permissions
python scripts/seeds/seed_roles_permissions.py
```

See [docs/SEEDING_GUIDE.md](docs/SEEDING_GUIDE.md) for the full seeding order.

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Backend Coding Standards](docs/backend/CODING_STANDARDS.md)
- [Forge CLI Guide](docs/backend/FORGE_GUIDE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [Seeding Guide](docs/SEEDING_GUIDE.md)
- [Database Credentials](docs/DATABASE_CREDENTIALS.md)

## Environment Variables

See [`.env.example`](.env.example) for the full list. The only required variable is `DATABASE_URL`.

## Server Connection & Deployment

### Server Access (Contabo VPS)

| Item | Value |
|------|-------|
| **Host** | `194.233.77.65` |
| **SSH Port** | `2228` |
| **Username** | `cwadmin` |
| **Password** | `Cw@dm1n!2026Sec` |

```bash
# Connect via SSH
ssh -p 2228 cwadmin@194.233.77.65

# Or using sshpass (for scripts)
sshpass -p 'Cw@dm1n!2026Sec' ssh -p 2228 cwadmin@194.233.77.65
```

### Instance Configurations

#### CHI Instance

| Item | Value |
|------|-------|
| **Domain** | `chieam.cubeworksinnovation.com` |
| **Server Path** | `/home/cwadmin/eam-tests/eam-chi` |
| **Frontend Port** | `3015` |
| **Backend Port** | `8015` |
| **Frontend Service** | `eam-chi-frontend` |
| **Backend Service** | `eam-chi-backend` |

**CHI Database:**

| Item | Value |
|------|-------|
| **Database** | `eam-chi` |
| **Username** | `eam_chi_user` |
| **Password** | `CwChiSec2026xP9` |
| **Secret Key** | `5DTosvnyl9QrCx7U-Xp_Lcc8RPR3OOzhXTOijP0A_0FxsT0suTB2zk2iwZHuxBuf` |
| **Async URL** | `postgresql+asyncpg://eam_chi_user:CwChiSec2026xP9@localhost:5432/eam-chi` |

#### ITBA Instance

| Item | Value |
|------|-------|
| **Domain** | `itbaeam.cubeworksinnovation.com` |
| **Server Path** | `/home/cwadmin/eam-tests/eam-itba` |
| **Frontend Port** | `3014` |
| **Backend Port** | `8014` |
| **Frontend Service** | `eam-itba-backend` |
| **Backend Service** | `eam-itba-frontend` |

**ITBA Database:**

| Item | Value |
|------|-------|
| **Database** | `eam-itba` |
| **Username** | `eam_itba_user` |
| **Password** | `CwItbaSec2026mR7` |
| **Async URL** | `postgresql+asyncpg://eam_itba_user:CwItbaSec2026mR7@localhost:5432/eam-itba` |

### Updating Instances

#### Quick Deploy (sync local code to both instances)

Run from the project root (`EAM-CHI/`):

```bash
# Sync CHI and ITBA instances from local code
./sync_chi_to_itba.sh
```

This script:
1. Backs up `.env` files on the server
2. Uploads local `eam-chi/` code to the server's CHI instance via rsync
3. Copies code from CHI to ITBA on the server (preserving each instance's `.env`)
4. Restores `.env` files
5. Stops all services
6. Runs Alembic database migrations on both databases
7. Rebuilds both frontends
8. Restarts all services

#### Manual Deploy (single instance)

```bash
# SSH into server
ssh -p 2228 cwadmin@194.233.77.65

# --- CHI Instance ---
cd /home/cwadmin/eam-tests/eam-chi

# Pull latest changes (if using git on server)
git stash && git pull origin main

# Rebuild frontend
cd frontend
export NVM_DIR=/home/cwadmin/.nvm && source "$NVM_DIR/nvm.sh" && nvm use 20
npx nuxt build

# Restart services
sudo systemctl restart eam-chi-backend
sudo systemctl restart eam-chi-frontend

# --- ITBA Instance (same steps, different paths/services) ---
cd /home/cwadmin/eam-tests/eam-itba
# ... same build steps ...
sudo systemctl restart eam-itba-backend
sudo systemctl restart eam-itba-frontend
```

#### Useful Server Commands

```bash
# Check service status
sudo systemctl status eam-chi-backend --no-pager
sudo systemctl status eam-chi-frontend --no-pager
sudo systemctl status eam-itba-backend --no-pager
sudo systemctl status eam-itba-frontend --no-pager

# View logs
sudo journalctl -u eam-chi-backend --since "10 min ago"
sudo journalctl -u eam-chi-frontend --since "10 min ago"

# Restart nginx
sudo systemctl reload nginx

# Connect to CHI database
PGPASSWORD=CwChiSec2026xP9 psql -U eam_chi_user -h localhost -d eam-chi

# Connect to ITBA database
PGPASSWORD=CwItbaSec2026mR7 psql -U eam_itba_user -h localhost -d eam-itba

# Full restart (both instances)
sudo systemctl restart eam-chi-backend eam-chi-frontend eam-itba-backend eam-itba-frontend
```

### Prerequisites for Sync Script

The `sync_chi_to_itba.sh` script requires `sshpass` and `rsync` on the local machine:

```bash
# macOS
brew install sshpass rsync

# Ubuntu/Debian
sudo apt install sshpass rsync
```

## Tech Stack

**Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, Socket.IO, Jinja2, aiosmtplib

**Frontend:** Nuxt 4, Vue 3, Nuxt UI 4, Pinia, Tailwind CSS 4, VueUse, Cytoscape.js, Socket.IO Client
