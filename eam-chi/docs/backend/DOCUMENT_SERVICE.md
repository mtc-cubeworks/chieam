# Document Service - Frappe-like Helpers

## Overview

The Document Service provides Frappe-style helpers for database operations, eliminating boilerplate SQLAlchemy code and making business logic more readable and maintainable.

**Location**: `app/services/document.py`

## Core Philosophy

- **No direct model imports** in business logic
- **Consistent terminology**: Use `doc` instead of `record` or `data`
- **Dynamic model resolution**: Models are resolved by entity name at runtime
- **Auto ID generation**: Naming service integration for automatic ID generation

## Available Helpers

### 1. `get_meta(entity)`

Get entity metadata (non-async).

```python
from app.services.document import get_meta

meta = get_meta("asset")
# Returns: EntityMeta with fields, naming config, etc.
```

**Use Cases**:
- Check if entity has naming enabled
- Get field definitions
- Access entity configuration

---

### 2. `get_doc(entity, id, db, as_dict=False)`

Fetch a single document by ID.

```python
from app.services.document import get_doc

# Get as model instance
asset = await get_doc("asset", "AST-0001", db)
print(asset.asset_tag)

# Get as dict
asset_dict = await get_doc("asset", "AST-0001", db, as_dict=True)
print(asset_dict["asset_tag"])
```

**Parameters**:
- `entity`: Entity name (e.g., "asset", "work_order")
- `id`: Document ID
- `db`: AsyncSession
- `as_dict`: Return dict instead of model instance

**Returns**: Model instance, dict, or None

---

### 3. `get_value(entity, filters, fieldname, db, as_dict=False)`

Get specific field value(s) from a document (like `frappe.db.get_value`).

```python
from app.services.document import get_value

# Get single field by ID
status = await get_value("asset", "AST-0001", "workflow_state", db)

# Get single field by filters
activity_type = await get_value(
    "request_activity_type", 
    {"menu": "Asset", "type": "Inspect"}, 
    "id", 
    db
)

# Get all fields as dict
doc_data = await get_value("asset", "AST-0001", "*", db)

# Get multiple fields as tuple
name, status = await get_value("asset", "AST-0001", ["name", "workflow_state"], db)

# Get multiple fields as dict
fields = await get_value("asset", "AST-0001", ["name", "workflow_state"], db, as_dict=True)
```

**Parameters**:
- `entity`: Entity name
- `filters`: Document ID (str) or filter dict
- `fieldname`: Field name, list of fields, or "*" for all
- `db`: AsyncSession
- `as_dict`: Return dict for multiple fields

**Returns**: Value, tuple, dict, or None

---

### 4. `get_list(entity, filters=None, fields="*", db=None, limit=0, order_by=None, as_dict=True)`

Fetch multiple documents matching filters.

```python
from app.services.document import get_list

# Get all properties for an asset class
props = await get_list(
    "asset_class_property", 
    {"asset_class": "AC-001"}, 
    db=db
)

# Get specific fields only
assets = await get_list(
    "asset", 
    {"site": "SITE-001"}, 
    fields=["id", "asset_tag", "description"],
    db=db,
    limit=10,
    order_by="asset_tag"
)

# Get as model instances
asset_models = await get_list(
    "asset", 
    {"workflow_state": "active"}, 
    db=db,
    as_dict=False
)
```

**Parameters**:
- `entity`: Entity name
- `filters`: Filter dict (optional)
- `fields`: List of fields or "*" for all
- `db`: AsyncSession
- `limit`: Max records (0 = no limit)
- `order_by`: Field to order by
- `as_dict`: Return dicts (default) or model instances

**Returns**: List of dicts or model instances

---

### 5. `new_doc(entity, db, **kwargs)`

Create a new document instance (not saved yet).

```python
from app.services.document import new_doc

# Create new work order activity
wo = await new_doc("work_order_activity", db,
    description="Inspect Asset",
    work_item_type="Asset",
    work_item="AST-0001",
    site="SITE-001",
    workflow_state="draft"
)
# ID is auto-generated if naming is enabled
print(wo.id)  # e.g., "WOA-0001"
```

**Parameters**:
- `entity`: Entity name
- `db`: AsyncSession (for ID generation)
- `**kwargs`: Field values

**Returns**: Model instance or None

**Note**: Automatically generates ID if naming is enabled in metadata.

---

### 6. `save_doc(doc, db, commit=True)`

Save a document (insert or update).

```python
from app.services.document import new_doc, save_doc

# Create and save
wo = await new_doc("work_order_activity", db, description="Test")
await save_doc(wo, db)

# Update existing
asset = await get_doc("asset", "AST-0001", db)
asset.workflow_state = "active"
await save_doc(asset, db)

# Save without commit (for batch operations)
await save_doc(wo, db, commit=False)
await save_doc(asset, db, commit=False)
await db.commit()
```

**Parameters**:
- `doc`: Model instance
- `db`: AsyncSession
- `commit`: Auto-commit (default True)

**Returns**: Saved document

---

### 7. `delete_doc(entity, id, db, commit=True)`

Delete a document by ID.

```python
from app.services.document import delete_doc

success = await delete_doc("work_order_activity", "WOA-0001", db)
```

**Parameters**:
- `entity`: Entity name
- `id`: Document ID
- `db`: AsyncSession
- `commit`: Auto-commit (default True)

