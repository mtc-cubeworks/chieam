"""
Maintenance Request Server Actions

Mirrors:
- ci_eam/maintenance_management/doctype/maintenance_request/maintenance_request.py
  - generate_maint_order(doc)
  - create_purchase_request(doc_id, doctype)

Server actions callable from frontend via entity action buttons.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc
from app.services.server_actions import server_actions, ActionContext


async def generate_maintenance_order(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Create a Maintenance Order + Maintenance Order Detail from a Maintenance Request.
    Checks resource availability (trade, equipment, materials).

    Mirrors: generate_maint_order() from Frappe
    """
    mr_id = doc.id if hasattr(doc, 'id') else (doc.get('id') if isinstance(doc, dict) else None)
    if not mr_id:
        return {"status": "error", "message": "Maintenance Request ID is required."}

    asset_id = getattr(doc, 'asset', None) if hasattr(doc, 'asset') else (doc.get('asset') if isinstance(doc, dict) else None)
    if not asset_id:
        return {"status": "error", "message": "Asset is required."}

    maint_req = await get_value("maintenance_request", {"id": mr_id}, "*", db)
    if not maint_req:
        return {"status": "error", "message": f"Maintenance Request '{mr_id}' not found."}

    asset_doc = await get_value("asset", {"id": asset_id}, "*", db)
    if not asset_doc:
        return {"status": "error", "message": f"Asset '{asset_id}' not found."}

    try:
        # Create Maintenance Order
        new_mo = await new_doc("maintenance_order", db,
            created_date=date.today(),
        )
        await save_doc(new_mo, db, commit=False)

        # Create Maintenance Order Detail with resource availability check
        resource_status = await _check_resource_availability(maint_req, asset_doc, db)

        new_mod = await new_doc("maintenance_order_detail", db,
            maintenance_order=new_mo.id,
            seq_num=1,
            maint_req=mr_id,
            asset=asset_id,
            due_date=maint_req.get("due_date"),
            resource_availability_status=resource_status,
        )
        await save_doc(new_mod, db, commit=False)

        await db.commit()
        return {
            "status": "success",
            "message": "Successfully created maintenance order.",
            "action": "generate_id",
            "path": f"/maintenance_order/{new_mo.id}",
            "data": {"maintenance_order_id": new_mo.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to generate maintenance order: {str(e)}"}


async def create_purchase_request_from_context(
    doc_id: str, entity_name: str, db: AsyncSession, user: Any
) -> dict:
    """
    Create a Purchase Request linked to a Work Order Activity or Maintenance Request.

    Mirrors: create_purchase_request() from Frappe
    """
    if not doc_id:
        return {"status": "error", "message": "Document ID is required."}

    allowed = ["work_order_activity", "maintenance_request"]
    if entity_name not in allowed:
        return {"status": "error", "message": f"Invalid entity '{entity_name}'. Allowed: {', '.join(allowed)}"}

    # Validate the linked document exists
    linked_doc = await get_value(entity_name, {"id": doc_id}, "*", db)
    if not linked_doc:
        return {"status": "error", "message": f"{entity_name} '{doc_id}' not found."}

    try:
        pr_kwargs = {"date_requested": date.today()}
        if entity_name == "work_order_activity":
            pr_kwargs["work_activity_id"] = doc_id
        elif entity_name == "maintenance_request":
            pr_kwargs["maintenance_request"] = doc_id

        new_pr = await new_doc("purchase_request", db, **pr_kwargs)
        await save_doc(new_pr, db)

        return {
            "status": "success",
            "message": "Successfully created purchase request for resource allocation.",
            "action": "generate_id",
            "path": f"/purchase_request/{new_pr.id}",
            "data": {"purchase_request_id": new_pr.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create purchase request: {str(e)}"}


async def _check_resource_availability(maint_req: dict, asset_doc: dict, db: AsyncSession) -> str:
    """Check trade, equipment, and material availability. Returns status string."""
    pma_id = maint_req.get("planned_maintenance_activity")
    if not pma_id:
        return "Unknown"

    pma = await get_value("planned_maintenance_activity", {"id": pma_id}, "*", db)
    if not pma or not pma.get("maintenance_activity"):
        return "Unknown"

    maint_act_id = pma["maintenance_activity"]
    due_date = maint_req.get("due_date")
    location = maint_req.get("location") or asset_doc.get("location")

    trade_ok = 0
    equip_ok = 0
    materials_ok = 0

    # Trade Availability
    maint_trade = await get_value("maintenance_trade", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_trade:
        trade_avails = await get_list("trade_availability", {"trade": maint_trade.get("trade")}, db=db)
        for ta in trade_avails:
            ta_dt = ta.get("specific_datetime")
            if ta_dt and due_date:
                ta_date = ta_dt.date() if hasattr(ta_dt, 'date') else ta_dt
                if ta_date == due_date:
                    avail = ta.get("available_capacity") or 0
                    req = maint_trade.get("required_qty") or 0
                    if int(avail) >= int(req):
                        trade_ok = 1

    # Equipment Availability
    maint_equip = await get_value("maintenance_equipment", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_equip:
        equip_avails = await get_list("asset_class_availability", {"asset_class": maint_equip.get("asset_class")}, db=db)
        for ea in equip_avails:
            ea_dt = ea.get("specific_datetime")
            if ea_dt and due_date:
                ea_date = ea_dt.date() if hasattr(ea_dt, 'date') else ea_dt
                if ea_date == due_date:
                    avail = ea.get("available_capacity") or 0
                    req = maint_equip.get("required_qty") or 0
                    if int(avail) >= int(req):
                        equip_ok = 1

    # Material Availability
    maint_part = await get_value("maintenance_parts", {"maintenance_activity": maint_act_id}, "*", db)
    if maint_part and location:
        inventory = await get_value("inventory", {"item": maint_part.get("item"), "location": location}, "*", db)
        if inventory:
            avail = inventory.get("available_inv") or 0
            req = maint_part.get("quantity") or 0
            if int(avail) >= int(req):
                materials_ok = 1

    if trade_ok == 0 and equip_ok == 0 and materials_ok == 0:
        return "Not Available"
    elif trade_ok == 1 and equip_ok == 1 and materials_ok == 1:
        return "Available"
    else:
        return "Partially Available"


# --- Server Action Registrations ---

@server_actions.register("maintenance_request", "generate_maint_order")
async def generate_maint_order_action(ctx: ActionContext):
    """Server action: Generate Maintenance Order from Maintenance Request."""
    return await generate_maintenance_order(ctx.doc, ctx.db, ctx.user)


@server_actions.register("maintenance_request", "create_purchase_request")
async def create_purchase_request_action(ctx: ActionContext):
    """Server action: Create Purchase Request from Maintenance Request."""
    doc_id = ctx.doc.id if hasattr(ctx.doc, 'id') else ctx.params.get("doc_id")
    return await create_purchase_request_from_context(doc_id, "maintenance_request", ctx.db, ctx.user)
