"""
Setup Routes
=============
First-user setup wizard endpoints.
On a fresh install (no users in DB), allows creating the initial superuser
without authentication.
"""
import uuid
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.auth import User, Role

router = APIRouter(tags=["setup"])


class SetupAdminRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)


async def _has_users(db: AsyncSession) -> bool:
    """Check if any users exist in the database."""
    result = await db.execute(select(func.count()).select_from(User))
    return (result.scalar() or 0) > 0


@router.get("/setup/status")
async def setup_status(db: AsyncSession = Depends(get_db)):
    """Check if the system needs initial setup (no users exist)."""
    has_users = await _has_users(db)
    return {
        "is_setup_complete": has_users,
        "needs_setup": not has_users,
    }


@router.post("/setup/create-admin")
async def create_admin(
    data: SetupAdminRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create the first administrator account. Only works when no users exist."""
    if await _has_users(db):
        raise HTTPException(
            status_code=403,
            detail="Setup already completed. An administrator account already exists.",
        )

    # Ensure the SystemManager role exists
    role_result = await db.execute(select(Role).where(Role.name == "SystemManager"))
    role = role_result.scalar_one_or_none()
    if not role:
        role = Role(
            id=str(uuid.uuid4()),
            name="SystemManager",
            description="Full system access",
            is_active=True,
        )
        db.add(role)
        await db.flush()

    # Create the superuser
    user = User(
        id=str(uuid.uuid4()),
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        first_name=data.full_name.split()[0] if " " in data.full_name else data.full_name,
        last_name=data.full_name.split()[-1] if " " in data.full_name else "",
        hashed_password=get_password_hash(data.password),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    await db.flush()

    # Assign SystemManager role
    user.roles.append(role)
    await db.commit()

    return {
        "status": "success",
        "message": "Administrator account created successfully. You can now log in.",
        "data": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        },
    }
