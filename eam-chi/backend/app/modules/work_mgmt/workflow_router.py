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
            # Record downtime start when WO begins
            wo_doc = await get_doc("work_order", wo_id, db)
            if wo_doc and not getattr(wo_doc, "downtime_start", None):
                from datetime import datetime
                wo_doc.downtime_start = datetime.now()
                await save_doc(wo_doc, db)
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
            # Calculate downtime hours on completion
            wo_doc = await get_doc("work_order", wo_id, db)
            if wo_doc and getattr(wo_doc, "downtime_start", None):
                from datetime import datetime
                wo_doc.downtime_end = datetime.now()
                delta = wo_doc.downtime_end - wo_doc.downtime_start
                wo_doc.downtime_hours = round(delta.total_seconds() / 3600, 2)
                await save_doc(wo_doc, db)

            # Log asset maintenance history for each WO Activity's asset
            from app.services.document import new_doc as _new_doc
            from datetime import datetime as _dt
            wo_doc = wo_doc or await get_doc("work_order", wo_id, db)
            for activity in wo_activities:
                asset_id = activity.get("work_item")
                if not asset_id:
                    continue
                history = await _new_doc("asset_maintenance_history", db,
                    asset=asset_id,
                    work_order=wo_id,
                    work_order_activity=activity.get("id"),
                    maintenance_type=_get_attr(wo_doc, "work_order_type") if wo_doc else None,
                    description=activity.get("description"),
                    completed_date=_dt.now(),
                    downtime_hours=getattr(wo_doc, "downtime_hours", None) if wo_doc else None,
                    total_cost=getattr(wo_doc, "total_cost", None) if wo_doc else None,
                    category_of_failure=_get_attr(wo_doc, "category_of_failure") if wo_doc else None,
                    cause_code=_get_attr(wo_doc, "cause_code") if wo_doc else None,
                    remedy_code=_get_attr(wo_doc, "remedy_code") if wo_doc else None,
                    site=activity.get("site") or (_get_attr(wo_doc, "site") if wo_doc else None),
                )
                if history:
                    await save_doc(history, db, commit=False)

                # Increment asset repair count
                asset_doc = await get_doc("asset", asset_id, db)
                if asset_doc:
                    asset_doc.number_of_repairs = (getattr(asset_doc, "number_of_repairs", 0) or 0) + 1
                    await save_doc(asset_doc, db, commit=False)

            await db.commit()
            
            # Auto-create Failure Analysis if failure codes are present
            if wo_doc and (
                _get_attr(wo_doc, "cause_code")
                or _get_attr(wo_doc, "category_of_failure")
            ):
                fa = await _new_doc("failure_analysis", db,
                    work_order=wo_id,
                    asset=wo_activities[0].get("work_item") if wo_activities else None,
                    category_of_failure=_get_attr(wo_doc, "category_of_failure"),
                    cause_code=_get_attr(wo_doc, "cause_code"),
                    remedy_code=_get_attr(wo_doc, "remedy_code"),
                    analysis_date=_dt.now().date(),
                    site=_get_attr(wo_doc, "site"),
                    workflow_state="Draft",
                )
                if fa:
                    await save_doc(fa, db)

            return {"status": "success", "message": "Work Order completed"}

        elif action == "Reopen":
            return {"status": "success", "message": "Work Order reopened"}

        elif action == "Cancel":
            # Release all parts reservations for this WO
            from app.services.parts_reservation import release_all_reservations_for_wo_parts

            for activity in wo_activities:
                woa_id = activity.get("id")
                if woa_id:
                    wo_parts_list = await get_list("work_order_parts", {"work_order_activity": woa_id}, db=db)
                    for wp in wo_parts_list:
                        wp_id = wp.get("id")
                        if wp_id:
                            await release_all_reservations_for_wo_parts(wp_id, db)
            return {"status": "success", "message": "Work Order cancelled, reservations released"}

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
