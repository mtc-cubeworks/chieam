"""
Maintenance Order Entity Business Logic

Mirrors: ci_eam/maintenance_management/doctype/maintenance_order/maintenance_order.py
- generate_work_order(doc)
- create_work_order(...)
- create_work_order_activity(...)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def generate_work_order_from_maintenance_order(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Generate Work Order from Maintenance Order.
    
    Mirrors: generate_work_order() from ci_eam/maintenance_management/doctype/maintenance_order/maintenance_order.py
    """
    if not doc:
        return {"status": "error", "message": "Input document is required"}
    
    mo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not mo_id:
        return {"status": "error", "message": "Maintenance Order name is required"}
    
    # Check if work order already exists
    existing_wo = getattr(doc, 'work_order', None)
    if existing_wo:
        return {"status": "error", "message": "Work Order already exists for this Maintenance Order"}
    
    # Get maintenance order details
    mo_details = await get_list("maintenance_order_detail", {"maintenance_order": mo_id}, db=db, order_by="seq_num")
    
    if not mo_details:
        return {"status": "error", "message": "No Maintenance Order Details found for this Maintenance Order"}
    
    # Create Work Order
    wo_description = f"For Maintenance Order: {mo_id}."
    new_work_order = await new_doc("work_order", db,
        description=wo_description,
        workflow_state="requested"
    )
    await save_doc(new_work_order, db, commit=False)
    
    # Process each maintenance order detail
    for item in mo_details:
        maint_req_id = item.get("maint_req")
        if not maint_req_id:
            continue
        
        maint_req = await get_value("maintenance_request", {"id": maint_req_id}, "*", db)
        if maint_req:
            wo_activity_id = maint_req.get("work_order_activity")
            if wo_activity_id:
                # Update work order activity with work order reference
                wo_activity = await get_doc("work_order_activity", wo_activity_id, db)
                if wo_activity:
                    wo_activity.work_order = new_work_order.id
                    await save_doc(wo_activity, db, commit=False)
            
            # Update maintenance request workflow state to Release
            mr_doc = await get_doc("maintenance_request", maint_req_id, db)
            if mr_doc:
                mr_doc.workflow_state = "release"
                await save_doc(mr_doc, db, commit=False)
    
    # Update maintenance order with work order reference
    doc.work_order = new_work_order.id
    await save_doc(doc, db, commit=False)
    
    # Approve the work order
    new_work_order.workflow_state = "approved"
    await save_doc(new_work_order, db)
    
    return {
        "status": "success",
        "message": "Successfully created work order record",
        "action": "generate_id",
        "path": f"/work_order/{new_work_order.id}"
    }
