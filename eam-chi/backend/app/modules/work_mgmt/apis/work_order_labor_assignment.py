"""
Work Order Labor Assignment Entity Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_labor_assignment/work_order_labor_assignment.py
- update_wolabor_trade_labor_avail(doc)
- search_employee_query(...)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc


async def update_labor_availability_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After save hook: Update Work Order Labor state and Trade/Labor Availability.
    
    Mirrors: update_wolabor_trade_labor_avail() from Frappe
    """
    wo_labor_id = getattr(doc, 'work_order_labor', None)
    labor_id = getattr(doc, 'labor', None)
    start_datetime = getattr(doc, 'start_datetime', None)
    end_datetime = getattr(doc, 'end_datetime', None)
    
    if not wo_labor_id:
        return {"status": "success"}
    
    # Get Work Order Labor
    wo_labor = await get_doc("work_order_labor", wo_labor_id, db)
    if not wo_labor:
        return {"status": "error", "message": f"Work Order Labor {wo_labor_id} not found"}
    
    # Count assignments
    assignments = await get_list("work_order_labor_assignment", {"work_order_labor": wo_labor_id}, db=db)
    assignment_count = len(assignments) if assignments else 0
    
    # Get Maintenance Trade to check required quantity
    trade_id = getattr(wo_labor, 'trade', None)
    wo_activity_id = getattr(wo_labor, 'work_order_activity', None)
    
    maint_req = await get_value("maintenance_request", {"work_order_activity": wo_activity_id}, "*", db) if wo_activity_id else None
    required_qty = 1  # Default
    
    if maint_req and maint_req.get("planned_maintenance_activity"):
        pma = await get_value("planned_maintenance_activity", maint_req["planned_maintenance_activity"], "*", db)
        if pma:
            maint_trade = await get_value("maintenance_trade", {"maintenance_activity": pma.get("maintenance_activity"), "trade": trade_id}, "*", db)
            if maint_trade:
                required_qty = maint_trade.get("required_qty", 1) or 1
    
    # Update Work Order Labor workflow state
    if assignment_count >= required_qty:
        wo_labor.workflow_state = "assigned_all_items"
    elif assignment_count > 0:
        wo_labor.workflow_state = "assigned_partial_items"
    
    await save_doc(wo_labor, db, commit=False)
    
    # Update Trade Availability - mark time slots as 'Reserved'
    if trade_id and start_datetime and end_datetime:
        trade_avail = await get_value("trade_availability", {"trade": trade_id, "specific_datetime": start_datetime}, "*", db)
        if trade_avail:
            ta_doc = await get_doc("trade_availability", trade_avail["id"], db)
            if ta_doc:
                reserved = getattr(ta_doc, 'reserved_capacity', 0) or 0
                ta_doc.reserved_capacity = reserved + 1
                available = getattr(ta_doc, 'available_capacity', 0) or 0
                ta_doc.available_capacity = max(0, available - 1)
                await save_doc(ta_doc, db, commit=False)
    
    # Update Labor Availability Details - mark as 'Reserved'
    if labor_id and start_datetime:
        labor_avail_dtl = await get_value("labor_availability_details", {"labor": labor_id, "specific_datetime": start_datetime}, "*", db)
        if labor_avail_dtl:
            lad_doc = await get_doc("labor_availability_details", labor_avail_dtl["id"], db)
            if lad_doc:
                lad_doc.status = "Reserved"
                await save_doc(lad_doc, db, commit=False)
    
    await db.commit()
    return {"status": "success", "message": "Labor availability updated"}
