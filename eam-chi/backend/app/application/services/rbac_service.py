"""
RBAC Service (Application Layer)
==================================
Permission checking orchestration.
Delegates DB access to AuthRepository.
"""
from typing import Any, Optional


class RBACAppService:
    """Application-layer RBAC that delegates to repository."""

    def __init__(self, auth_repo):
        self.auth_repo = auth_repo
        self._cache: dict[str, dict[str, bool]] = {}

    async def check_permission(
        self,
        user_id: str,
        entity: str,
        action: str,
        role_ids: Optional[list[str]] = None,
        is_superuser: bool = False,
    ) -> bool:
        if is_superuser:
            return True

        if not role_ids:
            return False

        # Check cache first
        for role_id in role_ids:
            cache_key = f"{role_id}:{entity}"
            if cache_key in self._cache:
                perms = self._cache[cache_key]
                if perms.get(f"can_{action}"):
                    return True

        # Fall back to DB
        permissions = await self.auth_repo.get_entity_permissions(role_ids, entity)
        for perm in permissions:
            if action == "read" and perm.can_read:
                return True
            if action == "create" and perm.can_create:
                return True
            if action == "update" and perm.can_update:
                return True
            if action == "delete" and perm.can_delete:
                return True

        return False

    async def load_cache(self, role_ids: list[str]):
        """Pre-load permissions into cache for performance."""
        permissions = await self.auth_repo.get_entity_permissions(role_ids)
        for perm in permissions:
            for role_id in role_ids:
                cache_key = f"{role_id}:{perm.entity_name}"
                self._cache[cache_key] = {
                    "can_read": perm.can_read,
                    "can_create": perm.can_create,
                    "can_update": perm.can_update,
                    "can_delete": perm.can_delete,
                }

    def clear_cache(self):
        self._cache.clear()
