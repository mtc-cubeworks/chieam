# Backend Development Tools & Patterns

**Purpose:** Comprehensive guide for querying, testing, CLI tools, and development patterns in the EAM FastAPI backend.

---

## Document Query Helpers

**Location:** `app.services.document`

Frappe-inspired helpers for entity operations:

### Core Functions

```python
from app.services.document import (
    get_doc,           # Fetch single record by ID
    get_list,          # Query multiple records with filters
    get_value,         # Get specific field value(s)
    new_doc,           # Create new document instance
    save_doc,          # Save (insert/update) document
    delete_doc,        # Delete document by ID
    apply_workflow_state,  # Change workflow state (validated)
)
```

### Query Patterns

#### Get Single Record

```python
# Fetch by ID
asset = await get_doc("asset", "AST-0001", db)

# Returns None if not found
pr = await get_doc("purchase_request", "PR-9999", db)
if not pr:
    return {"status": "error", "message": "Not found"}
```

#### Query Multiple Records

```python
# Simple filter
lines = await get_list("purchase_request_line", {"purchase_request": pr_id}, db)

# Multiple filters (AND condition)
active_assets = await get_list("asset", {"status": "Active", "site": "SITE-001"}, db)

# Fetch specific fields only (performance)
names = await get_list("employee", {}, db, fields=["id", "name"])

# Return as model objects (for updates)
docs = await get_list("asset", {"site": site_id}, db, as_dict=False)
for doc in docs:
    doc.status = "Inactive"
    await save_doc(doc, db)
```

#### Get Specific Field Values

```python
# Single field, single record
asset_name = await get_value("asset", "AST-0001", "name", db)

# Multiple fields, single record
values = await get_value("asset", "AST-0001", ["name", "status"], db)
# Returns: {"name": "Pump A", "status": "Active"}

# Field from filtered query
site_name = await get_value("site", {"code": "MAIN"}, "name", db)
```

#### Create New Records

```python
# Create with initial values
doc = await new_doc("asset", db,
    name="New Asset",
    asset_class="AC-001",
    site="SITE-001",
    workflow_state="draft"  # Set initial state
)
await save_doc(doc, db)

# Create child record
line = await new_doc("purchase_request_line", db,
    purchase_request=pr_id,
    item="ITEM-001",
    qty=10
)
await save_doc(line, db)
```

#### Update Existing Records

```python
# Fetch → modify → save
doc = await get_doc("asset", asset_id, db)
doc.status = "Inactive"
doc.notes = "Decommissioned"
await save_doc(doc, db)

# Bulk update pattern
assets = await get_list("asset", {"site": old_site_id}, db, as_dict=False)
for asset in assets:
    asset.site = new_site_id
    await save_doc(asset, db, commit=False)  # Batch commit
await db.commit()
```

#### Delete Records

```python
# Delete by ID
await delete_doc("asset", "AST-0001", db)

# Delete with validation
doc = await get_doc("purchase_request", pr_id, db)
if doc.workflow_state != "draft":
    return {"status": "error", "message": "Cannot delete non-draft PR"}
await delete_doc("purchase_request", pr_id, db)
```

---

## Testing Patterns

### Unit Tests (Business Logic)

**Location:** `backend/tests/`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.modules.purchasing_stores.apis.purchase_request import approve_request

@pytest.mark.asyncio
async def test_approve_request_success():
    # Arrange
    mock_db = AsyncMock()
    mock_user = {"id": "USR-001", "name": "Admin"}
    doc = {"id": "PR-001", "workflow_state": "pending_approval"}

    # Act
    result = await approve_request(doc, mock_db, mock_user)

    # Assert
    assert result["status"] == "success"
    assert "approved" in result["message"].lower()

@pytest.mark.asyncio
async def test_approve_request_invalid_state():
    mock_db = AsyncMock()
    mock_user = {"id": "USR-001"}
    doc = {"id": "PR-001", "workflow_state": "draft"}  # Wrong state

    result = await approve_request(doc, mock_db, mock_user)

    assert result["status"] == "error"
    assert "cannot approve" in result["message"].lower()
```

### Integration Tests (Routes)

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_purchase_request():
    # Login first
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Create PR
    response = client.post("/api/purchase_request",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test PR",
            "department": "DEPT-001",
            "workflow_state": "draft"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test PR"
    assert data["workflow_state"] == "draft"

def test_workflow_transition():
    # ... login and create PR ...

    # Submit for approval
    response = client.post(f"/api/purchase_request/{pr_id}/workflow",
        headers={"Authorization": f"Bearer {token}"},
        json={"action": "Submit for Approval"}
    )

    assert response.status_code == 200
    assert response.json()["workflow_state"] == "pending_approval"
```

