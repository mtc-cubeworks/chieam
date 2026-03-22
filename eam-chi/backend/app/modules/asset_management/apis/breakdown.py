"""
Breakdown Entity Business Logic

Mirrors: ci_eam/asset_management/doctype/breakdown/breakdown.py
- create_update_equip_availability(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def create_update_equip_availability_on_save(doc: Any, db: AsyncSession) -> dict:
    """
    After save hook: Create/update Equipment Availability based on breakdown.
    
    Mirrors: create_update_equip_availability() from Frappe
    """
    equipment_id = getattr(doc, 'equipment', None)
    start_datetime = getattr(doc, 'start_datetime', None)
    end_datetime = getattr(doc, 'end_datetime', None)
    
    if not equipment_id or not start_datetime:
        return {"status": "success"}
    
    equipment = await get_doc("equipment", equipment_id, db)
    if not equipment:
        return {"status": "error", "message": f"Equipment {equipment_id} not found"}
    
    # Get or create Equipment Availability for the date
    breakdown_date = start_datetime.date() if hasattr(start_datetime, 'date') else start_datetime
    
    equip_avail = await get_value("equipment_availability", {"equipment": equipment_id, "date": breakdown_date}, "*", db)
    
    if not equip_avail:
        # Create new Equipment Availability
        equip_avail_doc = await new_doc("equipment_availability", db,
            equipment=equipment_id,
            date=breakdown_date
        )
        await save_doc(equip_avail_doc, db, commit=False)
        equip_avail = {"id": equip_avail_doc.id}
    
    # Mark hours within breakdown period as 'Breakdown'
    start_hour = start_datetime.hour if hasattr(start_datetime, 'hour') else 0
    end_hour = end_datetime.hour if end_datetime and hasattr(end_datetime, 'hour') else 23
    
    for hour in range(start_hour, end_hour + 1):
        hour_datetime = datetime.combine(breakdown_date, datetime.min.time().replace(hour=hour))
        
        # Check for existing detail
        detail = await get_value("equipment_availability_details", {"equipment_availability": equip_avail["id"], "specific_datetime": hour_datetime}, "*", db)
        
        if detail:
            detail_doc = await get_doc("equipment_availability_details", detail["id"], db)
            if detail_doc:
                detail_doc.status = "Breakdown"
                await save_doc(detail_doc, db, commit=False)
        else:
            new_detail = await new_doc("equipment_availability_details", db,
                equipment_availability=equip_avail["id"],
                equipment=equipment_id,
                specific_datetime=hour_datetime,
                status="Breakdown"
            )
            await save_doc(new_detail, db, commit=False)
    
    # Update Asset Class Availability if equipment has asset class
    inventory_id = getattr(equipment, 'inventory', None)
    if inventory_id:
        inventory = await get_value("inventory", inventory_id, "*", db)
        if inventory:
            item = await get_value("item", inventory.get("item"), "*", db)
            if item and item.get("asset_class"):
                await _update_asset_class_availability(item["asset_class"], breakdown_date, -1, db)
    
    await db.commit()
    return {"status": "success", "message": "Equipment availability updated for breakdown"}


async def _update_asset_class_availability(asset_class_id: str, date_val: Any, delta: int, db: AsyncSession) -> None:
    """Update Asset Class Availability capacity."""
    aca = await get_value("asset_class_availability", {"asset_class": asset_class_id, "specific_datetime": date_val}, "*", db)
    
    if aca:
        aca_doc = await get_doc("asset_class_availability", aca["id"], db)
        if aca_doc:
            available = (getattr(aca_doc, 'available_capacity', 0) or 0) + delta
            aca_doc.available_capacity = max(0, available)
            await save_doc(aca_doc, db, commit=False)


# Register server action
from app.services.server_actions import server_actions, ActionContext

@server_actions.register("breakdown", "create_update_equip_availability")
async def create_update_equip_availability_action(ctx: ActionContext):
    """Server action wrapper for create_update_equip_availability_on_save."""
    doc = ctx.params.get("doc")
    return await create_update_equip_availability_on_save(doc, ctx.db)
