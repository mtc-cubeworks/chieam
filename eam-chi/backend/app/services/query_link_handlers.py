"""
Query Link Handlers
===================
Whitelisted query methods for query_link field type.
Each key maps to a specific handler function that returns options.
"""
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.core_eam.models.request_activity_type import RequestActivityType
from app.meta.registry import MetaRegistry


async def sample_test_query(
    db: AsyncSession,
    entity: str,
    field: str,
    form_state: Optional[dict] = None,
    static_params: Optional[dict] = None
) -> list[dict]:
    """
    Sample test query handler that returns a simple test option.
    Used for testing query_link field type.
    """
    return [
        {
            "value": "hello",
            "label": "hello"
        }
    ]


async def request_activity_type_query(
    db: AsyncSession,
    entity: str,
    field: str,
    form_state: Optional[dict] = None,
    static_params: Optional[dict] = None
) -> list[dict]:
    """
    Query handler for Request Activity Type filtering.
    Filters Request Activity Types based on asset workflow state.
    
    Expected form_state:
    - asset: Asset ID (will fetch asset's workflow_state)
    - workflow_state: Direct workflow_state (overrides asset's state)
    - type: Optional type filter (default: 'Asset')
    """
    workflow_state = None
    type_filter = form_state.get('type', 'Asset') if form_state else 'Asset'
    
    # If asset/work_item is provided, fetch its workflow_state
    asset_workflow_state = None
    asset_id = None
    if form_state:
        # Check for 'asset' field (for maintenance_request) or 'work_item' field (for work_order_activity)
        asset_id = form_state.get('asset') or form_state.get('work_item')
    
    if asset_id:
        from app.modules.asset_management.models.asset import Asset
        result = await db.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if asset:
            asset_workflow_state = asset.workflow_state
    
    # For request activity types, use asset workflow_state if available
    # Otherwise use direct workflow_state from form
    if asset_workflow_state:
        workflow_state = asset_workflow_state
    elif form_state and form_state.get('workflow_state'):
        workflow_state = form_state.get('workflow_state')
    
    query = select(RequestActivityType)
    
    # Filter by type if provided
    if type_filter:
        query = query.where(RequestActivityType.type == type_filter)
    
    # Filter by state if workflow_state is provided
    if workflow_state:
        # Make case-insensitive comparison
        query = query.where(RequestActivityType.state.ilike(workflow_state))
    
    search = (static_params or {}).get("search")
    limit = int((static_params or {}).get("limit") or 10)
    if limit < 1:
        limit = 10

    meta = MetaRegistry.get("request_activity_type")
    title_field = (meta.title_field if meta else None) or "id"

    if search:
        cols = []
        if hasattr(RequestActivityType, "id"):
            cols.append(RequestActivityType.id.ilike(f"%{search}%"))
        if hasattr(RequestActivityType, title_field) and title_field != "id":
            cols.append(getattr(RequestActivityType, title_field).ilike(f"%{search}%"))
        if cols:
            query = query.where(*cols)

    # Order by title_field for consistent results
    if hasattr(RequestActivityType, title_field):
        query = query.order_by(getattr(RequestActivityType, title_field))
    else:
        query = query.order_by(RequestActivityType.id)

    query = query.limit(limit)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    list_view_fields: list[str] = []
    if meta:
        list_view_fields = [
            f.name for f in meta.fields if f.in_list_view and f.name != title_field
        ]

    options: list[dict] = []
    for record in records:
        value = getattr(record, "id", None)
        label = getattr(record, title_field, None) or value

        option: dict[str, Any] = {"value": str(value), "label": str(label)}

        desc_parts: list[str] = []
        for field_name in list_view_fields:
            if hasattr(record, field_name):
                field_value = getattr(record, field_name)
                if field_value not in (None, ""):
                    desc_parts.append(str(field_value))
        if desc_parts:
            option["description"] = " | ".join(desc_parts)

        options.append(option)
    
    return options


# Whitelist mapping: key -> handler function
QUERY_HANDLERS = {
    "sample_test": sample_test_query,
    "request_activity_type": request_activity_type_query,
}


QUERY_LINK_TARGET_ENTITY: dict[str, str] = {
    "request_activity_type": "request_activity_type",
}


async def execute_query_link(
    key: str,
    db: AsyncSession,
    entity: str,
    field: str,
    form_state: Optional[dict] = None,
    static_params: Optional[dict] = None
) -> dict:
    """
    Execute a whitelisted query link handler.
    
    Args:
        key: Whitelisted handler key
        db: Database session
        entity: Entity name
        field: Field name
        form_state: Current form data
        static_params: Static parameters from field config
        
    Returns:
        Dict with status and options list
    """
    handler = QUERY_HANDLERS.get(key)
    
    if not handler:
        return {
            "status": "error",
            "message": f"Unknown query key: {key}",
            "options": []
        }
    
    try:
        options = await handler(
            db=db,
            entity=entity,
            field=field,
            form_state=form_state,
            static_params=static_params
        )
        
        return {
            "status": "success",
            "options": options
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Query execution failed: {str(e)}",
            "options": []
        }
