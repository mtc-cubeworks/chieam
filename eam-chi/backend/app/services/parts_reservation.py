"""
Parts Reservation Service
==========================
Reserve and release inventory for scheduled Work Order parts.
Prevents scheduled PM parts from being consumed by emergency work.
"""
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def reserve_parts_for_wo(wo_parts_id: str, db: AsyncSession) -> dict:
    """
    Reserve inventory for a Work Order Parts record.

    Finds available inventory for the item, creates a reservation record,
    and adjusts inventory available/reserved quantities.
    """
    wo_parts = await get_doc("work_order_parts", wo_parts_id, db)
    if not wo_parts:
        return {"status": "error", "message": f"Work Order Parts '{wo_parts_id}' not found"}

    item_id = getattr(wo_parts, "item", None)
    qty_required = getattr(wo_parts, "quantity_required", 0) or 0
    qty_issued = getattr(wo_parts, "quantity_issued", 0) or 0
    qty_to_reserve = qty_required - qty_issued

    if qty_to_reserve <= 0:
        return {"status": "success", "message": "No quantity to reserve (already issued)"}

    # Check for existing active reservations
    existing = await get_list(
        "work_order_parts_reservation",
        {"work_order_parts": wo_parts_id, "status": "Reserved"},
        db=db,
    )
    already_reserved = sum(float(r.get("quantity_reserved", 0) or 0) for r in existing)
    qty_to_reserve = qty_to_reserve - already_reserved
    if qty_to_reserve <= 0:
        return {"status": "success", "message": "Parts already fully reserved"}

    if not item_id:
        return {"status": "error", "message": "No item linked to Work Order Parts"}

    # Find available inventory records for this item
    inventories = await get_list("inventory", {"item": item_id}, db=db)
    if not inventories:
        return {
            "status": "error",
            "message": f"No inventory found for item '{item_id}'. Consider creating a Purchase Request.",
        }

    reserved_total = 0
    for inv_dict in inventories:
        if qty_to_reserve <= 0:
            break

        available = int(inv_dict.get("available_inv", 0) or 0)
        if available <= 0:
            continue

        reserve_qty = min(available, int(qty_to_reserve))

        # Create reservation record
        reservation = await new_doc("work_order_parts_reservation", db,
            work_order_parts=wo_parts_id,
            item_id=item_id,
            item=inv_dict.get("item_name") or item_id,
            unit_of_measure=getattr(wo_parts, "unit_of_measure", None),
            inventory=inv_dict["id"],
            avail_quantity_data=str(available),
            date_reserved=datetime.now(),
            quantity_reserved=float(reserve_qty),
            status="Reserved",
        )
        if reservation:
            await save_doc(reservation, db, commit=False)

        # Update inventory quantities
        inv_doc = await get_doc("inventory", inv_dict["id"], db)
        if inv_doc:
            inv_doc.available_inv = (getattr(inv_doc, "available_inv", 0) or 0) - reserve_qty
            inv_doc.reserved_inv = (getattr(inv_doc, "reserved_inv", 0) or 0) + reserve_qty
            await save_doc(inv_doc, db, commit=False)

        # Update item reserved capacity
        item_doc = await get_doc("item", item_id, db)
        if item_doc:
            item_doc.reserved_capacity = (getattr(item_doc, "reserved_capacity", 0) or 0) + reserve_qty
            item_doc.available_capacity = (getattr(item_doc, "available_capacity", 0) or 0) - reserve_qty
            await save_doc(item_doc, db, commit=False)

        reserved_total += reserve_qty
        qty_to_reserve -= reserve_qty

    await db.commit()

    if reserved_total == 0:
        return {
            "status": "error",
            "message": "Insufficient available inventory to reserve. Consider creating a Purchase Request.",
        }

    shortfall = (qty_required - qty_issued - already_reserved) - reserved_total
    msg = f"Reserved {reserved_total} unit(s) for {wo_parts_id}"
    if shortfall > 0:
        msg += f". Shortfall: {shortfall} unit(s) — consider procurement."

    return {"status": "success", "message": msg}


async def release_reservation(reservation_id: str, db: AsyncSession) -> dict:
    """
    Release a specific parts reservation, restoring inventory availability.
    Called when a WO is cancelled or parts are no longer needed.
    """
    res_doc = await get_doc("work_order_parts_reservation", reservation_id, db)
    if not res_doc:
        return {"status": "error", "message": f"Reservation '{reservation_id}' not found"}

    if getattr(res_doc, "status", None) != "Reserved":
        return {"status": "success", "message": "Reservation already released"}

    qty = float(getattr(res_doc, "quantity_reserved", 0) or 0)
    inv_id = getattr(res_doc, "inventory", None)
    item_id = getattr(res_doc, "item_id", None)

    # Restore inventory availability
    if inv_id and qty > 0:
        inv_doc = await get_doc("inventory", inv_id, db)
        if inv_doc:
            inv_doc.available_inv = (getattr(inv_doc, "available_inv", 0) or 0) + int(qty)
            inv_doc.reserved_inv = max((getattr(inv_doc, "reserved_inv", 0) or 0) - int(qty), 0)
            await save_doc(inv_doc, db, commit=False)

        if item_id:
            item_doc = await get_doc("item", item_id, db)
            if item_doc:
                item_doc.reserved_capacity = max((getattr(item_doc, "reserved_capacity", 0) or 0) - int(qty), 0)
                item_doc.available_capacity = (getattr(item_doc, "available_capacity", 0) or 0) + int(qty)
                await save_doc(item_doc, db, commit=False)

    res_doc.status = "Released"
    await save_doc(res_doc, db, commit=False)
    await db.commit()

    return {"status": "success", "message": f"Reservation {reservation_id} released ({int(qty)} unit(s))"}


async def release_all_reservations_for_wo_parts(wo_parts_id: str, db: AsyncSession) -> dict:
    """Release all active reservations for a WO Parts record."""
    reservations = await get_list(
        "work_order_parts_reservation",
        {"work_order_parts": wo_parts_id, "status": "Reserved"},
        db=db,
    )
    released = 0
    for res in reservations:
        result = await release_reservation(res["id"], db)
        if result["status"] == "success":
            released += 1
    return {"status": "success", "message": f"Released {released} reservation(s)"}
