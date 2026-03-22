"""
Reports Registry
================
Central registry of all available reports.
Each report defines: title, description, icon, category, filters, data_fetcher, template.
"""
from pathlib import Path
from typing import Any
from datetime import datetime, date, time, timedelta
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.database import async_session_maker

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "reports"


def _get_jinja_env() -> Environment:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )


def _coerce_date(value: Any, fallback: date) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return fallback
    return fallback


def _build_datetime_range(
    filters: dict,
    default_days: int,
) -> tuple[date, date, datetime, datetime]:
    default_from_date = (datetime.now() - timedelta(days=default_days)).date()
    default_to_date = datetime.now().date()
    from_date = _coerce_date(filters.get("from_date"), default_from_date)
    to_date = _coerce_date(filters.get("to_date"), default_to_date)
    if to_date < from_date:
        from_date, to_date = to_date, from_date
    start_dt = datetime.combine(from_date, time.min)
    end_dt = datetime.combine(to_date + timedelta(days=1), time.min)
    return from_date, to_date, start_dt, end_dt


# ── Report Definitions ─────────────────────────────────────────────────────

REPORTS: dict[str, dict[str, Any]] = {
    "inventory_summary": {
        "title": "Inventory Summary",
        "description": "Overview of stock levels across all locations, highlighting low and out-of-stock items.",
        "icon": "i-lucide-package",
        "category": "Purchasing & Stores",
        "filters": [
            {
                "key": "min_threshold",
                "label": "Min Threshold",
                "type": "number",
                "default": 5,
                "description": "Items with stock at or below this level are flagged as low stock",
            },
            {
                "key": "site",
                "label": "Site",
                "type": "link",
                "link_entity": "site",
                "description": "Filter by site",
            },
            {
                "key": "location",
                "label": "Location",
                "type": "link",
                "link_entity": "location",
                "description": "Filter by location",
            },
        ],
        "template": "inventory_summary.html",
        "data_fetcher": "_fetch_inventory_summary",
    },
    "work_order_summary": {
        "title": "Work Order Summary",
        "description": "Summary of work orders by status, type, and department with activity breakdown.",
        "icon": "i-lucide-clipboard-list",
        "category": "Work Management",
        "filters": [
            {"key": "from_date", "label": "From Date", "type": "date", "description": "Start date"},
            {"key": "to_date", "label": "To Date", "type": "date", "description": "End date"},
            {"key": "site", "label": "Site", "type": "link", "link_entity": "site", "description": "Filter by site"},
            {"key": "department", "label": "Department", "type": "link", "link_entity": "department", "description": "Filter by department"},
        ],
        "template": "work_order_summary.html",
        "data_fetcher": "_fetch_work_order_summary",
    },
    "pr_summary": {
        "title": "Purchase Request Summary",
        "description": "Summary of purchase requests by status, department, and requestor.",
        "icon": "i-lucide-file-text",
        "category": "Purchasing & Stores",
        "filters": [
            {"key": "from_date", "label": "From Date", "type": "date", "description": "Start date"},
            {"key": "to_date", "label": "To Date", "type": "date", "description": "End date"},
            {"key": "site", "label": "Site", "type": "link", "link_entity": "site", "description": "Filter by site"},
        ],
        "template": "pr_summary.html",
        "data_fetcher": "_fetch_pr_summary",
    },
    "incident_summary": {
        "title": "Safety & Incident Summary",
        "description": "Summary of safety incidents by type, severity, and site.",
        "icon": "i-lucide-alert-triangle",
        "category": "Asset Management",
        "filters": [
            {"key": "from_date", "label": "From Date", "type": "date", "description": "Start date"},
            {"key": "to_date", "label": "To Date", "type": "date", "description": "End date"},
            {"key": "site", "label": "Site", "type": "link", "link_entity": "site", "description": "Filter by site"},
            {"key": "severity", "label": "Severity", "type": "text", "description": "e.g. Low, Medium, High, Critical"},
        ],
        "template": "incident_summary.html",
        "data_fetcher": "_fetch_incident_summary",
    },
    "budget_vs_actual": {
        "title": "Budget vs Actual",
        "description": "Compare budgeted amounts against actual costs by cost code for a fiscal year.",
        "icon": "i-lucide-bar-chart-3",
        "category": "Cost Management",
        "filters": [
            {"key": "fiscal_year", "label": "Fiscal Year", "type": "number", "default": datetime.now().year, "description": "Fiscal year"},
        ],
        "template": "budget_vs_actual.html",
        "data_fetcher": "_fetch_budget_vs_actual",
    },
    "maintenance_pms": {
        "title": "Preventive Maintenance Schedule",
        "description": "Overview of preventive maintenance requests and completion rates.",
        "icon": "i-lucide-calendar-check",
        "category": "Maintenance",
        "filters": [
            {"key": "from_date", "label": "From Date", "type": "date", "description": "Start date"},
            {"key": "to_date", "label": "To Date", "type": "date", "description": "End date"},
            {"key": "site", "label": "Site", "type": "link", "link_entity": "site", "description": "Filter by site"},
        ],
        "template": "maintenance_pms.html",
        "data_fetcher": "_fetch_maintenance_pms",
    },
    "stock_movement": {
        "title": "Stock Movement",
        "description": "Track stock issues, returns, and adjustments over a period.",
        "icon": "i-lucide-arrow-left-right",
        "category": "Purchasing & Stores",
        "filters": [
            {"key": "from_date", "label": "From Date", "type": "date", "description": "Start date"},
            {"key": "to_date", "label": "To Date", "type": "date", "description": "End date"},
            {"key": "site", "label": "Site", "type": "link", "link_entity": "site", "description": "Filter by site"},
        ],
        "template": "stock_movement.html",
        "data_fetcher": "_fetch_stock_movement",
    },
}


