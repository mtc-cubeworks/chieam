# Maintenance Management Module - Business Logic

## Overview

This document describes the business logic migrated from the old Frappe-based EAM system for the Maintenance Management module.

## Source Files (Old System)

| Old File | New File |
|----------|----------|
| `ci_eam/maintenance_management/doctype/maintenance_request/maintenance_request.py` | `app/modules/maintenance_mgmt/apis/maintenance_request.py` |
| `ci_eam/maintenance_management/doctype/maintenance_order/maintenance_order.py` | `app/modules/maintenance_mgmt/apis/maintenance_order.py` |

## Maintenance Request Entity

### Workflow Actions

| Action | Description | Creates Records |
|--------|-------------|-----------------|
| `approve` | Approve request | Work Order Activity (+ Checklist, Equipment, Labor, Parts from PMA) |
| `submit_for_emergency` | Emergency request | Work Order, Work Order Activity |
| `submit_for_resolution` | Submit for resolution | Work Order |
| `complete` | Complete request | Updates closed_date |
| `reopen` | Reopen request | Reopens Work Order Activity and Work Order |

### Workflow Hook

```python
async def check_maintenance_request_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Maintenance Request entity.
    Mirrors: check_maint_request_state() from Frappe
    """
```

### Helper Functions

```python
async def _generate_work_order(doc, action, db, user) -> dict:
    """
    Generate Work Order and Work Order Activity for Maintenance Request.
    
    Logic:
    - Approve: Creates Work Order Activity with resources from PMA
    - Emergency: Creates Work Order + Activity immediately
    - Submit for Resolution: Creates Work Order for existing activity
    """

async def _create_work_order_activity(doc, pma_id, work_order, db) -> Any:
    """Create Work Order Activity from Maintenance Request."""

async def _create_wo_resources_from_pma(wo_activity, pma_id, db) -> None:
    """
    Create Work Order resources from Planned Maintenance Activity.
    Creates: Checklist, Equipment, Labor, Parts
    """

async def get_resource_availability_status(doc, db) -> dict:
    """
    Check resource availability for a Maintenance Request.
    Returns: Available, Partially Available, or Not Available
    """
```

## Maintenance Order Entity

### Custom APIs

```python
async def generate_work_order_from_maintenance_order(doc, db, user) -> dict:
    """
    Generate Work Order from Maintenance Order.
    
    Logic:
    1. Validate no existing Work Order
    2. Get all Maintenance Order Details
    3. Create Work Order
    4. Link all Work Order Activities to the Work Order
    5. Update Maintenance Requests to 'Release' state
    6. Approve the Work Order
    """
```

## Entity Mapping

| Old Entity (Frappe) | New Entity (FastAPI) |
|---------------------|----------------------|
| Maintenance Request | maintenance_request |
| Maintenance Order | maintenance_order |
| Maintenance Order Detail | maintenance_order_detail |
| Maintenance Plan | maintenance_plan |
| Planned Maintenance Activity | planned_maintenance_activity |
| Maintenance Activity | maintenance_activity |
| Maintenance Trade | maintenance_trade |
| Maintenance Equipment | maintenance_equipment |
| Maintenance Parts | maintenance_parts |
| Checklist | checklist |
| Checklist Details | checklist_details |

## Workflow State Mapping

| Old State | New State |
|-----------|-----------|
| Draft | draft |
| Pending Approval | pending_approval |
| Approved | approved |
| Release | release |
| Completed | completed |

## Resource Availability Check

The `get_resource_availability_status` function checks:

1. **Trade Availability**: Compares `Trade Availability.available_capacity` with `Maintenance Trade.required_qty`
2. **Equipment Availability**: Compares `Asset Class Availability.available_capacity` with `Maintenance Equipment.required_qty`
3. **Material Availability**: Compares `Inventory.available_inv` with `Maintenance Parts.quantity`

Returns:
- `Available`: All resources available
- `Partially Available`: Some resources available
- `Not Available`: No resources available
