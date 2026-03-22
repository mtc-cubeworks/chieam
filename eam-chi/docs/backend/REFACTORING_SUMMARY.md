# Backend Refactoring Summary

## Overview

This document summarizes the refactoring work done to standardize the backend codebase with Frappe-like document helpers and consistent terminology.

**Date**: January 2026  
**Scope**: Backend business logic layer

---

## What Changed

### 1. New Document Service (`app/services/document.py`)

Created a comprehensive document service with Frappe-style helpers:

- **`get_meta(entity)`** - Get entity metadata
- **`get_doc(entity, id, db)`** - Fetch single document by ID
- **`get_value(entity, filters, fieldname, db)`** - Get specific field values
- **`get_list(entity, filters, db)`** - Fetch multiple documents
- **`new_doc(entity, db, **kwargs)`** - Create new document (auto-generates ID)
- **`save_doc(doc, db)`** - Save document (insert or update)
- **`delete_doc(entity, id, db)`** - Delete document

**Benefits**:
- No direct model imports needed
- Auto ID generation via naming service
- Consistent API across all entities
- Easier to trace and maintain

---

### 2. Standardized Terminology

**Global replacement**: `record` → `doc`, `data` → `doc`

| Component | Old | New |
|-----------|-----|-----|
| **Function parameters** | `record`, `data` | `doc` |
| **Variable names** | `record`, `data`, `item` | `doc` |
| **Internal helpers** | `_record_to_dict()` | `_record_to_dict(doc)` |

**Affected Files**:
- `app/services/document.py` - Internal variable names
- `app/services/hooks.py` - Hook signatures and context
- `app/routers/entity.py` - Workflow logic
- `app/modules/asset_management/apis/asset.py` - All functions
- `app/modules/asset_management/apis/asset_class_hooks.py` - All functions

---

### 3. Refactored Files

#### `app/modules/asset_management/apis/asset.py`

**Before**:
```python
from sqlalchemy import select
from app.modules.core_eam.models.request_activity_type import RequestActivityType

async def _handle_inspect_asset(record: Any, db: AsyncSession, user: Any):
    result = await db.execute(
        select(RequestActivityType).where(
            RequestActivityType.menu == "Asset",
            RequestActivityType.type == "Inspect Asset"
        )
    )
    activity_type = result.scalar_one_or_none()
    
    wo_activity = WorkOrderActivity(id=woa_id, ...)
    db.add(wo_activity)
    await db.commit()
```

**After**:
```python
from app.services.document import get_value, new_doc, save_doc

async def _handle_inspect_asset(doc: Any, db: AsyncSession, user: Any):
    activity_type = await get_value(
        "request_activity_type", 
        {"menu": "Asset", "type": "Inspect Asset"}, 
        "*", 
        db
    )
    
    wo_activity = await new_doc("work_order_activity", db, ...)
    await save_doc(wo_activity, db)
```

**Changes**:
- Removed 15+ direct model imports
- Replaced all `select()` statements with `get_value()` or `get_doc()`
- Replaced `db.add()` + manual ID generation with `new_doc()`
- Replaced `db.add()` + `db.commit()` with `save_doc()`
- Renamed `record` → `doc` throughout

---

#### `app/modules/asset_management/apis/asset_class_hooks.py`

**Before**:
```python
from sqlalchemy import select
from app.modules.asset_management.models.asset_class_property import AssetClassProperty
from app.services.naming import NamingService

async def populate_asset_class_prop_and_maint_plan(record, ctx):
    result = await db.execute(
        select(AssetClassProperty).where(
            AssetClassProperty.asset_class == parent_id
        )
    )
    props = result.scalars().all()
    
    for prop in props:
        new_id = await NamingService.generate_id(db, meta.naming)
        new_prop = AssetClassProperty(id=new_id, ...)
        db.add(new_prop)
```

**After**:
```python
from app.services.document import get_list, new_doc, save_doc

async def populate_asset_class_prop_and_maint_plan(doc, ctx):
    props = await get_list(
        "asset_class_property", 
        {"asset_class": parent_id}, 
        db=ctx.db,
        as_dict=False
    )
    
    for prop in props:
        new_prop = await new_doc("asset_class_property", ctx.db, ...)
        await save_doc(new_prop, ctx.db, commit=False)
```

**Changes**:
- Removed direct model imports
- Replaced `select()` with `get_list()`
- Replaced manual ID generation + model instantiation with `new_doc()`
- Replaced `db.add()` with `save_doc()`
- Renamed `record` → `doc`

---

#### `app/services/hooks.py`

