# Work Management Module - Business Logic

## Overview

This document describes the business logic migrated from the old Frappe-based EAM system for the Work Management module.

## Source Files (Old System)

| Old File | New File |
|----------|----------|
| `ci_eam/work_management/doctype/work_order/work_order.py` | `app/modules/work_mgmt/apis/work_order.py` |
| `ci_eam/work_management/doctype/work_order_activity/work_order_activity.py` | `app/modules/work_mgmt/apis/work_order_activity.py` |
| `ci_eam/work_management/doctype/work_order_parts/work_order_parts.py` | `app/modules/work_mgmt/apis/work_order_parts.py` |
| `ci_eam/work_management/doctype/work_order_labor_assignment/work_order_labor_assignment.py` | `app/modules/work_mgmt/apis/work_order_labor_assignment.py` |
| `ci_eam/work_management/doctype/work_order_equipment_assignment/work_order_equipment_assignment.py` | `app/modules/work_mgmt/apis/work_order_equipment_assignment.py` |

## Work Order Entity

### Workflow Actions

| Action | Description | Validation |
|--------|-------------|------------|
| `approve` | Approve work order | Always allowed |
| `start` | Start work order | All Work Order Activities must be in 'ready' state |
| `complete` | Complete work order | All Work Order Activities must be 'completed' or 'closed' |
| `reopen` | Reopen work order | Always allowed |

### Workflow Hook

```python
async def check_work_order_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Work Order entity.
    Mirrors: check_wo_order_state() from Frappe
    """
```

## Work Order Activity Entity

### Workflow Actions

| Action | Description | Creates Records |
|--------|-------------|-----------------|
| `allocate` | Allocate resources | Validates labor, equipment, parts assigned |
| `start_activity` | Start activity | Updates asset workflow if applicable |
| `complete` | Complete activity | Updates Maintenance Request, Asset Position |
| `reopen` | Reopen activity | - |
| `close` | Close activity | Validates logs, parts issued, hours recorded |

### After Save Hook

```python
async def create_wo_labor_on_save(doc, db) -> dict:
    """
    Create Work Order Labor record when assigned_to is set.
    Mirrors: create_wo_labor() from Frappe
    """
```

### Workflow Hook

```python
async def check_work_order_activity_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Work Order Activity entity.
    Mirrors: check_wo_activity_state() from Frappe
    
    Key logic:
    - Allocate: Validates all required resources are assigned
    - Complete: Handles Install Asset / Remove Asset position updates
    - Close: Validates activity logs, parts issued, hours recorded
    """
```

### Helper Functions

```python
async def _install_asset_position(doc, db) -> Any:
    """Install asset at position. Creates Asset Position record."""

async def _uninstall_asset_position(doc, db) -> dict:
    """Remove asset from position. Updates Asset Position with date_removed."""
```

## Work Order Parts Entity

### Workflow Actions

| Action | Description | Validation |
|--------|-------------|------------|
| `assigned_partial_items` | Partially assign parts | Parts Issue or Reservation must exist |
| `assigned_all_items` | Fully assign parts | Parts Issue or Reservation must exist |
| `start` | Start parts workflow | May trigger parent activity start |
| `complete` | Complete parts | - |

## Work Order Labor Assignment Entity

### After Save Hook

```python
async def update_labor_availability_on_save(doc, db) -> dict:
    """
    Update Work Order Labor state and Trade/Labor Availability.
    
    Logic:
    1. Count assignments vs required quantity
    2. Update Work Order Labor workflow state
    3. Update Trade Availability (reserved_capacity, available_capacity)
    4. Update Labor Availability Details (mark as 'Reserved')
    """
```

## Work Order Equipment Assignment Entity

### After Save Hook

```python
async def update_equipment_availability_on_save(doc, db) -> dict:
    """
    Update Work Order Equipment state and Asset Class/Equipment Availability.
    
    Logic:
    1. Count assignments vs required quantity
    2. Update Work Order Equipment workflow state
    3. Update Asset Class Availability (reserved_capacity, available_capacity)
    4. Update Equipment Availability Details (mark as 'Reserved')
    """
```

## Entity Mapping

| Old Entity (Frappe) | New Entity (FastAPI) |
|---------------------|----------------------|
| Work Order | work_order |
| Work Order Activity | work_order_activity |
| Work Order Activity Logs | work_order_activity_logs |
| Work Order Checklist | work_order_checklist |
| Work Order Checklist Detail | work_order_checklist_detail |
| Work Order Equipment | work_order_equipment |
| Work Order Equipment Assignment | work_order_equipment_assignment |
| Work Order Equipment Actual Hours | work_order_equipment_actual_hours |
| Work Order Labor | work_order_labor |
| Work Order Labor Assignment | work_order_labor_assignment |
| Work Order Labor Actual Hours | work_order_labor_actual_hours |
| Work Order Parts | work_order_parts |
| Work Order Parts Issue | work_order_parts_issue |
| Work Order Parts Return | work_order_parts_return |
| Work Order Parts Reservation | work_order_parts_reservation |

## Workflow State Mapping

| Old State | New State |
|-----------|-----------|
| Requested | requested |
| Approved | approved |
| In Progress | in_progress |
| Closed | closed |
| Awaiting Resources | awaiting_resources |
| Ready | ready |
| Scheduled | scheduled |
| Completed | completed |
