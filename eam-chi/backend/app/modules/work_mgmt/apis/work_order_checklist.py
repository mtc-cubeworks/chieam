"""
Work Order Checklist Post-Save Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_checklist/work_order_checklist.py
- create_checklist_dtl(doc)

When a Work Order Checklist is created with a checklist link,
auto-create Work Order Checklist Details from Checklist Details.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_value, get_list, new_doc, save_doc


async def create_checklist_details_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: Auto-create WO Checklist Details from the linked Checklist.
    """
    wo_checklist_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    checklist_id = getattr(doc, 'checklist', None)

    if not wo_checklist_id or not checklist_id:
        return {"status": "success"}

    # Get checklist details from the master checklist
    checklist_details = await get_list(
        "checklist_details",
        {"checklist": checklist_id},
        db=db
    )

    if not checklist_details:
        return {"status": "success"}

    created_count = 0
    for detail in checklist_details:
        wo_detail = await new_doc("work_order_checklist_detail", db,
            work_order_checklist=wo_checklist_id,
            item_name=detail.get("item_name"),
            is_mandatory=detail.get("is_mandatory"),
        )
        if wo_detail:
            await save_doc(wo_detail, db, commit=False)
            created_count += 1

    if created_count > 0:
        await db.commit()

    return {"status": "success", "message": f"Created {created_count} checklist details" if created_count else ""}
