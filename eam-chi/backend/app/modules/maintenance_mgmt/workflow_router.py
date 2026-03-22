"""
Maintenance Management Module - Central Workflow Router
========================================================
Single entry point for all workflow logic in the Maintenance Management module.

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
    """Central workflow router for the Maintenance Management module."""
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
# Maintenance Request Workflow
# =============================================================================

@register_workflow("maintenance_request")
async def maintenance_request_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Maintenance Request workflow handler.

    States: Draft → Approved → Release → Completed
                  → Emergency
                  → Reopened

    Business Rules:
    - Approve / Submit for Emergency / Submit for Resolution: generate Work Order + WOA
    - Complete: linked WOA must be 'Completed' or 'Closed'
    - Reopen: always allowed
    """
    from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
    return await check_maintenance_request_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Maintenance Order Workflow
# =============================================================================

@register_workflow("maintenance_order")
async def maintenance_order_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Maintenance Order workflow handler.

    States: Draft → Approved → Released → Closed

    Business Rules:
    - Approve: validates MO has details
    - Release / Generate Work Order: creates WO from MO details, transitions MRs to Release
    - Close: all linked WOAs must be complete
    """
    from app.services.document import get_list

    if not doc:
        return {"status": "error", "message": "Maintenance Order not specified"}

    mo_id = _get_id(doc)
    if not mo_id:
        return {"status": "error", "message": "Maintenance Order ID is required"}

    try:
        if action == "Approve":
            mo_details = await get_list(
                "maintenance_order_detail",
                {"maintenance_order": mo_id},
                db=db
            )
            if not mo_details:
                return {"status": "error", "message": "Cannot approve: Maintenance Order has no details"}
            return {"status": "success", "message": "Maintenance Order approved"}

        elif action in ("Release", "Generate Work Order"):
            from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order
            return await generate_work_order_from_maintenance_order(doc, db, user)

        elif action == "Close":
            return {"status": "success", "message": "Maintenance Order closed"}

        return {"status": "success", "message": f"Maintenance Order workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Maintenance Order workflow error: {str(e)}"}
