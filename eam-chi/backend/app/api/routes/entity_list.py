"""
Entity List Routes
===================
List and List-view operations for entities.
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql.sqltypes import String, Text

from app.core.database import get_db
from app.core.security import get_current_user_from_token, CurrentUser
from app.core.serialization import record_to_dict
from app.core.exceptions import NotFoundError, ForbiddenError
from app.meta.registry import MetaRegistry
from app.schemas.base import ActionResponse
from app.services.rbac import RBACService
from app.infrastructure.database.repositories.entity_repository import get_entity_model

router = APIRouter(tags=["entity"])


def _inject_link_name_fields(meta, record_dict: dict, link_titles: dict[str, str]) -> None:
    if not meta or not getattr(meta, "fields", None):
        return

    for field in meta.fields:
        if hasattr(field, 'field_type'):
            field_type = field.field_type
            link_entity = getattr(field, 'link_entity', None)
            child_entity = getattr(field, 'child_entity', None)
            field_name = field.name
            query_key = getattr(getattr(field, 'query', None), 'key', None)
            if query_key is None and isinstance(getattr(field, 'query', None), dict):
                query_key = getattr(field, 'query', {}).get('key')
        elif isinstance(field, dict):
            field_type = field.get('field_type')
            link_entity = field.get('link_entity')
            child_entity = field.get('child_entity')
            field_name = field.get('name')
            query_key = (field.get('query') or {}).get('key')
        else:
            continue

        if field_type == 'parent_child_link' and child_entity:
            link_entity = child_entity
            field_type = 'link'

        if field_type == 'query_link':
            if not link_entity and query_key:
                try:
                    from app.services.query_link_handlers import QUERY_LINK_TARGET_ENTITY

                    link_entity = QUERY_LINK_TARGET_ENTITY.get(query_key)
                except Exception:
                    link_entity = None
            field_type = 'link'

        if field_type != 'link' or not link_entity or not field_name:
            continue

        fk_value = record_dict.get(field_name)
        if not fk_value:
            continue

        name_field = f"{field_name}_name"
        if record_dict.get(name_field) not in (None, ""):
            continue

        key = f"{link_entity}::{fk_value}"
        title = link_titles.get(key)
        if title:
            record_dict[name_field] = title


async def _build_link_titles_batch(db: AsyncSession, meta, records: list[dict]) -> list[dict[str, str]]:
    """Build _link_titles dict for multiple records using batch queries."""
    if not meta.fields or not records:
        return [{} for _ in records]

    entity_fk_map: dict[str, set[str]] = {}
    field_entity_map: dict[str, str] = {}

    for field in meta.fields:
        if hasattr(field, 'field_type'):
            field_type = field.field_type
            link_entity = getattr(field, 'link_entity', None)
            child_entity = getattr(field, 'child_entity', None)
            field_name = field.name
            query_key = getattr(getattr(field, 'query', None), 'key', None)
            if query_key is None and isinstance(getattr(field, 'query', None), dict):
                query_key = getattr(field, 'query', {}).get('key')
        elif isinstance(field, dict):
            field_type = field.get('field_type')
            link_entity = field.get('link_entity')
            child_entity = field.get('child_entity')
            field_name = field.get('name')
            query_key = (field.get('query') or {}).get('key')
        else:
            continue

        if field_type == 'parent_child_link' and child_entity:
            link_entity = child_entity
            field_type = 'link'

        if field_type == 'query_link':
            if not link_entity and query_key:
                try:
                    from app.services.query_link_handlers import QUERY_LINK_TARGET_ENTITY

                    link_entity = QUERY_LINK_TARGET_ENTITY.get(query_key)
                except Exception:
                    link_entity = None
            field_type = 'link'

        if field_type != 'link' or not link_entity or not field_name:
            continue

        field_entity_map[field_name] = link_entity

        fk_values = set()
        for record in records:
            fk_value = record.get(field_name)
            if fk_value:
                fk_values.add(str(fk_value))

        if fk_values:
            entity_fk_map[link_entity] = entity_fk_map.get(link_entity, set()) | fk_values

    linked_entities_data: dict[str, dict[str, str]] = {}

    for entity_name, fk_values in entity_fk_map.items():
        if not fk_values:
            continue

        linked_meta = MetaRegistry.get(entity_name)
        linked_model = get_entity_model(entity_name)

        if not linked_meta or not linked_model:
            continue

        title_field = linked_meta.title_field or 'id'

        try:
            result = await db.execute(
                select(linked_model).where(linked_model.id.in_(list(fk_values)))
            )
            linked_records = result.scalars().all()

            entity_titles = {}
            for record in linked_records:
                record_id = str(getattr(record, 'id', None))
                title_value = getattr(record, title_field, None) or record_id
                entity_titles[record_id] = str(title_value)

            linked_entities_data[entity_name] = entity_titles
        except Exception:
            continue

    records_link_titles = []
    for record in records:
        link_titles = {}
        for field_name, entity_name in field_entity_map.items():
            fk_value = record.get(field_name)
            if not fk_value:
                continue
            entity_titles = linked_entities_data.get(entity_name, {})
            title_value = entity_titles.get(str(fk_value))
            if title_value:
                key = f"{entity_name}::{fk_value}"
                link_titles[key] = title_value
        records_link_titles.append(link_titles)

    return records_link_titles


@router.get("/{entity}/list", name="get_entity_list")
async def get_entity_list(
    entity: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_field: Optional[str] = Query(None),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    filter_field: Optional[str] = Query(None),
    filter_value: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List records for an entity."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "read"):
        raise ForbiddenError(f"You don't have permission to access {meta.label}")

    model = get_entity_model(entity)
    if not model:
        return ActionResponse(status="error", message=f"Model for '{entity}' not found")

    offset = (page - 1) * page_size
    selectable_columns = set(getattr(model, "__table__").columns.keys())

    query = select(model)
    count_query = select(func.count()).select_from(model)

    # --- Row-level data scoping ---
    scope_filter = RBACService.build_scope_filter(user, model)
    if scope_filter is not None:
        query = query.where(scope_filter)
        count_query = count_query.where(scope_filter)

    if filter_field and filter_value is not None:
        if filter_field not in selectable_columns:
            return ActionResponse(status="error", message=f"Invalid filter field '{filter_field}'")
        col = getattr(model, filter_field)
        if isinstance(col.type, (String, Text)):
            clause = col.ilike(f"%{filter_value}%")
        else:
            clause = col == filter_value
        query = query.where(clause)
        count_query = count_query.where(clause)

    if sort_field:
        if sort_field not in selectable_columns:
            return ActionResponse(status="error", message=f"Invalid sort field '{sort_field}'")
        sort_col = getattr(model, sort_field)
        query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())
    elif hasattr(model, 'created_at'):
        query = query.order_by(model.created_at.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    result = await db.execute(query.offset(offset).limit(page_size))
    records = result.scalars().all()

    data = [record_to_dict(r) for r in records]

    return {
        "status": "success",
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{entity}/list-view", name="get_entity_list_view")
async def get_entity_list_view(
    entity: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_field: Optional[str] = Query(None),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    filter_field: Optional[str] = Query(None),
    filter_value: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List records with enriched link field display names."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "read"):
        raise ForbiddenError(f"You don't have permission to access {meta.label}")

    model = get_entity_model(entity)
    if not model:
        return ActionResponse(status="error", message=f"Model for '{entity}' not found")

    offset = (page - 1) * page_size
    selectable_columns = set(getattr(model, "__table__").columns.keys())

    # Determine fields to return
    fields_to_return = ['id', 'created_at', 'updated_at']

    # Add in_list_view fields
    if meta.fields:
        for field in meta.fields:
            if getattr(field, 'in_list_view', False):
                fields_to_return.append(field.name)

    # Add workflow_state if entity has it
    if meta.fields and any(getattr(f, 'name', None) == 'workflow_state' for f in meta.fields):
        fields_to_return.append('workflow_state')

    # Remove duplicates while preserving order
    seen = set()
    fields_to_return = [x for x in fields_to_return if not (x in seen or seen.add(x))]

    # Filter fields_to_return to only those that exist in the table
    fields_to_return = [f for f in fields_to_return if f in selectable_columns]

    query = select(model)
    count_query = select(func.count()).select_from(model)

    # --- Row-level data scoping ---
    scope_filter = RBACService.build_scope_filter(user, model)
    if scope_filter is not None:
        query = query.where(scope_filter)
        count_query = count_query.where(scope_filter)

    if filter_field and filter_value is not None:
        if filter_field not in selectable_columns:
            return ActionResponse(status="error", message=f"Invalid filter field '{filter_field}'")
        col = getattr(model, filter_field)
        if isinstance(col.type, (String, Text)):
            clause = col.ilike(f"%{filter_value}%")
        else:
            clause = col == filter_value
        query = query.where(clause)
        count_query = count_query.where(clause)

    if sort_field:
        if sort_field not in selectable_columns:
            return ActionResponse(status="error", message=f"Invalid sort field '{sort_field}'")
        sort_col = getattr(model, sort_field)
        query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())
    elif hasattr(model, 'created_at'):
        query = query.order_by(model.created_at.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    result = await db.execute(query.offset(offset).limit(page_size))
    records = result.scalars().all()

    data = []
    if records:
        records_dict = []
        for record in records:
            full_dict = record_to_dict(record)
            filtered_dict = {k: full_dict.get(k) for k in fields_to_return}
            records_dict.append(filtered_dict)

        all_link_titles = await _build_link_titles_batch(db, meta, records_dict)
        for i, record_dict in enumerate(records_dict):
            record_dict["_link_titles"] = all_link_titles[i] or {}
            _inject_link_name_fields(meta, record_dict, record_dict["_link_titles"])
            data.append(record_dict)

    return {
        "status": "success",
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{entity}/detail/{id}", name="get_entity_detail")
async def get_entity_detail(
    entity: str,
    id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a single record by ID."""
    # import time as _time  # Timing disabled
    # _t0 = _time.time()

    meta = MetaRegistry.get(entity)
    if not meta:
        raise NotFoundError("Entity", entity)

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "read"):
        raise ForbiddenError(f"You don't have permission to read {meta.label}")
    # print(f"[TIMING] {entity}/{id} auth: {(_time.time()-_t0)*1000:.0f}ms")

    # _t1 = _time.time()
    model = get_entity_model(entity)
    if not model:
        raise NotFoundError("Model", entity)

    detail_query = select(model).where(model.id == id)
    # --- Row-level data scoping ---
    scope_filter = RBACService.build_scope_filter(user, model)
    if scope_filter is not None:
        detail_query = detail_query.where(scope_filter)

    result = await db.execute(detail_query)
    record = result.scalar_one_or_none()
    # print(f"[TIMING] {entity}/{id} main query: {(_time.time()-_t1)*1000:.0f}ms")

    if not record:
        raise NotFoundError(meta.label, id)

    # _t2 = _time.time()
    record_data = record_to_dict(record)
    # print(f"[TIMING] {entity}/{id} serialization: {(_time.time()-_t2)*1000:.0f}ms")

    # Get linked entity counts
    # _t3 = _time.time()
    linked_counts = {}
    if meta.links:
        for link in meta.links:
            link_entity = link.get("entity")
            fk_field = link.get("fk_field")
            if link_entity and fk_field:
                link_model = get_entity_model(link_entity)
                if link_model and hasattr(link_model, fk_field):
                    count_stmt = select(func.count()).select_from(link_model).where(
                        getattr(link_model, fk_field) == record.id
                    )
                    count_result = await db.execute(count_stmt)
                    linked_counts[link_entity] = count_result.scalar() or 0
    # print(f"[TIMING] {entity}/{id} linked_counts ({len(linked_counts)} links): {(_time.time()-_t3)*1000:.0f}ms")

    # Build _link_titles for link fields
    # _t4 = _time.time()
    link_titles = await _build_link_titles_single(db, meta, record)
    # print(f"[TIMING] {entity}/{id} link_titles ({len(link_titles)} titles): {(_time.time()-_t4)*1000:.0f}ms")
    # print(f"[TIMING] {entity}/{id} TOTAL: {(_time.time()-_t0)*1000:.0f}ms")

    _inject_link_name_fields(meta, record_data, link_titles)

    return {
        "status": "success",
        "data": record_data,
        "linked_counts": linked_counts,
        "_link_titles": link_titles,
    }


