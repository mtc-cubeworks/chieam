"""
Entity Children Routes
=======================
Bulk CRUD operations for parent-child entity relationships.
Supports saving all child rows in a single atomic transaction.
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_from_token, CurrentUser
from app.core.serialization import record_to_dict
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.sanitization import sanitize_dict
from app.meta.registry import MetaRegistry
from app.schemas.base import ActionResponse
from app.services.rbac import RBACService
from app.services.naming import NamingService
from app.infrastructure.database.repositories.entity_repository import get_entity_model
from app.api.routes.entity_list import _build_link_titles_single
from app.application.hooks.context import SaveContext
from app.application.hooks.registry import hook_registry
from app.services.socketio_manager import socket_manager

router = APIRouter(tags=["entity-children"])


class BulkChildRequest(BaseModel):
    """Request body for bulk child save."""
    rows: List[dict[str, Any]]
    deleted_ids: Optional[List[str]] = None


def _coerce_incoming_types(model: Any, data: dict[str, Any]) -> dict[str, Any]:
    from app.application.services.entity_service import EntityService
    return EntityService.coerce_incoming_types(model, data)


@router.get("/{entity}/{record_id}/children/{child_entity}", name="get_child_records")
async def get_child_records(
    entity: str,
    record_id: str,
    child_entity: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all child records for a parent entity record."""
    parent_meta = MetaRegistry.get(entity)
    if not parent_meta:
        raise NotFoundError("Entity", entity)

    child_meta = MetaRegistry.get(child_entity)
    if not child_meta:
        raise NotFoundError("Entity", child_entity)

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, child_entity, "read"):
        raise ForbiddenError(f"You don't have permission to read {child_meta.label}")

    # Find the FK field linking child to parent
    fk_field = _find_fk_field(parent_meta, child_entity)
    if not fk_field:
        return ActionResponse(
            status="error",
            message=f"No link found between {entity} and {child_entity}"
        )

    child_model = get_entity_model(child_entity)
    if not child_model:
        raise NotFoundError("Model", child_entity)

    # Query all child records (with row-level scoping)
    stmt = select(child_model).where(getattr(child_model, fk_field) == record_id)
    scope_filter = RBACService.build_scope_filter(user, child_model)
    if scope_filter is not None:
        stmt = stmt.where(scope_filter)
    result = await db.execute(stmt)
    records = result.scalars().all()

    rows = [record_to_dict(r) for r in records]

    # Build _link_titles for all rows (child link fields)
    link_titles: dict[str, str] = {}
    try:
      for r in rows:
        per_row = await _build_link_titles_single(db, child_meta, r)
        link_titles.update(per_row)
    except Exception:
      # Never fail child list because of link title resolution
      pass

    return {
        "status": "success",
        "data": rows,
        "total": len(rows),
        "child_entity": child_entity,
        "fk_field": fk_field,
        "_link_titles": link_titles,
    }


