"""
RBAC Service
============
Role-Based Access Control service for permission management.

Provides:
- Permission checking (sync and async)
- Permission caching for performance
- User/Role management helpers
- Workflow permission checks

Last Updated: 2026-01-29
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.security import CurrentUser
from app.meta.registry import EntityMeta
from app.models.auth import User, Role, EntityPermission
from app.infrastructure.cache.permission_cache import permission_cache


class RBACService:
    """RBAC enforcement using database permissions."""
    
    # =========================================================================
    # PERMISSION CHECKING
    # =========================================================================
    
    @staticmethod
    def check_permission(
        user: CurrentUser,
        entity: EntityMeta,
        action: str
    ) -> bool:
        """
        Check if user has permission for action on entity (sync, uses cache).
        
        Actions: read, create, update, delete
        
        Note: This is a synchronous check using cached permissions.
        For real-time checks, use check_permission_async.
        """
        if user.is_superuser:
            return True
        
        if "SystemManager" in user.roles:
            return True
        
        for role_id in user.role_ids:
            perms = permission_cache.get(role_id, entity.name)
            if perms:
                if action == "read" and perms.get("can_read"):
                    return True
                if action == "create" and perms.get("can_create"):
                    return True
                if action == "update" and perms.get("can_update"):
                    return True
                if action == "delete" and perms.get("can_delete"):
                    return True
                if action == "select" and perms.get("can_select"):
                    return True
                if action == "export" and perms.get("can_export"):
                    return True
                if action == "import" and perms.get("can_import"):
                    return True
        
        return False
    
    @staticmethod
    async def check_permission_async(
        db: AsyncSession,
        user: CurrentUser,
        entity_name: str,
        action: str
    ) -> bool:
        """
        Check permission asynchronously — uses in-memory TTL cache first,
        falls back to database query and populates cache on miss.
        
        Actions: read, create, update, delete, select, export, import
        """
        if user.is_superuser:
            return True
        
        if "SystemManager" in user.roles:
            return True
        
        _ACTION_KEY = {
            "read": "can_read", "create": "can_create",
            "update": "can_update", "delete": "can_delete",
            "select": "can_select", "export": "can_export",
            "import": "can_import",
        }
        perm_key = _ACTION_KEY.get(action)
        if not perm_key:
            return False

        for role_id in user.role_ids:
            # 1. Check TTL cache first (avoids DB round-trip)
            cached = permission_cache.get(role_id, entity_name)
            if cached is not None:
                if cached.get(perm_key):
                    return True
                continue  # cached but action not allowed for this role

            # 2. Cache miss — query DB and populate cache
            result = await db.execute(
                select(EntityPermission)
                .where(EntityPermission.role_id == role_id)
                .where(EntityPermission.entity_name == entity_name)
            )
            perm = result.scalar_one_or_none()
            
            if perm:
                perm_dict = {
                    "can_read": perm.can_read,
                    "can_create": perm.can_create,
                    "can_update": perm.can_update,
                    "can_delete": perm.can_delete,
                    "can_select": perm.can_select,
                    "can_export": perm.can_export,
                    "can_import": perm.can_import,
                }
                permission_cache.set(role_id, entity_name, perm_dict)
                if perm_dict.get(perm_key):
                    return True
            else:
                # Cache negative result too (no permission row exists)
                permission_cache.set(role_id, entity_name, {
                    "can_read": False, "can_create": False,
                    "can_update": False, "can_delete": False,
                    "can_select": False, "can_export": False,
                    "can_import": False,
                })
        
        return False
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    @staticmethod
    async def load_permissions_cache(db: AsyncSession, user: CurrentUser):
        """Load user's permissions into cache."""
        for role_id in user.role_ids:
            result = await db.execute(
                select(EntityPermission)
                .where(EntityPermission.role_id == role_id)
            )
            perms = result.scalars().all()
            
            for perm in perms:
                permission_cache.set(role_id, perm.entity_name, {
                    "can_read": perm.can_read,
                    "can_create": perm.can_create,
                    "can_update": perm.can_update,
                    "can_delete": perm.can_delete,
                    "can_select": perm.can_select,
                    "can_export": perm.can_export,
                    "can_import": perm.can_import,
                })
    
    @staticmethod
    def clear_cache():
        """Clear the permission cache."""
        permission_cache.clear()
    
    # =========================================================================
    # WORKFLOW PERMISSIONS
    # =========================================================================
    
    @staticmethod
    def check_workflow_permission(
        user: CurrentUser,
        entity: EntityMeta,
        current_state: str,
        action: str
    ) -> bool:
        """Check if user can perform workflow action from current state."""
        if "SystemManager" in user.roles:
            return True
        
        if not entity.workflow or not entity.workflow.enabled:
            return False
        
        state = entity.workflow.states.get(current_state)
        if not state:
            return False
        
        for wf_action in state.actions:
            if wf_action.name == action:
                if not wf_action.roles_allowed:
                    return True
                return any(role in wf_action.roles_allowed for role in user.roles)
        
        return False
    
    # =========================================================================
    # USER/ROLE HELPERS
    # =========================================================================
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username with roles loaded."""
        result = await db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: str) -> list[str]:
        """Get role names for a user."""
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        if not user:
            return []
        return [role.name for role in user.roles]
    
    @staticmethod
    async def get_all_permissions_for_role(db: AsyncSession, role_id: str) -> list[EntityPermission]:
        """Get all entity permissions for a role."""
        result = await db.execute(
            select(EntityPermission)
            .where(EntityPermission.role_id == role_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def set_permission(
        db: AsyncSession,
        role_id: str,
        entity_name: str,
        can_read: bool = False,
        can_create: bool = False,
        can_update: bool = False,
        can_delete: bool = False,
        can_select: bool = False,
        can_export: bool = False,
        can_import: bool = False,
    ) -> EntityPermission:
        """Set or update permission for a role on an entity."""
        result = await db.execute(
            select(EntityPermission)
            .where(EntityPermission.role_id == role_id)
            .where(EntityPermission.entity_name == entity_name)
        )
        perm = result.scalar_one_or_none()
        
        if perm:
            perm.can_read = can_read
            perm.can_create = can_create
            perm.can_update = can_update
            perm.can_delete = can_delete
            perm.can_select = can_select
            perm.can_export = can_export
            perm.can_import = can_import
        else:
            perm = EntityPermission(
                role_id=role_id,
                entity_name=entity_name,
                can_read=can_read,
                can_create=can_create,
                can_update=can_update,
                can_delete=can_delete,
                can_select=can_select,
                can_export=can_export,
                can_import=can_import,
            )
            db.add(perm)
        
        await db.commit()
        await db.refresh(perm)
        return perm


# Singleton instance for convenience
rbac_service = RBACService()

# Backwards compatibility aliases
RBACDBService = RBACService
rbac_db_service = rbac_service
