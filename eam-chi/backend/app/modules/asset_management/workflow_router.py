"""
Asset Management Module - Central Workflow Router
===================================================
Single entry point for all workflow logic in the Asset Management module.

Each handler follows the signature:
    async def handler(doc, action, db, user) -> dict

Returns:
    {"status": "success"|"error", "message": str, ...}
"""
from typing import Any, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession


WorkflowHandler = Callable[[Any, str, AsyncSession, Any], Awaitable[dict]]
_WORKFLOW_HANDLERS: dict[str, WorkflowHandler] = {}


def register_workflow(entity: str):
    """Decorator to register a workflow handler for an entity."""
    def decorator(func: WorkflowHandler) -> WorkflowHandler:
        _WORKFLOW_HANDLERS[entity] = func
        return func
    return decorator


async def route_workflow(entity: str, doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """Central workflow router for the Asset Management module."""
    handler = _WORKFLOW_HANDLERS.get(entity)
    if handler:
        return await handler(doc, action, db, user)
    return {"status": "success", "message": f"No workflow handler for '{entity}'"}


# =============================================================================
# Helpers
# =============================================================================

def _get_id(doc: Any) -> str | None:
    return doc.id if hasattr(doc, 'id') else doc.get('id') if isinstance(doc, dict) else None


def _get_attr(doc: Any, attr: str) -> Any:
    if hasattr(doc, attr):
        return getattr(doc, attr)
    if isinstance(doc, dict):
        return doc.get(attr)
    return None


# =============================================================================
# Asset Workflow
# =============================================================================

@register_workflow("asset")
async def asset_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Asset workflow handler.
    Delegates to the existing business logic in apis/asset.py.
    """
    from app.modules.asset_management.apis.asset import check_asset_workflow
    return await check_asset_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Incident Workflow
# =============================================================================

@register_workflow("incident")
async def incident_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Incident workflow handler.
    States: Draft → Reported → Under Investigation → Resolved → Closed / Reopened

    Actions:
    - report: Validate required fields, set to Reported
    - investigate: Create WO + WOA for corrective action
    - resolve: Validate corrective actions taken, link to WO
    - close: Final close with resolution notes
    - reopen: Allow re-investigation
    """
    from app.services.document import get_doc, new_doc, save_doc, get_list
    from datetime import datetime, timedelta

    incident_id = _get_id(doc)
    if not incident_id:
        return {"status": "error", "message": "Incident ID is required"}

    if action == "report":
        asset_id = _get_attr(doc, "asset")
        if not asset_id:
            return {"status": "error", "message": "Asset is required to report an incident"}
        return {"status": "success", "message": "Incident reported"}

    elif action == "investigate":
        asset_id = _get_attr(doc, "asset")
        site = _get_attr(doc, "site")
        department = _get_attr(doc, "department")
        description = _get_attr(doc, "description") or "Incident investigation"

        # Create corrective Work Order
        wo = await new_doc("work_order", db,
            workflow_state="Requested",
            work_order_type="Corrective",
            description=f"Incident Investigation: {description}",
            due_date=(datetime.now().date() + timedelta(days=7)),
            priority=_get_attr(doc, "priority") or "High",
            severity=_get_attr(doc, "severity"),
            asset=asset_id,
            site=site,
            department=department,
        )
        if wo:
            await save_doc(wo, db, commit=False)

            # Create WOA
            woa = await new_doc("work_order_activity", db,
                workflow_state="awaiting_resources",
                work_order=wo.id,
                description=f"Investigate Incident: {description}",
                work_item_type="Asset",
                work_item=asset_id,
                site=site,
                department=department,
                start_date=datetime.now(),
            )
            if woa:
                await save_doc(woa, db, commit=False)

            # Link WO to incident
            doc.work_order = wo.id
            await save_doc(doc, db, commit=False)

            # Create Maintenance Request
            mr = await new_doc("maintenance_request", db,
                workflow_state="Draft",
                asset=asset_id,
                description=f"Corrective action for incident: {description}",
                due_date=(datetime.now().date() + timedelta(days=7)),
                site=site,
                department=department,
                work_order_activity=woa.id,
                incident=incident_id,
            )
            if mr:
                mr.workflow_state = "pending_approval"
                await save_doc(mr, db, commit=False)
                mr.workflow_state = "approved"
                await save_doc(mr, db)

        return {
            "status": "success",
            "message": "Investigation started. Work Order and Maintenance Request created.",
            "action": "generate_id",
            "path": f"/work_order/{wo.id}" if wo else None,
        }

    elif action == "resolve":
        # Verify linked WO activities are completed
        wo_id = _get_attr(doc, "work_order")
        if wo_id:
            wo_activities = await get_list("work_order_activity", {"work_order": wo_id}, db=db)
            incomplete = [a for a in wo_activities if a.get("workflow_state") not in ("completed", "closed")]
            if incomplete:
                return {
                    "status": "error",
                    "message": f"Cannot resolve: {len(incomplete)} Work Order Activities are still open"
                }

        doc.resolved_date = datetime.now()
        await save_doc(doc, db)
        return {"status": "success", "message": "Incident resolved"}

    elif action == "close":
        return {"status": "success", "message": "Incident closed"}

    elif action == "reopen":
        doc.resolved_date = None
        await save_doc(doc, db)
        return {"status": "success", "message": "Incident reopened for re-investigation"}

    return {"status": "success", "message": f"Incident workflow '{action}' allowed"}
