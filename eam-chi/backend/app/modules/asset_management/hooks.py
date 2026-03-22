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

@hook_registry.workflow("asset")
async def asset_workflow_hook(ctx):
    from app.modules.asset_management.workflow_router import route_workflow
    return await route_workflow("asset", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("incident")
async def incident_workflow_hook(ctx):
    from app.modules.asset_management.workflow_router import route_workflow
    return await route_workflow("incident", ctx.doc, ctx.action, ctx.db, ctx.user)


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.asset_management.apis.disposed  # noqa: F401
    import app.modules.asset_management.apis.breakdown  # noqa: F401
    import app.modules.asset_management.apis.position  # noqa: F401
    import app.modules.asset_management.apis.equipment_schedule  # noqa: F401
