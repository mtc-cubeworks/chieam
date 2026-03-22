"""
Work Order Activity Custom Actions

Mirrors: ci_eam/work_management/doctype/work_order_activity/work_order_activity.py
- generate_templated_pma(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, new_doc, save_doc


async def generate_templated_pma(doc: Any, db: AsyncSession) -> dict:
    """
    Generate Planned Maintenance Activity from Work Order Activity resources.
    
    Mirrors: generate_templated_pma() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Input document is required."}
    
    doc_id = doc.id if hasattr(doc, 'id') else doc.get('id') if isinstance(doc, dict) else None
    if not doc_id:
        return {"status": "error", "message": "Work Order Activity name is required."}
    
    # Check if maintenance request exists and has no PMA
    maint_req = await get_value("maintenance_request", {"work_order_activity": doc_id}, "*", db)
    if not maint_req:
        return {"status": "error", "message": f"Maintenance Request for Work Order Activity '{doc_id}' not found."}
    
    if maint_req.get("planned_maintenance_activity"):
        return {"status": "error", "message": "Planned Maintenance Activity already exists."}
    
    return await _create_pma(doc_id, db)


async def _create_pma(wo_activity_id: str, db: AsyncSession) -> dict:
    """Create Planned Maintenance Activity from Work Order Activity resources."""
    
    wo_activity = await get_value("work_order_activity", wo_activity_id, "*", db)
    wo_labor = await get_value("work_order_labor", {"work_order_activity": wo_activity_id}, "*", db)
    wo_equip = await get_value("work_order_equipment", {"work_order_activity": wo_activity_id}, "*", db)
    wo_part = await get_value("work_order_parts", {"work_order_activity": wo_activity_id}, "*", db)
    
    if not wo_activity:
        return {"status": "error", "message": "Work Order Activity not found."}
    
    # Create Maintenance Activity
    maint_activity = await new_doc("maintenance_activity", db,
        activity_name=wo_activity.get("description"),
        date=datetime.now()
    )
    await save_doc(maint_activity, db, commit=False)
    
    # Create Maintenance Trade
    if wo_labor:
        maint_trade = await new_doc("maintenance_trade", db,
            maintenance_activity=maint_activity.id,
            trade=wo_labor.get("trade"),
            required_hours=wo_labor.get("estimated_hours")
        )
        await save_doc(maint_trade, db, commit=False)
    
    # Create Maintenance Equipment
    if wo_equip:
        maint_equip = await new_doc("maintenance_equipment", db,
            maintenance_activity=maint_activity.id,
            asset_class=wo_equip.get("asset_class"),
            required_hours=wo_equip.get("estimated_hours")
        )
        await save_doc(maint_equip, db, commit=False)
    
    # Create Maintenance Parts
    if wo_part:
        maint_part = await new_doc("maintenance_parts", db,
            maintenance_activity=maint_activity.id,
            item=wo_part.get("item"),
            quantity=wo_part.get("quantity_required")
        )
        await save_doc(maint_part, db, commit=False)
    
    # Create Planned Maintenance Activity
    new_pma = await new_doc("planned_maintenance_activity", db,
        maintenance_activity=maint_activity.id,
        maintenance_activity_name=maint_activity.activity_name
    )
    await save_doc(new_pma, db)
    
    return {
        "status": "success",
        "message": "Successfully generated planned maintenance activity record.",
        "action": "generate_id",
        "path": f"/planned_maintenance_activity/{new_pma.id}"
    }


