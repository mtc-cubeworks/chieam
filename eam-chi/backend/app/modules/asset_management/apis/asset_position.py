"""
Asset Position Post-Save Business Logic

Mirrors: ci_eam/asset_management/doctype/asset_position/asset_position.py
- update_asset_position(doc)

When an Asset Position is saved:
- If date_removed is set: clear Position.current_asset, apply workflow
- If no date_removed: set Position.current_asset, update Asset fields, apply workflow
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, save_doc
from app.services.document_mutation import apply_workflow_state


async def update_asset_position_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook for Asset Position.
    Updates Position.current_asset and Asset location/system/site based on install/remove.
    """
    asset_id = getattr(doc, 'asset', None)
    position_id = getattr(doc, 'position', None)

    if not asset_id or not position_id:
        return {"status": "success", "message": "Missing asset or position. Skipping."}

    asset_doc = await get_doc("asset", asset_id, db)
    if not asset_doc:
        return {"status": "success", "message": "Asset not found. Skipping."}

    date_removed = getattr(doc, 'date_removed', None)

    try:
        if date_removed:
            # Asset is being REMOVED from position
            position_doc = await get_doc("position", position_id, db)
            if position_doc:
                position_doc.current_asset = None
                await save_doc(position_doc, db, commit=False)

            # Apply "Remove Asset" workflow if asset is "Under Maintenance"
            current_state = getattr(asset_doc, 'workflow_state', None)
            if current_state == "under_maintenance":
                try:
                    await apply_workflow_state(
                        "asset", asset_id, "remove_asset", db
                    )
                except Exception:
                    pass  # Non-critical: workflow may not have this transition

            await db.commit()
            return {"status": "success", "message": "Successfully removed asset from position."}
        else:
            # Asset is being INSTALLED at position
            position_doc = await get_doc("position", position_id, db)
            if not position_doc:
                return {"status": "success", "message": "Position not found. Skipping."}

            # Update Position with current asset
            position_doc.current_asset = asset_id
            await save_doc(position_doc, db, commit=False)

            # Update Asset with location/system/site from position
            asset_doc.location = getattr(position_doc, 'location', None)
            asset_doc.system = getattr(position_doc, 'system', None)
            asset_doc.site = getattr(position_doc, 'site', None)
            asset_doc.position = position_id
            await save_doc(asset_doc, db, commit=False)

            # Apply workflow transitions based on current asset state
            current_state = getattr(asset_doc, 'workflow_state', None)
            if current_state in ["acquired", "inspected", "inactive", "under_maintenance", "receiving"]:
                try:
                    if current_state == "acquired":
                        await apply_workflow_state(
                            "asset", asset_id, "inspect_asset", db
                        )
                    await apply_workflow_state(
                        "asset", asset_id, "install_asset", db
                    )
                except Exception:
                    pass  # Non-critical: workflow transitions may vary

            await db.commit()
            return {"status": "success", "message": "Successfully installed asset at position."}
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to update asset position: {str(e)}"}
