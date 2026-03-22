"""
PM Calendar Seed Data
======================
Seeds the exact data from the Excel file:
- 32 maintenance activities
- 6 team members (employees + labor)
- 32 PM tasks for January 2026 (from PM Planner sheet)
- Holidays for 2026
Uses new_doc / save_doc for proper naming integration.
"""
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.document import new_doc, save_doc, get_doc, get_list


# ── Activities from Excel Settings col B ──────────────────────────────────────

ACTIVITIES = [
    "ENGINE AREA CLEANING/ INSPECTION",
    "BIOGRINDER INSPECTION/cleaning",
    "HOPPER 1 INSPECTION/cleaning",
    "HOSE PUMP INSPECTION AND CLEANING",
    "MIXERS INSPECTION(CHANGE OIL 5K)/cleaning",
    "AIR BLOWER INSPECTION/cleaning",
    "MEMBRANES CHECKING",
    "RECIRCULATION PUMP INSPECTION/cleaning",
    "GAS BLOWERS COMPONENTS INSPECTION/cleaning",
    "CHILLER INSPECTION/cleaning",
    "CARBON FILTER",
    "SEPARATOR inspection and cleaning",
    "TRUCK UNITS GREASING AND INSPECTION",
    "BOILER INSPECTION",
    "FLARE SYSTEM",
    "AIR COMPRESSORS inspection and cleaning",
    "GAS PIPES DRAINING",
    "GENERAL CLEANING",
    "VFD INSPECTION/CLEANING",
    "AIRCON CHECKING",
    "FAULTS CHECKING HMI",
    "CHILLER SERVICING",
    "SENSORS CHECKING",
    "GENSET INSPECTION",
    "VALVES INSPECTION",
    "PANEL FANS INSPECTION/ CLEANING",
    "ANALYZER CALIBRATION",
    "FLOWMETER INSPECTION",
    "GREASING ALL COMPONENTS",
    "HOPPER 2 INSPECTION",
    "FIRE EXTINQUISHER INSPECTION",
    "WAREHOUSE INSPECTION FOR THE PARTS",
]

# ── Team from Excel Settings col C ────────────────────────────────────────────

TEAM = ["BENROD", "DANNY", "MICHAEL", "ERNESTO", "JUN", "RONALD"]

# ── Holidays from Excel Settings col F (2026) ────────────────────────────────

HOLIDAYS_2026 = [
    ("2026-01-01", "New Year's Day"),
    ("2026-01-19", "Martin Luther King Jr. Day"),
    ("2026-02-02", "Groundhog Day"),
    ("2026-02-14", "Valentine's Day"),
    ("2026-02-16", "Presidents' Day"),
    ("2026-03-04", "Mardi Gras"),
    ("2026-04-01", "April Fools' Day"),
    ("2026-04-22", "Earth Day"),
    ("2026-05-04", "Star Wars Day"),
    ("2026-05-05", "Cinco de Mayo"),
    ("2026-05-10", "Mother's Day"),
    ("2026-05-18", "Victoria Day"),
    ("2026-05-25", "Memorial Day"),
    ("2026-06-14", "Flag Day"),
    ("2026-06-21", "Father's Day"),
    ("2026-07-04", "Independence Day"),
    ("2026-08-03", "Civic Holiday"),
    ("2026-08-31", "Summer Bank Holiday"),
    ("2026-09-07", "Labor Day"),
    ("2026-09-11", "Patriot Day"),
    ("2026-09-17", "Constitution Day"),
    ("2026-10-16", "Boss's Day"),
    ("2026-10-24", "United Nations Day"),
    ("2026-10-31", "Halloween"),
    ("2026-11-11", "Veterans Day"),
    ("2026-11-26", "Thanksgiving"),
    ("2026-12-07", "Pearl Harbor Day"),
    ("2026-12-24", "Christmas Eve"),
    ("2026-12-25", "Christmas Day"),
    ("2026-12-26", "Boxing Day"),
    ("2026-12-31", "New Year's Eve"),
]