### Workflow Tests (E2E)

```python
@pytest.mark.asyncio
async def test_purchase_request_full_workflow(db):
    from app.services.document import new_doc, save_doc, apply_workflow_state

    # Create PR in draft
    pr = await new_doc("purchase_request", db,
        title="Test PR",
        department="DEPT-001",
        workflow_state="draft"
    )
    await save_doc(pr, db)

    # Submit for approval
    result = await apply_workflow_state("purchase_request", pr, "submit", db)
    assert result["status"] == "success"
    assert pr.workflow_state == "pending_approval"

    # Approve
    result = await apply_workflow_state("purchase_request", pr, "approve", db)
    assert result["status"] == "success"
    assert pr.workflow_state == "approved"

    # Verify lines also approved (cascade)
    lines = await get_list("purchase_request_line", {"purchase_request": pr.id}, db)
    for line in lines:
        assert line["workflow_state"] == "approved"
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_purchase_request.py

# Specific test
pytest tests/test_purchase_request.py::test_approve_request_success

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only marked tests
pytest -m "workflow"
```

---

## CLI Tools

### Forge CLI

See `forge-cli.md` for full reference. Quick commands:

```bash
# Sync everything
forge sync

# Check DB status
forge migrate --status

# Interactive Python shell
forge console

# Run seed data
forge seed
```

### Alembic (Direct)

```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Generate migration (manual)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show SQL without applying
alembic upgrade head --sql
```

### Pytest (Testing)

```bash
# Run all tests
pytest

# Run with markers
pytest -m "unit"
pytest -m "integration"
pytest -m "workflow"

# Run specific module
pytest tests/test_purchasing_stores/

# Parallel execution (faster)
pytest -n auto

# Generate coverage report
pytest --cov=app --cov-report=term-missing
```

### Database CLI

```bash
# Connect to DB (psql)
psql $DATABASE_URL

# Dump schema
pg_dump -s $DATABASE_URL > schema.sql

# Dump data
pg_dump -a $DATABASE_URL > data.sql

# Restore
psql $DATABASE_URL < backup.sql
```

---

## Development Patterns

### Field Access (Frappe-style)

```python
# ✅ CORRECT: Simple and readable
purchase_request = doc.get("purchase_request")
item_name = doc.get("item_name", "Default Item")

# ❌ WRONG: Overly complex
purchase_request_id = getattr(doc, "purchase_request", None) or doc.get("purchase_request") if hasattr(doc, "get") else None
```

### Error Handling (Mandatory)

```python
# ✅ CORRECT: Always rollback on error
try:
    doc = await get_doc("asset", asset_id, db)
    doc.status = "Inactive"
    await save_doc(doc, db)
    await db.commit()
    return {"status": "success", "message": "Asset deactivated"}
except Exception as e:
    await db.rollback()
    return {"status": "error", "message": f"Failed: {str(e)}"}

# ❌ WRONG: No rollback (leaves DB inconsistent)
try:
    # ... operations ...
    await db.commit()
except Exception as e:
    return {"status": "error", "message": str(e)}  # Missing rollback!
```

### Validation Patterns

```python
# ✅ CORRECT: Validate early, fail fast
purchase_request = doc.get("purchase_request")
if not purchase_request:
    return {"status": "error", "message": "Purchase Request is required"}

item = doc.get("item")
if not item:
    return {"status": "error", "message": "Item is required"}

qty = doc.get("qty", 0)
if qty <= 0:
    return {"status": "error", "message": "Quantity must be positive"}

# Now proceed with business logic
```

### Hook Return Format

```python
# ✅ CORRECT: Consistent dict responses
return {"status": "success", "message": "Operation completed"}
return {"status": "error", "message": "Validation failed"}

# For record-creating actions
return {
    "status": "success",
    "message": "Record created",
    "action": "generate_id",
    "path": f"/purchase_order/{po_id}"
}

# ❌ WRONG: Inconsistent formats
return doc, ["error message"]  # Wrong
return True  # Wrong
return "Success"  # Wrong
```

### Batch Operations