**Returns**: True if deleted, False if not found

---

## Standard Terminology

### Use `doc` everywhere

| ❌ Old (Avoid) | ✅ New (Standard) |
|---------------|------------------|
| `record` | `doc` |
| `data` (for documents) | `doc` |
| `item` | `doc` |

### Context

- **Before save hooks**: `doc` is a `dict` (incoming data)
- **After save hooks**: `doc` is a model instance
- **Workflow hooks**: `doc` is a model instance

---

## Usage Patterns

### Pattern 1: Before Save Hook (Denormalization)

```python
async def populate_asset_names(doc: dict, db: AsyncSession) -> dict:
    """Populate denormalized fields from linked records."""
    
    if doc.get("asset_class"):
        asset_class = await get_doc("asset_class", doc["asset_class"], db)
        if asset_class:
            doc["asset_class_name"] = asset_class.name
    
    return doc
```

### Pattern 2: After Save Hook (Copy Child Records)

```python
async def copy_properties_from_parent(doc, ctx):
    """Copy properties from parent asset class."""
    
    if not doc.parent_asset_class:
        return
    
    # Check if already has properties
    existing = await get_list("asset_class_property", {"asset_class": doc.id}, db=ctx.db)
    if existing:
        return
    
    # Get parent properties
    parent_props = await get_list(
        "asset_class_property", 
        {"asset_class": doc.parent_asset_class}, 
        db=ctx.db,
        as_dict=False
    )
    
    # Copy each property
    for prop in parent_props:
        new_prop = await new_doc("asset_class_property", ctx.db,
            asset_class=doc.id,
            property=prop.property,
            property_name=prop.property_name,
            default_value=prop.default_value
        )
        await save_doc(new_prop, ctx.db, commit=False)
    
    if parent_props:
        await ctx.db.commit()
```

### Pattern 3: Workflow Hook (Create Related Records)

```python
async def _handle_inspect_asset(doc: Any, db: AsyncSession, user: Any) -> dict:
    """Create Work Order Activity and Maintenance Request."""
    
    # Get activity type
    activity_type = await get_value(
        "request_activity_type", 
        {"menu": "Asset", "type": "Inspect Asset"}, 
        "*", 
        db
    )
    
    if not activity_type:
        return {"status": "error", "message": "Activity type not found"}
    
    # Create Work Order Activity
    wo = await new_doc("work_order_activity", db,
        description=f"Inspect Asset: {doc.asset_tag}",
        work_item_type="Asset",
        work_item=doc.id,
        activity_type=activity_type["id"],
        site=doc.site,
        workflow_state="awaiting_resources"
    )
    await save_doc(wo, db, commit=False)
    
    # Create Maintenance Request
    mr = await new_doc("maintenance_request", db,
        request_type=activity_type["id"],
        asset=doc.id,
        work_order_activity=wo.id,
        workflow_state="draft"
    )
    await save_doc(mr, db, commit=True)
    
    return {
        "status": "success",
        "message": "Inspection request created",
        "data": {"maintenance_request_id": mr.id}
    }
```

---

## Migration Guide

### Before (Direct SQLAlchemy)

```python
from sqlalchemy import select
from app.modules.asset_management.models.asset_class import AssetClass
from app.modules.asset_management.models.asset_class_property import AssetClassProperty

async def populate_properties(record, ctx):
    # Get parent
    result = await ctx.db.execute(
        select(AssetClass).where(AssetClass.id == record.parent_asset_class)
    )
    parent = result.scalar_one_or_none()
    
    # Get properties
    result = await ctx.db.execute(
        select(AssetClassProperty).where(
            AssetClassProperty.asset_class == parent.id
        )
    )
    props = result.scalars().all()
    
    # Create new properties
    for prop in props:
        new_prop = AssetClassProperty(
            id=await generate_id(...),
            asset_class=record.id,
            property=prop.property
        )
        ctx.db.add(new_prop)
    
    await ctx.db.commit()
```

### After (Document Service)

```python
from app.services.document import get_list, new_doc, save_doc

async def populate_properties(doc, ctx):
    # Get properties from parent
    props = await get_list(
        "asset_class_property", 
        {"asset_class": doc.parent_asset_class}, 
        db=ctx.db,
        as_dict=False
    )
    
    # Create new properties
    for prop in props:
        new_prop = await new_doc("asset_class_property", ctx.db,
            asset_class=doc.id,
            property=prop.property
        )
        await save_doc(new_prop, ctx.db, commit=False)
    
    if props:
        await ctx.db.commit()
```

---

## Benefits

1. **Less Boilerplate**: No model imports, no select statements
2. **Easier Tracing**: Clear, readable code that mirrors Frappe
3. **Consistent Style**: All business logic uses same patterns
4. **Auto ID Generation**: Naming service integration built-in
5. **Type Safety**: Dynamic but predictable model resolution

---

## Best Practices

1. **Always use helpers in business logic** (apis/ folder)
2. **Use `doc` terminology** consistently
3. **Batch operations**: Use `commit=False` then manual commit
4. **Error handling**: Check for None returns
5. **Keep routers clean**: Use helpers only in module APIs, not in routers

---

## Related Documentation

- `ARCHITECTURE.md` - System architecture overview
- `STRUCTURE.md` - Backend structure
- `app/services/hooks.py` - Central hooks router
- `app/meta/registry.py` - Entity metadata registry
