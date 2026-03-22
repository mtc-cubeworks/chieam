"""
Work Order Activity Entity Business Logic

Mirrors: ci_eam/work_management/doctype/work_order_activity/work_order_activity.py
- check_wo_activity_state(wo_activity, action)
- create_wo_labor(doc)
- install_asset_position(doc)
- uninstall_asset_position(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import (
    get_doc,
    get_value,
    get_list,
    new_doc,
    save_doc,
    apply_workflow_state,
)


async def check_work_order_activity_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Work Order Activity entity.
    
    Mirrors: check_wo_activity_state() from ci_eam/work_management/doctype/work_order_activity/work_order_activity.py
    """
    if not doc:
        return {"status": "error", "message": "Work Order Activity not specified"}
    
    wo_activity_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not wo_activity_id:
        return {"status": "error", "message": "Work Order Activity ID is required"}
    
    # Normalize action to lowercase for matching
    action = action.lower().replace(" ", "_")
    
    # Get related records
    wo_labor = await get_list("work_order_labor", {"work_order_activity": wo_activity_id}, db=db)
    wo_equip = await get_list("work_order_equipment", {"work_order_activity": wo_activity_id}, db=db)
    wo_parts = await get_list("work_order_parts", {"work_order_activity": wo_activity_id}, db=db)
    
    work_order_id = getattr(doc, 'work_order', None)
    work_order = await get_doc("work_order", work_order_id, db) if work_order_id else None
    
    maint_req = await get_value("maintenance_request", {"work_order_activity": wo_activity_id}, "*", db)
    
    if action == "allocate":
        return await _handle_allocate(doc, wo_labor, wo_equip, wo_parts, maint_req, db)
    
    elif action == "start_activity":
        return await _handle_start_activity(doc, work_order, db)
    
    elif action == "complete":
        return await _handle_complete(doc, maint_req, db, user)
    
    elif action == "reopen":
        return await _handle_reopen(doc, work_order, maint_req, db)
    
    elif action == "close":
        return await _handle_close(doc, wo_activity_id, wo_labor, wo_equip, wo_parts, db)
    
    return {"status": "success", "message": f"Work Order Activity workflow '{action}' allowed"}


async def _handle_allocate(doc: Any, wo_labor: list, wo_equip: list, wo_parts: list, maint_req: dict, db: AsyncSession) -> dict:
    """Handle 'Allocate' action - validates resources are assigned."""
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    
    if not maint_req or not maint_req.get("planned_maintenance_activity"):
        # No planned maintenance activity - just check labor
        if not wo_labor:
            return {"status": "error", "message": f"[WOA {wo_id}] Cannot allocate: no Work Order Labor records found. Assign labor before allocating."}
        return {"status": "success", "message": f"[WOA {wo_id}] Allocated successfully ({len(wo_labor)} labor record(s) found)."}
    
    # Has planned maintenance activity - check all resources
    missing = []
    pma_id = maint_req["planned_maintenance_activity"]
    
    if not wo_labor:
        missing.append("Labor")
    
    pma = await get_value("planned_maintenance_activity", pma_id, "*", db)
    if pma:
        # Check Maintenance Equipment
        maint_equip = await get_value("maintenance_equipment", {"maintenance_activity": pma.get("maintenance_activity")}, "*", db)
        if maint_equip and not wo_equip:
            missing.append("Equipment")
        
        # Check Maintenance Parts
        maint_part = await get_value("maintenance_parts", {"maintenance_activity": pma.get("maintenance_activity")}, "*", db)
        if maint_part and not wo_parts:
            missing.append("Parts")
    
    if not missing:
        return {"status": "success", "message": f"[WOA {wo_id}] Allocated successfully (PMA: {pma_id})."}
    
    return {"status": "error", "message": f"[WOA {wo_id}] Cannot allocate: missing {', '.join(missing)}. Assign all required resources before allocating."}


