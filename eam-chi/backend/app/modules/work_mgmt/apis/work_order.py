"""
Work Order Entity Business Logic

Mirrors: ci_eam/work_management/doctype/work_order/work_order.py
- check_wo_order_state(work_order, action)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_list


async def check_work_order_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Work Order entity.
    
    Mirrors: check_wo_order_state() from ci_eam/work_management/doctype/work_order/work_order.py
    
    Validates:
    - Approve: Always allowed
    - Start: All Work Order Activities must be in 'Ready' state
    - Complete: All Work Order Activities must be 'Completed' or 'Closed'
    """
    if not doc:
        return {"status": "error", "message": "Work Order not specified"}
    
    work_order_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not work_order_id:
        return {"status": "error", "message": "Work Order ID is required"}
    
    # Get all Work Order Activities for this Work Order
    wo_activities = await get_list(
        "work_order_activity",
        {"work_order": work_order_id},
        db=db,
        as_dict=True
    )
    
    if not wo_activities:
        return {"status": "error", "message": "No work order activities found"}
    
    if action == "approve":
        return {"status": "success", "message": "Work Order is approved"}
    
    elif action == "start":
        # All activities must be in 'ready' state
        ready_count = sum(1 for a in wo_activities if a.get("workflow_state") == "ready")
        
        if ready_count == len(wo_activities):
            return {"status": "success", "message": "Work Order is in progress"}
        else:
            return {
                "status": "error",
                "message": "Cannot start Work Order because not all Work Order Activities are ready"
            }
    
    elif action == "complete":
        # All activities must be 'completed' or 'closed'
        completed_count = sum(
            1 for a in wo_activities 
            if a.get("workflow_state") in ["completed", "closed"]
        )
        
        if completed_count == len(wo_activities):
            return {"status": "success", "message": "Work Order is complete"}
        else:
            return {
                "status": "error",
                "message": "Cannot complete Work Order because not all Work Order Activities are complete"
            }
    
    elif action == "reopen":
        return {"status": "success", "message": "Work Order reopened"}
    
    return {"status": "success", "message": f"Work Order workflow '{action}' allowed"}
