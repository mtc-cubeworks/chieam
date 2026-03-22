"""
Work Order Equipment Assignment Entity Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_equipment_assignment/work_order_equipment_assignment.py
- update_woequip_asset_equip_avail(doc)
- search_equipment_query(...)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc


async def update_equipment_availability_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After save hook: Update Work Order Equipment state and Asset Class/Equipment Availability.
    
    Mirrors: update_woequip_asset_equip_avail() from Frappe
    """
    wo_equip_id = getattr(doc, 'work_order_equipment', None)
    equipment_id = getattr(doc, 'equipment', None)
    start_datetime = getattr(doc, 'start_datetime', None)
    end_datetime = getattr(doc, 'end_datetime', None)
    
    if not wo_equip_id:
        return {"status": "success"}
    
    # Get Work Order Equipment
    wo_equip = await get_doc("work_order_equipment", wo_equip_id, db)
    if not wo_equip:
        return {"status": "error", "message": f"Work Order Equipment {wo_equip_id} not found"}
    
    # Count assignments
    assignments = await get_list("work_order_equipment_assignment", {"work_order_equipment": wo_equip_id}, db=db)
    assignment_count = len(assignments) if assignments else 0
    
    # Get Maintenance Equipment to check required quantity
    item_id = getattr(wo_equip, 'item', None)
    wo_activity_id = getattr(wo_equip, 'work_order_activity', None)
    
    maint_req = await get_value("maintenance_request", {"work_order_activity": wo_activity_id}, "*", db) if wo_activity_id else None
    required_qty = 1  # Default
    
    if maint_req and maint_req.get("planned_maintenance_activity"):
        pma = await get_value("planned_maintenance_activity", maint_req["planned_maintenance_activity"], "*", db)
        if pma:
            maint_equip = await get_value("maintenance_equipment", {"maintenance_activity": pma.get("maintenance_activity")}, "*", db)
            if maint_equip:
                required_qty = maint_equip.get("required_qty", 1) or 1
    
    # Update Work Order Equipment workflow state
    if assignment_count >= required_qty:
        wo_equip.workflow_state = "assigned_all_items"
    elif assignment_count > 0:
        wo_equip.workflow_state = "assigned_partial_items"
    
    await save_doc(wo_equip, db, commit=False)
    
    # Update Asset Class Availability - mark time slots as 'Reserved'
    if equipment_id and start_datetime:
        equipment = await get_doc("equipment", equipment_id, db)
        if equipment:
            inventory_id = getattr(equipment, 'inventory', None)
            if inventory_id:
                inventory = await get_value("inventory", inventory_id, "*", db)
                if inventory:
                    item = await get_value("item", inventory.get("item"), "*", db)
                    if item and item.get("asset_class"):
                        asset_class_avail = await get_value("asset_class_availability", {"asset_class": item["asset_class"], "specific_datetime": start_datetime}, "*", db)
                        if asset_class_avail:
                            aca_doc = await get_doc("asset_class_availability", asset_class_avail["id"], db)
                            if aca_doc:
                                reserved = getattr(aca_doc, 'reserved_capacity', 0) or 0
                                aca_doc.reserved_capacity = reserved + 1
                                available = getattr(aca_doc, 'available_capacity', 0) or 0
                                aca_doc.available_capacity = max(0, available - 1)
                                await save_doc(aca_doc, db, commit=False)
    
    # Update Equipment Availability Details - mark as 'Reserved'
    if equipment_id and start_datetime:
        equip_avail_dtl = await get_value("equipment_availability_details", {"equipment": equipment_id, "specific_datetime": start_datetime}, "*", db)
        if equip_avail_dtl:
            ead_doc = await get_doc("equipment_availability_details", equip_avail_dtl["id"], db)
            if ead_doc:
                ead_doc.status = "Reserved"
                await save_doc(ead_doc, db, commit=False)
    
    await db.commit()
    return {"status": "success", "message": "Equipment availability updated"}
