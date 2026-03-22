"""
Entity CRUD Routes
===================
Create, Update, Delete operations for entities.
Thin handlers that delegate to EntityService.
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_from_token, CurrentUser
from app.core.serialization import record_to_dict
from app.core.exceptions import ForbiddenError
from app.meta.registry import MetaRegistry
from app.schemas.base import ActionRequest, ActionResponse
from app.services.rbac import RBACService
from app.application.hooks.registry import hook_registry
from app.application.hooks.context import SaveContext
from app.services.server_actions import server_actions, ActionContext
from app.services.socketio_manager import socket_manager
from app.services.naming import NamingService
from app.apis.base_entity_api import BaseEntityAPI, Context
from app.infrastructure.database.repositories.entity_repository import get_entity_model
from app.core.sanitization import sanitize_dict
from app.api.routes.entity_children import BulkChildRequest, bulk_save_children

router = APIRouter(tags=["entity"])

ENTITY_APIS: dict[str, BaseEntityAPI] = {}


def get_entity_api(entity: str) -> BaseEntityAPI:
    return ENTITY_APIS.get(entity, BaseEntityAPI())


def _coerce_incoming_types(model: Any, data: dict[str, Any]) -> dict[str, Any]:
    from app.application.services.entity_service import EntityService
    return EntityService.coerce_incoming_types(model, data)


def _validate_required_fields(meta: Any, data: dict[str, Any], action: str = "create") -> dict[str, str]:
    """Validate required fields from entity metadata. Returns dict of {field_name: error_message}."""
    errors: dict[str, str] = {}
    skip_fields = {"id", "created_at", "updated_at", "workflow_state", "row_no"}
    for field in (meta.fields or []):
        if field.name in skip_fields:
            continue
        if not field.required:
            continue
        # On update, only validate fields that are present in the payload
        if action == "update" and field.name not in data:
            continue
        value = data.get(field.name)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors[field.name] = f"{field.label} is required"
    return errors


@router.post("/{entity}/action", name="post_entity_action")
async def post_entity_action(
    entity: str,
    request: ActionRequest,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Single CRUD endpoint for entity actions."""
    try:
        meta = MetaRegistry.get(entity)
        if not meta:
            return ActionResponse(status="error", message=f"Entity '{entity}' not found")

        user = await get_current_user_from_token(authorization, db)
        api = get_entity_api(entity)
        model = get_entity_model(entity)

        if not model:
            return ActionResponse(status="error", message=f"Model for '{entity}' not found")

        ctx = Context(db=db, user=user, meta=meta)

        entity_label = meta.label or entity.replace("_", " ").title()

        if request.action == "create":
            if not await RBACService.check_permission_async(db, user, entity, "create"):
                raise ForbiddenError(f"You don't have permission to create {meta.label}")

            raw_data = sanitize_dict(request.data or {})

            # Validate required fields from metadata
            req_errors = _validate_required_fields(meta, raw_data, "create")
            if req_errors:
                return ActionResponse(status="error", message="Validation failed", errors=req_errors)

            errors = await api.validate_create(raw_data, ctx)
            if errors:
                return ActionResponse(status="error", message="Validation failed", errors=errors)

            data = await api.before_create(raw_data, ctx)

            save_ctx = SaveContext(db=db, user=user, entity=entity, action="create", meta=meta)
            # Execute before_save hooks via registry
            hook_result = await hook_registry.execute_before_save(entity, data, save_ctx)
            if hook_result and isinstance(hook_result, dict) and "errors" in hook_result:
                return ActionResponse(status="error", message="Validation failed", errors=hook_result["errors"])
            elif hook_result and isinstance(hook_result, dict) and "data" in hook_result:
                data = hook_result["data"]

            if meta.naming and meta.naming.enabled:
                if not data.get("id"):
                    generated_id = await NamingService.generate_id(db, meta.naming)
                    if generated_id:
                        data["id"] = generated_id

            # Auto-fill workflow_state from entity metadata when not provided
            if (
                meta.workflow and meta.workflow.enabled
                and data.get("workflow_state") in (None, "")
                and meta.workflow.initial_state
            ):
                data["workflow_state"] = meta.workflow.initial_state

            # If workflow is disabled in JSON but the table enforces NOT NULL on workflow_state,
            # fall back to DB workflow initial state when available.
            if data.get("workflow_state") in (None, "") and hasattr(model, "workflow_state"):
                try:
                    from app.services.workflow import WorkflowService

                    initial_state = await WorkflowService.get_initial_state(db, entity)
                    if initial_state:
                        data["workflow_state"] = initial_state
                except Exception:
                    pass

            data = _coerce_incoming_types(model, data)

            record = model(**data)
            db.add(record)

            try:
                await db.commit()
                await db.refresh(record)
            except Exception as e:
                await db.rollback()
                from sqlalchemy.exc import IntegrityError

                if isinstance(e, IntegrityError):
                    return ActionResponse(
                        status="error",
                        message="Database integrity error",
                        errors={"type": type(e).__name__, "error": str(e)},
                    )
                raise

            await api.after_create(record, ctx)
            # Execute after_save hooks via registry
            hook_result = await hook_registry.execute_after_save(entity, record, save_ctx)

            record_dict = record_to_dict(record)

            # Save children atomically if provided
            if request.children:
                parent_id = record_dict.get("id")
                if parent_id:
                    for child_entity, child_data in request.children.items():
                        bulk_req = BulkChildRequest(
                            rows=child_data.get("rows", []),
                            deleted_ids=child_data.get("deleted_ids", [])
                        )
                        # Use the same transaction for atomicity
                        child_result = await bulk_save_children(
                            entity, parent_id, child_entity, bulk_req, authorization, db
                        )
                        if child_result.status != "success":
                            await db.rollback()
                            return child_result

            await socket_manager.emit_created(entity, record_dict)
            await socket_manager.emit_post_save(entity, record_dict, "create", hook_result)

            created_id = record_dict.get("id") or request.id or "unknown"
            return ActionResponse(
                status="success",
                message=f"{entity_label} {created_id} created",
                data=record_dict,
            )

        elif request.action == "update":
            if not await RBACService.check_permission_async(db, user, entity, "update"):
                raise ForbiddenError(f"You don't have permission to update {meta.label}")

            if not request.id:
                return ActionResponse(status="error", message="ID required for update")

            from sqlalchemy import select
            result = await db.execute(select(model).where(model.id == request.id))
            record = result.scalar_one_or_none()

            if not record:
                return ActionResponse(status="error", message="Record not found")

            raw_data = sanitize_dict(request.data or {})

            # Validate required fields from metadata
            req_errors = _validate_required_fields(meta, raw_data, "update")
            if req_errors:
                return ActionResponse(status="error", message="Validation failed", errors=req_errors)

            errors = await api.validate_update(request.id, raw_data, ctx)
            if errors:
                return ActionResponse(status="error", message="Validation failed", errors=errors)

            data = await api.before_update(record, raw_data, ctx)

            save_ctx = SaveContext(db=db, user=user, entity=entity, action="update", meta=meta)
            # Execute before_save hooks via registry
            hook_result = await hook_registry.execute_before_save(entity, data, save_ctx)
            if hook_result and isinstance(hook_result, dict) and "errors" in hook_result:
                return ActionResponse(status="error", message="Validation failed", errors=hook_result["errors"])
            elif hook_result and isinstance(hook_result, dict) and "data" in hook_result:
                data = hook_result["data"]

            data = _coerce_incoming_types(model, data)

            system_fields = {"id", "created_at", "updated_at"}
            for key, value in data.items():
                if key in system_fields:
                    continue
                if hasattr(record, key):
                    setattr(record, key, value)

            try:
                await db.commit()
                await db.refresh(record)
            except Exception as e:
                await db.rollback()
                from sqlalchemy.exc import IntegrityError

                if isinstance(e, IntegrityError):
                    return ActionResponse(
                        status="error",
                        message="Database integrity error",
                        details={"type": type(e).__name__, "error": str(e)},
                    )
                raise

            await api.after_update(record, ctx)
            # Execute after_save hooks via registry
            hook_result = await hook_registry.execute_after_save(entity, record, save_ctx)
            await db.commit()

            # Save children atomically if provided
            if request.children:
                for child_entity, child_data in request.children.items():
                    bulk_req = BulkChildRequest(
                        rows=child_data.get("rows", []),
                        deleted_ids=child_data.get("deleted_ids", [])
                    )
                    # Use the same transaction for atomicity
                    child_result = await bulk_save_children(
                        entity, request.id, child_entity, bulk_req, authorization, db
                    )
                    if child_result.status != "success":
                        await db.rollback()
                        return child_result

            record_dict = record_to_dict(record)
            await socket_manager.emit_updated(entity, record_dict)
            await socket_manager.emit_post_save(entity, record_dict, "update", hook_result)

            updated_id = record_dict.get("id") or request.id or "unknown"
            return ActionResponse(
                status="success",
                message=f"{entity_label} {updated_id} updated",
                data=record_dict,
            )

        elif request.action == "delete":
            if not await RBACService.check_permission_async(db, user, entity, "delete"):
                raise ForbiddenError(f"You don't have permission to delete {meta.label}")

            if not request.id:
                return ActionResponse(status="error", message="ID required for delete")

            from sqlalchemy import select
            result = await db.execute(select(model).where(model.id == request.id))
            record = result.scalar_one_or_none()

            if not record:
                return ActionResponse(status="error", message="Record not found")

            await api.before_delete(record, ctx)

            record_id = record.id
            await db.delete(record)
            await db.commit()

            await api.after_delete(ctx)
            await socket_manager.emit_deleted(entity, record_id)

            deleted_id = record_id or request.id or "unknown"
            return ActionResponse(status="success", message=f"{entity_label} {deleted_id} deleted")

        else:
            action_ctx = ActionContext(
                db=db, user=user, entity_name=entity,
                record_id=request.id, params=request.data or {}
            )
            result = await server_actions.execute(entity, request.action, action_ctx)
            return ActionResponse(**result)

    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in post_entity_action for {entity}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return ActionResponse(
            status="error", message=str(e),
            details={"type": type(e).__name__, "entity": entity,
                     "action": getattr(request, 'action', 'unknown')}
        )


@router.delete("/{entity}/{id}", name="delete_entity")
async def delete_entity(
    entity: str,
    id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single record by ID using REST DELETE method."""
    from app.core.exceptions import NotFoundError, ForbiddenError

    meta = MetaRegistry.get(entity)
    if not meta:
        raise NotFoundError("Entity", entity)

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "delete"):
        raise ForbiddenError(f"You don't have permission to delete {meta.label}")

    model = get_entity_model(entity)
    if not model:
        raise NotFoundError("Model", entity)

    api = get_entity_api(entity)
    ctx = Context(db=db, user=user, meta=meta)

    from sqlalchemy import select
    result = await db.execute(select(model).where(model.id == id))
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundError(meta.label, id)

    try:
        await api.before_delete(record, ctx)
        record_id = record.id
        await db.delete(record)
        await db.commit()
        await api.after_delete(ctx)
        await socket_manager.emit_deleted(entity, record_id)
        return ActionResponse(status="success", message="Record deleted")
    except Exception as e:
        await db.rollback()
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            return ActionResponse(
                status="error",
                message=f"Cannot delete {meta.label}. It is referenced by other records.",
                details={"type": "foreign_key_violation", "error": error_msg}
            )
        raise


    # document_action route moved to entity_actions.py (SRP)
