"""
Work Management Module - Central Workflow Router
==================================================
Single entry point for all workflow logic in the Work Management module.

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
    """Central workflow router for the Work Management module."""
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
# Work Order Workflow
# =============================================================================

@register_workflow("work_order")
async def work_order_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Work Order workflow handler.

    States: Requested → Approved → In Progress → Completed → Closed
                                                            → Reopened

    Business Rules:
    - Approve: Always allowed
    - Start: All WOAs must be in 'Ready' state; cascade start to all WOAs
    - Complete: All WOAs must be 'Completed' or 'Closed'
    - Reopen: Always allowed
    """
    from app.services.document import get_list, get_doc, save_doc

    if not doc:
        return {"status": "error", "message": "Work Order not specified"}

    wo_id = _get_id(doc)
    if not wo_id:
        return {"status": "error", "message": "Work Order ID is required"}

    try:
        wo_activities = await get_list(
            "work_order_activity",
            {"work_order": wo_id},
            db=db,
            as_dict=True
        )

        if action == "Approve":
            return {"status": "success", "message": "Work Order approved"}

        elif action == "Start":
            if not wo_activities:
                return {"status": "error", "message": "No work order activities found"}

            ready_count = sum(1 for a in wo_activities if a.get("workflow_state") == "ready")
            if ready_count != len(wo_activities):
                return {
                    "status": "error",
                    "message": "Cannot start Work Order because not all Work Order Activities are ready"
                }

            # Cascade: apply "Start Activity" to each WOA
            for activity in wo_activities:
                woa_id = activity.get("id")
                if woa_id:
                    woa_doc = await get_doc("work_order_activity", woa_id, db)
                    if woa_doc and getattr(woa_doc, 'workflow_state', None) == "ready":
                        woa_doc.workflow_state = "in_progress"
                        await save_doc(woa_doc, db, commit=False)

            await db.commit()
            return {"status": "success", "message": "Work Order started, all activities moved to In Progress"}

        elif action == "Complete":
            if not wo_activities:
                return {"status": "error", "message": "No work order activities found"}

            completed_count = sum(
                1 for a in wo_activities
                if a.get("workflow_state") in ["completed", "closed"]
            )
            if completed_count != len(wo_activities):
                return {
                    "status": "error",
                    "message": "Cannot complete Work Order because not all Work Order Activities are complete"
                }
            return {"status": "success", "message": "Work Order completed"}

        elif action == "Reopen":
            return {"status": "success", "message": "Work Order reopened"}

        return {"status": "success", "message": f"Work Order workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Work Order workflow error: {str(e)}"}


# =============================================================================
# Work Order Activity Workflow
# =============================================================================

@register_workflow("work_order_activity")
async def work_order_activity_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Work Order Activity workflow handler.
    Delegates to the existing business logic in apis/work_order_activity.py.
    """
    from app.modules.work_mgmt.apis.work_order_activity import check_work_order_activity_workflow
    return await check_work_order_activity_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Work Order Parts Workflow
# =============================================================================

@register_workflow("work_order_parts")
async def work_order_parts_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Work Order Parts workflow handler.
    Delegates to the existing business logic in apis/work_order_parts.py.
    """
    from app.modules.work_mgmt.apis.work_order_parts import check_work_order_parts_workflow
    return await check_work_order_parts_workflow(doc=doc, action=action, db=db, user=user)
