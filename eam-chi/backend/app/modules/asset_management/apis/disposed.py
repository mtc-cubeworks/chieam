"""
Disposed Entity Business Logic

Mirrors: ci_eam/asset_management/doctype/disposed/disposed.py
- create_purchase_request(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, new_doc, save_doc


async def create_purchase_request_on_dispose(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    After save hook: Create Purchase Request when asset is disposed.
    
    Mirrors: create_purchase_request() from Frappe
    """
    asset_id = getattr(doc, 'asset', None)
    if not asset_id:
        return {"status": "success"}
    
    asset = await get_doc("asset", asset_id, db)
    if not asset:
        return {"status": "error", "message": f"Asset {asset_id} not found"}
    
    asset_description = getattr(asset, 'description', '')
    item_type = getattr(asset, 'item_type', None)
    
    # Create Purchase Request for replacement
    pr = await new_doc("purchase_request", db,
        date_requested=datetime.now(),
        description=f"Replacement request for disposed asset: {asset_description}",
        site=getattr(asset, 'site', None),
        department=getattr(asset, 'department', None)
    )
    await save_doc(pr, db, commit=False)
    
    # If Fixed Asset Item, update Asset Position
    if item_type == "Fixed Asset Item":
        asset_position = await get_value("asset_position", {"asset": asset_id}, "*", db)
        if asset_position and not asset_position.get("date_removed"):
            # Note: date_removed needs to be set manually
            pass
    
    await db.commit()
    
    return {
        "status": "success",
        "message": "Successfully created purchase request for disposed asset",
        "action": "generate_id",
        "path": f"/purchase_request/{pr.id}"
    }


# Register server action
from app.services.server_actions import server_actions, ActionContext

@server_actions.register("disposed", "create_purchase_request")
async def create_purchase_request_action(ctx: ActionContext):
    """Server action wrapper for create_purchase_request_on_dispose."""
    doc = ctx.params.get("doc")
    return await create_purchase_request_on_dispose(doc, ctx.db, ctx.user)