# ── PM Planner tasks – Jan 2026, all 6 team members, varied statuses/times ───
# Cols: Status, Activity, Team Member, Event Time, Event Date

PM_TASKS = [
    # ── March 2026 (current month) ──────────────────────────────────────────
    # Week 1 – Mar 1–7
    ("COMPLETE",    "ENGINE AREA CLEANING/ INSPECTION",            "BENROD",  "07:00", "2026-03-02"),
    ("COMPLETE",    "GENERAL CLEANING",                            "DANNY",   "07:30", "2026-03-02"),
    ("COMPLETE",    "BIOGRINDER INSPECTION/cleaning",              "MICHAEL", "08:00", "2026-03-03"),
    ("COMPLETE",    "HOSE PUMP INSPECTION AND CLEANING",           "ERNESTO", "09:00", "2026-03-03"),
    ("COMPLETE",    "AIR BLOWER INSPECTION/cleaning",              "JUN",     "09:00", "2026-03-04"),
    ("COMPLETE",    "MEMBRANES CHECKING",                          "RONALD",  "10:00", "2026-03-04"),
    ("COMPLETE",    "MIXERS INSPECTION(CHANGE OIL 5K)/cleaning",   "BENROD",  "08:30", "2026-03-05"),
    # Week 2 – Mar 8–14
    ("COMPLETE",    "RECIRCULATION PUMP INSPECTION/cleaning",      "DANNY",   "08:30", "2026-03-09"),
    ("COMPLETE",    "GAS BLOWERS COMPONENTS INSPECTION/cleaning",  "MICHAEL", "09:00", "2026-03-09"),
    ("SCHEDULED",   "CHILLER INSPECTION/cleaning",                 "ERNESTO", "10:00", "2026-03-10"),
    ("SCHEDULED",   "CARBON FILTER",                               "JUN",     "11:00", "2026-03-10"),
    ("SCHEDULED",   "SEPARATOR inspection and cleaning",           "RONALD",  "08:00", "2026-03-11"),
    ("SCHEDULED",   "TRUCK UNITS GREASING AND INSPECTION",         "BENROD",  "08:00", "2026-03-11"),
    ("SCHEDULED",   "BOILER INSPECTION",                           "DANNY",   "09:00", "2026-03-12"),
    ("SCHEDULED",   "FLARE SYSTEM",                                "MICHAEL", "08:00", "2026-03-13"),
    # Week 3 – Mar 15–21
    ("IN PREP",     "AIR COMPRESSORS inspection and cleaning",     "ERNESTO", "10:00", "2026-03-16"),
    ("IN PREP",     "GAS PIPES DRAINING",                          "JUN",     "08:00", "2026-03-16"),
    ("IN PREP",     "VFD INSPECTION/CLEANING",                     "RONALD",  "09:30", "2026-03-17"),
    ("IN PREP",     "AIRCON CHECKING",                             "BENROD",  "08:00", "2026-03-17"),
    ("IN PREP",     "FAULTS CHECKING HMI",                         "DANNY",   "11:00", "2026-03-18"),
    ("ON HOLD",     "CHILLER SERVICING",                           "MICHAEL", "08:00", "2026-03-18"),
    ("ON HOLD",     "SENSORS CHECKING",                            "ERNESTO", "08:30", "2026-03-19"),
    # Week 4 – Mar 22–31
    ("PLANNED",     "GENSET INSPECTION",                           "JUN",     "09:00", "2026-03-23"),
    ("PLANNED",     "VALVES INSPECTION",                           "RONALD",  "08:00", "2026-03-23"),
    ("PLANNED",     "PANEL FANS INSPECTION/ CLEANING",             "BENROD",  "10:00", "2026-03-24"),
    ("PLANNED",     "ANALYZER CALIBRATION",                        "DANNY",   "08:00", "2026-03-24"),
    ("PLANNED",     "FLOWMETER INSPECTION",                        "MICHAEL", "09:00", "2026-03-25"),
    ("PLANNED",     "GREASING ALL COMPONENTS",                     "ERNESTO", "08:30", "2026-03-25"),
    ("PLANNED",     "HOPPER 2 INSPECTION",                         "JUN",     "08:00", "2026-03-26"),
    ("PLANNED",     "FIRE EXTINQUISHER INSPECTION",                "RONALD",  "07:00", "2026-03-26"),
    ("PLANNED",     "WAREHOUSE INSPECTION FOR THE PARTS",          "BENROD",  "07:30", "2026-03-27"),
    ("CANCELLED",   "HOPPER 1 INSPECTION/cleaning",                "DANNY",   "09:00", "2026-03-30"),
    # ── January 2026 ────────────────────────────────────────────────────────
    # Week 1 – Jan 1–7
    ("COMPLETE",    "ENGINE AREA CLEANING/ INSPECTION",            "BENROD",  "07:00", "2026-01-01"),
    ("COMPLETE",    "GENERAL CLEANING",                            "DANNY",   "07:30", "2026-01-01"),
    ("COMPLETE",    "BIOGRINDER INSPECTION/cleaning",              "BENROD",  "08:00", "2026-01-02"),
    ("COMPLETE",    "HOPPER 1 INSPECTION/cleaning",                "MICHAEL", "08:00", "2026-01-02"),
    ("COMPLETE",    "HOSE PUMP INSPECTION AND CLEANING",           "ERNESTO", "09:00", "2026-01-03"),
    ("COMPLETE",    "AIR BLOWER INSPECTION/cleaning",              "JUN",     "09:00", "2026-01-03"),
    ("COMPLETE",    "MEMBRANES CHECKING",                          "RONALD",  "10:00", "2026-01-04"),
    ("COMPLETE",    "MIXERS INSPECTION(CHANGE OIL 5K)/cleaning",   "BENROD",  "08:30", "2026-01-05"),
    ("COMPLETE",    "RECIRCULATION PUMP INSPECTION/cleaning",      "DANNY",   "08:30", "2026-01-05"),
    ("COMPLETE",    "GAS BLOWERS COMPONENTS INSPECTION/cleaning",  "MICHAEL", "09:00", "2026-01-06"),
    ("COMPLETE",    "CHILLER INSPECTION/cleaning",                 "ERNESTO", "10:00", "2026-01-07"),
    ("COMPLETE",    "CARBON FILTER",                               "JUN",     "11:00", "2026-01-07"),
    # Week 2 – Jan 8–14
    ("COMPLETE",    "SEPARATOR inspection and cleaning",           "RONALD",  "08:00", "2026-01-08"),
    ("COMPLETE",    "TRUCK UNITS GREASING AND INSPECTION",         "BENROD",  "08:00", "2026-01-09"),
    ("SCHEDULED",   "BOILER INSPECTION",                           "DANNY",   "09:00", "2026-01-09"),
    ("SCHEDULED",   "FLARE SYSTEM",                                "MICHAEL", "08:00", "2026-01-10"),
    ("SCHEDULED",   "AIR COMPRESSORS inspection and cleaning",     "ERNESTO", "10:00", "2026-01-10"),
    ("SCHEDULED",   "GAS PIPES DRAINING",                          "JUN",     "08:00", "2026-01-11"),
    ("SCHEDULED",   "VFD INSPECTION/CLEANING",                     "RONALD",  "09:30", "2026-01-12"),
    ("SCHEDULED",   "AIRCON CHECKING",                             "BENROD",  "08:00", "2026-01-13"),
    ("SCHEDULED",   "FAULTS CHECKING HMI",                         "DANNY",   "11:00", "2026-01-13"),
    ("SCHEDULED",   "CHILLER SERVICING",                           "MICHAEL", "08:00", "2026-01-14"),
    # Week 3 – Jan 15–21
    ("IN PREP",     "SENSORS CHECKING",                            "ERNESTO", "08:30", "2026-01-15"),
    ("IN PREP",     "GENSET INSPECTION",                           "JUN",     "09:00", "2026-01-15"),
    ("IN PREP",     "VALVES INSPECTION",                           "RONALD",  "08:00", "2026-01-16"),
    ("IN PREP",     "PANEL FANS INSPECTION/ CLEANING",             "BENROD",  "10:00", "2026-01-16"),
    ("IN PREP",     "ANALYZER CALIBRATION",                        "DANNY",   "08:00", "2026-01-17"),
    ("IN PREP",     "FLOWMETER INSPECTION",                        "MICHAEL", "09:00", "2026-01-19"),
    ("IN PREP",     "GREASING ALL COMPONENTS",                     "ERNESTO", "08:30", "2026-01-19"),
    ("IN PREP",     "HOPPER 2 INSPECTION",                         "JUN",     "08:00", "2026-01-20"),
    ("ON HOLD",     "FIRE EXTINQUISHER INSPECTION",                "RONALD",  "07:00", "2026-01-20"),
    ("ON HOLD",     "WAREHOUSE INSPECTION FOR THE PARTS",          "BENROD",  "07:30", "2026-01-21"),
    # Week 4 – Jan 22–31
    ("PLANNED",     "ENGINE AREA CLEANING/ INSPECTION",            "DANNY",   "08:00", "2026-01-22"),
    ("PLANNED",     "BIOGRINDER INSPECTION/cleaning",              "MICHAEL", "08:00", "2026-01-22"),
    ("PLANNED",     "HOSE PUMP INSPECTION AND CLEANING",           "ERNESTO", "09:00", "2026-01-23"),
    ("PLANNED",     "AIR BLOWER INSPECTION/cleaning",              "JUN",     "09:00", "2026-01-23"),
    ("PLANNED",     "CHILLER INSPECTION/cleaning",                 "RONALD",  "10:00", "2026-01-24"),
    ("PLANNED",     "CARBON FILTER",                               "BENROD",  "08:30", "2026-01-24"),
    ("PLANNED",     "SEPARATOR inspection and cleaning",           "DANNY",   "08:00", "2026-01-26"),
    ("PLANNED",     "BOILER INSPECTION",                           "MICHAEL", "09:00", "2026-01-26"),
    ("PLANNED",     "VFD INSPECTION/CLEANING",                     "ERNESTO", "08:00", "2026-01-27"),
    ("PLANNED",     "SENSORS CHECKING",                            "JUN",     "09:30", "2026-01-27"),
    ("PLANNED",     "GENSET INSPECTION",                           "RONALD",  "08:00", "2026-01-28"),
    ("PLANNED",     "VALVES INSPECTION",                           "BENROD",  "10:00", "2026-01-28"),
    ("PLANNED",     "FLOWMETER INSPECTION",                        "DANNY",   "08:00", "2026-01-29"),
    ("PLANNED",     "GREASING ALL COMPONENTS",                     "MICHAEL", "08:30", "2026-01-29"),
    ("CANCELLED",   "HOPPER 1 INSPECTION/cleaning",                "ERNESTO", "09:00", "2026-01-30"),
    ("PLANNED",     "GENERAL CLEANING",                            "JUN",     "07:30", "2026-01-30"),
    ("PLANNED",     "TRUCK UNITS GREASING AND INSPECTION",         "RONALD",  "08:00", "2026-01-31"),
    ("PLANNED",     "PANEL FANS INSPECTION/ CLEANING",             "BENROD",  "09:00", "2026-01-31"),
]

