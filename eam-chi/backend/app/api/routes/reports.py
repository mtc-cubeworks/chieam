"""
Reports Router
==============
Serves report definitions, generates HTML previews, and produces PDF downloads.
Each report is a self-contained module that provides:
  - metadata (title, description, filters)
  - data fetcher (async, returns dict for Jinja context)
  - Jinja2 template (HTML)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import Optional
from datetime import date, datetime
from io import BytesIO

from app.core.security import get_current_user_from_token, CurrentUser
from app.services.print_service import html_to_pdf
from app.api.routes.reports_registry import REPORTS, get_report_data, render_report_html

router = APIRouter(tags=["reports"])


@router.get("/reports")
async def list_reports(
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """List all available reports with metadata."""
    reports = []
    for key, cfg in REPORTS.items():
        reports.append({
            "key": key,
            "title": cfg["title"],
            "description": cfg["description"],
            "icon": cfg.get("icon", "i-lucide-file-text"),
            "category": cfg.get("category", "General"),
            "filters": cfg.get("filters", []),
        })
    return {"status": "success", "data": reports}


@router.get("/reports/{report_key}")
async def get_report(
    report_key: str,
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """Get report metadata including available filters."""
    cfg = REPORTS.get(report_key)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Report '{report_key}' not found")
    return {
        "status": "success",
        "data": {
            "key": report_key,
            "title": cfg["title"],
            "description": cfg["description"],
            "icon": cfg.get("icon", "i-lucide-file-text"),
            "category": cfg.get("category", "General"),
            "filters": cfg.get("filters", []),
        },
    }


@router.post("/reports/{report_key}/generate")
async def generate_report(
    report_key: str,
    filters: dict = None,
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """Generate report data and return HTML preview."""
    cfg = REPORTS.get(report_key)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Report '{report_key}' not found")

    filters = filters or {}
    try:
        data = await get_report_data(report_key, filters)
        html = render_report_html(report_key, data, filters)
        return {
            "status": "success",
            "data": {
                "html": html,
                "title": cfg["title"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/{report_key}/pdf")
async def generate_report_pdf(
    report_key: str,
    filters: dict = None,
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """Generate report as PDF and return as downloadable file."""
    cfg = REPORTS.get(report_key)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Report '{report_key}' not found")

    filters = filters or {}
    try:
        data = await get_report_data(report_key, filters)
        html = render_report_html(report_key, data, filters)
        pdf_bytes = await html_to_pdf(html)

        filename = f"{report_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
