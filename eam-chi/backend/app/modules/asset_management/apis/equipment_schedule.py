"""
Equipment Schedule Entity Business Logic

Mirrors: ci_eam/asset_management/doctype/equipment_schedule/equipment_schedule.py
- generate_equipment_availability(doc)

Uses document helpers for Frappe-like syntax.
"""
from typing import Any
from datetime import datetime, timedelta, time
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def generate_equipment_availability(doc: Any, db: AsyncSession) -> dict:
    """
    Generate Equipment Availability records from Equipment Schedule.
    
    Mirrors: generate_equipment_availability() from Frappe
    """
    if not doc:
        return {"status": "success", "message": "No equipment schedule provided. Skipping availability generation."}
    
    doc_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not doc_id:
        return {"status": "success", "message": "Equipment schedule name not provided. Skipping availability generation."}
    
    equipment_sched = await get_value("equipment_schedule", doc_id, "*", db)
    if not equipment_sched:
        return {"status": "success", "message": "Equipment Schedule not found. Skipping availability generation."}
    
    sched_details = await get_list("equipment_schedule_details", {"equipment_schedule": doc_id}, db=db)
    
    equipment_id = equipment_sched.get("equipment")
    equipment_group_id = equipment_sched.get("equipment_group")
    start_date = equipment_sched.get("start_date")
    end_date = equipment_sched.get("end_date")
    
    if equipment_id:
        # Single equipment
        equipment = await get_value("equipment", equipment_id, "*", db)
        equipment_name = await _get_equipment_name(equipment, db)
        
        all_dates = []
        for item in sched_details:
            if item.get("day"):
                dates = _generate_dates(start_date, end_date, item["day"])
                all_dates.extend(dates)
        
        sorted_dates = sorted(all_dates)
        for date_val in sorted_dates:
            day_name = date_val.strftime("%A")
            matching_items = [d for d in sched_details if d.get("day") == day_name]
            if matching_items:
                await _save_equipment_availability(equipment_id, date_val, matching_items[0], equipment_name, db)
    else:
        # Equipment group
        equipments = await get_list("equipment", {"equipment_group": equipment_group_id}, db=db)
        
        for equipment in equipments:
            equipment_name = await _get_equipment_name(equipment, db)
            
            all_dates = []
            for item in sched_details:
                if item.get("day"):
                    dates = _generate_dates(start_date, end_date, item["day"])
                    all_dates.extend(dates)
            
            sorted_dates = sorted(all_dates)
            for date_val in sorted_dates:
                day_name = date_val.strftime("%A")
                matching_items = [d for d in sched_details if d.get("day") == day_name]
                if matching_items:
                    await _save_equipment_availability(equipment["id"], date_val, matching_items[0], equipment_name, db)
    
    await db.commit()
    return {"status": "success", "message": "Equipment availability generated successfully"}


async def _get_equipment_name(equipment: dict, db: AsyncSession) -> str:
    """Get equipment display name based on type."""
    if not equipment:
        return ""
    
    if equipment.get("equipment_type") == "Rented":
        return equipment.get("pr_line_no", "")
    else:
        return equipment.get("asset_description", equipment.get("description", ""))


async def _save_equipment_availability(equipment_id: str, date_val: Any, schedule_item: dict, equipment_name: str, db: AsyncSession) -> bool:
    """Save or update Equipment Availability record."""
    
    existing = await get_value("equipment_availability", {"equipment": equipment_id, "date": date_val}, "*", db)
    
    start_time = schedule_item.get("start_time")
    end_time = schedule_item.get("end_time")
    time_list = _get_times_within_range(start_time, end_time, interval_minutes=60)
    sorted_times = sorted(time_list)
    
    if existing:
        equip_avail_id = existing["id"]
        
        for time_val in sorted_times:
            existing_detail = await get_value("equipment_availability_details", {"equipment_availability": equip_avail_id, "hour": time_val}, "*", db)
            
            if not existing_detail:
                new_detail = await new_doc("equipment_availability_details", db,
                    equipment_availability=equip_avail_id,
                    equipment=equipment_id,
                    hour=time_val,
                    status="Available"
                )
                await save_doc(new_detail, db, commit=False)
    else:
        new_avail = await new_doc("equipment_availability", db,
            equipment=equipment_id,
            equipment_name=equipment_name,
            date=date_val
        )
        await save_doc(new_avail, db, commit=False)
        
        for time_val in sorted_times:
            new_detail = await new_doc("equipment_availability_details", db,
                equipment_availability=new_avail.id,
                equipment=equipment_id,
                hour=time_val,
                status="Available"
            )
            await save_doc(new_detail, db, commit=False)
    
    return True


def _generate_dates(start_date: Any, end_date: Any, selected_day: str) -> list:
    """Generate all dates between start and end that fall on the specified weekday."""
    days_of_week = {
        "sunday": 6,
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
    }
    
    selected_day = selected_day.lower()
    if selected_day not in days_of_week:
        return []
    
    target_day = days_of_week[selected_day]
    current_date = start_date
    
    # Find the first occurrence of the target day
    while current_date.weekday() != target_day:
        current_date += timedelta(days=1)
    
    matching_dates = []
    while current_date <= end_date:
        matching_dates.append(current_date)
        current_date += timedelta(weeks=1)
    
    return matching_dates


def _get_times_within_range(start_time: Any, end_time: Any, interval_minutes: int = 60) -> list:
    """Generate all times between start and end with a fixed interval."""
    if not start_time or not end_time:
        return []
    
    # Convert to time objects if needed
    if hasattr(start_time, 'total_seconds'):
        start_time = _convert_timedelta_to_time(start_time)
    if hasattr(end_time, 'total_seconds'):
        end_time = _convert_timedelta_to_time(end_time)
    
    today = datetime.today().date()
    start_datetime = datetime.combine(today, start_time)
    end_datetime = datetime.combine(today, end_time)
    
    if start_datetime > end_datetime:
        return []
    
    current_time = start_datetime
    times = []
    while current_time <= end_datetime:
        times.append(current_time.time())
        current_time += timedelta(minutes=interval_minutes)
    
    return times


def _convert_timedelta_to_time(td: Any) -> time:
    """Convert timedelta to time object."""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600) % 24
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return time(hour=hours, minute=minutes, second=seconds)
