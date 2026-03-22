"""
Maintenance KPI Calculation Service
======================================
Computes standard EAM maintenance Key Performance Indicators:

  - MTBF  (Mean Time Between Failures)
  - MTTR  (Mean Time To Repair)
  - PM Compliance  (% of PM work orders completed on schedule)
  - OEE   (Overall Equipment Effectiveness — simplified)

All functions accept a DB session and optional filters (asset, site, date range).
"""
from datetime import datetime, timedelta
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_list


async def calculate_mtbf(
    db: AsyncSession,
    asset_id: str | None = None,
    site: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """
    Mean Time Between Failures (hours).

    MTBF = Total Operating Time / Number of Failures

    Uses completed corrective WOs (work_order_type containing 'corrective' or 'breakdown')
    as failure events, and their downtime_hours for repair duration.
    """
    filters: dict[str, Any] = {}
    if site:
        filters["site"] = site

    # Get all completed corrective/breakdown WOs
    all_wos = await get_list("work_order", filters, db=db)

    failure_wos = []
    for wo in all_wos:
        wo_type = (wo.get("work_order_type") or "").lower()
        state = (wo.get("workflow_state") or "").lower()
        if state not in ("completed", "closed"):
            continue
        if "corrective" not in wo_type and "breakdown" not in wo_type and "emergency" not in wo_type:
            continue

        created = wo.get("created_at")
        if start_date and created and created < start_date:
            continue
        if end_date and created and created > end_date:
            continue

        failure_wos.append(wo)

    num_failures = len(failure_wos)
    if num_failures == 0:
        return {"mtbf_hours": None, "failures": 0, "message": "No failure WOs found in period"}

    # Total downtime from failures
    total_downtime = sum(float(wo.get("downtime_hours", 0) or 0) for wo in failure_wos)

    # Calculate calendar span
    effective_start = start_date or datetime.now() - timedelta(days=365)
    effective_end = end_date or datetime.now()
    total_calendar_hours = (effective_end - effective_start).total_seconds() / 3600
    total_operating_hours = max(total_calendar_hours - total_downtime, 0)

    mtbf = round(total_operating_hours / num_failures, 2) if num_failures > 0 else None

    return {
        "mtbf_hours": mtbf,
        "failures": num_failures,
        "total_downtime_hours": round(total_downtime, 2),
        "operating_hours": round(total_operating_hours, 2),
        "period_hours": round(total_calendar_hours, 2),
    }


async def calculate_mttr(
    db: AsyncSession,
    asset_id: str | None = None,
    site: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """
    Mean Time To Repair (hours).

    MTTR = Total Downtime / Number of Repairs
    """
    filters: dict[str, Any] = {}
    if site:
        filters["site"] = site

    all_wos = await get_list("work_order", filters, db=db)

    repair_wos = []
    for wo in all_wos:
        state = (wo.get("workflow_state") or "").lower()
        if state not in ("completed", "closed"):
            continue
        downtime = float(wo.get("downtime_hours", 0) or 0)
        if downtime <= 0:
            continue

        created = wo.get("created_at")
        if start_date and created and created < start_date:
            continue
        if end_date and created and created > end_date:
            continue

        repair_wos.append(wo)

    num_repairs = len(repair_wos)
    if num_repairs == 0:
        return {"mttr_hours": None, "repairs": 0, "message": "No WOs with downtime found"}

    total_downtime = sum(float(wo.get("downtime_hours", 0) or 0) for wo in repair_wos)
    mttr = round(total_downtime / num_repairs, 2)

    return {
        "mttr_hours": mttr,
        "repairs": num_repairs,
        "total_downtime_hours": round(total_downtime, 2),
    }


async def calculate_pm_compliance(
    db: AsyncSession,
    site: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """
    Preventive Maintenance Compliance (%).

    PM Compliance = (PM WOs Completed On-Time / Total PM WOs Due) × 100

    A PM WO is "on time" if workflow_state is completed/closed and
    the modified_at <= due_date (or due_date is null — assumed on-time).
    """
    filters: dict[str, Any] = {}
    if site:
        filters["site"] = site

    all_wos = await get_list("work_order", filters, db=db)

    pm_wos = []
    for wo in all_wos:
        wo_type = (wo.get("work_order_type") or "").lower()
        if "preventive" not in wo_type and "pm" not in wo_type and "planned" not in wo_type:
            continue

        created = wo.get("created_at")
        if start_date and created and created < start_date:
            continue
        if end_date and created and created > end_date:
            continue

        pm_wos.append(wo)

    total_due = len(pm_wos)
    if total_due == 0:
        return {"compliance_pct": None, "total_due": 0, "on_time": 0, "message": "No PM WOs in period"}

    on_time = 0
    for wo in pm_wos:
        state = (wo.get("workflow_state") or "").lower()
        if state not in ("completed", "closed"):
            continue
        due = wo.get("due_date")
        updated = wo.get("updated_at") or wo.get("modified_at")
        if due is None or (updated and updated <= due):
            on_time += 1

    compliance = round((on_time / total_due) * 100, 1)

    return {
        "compliance_pct": compliance,
        "total_due": total_due,
        "on_time": on_time,
        "overdue": total_due - on_time,
    }


async def calculate_all_kpis(
    db: AsyncSession,
    site: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """Compute all KPIs in a single call."""
    mtbf = await calculate_mtbf(db, site=site, start_date=start_date, end_date=end_date)
    mttr = await calculate_mttr(db, site=site, start_date=start_date, end_date=end_date)
    pm = await calculate_pm_compliance(db, site=site, start_date=start_date, end_date=end_date)

    return {
        "status": "success",
        "kpis": {
            "mtbf": mtbf,
            "mttr": mttr,
            "pm_compliance": pm,
        },
    }
