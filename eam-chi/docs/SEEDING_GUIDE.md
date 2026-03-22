# Seeding Instructions (Server-Ready)

This repository supports two different concepts of "seeding":

- **Application bootstrap seeding** (roles/users/workflow sample config, etc.) via `app/core/seed.py`.
- **Masterfiles Excel seeding** (authoritative reference data) via `seed_masterfiles_workbooks.py`.

Keep these separate to avoid mixing test/sample records with master data.

## 1) Prerequisites

- **Database migrations are applied** (tables exist).
- You have a working `DATABASE_URL` (or whatever your `app.core.config` expects).
- You have access to the masterfiles workbooks directory on the server.

Schema requirement:

- This system uses **human-readable string IDs** (e.g. `ORG-00001`) as primary keys and foreign keys.
- Postgres schemas initialized with UUID-typed `id` / FK columns are incompatible with Excel seeding.
- Ensure Alembic has been applied through the latest revision before running any seed scripts.

## 2) Environment Variables

### Masterfiles workbook paths (recommended)

`seed_masterfiles_workbooks.py` is configurable and **must not rely on local developer paths**.

The repository now vendors the Excel data:

- `./masterfiles/` (workbooks: Asset/Core/Maintenance/Workflow/Role_Permission...)
- `./records/` (the larger Excel dump folder, previously drive-download...)

Set one of the following:

- `EAM_MASTERFILES_DIR`
  - Directory that contains the workbooks.
  - Must include:
    - `Asset Masterfiles.xlsx`
    - `Core Masterfiles.xlsx`

Or override individual workbook paths:

- `EAM_ASSET_MASTERFILES`
- `EAM_CORE_MASTERFILES`
- `EAM_WORKFLOW_XLSX` (optional override for Workflow.xlsx)

If none are provided, it defaults to a `masterfiles/` directory adjacent to the repo (if present).

### Application bootstrap seeding

The app can run `app/core/seed.py` on startup if `RUN_SEEDS` is enabled in your environment.
This is controlled in `app/main.py`:

- If `settings.RUN_SEEDS` is true, the server will execute `run_seeds(db)` during startup.

For production servers, you typically want `RUN_SEEDS=false` and run explicit seed scripts instead.

## 3) Recommended Seeding Order

Run these steps **in this exact order**:

Important:

- Run these commands from the `backend/` directory so `backend/.env` is loaded correctly.

### Step A: (Optional) Clean existing business master/transaction data

Use the safe cleaner that deletes in dependency order without elevated privileges:

```bash
python clean_seeded_simple.py
```

Notes:

- This targets operational/business tables that were seeded from Excel.
- It intentionally avoids deleting auth/users/roles and workflow config.

### Step B: Seed masterfiles from Excel workbooks (authoritative)

```bash
python seed_masterfiles_workbooks.py
```

This will seed worksheets one-by-one in dependency order, using update-if-exists behavior.

### Step C: Reset global workflow catalog (states & actions)

If you need to replace all workflow states/actions with the canonical lists:

```bash
python reset_workflow_catalog.py
```

This will:

- delete `workflow_transitions`, `workflow_state_links`, and `workflows`
- delete all rows in `workflow_states` and `workflow_actions`
- insert the canonical states/actions set

### Step D: Seed entity workflows (workflows + state links + transitions)

Seeds `workflows`, `workflow_state_links`, and `workflow_transitions` from `Workflow.xlsx`.

```bash
python seed_workflows_from_excel.py
```

### Step E: Seed roles and CRUD permissions (from Role_Permission_reorganized.xlsx)

```bash
python seed_roles_permissions.py
```

Notes:

- Seeds `roles` and `entity_permissions` from the reorganized matrix workbook.
- Only CRUD is applied (`Read/Create/Write/Delete`). Other permission types are ignored.
- `SystemManager` is enforced to have full CRUD across all registered entities.

### Step F: (Optional) Application bootstrap seeds

If you want the app’s bootstrap seeds (roles/users/etc.) run:

```bash
python - <<'PY'
import asyncio
from app.core.database import async_session_maker
from app.core.seed import run_seeds

async def main():
    async with async_session_maker() as db:
        await run_seeds(db)

asyncio.run(main())
PY
```

## 4) Verification Queries

Run these checks after Step B:

```bash
python - <<'PY'
import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker

async def main():
    async with async_session_maker() as db:
        checks = [
            ("site missing site_name", "SELECT COUNT(*) FROM site WHERE site_name IS NULL"),
            ("department missing department_name", "SELECT COUNT(*) FROM department WHERE department_name IS NULL"),
            ("system missing system_type_name", "SELECT COUNT(*) FROM system WHERE system_type IS NOT NULL AND system_type_name IS NULL"),
            ("locations missing location_type_name", "SELECT COUNT(*) FROM location WHERE location_type IS NOT NULL AND location_type_name IS NULL"),
            ("assets missing asset_class_name", "SELECT COUNT(*) FROM asset WHERE asset_class IS NOT NULL AND asset_class_name IS NULL"),
        ]
        for label, sql in checks:
            res = await db.execute(text(sql))
            print(label + ":", res.scalar())

asyncio.run(main())
PY
```

## 5) What to keep as the single source of truth

- `seed_masterfiles_workbooks.py` is the authoritative masterfiles seeder.
- `clean_seeded_simple.py` is the safe cleaner for Excel-seeded business data.
- `reset_workflow_catalog.py` is the canonical workflow catalog reset.

Other one-off `seed_*.py` scripts should be considered deprecated and removed once you confirm you no longer need them.