# Map Excel statuses → our workflow_state
STATUS_MAP = {
    "PLANNED": "Draft",
    "SCHEDULED": "Approved",
    "IN PREP": "Pending Approval",
    "ON HOLD": "Release",
    "CANCELLED": "Draft",
    "COMPLETE": "Completed",
}


async def _find_by_field(db: AsyncSession, entity: str, field: str, value):
    """Find a record by a specific field value."""
    from app.services.document_query import _get_model
    model = _get_model(entity)
    if not model:
        return None
    col = getattr(model, field, None)
    if col is None:
        return None
    result = await db.execute(select(model).where(col == value))
    # Return the first match (tolerant of duplicates in remote DB)
    return result.scalars().first()


def _generate_id(prefix: str, seq: int) -> str:
    return f"{prefix}-{seq:05d}"


async def _next_id(db: AsyncSession, model, prefix: str) -> str:
    """Get next sequential ID for a given model/prefix (tolerant of naming drift)."""
    result = await db.execute(select(func.count()).select_from(model))
    count = result.scalar() or 0
    for i in range(count + 1, count + 500):
        candidate = _generate_id(prefix, i)
        existing = await db.execute(select(model).where(model.id == candidate))
        if not existing.scalars().first():
            return candidate
    return _generate_id(prefix, count + 1)