# ── Data Fetchers ───────────────────────────────────────────────────────────

async def _fetch_inventory_summary(filters: dict) -> dict:
    """Fetch inventory summary data from the database."""
    from sqlalchemy import text

    min_threshold = int(filters.get("min_threshold", 5))
    site_filter = filters.get("site")
    location_filter = filters.get("location")

    # Build query
    where_clauses = []
    params: dict[str, Any] = {}

    if site_filter:
        where_clauses.append("inv.site = :site")
        params["site"] = site_filter
    if location_filter:
        where_clauses.append("inv.location = :location")
        params["location"] = location_filter

    where_sql = (" AND " + " AND ".join(where_clauses)) if where_clauses else ""

    query = text(f"""
        SELECT
            inv.id,
            inv.item,
            i.item_name AS item_display,
            inv.serial_number,
            inv.site,
            s.site_name AS site_name,
            inv.location,
            l.name AS location_name,
            inv.store_location AS store_name,
            inv.bin_location AS bin,
            inv.zone AS zone_name,
            inv.actual_inv,
            inv.available_inv
        FROM inventory inv
        LEFT JOIN item i ON i.id = inv.item
        LEFT JOIN site s ON s.id = inv.site
        LEFT JOIN location l ON l.id = inv.location
        WHERE 1=1 {where_sql}
        ORDER BY l.name, s.site_name, inv.bin_location, i.item_name
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, params)
        rows = [dict(r._mapping) for r in result]

    # Build summary
    total_items = len(rows)
    out_of_stock = sum(1 for r in rows if (r.get("actual_inv") or 0) == 0)
    low_stock = sum(1 for r in rows if 0 < (r.get("actual_inv") or 0) <= min_threshold)
    adequate_stock = total_items - out_of_stock - low_stock

    summary = {
        "total_items": total_items,
        "out_of_stock_items": out_of_stock,
        "low_stock_items": low_stock,
        "adequate_stock_items": adequate_stock,
    }

    # Group by location + site
    site_groups: list[dict] = []
    current_key = None
    current_group: dict | None = None

    for row in rows:
        key = (row.get("location_name", ""), row.get("site_name", ""))
        if key != current_key:
            if current_group:
                site_groups.append(current_group)
            current_group = {
                "location": row.get("location_name", "N/A"),
                "site": row.get("site_name", "N/A"),
                "bin_groups": [],
            }
            current_key = key

        # Group by bin within location+site
        bin_val = row.get("bin", "")
        if current_group:
            existing_bin = next(
                (bg for bg in current_group["bin_groups"] if bg["bin"] == bin_val),
                None,
            )
            if existing_bin:
                existing_bin["rows"].append(row)
            else:
                current_group["bin_groups"].append({"bin": bin_val, "rows": [row]})

    if current_group:
        site_groups.append(current_group)

    # Active filters for display
    active_filters = []
    if site_filter:
        active_filters.append({"label": "Site", "value": site_filter})
    if location_filter:
        active_filters.append({"label": "Location", "value": location_filter})

    return {
        "summary": summary,
        "site_groups": site_groups,
        "min_threshold": min_threshold,
        "active_filters": active_filters,
        "records": rows,
    }


async def _fetch_work_order_summary(filters: dict) -> dict:
    """Fetch work order summary data."""
    from sqlalchemy import text
    from_date, to_date, start_dt, end_dt = _build_datetime_range(filters, 30)

    activity_where_clauses = [
        """
        (
            (woa.start_date IS NOT NULL AND woa.end_date IS NOT NULL AND woa.start_date < :end_dt AND woa.end_date >= :start_dt)
            OR
            (woa.start_date IS NOT NULL AND woa.end_date IS NULL AND woa.start_date >= :start_dt AND woa.start_date < :end_dt)
            OR
            (woa.start_date IS NULL AND woa.end_date IS NOT NULL AND woa.end_date >= :start_dt AND woa.end_date < :end_dt)
        )
        """
    ]
    params: dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}

    if filters.get("site"):
        activity_where_clauses.append("wo.site = :site")
        params["site"] = filters["site"]
    if filters.get("department"):
        activity_where_clauses.append("wo.department = :department")
        params["department"] = filters["department"]

    activity_where_sql = " AND ".join(activity_where_clauses)

    async with async_session_maker() as db:
        activities_by_work_order: dict[str, list[dict[str, Any]]] = {}
        work_order_ids: list[str] = []

        activity_query = text(f"""
                SELECT
                    woa.id,
                    woa.work_order,
                    woa.description,
                    woa.workflow_state,
                    woa.work_item_type,
                    woa.work_item,
                    woa.asset_name,
                    woa.activity_type,
                    woa.activity_type_name,
                    woa.assigned_to,
                    woa.start_date,
                    woa.end_date
                FROM work_order_activity woa
                INNER JOIN work_order wo ON wo.id = woa.work_order
                WHERE {activity_where_sql}
                ORDER BY woa.work_order ASC, woa.created_at ASC, woa.id ASC
            """)
        activity_result = await db.execute(activity_query, params)
        matching_activities = [dict(r._mapping) for r in activity_result]

        for activity in matching_activities:
            work_order_id = activity.get("work_order")
            if not work_order_id:
                continue
            activities_by_work_order.setdefault(work_order_id, []).append(activity)
            if work_order_id not in work_order_ids:
                work_order_ids.append(work_order_id)

        rows: list[dict[str, Any]] = []
        if work_order_ids:
            work_order_query = text("""
                SELECT
                    wo.id, wo.work_order_type, wo.description, wo.due_date,
                    wo.site, s.site_name, wo.department, d.department_name,
                    wo.workflow_state, wo.priority, wo.created_at
                FROM work_order wo
                LEFT JOIN site s ON s.id = wo.site
                LEFT JOIN department d ON d.id = wo.department
                WHERE wo.id = ANY(:work_order_ids)
                ORDER BY wo.created_at DESC
            """)
            result = await db.execute(work_order_query, {"work_order_ids": work_order_ids})
            rows = [dict(r._mapping) for r in result]

    # Summary counts
    summary = {
        "total": len(rows),
        "by_status": {},
        "by_priority": {},
        "by_department": {},
    }

    for r in rows:
        state = r.get("workflow_state") or "Draft"
        summary["by_status"][state] = summary["by_status"].get(state, 0) + 1
        priority = r.get("priority") or "Unspecified"
        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
        dept = r.get("department_name") or r.get("department") or "Unassigned"
        summary["by_department"][dept] = summary["by_department"].get(dept, 0) + 1
        r["activities"] = activities_by_work_order.get(r["id"], [])

    normalized_filters = dict(filters)
    normalized_filters["from_date"] = from_date.isoformat()
    normalized_filters["to_date"] = to_date.isoformat()
    return {"summary": summary, "work_orders": rows, "filters": normalized_filters}


async def _fetch_pr_summary(filters: dict) -> dict:
    """Fetch purchase request summary data."""
    from sqlalchemy import text
    from_date, to_date, _, _ = _build_datetime_range(filters, 30)

    where_clauses = ["pr.date_requested >= :from_date", "pr.date_requested <= :to_date"]
    params: dict[str, Any] = {"from_date": from_date, "to_date": to_date}

    if filters.get("site"):
        where_clauses.append("pr.site = :site")
        params["site"] = filters["site"]

    where_sql = " AND ".join(where_clauses)

    query = text(f"""
        SELECT pr.id, pr.date_requested, pr.requestor, pr.requestor_name,
               pr.site, s.site_name, pr.department, d.department_name,
               pr.workflow_state, pr.pr_description
        FROM purchase_request pr
        LEFT JOIN site s ON s.id = pr.site
        LEFT JOIN department d ON d.id = pr.department
        WHERE {where_sql}
        ORDER BY pr.date_requested DESC
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, params)
        rows = [dict(r._mapping) for r in result]

    summary = {
        "total": len(rows),
        "by_status": {},
        "by_department": {},
    }
    for r in rows:
        state = r.get("workflow_state") or "Draft"
        summary["by_status"][state] = summary["by_status"].get(state, 0) + 1
        dept = r.get("department_name") or r.get("department") or "Unassigned"
        summary["by_department"][dept] = summary["by_department"].get(dept, 0) + 1

    normalized_filters = dict(filters)
    normalized_filters["from_date"] = from_date.isoformat()
    normalized_filters["to_date"] = to_date.isoformat()
    return {"summary": summary, "purchase_requests": rows, "filters": normalized_filters}


