# Backend Coding Standards

## Terminology Standards

### Use `doc` for Documents

Always use `doc` to refer to document objects, whether they are dictionaries (before save) or model instances (after save).

| ❌ Avoid | ✅ Use |
|---------|--------|
| `record` | `doc` |
| `data` (for documents) | `doc` |
| `item` | `doc` |
| `entity_data` | `doc` |

**Examples**:

```python
# ✅ Correct
async def populate_asset_names(doc: dict, db: AsyncSession) -> dict:
    if doc.get("asset_class"):
        asset_class = await get_doc("asset_class", doc["asset_class"], db)
        if asset_class:
            doc["asset_class_name"] = asset_class.name
    return doc

# ✅ Correct
async def check_asset_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    if action == "activate":
        cost = getattr(doc, "cost", None)
        if cost is None or cost <= 0:
            return {"status": "error", "message": "Cost required"}
    return {"status": "success"}

# ❌ Avoid
async def populate_asset_names(data: dict, db: AsyncSession) -> dict:
    # Don't use 'data' for documents
    pass

# ❌ Avoid
async def check_asset_workflow(record: Any, action: str, db: AsyncSession, user: Any) -> dict:
    # Don't use 'record' for documents
    pass
```

---

## Document Service Usage

### Always Use Helpers in Business Logic

Never use direct SQLAlchemy imports or queries in business logic files (`app/modules/*/apis/*.py`).

**❌ Don't Do This**:

```python
from sqlalchemy import select
from app.modules.asset_management.models.asset import Asset

async def my_hook(doc, ctx):
    result = await ctx.db.execute(select(Asset).where(Asset.id == doc.parent))
    parent = result.scalar_one_or_none()
```

**✅ Do This Instead**:

```python
from app.services.document import get_doc

async def my_hook(doc, ctx):
    parent = await get_doc("asset", doc.parent, ctx.db)
```

### Import Pattern

```python
# Standard imports for business logic
from app.services.document import get_doc, get_value, get_list, new_doc, save_doc, delete_doc, get_meta
```

---

## Hook Function Signatures

### Before Save Hooks

```python
async def my_before_save_hook(doc: dict, db: AsyncSession) -> dict:
    """
    Before save hooks receive a dict and return a dict.
    
    Args:
        doc: Dictionary of field values (incoming data)
        db: Database session
        
    Returns:
        Modified doc dictionary
    """
    # Modify doc
    doc["computed_field"] = "value"
    return doc
```

### After Save Hooks

```python
async def my_after_save_hook(doc: Any, ctx: HookContext) -> None:
    """
    After save hooks receive a model instance.
    
    Args:
        doc: SQLAlchemy model instance (saved record)
        ctx: Hook context with db, user, etc.
    """
    # Create related records
    child = await new_doc("child_entity", ctx.db, parent=doc.id)
    await save_doc(child, ctx.db)
```

### Workflow Hooks

```python
async def my_workflow_hook(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Workflow hooks receive a model instance and return a status dict.
    
    Args:
        doc: SQLAlchemy model instance
        action: Workflow action slug
        db: Database session
        user: Current user object
        
    Returns:
        Status dict with "status" key ("success" or "error")
    """
    if action == "approve":
        # Validation logic
        if not doc.approved_by:
            return {
                "status": "error",
                "message": "Approver required",
                "errors": {"approved_by": "This field is required"}
            }
    
    return {"status": "success"}
```

---

## File Organization

### Module Structure

```
app/modules/{module_name}/
├── models/          # SQLAlchemy models only
│   └── entity.py
├── apis/            # Business logic (hooks)
│   ├── __init__.py
│   └── entity.py    # Hook functions for this entity
└── schemas/         # Pydantic schemas (if needed)
    └── entity.py
```

### Business Logic Files (`apis/`)

Keep business logic in `apis/` folder, separate from models.

```python
# app/modules/asset_management/apis/asset.py

"""
Asset Entity Business Logic

Hook functions for Asset entity lifecycle events.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, new_doc, save_doc


async def populate_asset_names(doc: dict, db: AsyncSession) -> dict:
    """Before save: Populate denormalized name fields."""
    # Implementation
    return doc


async def check_asset_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """Workflow: Validate and handle asset workflow transitions."""
    # Implementation
    return {"status": "success"}
```

---

## Error Handling

### Return Error Dicts

Always return structured error responses from workflow hooks.

```python
async def my_workflow_hook(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    # Validation error
    if not doc.required_field:
        return {
            "status": "error",
            "message": "Validation failed",
            "errors": {"required_field": "This field is required"}
        }
    
    # Business logic error
    if doc.status == "locked":
        return {
            "status": "error",
            "message": "Cannot modify locked document"
        }
    
    # Success
    return {"status": "success"}
```

### Handle None Returns

Always check for None when using document helpers.

```python
# ✅ Good
asset = await get_doc("asset", asset_id, db)
if not asset:
    return {"status": "error", "message": "Asset not found"}

# ✅ Good
activity_type = await get_value("request_activity_type", filters, "*", db)
if not activity_type:
    return {"status": "error", "message": "Activity type not found"}
```

---

## Batch Operations

