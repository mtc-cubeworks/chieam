# Asset Management Module - Business Logic

## Overview

This document describes the business logic migrated from the old Frappe-based EAM system for the Asset Management module.

## Source Files (Old System)

| Old File | New File |
|----------|----------|
| `ci_eam/asset_management/doctype/asset/asset.py` | `app/modules/asset_management/apis/asset.py` |
| `ci_eam/asset_management/doctype/asset_class/asset_class.py` | `app/modules/asset_management/apis/asset_class_hooks.py` |
| `ci_eam/asset_management/doctype/breakdown/breakdown.py` | `app/modules/asset_management/apis/breakdown.py` |
| `ci_eam/asset_management/doctype/disposed/disposed.py` | `app/modules/asset_management/apis/disposed.py` |
| `ci_eam/asset_management/doctype/position/position.py` | `app/modules/asset_management/apis/position.py` |

## Asset Entity

### Workflow Actions

| Action | Description | Creates Records |
|--------|-------------|-----------------|
| `inspect_asset` | Create inspection request | Work Order Activity, Maintenance Request |
| `issue_equipment` | Issue equipment to user | Item Issue |
| `putaway` | Store asset in warehouse | Putaway |
| `commission` | Commission asset | Asset Position |
| `install_asset` | Install at position | Asset Position |
| `maintain_asset` | Create maintenance request | Work Order Activity, Maintenance Request |
| `remove_asset` | Remove from position | Updates Asset Position |
| `dispose` | Dispose asset | Disposed, Purchase Request |

### Before Save Hook

```python
async def populate_asset_names(doc: dict, db: AsyncSession) -> dict:
    """Populate denormalized name fields from linked records."""
    # Populates: asset_class_name, manufacturer_name
```

### Workflow Hook

```python
async def check_asset_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Asset entity.
    Mirrors: check_asset_state() from Frappe
    """
```

## Asset Class Entity

### After Save Hook

```python
async def populate_asset_class_prop_and_maint_plan(doc, ctx):
    """
    Populates Asset Class Properties and Maintenance Plans from parent.
    
    Logic:
    1. If parent_asset_class exists:
       - Copies all Asset Class Properties from parent
       - (Future) Copies all Maintenance Plans from parent
    """
```

## Breakdown Entity

### After Save Hook

```python
async def create_update_equip_availability_on_save(doc, db) -> dict:
    """
    Create/update Equipment Availability based on breakdown.
    
    Logic:
    1. Get or create Equipment Availability for the date
    2. Mark hours within breakdown period as 'Breakdown'
    3. Update Asset Class Availability if equipment has asset class
    """
```

## Disposed Entity

### After Save Hook

```python
async def create_purchase_request_on_dispose(doc, db, user) -> dict:
    """
    Create Purchase Request when asset is disposed.
    
    Logic:
    1. Create Purchase Request for replacement
    2. If Fixed Asset Item, note that Asset Position needs date_removed
    """
```

## Position Entity

### Custom APIs

```python
async def create_install_asset(position_id, db, user) -> dict:
    """Create maintenance request to install an asset at a position."""

async def create_swap_asset(position_id, new_asset_id, db, user) -> dict:
    """Create maintenance request to swap an asset at a position."""

async def create_decommission_asset(position_id, db, user) -> dict:
    """Create maintenance request to decommission an asset at a position."""
```

## Entity Mapping

| Old Entity (Frappe) | New Entity (FastAPI) |
|---------------------|----------------------|
| Asset | asset |
| Asset Class | asset_class |
| Asset Class Property | asset_class_property |
| Asset Position | asset_position |
| Asset Property | asset_property |
| Breakdown | breakdown |
| Disposed | disposed |
| Equipment | equipment |
| Equipment Availability | equipment_availability |
| Equipment Availability Details | equipment_availability_details |
| Incident | incident |
| Location | location |
| Position | position |

## Field Mapping

Most fields have identical names. Key differences:

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| `name` (Frappe ID) | `id` | Primary key |
| `workflow_state` | `workflow_state` | Same |
| `doctype` | N/A | Not needed in FastAPI |
