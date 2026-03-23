"""
Roles Router
============
Role management endpoints.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import ValidationError

from app.core.database import get_db
from app.core.security import get_current_user_from_token, CurrentUser
from app.models.auth import User, Role
from app.models.workflow import WorkflowState, WorkflowTransition
from app.schemas.role import RoleCreate, RoleUpdate
from app.schemas.base import ActionResponse
from .common import api_response

router = APIRouter(tags=["admin-roles"])


@router.get("/meta/role")
async def get_role_metadata(current_user: CurrentUser = Depends(get_current_user_from_token)):
    """Get metadata for Role entity."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    return api_response(
        status="success",
        message="Role metadata retrieved",
        data={
            "entity": "role",
            "label": "Role",
            "title_field": "name",
            "fields": [
                {
                    "name": "name",
                    "label": "Name",
                    "field_type": "string",
                    "required": True,
                    "readonly": False,
                    "max_length": 100,
                },
                {
                    "name": "description",
                    "label": "Description",
                    "field_type": "text",
                    "required": False,
                    "readonly": False,
                    "max_length": 500,
                },
                {
                    "name": "is_active",
                    "label": "Active",
                    "field_type": "boolean",
                    "required": False,
                    "readonly": False,
                    "default": True,
                },
            ],
        },
    )


@router.get("/workflow/states")
async def list_workflow_states(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowState).order_by(WorkflowState.sort_order.asc()))
    states = result.scalars().all()
    return api_response(
        status="success",
        message="Workflow states retrieved successfully",
        data=[
            {
                "id": s.id,
                "name": s.name,
                "label": s.label,
                "is_terminal": 1 if s.is_terminal else 0,
            }
            for s in states
        ],
    )


@router.get("/workflow/transitions")
async def list_workflow_transitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkflowTransition)
        .options(selectinload(WorkflowTransition.from_state), selectinload(WorkflowTransition.to_state))
    )
    transitions = result.scalars().all()
    return api_response(
        status="success",
        message="Workflow transitions retrieved successfully",
        data=[
            {
                "id": t.id,
                "from_state": t.from_state.name if t.from_state else "",
                "action": t.action,
                "action_label": t.label,
                "to_state": t.to_state.name if t.to_state else "",
            }
            for t in transitions
        ],
    )


@router.post("/workflow/save")
async def save_workflow_config(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_from_token),
):
    """
    Save workflow transitions for an entity.
    Payload: {
        "entity": "purchase_order",
        "transitions": [
            {"from_state": "Draft", "action": "Submit", "to_state": "Pending Approval", "allowed_roles": ["PurchaseManager"]},
            ...
        ]
    }
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied: Superuser required")

    entity = payload.get("entity")
    transitions_data = payload.get("transitions", [])
    if not entity:
        return ActionResponse(status="error", message="entity is required")

    from app.models.workflow import Workflow, WorkflowTransition, WorkflowState, WorkflowAction
    import uuid as uuid_mod

    # Find or create the Workflow for this entity
    result = await db.execute(select(Workflow).where(Workflow.target_entity == entity))
    workflow = result.scalar_one_or_none()
    if not workflow:
        workflow = Workflow(
            id=str(uuid_mod.uuid4()),
            name=f"{entity} workflow",
            target_entity=entity,
            is_active=True,
        )
        db.add(workflow)
        await db.flush()

    # Load all states and actions for lookup
    states_result = await db.execute(select(WorkflowState))
    states_by_name = {s.label: s for s in states_result.scalars().all()}
    # Also match by slug
    for s in list(states_by_name.values()):
        if s.slug:
            states_by_name[s.slug] = s

    actions_result = await db.execute(select(WorkflowAction))
    actions_by_label = {a.label: a for a in actions_result.scalars().all()}
    for a in list(actions_by_label.values()):
        if a.slug:
            actions_by_label[a.slug] = a

    # Delete existing transitions for this workflow
    existing = await db.execute(
        select(WorkflowTransition).where(WorkflowTransition.workflow_id == workflow.id)
    )
    for t in existing.scalars().all():
        await db.delete(t)
    await db.flush()

    # Create new transitions
    created = []
    for idx, t_data in enumerate(transitions_data):
        from_name = t_data.get("from_state", "")
        action_name = t_data.get("action", "")
        to_name = t_data.get("to_state", "")
        allowed_roles = t_data.get("allowed_roles")

        from_state = states_by_name.get(from_name)
        to_state = states_by_name.get(to_name)
        action_obj = actions_by_label.get(action_name)

        if not from_state or not to_state or not action_obj:
            missing = []
            if not from_state:
                missing.append(f"state '{from_name}'")
            if not to_state:
                missing.append(f"state '{to_name}'")
            if not action_obj:
                missing.append(f"action '{action_name}'")
            return ActionResponse(
                status="error",
                message=f"Row {idx + 1}: not found: {', '.join(missing)}",
            )

        new_t = WorkflowTransition(
            id=str(uuid_mod.uuid4()),
            workflow_id=workflow.id,
            from_state_id=from_state.id,
            action_id=action_obj.id,
            to_state_id=to_state.id,
            sort_order=idx,
        )
        if allowed_roles:
            new_t.set_allowed_roles(allowed_roles)
        db.add(new_t)
        created.append({
            "from_state": from_name,
            "action": action_name,
            "to_state": to_name,
        })

    await db.commit()
    return ActionResponse(
        status="success",
        message=f"Saved {len(created)} transitions for '{entity}'",
    )


@router.get("/roles")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_from_token)
):
    """List all roles with their permissions."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied: Superuser required")
    
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions))
    )
    roles = result.scalars().all()
    
    return api_response(
        status="success",
        message="Roles retrieved successfully",
        data=[
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_active": r.is_active,
                "permissions": [
                    {
                        "id": p.id,
                        "entity_name": p.entity_name,
                        "can_read": p.can_read,
                        "can_create": p.can_create,
                        "can_update": p.can_update,
                        "can_delete": p.can_delete,
                        "in_sidebar": p.in_sidebar,
                    }
                    for p in r.permissions
                ],
            }
            for r in roles
        ]
    )


