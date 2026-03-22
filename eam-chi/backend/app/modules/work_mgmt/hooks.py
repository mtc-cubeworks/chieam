"""
Work Management Module Hooks
==============================
Registers entity lifecycle hooks with the hook registry.
"""
from app.application.hooks.registry import hook_registry


@hook_registry.after_save("work_order_activity")
async def work_order_activity_after_save(doc, ctx):
    from app.modules.work_mgmt.apis.work_order_activity import create_wo_labor_on_save
    return await create_wo_labor_on_save(doc, ctx.db)


@hook_registry.after_save("work_order_labor")
async def work_order_labor_after_save(doc, ctx):
    from app.modules.work_mgmt.apis.work_order_labor import update_wo_labor_lead
    return await update_wo_labor_lead(doc, ctx.db)


@hook_registry.after_save("work_order_checklist")
async def work_order_checklist_after_save(doc, ctx):
    from app.modules.work_mgmt.apis.work_order_checklist import create_checklist_details_on_save
    return await create_checklist_details_on_save(doc, ctx.db)


@hook_registry.after_save("work_order_labor_assignment")
async def work_order_labor_assignment_after_save(doc, ctx):
    from app.modules.work_mgmt.apis.work_order_labor_assignment import update_labor_availability_on_save
    return await update_labor_availability_on_save(doc, ctx.db)


@hook_registry.after_save("work_order_equipment_assignment")
async def work_order_equipment_assignment_after_save(doc, ctx):
    from app.modules.work_mgmt.apis.work_order_equipment_assignment import update_equipment_availability_on_save
    return await update_equipment_availability_on_save(doc, ctx.db)


# =============================================================================
# WO Cost Rollup Hooks
# =============================================================================

@hook_registry.after_save("work_order_labor_actual_hours")
async def wo_labor_actual_hours_after_save(doc, ctx):
    """Roll up labor costs to Work Order when actual hours are recorded."""
    await _rollup_wo_costs(doc, ctx)


@hook_registry.after_save("work_order_equipment_actual_hours")
async def wo_equipment_actual_hours_after_save(doc, ctx):
    """Roll up equipment costs to Work Order when actual hours are recorded."""
    await _rollup_wo_costs(doc, ctx)


@hook_registry.after_save("work_order_parts")
async def work_order_parts_after_save(doc, ctx):
    """Roll up parts costs to Work Order when parts are added/updated."""
    await _rollup_wo_costs(doc, ctx)


async def _rollup_wo_costs(doc, ctx):
    """Calculate total WO cost from labor + equipment + parts actuals."""
    from app.services.document import get_list, get_doc, get_value, save_doc

    # Find the parent WO - navigate through WO Activity if needed
    wo_id = getattr(doc, "work_order", None)
    if not wo_id:
        wo_activity_id = getattr(doc, "work_order_activity", None)
        if not wo_activity_id:
            wo_labor_id = getattr(doc, "work_order_labor", None)
            if wo_labor_id:
                wo_labor = await get_value("work_order_labor", wo_labor_id, "*", ctx.db)
                wo_activity_id = wo_labor.get("work_order_activity") if wo_labor else None
            wo_equip_id = getattr(doc, "work_order_equipment", None)
            if wo_equip_id:
                wo_equip = await get_value("work_order_equipment", wo_equip_id, "*", ctx.db)
                wo_activity_id = wo_equip.get("work_order_activity") if wo_equip else None
        if wo_activity_id:
            woa = await get_value("work_order_activity", wo_activity_id, "*", ctx.db)
            wo_id = woa.get("work_order") if woa else None

    if not wo_id:
        return

    # Get all WO Activities for this WO
    wo_activities = await get_list("work_order_activity", {"work_order": wo_id}, db=ctx.db)

    total_labor_cost = 0.0
    total_equipment_cost = 0.0
    total_parts_cost = 0.0

    for woa in wo_activities:
        woa_id = woa.get("id")

        # Sum labor actual hours × rate
        labor_records = await get_list("work_order_labor", {"work_order_activity": woa_id}, db=ctx.db)
        for lr in labor_records:
            lr_id = lr.get("id")
            actual_hours_list = await get_list("work_order_labor_actual_hours", {"work_order_labor": lr_id}, db=ctx.db)
            for ah in actual_hours_list:
                hours = float(ah.get("actual_hours", 0) or 0)
                rate = float(ah.get("rate", 0) or lr.get("rate", 0) or 0)
                total_labor_cost += hours * rate

        # Sum equipment actual hours × rate
        equip_records = await get_list("work_order_equipment", {"work_order_activity": woa_id}, db=ctx.db)
        for er in equip_records:
            er_id = er.get("id")
            actual_hours_list = await get_list("work_order_equipment_actual_hours", {"work_order_equipment": er_id}, db=ctx.db)
            for ah in actual_hours_list:
                hours = float(ah.get("actual_hours", 0) or 0)
                rate = float(ah.get("rate", 0) or er.get("rate", 0) or 0)
                total_equipment_cost += hours * rate

        # Sum parts cost (quantity_issued × unit_cost)
        parts_records = await get_list("work_order_parts", {"work_order_activity": woa_id}, db=ctx.db)
        for pr in parts_records:
            qty_issued = float(pr.get("quantity_issued", 0) or 0)
            unit_cost = float(pr.get("unit_cost", 0) or 0)
            total_parts_cost += qty_issued * unit_cost

    total_cost = round(total_labor_cost + total_equipment_cost + total_parts_cost, 2)

    wo_doc = await get_doc("work_order", wo_id, ctx.db)
    if wo_doc:
        changed = False
        if getattr(wo_doc, "total_labor_cost", None) != round(total_labor_cost, 2):
            wo_doc.total_labor_cost = round(total_labor_cost, 2)
            changed = True
        if getattr(wo_doc, "total_equipment_cost", None) != round(total_equipment_cost, 2):
            wo_doc.total_equipment_cost = round(total_equipment_cost, 2)
            changed = True
        if getattr(wo_doc, "total_parts_cost", None) != round(total_parts_cost, 2):
            wo_doc.total_parts_cost = round(total_parts_cost, 2)
            changed = True
        if getattr(wo_doc, "total_cost", None) != total_cost:
            wo_doc.total_cost = total_cost
            changed = True
        if changed:
            await save_doc(wo_doc, ctx.db)


# =============================================================================
# Workflow Hooks - All routed through central workflow_router
# =============================================================================

@hook_registry.workflow("work_order")
async def work_order_workflow_hook(ctx):
    from app.modules.work_mgmt.workflow_router import route_workflow
    return await route_workflow("work_order", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("work_order_activity")
async def work_order_activity_workflow_hook(ctx):
    from app.modules.work_mgmt.workflow_router import route_workflow
    return await route_workflow("work_order_activity", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("work_order_parts")
async def work_order_parts_workflow_hook(ctx):
    from app.modules.work_mgmt.workflow_router import route_workflow
    return await route_workflow("work_order_parts", ctx.doc, ctx.action, ctx.db, ctx.user)


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.work_mgmt.apis.work_order_activity_actions  # noqa: F401
    import app.modules.work_mgmt.apis.parts_reservation_actions  # noqa: F401
    import app.modules.work_mgmt.apis.job_plan_actions  # noqa: F401
    import app.modules.work_mgmt.apis.follow_up_wo_actions  # noqa: F401
