"""
Dashboard Router
================
Provides aggregated dashboard data from the EAM database.
Returns summary counts and breakdowns for the main dashboard page.
"""
from fastapi import APIRouter, Depends
from typing import Any
from datetime import datetime, date, time, timedelta

from app.core.database import async_session_maker
from app.core.security import get_current_user_from_token, CurrentUser

router = APIRouter(tags=["dashboard"])


def _date_range(days: int = 30):
    end = datetime.now()
    start = end - timedelta(days=days)
    return datetime.combine(start.date(), time.min), datetime.combine(end.date() + timedelta(days=1), time.min)


@router.get("/dashboard")
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """Return aggregated dashboard data."""
    from sqlalchemy import text

    start_30, end_now = _date_range(30)

    async with async_session_maker() as db:
        # -- Work Orders --
        wo_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Open') AS open,"
            " COUNT(*) FILTER (WHERE workflow_state = 'In Progress') AS in_progress,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Completed') AS completed,"
            " COUNT(*) FILTER (WHERE workflow_state NOT IN ('Open','In Progress','Completed','Closed','Cancelled')) AS other,"
            " COUNT(*) FILTER (WHERE priority = 'High' AND workflow_state NOT IN ('Completed','Closed','Cancelled')) AS high_priority_active"
            " FROM work_order"
        ))
        wo = dict(wo_result.mappings().first() or {})

        wo_recent = await db.execute(text(
            "SELECT COUNT(*) AS created_30d FROM work_order WHERE created_at >= :start AND created_at < :enddt"
        ), {"start": start_30, "enddt": end_now})
        wo["created_30d"] = (wo_recent.mappings().first() or {}).get("created_30d", 0)

        wo_type_result = await db.execute(text(
            "SELECT COALESCE(work_order_type, 'Unspecified') AS label, COUNT(*) AS count"
            " FROM work_order GROUP BY work_order_type ORDER BY count DESC LIMIT 10"
        ))
        wo_by_type = [dict(r) for r in wo_type_result.mappings()]

        wo_status_result = await db.execute(text(
            "SELECT COALESCE(workflow_state, 'Draft') AS label, COUNT(*) AS count"
            " FROM work_order GROUP BY workflow_state ORDER BY count DESC"
        ))
        wo_by_status = [dict(r) for r in wo_status_result.mappings()]

        # -- Assets --
        asset_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Active') AS active,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Inactive') AS inactive,"
            " COUNT(*) FILTER (WHERE workflow_state NOT IN ('Active','Inactive')) AS other"
            " FROM asset"
        ))
        assets = dict(asset_result.mappings().first() or {})

        asset_class_result = await db.execute(text(
            "SELECT COALESCE(ac.name, 'Unclassified') AS label, COUNT(*) AS count"
            " FROM asset a LEFT JOIN asset_class ac ON ac.id = a.asset_class"
            " GROUP BY ac.name ORDER BY count DESC LIMIT 10"
        ))
        assets_by_class = [dict(r) for r in asset_class_result.mappings()]

        # -- Inventory --
        inv_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total_lines,"
            " COUNT(*) FILTER (WHERE actual_inv <= 0) AS out_of_stock,"
            " COUNT(*) FILTER (WHERE actual_inv > 0 AND actual_inv <= 5) AS low_stock,"
            " COUNT(*) FILTER (WHERE actual_inv > 5) AS adequate"
            " FROM inventory"
        ))
        inventory = dict(inv_result.mappings().first() or {})

        # -- Purchase Requests --
        pr_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Draft') AS draft,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Submitted') AS submitted,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Approved') AS approved,"
            " COUNT(*) FILTER (WHERE workflow_state = 'Rejected') AS rejected"
            " FROM purchase_request"
        ))
        purchase_requests = dict(pr_result.mappings().first() or {})

        pr_recent = await db.execute(text(
            "SELECT COUNT(*) AS created_30d FROM purchase_request WHERE created_at >= :start AND created_at < :enddt"
        ), {"start": start_30, "enddt": end_now})
        purchase_requests["created_30d"] = (pr_recent.mappings().first() or {}).get("created_30d", 0)

        # -- Maintenance Requests --
        mr_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total,"
            " COUNT(*) FILTER (WHERE workflow_state IN ('Completed','Closed')) AS completed,"
            " COUNT(*) FILTER (WHERE workflow_state NOT IN ('Completed','Closed','Cancelled')) AS pending"
            " FROM maintenance_request"
        ))
        maintenance = dict(mr_result.mappings().first() or {})
        maintenance["completion_rate"] = round(
            (int(maintenance.get("completed", 0)) / max(int(maintenance.get("total", 0)), 1)) * 100, 1
        )

        # -- Incidents --
        inc_result = await db.execute(text(
            "SELECT"
            " COUNT(*) AS total,"
            " COUNT(*) FILTER (WHERE closed_date IS NULL) AS open,"
            " COUNT(*) FILTER (WHERE closed_date IS NOT NULL) AS closed"
            " FROM incident"
        ))
        incidents = dict(inc_result.mappings().first() or {})

        inc_sev_result = await db.execute(text(
            "SELECT COALESCE(severity, 'Unspecified') AS label, COUNT(*) AS count"
            " FROM incident GROUP BY severity ORDER BY count DESC"
        ))
        incidents_by_severity = [dict(r) for r in inc_sev_result.mappings()]

        # -- Overdue Work Orders --
        overdue_result = await db.execute(text(
            "SELECT COUNT(*) AS count FROM work_order"
            " WHERE due_date < CURRENT_DATE"
            " AND workflow_state NOT IN ('Completed','Closed','Cancelled')"
        ))
        overdue_wo = (overdue_result.mappings().first() or {}).get("count", 0)

        # -- Recent Work Order Activities (last 30 days) --
        recent_activity_result = await db.execute(text(
            "SELECT COUNT(*) AS total_activities, COUNT(DISTINCT work_order) AS work_orders_touched"
            " FROM work_order_activity WHERE created_at >= :start AND created_at < :enddt"
        ), {"start": start_30, "enddt": end_now})
        recent_activity = dict(recent_activity_result.mappings().first() or {})

        # -- Stock Movements last 30 days --
        sle_result = await db.execute(text(
            "SELECT COUNT(*) AS total_movements,"
            " COALESCE(SUM(qty_out), 0) AS total_issued,"
            " COALESCE(SUM(qty_in), 0) AS total_received"
            " FROM stock_ledger_entry"
            " WHERE created_at >= :start AND created_at < :enddt"
        ), {"start": start_30, "enddt": end_now})
        stock_movements = dict(sle_result.mappings().first() or {})

        # -- Budget summary (current year) --
        current_year = datetime.now().year
        budget_result = await db.execute(text(
            "SELECT COUNT(*) AS budget_lines, COALESCE(SUM(budgetary_amount), 0) AS total_budget"
            " FROM annual_budget WHERE year = :yr"
        ), {"yr": current_year})
        budget = dict(budget_result.mappings().first() or {})
        budget["fiscal_year"] = current_year

    return {
        "status": "success",
        "data": {
            "work_orders": wo,
            "work_orders_by_type": wo_by_type,
            "work_orders_by_status": wo_by_status,
            "assets": assets,
            "assets_by_class": assets_by_class,
            "inventory": inventory,
            "purchase_requests": purchase_requests,
            "maintenance": maintenance,
            "incidents": incidents,
            "incidents_by_severity": incidents_by_severity,
            "overdue_work_orders": overdue_wo,
            "recent_activity": recent_activity,
            "stock_movements": stock_movements,
            "budget": budget,
        },
    }