@router.post("/roles")
async def create_role(
    role_data: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_from_token)
):
    """Create a new role."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied: Superuser required")
    
    try:
        validated_data = RoleCreate(**role_data)
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            errors[field] = error['msg']
        return api_response(
            status="error",
            message="Validation failed",
            data={"errors": errors}
        )
    
    existing = await db.execute(
        select(Role).where(Role.name == validated_data.name)
    )
    if existing.scalar_one_or_none():
        return api_response(
            status="error",
            message="Role name already exists",
            data={"errors": {"name": "Role name already exists"}}
        )
    
    role = Role(
        name=validated_data.name,
        description=validated_data.description or "",
        is_active=validated_data.is_active,
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return api_response(
        status="success",
        message="Role created successfully",
        data={
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
        }
    )


@router.put("/roles/{role_id}")
async def update_role(
    role_id: str,
    role_data: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_from_token)
):
    """Update a role."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied: Superuser required")
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        return api_response(status="error", message="Role not found")
    
    if role.name == "SystemManager":
        return api_response(
            status="error",
            message="Cannot modify SystemManager role"
        )
    
    try:
        validated_data = RoleUpdate(**role_data)
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            errors[field] = error['msg']
        return api_response(
            status="error",
            message="Validation failed",
            data={"errors": errors}
        )
    
    if validated_data.name is not None:
        existing = await db.execute(
            select(Role).where(Role.name == validated_data.name).where(Role.id != role_id)
        )
        if existing.scalar_one_or_none():
            return api_response(
                status="error",
                message="Role name already exists",
                data={"errors": {"name": "Role name already exists"}}
            )
        role.name = validated_data.name
    if validated_data.description is not None:
        role.description = validated_data.description
    if validated_data.is_active is not None:
        role.is_active = validated_data.is_active
    
    await db.commit()
    
    return api_response(
        status="success",
        message="Role updated successfully",
        data={
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
        }
    )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user_from_token)
):
    """Delete a role."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied: Superuser required")
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        return api_response(status="error", message="Role not found")
    
    if role.name == "SystemManager":
        return api_response(
            status="error",
            message="Cannot delete SystemManager role"
        )
    
    users_with_role = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.roles.any(Role.id == role_id))
    )
    if users_with_role.scalar_one_or_none():
        return api_response(
            status="error",
            message="Cannot delete role that is assigned to users"
        )
    
    await db.delete(role)
    await db.commit()
    
    return api_response(
        status="success",
        message="Role deleted successfully"
    )