async def _build_link_titles_single(db: AsyncSession, meta, record) -> dict[str, str]:
    """Build _link_titles dict for a single record."""
    link_titles = {}

    if not meta.fields:
        return link_titles

    for field in meta.fields:
        if hasattr(field, 'field_type'):
            field_type = field.field_type
            link_entity = getattr(field, 'link_entity', None)
            child_entity = getattr(field, 'child_entity', None)
            field_name = field.name
            query_key = getattr(getattr(field, 'query', None), 'key', None)
            if query_key is None and isinstance(getattr(field, 'query', None), dict):
                query_key = getattr(field, 'query', {}).get('key')
        elif isinstance(field, dict):
            field_type = field.get('field_type')
            link_entity = field.get('link_entity')
            child_entity = field.get('child_entity')
            field_name = field.get('name')
            query_key = (field.get('query') or {}).get('key')
        else:
            continue

        if field_type == 'parent_child_link' and child_entity:
            link_entity = child_entity
            field_type = 'link'

        if field_type == 'query_link':
            if not link_entity and query_key:
                try:
                    from app.services.query_link_handlers import QUERY_LINK_TARGET_ENTITY

                    link_entity = QUERY_LINK_TARGET_ENTITY.get(query_key)
                except Exception:
                    link_entity = None
            field_type = 'link'

        if field_type != 'link' or not link_entity or not field_name:
            continue

        if isinstance(record, dict):
            fk_value = record.get(field_name)
        else:
            fk_value = getattr(record, field_name, None)
        if not fk_value:
            continue

        linked_meta = MetaRegistry.get(link_entity)
        linked_model = get_entity_model(link_entity)

        if not linked_meta or not linked_model:
            continue

        title_field = linked_meta.title_field or 'id'

        try:
            result = await db.execute(
                select(linked_model).where(linked_model.id == fk_value)
            )
            linked_record = result.scalar_one_or_none()

            if linked_record:
                title_value = getattr(linked_record, title_field, None) or fk_value
                key = f"{link_entity}::{fk_value}"
                link_titles[key] = str(title_value)
        except Exception:
            pass

    return link_titles
