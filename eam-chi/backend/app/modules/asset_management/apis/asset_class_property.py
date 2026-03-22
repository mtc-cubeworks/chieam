"""
Asset Class Property Post-Save Business Logic

Mirrors: ci_eam/asset_management/doctype/asset_class_property/asset_class_property.py
- populate_asset_prop(doc)

When a new Asset Class Property is created, propagate it to all Assets of that class.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def propagate_property_to_assets(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: When an Asset Class Property is created/updated,
    ensure all Assets of that class have a corresponding Asset Property.
    """
    acp_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not acp_id:
        return {"status": "success", "message": "No ACP ID. Skipping."}

    acp = await get_doc("asset_class_property", acp_id, db)
    if not acp:
        return {"status": "success", "message": "Asset Class Property not found. Skipping."}

    asset_class_id = getattr(acp, 'asset_class', None)
    property_id = getattr(acp, 'property', None)
    if not asset_class_id or not property_id:
        return {"status": "success", "message": "Missing asset_class or property. Skipping."}

    # Get all assets of this class
    assets = await get_list("asset", {"asset_class": asset_class_id}, db=db)
    if not assets:
        return {"status": "success"}

    created_count = 0
    for asset in assets:
        asset_id = asset.get("id")
        if not asset_id:
            continue

        # Check if asset property already exists
        existing = await get_value(
            "asset_property",
            {"asset": asset_id, "property": property_id},
            "*", db
        )
        if existing:
            continue

        # Create new asset property
        new_prop = await new_doc("asset_property", db,
            asset=asset_id,
            property=property_id,
            value=getattr(acp, 'default_value', None),
            unit_of_measure=getattr(acp, 'unit_of_measure', None),
        )
        if new_prop:
            await save_doc(new_prop, db, commit=False)
            created_count += 1

    if created_count > 0:
        await db.commit()

    return {
        "status": "success",
        "message": f"Propagated property to {created_count} assets" if created_count else ""
    }
