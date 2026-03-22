# EAM System Documentation

**Last Updated:** 2026-01-29

## Quick Links

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System overview and high-level design |
| [backend/STRUCTURE.md](./backend/STRUCTURE.md) | Backend directory structure |
| [backend/DOCUMENT_SERVICE.md](./backend/DOCUMENT_SERVICE.md) | Frappe-like document API |
| [backend/FORGE_GUIDE.md](./backend/FORGE_GUIDE.md) | CLI tool usage |

## Documentation Structure

```
docs/
├── README.md                    # This file
├── ARCHITECTURE.md              # System architecture overview
├── backend/
│   ├── STRUCTURE.md             # Backend directory structure
│   ├── DOCUMENT_SERVICE.md      # Document service API
│   ├── FORGE_GUIDE.md           # Forge CLI guide
│   ├── CODING_STANDARDS.md      # Code style guidelines
│   └── ENTITY_REFERENCE.md      # Entity metadata reference
├── frontend/
│   └── VALIDATION_GUIDE.md      # Frontend validation
└── suggestions/
    ├── CLEANUP_REPORT.md        # Recent cleanup actions
    └── IMPROVEMENTS.md          # Future improvements
```

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
./scripts/deploy.sh --migrate

# Seed data
python -m app.forge seed

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Key Concepts

### 1. Modular Architecture
Each feature is a self-contained module in `app/modules/{module_name}/`:
- `models/` - SQLAlchemy models
- `entities/` - JSON metadata
- `apis/` - Custom business logic

### 2. Code-First Development
1. Define SQLAlchemy model
2. Run `python -m app.forge sync-meta` to generate JSON
3. Run `python -m app.forge migrate` to update DB

### 3. Generic CRUD
The `/api/entity/{name}` router handles all entities automatically based on metadata.

## Recent Changes (2026-01-29)

- Consolidated `seed.py` and `seed_eam.py` into single file
- Merged `workflow.py` and `workflow_db.py` services
- Merged `rbac.py` and `rbac_db.py` services
- Made all DB columns nullable for testing flexibility
- Added `scripts/deploy.sh` for deployment automation
- Cleaned up unused files and `__pycache__` directories
