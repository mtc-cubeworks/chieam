# Forge CLI Tool Documentation

The Forge CLI (`forge.py`) provides commands for entity management, database operations, and code generation.

## Installation

The CLI is part of the backend application. No separate installation required.

```bash
cd backend
python -m app.forge --help
```

## Commands

### `new-entity` - Create a New Entity

Creates a complete entity with all required files in the modular structure.

```bash
python -m app.forge new-entity <name> [options]
```

**Arguments:**

| Argument | Description                                    |
| -------- | ---------------------------------------------- |
| `name`   | Entity name in snake_case (e.g., `work_order`) |

**Options:**

| Option          | Description                      | Default                  |
| --------------- | -------------------------------- | ------------------------ |
| `--label`       | Display label                    | Auto-generated from name |
| `--naming`      | ID format (e.g., `WO-{####}`)    | Auto-generated prefix    |
| `--module`      | Module name                      | `core`                   |
| `--title-field` | Field used as record title       | `name`                   |
| `--fields`      | Field definitions                | None                     |
| `--in-sidebar`  | Show in sidebar navigation       | False                    |
| `--no-model`    | Skip SQLAlchemy model generation | False                    |
| `--force`       | Overwrite existing files         | False                    |

**Field Format:**

```
name:type:link_entity
```

- `name` - Field name (snake_case)
- `type` - Field type: `string`, `text`, `int`, `float`, `boolean`, `date`, `datetime`, `select`, `link`
- `link_entity` - For `link` type only, the target entity name

**Examples:**

```bash
# Simple entity
python -m app.forge new-entity asset --naming "AST-{####}" --module asset_management --in-sidebar

# Entity with fields
python -m app.forge new-entity work_order \
  --naming "WO-{####}" \
  --module maintenance \
  --fields "asset_id:link:asset,description:text,priority:select,due_date:date" \
  --in-sidebar

# Overwrite existing
python -m app.forge new-entity todo --force
```

**Generated Files:**

```
backend/app/modules/{module}/
├── __init__.py           # Module registration (created if missing)
├── entities/
│   └── {entity}/
│       ├── {entity}.json # Metadata definition
│       └── {entity}.py   # Custom hooks/API template
└── models/
    └── {entity}.py       # SQLAlchemy model
```

---

### `init-db` - Initialize Database

Creates all database tables without using Alembic migrations. Useful for development.

```bash
python -m app.forge init-db
```

**Note:** This drops and recreates tables. Use `migrate` + `upgrade` for production.

---

### `migrate` - Generate Migration

Creates a new Alembic migration based on model changes.

```bash
python -m app.forge migrate --message "Add work_order table"
```

**Options:**

| Option            | Description           |
| ----------------- | --------------------- |
| `-m`, `--message` | Migration description |

---

### `upgrade` - Run Migrations

Applies pending Alembic migrations to the database.

```bash
python -m app.forge upgrade
```

---

### `seed` - Seed Initial Data

Populates the database with initial data (roles, default users, etc.).

```bash
python -m app.forge seed
```

---

### `sync-meta` - Sync Entity Metadata

Regenerates entity JSON files from existing SQLAlchemy models. This command scans all modules for entity JSON files and updates their field definitions based on the corresponding SQLAlchemy model columns.

```bash
python -m app.forge sync-meta
```

**What it does:**

- Scans `app/modules/*/entities/*/` for JSON files
- Finds matching SQLAlchemy model by entity name
- Updates field definitions (type, required, etc.) from model columns
- Preserves existing metadata (labels, options, link_entity)
- Detects foreign keys and converts them to `link` fields

**Use case:** After modifying a SQLAlchemy model (adding/removing columns), run this to keep the JSON metadata in sync.

---

### `generate-types` - Generate TypeScript Types

Creates TypeScript interfaces from entity metadata for the frontend.

```bash
python -m app.forge generate-types
```

**Output:** `frontend/src/generated/entity-types.ts`

---

### `list-entities` - List All Entities

Shows all registered entities with their module and naming configuration.

```bash
python -m app.forge list-entities
```

**Output:**

```
📋 Registered Entities (4):

Name                 Label                Module          Naming
----------------------------------------------------------------------
todo                 Todo                 core            TODO-{...}
todo_comment         Todo Comment         core            TC-{...}
user                 User                 admin           -
role                 Role                 admin           -
```

---

## Modular System

Entities are organized into modules for better organization and potential "app" installation:

```
app/modules/
├── core/                    # System entities
│   ├── entities/
│   │   ├── todo/
│   │   └── todo_comment/
│   └── models/
├── asset_management/        # Asset-related entities
│   ├── entities/
│   │   ├── asset/
│   │   └── asset_class/
│   └── models/
└── maintenance/             # Maintenance entities
    ├── entities/
    │   └── work_order/
    └── models/
```

**Module Structure:**

Each module has:

- `__init__.py` - Module metadata (MODULE_NAME, MODULE_LABEL)
- `entities/` - Entity metadata and hooks
- `models/` - SQLAlchemy models

---

## Entity JSON Schema

```json
{
  "name": "work_order",
  "label": "Work Order",
  "module": "maintenance",
  "table_name": "work_order",
  "title_field": "description",
  "in_sidebar": 1,
  "naming": "WO-{####}",
  "links": [
    {
      "entity": "work_order_activity",
      "fk_field": "work_order_id",
      "label": "Activities"
    }
  ],
  "fields": [
    {
      "name": "asset_id",
      "label": "Asset",
      "field_type": "link",
      "link_entity": "asset",
      "required": 1,
      "in_list_view": 1
    },
    {
      "name": "description",
      "label": "Description",
      "field_type": "text",
      "required": 1
    },
    {
      "name": "status",
      "label": "Status",
      "field_type": "select",
      "options": ["draft", "open", "in_progress", "completed"],
      "default": "draft",
      "in_list_view": 1
    }
  ],
  "rbac": {
    "SystemManager": ["*"],
    "Technician": ["read", "update"]
  }
}
```

**Important:** System fields (`id`, `created_at`, `updated_at`) are NOT included in the JSON. They are automatically managed by `BaseModel`.

---

## ID Generation

IDs are human-readable codes, NOT UUIDs:

| Entity     | ID Format     | Examples             |
| ---------- | ------------- | -------------------- |
| Asset      | `AST-{####}`  | AST-0001, AST-0002   |
| Work Order | `WO-{####}`   | WO-0001, WO-0002     |
| Todo       | `TODO-{####}` | TODO-0001, TODO-0002 |

The `Series` table tracks the current sequence for each prefix.

---

## Workflow

After creating an entity:

1. **Review generated files** - Check JSON metadata and model
2. **Add custom fields** - Edit the JSON file if needed
3. **Run migration** - `python -m app.forge migrate -m "Add {entity}"`
4. **Apply migration** - `python -m app.forge upgrade`
5. **Restart server** - The entity will be auto-discovered

---

## Troubleshooting

**Entity not appearing in sidebar:**

- Check `in_sidebar: 1` in JSON
- Verify entity is in a valid module directory
- Restart the backend server

**Model import errors:**

- Ensure `from app.core.base_model import BaseModel` is correct
- Check all field types have proper SQLAlchemy imports

**Naming not working:**

- Verify `naming` format: `PREFIX-{####}`
- Check `Series` table has the prefix entry
