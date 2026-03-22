"""
Asset Class Availability Post-Save Business Logic

Mirrors: ci_eam/asset_management/doctype/asset_class_availability/asset_class_availability.py
- get_available_reserved_capacity(doc)

Calculates available and reserved capacity from Equipment Availability Details.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc


async def calculate_asset_class_capacity(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: Calculate available/reserved capacity for an Asset Class Availability record.

    Logic:
    1. Get all Assets of the asset_class (owned)
    2. For each asset, find Equipment → Equipment Availability → Details for the datetime
    3. Count Available and Reserved statuses
    4. Also check rented equipment via Purchase Request Line
    5. Update the record with calculated values
    """
    aca_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not aca_id:
        return {"status": "success", "message": "No ACA ID. Skipping."}

    aca = await get_doc("asset_class_availability", aca_id, db)
    if not aca:
        return {"status": "success", "message": "Asset Class Availability not found. Skipping."}

    asset_class_id = getattr(aca, 'asset_class', None)
    specific_datetime = getattr(aca, 'specific_datetime', None)
    if not asset_class_id or not specific_datetime:
        return {"status": "success", "message": "Missing asset_class or datetime. Skipping."}

    available = 0
    reserved = 0

    avail_date = specific_datetime.date() if hasattr(specific_datetime, 'date') else specific_datetime
    avail_time = specific_datetime.time() if hasattr(specific_datetime, 'time') else None

    # --- Owned assets ---
    assets = await get_list("asset", {"asset_class": asset_class_id}, db=db)
    for asset in assets:
        asset_id = asset.get("id")
        if not asset_id:
            continue

        # Find equipment for this asset
        equip = await get_value("equipment", {"asset": asset_id}, "*", db)
        if not equip:
            continue

        # Find equipment availability for the date
        equip_avail = await get_value(
            "equipment_availability",
            {"equipment": equip["id"], "date": avail_date},
            "*", db
        )
        if not equip_avail:
            continue

        # Find equipment availability details for the hour
        if avail_time is not None:
            equip_avail_detail = await get_value(
                "equipment_availability_details",
                {"equipment_availability": equip_avail["id"], "hour": avail_time},
                "*", db
            )
            if equip_avail_detail:
                status = equip_avail_detail.get("status")
                if status == "Available":
                    available += 1
                elif status == "Reserved":
                    reserved += 1

    # --- Rented equipment ---
    rented_equips = await get_list("equipment", {"equipment_type": "Rented"}, db=db)
    for equip in rented_equips:
        pr_line_id = equip.get("pr_line_no")
        if not pr_line_id:
            continue

        pr_line = await get_value("purchase_request_line", {"id": pr_line_id}, "*", db)
        if not pr_line:
            continue

        item = await get_value("item", {"id": pr_line.get("item")}, "*", db)
        if not item or item.get("asset_class") != asset_class_id:
            continue

        equip_avail = await get_value(
            "equipment_availability",
            {"equipment": equip["id"], "date": avail_date},
            "*", db
        )
        if not equip_avail:
            continue

        if avail_time is not None:
            equip_avail_detail = await get_value(
                "equipment_availability_details",
                {"equipment_availability": equip_avail["id"], "hour": avail_time},
                "*", db
            )
            if equip_avail_detail:
                status = equip_avail_detail.get("status")
                if status == "Available":
                    available += 1
                elif status == "Reserved":
                    reserved += 1

    # Update the record
    aca.reserved_capacity = reserved
    aca.available_capacity = available
    await save_doc(aca, db)

    return {"status": "success", "message": f"Asset Class Availability updated: available={available}, reserved={reserved}"}
