"""
Auth Repository
================
Concrete SQLAlchemy implementation for user/role data access.
"""
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import User, Role, EntityPermission


class AuthRepository:
    """Concrete auth repository backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def get_user_roles(self, user_id: str) -> list[str]:
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        if not user:
            return []
        return [role.name for role in user.roles]

    async def get_entity_permissions(
        self,
        role_ids: list[str],
        entity: Optional[str] = None,
    ) -> list[EntityPermission]:
        query = select(EntityPermission).where(EntityPermission.role_id.in_(role_ids))
        if entity:
            query = query.where(EntityPermission.entity_name == entity)
        result = await self.db.execute(query)
        return list(result.scalars().all())
