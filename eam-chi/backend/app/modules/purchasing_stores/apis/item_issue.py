"""
Item Issue Entity Business Logic

Mirrors: ci_eam/purchasing_and_stores/doctype/item_issue/item_issue.py
- check_item_issue_state(item_issue, action)
- update_inventory_issue(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc
from app.services.stock_ledger import ledger_for_issue


async def check_item_issue_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Item Issue entity.
    
    Mirrors: check_item_issue_state() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Item Issue not specified"}
    
    item_issue_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not item_issue_id:
        return {"status": "error", "message": "Item Issue ID is required"}
    
    if action == "issue_item":
        response = await _update_inventory_issue(doc, db)
        if response["status"] == "success":
            # Get inventory ID from first Item Issue Line for the path
            issue_lines = await get_list("item_issue_line", {"item_issue": item_issue_id}, db=db, limit=1)
            inventory_id = issue_lines[0].get("inventory") if issue_lines else None
            
            return {
                "status": "success",
                "message": "Successfully issued parts",
                "action": "generate_id",
                "path": f"/inventory/{inventory_id}" if inventory_id else f"/item_issue/{item_issue_id}"
            }
        return response
    
    return {"status": "success", "message": f"Item Issue workflow '{action}' allowed"}


async def _update_inventory_issue(doc: Any, db: AsyncSession) -> dict:
    """
    Update inventory quantities when items are issued.
    
    Mirrors: update_inventory_issue() from Frappe
    """
    item_issue_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    issue_type = getattr(doc, 'issue_type', None)
    wo_activity_id = getattr(doc, 'work_order_activity', None)
    issue_to = getattr(doc, 'issue_to', None)
    
    # Get issue lines
    issue_lines = await get_list("item_issue_line", {"item_issue": item_issue_id}, db=db)
    
    if not issue_lines:
        return {"status": "error", "message": "No Item Issue Lines found for this Item Issue"}
    
    if issue_type == "WO Parts Issue":
        for line in issue_lines:
            wo_parts_id = line.get("work_order_parts")
            if wo_parts_id:
                wo_part = await get_doc("work_order_parts", wo_parts_id, db)
                if wo_part:
                    qty_issued = getattr(wo_part, 'quantity_issued', 0) or 0
                    line_qty = line.get("quantity_issued", 0) or 0
                    wo_part.quantity_issued = qty_issued + line_qty
                    await save_doc(wo_part, db, commit=False)
    
    elif issue_type == "WO Equipment Issue":
        for line in issue_lines:
            inventory_id = line.get("inventory")
            if inventory_id:
                inventory = await get_value("inventory", inventory_id, "*", db)
                if inventory:
                    # Find equipment linked to this inventory
                    equipment = await get_value("equipment", {"equipment_type": "Owned", "inventory": inventory_id}, "*", db)
                    if equipment:
                        equip_doc = await get_doc("equipment", equipment["id"], db)
                        if equip_doc:
                            equip_doc.custodian = issue_to
                            await save_doc(equip_doc, db, commit=False)
                    
                    # Update asset workflow if linked
                    asset_id = inventory.get("asset")
                    if asset_id:
                        asset = await get_doc("asset", asset_id, db)
                        if asset:
                            asset.workflow_state = "issued"
                            await save_doc(asset, db, commit=False)
    
    # Update Inventory and Item quantities
    for line in issue_lines:
        inventory_id = line.get("inventory")
        if not inventory_id:
            continue
        
        inventory = await get_doc("inventory", inventory_id, db)
        if not inventory:
            continue
        
        item_id = getattr(inventory, 'item', None)
        item = await get_doc("item", item_id, db) if item_id else None
        
        qty_to_issue = line.get("quantity_issued", 0) or 0
        actual_inv = getattr(inventory, 'actual_inv', 0) or 0
        available_inv = getattr(inventory, 'available_inv', 0) or 0
        
        if actual_inv >= qty_to_issue and available_inv >= qty_to_issue:
            inventory.actual_inv = actual_inv - qty_to_issue
            inventory.available_inv = available_inv - qty_to_issue
            await save_doc(inventory, db, commit=False)
            
            if item:
                item_actual = getattr(item, 'actual_qty_on_hand', 0) or 0
                item_available = getattr(item, 'available_capacity', 0) or 0
                item.actual_qty_on_hand = item_actual - qty_to_issue
                item.available_capacity = item_available - qty_to_issue
                await save_doc(item, db, commit=False)

            # Stock ledger audit trail
            await ledger_for_issue(
                db=db,
                item_issue_id=item_issue_id,
                item_id=item_id,
                qty=qty_to_issue,
                unit_cost=getattr(inventory, 'base_unit_cost', 0) or 0,
                store=getattr(inventory, 'store_location', None),
                serial_no=getattr(inventory, 'serial_number', None),
                site=getattr(inventory, 'site', None),
            )
        else:
            return {
                "status": "error",
                "message": "Insufficient inventory to issue the requested quantity",
                "exception": "Insufficient inventory"
            }
    
    await db.commit()
    return {"status": "success", "message": f"Successfully issued parts. Inventory updated."}