async def _handle_start_activity(doc: Any, work_order: Any, db: AsyncSession) -> dict:
    """Handle 'Start Activity' action."""
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    work_item_type = getattr(doc, 'work_item_type', None)
    activity_type = getattr(doc, 'activity_type', None)
    work_order_id = getattr(doc, 'work_order', None)
    
    if not work_order_id:
        return {"status": "error", "message": f"[WOA {wo_id}] Cannot start: no Work Order linked. A Work Order must be created (release the Maintenance Request first)."}
    
    if work_item_type == "Asset" and activity_type:
        get_state = await get_value("request_activity_type", {"id": activity_type}, "*", db)
        if get_state and get_state.get("menu") == "Maintain Asset":
            work_item = getattr(doc, 'work_item', None)
            if work_item:
                asset_doc = await get_doc("asset", work_item, db)
                if asset_doc:
                    result = await apply_workflow_state(
                        "asset", asset_doc, "maintain_asset", db
                    )
                    if result.get("status") != "success":
                        return {
                            "status": "error",
                            "message": (
                                f"[WOA {wo_id}] Failed to move asset {work_item} "
                                "to 'Under Maintenance': "
                                f"{result.get('message', 'Unknown error')}"
                            ),
                        }
                    await save_doc(asset_doc, db, commit=False)
    
    return {"status": "success", "message": f"[WOA {wo_id}] Activity started. Work Order: {work_order_id}."}


async def _handle_complete(doc: Any, maint_req: dict, db: AsyncSession, user: Any) -> dict:
    """Handle 'Complete' action - validates and updates related records."""
    
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    activity_type = getattr(doc, 'activity_type', None)
    work_item = getattr(doc, 'work_item', None)
    position = getattr(doc, 'position', None)
    
    if not activity_type:
        await db.commit()
        return {"status": "success", "message": f"[WOA {wo_id}] Completed (no activity type configured, skipping business logic)."}
    
    get_state = await get_value("request_activity_type", {"id": activity_type}, "*", db)
    if not get_state:
        await db.commit()
        return {"status": "success", "message": f"[WOA {wo_id}] Completed (activity type {activity_type} not found in Request Activity Types)."}
    
    action_type = get_state.get("menu")  # 'menu' holds the action name e.g. 'Install Asset'
    asset_doc = await get_doc("asset", work_item, db) if work_item else None
    
    # Update maintenance request closed date
    if maint_req:
        mr_id = maint_req["id"]
        maint_req_doc = await get_doc("maintenance_request", mr_id, db)
        if maint_req_doc:
            maint_req_doc.closed_date = date.today()
            await save_doc(maint_req_doc, db, commit=False)
        
        # Update asset properties if specified
        if asset_doc and maint_req.get("property"):
            asset_prop = await get_value("asset_property", {"asset": asset_doc.id, "property": maint_req["property"]}, "*", db)
            if asset_prop:
                prop_doc = await get_doc("asset_property", asset_prop["id"], db)
                if prop_doc:
                    prop_doc.property_value = date.today().strftime("%m/%d/%Y")
                    await save_doc(prop_doc, db, commit=False)
    
    if action_type in ["Install Asset", "Remove Asset"]:
        if not position:
            return {"status": "error", "message": f"[WOA {wo_id}] Cannot complete '{action_type}': Position field is not set. Edit the WOA and select a Position before completing."}
        
        if not asset_doc:
            return {"status": "error", "message": f"[WOA {wo_id}] Cannot complete '{action_type}': Work Item (asset '{work_item}') not found."}
        
        if action_type == "Install Asset":
            asset_position = await _install_asset_position(doc, db)
            await db.commit()
            await _auto_complete_parent_wo(doc, db)
            ap_id = asset_position.id if asset_position else "unknown"
            return {
                "status": "success",
                "message": f"[WOA {wo_id}] Install Asset complete. Asset Position {ap_id} created for asset {work_item} at position {position}.",
                "action": "generate_id",
                "path": f"/asset/{asset_doc.id}"
            }
        else:
            await _uninstall_asset_position(doc, db)
            await db.commit()
            await _auto_complete_parent_wo(doc, db)
            return {
                "status": "success",
                "message": f"[WOA {wo_id}] Remove Asset complete. Asset {work_item} uninstalled from position {position}.",
                "action": "generate_id",
                "path": f"/asset/{asset_doc.id}"
            }
    elif action_type == "Maintain Asset":
        if asset_doc:
            asset_doc.need_repair = False
            asset_doc.workflow_state = "active"
            await save_doc(asset_doc, db, commit=False)
        await db.commit()
        await _auto_complete_parent_wo(doc, db)
        return {"status": "success", "message": f"[WOA {wo_id}] Maintain Asset complete. Asset {work_item} set to Active, need_repair cleared."}
    
    await db.commit()
    await _auto_complete_parent_wo(doc, db)
    return {"status": "success", "message": f"[WOA {wo_id}] Completed (activity type: '{action_type}', no special handler needed)."}
    

