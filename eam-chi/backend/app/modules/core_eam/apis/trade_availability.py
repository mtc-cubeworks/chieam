"""
Trade Availability Post-Save Business Logic

Mirrors: ci_eam/core_enterprise_asset_management/doctype/trade_availability/trade_availability.py
- get_available_reserved_capacity(doc)

Calculates available and reserved capacity from Labor Availability Details.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, save_doc


async def calculate_trade_capacity(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: Calculate available/reserved capacity for a Trade Availability record.

    Logic:
    1. Get all Trade Labor records for the trade
    2. For each labor, check Labor Availability for the date
    3. For each Labor Availability, check Labor Availability Details for the hour
    4. Count Available and Reserved statuses
    5. Update the Trade Availability record with calculated values
    """
    trade_avail_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not trade_avail_id:
        return {"status": "success", "message": "No trade availability ID. Skipping."}

    trade_avail = await get_doc("trade_availability", trade_avail_id, db)
    if not trade_avail:
        return {"status": "error", "message": f"Trade Availability {trade_avail_id} not found."}

    trade_id = getattr(trade_avail, 'trade', None)
    specific_datetime = getattr(trade_avail, 'specific_datetime', None)
    if not trade_id or not specific_datetime:
        return {"status": "success", "message": "Missing trade or datetime. Skipping."}

    available = 0
    reserved = 0

    # Get all Trade Labor records for this trade
    trade_labors = await get_list("trade_labor", {"trade": trade_id}, db=db)

    for tl in trade_labors:
        labor_id = tl.get("labor")
        if not labor_id:
            continue

        # Get Labor Availability for the date
        avail_date = specific_datetime.date() if hasattr(specific_datetime, 'date') else specific_datetime
        labor_avail = await get_value(
            "labor_availability",
            {"labor": labor_id, "date": avail_date},
            "*", db
        )
        if not labor_avail:
            continue

        # Get Labor Availability Details for the hour
        avail_hour = specific_datetime.time() if hasattr(specific_datetime, 'time') else None
        if avail_hour is None:
            continue

        labor_avail_detail = await get_value(
            "labor_availability_details",
            {"labor_availability": labor_avail["id"], "hour": avail_hour},
            "*", db
        )
        if not labor_avail_detail:
            continue

        status = labor_avail_detail.get("status")
        if status == "Available":
            available += 1
        elif status == "Reserved":
            reserved += 1

    # Update the Trade Availability record
    trade_avail.reserved_capacity = reserved
    trade_avail.available_capacity = available
    await save_doc(trade_avail, db)

    return {"status": "success", "message": f"Trade Availability updated: available={available}, reserved={reserved}"}
