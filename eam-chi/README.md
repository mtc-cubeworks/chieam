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

## Tech Stack

**Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, Socket.IO, Jinja2, aiosmtplib

**Frontend:** Nuxt 4, Vue 3, Nuxt UI 4, Pinia, Tailwind CSS 4, VueUse, Cytoscape.js, Socket.IO Client
