"""
Position Entity Business Logic

Mirrors: ci_eam/asset_management/doctype/position/position.py
- create_install_asset(position)
- create_swap_asset(position)
- create_decommission_asset(position)
- create_maintenance_request_for_position(...)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, new_doc, save_doc


async def create_install_asset(position_id: str, db: AsyncSession, user: Any) -> dict:
    """
    Create maintenance request to install an asset at a position.
    
    Mirrors: create_install_asset() from Frappe
    """
    position = await get_doc("position", position_id, db)
    if not position:
        return {"status": "error", "message": f"Position {position_id} not found"}
    
    current_asset = getattr(position, 'current_asset', None)
    if current_asset:
        return {"status": "error", "message": "Position already has an asset installed"}
    
    return await _create_maintenance_request_for_position(
        position=position,
        request_type="Install Asset",
        action="Install Asset",
        asset_id=None,
        db=db,
        user=user
    )


async def create_swap_asset(position_id: str, new_asset_id: str, db: AsyncSession, user: Any) -> dict:
    """
    Create maintenance request to swap an asset at a position.
    
    Mirrors: create_swap_asset() from Frappe
    """
    position = await get_doc("position", position_id, db)
    if not position:
        return {"status": "error", "message": f"Position {position_id} not found"}
    
    current_asset_id = getattr(position, 'current_asset', None)
    
    # First, create request to remove current asset if exists
    if current_asset_id:
        result = await _create_maintenance_request_for_position(
            position=position,
            request_type="Replace Asset",
            action="Start Maintenance",
            asset_id=current_asset_id,
            db=db,
            user=user
        )
        if result["status"] == "error":
            return result
    
    # Then create request to install new asset
    return await _create_maintenance_request_for_position(
        position=position,
        request_type="Install Asset",
        action="Install Asset",
        asset_id=new_asset_id,
        db=db,
        user=user
    )


async def create_decommission_asset(position_id: str, db: AsyncSession, user: Any) -> dict:
    """
    Create maintenance request to decommission an asset at a position.
    
    Mirrors: create_decommission_asset() from Frappe
    """
    position = await get_doc("position", position_id, db)
    if not position:
        return {"status": "error", "message": f"Position {position_id} not found"}
    
    current_asset_id = getattr(position, 'current_asset', None)
    if not current_asset_id:
        return {"status": "error", "message": "Position has no asset to decommission"}
    
    return await _create_maintenance_request_for_position(
        position=position,
        request_type="Decommission",
        action="Start Maintenance",
        asset_id=current_asset_id,
        db=db,
        user=user
    )


async def _create_maintenance_request_for_position(
    position: Any,
    request_type: str,
    action: str,
    asset_id: str,
    db: AsyncSession,
    user: Any
) -> dict:
    """
    Create Work Order Activity and Maintenance Request for position operations.
    
    Mirrors: create_maintenance_request_for_position() from Frappe
    """
    position_id = position.id if hasattr(position, 'id') else position.get('id')
    location = getattr(position, 'location', None)
    site = getattr(position, 'site', None)
    department = getattr(position, 'department', None)
    
    # Get activity type
    get_state = await get_value("request_activity_type", {"type": request_type}, "*", db)
    if not get_state:
        return {"status": "error", "message": f"Activity type '{request_type}' not found"}
    
    # Get asset details if provided
    asset = await get_doc("asset", asset_id, db) if asset_id else None
    asset_description = getattr(asset, 'description', '') if asset else ''
    
    # Create Work Order Activity
    wo_activity = await new_doc("work_order_activity", db,
        description=f"{request_type} at Position: {position_id}",
        work_item_type="Asset" if asset_id else "Non-Asset",
        work_item=asset_id,
        activity_type=get_state.get("id"),
        activity_type_name=request_type,
        position=position_id,
        location=location,
        site=site,
        department=department,
        start_date=datetime.now(),
        workflow_state="awaiting_resources"
    )
    await save_doc(wo_activity, db, commit=False)
    
    # Create Maintenance Request
    maint_request = await new_doc("maintenance_request", db,
        requested_date=date.today(),
        request_type=get_state.get("id"),
        asset=asset_id,
        position=position_id,
        location=location,
        due_date=date.today(),
        site=site,
        department=department,
        work_order_activity=wo_activity.id,
        workflow_state="draft"
    )
    await save_doc(maint_request, db, commit=False)
    
    # Apply workflow transitions
    maint_request.workflow_state = "pending_approval"
    await save_doc(maint_request, db, commit=False)
    maint_request.workflow_state = "approved"
    await save_doc(maint_request, db)
    
    return {
        "status": "success",
        "message": f"Successfully created {request_type} request",
        "action": "generate_id",
        "path": f"/maintenance_request/{maint_request.id}",
        "data": {
            "maintenance_request_id": maint_request.id,
            "work_order_activity_id": wo_activity.id
        }
    }
