"""
Asset Management Module Hooks
===============================
Registers entity lifecycle hooks with the hook registry.
"""
from app.application.hooks.registry import hook_registry


@hook_registry.before_save("asset")
async def asset_before_save(doc, ctx):
    from app.modules.asset_management.apis.asset import populate_asset_names
    doc = await populate_asset_names(doc, ctx.db)
    return doc


@hook_registry.after_save("asset")
async def asset_after_save(doc, ctx):
    from app.modules.asset_management.apis.asset import populate_asset_properties, provision_inventory
    await populate_asset_properties(doc, ctx.db)
    await provision_inventory(doc, ctx.db)


@hook_registry.after_save("asset_class")
async def asset_class_after_save(doc, ctx):
    from app.modules.asset_management.apis.asset_class import populate_asset_class_prop_and_maint_plan
    return await populate_asset_class_prop_and_maint_plan(doc, ctx)


@hook_registry.after_save("breakdown")
async def breakdown_after_save(doc, ctx):
    from app.modules.asset_management.apis.breakdown import create_update_equip_availability_on_save
    return await create_update_equip_availability_on_save(doc, ctx.db)


@hook_registry.after_save("disposed")
async def disposed_after_save(doc, ctx):
    from app.modules.asset_management.apis.disposed import create_purchase_request_on_dispose
    return await create_purchase_request_on_dispose(doc, ctx.db, ctx.user)


@hook_registry.after_save("asset_class_property")
async def asset_class_property_after_save(doc, ctx):
    from app.modules.asset_management.apis.asset_class_property import propagate_property_to_assets
    return await propagate_property_to_assets(doc, ctx.db)


@hook_registry.after_save("asset_position")
async def asset_position_after_save(doc, ctx):
    from app.modules.asset_management.apis.asset_position import update_asset_position_on_save
    return await update_asset_position_on_save(doc, ctx.db)


@hook_registry.after_save("asset_class_availability")
async def asset_class_availability_after_save(doc, ctx):
    from app.modules.asset_management.apis.asset_class_availability import calculate_asset_class_capacity
    return await calculate_asset_class_capacity(doc, ctx.db)


@hook_registry.before_save("asset_property")
async def asset_property_before_save(doc, ctx):
    from app.modules.asset_management.apis.asset_property import copy_unit_of_measure_from_property
    doc = await copy_unit_of_measure_from_property(doc, ctx.db)
    return doc


# =============================================================================
# Incident Hooks
# =============================================================================

@hook_registry.after_save("incident")
async def incident_after_save(doc, ctx):
    """
    After saving an incident:
    1. If incident_type is 'Breakdown', auto-create a Breakdown record
    2. Link incident to asset for history tracking
    """
    from app.services.document import new_doc, save_doc, get_value

    asset_id = getattr(doc, "asset", None)
    incident_type = getattr(doc, "incident_type", None) or getattr(doc, "type", None) or ""

    if asset_id and incident_type.lower() in ("breakdown", "equipment_failure", "equipment failure"):
        existing = await get_value("breakdown", {"asset": asset_id, "incident": doc.id}, "*", ctx.db)
        if not existing:
            breakdown = await new_doc("breakdown", ctx.db,
                asset=asset_id,
                incident=doc.id,
                breakdown_date=getattr(doc, "incident_date", None) or getattr(doc, "date", None),
                description=getattr(doc, "description", None),
                site=getattr(doc, "site", None),
                department=getattr(doc, "department", None),
            )
            if breakdown:
                await save_doc(breakdown, ctx.db)

    return None


@hook_registry.after_save("equipment_schedule")
async def equipment_schedule_after_save(doc, ctx):
    """Generate equipment availability when schedule is saved."""
    from app.modules.asset_management.apis.equipment_schedule import generate_equipment_availability
    return await generate_equipment_availability(doc, ctx.db)


# =============================================================================
# Workflow Hooks - All routed through central workflow_router
# =============================================================================

@hook_registry.after_save("meter_reading")
async def meter_reading_after_save(doc, ctx):
    """
    When a meter reading is saved:
    1. Calculate delta from previous reading
    2. Update parent meter's last_reading and last_reading_date
    3. Check if meter-based PM threshold is reached
    """
    from app.services.document import get_doc, get_value, get_list, save_doc, new_doc
    from datetime import datetime, timedelta

    meter_id = getattr(doc, "meter", None)
    reading_value = getattr(doc, "reading_value", None)
    if not meter_id or reading_value is None:
        return

    reading_value = float(reading_value)

    # Get meter and update last reading
    meter_doc = await get_doc("meter", meter_id, ctx.db)
    if not meter_doc:
        return

    prev_reading = float(getattr(meter_doc, "last_reading", 0) or 0)
    rollover = float(getattr(meter_doc, "rollover_point", 0) or 0)

    # Calculate delta (handle rollover)
    if rollover > 0 and reading_value < prev_reading:
        delta = (rollover - prev_reading) + reading_value
    else:
        delta = reading_value - prev_reading

    # Set delta on reading doc
    if delta != (getattr(doc, "delta", None) or 0):
        doc.delta = round(delta, 2)
        await save_doc(doc, ctx.db, commit=False)

    # Update meter
    meter_doc.last_reading = reading_value
    meter_doc.last_reading_date = getattr(doc, "reading_date", None) or datetime.now()
    await save_doc(meter_doc, ctx.db, commit=False)
    await ctx.db.commit()


@hook_registry.workflow("asset")
async def asset_workflow_hook(ctx):
    from app.modules.asset_management.workflow_router import route_workflow
    return await route_workflow("asset", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("incident")
async def incident_workflow_hook(ctx):
    from app.modules.asset_management.workflow_router import route_workflow
    return await route_workflow("incident", ctx.doc, ctx.action, ctx.db, ctx.user)


# =============================================================================
# MW-11: Asset Transfer Workflow
# =============================================================================

@hook_registry.workflow("asset_transfer")
async def asset_transfer_workflow_hook(ctx):
    """
    Asset Transfer workflow: on 'Received' action, update asset's
    location, site, and department to the transfer destination.
    """
    from app.services.document import get_doc, save_doc

    doc = ctx.doc
    action = ctx.action

    if action in ("receive", "Receive"):
        asset_id = getattr(doc, "asset", None)
        if asset_id:
            asset_doc = await get_doc("asset", asset_id, ctx.db)
            if asset_doc:
                to_site = getattr(doc, "to_site", None)
                to_loc = getattr(doc, "to_location", None)
                to_dept = getattr(doc, "to_department", None)
                changed = False
                if to_site:
                    asset_doc.site = to_site
                    changed = True
                if to_loc:
                    asset_doc.location = to_loc
                    changed = True
                if to_dept:
                    asset_doc.department = to_dept
                    changed = True
                if changed:
                    await save_doc(asset_doc, ctx.db)

        from datetime import datetime
        doc.received_date = datetime.now()
        await save_doc(doc, ctx.db)

        return {"status": "success", "message": "Asset transfer received. Asset location updated."}

    return {"status": "success", "message": f"Asset transfer workflow '{action}' allowed"}


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.asset_management.apis.disposed  # noqa: F401
    import app.modules.asset_management.apis.breakdown  # noqa: F401
    import app.modules.asset_management.apis.position  # noqa: F401
    import app.modules.asset_management.apis.equipment_schedule  # noqa: F401
    import app.modules.asset_management.apis.asset_clone_actions  # noqa: F401
