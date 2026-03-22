"""
Maintenance Request Entity Business Logic

Mirrors: ci_eam/maintenance_management/doctype/maintenance_request/maintenance_request.py
- check_maint_request_state(maint_req_id, action)
- generate_work_order(doc, action)
- get_maint_req_info(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def check_maintenance_request_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Maintenance Request entity.
    
    Mirrors: check_maint_request_state() from Frappe
    """
    if not doc:
        return {"status": "error", "message": "Maintenance Request not specified"}
    
    maint_req_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not maint_req_id:
        return {"status": "error", "message": "Maintenance Request ID is required"}
    
    # Normalize action label to slug (workflow route passes human-readable label)
    import re as _re
    action_slug = _re.sub(r'[^a-z0-9]+', '_', action.lower().strip()).strip('_')

    allowed_actions = ["submit_for_approval", "approve", "submit_for_emergency", "submit_for_resolution", "complete", "reopen"]
    if action_slug not in allowed_actions:
        return {"status": "error", "message": f"Invalid action '{action}'. Allowed: {', '.join(allowed_actions)}"}

    if action_slug == "submit_for_approval":
        return {"status": "success", "message": "Maintenance Request submitted for approval"}

    if action_slug == "approve":
        # Path A: create WO + WOA from PMA, link WOA back to MR
        return await _approve_and_generate_wo(doc, db, user)

    elif action_slug == "submit_for_emergency":
        # Path B: validate priority=Emergency, create WO+WOA with defaults
        priority = getattr(doc, 'priority', None)
        if priority != "Emergency":
            return {"status": "error", "message": "Submit for Emergency is only allowed when Priority is 'Emergency'"}
        return await _emergency_generate_wo(doc, db, user)

    elif action_slug == "submit_for_resolution":
        # Path A continuation: just validate that a WOA is already linked
        wo_activity_id = getattr(doc, 'work_order_activity', None)
        if not wo_activity_id:
            return {"status": "error", "message": "Work Order Activity not linked. Approve the Maintenance Request first to generate a Work Order Activity before submitting for resolution."}
        wo_activity = await get_doc("work_order_activity", wo_activity_id, db)
        if not wo_activity:
            return {"status": "error", "message": f"Linked Work Order Activity '{wo_activity_id}' not found"}
        return {"status": "success", "message": "Maintenance Request submitted for resolution"}

    elif action_slug == "complete":
        wo_activity_id = getattr(doc, 'work_order_activity', None)
        if not wo_activity_id:
            return {"status": "error", "message": "No Work Order Activity linked to this Maintenance Request"}

        wo_activity = await get_doc("work_order_activity", wo_activity_id, db)
        if not wo_activity:
            return {"status": "error", "message": f"Work Order Activity '{wo_activity_id}' not found"}

        if getattr(wo_activity, 'workflow_state', None) not in ("completed", "closed"):
            return {"status": "error", "message": "Work Order Activity must be in Completed state before completing the Maintenance Request"}

        doc.closed_date = date.today()
        await save_doc(doc, db)
        return {"status": "success", "message": "Maintenance Request completed", "data": {"closed_date": str(date.today())}}

    elif action_slug == "reopen":
        # Clear closed_date and cascade reopen to WOA and WO
        wo_activity_id = getattr(doc, 'work_order_activity', None)
        if not wo_activity_id:
            return {"status": "error", "message": "No Work Order Activity linked to this Maintenance Request"}

        wo_activity = await get_doc("work_order_activity", wo_activity_id, db)
        if not wo_activity:
            return {"status": "error", "message": f"Work Order Activity '{wo_activity_id}' not found"}

        # Clear closed_date on MR
        doc.closed_date = None
        await save_doc(doc, db, commit=False)

        # Reopen the work order activity
        wo_activity.workflow_state = "in_progress"
        await save_doc(wo_activity, db, commit=False)

        # If work order is closed, reopen it too
        work_order_id = getattr(wo_activity, 'work_order', None)
        if work_order_id:
            work_order = await get_doc("work_order", work_order_id, db)
            if work_order and getattr(work_order, 'workflow_state', None) == "closed":
                work_order.workflow_state = "in_progress"
                await save_doc(work_order, db, commit=False)

        await db.commit()
        return {"status": "success", "message": "Maintenance Request reopened. Linked Work Order Activity and Work Order have been reverted to In Progress."}

    return {"status": "success", "message": f"Maintenance Request workflow '{action}' allowed"}