async def _fetch_incident_summary(filters: dict) -> dict:
    """Fetch incident summary data."""
    from sqlalchemy import text
    from_date, to_date, start_dt, end_dt = _build_datetime_range(filters, 90)

    where_clauses = ["inc.incident_datetime >= :start_dt", "inc.incident_datetime < :end_dt"]
    params: dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}

    if filters.get("site"):
        where_clauses.append("inc.site = :site")
        params["site"] = filters["site"]
    if filters.get("severity"):
        where_clauses.append("inc.severity = :severity")
        params["severity"] = filters["severity"]

    where_sql = " AND ".join(where_clauses)

    query = text(f"""
        SELECT inc.id, inc.title, inc.incident_type, inc.incident_datetime,
               inc.severity, inc.site, s.site_name,
               inc.department, d.department_name,
               inc.closed_date
        FROM incident inc
        LEFT JOIN site s ON s.id = inc.site
        LEFT JOIN department d ON d.id = inc.department
        WHERE {where_sql}
        ORDER BY inc.incident_datetime DESC
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, params)
        rows = [dict(r._mapping) for r in result]

    open_count = sum(1 for r in rows if not r.get("closed_date"))
    closed_count = sum(1 for r in rows if r.get("closed_date"))

    summary = {
        "total": len(rows),
        "open": open_count,
        "closed": closed_count,
        "by_severity": {},
        "by_type": {},
    }
    for r in rows:
        sev = r.get("severity") or "Unspecified"
        summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
        itype = r.get("incident_type") or "Other"
        summary["by_type"][itype] = summary["by_type"].get(itype, 0) + 1

    normalized_filters = dict(filters)
    normalized_filters["from_date"] = from_date.isoformat()
    normalized_filters["to_date"] = to_date.isoformat()
    return {"summary": summary, "incidents": rows, "filters": normalized_filters}


async def _fetch_budget_vs_actual(filters: dict) -> dict:
    """Fetch budget vs actual data."""
    from sqlalchemy import text

    fiscal_year = int(filters.get("fiscal_year", datetime.now().year))

    query = text("""
        SELECT ab.id, ab.cost_code, cc.code AS cost_code_name,
               cc.description AS cost_code_description,
               ab.year, ab.budgetary_amount
        FROM annual_budget ab
        LEFT JOIN cost_code cc ON cc.id = ab.cost_code
        WHERE ab.year = :fiscal_year
        ORDER BY cc.code
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, {"fiscal_year": fiscal_year})
        budgets = [dict(r._mapping) for r in result]

    total_budget = sum(float(b.get("budgetary_amount") or 0) for b in budgets)

    budget_items = []
    for b in budgets:
        budgeted = float(b.get("budgetary_amount") or 0)
        budget_items.append({
            "cost_code": b.get("cost_code_name") or b.get("cost_code") or "",
            "description": b.get("cost_code_description") or "",
            "budgeted": budgeted,
            "actual": 0,
            "variance": budgeted,
            "variance_pct": 100.0,
        })

    summary = {
        "fiscal_year": fiscal_year,
        "total_budget": total_budget,
        "total_actual": 0,
        "variance": total_budget,
        "budget_count": len(budgets),
    }

    return {"summary": summary, "budget_items": budget_items, "filters": filters}