async def _handle_reopen(doc: Any, work_order: Any, maint_req: dict, db: AsyncSession) -> dict:
    """Handle 'Reopen' action."""
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    work_order_id = getattr(doc, 'work_order', None)
    return {"status": "success", "message": f"[WOA {wo_id}] Reopened and set back to In Progress. Work Order: {work_order_id}."}


async def _handle_close(doc: Any, wo_activity_id: str, wo_labor: list, wo_equip: list, wo_parts: list, db: AsyncSession) -> dict:
    """Handle 'Close' action - validates all requirements are met."""
    
    error_messages = []
    
    # Check Activity Logs
    activity_logs = await get_list("work_order_activity_logs", {"work_order_activity": wo_activity_id}, db=db)
    if not activity_logs:
        error_messages.append("No Work Order Activity Logs found")
    
    # Check Parts - quantity_issued must match quantity_required
    if wo_parts:
        for part in wo_parts:
            qty_required = part.get("quantity_required", 0) or 0
            qty_issued = part.get("quantity_issued", 0) or 0
            if qty_required > 0 and qty_issued == 0:
                error_messages.append(f"Part {part.get('id')} needs issuance")
    
    # Check Equipment - must have actual hours
    if wo_equip:
        for equip in wo_equip:
            actual_hours = await get_list("work_order_equipment_actual_hours", {"wo_equip_id": equip.get("id")}, db=db)
            if not actual_hours:
                error_messages.append(f"Equipment {equip.get('id')} missing actual hours")
    
    # Check Labor - must have actual hours
    if wo_labor:
        for labor in wo_labor:
            actual_hours = await get_list("work_order_labor_actual_hours", {"wo_labor_id": labor.get("id")}, db=db)
            if not actual_hours:
                error_messages.append(f"Labor {labor.get('id')} missing actual hours")
    
    if error_messages:
        wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
        return {"status": "error", "message": f"[WOA {wo_id}] Cannot close: {'; '.join(error_messages)}"}
    
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    # Set end_date
    doc.end_date = datetime.now()
    await save_doc(doc, db)

    # Auto-complete parent WO if all WOAs are now completed/closed
    await _auto_complete_parent_wo(doc, db)

    return {"status": "success", "message": f"[WOA {wo_id}] Closed successfully. End date set to {doc.end_date.date()}."}


