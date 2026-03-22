"""
Core EAM Module Hooks
======================
Registers entity lifecycle hooks with the hook registry.
"""
from app.application.hooks.registry import hook_registry


@hook_registry.after_save("organization")
async def organization_after_save(doc, ctx):
    return {"status": "success", "message": f"Organization '{getattr(doc, 'organization_name', doc.id)}' post-save processed"}


@hook_registry.after_save("site")
async def site_after_save(doc, ctx):
    return {"status": "success", "message": f"Site '{getattr(doc, 'site_name', doc.id)}' post-save processed"}


@hook_registry.after_save("trade_availability")
async def trade_availability_after_save(doc, ctx):
    from app.modules.core_eam.apis.trade_availability import calculate_trade_capacity
    return await calculate_trade_capacity(doc, ctx.db)


@hook_registry.after_save("employee_site")
async def employee_site_after_save(doc, ctx):
    from app.modules.core_eam.apis.employee_site import populate_site_field
    return await populate_site_field(doc, ctx.db)


@hook_registry.after_delete("employee_site")
async def employee_site_after_delete(doc, ctx):
    from app.modules.core_eam.apis.employee_site import remove_site_field
    return await remove_site_field(doc, ctx.db)


# =============================================================================
# Leave Application Workflow Hook
# =============================================================================

@hook_registry.workflow("leave_application")
async def leave_application_workflow_hook(ctx):
    """
    When leave is approved, mark the labor as unavailable
    for the leave dates by creating LaborAvailabilityDetails
    with status='On Leave'.
    """
    from app.services.document import get_value, get_list, get_doc, new_doc, save_doc
    from datetime import timedelta

    doc = ctx.doc
    action = ctx.action

    if action not in ("approve", "Approve"):
        return {"status": "success", "message": f"Leave application workflow '{action}' allowed"}

    labor_id = getattr(doc, 'labor', None)
    from_date = getattr(doc, 'from_date', None)
    to_date = getattr(doc, 'to_date', None)
    reason = getattr(doc, 'reason', None) or "Leave"

    if not labor_id or not from_date or not to_date:
        return {"status": "success", "message": "Leave approved (no labor/date info to update availability)"}

    # Iterate through each day in the leave range
    current = from_date.date() if hasattr(from_date, 'date') else from_date
    end = to_date.date() if hasattr(to_date, 'date') else to_date
    created = 0

    while current <= end:
        # Find or create LaborAvailability for this labor + date
        la = await get_value(
            "labor_availability",
            {"labor": labor_id, "date": current},
            "*",
            ctx.db,
        )
        if not la:
            la_doc = await new_doc("labor_availability", ctx.db,
                labor=labor_id,
                laborer=getattr(doc, 'laborer', None),
                date=current,
            )
            if la_doc:
                await save_doc(la_doc, ctx.db, commit=False)
                la = {"id": la_doc.id}

        if la:
            # Create detail entries marking all hours as on leave
            detail = await new_doc("labor_availability_details", ctx.db,
                labor_availability=la.get("id") if isinstance(la, dict) else la.id,
                hour="All Day",
                status="On Leave",
                reason=reason,
            )
            if detail:
                await save_doc(detail, ctx.db, commit=False)
                created += 1

        current += timedelta(days=1)

    await ctx.db.commit()
    return {
        "status": "success",
        "message": f"Leave approved. Updated availability for {created} day(s).",
    }


# =============================================================================
# Labor after_save: denormalize laborer name
# =============================================================================

@hook_registry.after_save("labor")
async def labor_after_save(doc, ctx):
    """When a Labor record is saved, sync the laborer name to linked records."""
    from app.services.document import get_value

    labor_id = doc.id if hasattr(doc, 'id') else None
    laborer_name = getattr(doc, 'laborer', None)
    if not labor_id or not laborer_name:
        return

    # Update trade_labor records with the laborer name
    from app.services.document import get_list, get_doc, save_doc
    trade_labors = await get_list("trade_labor", {"labor": labor_id}, db=ctx.db)
    for tl in trade_labors:
        if tl.get("laborer") != laborer_name:
            tl_doc = await get_doc("trade_labor", tl["id"], ctx.db)
            if tl_doc:
                tl_doc.laborer = laborer_name
                await save_doc(tl_doc, ctx.db, commit=False)


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    pass