### Use `commit=False` for Multiple Saves

```python
async def copy_multiple_records(doc, ctx):
    """Copy multiple child records."""
    
    # Get source records
    source_records = await get_list("child_entity", {"parent": doc.source_id}, db=ctx.db, as_dict=False)
    
    # Create copies (don't commit each one)
    for source in source_records:
        new_record = await new_doc("child_entity", ctx.db,
            parent=doc.id,
            field1=source.field1,
            field2=source.field2
        )
        await save_doc(new_record, ctx.db, commit=False)
    
    # Commit once at the end
    if source_records:
        await ctx.db.commit()
```

---

## Comments and Documentation

### Docstring Format

```python
async def my_function(doc: Any, db: AsyncSession) -> dict:
    """
    Brief one-line description.
    
    Longer description if needed. Explain the business logic,
    not just what the code does.
    
    Args:
        doc: Document instance or dict
        db: Database session
        
    Returns:
        Status dict or modified doc
        
    Mirrors: check_asset_state() from Frappe (if applicable)
    """
    pass
```

### Inline Comments

Use comments to explain **why**, not **what**.

```python
# ✅ Good - explains why
# Skip copying if properties already exist (avoid duplicates on update)
existing = await get_list("asset_class_property", {"asset_class": doc.id}, db=db)
if existing:
    return

# ❌ Bad - just repeats the code
# Get existing properties
existing = await get_list("asset_class_property", {"asset_class": doc.id}, db=db)
```

---

## Testing Considerations

### Keep Functions Testable

```python
# ✅ Good - easy to test
async def calculate_total_cost(doc: dict) -> float:
    """Pure calculation function."""
    return doc.get("unit_cost", 0) * doc.get("quantity", 0)

async def my_hook(doc: dict, db: AsyncSession) -> dict:
    """Hook that uses pure function."""
    doc["total_cost"] = calculate_total_cost(doc)
    return doc

# ❌ Harder to test - everything in one function
async def my_hook(doc: dict, db: AsyncSession) -> dict:
    doc["total_cost"] = doc.get("unit_cost", 0) * doc.get("quantity", 0)
    return doc
```

---

## Performance

### Use `get_list` with Filters

```python
# ✅ Good - filter at database level
active_assets = await get_list(
    "asset", 
    {"workflow_state": "active", "site": "SITE-001"}, 
    db=db
)

# ❌ Bad - fetch all then filter in Python
all_assets = await get_list("asset", db=db)
active_assets = [a for a in all_assets if a["workflow_state"] == "active"]
```

### Limit Results When Possible

```python
# ✅ Good - limit at database
recent_orders = await get_list(
    "work_order", 
    {"site": "SITE-001"}, 
    db=db,
    limit=10,
    order_by="created_at"
)
```

---

## Common Patterns

### Pattern: Denormalization (Before Save)

```python
async def populate_names(doc: dict, db: AsyncSession) -> dict:
    """Populate denormalized name fields from linked records."""
    
    if doc.get("parent_id"):
        parent = await get_doc("parent_entity", doc["parent_id"], db)
        if parent:
            doc["parent_name"] = parent.name
    
    return doc
```

### Pattern: Copy Child Records (After Save)

```python
async def copy_children(doc, ctx):
    """Copy child records from parent."""
    
    if not doc.parent_id:
        return
    
    # Check if already copied
    existing = await get_list("child_entity", {"parent": doc.id}, db=ctx.db)
    if existing:
        return
    
    # Get source children
    source_children = await get_list(
        "child_entity", 
        {"parent": doc.parent_id}, 
        db=ctx.db,
        as_dict=False
    )
    
    # Copy each child
    for child in source_children:
        new_child = await new_doc("child_entity", ctx.db,
            parent=doc.id,
            field1=child.field1
        )
        await save_doc(new_child, ctx.db, commit=False)
    
    if source_children:
        await ctx.db.commit()
```

### Pattern: Create Related Records (Workflow)

```python
async def _handle_submit_action(doc: Any, db: AsyncSession, user: Any) -> dict:
    """Create approval request when document is submitted."""
    
    # Create approval request
    approval = await new_doc("approval_request", db,
        document_type="work_order",
        document_id=doc.id,
        requested_by=user.id,
        workflow_state="pending"
    )
    await save_doc(approval, db)
    
    return {
        "status": "success",
        "message": "Approval request created",
        "action": "generate_id",
        "path": f"/approval_request/{approval.id}",
        "data": {"approval_request_id": approval.id}
    }
```

---

## Migration Checklist

When refactoring existing code:

- [ ] Replace `record` → `doc`
- [ ] Replace `data` → `doc` (for documents)
- [ ] Remove direct model imports
- [ ] Replace `select()` with `get_doc()` or `get_list()`
- [ ] Replace `db.add()` + manual ID with `new_doc()`
- [ ] Replace `db.add()` + `db.commit()` with `save_doc()`
- [ ] Add proper type hints
- [ ] Add docstrings
- [ ] Test the refactored code

---

## Related Documentation

- `DOCUMENT_SERVICE.md` - Document helper reference
- `ARCHITECTURE.md` - System architecture
- `app/services/hooks.py` - Central hooks router