async def _install_asset_position(doc: Any, db: AsyncSession) -> Any:
    """
    Install asset at position.
    Mirrors: install_asset_position() from Frappe
    """
    position_id = getattr(doc, 'position', None)
    work_item = getattr(doc, 'work_item', None)
    wo_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    
    if not position_id or not work_item:
        return None
    
    # Create Asset Position record
    new_asset_position = await new_doc("asset_position", db,
        position=position_id,
        asset=work_item,
        date_installed=datetime.now()
    )
    await save_doc(new_asset_position, db, commit=False)
    
    # Update Position with current asset
    position_doc = await get_doc("position", position_id, db)
    if position_doc:
        position_doc.current_asset = work_item
        await save_doc(position_doc, db, commit=False)
    else:
        import logging
        logging.getLogger(__name__).warning(f"[WOA {wo_id}] Position '{position_id}' not found when installing asset '{work_item}'. Asset position created but position record not updated.")
    
    # Update Asset with location from position
    if position_doc:
        asset_doc = await get_doc("asset", work_item, db)
        if asset_doc:
            asset_doc.location = position_doc.location
            asset_doc.system = getattr(position_doc, 'system', None)
            asset_doc.position = position_id
            await save_doc(asset_doc, db, commit=False)
        else:
            import logging
            logging.getLogger(__name__).warning(f"[WOA {wo_id}] Asset '{work_item}' not found when updating location/position fields after install.")
    
    return new_asset_position


async def _uninstall_asset_position(doc: Any, db: AsyncSession) -> dict:
    """
    Remove asset from position.
    Mirrors: uninstall_asset_position() from Frappe
    """
    position_id = getattr(doc, 'position', None)
    work_item = getattr(doc, 'work_item', None)
    
    if not position_id or not work_item:
        return {"status": "success"}
    
    # Find and update Asset Position record
    asset_position = await get_value("asset_position", {"position": position_id, "asset": work_item}, "*", db)
    if asset_position:
        ap_doc = await get_doc("asset_position", asset_position["id"], db)
        if ap_doc:
            ap_doc.date_removed = datetime.now()
            await save_doc(ap_doc, db, commit=False)
    
    # Clear current_asset from position
    position_doc = await get_doc("position", position_id, db)
    if position_doc:
        position_doc.current_asset = None
        await save_doc(position_doc, db, commit=False)
    
    return {"status": "success"}


async def create_wo_labor_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After save hook: Create Work Order Labor record when assigned_to is set.
    Mirrors: create_wo_labor() from Frappe
    """
    assigned_to = getattr(doc, 'assigned_to', None)
    wo_activity_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    
    if not assigned_to or not wo_activity_id:
        return {"status": "success"}
    
    # Check if labor already exists
    existing = await get_value("work_order_labor", {"work_order_activity": wo_activity_id, "labor": assigned_to}, "*", db)
    if existing:
        return {"status": "success"}
    
    # Get trade from Trade Labor (primary first)
    trade_labor = await get_value("trade_labor", {"labor": assigned_to, "primary": True}, "*", db)
    if not trade_labor:
        trade_labor = await get_value("trade_labor", {"labor": assigned_to}, "*", db)
    
    if not trade_labor:
        return {"status": "success"}
    
    # Create Work Order Labor
    new_wo_labor = await new_doc("work_order_labor", db,
        work_order_activity=wo_activity_id,
        trade=trade_labor.get("trade"),
        labor=assigned_to,
        lead=True,
        start_datetime=datetime.now()
    )
    await save_doc(new_wo_labor, db)
    
    return {"status": "success"}


async def _auto_complete_parent_wo(doc: Any, db: AsyncSession) -> None:
    """
    Auto-complete the parent Work Order when all sibling WOAs
    are in 'completed' or 'closed' state.
    """
    work_order_id = getattr(doc, 'work_order', None)
    if not work_order_id:
        return

    wo_doc = await get_doc("work_order", work_order_id, db)
    if not wo_doc:
        return

    current_state = getattr(wo_doc, 'workflow_state', '')
    if current_state in ('completed', 'closed'):
        return

    siblings = await get_list(
        "work_order_activity", {"work_order": work_order_id}, db=db
    )
    if not siblings:
        return

    all_done = all(
        s.get("workflow_state") in ("completed", "closed") for s in siblings
    )
    if all_done:
        result = await apply_workflow_state(
            "work_order", wo_doc, "Complete", db
        )
        if result.get("status") != "success":
            wo_doc.workflow_state = "completed"
            await save_doc(wo_doc, db)
