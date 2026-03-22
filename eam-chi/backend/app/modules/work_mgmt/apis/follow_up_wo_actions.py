"""
Follow-up Work Order Actions
===============================
Server action to create a follow-up Work Order from a completed WO.
Copies key fields (asset, location, job plan, safety notes) and links
the follow-up back to the original.
"""
from app.application.server_actions.registry import server_actions


@server_actions.register("work_order", "Create Follow-Up WO")
async def create_follow_up_wo(doc, ctx):
    """
    Create a new Work Order that references the current WO as parent.
    Pre-fills asset, location, job plan, and recommendations from the original.
    """
    from app.services.document import new_doc, save_doc

    wo_id = doc.id if hasattr(doc, "id") else getattr(doc, "name", None)

    follow_up = await new_doc("work_order", ctx.db,
        workflow_state="Draft",
        parent_work_order=wo_id,
        asset=getattr(doc, "asset", None),
        location=getattr(doc, "location", None),
        work_order_type=getattr(doc, "work_order_type", None),
        job_plan=getattr(doc, "job_plan", None),
        site=getattr(doc, "site", None),
        description=f"Follow-up from {wo_id}: {getattr(doc, 'recommendations', '') or ''}".strip(),
        loto_required=getattr(doc, "loto_required", None),
        safety_permit=getattr(doc, "safety_permit", None),
    )
    if not follow_up:
        return {"status": "error", "message": "Failed to create follow-up Work Order"}

    await save_doc(follow_up, ctx.db, commit=False)

    # Link back: set follow_up_work_order on the original WO
    doc.follow_up_work_order = follow_up.id
    await save_doc(doc, ctx.db, commit=False)

    await ctx.db.commit()

    return {
        "status": "success",
        "message": f"Follow-up Work Order {follow_up.id} created"
    }
