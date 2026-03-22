"""
Parts Reservation Server Actions
==================================
Registers server actions for reserving and releasing WO parts.
"""
from app.application.hooks.server_actions import server_actions


@server_actions.register("work_order_parts", "reserve_parts")
async def reserve_parts_action(doc, ctx):
    """Reserve inventory for Work Order Parts."""
    from app.services.parts_reservation import reserve_parts_for_wo
    wo_parts_id = doc.id if hasattr(doc, "id") else doc.get("id")
    return await reserve_parts_for_wo(wo_parts_id, ctx.db)


@server_actions.register("work_order_parts", "release_reservations")
async def release_reservations_action(doc, ctx):
    """Release all active reservations for Work Order Parts."""
    from app.services.parts_reservation import release_all_reservations_for_wo_parts
    wo_parts_id = doc.id if hasattr(doc, "id") else doc.get("id")
    return await release_all_reservations_for_wo_parts(wo_parts_id, ctx.db)