```python
# ✅ CORRECT: Batch commit for performance
lines = await get_list("purchase_request_line", {"purchase_request": pr_id}, db, as_dict=False)
for line in lines:
    line.workflow_state = "approved"
    await save_doc(line, db, commit=False)  # Don't commit each iteration

await db.commit()  # Single commit at end

# ❌ WRONG: Commit inside loop (slow)
for line in lines:
    line.workflow_state = "approved"
    await save_doc(line, db)  # Commits every iteration
```

---

## Performance Tips

### Query Optimization

```python
# ✅ CORRECT: Fetch only needed fields
names = await get_list("employee", {}, db, fields=["id", "name"])

# ❌ WRONG: Fetch all fields when only need few
employees = await get_list("employee", {}, db)  # Fetches everything
```

### Eager Loading (Avoid N+1)

```python
# ✅ CORRECT: Fetch related records in batch
pr_ids = [line["purchase_request"] for line in lines]
prs = await get_list("purchase_request", {"id": ("in", pr_ids)}, db)
pr_map = {pr["id"]: pr for pr in prs}

for line in lines:
    pr = pr_map.get(line["purchase_request"])
    # Use pr data

# ❌ WRONG: Query inside loop (N+1 problem)
for line in lines:
    pr = await get_doc("purchase_request", line["purchase_request"], db)  # N queries
```

### Caching (When Appropriate)

```python
# Cache static/rarely-changing data
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_site_name(site_id: str, db) -> str:
    return await get_value("site", site_id, "name", db)
```

---

## Common Pitfalls

### 1. Over-Engineering Field Access

```python
# ❌ WRONG: Complex chains
value = getattr(doc, "field", None) or doc.get("field") if hasattr(doc, "get") else None

# ✅ CORRECT: Simple
value = doc.get("field")
```

### 2. Missing Rollback

```python
# ❌ WRONG: No rollback on error
try:
    await save_doc(doc, db)
    await db.commit()
except Exception as e:
    return {"status": "error", "message": str(e)}  # DB left dirty!

# ✅ CORRECT: Always rollback
try:
    await save_doc(doc, db)
    await db.commit()
except Exception as e:
    await db.rollback()
    return {"status": "error", "message": str(e)}
```

### 3. Direct Workflow State Assignment

```python
# ❌ WRONG: Bypasses validation
doc.workflow_state = "approved"
await save_doc(doc, db)

# ✅ CORRECT: Use apply_workflow_state
result = await apply_workflow_state("entity", doc, "approve", db)
if result["status"] == "error":
    await db.rollback()
    return result
```

### 4. Inconsistent Return Formats

```python
# ❌ WRONG: Mixed formats
if error:
    return False
else:
    return {"status": "success"}

# ✅ CORRECT: Consistent dicts
if error:
    return {"status": "error", "message": "Failed"}
else:
    return {"status": "success", "message": "Done"}
```

---

## Naming Conventions

- **Functions:** `generate_row_number`, `validate_inventory`, `approve_request`
- **Variables:** `purchase_request_id`, `existing_lines`, `asset_doc`
- **Parameters:** `doc`, `db`, `user`, `ctx` (Frappe-style)
- **Constants:** `RESERVED_TABLES`, `BASEMODEL_FIELDS`

---

## File Organization

```
app/modules/{module}/
├── hooks.py              # Simple hooks (< 50 lines)
├── workflow_router.py    # Workflow dispatch
└── apis/                 # Complex business logic
    └── {entity}.py       # Multi-function logic

tests/
├── test_{module}/        # Module-specific tests
│   ├── test_{entity}.py
│   └── test_workflow.py
└── conftest.py           # Shared fixtures
```

**Guidelines:**

- Keep simple hooks in `hooks.py` (no separate API file needed)
- Use `apis/{entity}.py` only for complex logic with multiple functions
- Import document helpers at top: `from app.services.document import get_doc, get_list`

---

## Quick Reference

| Task                    | Command/Pattern                                           |
| ----------------------- | --------------------------------------------------------- |
| **Query single record** | `await get_doc("entity", id, db)`                         |
| **Query multiple**      | `await get_list("entity", filters, db)`                   |
| **Create record**       | `await new_doc("entity", db, **kwargs)` + `save_doc()`    |
| **Update record**       | `get_doc()` → modify → `save_doc()`                       |
| **Delete record**       | `await delete_doc("entity", id, db)`                      |
| **Change workflow**     | `await apply_workflow_state("entity", doc, "action", db)` |
| **Run tests**           | `pytest` or `pytest tests/test_file.py`                   |
| **Sync DB**             | `forge sync`                                              |
| **Check migrations**    | `forge migrate --status`                                  |
| **Interactive shell**   | `forge console`                                           |
