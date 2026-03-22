"""
Work Order Labor Post-Save Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_labor/work_order_labor.py
- update_wo_labor_lead(doc): Ensure only one lead per WOA; first labor is auto-lead
- assign_wo_labor(doc): (Frappe-specific assign_to — simplified for FastAPI)
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc


async def update_wo_labor_lead(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: Ensure only one lead per Work Order Activity.
    If this is the first labor for the WOA, set as lead.
    If this labor is set as lead, unset any other leads.
    """
    wo_labor_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    wo_activity_id = getattr(doc, 'work_order_activity', None)

    if not wo_labor_id or not wo_activity_id:
        return {"status": "success"}

    wo_labor = await get_doc("work_order_labor", wo_labor_id, db)
    if not wo_labor:
        return {"status": "error", "message": f"Work Order Labor {wo_labor_id} not found."}

    # Get all labors for this work order activity
    wo_labor_list = await get_list(
        "work_order_labor",
        {"work_order_activity": wo_activity_id},
        db=db
    )

    # If this is the only/first labor, set as lead
    if len(wo_labor_list) <= 1:
        if not getattr(wo_labor, 'lead', False):
            wo_labor.lead = True
            await save_doc(wo_labor, db)
        return {"status": "success", "message": f"Set {wo_labor_id} as lead (first labor)."}

    # If this labor is set as lead, unset any other leads
    is_lead = getattr(wo_labor, 'lead', False)
    if is_lead:
        for labor in wo_labor_list:
            labor_id = labor.get("id")
            if labor_id != wo_labor_id and labor.get("lead"):
                other_labor = await get_doc("work_order_labor", labor_id, db)
                if other_labor:
                    other_labor.lead = False
                    await save_doc(other_labor, db, commit=False)
        await db.commit()

    return {"status": "success", "message": f"Updated labor lead status for {wo_labor_id}."}