async def seed_pm_calendar_data(db: AsyncSession):
    """Seed all PM calendar data from the Excel file using new_doc/save_doc."""
    print("🗓️  Seeding PM Calendar data...")

    # ── 1. Seed Activities ────────────────────────────────────────────────────
    activity_ids = {}  # name → id
    created_acts = 0
    for name in ACTIVITIES:
        existing = await _find_by_field(db, "maintenance_activity", "activity_name", name)
        if existing:
            activity_ids[name] = existing.id
        else:
            doc = await new_doc("maintenance_activity", db, activity_name=name, description=name)
            if doc:
                doc = await save_doc(doc, db, commit=False)
                activity_ids[name] = doc.id
                created_acts += 1
    await db.commit()
    print(f"  ✅ Activities: {created_acts} created, {len(activity_ids)} total")

    # ── 2. Seed Employees + Labor ─────────────────────────────────────────────
    labor_ids = {}  # name → labor_id
    created_emp = 0
    created_lbr = 0
    for name in TEAM:
        # Employee
        existing_emp = await _find_by_field(db, "employee", "employee_name", name)
        if existing_emp:
            emp_id = existing_emp.id
        else:
            emp = await new_doc("employee", db, employee_name=name, position="Technician")
            if emp:
                emp = await save_doc(emp, db, commit=False)
                emp_id = emp.id
                created_emp += 1

        # Labor
        existing_lbr = await _find_by_field(db, "labor", "laborer", name)
        if existing_lbr:
            labor_ids[name] = existing_lbr.id
        else:
            lbr = await new_doc("labor", db,
                                labor_type="Employee",
                                employee=emp_id,
                                laborer=name)
            if lbr:
                lbr = await save_doc(lbr, db, commit=False)
                labor_ids[name] = lbr.id
                created_lbr += 1

    await db.commit()
    print(f"  ✅ Team: {created_emp} employees, {created_lbr} labor records")

    # ── 3. Seed Holidays ──────────────────────────────────────────────────────
    created_hol = 0
    for date_str, name in HOLIDAYS_2026:
        d = date.fromisoformat(date_str)
        existing = await _find_by_field(db, "holiday", "holiday_date", d)
        if not existing:
            hol = await new_doc("holiday", db,
                                holiday_name=name,
                                holiday_date=d)
            if hol:
                await save_doc(hol, db, commit=False)
                created_hol += 1
    await db.commit()
    print(f"  ✅ Holidays: {created_hol} created")

    # ── 4. Seed Planned Maintenance Activities ────────────────────────────────
    pma_ids = {}  # activity_name → pma_id
    created_pma = 0
    for name, act_id in activity_ids.items():
        # Check if PMA already exists for this activity + Calendar Based
        from app.services.document_query import _get_model
        pma_model = _get_model("planned_maintenance_activity")
        if pma_model:
            result = await db.execute(
                select(pma_model).where(
                    pma_model.maintenance_activity == act_id,
                    pma_model.maintenance_schedule == "Calendar Based",
                )
            )
            existing = result.scalars().first()
            if existing:
                pma_ids[name] = existing.id
            else:
                new_id = await _next_id(db, pma_model, "PMA")
                pma = await new_doc("planned_maintenance_activity", db,
                                    id=new_id,
                                    maintenance_activity=act_id,
                                    maintenance_activity_name=name,
                                    maintenance_schedule="Calendar Based")
                if pma:
                    pma = await save_doc(pma, db, commit=False)
                    pma_ids[name] = pma.id
                    created_pma += 1
    await db.commit()
    print(f"  ✅ PMAs: {created_pma} created")

    # ── 5. Clear existing seeded PM Tasks then re-seed ───────────────────────
    from sqlalchemy import delete as sa_delete, or_
    from app.services.document_query import _get_model as _gm
    mr_model = _gm("maintenance_request")
    woa_model = _gm("work_order_activity")
    wo_model = _gm("work_order")
    from datetime import datetime as dt
    # Clear Jan and Mar 2026 seeded data
    seed_ranges = [
        (date(2026, 1, 1), date(2026, 1, 31)),
        (date(2026, 3, 1), date(2026, 3, 31)),
    ]
    all_woa_ids = []
    all_wo_ids = []
    for range_start, range_end in seed_ranges:
        if not mr_model or not hasattr(mr_model, "due_date"):
            continue
        # Collect WOA + WO ids linked to these MRs before deleting
        mr_result = await db.execute(
            select(mr_model).where(
                mr_model.due_date >= range_start,
                mr_model.due_date <= range_end,
            )
        )
        mrs = mr_result.scalars().all()
        for mr in mrs:
            if mr.work_order_activity:
                all_woa_ids.append(mr.work_order_activity)
            # WO id is stored on the WOA, collect via woa lookup later

        # Delete MRs first (FK owner)
        await db.execute(
            sa_delete(mr_model).where(
                mr_model.due_date >= range_start,
                mr_model.due_date <= range_end,
            )
        )
        await db.flush()

    # Collect WO ids from the WOAs before deleting them
    if woa_model and all_woa_ids:
        woa_result = await db.execute(
            select(woa_model).where(woa_model.id.in_(all_woa_ids))
        )
        for woa in woa_result.scalars().all():
            if hasattr(woa, "work_order") and woa.work_order:
                all_wo_ids.append(woa.work_order)
        # Delete WOAs
        await db.execute(sa_delete(woa_model).where(woa_model.id.in_(all_woa_ids)))
        await db.flush()

    # Delete WOs
    if wo_model and all_wo_ids:
        await db.execute(sa_delete(wo_model).where(wo_model.id.in_(all_wo_ids)))
        await db.flush()

    await db.commit()
    print("  🗑️  Cleared existing Jan + Mar 2026 tasks")

    created_tasks = 0
    for status, activity_name, team_member, time_str, date_str in PM_TASKS:
        task_date = date.fromisoformat(date_str)
        workflow_state = STATUS_MAP.get(status, "Draft")
        pma_id = pma_ids.get(activity_name)
        labor_id = labor_ids.get(team_member.strip())

        hour, minute = int(time_str.split(":")[0]), int(time_str.split(":")[1])
        start_dt = datetime(task_date.year, task_date.month, task_date.day, hour, minute)
        end_dt = start_dt + timedelta(minutes=30)

        # Create Work Order
        wo = await new_doc("work_order", db,
                           workflow_state="Requested",
                           work_order_type="Preventive Maintenance",
                           description=f"PM: {activity_name}",
                           due_date=task_date)
        if not wo:
            continue
        wo = await save_doc(wo, db, commit=False)

        # Create Work Order Activity
        woa = await new_doc("work_order_activity", db,
                            workflow_state="Awaiting Resources",
                            work_order=wo.id,
                            work_order_name=wo.description,
                            description=activity_name,
                            assigned_to=labor_id,
                            start_date=start_dt,
                            end_date=end_dt)
        if not woa:
            continue
        woa = await save_doc(woa, db, commit=False)

        # Create Maintenance Request
        mr = await new_doc("maintenance_request", db,
                           workflow_state=workflow_state,
                           due_date=task_date,
                           description=activity_name,
                           planned_maintenance_activity=pma_id,
                           work_order_activity=woa.id)
        if not mr:
            continue
        mr = await save_doc(mr, db, commit=False)
        created_tasks += 1

    await db.commit()
    print(f"  ✅ PM Tasks: {created_tasks} created (MR + WO + WOA each)")
    print("🗓️  PM Calendar seed complete!")
