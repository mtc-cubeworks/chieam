"""
Preventive Maintenance Calendar Feature
=========================================
Endpoints for managing PM tasks on a monthly calendar view.
Each task is a maintenance_request linked to a planned_maintenance_activity,
with a work_order_activity holding the assigned labor and time.
"""
from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Header, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, extract, delete, func
from pydantic import BaseModel as PydanticBaseModel

from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.core.serialization import record_to_dict
from app.infrastructure.database.repositories.entity_repository import get_entity_model

router = APIRouter(tags=["pm-calendar"])

# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class TaskCreate(PydanticBaseModel):
    activity_name: str
    due_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM (24h)
    assigned_to: Optional[str] = None  # labor id
    workflow_state: str = "Draft"
    site: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None


class TaskUpdate(PydanticBaseModel):
    activity_name: Optional[str] = None
    due_date: Optional[str] = None
    start_time: Optional[str] = None
    assigned_to: Optional[str] = None
    workflow_state: Optional[str] = None
    site: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None


class TaskReschedule(PydanticBaseModel):
    due_date: str  # YYYY-MM-DD


class TaskStatusUpdate(PydanticBaseModel):
    workflow_state: str


# ── Color mapping ─────────────────────────────────────────────────────────────

STATUS_COLORS = {
    "Draft": "#94a3b8",            # slate
    "Pending Approval": "#f59e0b", # amber
    "Approved": "#3b82f6",         # blue
    "Release": "#8b5cf6",          # violet
    "Completed": "#22c55e",        # green
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_id(prefix: str, seq: int) -> str:
    return f"{prefix}-{seq:05d}"


async def _next_id(db: AsyncSession, model, prefix: str) -> str:
    """Get next sequential ID for a given model/prefix."""
    result = await db.execute(
        select(func.count()).select_from(model)
    )
    count = result.scalar() or 0
    # Try incrementing until we find a free one
    for i in range(count + 1, count + 100):
        candidate = _generate_id(prefix, i)
        existing = await db.execute(select(model).where(model.id == candidate))
        if not existing.scalar_one_or_none():
            return candidate
    return _generate_id(prefix, count + 1)


async def _get_or_create_activity(db: AsyncSession, activity_name: str) -> str:
    """Get existing maintenance_activity by name or create new one. Returns id."""
    model = get_entity_model("maintenance_activity")
    result = await db.execute(
        select(model).where(model.activity_name == activity_name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing.id

    new_id = await _next_id(db, model, "MTACT")
    record = model(
        id=new_id,
        activity_name=activity_name,
        description=activity_name,
    )
    db.add(record)
    await db.flush()
    return new_id


async def _get_or_create_pma(
    db: AsyncSession,
    maintenance_activity_id: str,
    activity_name: str,
    maintenance_plan_id: Optional[str] = None,
) -> str:
    """Get or create planned_maintenance_activity for Calendar Based scheduling."""
    model = get_entity_model("planned_maintenance_activity")
    result = await db.execute(
        select(model).where(
            and_(
                model.maintenance_activity == maintenance_activity_id,
                model.maintenance_schedule == "Calendar Based",
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing.id

    new_id = await _next_id(db, model, "PMA")
    record = model(
        id=new_id,
        maintenance_activity=maintenance_activity_id,
        maintenance_activity_name=activity_name,
        maintenance_schedule="Calendar Based",
        maintenance_plan=maintenance_plan_id,
    )
    db.add(record)
    await db.flush()
    return new_id


def _build_task_response(mr_dict: dict, woa_dict: Optional[dict], activity_name: str, laborer_name: str, minimal: bool = False) -> dict:
    """Build a unified task response dict.
    
    Args:
        mr_dict: Maintenance request data
        woa_dict: Work order activity data
        activity_name: Activity name
        laborer_name: Laborer name
        minimal: If True, return only essential fields for list view (id, activity_name, workflow_state, due_date, start_time, color)
    """
    start_time = None
    if woa_dict and woa_dict.get("start_date"):
        sd = woa_dict["start_date"]
        if isinstance(sd, str) and "T" in sd:
            start_time = sd.split("T")[1][:5]
        elif isinstance(sd, datetime):
            start_time = sd.strftime("%H:%M")

    ws = mr_dict.get("workflow_state") or "Draft"
    
    if minimal:
        return {
            "id": mr_dict["id"],
            "activity_name": activity_name,
            "workflow_state": ws,
            "due_date": mr_dict.get("due_date"),
            "start_time": start_time or "08:00",
            "color": STATUS_COLORS.get(ws, "#94a3b8"),
        }
    
    return {
        "id": mr_dict["id"],
        "activity_name": activity_name,
        "workflow_state": ws,
        "due_date": mr_dict.get("due_date"),
        "start_time": start_time or "08:00",
        "laborer": laborer_name,
        "assigned_to": woa_dict.get("assigned_to") if woa_dict else None,
        "work_order_activity_id": woa_dict.get("id") if woa_dict else None,
        "planned_maintenance_activity": mr_dict.get("planned_maintenance_activity"),
        "site": mr_dict.get("site"),
        "department": mr_dict.get("department"),
        "notes": mr_dict.get("description"),
        "color": STATUS_COLORS.get(ws, "#94a3b8"),
    }


# ── SEED ENDPOINT ─────────────────────────────────────────────────────────────

SEED_ACTIVITIES = [
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

SEED_TEAM = ["BENROD", "DANNY", "MICHAEL", "ERNESTO", "JUN", "RONALD"]


@router.post("/pm-calendar/seed", name="pm_calendar_seed")
async def seed_pm_calendar(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Seed full PM calendar data from Excel: activities, team, holidays, and Jan 2026 tasks."""
    user = await get_current_user_from_token(authorization, db)

    from app.api.features.pm_calendar_seed import seed_pm_calendar_data
    await seed_pm_calendar_data(db)

    return {
        "status": "success",
        "message": "Seeded 32 activities, 6 team members, 31 holidays, and 32 PM tasks for Jan 2026",
    }


# ── GET TASKS ─────────────────────────────────────────────────────────────────

@router.get("/pm-calendar/tasks", name="pm_calendar_tasks")
async def get_tasks(
    year: int = Query(...),
    month: int = Query(...),
    site: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Fetch minimal PM calendar tasks for a given month (optimized for list view).
    
    Returns only essential fields: id, activity_name, workflow_state, due_date, start_time, color.
    For full task details, use GET /pm-calendar/tasks/{task_id}.
    """
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")
    pma_model = get_entity_model("planned_maintenance_activity")
    activity_model = get_entity_model("maintenance_activity")

    if not mr_model:
        return {"status": "error", "message": "maintenance_request model not found"}

    # Build filters for maintenance_requests in the given month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    conditions = [
        mr_model.due_date >= first_day,
        mr_model.due_date <= last_day,
        mr_model.planned_maintenance_activity.isnot(None),
    ]
    if site:
        conditions.append(mr_model.site == site)
    if department:
        conditions.append(mr_model.department == department)

    result = await db.execute(
        select(mr_model).where(and_(*conditions)).order_by(mr_model.due_date)
    )
    requests = result.scalars().all()

    # Batch-load related data (minimal: only activity names and start times)
    pma_ids = {r.planned_maintenance_activity for r in requests if r.planned_maintenance_activity}

    # Load PMAs → activity names
    activity_names = {}
    if pma_ids and pma_model and activity_model:
        pma_result = await db.execute(select(pma_model).where(pma_model.id.in_(pma_ids)))
        pmas = {p.id: p for p in pma_result.scalars().all()}
        act_ids = {p.maintenance_activity for p in pmas.values() if p.maintenance_activity}
        if act_ids:
            act_result = await db.execute(select(activity_model).where(activity_model.id.in_(act_ids)))
            acts = {a.id: a for a in act_result.scalars().all()}
            for pma_id, pma in pmas.items():
                act = acts.get(pma.maintenance_activity)
                activity_names[pma_id] = act.activity_name if act else (pma.maintenance_activity_name or pma_id)

    # Load WOAs only for start_time extraction (minimal data)
    woa_map = {}
    if woa_model:
        woa_ids = [r.work_order_activity for r in requests if r.work_order_activity]
        if woa_ids:
            woa_result = await db.execute(select(woa_model).where(woa_model.id.in_(woa_ids)))
            for woa in woa_result.scalars().all():
                woa_map[woa.id] = record_to_dict(woa)

    # Build minimal response
    tasks = []
    for req in requests:
        mr_dict = record_to_dict(req)
        woa_dict = woa_map.get(req.work_order_activity) if req.work_order_activity else None
        act_name = activity_names.get(req.planned_maintenance_activity, "Unknown Activity")

        tasks.append(_build_task_response(mr_dict, woa_dict, act_name, "", minimal=True))

    return {"status": "success", "data": tasks}


# ── GET TASK DETAIL ──────────────────────────────────────────────────────────

@router.get("/pm-calendar/tasks/{task_id}", name="pm_calendar_get_task")
async def get_task(
    task_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Fetch full details for a single PM calendar task."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")
    pma_model = get_entity_model("planned_maintenance_activity")
    activity_model = get_entity_model("maintenance_activity")
    labor_model = get_entity_model("labor")

    if not mr_model:
        return {"status": "error", "message": "maintenance_request model not found"}

    # Load MR
    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()
    if not mr:
        return {"status": "error", "message": f"Task {task_id} not found"}

    mr_dict = record_to_dict(mr)

    # Load activity name
    act_name = "Unknown Activity"
    if mr.planned_maintenance_activity and pma_model and activity_model:
        pma_result = await db.execute(select(pma_model).where(pma_model.id == mr.planned_maintenance_activity))
        pma = pma_result.scalar_one_or_none()
        if pma and pma.maintenance_activity:
            act_result = await db.execute(select(activity_model).where(activity_model.id == pma.maintenance_activity))
            act = act_result.scalar_one_or_none()
            if act:
                act_name = act.activity_name
            elif pma.maintenance_activity_name:
                act_name = pma.maintenance_activity_name

    # Load WOA
    woa_dict = None
    if mr.work_order_activity and woa_model:
        woa_result = await db.execute(select(woa_model).where(woa_model.id == mr.work_order_activity))
        woa = woa_result.scalar_one_or_none()
        if woa:
            woa_dict = record_to_dict(woa)

    # Load laborer name
    laborer_name = ""
    if woa_dict and woa_dict.get("assigned_to") and labor_model:
        lbr_result = await db.execute(select(labor_model).where(labor_model.id == woa_dict["assigned_to"]))
        lbr = lbr_result.scalar_one_or_none()
        if lbr:
            laborer_name = lbr.laborer or ""

    task = _build_task_response(mr_dict, woa_dict, act_name, laborer_name, minimal=False)
    return {"status": "success", "data": task}


# ── CREATE TASK ───────────────────────────────────────────────────────────────

@router.post("/pm-calendar/tasks", name="pm_calendar_create_task")
async def create_task(
    payload: TaskCreate,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a new PM calendar task (activity → PMA → MR → WOA chain)."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")
    wo_model = get_entity_model("work_order")

    if not mr_model or not woa_model or not wo_model:
        return {"status": "error", "message": "Required models not found"}

    # 1. Get or create maintenance_activity
    activity_id = await _get_or_create_activity(db, payload.activity_name)

    # 2. Get or create planned_maintenance_activity
    pma_id = await _get_or_create_pma(db, activity_id, payload.activity_name)

    # 3. Create a work order (parent for WOA)
    wo_id = await _next_id(db, wo_model, "WO")
    wo = wo_model(
        id=wo_id,
        workflow_state="Requested",
        work_order_type="Preventive Maintenance",
        description=f"PM: {payload.activity_name}",
        due_date=date.fromisoformat(payload.due_date),
        site=payload.site,
        department=payload.department,
    )
    db.add(wo)
    await db.flush()

    # 4. Create work_order_activity with time
    woa_id = await _next_id(db, woa_model, "WOACT")
    hour, minute = map(int, payload.start_time.split(":"))
    task_date = date.fromisoformat(payload.due_date)
    start_dt = datetime(task_date.year, task_date.month, task_date.day, hour, minute)
    end_dt = start_dt + timedelta(minutes=30)

    woa = woa_model(
        id=woa_id,
        workflow_state="Awaiting Resources",
        work_order=wo_id,
        work_order_name=wo.description,
        description=payload.activity_name,
        assigned_to=payload.assigned_to,
        start_date=start_dt,
        end_date=end_dt,
        site=payload.site,
        department=payload.department,
    )
    db.add(woa)
    await db.flush()

    # 5. Create maintenance_request
    mr_id = await _next_id(db, mr_model, "MTREQ")
    mr = mr_model(
        id=mr_id,
        workflow_state=payload.workflow_state,
        due_date=task_date,
        description=payload.notes or payload.activity_name,
        planned_maintenance_activity=pma_id,
        work_order_activity=woa_id,
        site=payload.site,
        department=payload.department,
    )
    db.add(mr)
    await db.commit()

    # Get laborer name
    laborer_name = ""
    if payload.assigned_to:
        labor_model = get_entity_model("labor")
        if labor_model:
            lbr_result = await db.execute(select(labor_model).where(labor_model.id == payload.assigned_to))
            lbr = lbr_result.scalar_one_or_none()
            if lbr:
                laborer_name = lbr.laborer or ""

    task = _build_task_response(
        record_to_dict(mr),
        record_to_dict(woa),
        payload.activity_name,
        laborer_name,
    )
    return {"status": "success", "data": task}


# ── UPDATE TASK ───────────────────────────────────────────────────────────────

@router.put("/pm-calendar/tasks/{task_id}", name="pm_calendar_update_task")
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing PM calendar task."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")

    if not mr_model:
        return {"status": "error", "message": "maintenance_request model not found"}

    # Load MR
    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()
    if not mr:
        return {"status": "error", "message": f"Task {task_id} not found"}

    # Update MR fields
    if payload.workflow_state is not None:
        mr.workflow_state = payload.workflow_state
    if payload.due_date is not None:
        mr.due_date = date.fromisoformat(payload.due_date)
    if payload.site is not None:
        mr.site = payload.site
    if payload.department is not None:
        mr.department = payload.department
    if payload.notes is not None:
        mr.description = payload.notes

    # Handle activity name change
    activity_name = payload.activity_name
    if activity_name:
        activity_id = await _get_or_create_activity(db, activity_name)
        pma_id = await _get_or_create_pma(db, activity_id, activity_name)
        mr.planned_maintenance_activity = pma_id

    # Update WOA
    woa_dict = None
    if mr.work_order_activity and woa_model:
        woa_result = await db.execute(select(woa_model).where(woa_model.id == mr.work_order_activity))
        woa = woa_result.scalar_one_or_none()
        if woa:
            if payload.assigned_to is not None:
                woa.assigned_to = payload.assigned_to
            if payload.start_time is not None or payload.due_date is not None:
                task_date = date.fromisoformat(payload.due_date) if payload.due_date else mr.due_date
                time_str = payload.start_time
                if time_str:
                    hour, minute = map(int, time_str.split(":"))
                else:
                    # preserve existing time
                    hour = woa.start_date.hour if woa.start_date else 8
                    minute = woa.start_date.minute if woa.start_date else 0
                start_dt = datetime(task_date.year, task_date.month, task_date.day, hour, minute)
                woa.start_date = start_dt
                woa.end_date = start_dt + timedelta(minutes=30)
            if payload.site is not None:
                woa.site = payload.site
            if payload.department is not None:
                woa.department = payload.department
            woa_dict = record_to_dict(woa)

    await db.commit()

    # Resolve names
    act_name = activity_name or "Unknown Activity"
    if not activity_name and mr.planned_maintenance_activity:
        pma_model = get_entity_model("planned_maintenance_activity")
        act_model = get_entity_model("maintenance_activity")
        if pma_model and act_model:
            pma_r = await db.execute(select(pma_model).where(pma_model.id == mr.planned_maintenance_activity))
            pma = pma_r.scalar_one_or_none()
            if pma and pma.maintenance_activity:
                act_r = await db.execute(select(act_model).where(act_model.id == pma.maintenance_activity))
                act = act_r.scalar_one_or_none()
                if act:
                    act_name = act.activity_name

    laborer_name = ""
    if woa_dict and woa_dict.get("assigned_to"):
        labor_model = get_entity_model("labor")
        if labor_model:
            lbr_result = await db.execute(select(labor_model).where(labor_model.id == woa_dict["assigned_to"]))
            lbr = lbr_result.scalar_one_or_none()
            if lbr:
                laborer_name = lbr.laborer or ""

    # Re-read MR after commit for fresh data
    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()

    task = _build_task_response(record_to_dict(mr), woa_dict, act_name, laborer_name)
    return {"status": "success", "data": task}


# ── RESCHEDULE (drag and drop) ────────────────────────────────────────────────

@router.patch("/pm-calendar/tasks/{task_id}/reschedule", name="pm_calendar_reschedule")
async def reschedule_task(
    task_id: str,
    payload: TaskReschedule,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule a task to a new date (drag and drop). Preserves time."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")

    if not mr_model:
        return {"status": "error", "message": "Model not found"}

    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()
    if not mr:
        return {"status": "error", "message": f"Task {task_id} not found"}

    new_date = date.fromisoformat(payload.due_date)
    mr.due_date = new_date

    # Update WOA start/end dates preserving time
    if mr.work_order_activity and woa_model:
        woa_result = await db.execute(select(woa_model).where(woa_model.id == mr.work_order_activity))
        woa = woa_result.scalar_one_or_none()
        if woa and woa.start_date:
            old_time = woa.start_date.time()
            new_start = datetime.combine(new_date, old_time)
            duration = (woa.end_date - woa.start_date) if woa.end_date else timedelta(minutes=30)
            woa.start_date = new_start
            woa.end_date = new_start + duration

    await db.commit()
    return {"status": "success", "data": {"id": task_id, "due_date": payload.due_date}}


# ── UPDATE STATUS ─────────────────────────────────────────────────────────────

@router.patch("/pm-calendar/tasks/{task_id}/status", name="pm_calendar_update_status")
async def update_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Update only the workflow_state of a task."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    if not mr_model:
        return {"status": "error", "message": "Model not found"}

    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()
    if not mr:
        return {"status": "error", "message": f"Task {task_id} not found"}

    mr.workflow_state = payload.workflow_state

    # If completed, set closed_date
    if payload.workflow_state == "Completed":
        mr.closed_date = date.today()
    else:
        mr.closed_date = None

    await db.commit()

    color = STATUS_COLORS.get(payload.workflow_state, "#94a3b8")
    return {
        "status": "success",
        "data": {
            "id": task_id,
            "workflow_state": payload.workflow_state,
            "color": color,
        },
    }


# ── DELETE TASK ───────────────────────────────────────────────────────────────

@router.delete("/pm-calendar/tasks/{task_id}", name="pm_calendar_delete_task")
async def delete_task(
    task_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete a PM calendar task. Removes WOA first, then MR."""
    user = await get_current_user_from_token(authorization, db)

    mr_model = get_entity_model("maintenance_request")
    woa_model = get_entity_model("work_order_activity")

    if not mr_model:
        return {"status": "error", "message": "Model not found"}

    result = await db.execute(select(mr_model).where(mr_model.id == task_id))
    mr = result.scalar_one_or_none()
    if not mr:
        return {"status": "error", "message": f"Task {task_id} not found"}

    # Delete WOA first
    if mr.work_order_activity and woa_model:
        woa_result = await db.execute(select(woa_model).where(woa_model.id == mr.work_order_activity))
        woa = woa_result.scalar_one_or_none()
        if woa:
            await db.delete(woa)

    # Delete MR
    await db.delete(mr)
    await db.commit()

    return {"status": "success", "data": {"id": task_id}}


# ── DROPDOWN: Activities ──────────────────────────────────────────────────────

@router.get("/pm-calendar/activities", name="pm_calendar_activities")
async def get_activities(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all maintenance_activities for dropdown."""
    user = await get_current_user_from_token(authorization, db)

    model = get_entity_model("maintenance_activity")
    if not model:
        return {"status": "success", "data": []}

    result = await db.execute(select(model).order_by(model.activity_name))
    activities = result.scalars().all()

    return {
        "status": "success",
        "data": [
            {"id": a.id, "activity_name": a.activity_name}
            for a in activities
        ],
    }


# ── DROPDOWN: Labor ───────────────────────────────────────────────────────────

@router.get("/pm-calendar/labor", name="pm_calendar_labor")
async def get_labor(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all labor records for assignee dropdown."""
    user = await get_current_user_from_token(authorization, db)

    model = get_entity_model("labor")
    if not model:
        return {"status": "success", "data": []}

    result = await db.execute(select(model).order_by(model.laborer))
    records = result.scalars().all()

    return {
        "status": "success",
        "data": [
            {"id": r.id, "laborer": r.laborer or r.id, "labor_type": r.labor_type}
            for r in records
        ],
    }


# ── RESOURCE VIEW: Work Order Activities ─────────────────────────────────────

@router.get("/pm-calendar/work-order-activities", name="pm_calendar_work_order_activities")
async def get_work_order_activities(
    year: int = Query(...),
    month: int = Query(...),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get work order activities for resource view (tasks with labor assignments)."""
    try:
        user = await get_current_user_from_token(authorization, db)

        woa_model = get_entity_model("work_order_activity")
        labor_model = get_entity_model("labor")
        wo_model = get_entity_model("work_order")
        
        if not woa_model or not labor_model or not wo_model:
            return {"status": "success", "data": []}

        # Get work order activities for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        result = await db.execute(
            select(woa_model, wo_model, labor_model)
            .join(wo_model, woa_model.work_order == wo_model.id)
            .outerjoin(labor_model, woa_model.assigned_to == labor_model.id)
            .where(
                and_(
                    woa_model.start_date >= start_date,
                    woa_model.start_date < end_date,
                    woa_model.assigned_to.isnot(None)
                )
            )
            .order_by(woa_model.start_date)
        )
        
        records = result.all()
        activities = []
        
        for row in records:
            woa = record_to_dict(row[0])
            wo = record_to_dict(row[1])
            labor = record_to_dict(row[2]) if row[2] else None

            # Extract date and time from start_date timestamp
            start_dt = woa.get("start_date")
            if start_dt:
                if hasattr(start_dt, "strftime"):
                    due_date_str = start_dt.strftime("%Y-%m-%d")
                    start_time_str = start_dt.strftime("%H:%M")
                else:
                    due_date_str = str(start_dt)[:10]
                    start_time_str = str(start_dt)[11:16]
            else:
                due_date_str = ""
                start_time_str = "08:00"

            activities.append({
                "id": woa["id"],
                "activity_name": woa.get("description") or wo.get("description", ""),
                "workflow_state": woa.get("workflow_state", "Draft"),
                "due_date": due_date_str,
                "start_time": start_time_str,
                "laborer": labor.get("laborer", "") if labor else "",
                "assigned_to": woa.get("assigned_to"),
                "work_order_id": wo.get("id"),
                "work_order_name": wo.get("description", ""),
                "site": woa.get("site") or wo.get("site"),
                "department": woa.get("department") or wo.get("department"),
                "color": STATUS_COLORS.get(woa.get("workflow_state", "Draft"), "#94a3b8"),
            })
        
        return {"status": "success", "data": activities}
    
    except Exception as e:
        # Return empty data if there's any error
        return {"status": "success", "data": []}


@router.get("/pm-calendar/work-order-activities/{activity_id}", name="pm_calendar_work_order_activity")
async def get_work_order_activity(
    activity_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a single work order activity by ID."""
    try:
        user = await get_current_user_from_token(authorization, db)

        woa_model = get_entity_model("work_order_activity")
        labor_model = get_entity_model("labor")
        wo_model = get_entity_model("work_order")
        
        if not woa_model or not labor_model or not wo_model:
            return {"status": "error", "message": "Models not found"}

        result = await db.execute(
            select(woa_model, wo_model, labor_model)
            .join(wo_model, woa_model.work_order == wo_model.id)
            .outerjoin(labor_model, woa_model.assigned_to == labor_model.id)
            .where(woa_model.id == activity_id)
        )
        
        row = result.first()
        if not row:
            return {"status": "error", "message": f"Work order activity {activity_id} not found"}

        woa = record_to_dict(row[0])
        wo = record_to_dict(row[1])
        labor = record_to_dict(row[2]) if row[2] else None

        # Extract date and time from start_date timestamp
        start_dt = woa.get("start_date")
        if start_dt:
            if hasattr(start_dt, "strftime"):
                due_date_str = start_dt.strftime("%Y-%m-%d")
                start_time_str = start_dt.strftime("%H:%M")
            else:
                due_date_str = str(start_dt)[:10]
                start_time_str = str(start_dt)[11:16]
        else:
            due_date_str = ""
            start_time_str = "08:00"

        activity = {
            "id": woa["id"],
            "activity_name": woa.get("description") or wo.get("description", ""),
            "workflow_state": woa.get("workflow_state", "Draft"),
            "due_date": due_date_str,
            "start_time": start_time_str,
            "laborer": labor.get("laborer", "") if labor else "",
            "assigned_to": woa.get("assigned_to"),
            "work_order_id": wo.get("id"),
            "work_order_name": wo.get("description", ""),
            "site": woa.get("site") or wo.get("site"),
            "department": woa.get("department") or wo.get("department"),
            "color": STATUS_COLORS.get(woa.get("workflow_state", "Draft"), "#94a3b8"),
        }
        
        return {"status": "success", "data": activity}
    
    except Exception as e:
        return {"status": "error", "message": f"Error fetching work order activity: {str(e)}"}


# ── TIME SLOTS ────────────────────────────────────────────────────────────────

@router.get("/pm-calendar/time-slots", name="pm_calendar_time_slots")
async def get_time_slots():
    """Return static list of 30-min time slots from 6:00 AM to 10:00 PM."""
    slots = []
    hour = 6
    minute = 0
    while hour < 22 or (hour == 22 and minute == 0):
        label = f"{hour:02d}:{minute:02d}"
        ampm_hour = hour % 12 or 12
        period = "AM" if hour < 12 else "PM"
        display = f"{ampm_hour}:{minute:02d} {period}"
        slots.append({"value": label, "label": display})
        minute += 30
        if minute >= 60:
            minute = 0
            hour += 1

    return {"status": "success", "data": slots}


# ── HOLIDAYS ──────────────────────────────────────────────────────────────────

@router.get("/pm-calendar/holidays", name="pm_calendar_holidays")
async def get_holidays(
    year: int = Query(...),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all holidays for a given year."""
    user = await get_current_user_from_token(authorization, db)

    model = get_entity_model("holiday")
    if not model:
        return {"status": "success", "data": []}

    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)

    result = await db.execute(
        select(model).where(
            and_(model.holiday_date >= first_day, model.holiday_date <= last_day)
        ).order_by(model.holiday_date)
    )
    holidays = result.scalars().all()

    return {
        "status": "success",
        "data": [
            {
                "id": h.id,
                "holiday_name": h.holiday_name,
                "holiday_date": h.holiday_date.isoformat() if h.holiday_date else None,
            }
            for h in holidays
        ],
    }


# ── SITES dropdown ────────────────────────────────────────────────────────────

@router.get("/pm-calendar/sites", name="pm_calendar_sites")
async def get_sites(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all sites for the filter dropdown."""
    user = await get_current_user_from_token(authorization, db)

    model = get_entity_model("site")
    if not model:
        return {"status": "success", "data": []}

    result = await db.execute(select(model).order_by(model.site_name))
    sites = result.scalars().all()

    return {
        "status": "success",
        "data": [
            {"id": s.id, "site_name": s.site_name or s.id}
            for s in sites
        ],
    }


# ── DEPARTMENTS dropdown ─────────────────────────────────────────────────────

@router.get("/pm-calendar/departments", name="pm_calendar_departments")
async def get_departments(
    site: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List departments, optionally filtered by site."""
    user = await get_current_user_from_token(authorization, db)

    model = get_entity_model("department")
    if not model:
        return {"status": "success", "data": []}

    query = select(model).order_by(model.department_name)
    if site:
        query = query.where(model.site == site)

    result = await db.execute(query)
    departments = result.scalars().all()

    return {
        "status": "success",
        "data": [
            {"id": d.id, "department_name": d.department_name or d.id}
            for d in departments
        ],
    }
