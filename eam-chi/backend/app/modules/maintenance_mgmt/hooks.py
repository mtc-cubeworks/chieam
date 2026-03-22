"""
Maintenance Management Module Hooks
=====================================
Registers entity lifecycle hooks with the hook registry.
"""
from app.application.hooks.registry import hook_registry


# =============================================================================
# After-Save Hooks
# =============================================================================

@hook_registry.after_save("planned_maintenance_activity")
async def planned_maintenance_activity_after_save(doc, ctx):
    """
    When a PMA is saved, auto-create a MaintenanceCalendar entry
    if one doesn't exist and the PMA has a maintenance_schedule (frequency).
    """
    from app.services.document import get_value, new_doc, save_doc

    pma_id = doc.id if hasattr(doc, 'id') else None
    if not pma_id:
        return

    schedule = getattr(doc, 'maintenance_schedule', None)
    plan_id = getattr(doc, 'maintenance_plan', None)
    activity_id = getattr(doc, 'maintenance_activity', None)

    if not schedule or not plan_id:
        return

    # Check if calendar already exists for this PMA
    existing = await get_value(
        "maintenance_calendar",
        {"planned_maintenance_activity": pma_id},
        "*",
        ctx.db,
    )
    if existing:
        return

    cal = await new_doc("maintenance_calendar", ctx.db,
        planned_maintenance_activity=pma_id,
        maintenance_plan=plan_id,
        maintenance_activity=activity_id,
        frequency=schedule,
    )
    if cal:
        await save_doc(cal, ctx.db)


@hook_registry.after_save("sensor_data")
async def sensor_data_after_save(doc, ctx):
    """
    When sensor data is recorded, check MaintenanceConditions.
    If a threshold is breached, auto-create a Maintenance Request
    for condition-based maintenance.
    """
    from app.services.document import get_value, get_list, new_doc, save_doc

    sensor_id = getattr(doc, 'sensor', None)
    value_str = getattr(doc, 'value', None)
    if not sensor_id or not value_str:
        return

    try:
        reading = float(value_str)
    except (ValueError, TypeError):
        return

    # Get sensor -> linked asset
    sensor = await get_value("sensor", sensor_id, "*", ctx.db)
    if not sensor:
        return

    asset_id = sensor.get("asset")
    asset_property_id = sensor.get("asset_property")

    # Update the asset property value with latest reading
    if asset_property_id:
        from app.services.document import get_doc
        prop_doc = await get_doc("asset_property", asset_property_id, ctx.db)
        if prop_doc:
            prop_doc.property_value = value_str
            await save_doc(prop_doc, ctx.db, commit=False)

    # Check maintenance conditions linked to this sensor
    conditions = await get_list(
        "maintenance_condition", {"sensor": sensor_id}, db=ctx.db
    )
    if not conditions:
        return

    for cond in conditions:
        operator = cond.get("comparison_operator")
        threshold_prop_id = cond.get("threshold_property")
        pma_id = cond.get("planned_maintenance_activity")

        if not operator or not threshold_prop_id or not pma_id:
            continue

        # Get threshold value from the property definition
        threshold_prop = await get_value("property", threshold_prop_id, "*", ctx.db)
        if not threshold_prop:
            continue

        try:
            threshold = float(threshold_prop.get("default_value") or 0)
        except (ValueError, TypeError):
            continue

        # Evaluate condition
        breached = False
        if operator == ">" and reading > threshold:
            breached = True
        elif operator == ">=" and reading >= threshold:
            breached = True
        elif operator == "<" and reading < threshold:
            breached = True
        elif operator == "<=" and reading <= threshold:
            breached = True
        elif operator == "==" and reading == threshold:
            breached = True

        if not breached:
            continue

        # Check if an open MR already exists for this sensor/PMA
        existing_mr = await get_value(
            "maintenance_request",
            {
                "planned_maintenance_activity": pma_id,
                "asset": asset_id,
            },
            "*",
            ctx.db,
        )
        if existing_mr and existing_mr.get("workflow_state") not in (
            "completed", "closed", "cancelled",
        ):
            continue

        # Auto-create MR for condition-based maintenance
        from datetime import datetime, timedelta

        mr = await new_doc("maintenance_request", ctx.db,
            workflow_state="Draft",
            description=f"Condition-based: sensor {sensor.get('sensor_name', sensor_id)} "
                        f"reading {reading} {operator} threshold {threshold}",
            planned_maintenance_activity=pma_id,
            asset=asset_id,
            due_date=(datetime.now() + timedelta(days=3)).date(),
            site=sensor.get("site"),
            request_type="Condition Based",
        )
        if mr:
            await save_doc(mr, ctx.db)


@hook_registry.after_save("maintenance_order_detail")
async def maintenance_order_detail_after_save(doc, ctx):
    """
    When an MO detail is saved, copy MR description to the detail
    if not already set.
    """
    from app.services.document import get_value, save_doc

    mr_id = getattr(doc, 'maintenance_request', None)
    description = getattr(doc, 'description', None)

    if not mr_id or description:
        return

    mr = await get_value("maintenance_request", mr_id, "*", ctx.db)
    if mr and mr.get("description"):
        doc.description = mr["description"]
        await save_doc(doc, ctx.db)


# =============================================================================
# Workflow Hooks - All routed through central workflow_router
# =============================================================================

@hook_registry.workflow("maintenance_request")
async def maintenance_request_workflow_hook(ctx):
    from app.modules.maintenance_mgmt.workflow_router import route_workflow
    return await route_workflow("maintenance_request", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("maintenance_order")
async def maintenance_order_workflow_hook(ctx):
    from app.modules.maintenance_mgmt.workflow_router import route_workflow
    return await route_workflow("maintenance_order", ctx.doc, ctx.action, ctx.db, ctx.user)


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.maintenance_mgmt.apis.maintenance_request_actions  # noqa: F401