async def _approve_and_generate_wo(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Path A — Approve action handler.
    Creates Work Order (Requested state) + Work Order Activity (Awaiting Resources).
    Populates WOA resources from PMA if linked.
    Links WOA back to the Maintenance Request via work_order_activity field.
    """
    maint_req_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    asset_id = getattr(doc, 'asset', None)
    site = getattr(doc, 'site', None)
    department = getattr(doc, 'department', None)
    priority = getattr(doc, 'priority', None)
    due_date = getattr(doc, 'due_date', None)
    pma_id = getattr(doc, 'planned_maintenance_activity', None)
    request_type = getattr(doc, 'request_type', None)
    description = getattr(doc, 'description', '') or ''

    if not asset_id:
        return {"status": "error", "message": "Asset is required for Approve action"}
    if not site:
        return {"status": "error", "message": "Site is required for Approve action"}
    if not department:
        return {"status": "error", "message": "Department is required for Approve action"}

    asset = await get_doc("asset", asset_id, db)
    if not asset:
        return {"status": "error", "message": f"Asset '{asset_id}' not found"}

    # Build WO description from asset + request type
    wo_description = f"WO for {maint_req_id} – {getattr(asset, 'description', asset_id) or asset_id}"
    if request_type:
        rat = await get_value("request_activity_type", {"id": request_type}, "*", db)
        if rat:
            wo_description = f"{rat.get('type', '')} WO for {maint_req_id} – {getattr(asset, 'description', asset_id) or asset_id}"

    # Determine work_order_type from request_activity_type
    work_order_type = None
    if request_type:
        rat = await get_value("request_activity_type", {"id": request_type}, "*", db)
        if rat:
            rat_type = rat.get("type", "")
            if "preventive" in rat_type.lower():
                work_order_type = "Preventive Maintenance"
            elif "corrective" in rat_type.lower():
                work_order_type = "Corrective Maintenance"

    # Create Work Order in Requested state
    new_work_order = await new_doc("work_order", db,
        description=wo_description,
        work_order_type=work_order_type,
        priority=priority,
        due_date=due_date,
        site=site,
        department=department,
        workflow_state="requested"
    )
    await save_doc(new_work_order, db, commit=False)

    # Create Work Order Activity in Awaiting Resources state
    wo_activity = await _create_work_order_activity(doc, pma_id, new_work_order, db)

    # Populate WOA resources from PMA if linked
    if pma_id:
        await _create_wo_resources_from_pma(wo_activity, pma_id, db)

    # Link WOA back to the Maintenance Request
    doc.work_order_activity = wo_activity.id
    await save_doc(doc, db)

    return {
        "status": "success",
        "message": f"Work Order {new_work_order.id} and Work Order Activity {wo_activity.id} created successfully",
        "data": {
            "action": "generate_id",
            "path": f"/work_order/{new_work_order.id}",
            "work_order_id": new_work_order.id,
            "work_order_activity_id": wo_activity.id
        }
    }


async def _emergency_generate_wo(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Path B — Submit for Emergency action handler.
    Creates Work Order (Requested state) + Work Order Activity (Awaiting Resources) with defaults.
    WO due_date = now(), cost_code and category_of_failure auto-filled from defaults.
    No PMA resources are loaded — WOA tabs start empty.
    """
    maint_req_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    asset_id = getattr(doc, 'asset', None)
    site = getattr(doc, 'site', None)
    department = getattr(doc, 'department', None)
    location = getattr(doc, 'location', None)
    request_type = getattr(doc, 'request_type', None)
    description = getattr(doc, 'description', '') or ''

    if not site:
        return {"status": "error", "message": "Site is required for emergency submission"}
    if not department:
        return {"status": "error", "message": "Department is required for emergency submission"}

    # Build WO description
    asset_label = asset_id
    if asset_id:
        asset = await get_doc("asset", asset_id, db)
        if asset:
            asset_label = getattr(asset, 'description', asset_id) or asset_id

    wo_description = f"EMERGENCY WO for {maint_req_id} – {asset_label}"

    # Auto-fill defaults: get cost_code from department
    default_cost_code = None
    if department:
        dept_rec = await get_value("department", {"id": department}, "default_cost_code", db)
        if dept_rec:
            default_cost_code = dept_rec.get("default_cost_code")
    
    default_cof = None  # Keep null for now as per Frappe behavior

    # WO type from request_activity_type
    work_order_type = "Corrective Maintenance"
    if request_type:
        rat = await get_value("request_activity_type", {"id": request_type}, "*", db)
        if rat:
            rat_type = rat.get("type", "")
            if "preventive" in rat_type.lower():
                work_order_type = "Preventive Maintenance"

    # Create Work Order — due_date = now() for emergency
    new_work_order = await new_doc("work_order", db,
        description=wo_description,
        work_order_type=work_order_type,
        priority="Emergency",
        due_date=date.today(),
        site=site,
        department=department,
        cost_code=default_cost_code,
        category_of_failure=default_cof,
        workflow_state="requested"
    )
    await save_doc(new_work_order, db, commit=False)

    # Build WOA description
    woa_description = f"Emergency: {asset_label}"

    # Create Work Order Activity — NO PMA resources loaded
    new_wo_activity = await new_doc("work_order_activity", db,
        description=woa_description,
        work_order=new_work_order.id,
        work_item_type="Asset",  # Emergency always sets to "Asset" like Frappe
        work_item=asset_id,
        activity_type=request_type,
        location=location,
        site=site,
        department=department,
        start_date=datetime.now(),
        workflow_state="awaiting_resources"
    )
    await save_doc(new_wo_activity, db, commit=False)

    # Link WOA back to the Maintenance Request
    doc.work_order_activity = new_wo_activity.id
    await save_doc(doc, db)

    return {
        "status": "success",
        "message": f"Emergency Work Order {new_work_order.id} and Work Order Activity {new_wo_activity.id} created",
        "data": {
            "action": "generate_id",
            "path": f"/work_order/{new_work_order.id}",
            "work_order_id": new_work_order.id,
            "work_order_activity_id": new_wo_activity.id
        }
    }


async def _create_work_order_activity(doc: Any, pma_id: str, work_order: Any, db: AsyncSession) -> Any:
    """Create Work Order Activity from Maintenance Request."""
    
    maint_act = None
    if pma_id:
        pma = await get_value("planned_maintenance_activity", pma_id, "*", db)
        if pma and pma.get("maintenance_activity"):
            maint_act = await get_value("maintenance_activity", pma["maintenance_activity"], "*", db)
    
    description = maint_act.get("activity_name") if maint_act else None
    
    wo_activity = await new_doc("work_order_activity", db,
        work_order=work_order.id if work_order else None,
        description=description,
        location=getattr(doc, 'location', None),
        work_item=getattr(doc, 'asset', None),
        work_item_type="Asset" if getattr(doc, 'asset', None) else "Non-Asset",
        position=getattr(doc, 'position', None),
        activity_type=getattr(doc, 'request_type', None),
        start_date=datetime.now(),
        site=getattr(doc, 'site', None),
        department=getattr(doc, 'department', None),
        workflow_state="awaiting_resources"
    )
    await save_doc(wo_activity, db, commit=False)
    await db.commit()
    
    return wo_activity


async def _create_wo_resources_from_pma(wo_activity: Any, pma_id: str, db: AsyncSession) -> None:
    """Create Work Order Labor, Equipment, Parts from Planned Maintenance Activity."""
    
    pma = await get_value("planned_maintenance_activity", pma_id, "*", db)
    if not pma or not pma.get("maintenance_activity"):
        return
    
    maint_act_id = pma["maintenance_activity"]
    
    # Create Work Order Checklist
    if pma.get("inspection_checklist"):
        checklist = await get_value("checklist", pma["inspection_checklist"], "*", db)
        if checklist:
            wo_checklist = await new_doc("work_order_checklist", db,
                work_order_activity=wo_activity.id,
                checklist_name=checklist.get("checklist_name"),
                inspection_date=datetime.now()
            )
            await save_doc(wo_checklist, db, commit=False)
            
            # Create checklist details
            checklist_details = await get_list("checklist_details", {"checklist": checklist["id"]}, db=db)
            for detail in checklist_details:
                wo_checklist_detail = await new_doc("work_order_checklist_detail", db,
                    work_order_checklist=wo_checklist.id,
                    item_name=detail.get("item_name"),
                    is_mandatory=detail.get("is_mandatory")
                )
                await save_doc(wo_checklist_detail, db, commit=False)
    
    # Create Work Order Equipment
    maint_equip = await get_value("maintenance_equipment", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_equip:
        wo_equip = await new_doc("work_order_equipment", db,
            work_order_activity=wo_activity.id,
            item=maint_equip.get("item"),
            equipment=maint_equip.get("equipment"),
            start_datetime=datetime.now()
        )
        await save_doc(wo_equip, db, commit=False)
    
    # Create Work Order Labor
    maint_trade = await get_value("maintenance_trade", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_trade:
        trade = await get_value("trade", maint_trade.get("trade"), "*", db)
        wo_labor = await new_doc("work_order_labor", db,
            work_order_activity=wo_activity.id,
            trade=maint_trade.get("trade"),
            trade_name=trade.get("trade_name") if trade else None,
            start_datetime=datetime.now()
        )
        await save_doc(wo_labor, db, commit=False)
    
    # Create Work Order Parts
    maint_part = await get_value("maintenance_parts", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_part:
        item = await get_value("item", maint_part.get("item"), "*", db)
        wo_parts = await new_doc("work_order_parts", db,
            work_order_activity=wo_activity.id,
            item=maint_part.get("item"),
            item_name=item.get("item_name") if item else None,
            unit_of_measure=item.get("uom") if item else None,
            total_actual_qty=item.get("actual_qty_on_hand") if item else None,
            total_avail_qty=item.get("available_capacity") if item else None,
            quantity_required=maint_part.get("quantity")
        )
        await save_doc(wo_parts, db, commit=False)
    
    await db.commit()


async def get_resource_availability_status(doc: Any, db: AsyncSession) -> dict:
    """
    Check resource availability for a Maintenance Request.
    
    Mirrors: get_maint_req_info() from Frappe
    """
    pma_id = getattr(doc, 'planned_maintenance_activity', None)
    due_date = getattr(doc, 'due_date', None)
    location = getattr(doc, 'location', None)
    asset_id = getattr(doc, 'asset', None)
    
    if not pma_id:
        return {"status": "success", "resource_availability_status": "Unknown"}
    
    pma = await get_value("planned_maintenance_activity", pma_id, "*", db)
    if not pma or not pma.get("maintenance_activity"):
        return {"status": "success", "resource_availability_status": "Unknown"}
    
    maint_act_id = pma["maintenance_activity"]
    
    # Get location from asset if not specified
    if not location and asset_id:
        asset = await get_value("asset", asset_id, "*", db)
        if asset:
            location = asset.get("location")
    
    trade_available = 0
    equip_available = 0
    materials_available = 0
    
    # Check Trade Availability
    maint_trade = await get_value("maintenance_trade", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_trade:
        trade_avail_list = await get_list("trade_availability", {"trade": maint_trade.get("trade")}, db=db)
        for ta in trade_avail_list:
            ta_date = ta.get("specific_datetime")
            if ta_date and due_date:
                if hasattr(ta_date, 'date'):
                    ta_date = ta_date.date()
                if ta_date == due_date:
                    available = ta.get("available_capacity") or 0
                    required = maint_trade.get("required_qty") or 0
                    if available >= required:
                        trade_available = 1
    
    # Check Equipment Availability
    maint_equip = await get_value("maintenance_equipment", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_equip:
        equip_avail_list = await get_list("asset_class_availability", {"asset_class": maint_equip.get("asset_class")}, db=db)
        for ea in equip_avail_list:
            ea_date = ea.get("specific_datetime")
            if ea_date and due_date:
                if hasattr(ea_date, 'date'):
                    ea_date = ea_date.date()
                if ea_date == due_date:
                    available = ea.get("available_capacity") or 0
                    required = maint_equip.get("required_qty") or 0
                    if available >= required:
                        equip_available = 1
    
    # Check Material Availability
    maint_part = await get_value("maintenance_parts", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_part and location:
        inventory = await get_value("inventory", {"item": maint_part.get("item"), "location": location}, "*", db)
        if inventory:
            available = inventory.get("available_inv") or 0
            required = maint_part.get("quantity") or 0
            if available >= required:
                materials_available = 1
    
    # Determine status
    if trade_available == 0 and equip_available == 0 and materials_available == 0:
        status = "Not Available"
    elif trade_available == 1 and equip_available == 1 and materials_available == 1:
        status = "Available"
    else:
        status = "Partially Available"
    
    return {"status": "success", "resource_availability_status": status}
