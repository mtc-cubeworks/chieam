"""
Job Plan Actions
==================
Server actions for applying a Job Plan to a Work Order.
Copies job plan tasks as WO activities and materials as WO parts.
"""
from app.application.server_actions.registry import server_actions


@server_actions.register("work_order", "Apply Job Plan")
async def apply_job_plan_to_wo(doc, ctx):
    """
    Copy tasks from a Job Plan to the Work Order as Work Order Activities
    and associated parts. Expects doc.job_plan to be set.
    """
    from app.services.document import get_doc, get_list, new_doc, save_doc

    job_plan_id = getattr(doc, "job_plan", None)
    if not job_plan_id:
        return {"status": "error", "message": "No Job Plan specified on this Work Order"}

    job_plan = await get_doc("job_plan", job_plan_id, ctx.db)
    if not job_plan:
        return {"status": "error", "message": f"Job Plan {job_plan_id} not found"}

    # Get job plan tasks ordered by sequence
    tasks = await get_list("job_plan_task", {"job_plan": job_plan_id}, db=ctx.db)
    tasks = sorted(tasks, key=lambda t: int(t.get("sequence", 0) or 0))

    wo_id = doc.id if hasattr(doc, "id") else getattr(doc, "name", None)
    activities_created = 0
    parts_created = 0

    for task in tasks:
        # Create WO Activity from task
        woa = await new_doc("work_order_activity", ctx.db,
            work_order=wo_id,
            description=task.get("task_description"),
            craft=task.get("craft_required"),
            estimated_hours=task.get("estimated_hours"),
            sequence=task.get("sequence"),
        )
        if woa:
            await save_doc(woa, ctx.db, commit=False)
            activities_created += 1

            # If task has material/part, create WO Parts
            item_id = task.get("item")
            quantity = task.get("quantity")
            if item_id and quantity:
                wo_part = await new_doc("work_order_parts", ctx.db,
                    work_order_activity=woa.id,
                    work_order=wo_id,
                    item=item_id,
                    quantity_required=float(quantity),
                )
                if wo_part:
                    await save_doc(wo_part, ctx.db, commit=False)
                    parts_created += 1

    # Update WO estimated hours from job plan
    if getattr(job_plan, "estimated_hours", None):
        doc.estimated_hours = job_plan.estimated_hours
        await save_doc(doc, ctx.db, commit=False)

    # Apply checklist if present
    checklist_id = getattr(job_plan, "checklist", None)
    if checklist_id:
        doc.checklist = checklist_id
        await save_doc(doc, ctx.db, commit=False)

    # Apply safety procedures
    safety = getattr(job_plan, "safety_procedures", None)
    if safety:
        doc.safety_notes = safety
        await save_doc(doc, ctx.db, commit=False)

    await ctx.db.commit()

    return {
        "status": "success",
        "message": f"Applied Job Plan: {activities_created} activities, {parts_created} parts created"
    }