@router.post("/{entity}/{record_id}/children/{child_entity}", name="bulk_save_children")
async def bulk_save_children(
    entity: str,
    record_id: str,
    child_entity: str,
    request: BulkChildRequest,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk save child records for a parent entity in a single atomic transaction.

    For each row in request.rows:
    - If row has an 'id' that exists in DB → update
    - If row has no 'id' or id is empty → create new
    For each id in request.deleted_ids:
    - Delete the record

    All operations happen in one transaction (atomic).
    """
    parent_meta = MetaRegistry.get(entity)
    if not parent_meta:
        raise NotFoundError("Entity", entity)

    child_meta = MetaRegistry.get(child_entity)
    if not child_meta:
        raise NotFoundError("Entity", child_entity)

    user = await get_current_user_from_token(authorization, db)

    # Check permissions
    has_create = await RBACService.check_permission_async(db, user, child_entity, "create")
    has_update = await RBACService.check_permission_async(db, user, child_entity, "update")
    has_delete = await RBACService.check_permission_async(db, user, child_entity, "delete")

    # Find FK field
    fk_field = _find_fk_field(parent_meta, child_entity)
    if not fk_field:
        return ActionResponse(
            status="error",
            message=f"No link found between {entity} and {child_entity}"
        )

    child_model = get_entity_model(child_entity)
    if not child_model:
        raise NotFoundError("Model", child_entity)

    # Verify parent exists
    parent_model = get_entity_model(entity)
    if parent_model:
        parent_result = await db.execute(
            select(parent_model).where(parent_model.id == record_id)
        )
        if not parent_result.scalar_one_or_none():
            return ActionResponse(status="error", message=f"Parent record {record_id} not found")

    try:
        created = []
        updated = []
        hook_results: dict[str, dict[str, Any]] = {}
        deleted_count = 0
        errors = []

        # 1. Process deletes first
        if request.deleted_ids:
            if not has_delete:
                raise ForbiddenError(f"You don't have permission to delete {child_meta.label}")

            for del_id in request.deleted_ids:
                result = await db.execute(
                    select(child_model).where(child_model.id == del_id)
                )
                record = result.scalar_one_or_none()
                if record:
                    await db.delete(record)
                    deleted_count += 1

        # 2. Process creates and updates
        for idx, row_data in enumerate(request.rows):
            raw_data = sanitize_dict(row_data)

            # Always set the FK to point to parent
            raw_data[fk_field] = record_id

            # Remove system fields that shouldn't be sent
            row_id = raw_data.pop("id", None) or raw_data.pop("_id", None)
            raw_data.pop("created_at", None)
            raw_data.pop("updated_at", None)

            if row_id and not str(row_id).startswith("__new__"):
                # UPDATE existing record
                if not has_update:
                    errors.append({"row": idx, "error": "No update permission"})
                    continue

                result = await db.execute(
                    select(child_model).where(child_model.id == row_id)
                )
                record = result.scalar_one_or_none()

                if not record:
                    errors.append({"row": idx, "error": f"Record {row_id} not found"})
                    continue

                save_ctx = SaveContext(
                    db=db, user=user, entity=child_entity,
                    action="update", meta=child_meta
                )
                hook_result = await hook_registry.execute_before_save(
                    child_entity, raw_data, save_ctx
                )
                if hook_result and isinstance(hook_result, dict):
                    if "errors" in hook_result:
                        errors.append({"row": idx, "error": hook_result["errors"]})
                        continue
                    if "data" in hook_result:
                        raw_data = hook_result["data"]

                coerced = _coerce_incoming_types(child_model, raw_data)

                system_fields = {"id", "created_at", "updated_at"}
                for key, value in coerced.items():
                    if key in system_fields:
                        continue
                    if hasattr(record, key):
                        setattr(record, key, value)

                after_res = await hook_registry.execute_after_save(child_entity, record, save_ctx)
                if after_res is not None:
                    hook_results[str(row_id)] = {"action": "update", "result": after_res}
                updated.append(record)
            else:
                # CREATE new record
                if not has_create:
                    errors.append({"row": idx, "error": "No create permission"})
                    continue

                save_ctx = SaveContext(
                    db=db, user=user, entity=child_entity,
                    action="create", meta=child_meta
                )
                hook_result = await hook_registry.execute_before_save(
                    child_entity, raw_data, save_ctx
                )
                if hook_result and isinstance(hook_result, dict):
                    if "errors" in hook_result:
                        errors.append({"row": idx, "error": hook_result["errors"]})
                        continue
                    if "data" in hook_result:
                        raw_data = hook_result["data"]

                # Generate naming ID
                if child_meta.naming and child_meta.naming.enabled:
                    generated_id = await NamingService.generate_id(db, child_meta.naming)
                    if generated_id:
                        raw_data["id"] = generated_id

                # Auto-fill workflow_state
                if (
                    child_meta.workflow and child_meta.workflow.enabled
                    and raw_data.get("workflow_state") in (None, "")
                    and child_meta.workflow.initial_state
                ):
                    raw_data["workflow_state"] = child_meta.workflow.initial_state

                if raw_data.get("workflow_state") in (None, "") and hasattr(child_model, "workflow_state"):
                    try:
                        from app.services.workflow import WorkflowService
                        initial_state = await WorkflowService.get_initial_state(db, child_entity)
                        if initial_state:
                            raw_data["workflow_state"] = initial_state
                    except Exception:
                        pass

                coerced = _coerce_incoming_types(child_model, raw_data)
                record = child_model(**coerced)
                db.add(record)

                after_res = await hook_registry.execute_after_save(child_entity, record, save_ctx)
                created.append(record)
                # record.id may not exist yet; store on refresh phase
                if after_res is not None:
                    hook_results[f"__created__:{len(created)-1}"] = {"action": "create", "result": after_res}

        if errors:
            await db.rollback()
            return ActionResponse(
                status="error",
                message=f"Validation failed for {len(errors)} row(s)",
                errors={"rows": str(errors)}  # Convert list to string for schema compatibility
            )

        # Commit all changes atomically
        await db.commit()

        # Refresh all records to get DB-generated values
        all_records = []
        created_ids = {id(r) for r in created}
        created_idx = 0
        for record in created + updated:
            await db.refresh(record)
            rec_dict = record_to_dict(record)
            all_records.append(rec_dict)

            # Emit standard entity + post_save events so the frontend can toast
            if id(record) in created_ids:
                await socket_manager.emit_created(child_entity, rec_dict)
                hr = hook_results.get(f"__created__:{created_idx}")
                created_idx += 1
                await socket_manager.emit_post_save(
                    child_entity,
                    rec_dict,
                    "create",
                    (hr.get("result") if hr else None),
                )
            else:
                await socket_manager.emit_updated(child_entity, rec_dict)
                hr = hook_results.get(str(rec_dict.get("id")))
                await socket_manager.emit_post_save(
                    child_entity,
                    rec_dict,
                    "update",
                    (hr.get("result") if hr else None),
                )

        return ActionResponse(
            status="success",
            message=f"Saved {len(created)} new, {len(updated)} updated, {deleted_count} deleted",
            data={
                "rows": all_records,
                "created": len(created),
                "updated": len(updated),
                "deleted": deleted_count,
            }
        )

    except ForbiddenError:
        raise
    except Exception as e:
        await db.rollback()
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Bulk child save error for {entity}/{child_entity}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return ActionResponse(
            status="error",
            message=str(e),
        )


def _find_fk_field(parent_meta, child_entity: str) -> Optional[str]:
    """Find the FK field that links child_entity to parent entity.

    Checks both 'children' (inline child tables) and 'links' (related tabs).
    Links are stored as dicts in the registry.
    """
    # Check inline children first
    for child in (parent_meta.children or []):
        entity = child.entity if hasattr(child, "entity") else child.get("entity")
        fk = child.fk_field if hasattr(child, "fk_field") else child.get("fk_field")
        if entity == child_entity and fk:
            return fk

    # Fall back to links (stored as dicts)
    for link in (parent_meta.links or []):
        entity = link.get("entity") if isinstance(link, dict) else getattr(link, "entity", None)
        fk = link.get("fk_field") if isinstance(link, dict) else getattr(link, "fk_field", None)
        if entity == child_entity and fk:
            return fk

    return None
