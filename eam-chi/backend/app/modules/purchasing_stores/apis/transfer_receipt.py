"""
Transfer Receipt Entity Business Logic

Mirrors: ci_eam/purchasing_and_stores/doctype/transfer_receipt/transfer_receipt.py
- update_item_location(doc)
- create_asset_repair_inspection(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, new_doc, save_doc


async def update_item_location(doc: Any, db: AsyncSession) -> dict:
    """
    Update inventory and asset location when transfer is received.
    
    Mirrors: update_item_location() from Frappe
    """
    transfer_type = getattr(doc, 'transfer_type', None)
    transfer_request_id = getattr(doc, 'transfer_request', None)
    receiving_location = getattr(doc, 'receiving_location', None)
    inventory_id = getattr(doc, 'inventory', None)
    
    if not transfer_type:
        return {"status": "error", "message": "Transfer type is required."}
    
    transfer = await get_value("transfer", transfer_request_id, "*", db) if transfer_request_id else None
    
    if transfer_type in ["Inventory", "External Repair Service"]:
        inv = await get_value("inventory", transfer.get("inventory") if transfer else inventory_id, "*", db)
        location = await get_value("location", receiving_location, "*", db)
        
        if inv:
            inv_doc = await get_doc("inventory", inv["id"], db)
            if inv_doc:
                inv_doc.location = receiving_location
                inv_doc.store_location = location.get("store") if location else None
                inv_doc.bin_location = None
                inv_doc.zone = None
                await save_doc(inv_doc, db, commit=False)
            
            # Update asset location if linked
            if inv.get("asset"):
                asset_doc = await get_doc("asset", inv["asset"], db)
                if asset_doc:
                    asset_doc.location = receiving_location
                    await save_doc(asset_doc, db)
                
                return {
                    "status": "success",
                    "message": "Successfully updated item's location.",
                    "action": "generate_id",
                    "path": f"/asset/{inv['asset']}"
                }
        
        await db.commit()
        return {
            "status": "success",
            "message": "Successfully updated item's location.",
            "action": "generate_id",
            "path": f"/inventory/{transfer.get('inventory') if transfer else inventory_id}"
        }
    
    return {"status": "success", "message": "Location update not applicable for this transfer type."}


async def create_asset_repair_inspection(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Create inspection Work Order Activity and Maintenance Request for repaired asset.
    
    Mirrors: create_asset_repair_inspection() from Frappe
    """
    inventory_id = getattr(doc, 'inventory', None)
    transfer_request_id = getattr(doc, 'transfer_request', None)
    receiving_location = getattr(doc, 'receiving_location', None)
    
    if not inventory_id:
        return {"status": "error", "message": "Inventory is required."}
    
    inv = await get_value("inventory", inventory_id, "*", db)
    if not inv or not inv.get("asset"):
        return {"status": "error", "message": "Inventory has no linked asset."}
    
    asset = await get_doc("asset", inv["asset"], db)
    if not asset:
        return {"status": "error", "message": "Asset not found."}
    
    # Update asset workflow if under repair
    if getattr(asset, 'workflow_state', None) == "Under Repair":
        asset.workflow_state = "Inactive"
        await save_doc(asset, db, commit=False)
    
    transfer = await get_value("transfer", transfer_request_id, "*", db) if transfer_request_id else None
    
    if transfer and transfer.get("transfer_type") != "External Repair Service":
        return {"status": "error", "message": "Cannot create asset's inspection record for this transfer type."}
    
    site = getattr(asset, 'site', None)
    department = getattr(asset, 'department', None)
    work_order_id = None
    
    # Check if transfer has linked work order activity
    if transfer and transfer.get("work_order_activity"):
        wo_activity = await get_value("work_order_activity", transfer["work_order_activity"], "*", db)
        if wo_activity:
            work_order_id = wo_activity.get("work_order")
            site = wo_activity.get("site")
            department = wo_activity.get("department")
    
    # Create Work Order Activity for inspection
    new_wo_activity = await new_doc("work_order_activity", db,
        work_order=work_order_id,
        description=f"Inspect Repaired Asset: {asset.asset_tag}",
        work_item_type="Asset",
        work_item=asset.id,
        location=receiving_location,
        site=site,
        department=department,
        start_date=datetime.now(),
        workflow_state="awaiting_resources"
    )
    await save_doc(new_wo_activity, db, commit=False)
    
    # Create Maintenance Request
    due_date = datetime.now().date() + timedelta(days=7)
    maint_request = await new_doc("maintenance_request", db,
        requested_date=datetime.now(),
        asset=asset.id,
        location=receiving_location,
        due_date=due_date,
        site=site,
        department=department,
        work_order_activity=new_wo_activity.id,
        workflow_state="draft"
    )
    await save_doc(maint_request, db, commit=False)
    
    # Apply workflow transitions
    maint_request.workflow_state = "pending_approval"
    await save_doc(maint_request, db, commit=False)
    maint_request.workflow_state = "approved"
    await save_doc(maint_request, db, commit=False)
    
    if work_order_id:
        maint_request.workflow_state = "release"
        await save_doc(maint_request, db)
        return {
            "status": "success",
            "message": "Successfully created asset's inspection record.",
            "action": "generate_id",
            "path": f"/work_order/{work_order_id}"
        }
    
    await db.commit()
    return {
        "status": "success",
        "message": "Successfully created asset's inspection record.",
        "action": "generate_id",
        "path": f"/maintenance_request/{maint_request.id}"
    }