async def _fetch_maintenance_pms(filters: dict) -> dict:
    """Fetch preventive maintenance schedule data."""
    from sqlalchemy import text
    from_date, to_date, start_dt, end_dt = _build_datetime_range(filters, 90)

    where_clauses = ["mr.created_at >= :start_dt", "mr.created_at < :end_dt"]
    params: dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}

    if filters.get("site"):
        where_clauses.append("mr.site = :site")
        params["site"] = filters["site"]

    where_sql = " AND ".join(where_clauses)

    query = text(f"""
        SELECT mr.id, mr.description, mr.site, s.site_name,
               mr.workflow_state, mr.created_at
        FROM maintenance_request mr
        LEFT JOIN site s ON s.id = mr.site
        WHERE {where_sql}
        ORDER BY mr.created_at DESC
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, params)
        rows = [dict(r._mapping) for r in result]

    completed = sum(1 for r in rows if (r.get("workflow_state") or "").lower() in ("completed", "closed"))
    pending = len(rows) - completed

    summary = {
        "total": len(rows),
        "completed": completed,
        "pending": pending,
        "completion_rate": round((completed / len(rows) * 100), 1) if rows else 0,
        "by_status": {},
    }
    for r in rows:
        state = r.get("workflow_state") or "Draft"
        summary["by_status"][state] = summary["by_status"].get(state, 0) + 1

    normalized_filters = dict(filters)
    normalized_filters["from_date"] = from_date.isoformat()
    normalized_filters["to_date"] = to_date.isoformat()
    return {"summary": summary, "requests": rows, "filters": normalized_filters}


async def _fetch_stock_movement(filters: dict) -> dict:
    """Fetch stock movement data (issues and returns)."""
    from sqlalchemy import text
    from_date, to_date, start_dt, end_dt = _build_datetime_range(filters, 30)

    params: dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}

    site_clause = ""
    if filters.get("site"):
        site_clause = "AND sle.site = :site"
        params["site"] = filters["site"]

    query = text(f"""
        SELECT sle.id, sle.item, i.item_name,
               sle.transaction_type, sle.quantity, sle.site,
               s.site_name, sle.created_at
        FROM stock_ledger_entry sle
        LEFT JOIN item i ON i.id = sle.item
        LEFT JOIN site s ON s.id = sle.site
        WHERE sle.created_at >= :start_dt AND sle.created_at < :end_dt {site_clause}
        ORDER BY sle.created_at DESC
    """)

    async with async_session_maker() as db:
        result = await db.execute(query, params)
        rows = [dict(r._mapping) for r in result]

    total_issued = sum(abs(float(r.get("quantity") or 0)) for r in rows if (r.get("transaction_type") or "").lower() in ("issue", "item_issue"))
    total_returned = sum(abs(float(r.get("quantity") or 0)) for r in rows if (r.get("transaction_type") or "").lower() in ("return", "item_return"))
    total_adjusted = sum(abs(float(r.get("quantity") or 0)) for r in rows if (r.get("transaction_type") or "").lower() in ("adjustment",))

    summary = {
        "total_movements": len(rows),
        "total_issued": total_issued,
        "total_returned": total_returned,
        "total_adjusted": total_adjusted,
        "by_type": {},
    }
    for r in rows:
        ttype = r.get("transaction_type") or "Other"
        summary["by_type"][ttype] = summary["by_type"].get(ttype, 0) + 1

    normalized_filters = dict(filters)
    normalized_filters["from_date"] = from_date.isoformat()
    normalized_filters["to_date"] = to_date.isoformat()
    return {"summary": summary, "movements": rows, "filters": normalized_filters}


# ── Registry Helpers ────────────────────────────────────────────────────────

_FETCHERS = {
    "_fetch_inventory_summary": _fetch_inventory_summary,
    "_fetch_work_order_summary": _fetch_work_order_summary,
    "_fetch_pr_summary": _fetch_pr_summary,
    "_fetch_incident_summary": _fetch_incident_summary,
    "_fetch_budget_vs_actual": _fetch_budget_vs_actual,
    "_fetch_maintenance_pms": _fetch_maintenance_pms,
    "_fetch_stock_movement": _fetch_stock_movement,
}


async def get_report_data(report_key: str, filters: dict) -> dict:
    """Invoke the data fetcher for a report."""
    cfg = REPORTS.get(report_key)
    if not cfg:
        raise ValueError(f"Report '{report_key}' not found")
    fetcher_name = cfg["data_fetcher"]
    fetcher = _FETCHERS.get(fetcher_name)
    if not fetcher:
        raise ValueError(f"Data fetcher '{fetcher_name}' not found for report '{report_key}'")
    return await fetcher(filters)


def render_report_html(report_key: str, data: dict, filters: dict) -> str:
    """Render report data to HTML using the report's Jinja template."""
    cfg = REPORTS.get(report_key)
    if not cfg:
        raise ValueError(f"Report '{report_key}' not found")

    env = _get_jinja_env()
    template = env.get_template(cfg["template"])

    context = {
        **data,
        "report_title": cfg["title"],
        "report_description": cfg["description"],
        "filters": filters,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return template.render(**context)
