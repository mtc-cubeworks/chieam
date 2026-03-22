# Forge CLI Guide

The **Forge CLI** (`forge.py`) is the primary tool for managing the modular entity system. It enforces the "Code-First" architecture where Python models are the source of truth.

## Location

`backend/app/forge.py`

## Core Philosophy

1.  **Code-First**: You define the data structure in Python Models (`models/*.py`).
2.  **Sync-Driven**: JSON metadata (`entities/*.json`) is auto-generated from Python models.
3.  **Modular**: All entities belong to a specific module in `app/modules/{module_name}`.

## Commands

### 1. Create a New Entity

Scaffolds a new entity with a Model, JSON definition, and directory structure.

```bash
python -m app.forge new-entity <name> \
    --module <module_name> \
    --fields "<field_definitions>" \
    --naming "<naming_pattern>"
```

**Arguments:**

- `name`: The snake_case name of the entity (e.g., `work_order`).
- `--module`: Target module (e.g., `maintenance`). Creates folder if missing.
- `--fields`: Comma-separated list of `name:type:link_target`.
  - Types: `string`, `int`, `float`, `boolean`, `date`, `datetime`, `text`, `link`.
  - Example: `description:text,asset_id:link:asset,cost:float`
- `--naming`: ID generation pattern (e.g., `WO-{####}` -> WO-0001).

**Example:**

```bash
python -m app.forge new-entity project \
    --module project_management \
    --fields "name:string,budget:float,manager_id:link:user" \
    --naming "PRJ-{####}"
```

### 2. Sync Metadata (Crucial)

Updates the JSON metadata files (`entities/*.json`) to match your Python Models. Run this whenever you modify a `.py` model file.

```bash
python -m app.forge sync-meta
```

**What it does:**

1.  Scans all `app/modules/*/models/*.py`.
2.  Reads the SQLAlchemy columns (types, defaults, foreign keys).
3.  Updates the corresponding `.json` file fields.
4.  Ensures Frontend and Backend are in sync.

### 3. Database Migrations

Manages the database schema changes.

```bash
# 1. Create a migration file (after changing a model)
python -m app.forge migrate --message "Added status field to project"

# 2. Apply the migration to the database
python -m app.forge upgrade
```

### 4. Seed Data

Populates the database with initial data defined in `app/core/seed.py`.

```bash
python -m app.forge seed
```

### 5. Generate TypeScript Types

Generates frontend TypeScript interfaces based on the current metadata.

```bash
python -m app.forge generate-types
```

## Developer Workflow

1.  **Scaffold**: Use `new-entity` to create the files.
2.  **Refine**: Edit the generated Python Model in `app/modules/{module}/models/{entity}.py`.
    - Add custom SQLAlchemy columns.
    - Add helper methods.
3.  **Sync**: Run `sync-meta` to update the JSON.
4.  **Migrate**: Run `migrate` and `upgrade` to update the DB.
5.  **Develop**: The entity is now available in the generic API and Frontend.

## Module Structure

Entities are created in:

```text
backend/app/modules/{module_name}/
├── models/         # Python SQLAlchemy Models (Source of Truth)
├── entities/       # JSON Metadata (Generated/Synced)
└── apis/           # Custom API Logic (Optional)
```