**Changes**:
- `before_save(entity, doc, ctx)` - parameter renamed from `data` to `doc`
- `after_save(entity, doc, ctx)` - parameter renamed from `record` to `doc`
- `WorkflowContext.doc` - field renamed from `record` to `doc`

---

#### `app/routers/entity.py`

**Changes**:
- Updated workflow logic to use `doc` instead of `record`
- Fixed `WorkflowContext` instantiation to match new field name

---

### 4. New Documentation

Created comprehensive documentation:

1. **`DOCUMENT_SERVICE.md`** - Complete reference for all document helpers
2. **`CODING_STANDARDS.md`** - Coding standards and best practices
3. **`REFACTORING_SUMMARY.md`** - This document

---

## Verification

All refactored files compile successfully:

```bash
# Verified
python3 -m py_compile app/services/document.py
python3 -m py_compile app/modules/asset_management/apis/asset.py
python3 -m py_compile app/modules/asset_management/apis/asset_class_hooks.py
python3 -m py_compile app/services/hooks.py
python3 -m py_compile app/routers/entity.py

# All imports work
python3 -c "from app.services.document import get_doc; from app.modules.asset_management.apis.asset import check_asset_workflow; print('OK')"
```

---

## Impact Analysis

### Files Modified

1. `app/services/document.py` - **Created** (322 lines)
2. `app/modules/asset_management/apis/asset.py` - **Refactored** (400 lines)
3. `app/modules/asset_management/apis/asset_class_hooks.py` - **Refactored** (82 lines)
4. `app/services/hooks.py` - **Updated** (158 lines)
5. `app/routers/entity.py` - **Updated** (612 lines, minimal changes)

### Files Scanned (No Changes Needed)

- All other modules (`/app/modules/*/apis/`) - No business logic files found
- All routers (`/app/routers/*.py`) - Use direct SQLAlchemy (appropriate for routers)
- All services (`/app/services/*.py`) - No document operations

### Total Impact

- **Lines of code reduced**: ~150 lines (removed boilerplate)
- **Direct model imports removed**: 15+
- **SQLAlchemy select() statements removed**: 20+
- **Consistency improvements**: 100% of business logic now uses standard helpers

---

## Migration Pattern

For future business logic files, follow this pattern:

### Step 1: Identify Direct Database Operations

Look for:
- `from app.modules.*.models import *`
- `select(Model).where(...)`
- `db.execute()`
- `db.add()`
- `Model(**kwargs)`

### Step 2: Replace with Document Helpers

| Old Pattern | New Pattern |
|-------------|-------------|
| `select(Model).where(Model.id == id)` | `get_doc("entity", id, db)` |
| `select(Model).where(filters)` | `get_list("entity", filters, db=db)` |
| `Model(**kwargs); db.add()` | `new_doc("entity", db, **kwargs); save_doc()` |
| `getattr(record, "field")` | `get_value("entity", id, "field", db)` |

### Step 3: Update Terminology

- Rename all `record` → `doc`
- Rename all `data` → `doc` (for documents)
- Update function signatures
- Update docstrings

### Step 4: Test

```bash
# Compile check
python3 -m py_compile path/to/file.py

# Import check
python3 -c "from path.to.module import function_name; print('OK')"
```

---

## Best Practices Going Forward

1. **Always use document helpers** in business logic (`/apis/` files)
2. **Use `doc` terminology** consistently
3. **Keep routers clean** - helpers only in module APIs
4. **Batch operations** - use `commit=False` then manual commit
5. **Check for None** - always validate helper returns
6. **Document your code** - explain business logic, not syntax

---

## Related Documentation

- **`DOCUMENT_SERVICE.md`** - Complete API reference
- **`CODING_STANDARDS.md`** - Standards and patterns
- **`ARCHITECTURE.md`** - System architecture
- **`app/services/hooks.py`** - Central hooks router

---

## Future Work

### Potential Enhancements

1. **Add `get_all()` helper** - Fetch all records for an entity
2. **Add `exists()` helper** - Check if document exists
3. **Add `count()` helper** - Count documents matching filters
4. **Add `update_doc()` helper** - Update without fetching first
5. **Add transaction context manager** - For complex multi-doc operations

### Other Modules

As new business logic is added to other modules:
- Follow the established patterns
- Use document helpers from day one
- Maintain consistent terminology
- Document complex business logic

---

## Questions?

Refer to:
- `DOCUMENT_SERVICE.md` for API details
- `CODING_STANDARDS.md` for patterns and examples
- `app/services/document.py` for implementation
