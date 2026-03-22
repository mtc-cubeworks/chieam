# Purchasing and Stores Module - Business Logic

## Overview

This document describes the business logic migrated from the old Frappe-based EAM system for the Purchasing and Stores module.

## Source Files (Old System)

| Old File | New File |
|----------|----------|
| `ci_eam/purchasing_and_stores/doctype/purchase_request/purchase_request.py` | `app/modules/purchasing_stores/apis/purchase_request.py` |
| `ci_eam/purchasing_and_stores/doctype/purchase_receipt/purchase_receipt.py` | `app/modules/purchasing_stores/apis/purchase_receipt.py` |
| `ci_eam/purchasing_and_stores/doctype/item_issue/item_issue.py` | `app/modules/purchasing_stores/apis/item_issue.py` |
| `ci_eam/purchasing_and_stores/doctype/item_return/item_return.py` | `app/modules/purchasing_stores/apis/item_return.py` |
| `ci_eam/purchasing_and_stores/doctype/putaway/putaway.py` | (integrated into item_return.py) |

## Purchase Request Entity

### Workflow Actions

| Action | Description | Updates |
|--------|-------------|---------|
| `submit_for_approval` | Submit for approval | All non-rejected lines → 'added' state |
| `approve` | Approve request | All non-rejected lines → 'approved' state |
| `reject_purchase_request` | Reject request | All non-rejected lines → 'rejected' state |
| `complete` | Complete request | Validates all lines are 'complete' |

### Workflow Hook

```python
async def check_purchase_request_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Purchase Request entity.
    Mirrors: check_pr_state() from Frappe
    """
```

### Custom APIs

```python
async def generate_rfq_log(doc, db, user) -> dict:
    """
    Generate RFQ Log from Purchase Request.
    Requires: due_date to be set
    """
```

## Purchase Receipt Entity

### After Save Hook

```python
async def update_inventory_on_receive(doc, db, user) -> dict:
    """
    Create/update inventory when purchase receipt is received.
    
    Logic by Item Type:
    
    1. Asset Item / Fixed Asset Item (Serialized):
       - Create individual Inventory records
       - Create Asset records
       - Create Maintenance Request if inspection required
       - Create Equipment if is_equipment
       
    2. Asset Item / Fixed Asset Item (Non-Serialized):
       - Update existing Inventory or create new
       - Create Asset record
       - Create Maintenance Request if inspection required
       
    3. Regular Inventory Item (Serialized):
       - Create individual Inventory records
       - Create Equipment if is_equipment
       
    4. Regular Inventory Item (Non-Serialized):
       - Update existing Inventory or create new
    """
```

### Helper Functions

```python
async def _create_inventory(base_unit_cost, site, location, financial_asset_number, item, quantity, db) -> Any:
    """Create inventory record."""

async def _create_asset(inventory, item, pr_line, is_fixed, db) -> Any:
    """Create asset record with properties from asset class."""

async def _create_maint_request(asset, pr_line, db) -> Any:
    """Create maintenance request for asset inspection."""

async def _create_equipment(site, inventory, item, location, db) -> Any:
    """Create equipment record."""
```

## Item Issue Entity

### Workflow Actions

| Action | Description | Updates |
|--------|-------------|---------|
| `issue_item` | Issue items | Updates Inventory, Item quantities |

### Workflow Hook

```python
async def check_item_issue_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Item Issue entity.
    Mirrors: check_item_issue_state() from Frappe
    """
```

### Helper Functions

```python
async def _update_inventory_issue(doc, db) -> dict:
    """
    Update inventory quantities when items are issued.
    
    Logic by Issue Type:
    
    1. WO Parts Issue:
       - Update Work Order Parts.quantity_issued
       
    2. WO Equipment Issue:
       - Update Equipment.custodian
       - Update Asset workflow state to 'issued'
       
    3. All types:
       - Decrease Inventory.actual_inv and available_inv
       - Decrease Item.actual_qty_on_hand and available_capacity
    """
```

## Item Return Entity

### Workflow Actions

| Action | Description | Creates |
|--------|-------------|---------|
| `return_item` | Return items | Putaway records |

### Workflow Hook

```python
async def check_item_return_workflow(doc, action, db, user) -> dict:
    """
    Main workflow handler for Item Return entity.
    Mirrors: check_item_return_state() from Frappe
    """
```

### Helper Functions

```python
async def _create_putaway(line, doc, db) -> dict:
    """
    Create Putaway record for returned item.
    
    Logic by Return Type:
    
    1. WO Parts Return:
       - Create Putaway with item from Work Order Parts
       - Update inventory via _update_inventory_return
       
    2. WO Equipment Return:
       - Create Putaway with item from Equipment's Inventory
       - Clear Equipment.custodian
       - Update Asset workflow state to 'inactive'
    """

async def _update_inventory_return(putaway, db) -> dict:
    """
    Update inventory quantities when items are returned.
    
    Logic:
    1. Update Work Order Parts.quantity_returned (for parts)
    2. Clear Equipment.custodian (for equipment)
    3. Increase Inventory.actual_inv and available_inv
    4. Increase Item.actual_qty_on_hand and available_capacity
    """
```

## Entity Mapping

| Old Entity (Frappe) | New Entity (FastAPI) |
|---------------------|----------------------|
| Purchase Request | purchase_request |
| Purchase Request Line | purchase_request_line |
| Purchase Receipt | purchase_receipt |
| Item Issue | item_issue |
| Item Issue Line | item_issue_line |
| Item Return | item_return |
| Item Return Line | item_return_line |
| Putaway | putaway |
| Inventory | inventory |
| Item | item |
| Store | store |
| Bin | bin |
| RFQ Log | rfq_log |

## Workflow State Mapping

| Old State | New State |
|-----------|-----------|
| Draft | draft |
| Added | added |
| Approved | approved |
| Rejected | rejected |
| Partially Received | partially_received |
| Received All Items | received_all_items |
| Complete | complete |

## Inventory Update Flow

```
Purchase Receipt → Inventory Created/Updated → Item Quantities Updated
                         ↓
                   Asset Created (if Asset Item)
                         ↓
                   Maintenance Request (if inspection required)
                         ↓
                   Equipment Created (if is_equipment)
```

```
Item Issue → Inventory Decreased → Item Quantities Decreased
                  ↓
            Work Order Parts Updated (if WO Parts Issue)
                  ↓
            Equipment Custodian Set (if WO Equipment Issue)
```

```
Item Return → Putaway Created → Inventory Increased → Item Quantities Increased
                                      ↓
                               Work Order Parts Updated (if WO Parts Return)
                                      ↓
                               Equipment Custodian Cleared (if WO Equipment Return)
```
