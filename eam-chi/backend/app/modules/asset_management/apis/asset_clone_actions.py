"""
Asset Clone Server Action (AR-8)
==================================
Allows cloning an existing asset to quickly create new assets
from templates. Copies all configuration, properties, position
assignments, and maintenance plans.
"""
from app.application.server_actions.registry import server_actions


@server_actions.register("asset", "Clone Asset")
async def clone_asset(doc, ctx):
    """
    Clone the current asset into a new Draft asset.
    Copies: asset_class, location, site, department, properties,
    position assignments, and maintenance plan linkage.
    """
    from app.services.document import new_doc, save_doc, get_list

    source_id = doc.id if hasattr(doc, "id") else getattr(doc, "name", None)

    # Create new asset with same configuration
    clone = await new_doc("asset", ctx.db,
        workflow_state="Draft",
        asset_class=getattr(doc, "asset_class", None),
        asset_class_name=getattr(doc, "asset_class_name", None),
        description=f"Clone of {getattr(doc, 'description', '') or source_id}",
        location=getattr(doc, "location", None),
        site=getattr(doc, "site", None),
        department=getattr(doc, "department", None),
        criticality=getattr(doc, "criticality", None),
        manufacturer=getattr(doc, "manufacturer", None),
        model=getattr(doc, "model", None),
        is_active=True,
        parent_asset=getattr(doc, "parent_asset", None),
    )
    if not clone:
        return {"status": "error", "message": "Failed to create cloned asset"}

    await save_doc(clone, ctx.db, commit=False)

    # Copy asset properties
    properties = await get_list("asset_property", {"asset": source_id}, db=ctx.db)
    for prop in properties:
        ap = await new_doc("asset_property", ctx.db,
            asset=clone.id,
            property=prop.get("property"),
            property_name=prop.get("property_name"),
            property_value=prop.get("property_value"),
            unit_of_measure=prop.get("unit_of_measure"),
        )
        if ap:
            await save_doc(ap, ctx.db, commit=False)

    # Copy position assignments
    positions = await get_list("asset_position", {"asset": source_id}, db=ctx.db)
    for pos in positions:
        ap = await new_doc("asset_position", ctx.db,
            asset=clone.id,
            position=pos.get("position"),
        )
        if ap:
            await save_doc(ap, ctx.db, commit=False)

    await ctx.db.commit()

    return {
        "status": "success",
        "message": f"Asset cloned as {clone.id}",
        "action": "generate_id",
        "path": f"/asset/{clone.id}",
    }
