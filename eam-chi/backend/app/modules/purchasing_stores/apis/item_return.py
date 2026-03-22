"""
Item Return Entity Business Logic

Mirrors: ci_eam/purchasing_and_stores/doctype/item_return/item_return.py
- check_item_return_state(item_return, action)
- create_putaway(doc, item_return)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc
from app.services.stock_ledger import ledger_for_return


async def check_item_return_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Item Return entity.
    
    Mirrors: check_item_return_state() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Item Return not specified"}
    
    item_return_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not item_return_id:
        return {"status": "error", "message": "Item Return ID is required"}
    
    if action == "return_item":
        return_lines = await get_list("item_return_line", {"item_return": item_return_id}, db=db)
        
        if not return_lines:
            return {"status": "error", "message": "No Item Return Lines found for this Item Return"}
        
        for line in return_lines:
            response = await _create_putaway(line, doc, db)
            if response["status"] == "error":
                return response
        
        return {"status": "success", "message": "Successfully created putaway record for returning parts"}
    
    return {"status": "success", "message": f"Item Return workflow '{action}' allowed"}


async def _create_putaway(line: dict, doc: Any, db: AsyncSession) -> dict:
    """
    Create Putaway record for returned item.
    
    Mirrors: create_putaway() from Frappe
    """
    return_type = getattr(doc, 'return_type', None)
    wo_activity_id = getattr(doc, 'work_order_activity', None)
    
    if return_type == "WO Parts Return":
        wo_activity = await get_value("work_order_activity", wo_activity_id, "*", db) if wo_activity_id else None
        wo_parts = await get_value("work_order_parts", line.get("work_order_parts"), "*", db) if line.get("work_order_parts") else None
        
        if not wo_parts:
            return {"status": "error", "message": "Work Order Parts not found"}
        
        putaway = await new_doc("putaway", db,
            putaway_type="Item Return",
            source_data_parts_return=line.get("id"),
            item=wo_parts.get("item"),
            qty=line.get("quantity_returned"),
            site=wo_activity.get("site") if wo_activity else None
        )
        await save_doc(putaway, db, commit=False)
        
        # Update inventory via putaway post-save hook
        await _update_inventory_return(putaway, db)
        
        return {"status": "success", "message": "Successfully created putaway record"}
    
    elif return_type == "WO Equipment Return":
        wo_activity = await get_value("work_order_activity", wo_activity_id, "*", db) if wo_activity_id else None
        wo_equipment = await get_value("work_order_equipment", line.get("work_order_equipment"), "*", db) if line.get("work_order_equipment") else None
        
        if not wo_equipment:
            return {"status": "error", "message": "Work Order Equipment not found"}
        
        equipment = await get_value("equipment", wo_equipment.get("equipment"), "*", db)
        inventory = await get_value("inventory", equipment.get("inventory"), "*", db) if equipment else None
        
        putaway = await new_doc("putaway", db,
            putaway_type="Item Return",
            source_data_parts_return=line.get("id"),
            item=inventory.get("item") if inventory else None,
            serial_number=inventory.get("serial_number") if inventory else None,
            store=inventory.get("store_location") if inventory else None,
            bin=inventory.get("bin_location") if inventory else None,
            zone=inventory.get("zone") if inventory else None,
            qty=line.get("quantity_returned"),
            site=wo_activity.get("site") if wo_activity else None
        )
        await save_doc(putaway, db, commit=False)
        
        # Update inventory via putaway post-save hook
        await _update_inventory_return(putaway, db)
        
        return {"status": "success", "message": "Successfully created putaway record"}
    
    return {"status": "error", "message": f"Unknown return type: {return_type}"}


async def _update_inventory_return(putaway: Any, db: AsyncSession) -> dict:
    """
    Update inventory quantities when items are returned.
    
    Mirrors: update_inventory_return() from Frappe putaway.py
    """
    source_return_line_id = getattr(putaway, 'source_data_parts_return', None)
    
    if not source_return_line_id:
        return {"status": "error", "message": "Missing source_data_parts_return on Putaway"}
    
    parts_return = await get_value("item_return_line", source_return_line_id, "*", db)
    if not parts_return:
        return {"status": "error", "message": f"Item Return Line not found: {source_return_line_id}"}
    
    item_return_id = parts_return.get("item_return")
    item_return = await get_value("item_return", item_return_id, "*", db) if item_return_id else None
    
    if not item_return:
        return {"status": "error", "message": f"Item Return not found: {item_return_id}"}
    
    qty_returned = parts_return.get("quantity_returned", 0) or 0
    if qty_returned <= 0:
        return {"status": "error", "message": f"Invalid quantity_returned: {qty_returned}"}
    
    return_type = item_return.get("return_type")
    
    if return_type == "WO Parts Return":
        wo_parts_id = parts_return.get("work_order_parts")
        if wo_parts_id:
            wo_part = await get_doc("work_order_parts", wo_parts_id, db)
            if wo_part:
                qty_return = getattr(wo_part, 'quantity_returned', 0) or 0
                wo_part.quantity_returned = qty_return + qty_returned
                await save_doc(wo_part, db, commit=False)
    
    elif return_type == "WO Equipment Return":
        wo_equipment_id = parts_return.get("work_order_equipment")
        if wo_equipment_id:
            wo_equipment = await get_value("work_order_equipment", wo_equipment_id, "*", db)
            equipment = await get_value("equipment", wo_equipment.get("equipment"), "*", db) if wo_equipment else None
            
            if equipment:
                equip_doc = await get_doc("equipment", equipment["id"], db)
                if equip_doc:
                    equip_doc.custodian = None
                    await save_doc(equip_doc, db, commit=False)
                
                inventory = await get_value("inventory", equipment.get("inventory"), "*", db)
                if inventory and inventory.get("asset"):
                    asset = await get_doc("asset", inventory["asset"], db)
                    if asset:
                        asset.workflow_state = "inactive"
                        await save_doc(asset, db, commit=False)
    
    # Update Inventory and Item quantities
    inv_filter = {}
    if parts_return.get("item"):
        inv_filter["item"] = parts_return["item"]
    if parts_return.get("serial_number"):
        inv_filter["serial_number"] = parts_return["serial_number"]
    if parts_return.get("store"):
        inv_filter["store_location"] = parts_return["store"]
    if parts_return.get("bin"):
        inv_filter["bin_location"] = parts_return["bin"]
    if parts_return.get("zone"):
        inv_filter["zone"] = parts_return["zone"]
    
    if inv_filter:
        inventory = await get_value("inventory", inv_filter, "*", db)
        if inventory:
            inv_doc = await get_doc("inventory", inventory["id"], db)
            item = await get_doc("item", inventory.get("item"), db) if inventory.get("item") else None
            
            if inv_doc:
                available = (getattr(inv_doc, 'available_inv', 0) or 0) + qty_returned
                actual = (getattr(inv_doc, 'actual_inv', 0) or 0) + qty_returned
                inv_doc.available_inv = available
                inv_doc.actual_inv = actual
                await save_doc(inv_doc, db, commit=False)
            
            if item:
                total_available = (getattr(item, 'available_capacity', 0) or 0) + qty_returned
                total_actual = (getattr(item, 'actual_qty_on_hand', 0) or 0) + qty_returned
                item.available_capacity = total_available
                item.actual_qty_on_hand = total_actual
                await save_doc(item, db, commit=False)

            # Stock ledger audit trail
            if inv_doc:
                await ledger_for_return(
                    db=db,
                    item_return_id=item_return_id,
                    item_id=inventory.get("item"),
                    qty=qty_returned,
                    unit_cost=inventory.get("base_unit_cost") or 0,
                    store=inventory.get("store_location"),
                    serial_no=inventory.get("serial_number"),
                    site=inventory.get("site"),
                )
    
    await db.commit()
    return {"status": "success", "message": "Successfully updated inventory"}
