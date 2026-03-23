"""
Entity Workflow Routes
=======================
Workflow transition operations for entities.
"""
import re
from typing import Any, Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_from_token, CurrentUser
from app.core.serialization import record_to_dict
from app.meta.registry import MetaRegistry
from app.schemas.base import ActionResponse, WorkflowRequest
from app.services.workflow import WorkflowDBService
from app.application.hooks.registry import hook_registry
from app.application.hooks.context import WorkflowContext
from app.services.socketio_manager import socket_manager
from app.services.audit import audit_service
from app.infrastructure.database.repositories.entity_repository import get_entity_model

router = APIRouter(tags=["entity"])


@router.post("/{entity}/workflow")
async def workflow_action(
    entity: str,
    request: WorkflowRequest,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Execute a workflow transition."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(
            status="error",
            message=f"Entity '{entity}' not found",
            errors={"entity": f"Unknown entity: {entity}"}
        )

    model = get_entity_model(entity)
    if not model:
        return ActionResponse(
            status="error",
            message=f"Model for '{entity}' not found",
            errors={"model": f"No SQLAlchemy model registered for: {entity}"}
        )

    user = await get_current_user_from_token(authorization, db)

    workflow = await WorkflowDBService.get_workflow(db, entity)
    if not workflow:
        return ActionResponse(
            status="error",
            message=f"No workflow configured for entity '{entity}'",
            errors={"workflow": f"Create a workflow with target_entity='{entity}' first"}
        )

    result = await db.execute(
        select(model).where(model.id == request.id).with_for_update()
    )
    doc = result.scalar_one_or_none()

    if not doc:
        return ActionResponse(
            status="error",
            message=f"Record '{request.id}' not found",
            errors={"id": f"No {meta.label} found with ID: {request.id}"}
        )

    # Get current state and normalize to slug format
    current_state_raw = getattr(doc, "workflow_state", None)
    if not current_state_raw:
        initial_link = next((sl for sl in workflow.state_links if sl.is_initial), None)
        current_state = initial_link.state.slug if initial_link else None
    else:
        current_state = current_state_raw.lower().strip()
        current_state = re.sub(r'[^a-z0-9\s_]', '', current_state)
        current_state = re.sub(r'\s+', '_', current_state)

    # Validate transition
    is_valid, target_state, error = await WorkflowDBService.validate_transition(
        db, entity, current_state, request.action, user
    )

    if not is_valid:
        return ActionResponse(
            status="error",
            message=error,
            errors={"action": f"Cannot perform '{request.action}' from state '{current_state}'"}
        )

    # Resolve human-readable action label for workflow hooks
    action_label = await WorkflowDBService.get_action_label(db, entity, request.action)
    if not action_label:
        action_label = request.action  # fallback to slug

    # Run workflow hook (pass human-readable label as action)
    wf_ctx = WorkflowContext(
        db=db, user=user, entity=entity, doc=doc,
        record_id=request.id, action=action_label,
        from_state=current_state, to_state=target_state
    )
    hook_result = await hook_registry.execute_workflow(entity, wf_ctx)

    if hook_result["status"] == "error":
        # Rollback any partial writes from the hook before returning error
        await db.rollback()
        return ActionResponse(
            status="error",
            message=hook_result["message"],
            errors=hook_result.get("errors")
        )

    # Apply state transition on the parent doc
    setattr(doc, "workflow_state", target_state)
    await db.commit()
    await db.refresh(doc)

    # Audit trail for workflow state transition (SM-6)
    await audit_service.log_workflow(
        db, entity, request.id, current_state, target_state, request.action,
        user_id=user.id if user else None,
        username=user.username if user else None,
    )
    await db.commit()

    doc_dict = record_to_dict(doc)
    await socket_manager.emit_workflow(entity, doc_dict, request.action, current_state, target_state)

    # Build response — pass through redirect data if the hook created a new record
    response_data = doc_dict
    if hook_result.get("action") == "generate_id":
        response_data = {
            **doc_dict,
            "redirect_action": "generate_id",
            "redirect_path": hook_result.get("path"),
        }
    if hook_result.get("auto_closed"):
        response_data = {
            **doc_dict,
            "auto_closed": True,
            "parent_entity": hook_result.get("parent_entity"),
            "parent_id": hook_result.get("parent_id"),
        }

    return ActionResponse(
        status="success",
        message=f"Successfully transitioned from '{current_state}' to '{target_state}'",
        data=response_data
    )
