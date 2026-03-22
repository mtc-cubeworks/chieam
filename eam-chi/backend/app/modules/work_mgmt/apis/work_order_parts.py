"""
Work Order Parts Entity Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_parts/work_order_parts.py
- check_wo_part_state(wo_parts, action)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list


async def check_work_order_parts_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Work Order Parts entity.
    
    Mirrors: check_wo_part_state() from ci_eam/work_management/doctype/work_order_parts/work_order_parts.py
    """
    if not doc:
        return {"status": "error", "message": "Work Order Parts not specified"}
    
    wo_parts_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not wo_parts_id:
        return {"status": "error", "message": "Work Order Parts ID is required"}
    
    wo_activity_id = getattr(doc, 'work_order_activity', None)
    
    if action == "assigned_partial_items":
        # Check for Work Order Parts Issue or Reservation
        wo_parts_issue = await get_value("work_order_parts_issue", {"work_order_parts": wo_parts_id}, "*", db)
        wo_parts_reservation = await get_value("work_order_parts_reservation", {"work_order_parts": wo_parts_id}, "*", db)
        
        if not wo_parts_issue and not wo_parts_reservation:
            return {"status": "error", "message": "Cannot assign partial: no Parts Issue or Reservation found"}
        
        return {"status": "success", "message": "Work Order Parts partially assigned"}
    
    elif action == "assigned_all_items":
        # Check for Work Order Parts Issue or Reservation
        wo_parts_issue = await get_value("work_order_parts_issue", {"work_order_parts": wo_parts_id}, "*", db)
        wo_parts_reservation = await get_value("work_order_parts_reservation", {"work_order_parts": wo_parts_id}, "*", db)
        
        if not wo_parts_issue and not wo_parts_reservation:
            return {"status": "error", "message": "Cannot assign all: no Parts Issue or Reservation found"}
        
        return {"status": "success", "message": "Work Order Parts fully assigned"}
    
    elif action == "start":
        # Try to start the parent Work Order Activity if it's in 'scheduled' state
        if wo_activity_id:
            wo_activity = await get_doc("work_order_activity", wo_activity_id, db)
            if wo_activity and getattr(wo_activity, 'workflow_state', None) == "scheduled":
                # Workflow system will handle the transition
                pass
        
        return {"status": "success", "message": "Work Order Parts started"}
    
    elif action == "complete":
        # Check for Work Order Parts Return
        wo_parts_return = await get_value("work_order_parts_return", {"work_order_parts": wo_parts_id}, "*", db)
        
        # Parts can complete even without return (all parts consumed)
        return {"status": "success", "message": "Work Order Parts completed"}
    
    return {"status": "success", "message": f"Work Order Parts workflow '{action}' allowed"}