async def create_maint_request_from_woa(doc: Any, db: AsyncSession) -> dict:
    """
    Create Maintenance Request from Work Order Activity.
    Auto-advances MR to approved state.

    Mirrors: create_maint_request() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Input document is required."}

    doc_id = doc.id if hasattr(doc, 'id') else doc.get('id') if isinstance(doc, dict) else None
    if not doc_id:
        return {"status": "error", "message": "Work Order Activity name is required."}

    # Check if MR already exists for this WOA
    existing = await get_value("maintenance_request", {"work_order_activity": doc_id}, "*", db)
    if existing:
        return {"status": "success", "message": "Maintenance Request already exists for this WOA."}

    activity_type = getattr(doc, 'activity_type', None) if hasattr(doc, 'activity_type') else doc.get('activity_type') if isinstance(doc, dict) else None
    work_item = getattr(doc, 'work_item', None) if hasattr(doc, 'work_item') else doc.get('work_item') if isinstance(doc, dict) else None
    description = getattr(doc, 'description', None) if hasattr(doc, 'description') else doc.get('description') if isinstance(doc, dict) else None
    location = getattr(doc, 'location', None) if hasattr(doc, 'location') else doc.get('location') if isinstance(doc, dict) else None
    site = getattr(doc, 'site', None) if hasattr(doc, 'site') else doc.get('site') if isinstance(doc, dict) else None
    department = getattr(doc, 'department', None) if hasattr(doc, 'department') else doc.get('department') if isinstance(doc, dict) else None

    try:
        from datetime import date as date_type
        mr = await new_doc("maintenance_request", db,
            requested_date=date_type.today(),
            request_type=activity_type,
            asset=work_item,
            description=description,
            location=location,
            due_date=date_type.today(),
            site=site,
            department=department,
            work_order_activity=doc_id,
            workflow_state="draft",
        )
        await save_doc(mr, db, commit=False)

        # Auto-advance: draft → pending_approval → approved
        from app.services.workflow import WorkflowDBService
        _, t1, _ = await WorkflowDBService.validate_transition(
            db, "maintenance_request", "draft", "submit_for_approval"
        )
        if t1:
            mr.workflow_state = t1
        _, t2, _ = await WorkflowDBService.validate_transition(
            db, "maintenance_request", mr.workflow_state, "approve"
        )
        if t2:
            mr.workflow_state = t2

        await db.commit()
        return {
            "status": "success",
            "message": "Successfully created maintenance request.",
            "action": "generate_id",
            "path": f"/maintenance_request/{mr.id}",
            "data": {"maintenance_request_id": mr.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create maintenance request: {str(e)}"}


async def create_transfer_from_woa(transfer_type_source: str, db: AsyncSession) -> dict:
    """
    Create Transfer record from Work Order context.

    Mirrors: create_transfer() from Frappe
    transfer_type_source: 'work_order_labor' | 'work_order_equipment' | 'work_order_parts'
    """
    type_map = {
        "work_order_labor": "Labor",
        "work_order_equipment": "Equipment",
        "work_order_parts": "Inventory",
    }
    transfer_type = type_map.get(transfer_type_source)
    if not transfer_type:
        return {"status": "error", "message": f"Invalid transfer type source: {transfer_type_source}"}

    try:
        transfer = await new_doc("transfer", db,
            transfer_type=transfer_type,
        )
        await save_doc(transfer, db)
        return {
            "status": "success",
            "message": f"Successfully created {transfer_type} transfer.",
            "action": "generate_id",
            "path": f"/transfer/{transfer.id}",
            "data": {"transfer_id": transfer.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create transfer: {str(e)}"}


async def update_asset_status_from_woa(doc: Any, db: AsyncSession) -> dict:
    """
    Update asset status based on inspection results.

    Mirrors: update_asset_status() from Frappe
    For Inspection type: fail or retire asset based on workflow state.
    """
    if not doc:
        return {"status": "error", "message": "Input document is required."}

    activity_type = getattr(doc, 'activity_type', None) if hasattr(doc, 'activity_type') else doc.get('activity_type') if isinstance(doc, dict) else None
    work_item = getattr(doc, 'work_item', None) if hasattr(doc, 'work_item') else doc.get('work_item') if isinstance(doc, dict) else None

    if not activity_type or not work_item:
        return {"status": "error", "message": "Activity type and work item are required."}

    # Check if this is an inspection activity
    rat = await get_value("request_activity_type", {"id": activity_type}, "*", db)
    if not rat or rat.get("type") != "Inspection":
        return {"status": "error", "message": "Activity type is not for inspection."}

    asset = await get_doc("asset", work_item, db)
    if not asset:
        return {"status": "error", "message": f"Asset {work_item} not found."}

    try:
        from app.services.document_mutation import apply_workflow_state
        current_state = getattr(asset, 'workflow_state', None)
        if current_state == "acquired":
            await apply_workflow_state("asset", work_item, "failed_inspection", db)
        elif current_state == "receiving":
            await apply_workflow_state("asset", work_item, "retire_asset", db)

        await db.commit()
        return {
            "status": "success",
            "message": "Successfully updated asset status.",
            "action": "generate_id",
            "path": f"/asset/{work_item}",
            "data": {"asset_id": work_item},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to update asset status: {str(e)}"}


async def putaway_asset_from_woa(doc: Any, db: AsyncSession) -> dict:
    """
    Apply Putaway workflow to asset from inspection WOA.

    Mirrors: putaway_asset() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Input document is required."}

    activity_type = getattr(doc, 'activity_type', None) if hasattr(doc, 'activity_type') else doc.get('activity_type') if isinstance(doc, dict) else None
    work_item = getattr(doc, 'work_item', None) if hasattr(doc, 'work_item') else doc.get('work_item') if isinstance(doc, dict) else None

    if not activity_type or not work_item:
        return {"status": "error", "message": "Activity type and work item are required."}

    rat = await get_value("request_activity_type", {"id": activity_type}, "*", db)
    if not rat or rat.get("type") != "Inspection":
        return {"status": "error", "message": "Activity type is not for inspection."}

    asset = await get_doc("asset", work_item, db)
    if not asset:
        return {"status": "error", "message": f"Asset {work_item} not found."}

    try:
        current_state = getattr(asset, 'workflow_state', None)
        if current_state == "receiving":
            from app.services.document_mutation import apply_workflow_state
            await apply_workflow_state("asset", work_item, "putaway", db)

        await db.commit()
        return {
            "status": "success",
            "message": "Successfully updated asset status for putaway.",
            "action": "generate_id",
            "path": f"/asset/{work_item}",
            "data": {"asset_id": work_item},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to putaway asset: {str(e)}"}


# Register server actions
from app.services.server_actions import server_actions, ActionContext

@server_actions.register("work_order_activity", "generate_templated_pma")
async def generate_templated_pma_action(ctx: ActionContext):
    """Server action wrapper for generate_templated_pma."""
    doc = ctx.params.get("doc")
    return await generate_templated_pma(doc, ctx.db)


@server_actions.register("work_order_activity", "create_maint_request")
async def create_maint_request_action(ctx: ActionContext):
    """Server action: Create Maintenance Request from WOA."""
    return await create_maint_request_from_woa(ctx.doc, ctx.db)


@server_actions.register("work_order_activity", "create_transfer")
async def create_transfer_action(ctx: ActionContext):
    """Server action: Create Transfer from WOA context."""
    transfer_type = ctx.params.get("transfer_type", "work_order_parts")
    return await create_transfer_from_woa(transfer_type, ctx.db)


@server_actions.register("work_order_activity", "update_asset_status")
async def update_asset_status_action(ctx: ActionContext):
    """Server action: Update asset status from inspection WOA."""
    return await update_asset_status_from_woa(ctx.doc, ctx.db)


@server_actions.register("work_order_activity", "putaway_asset")
async def putaway_asset_action(ctx: ActionContext):
    """Server action: Putaway asset from inspection WOA."""
    return await putaway_asset_from_woa(ctx.doc, ctx.db)
