"""
Entity Repository
==================
Concrete SQLAlchemy implementation of EntityRepositoryProtocol.
Extracts model lookup and generic CRUD from routers/entity.py and services/document.py.
"""
from typing import Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.serialization import record_to_dict


# Model cache for dynamic lookups
_MODEL_CACHE: dict[str, Any] = {}

# Pre-registered models (core models that aren't in modules)
_REGISTERED_MODELS: dict[str, Any] = {}


def register_model(entity_name: str, model_class: Any):
    """Register a model class for an entity name."""
    _REGISTERED_MODELS[entity_name] = model_class


def get_entity_model(entity: str) -> Optional[Any]:
    """Get SQLAlchemy model class by entity name.

    Lookup order:
    1. Pre-registered models (core auth/workflow models)
    2. Cache from previous lookups
    3. Dynamic scan of Base.registry.mappers (by __tablename__)
    """
    if entity in _REGISTERED_MODELS:
        return _REGISTERED_MODELS[entity]

    if entity in _MODEL_CACHE:
        return _MODEL_CACHE[entity]

    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if hasattr(cls, "__tablename__") and cls.__tablename__ == entity:
            _MODEL_CACHE[entity] = cls
            return cls

    return None


def register_core_models():
    """Register core models that live outside modules.

    Called once during app startup after models are imported.
    """
    from app.models.auth import User, Role, EntityPermission
    from app.models.workflow import (
        Workflow, WorkflowState, WorkflowAction,
        WorkflowStateLink, WorkflowTransition,
    )

    for name, cls in {
        "users": User,
        "role": Role,
        "entity_permission": EntityPermission,
        "workflow": Workflow,
        "workflow_state": WorkflowState,
        "workflow_action": WorkflowAction,
        "workflow_state_link": WorkflowStateLink,
        "workflow_transition": WorkflowTransition,
    }.items():
        register_model(name, cls)


class EntityRepository:
    """Concrete entity repository backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Model lookup
    # ------------------------------------------------------------------

    def get_model(self, entity: str) -> Optional[Any]:
        return get_entity_model(entity)

    # ------------------------------------------------------------------
    # Single record
    # ------------------------------------------------------------------

    async def get_by_id(self, entity: str, record_id: str) -> Optional[Any]:
        model = self.get_model(entity)
        if not model:
            return None
        result = await self.db.execute(select(model).where(model.id == record_id))
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Paginated list
    # ------------------------------------------------------------------

    async def get_list(
        self,
        entity: str,
        filters: Optional[dict] = None,
        search: Optional[str] = None,
        search_fields: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        model = self.get_model(entity)
        if not model:
            return [], 0

        query = select(model)
        count_query = select(func.count()).select_from(model)

        # Apply filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(model, field_name) and value is not None:
                    query = query.where(getattr(model, field_name) == value)
                    count_query = count_query.where(getattr(model, field_name) == value)

        # Apply search
        if search and search_fields:
            from sqlalchemy import or_
            conditions = []
            for sf in search_fields:
                if hasattr(model, sf):
                    conditions.append(getattr(model, sf).ilike(f"%{search}%"))
            if conditions:
                query = query.where(or_(*conditions))
                count_query = count_query.where(or_(*conditions))

        # Count
        total = (await self.db.execute(count_query)).scalar() or 0

        # Order
        if order_by and hasattr(model, order_by):
            col = getattr(model, order_by)
            query = query.order_by(col.desc() if order_dir == "desc" else col.asc())

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        records = [record_to_dict(r) for r in result.scalars().all()]
        return records, total

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create(self, entity: str, data: dict[str, Any]) -> Any:
        model = self.get_model(entity)
        if not model:
            return None
        record = model(**data)
        self.db.add(record)
        await self.db.flush()
        return record

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update(self, entity: str, record_id: str, data: dict[str, Any]) -> Optional[Any]:
        record = await self.get_by_id(entity, record_id)
        if not record:
            return None
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        await self.db.flush()
        return record

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete(self, entity: str, record_id: str) -> bool:
        record = await self.get_by_id(entity, record_id)
        if not record:
            return False
        await self.db.delete(record)
        await self.db.flush()
        return True

    # ------------------------------------------------------------------
    # Options (for link dropdowns)
    # ------------------------------------------------------------------

    async def get_options(
        self,
        entity: str,
        search: Optional[str] = None,
        filters: Optional[dict] = None,
        title_field: str = "name",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        model = self.get_model(entity)
        if not model:
            return []

        query = select(model)

        if filters:
            for field_name, value in filters.items():
                if hasattr(model, field_name) and value is not None:
                    query = query.where(getattr(model, field_name) == value)

        if search and hasattr(model, title_field):
            query = query.where(getattr(model, title_field).ilike(f"%{search}%"))

        query = query.limit(limit)
        result = await self.db.execute(query)
        records = result.scalars().all()

        options = []
        for r in records:
            label = getattr(r, title_field, None) or getattr(r, "id", "")
            options.append({"value": r.id, "label": str(label)})
        return options
