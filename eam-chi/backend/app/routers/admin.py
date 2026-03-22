"""
Admin Router - Aggregates all admin sub-routers
"""

from fastapi import APIRouter

from .routers.users import router as users_router
from .routers.roles import router as roles_router
from .routers.permissions import router as permissions_router
from .routers.ordering import router as ordering_router
from .routers.model_editor import router as model_editor_router

router = APIRouter(prefix="/admin", tags=["admin"])

# Include all sub-routers
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(roles_router, prefix="/roles", tags=["roles"])
router.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
router.include_router(ordering_router, prefix="/ordering", tags=["ordering"])
router.include_router(model_editor_router, prefix="/model-editor", tags=["model-editor"])
