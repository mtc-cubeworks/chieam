"""
Admin Router Package
====================
Modular admin endpoints split into focused sub-routers.
"""
from fastapi import APIRouter

from .users import router as users_router
from .roles import router as roles_router
from .permissions import router as permissions_router
from .ordering import router as ordering_router
from .model_editor import router as model_editor_router

router = APIRouter(prefix="/admin", tags=["admin"])

# Include all sub-routers
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(permissions_router)
router.include_router(ordering_router)
router.include_router(model_editor_router)
