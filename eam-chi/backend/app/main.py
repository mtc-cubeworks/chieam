import time
import logging
from contextlib import asynccontextmanager
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.config import settings
from app.core.database import init_db, async_session_maker
from app.core.seed import run_seeds
from app.core.loader import load_modules
from app.core.exceptions import register_exception_handlers
from app.entities import load_all_entities
from app.infrastructure.rate_limit import limiter
from app.routers import meta
from app.services.socketio_manager import sio

# Configure slow_queries logger
logging.getLogger("slow_queries").setLevel(logging.WARNING)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        if duration > 0.5:  # log anything over 500ms
            print(f"SLOW REQUEST: {request.method} {request.url.path} took {duration*1000:.0f}ms")
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Security: reject default SECRET_KEY in production (PostgreSQL)
    if "postgresql" in settings.DATABASE_URL and settings.SECRET_KEY == "your-secret-key-change-in-production":
        raise RuntimeError(
            "SECURITY: SECRET_KEY is still set to the default value. "
            "Set a strong SECRET_KEY in your .env file before running in production."
        )

    # Load all module models (dynamic)
    load_modules()
    # Load entity metadata
    load_all_entities()
    
    # Register core models with the entity repository
    from app.infrastructure.database.repositories.entity_repository import register_core_models
    register_core_models()
    
    # Server actions and hooks are now auto-discovered by the module loader
    # via hooks.py register_hooks() in each module
    
    # Core models (auth, workflow) are registered by register_core_models()
    
    await init_db()
    if settings.RUN_SEEDS:
        async with async_session_maker() as db:
            await run_seeds(db)
    
    # Start APScheduler for PM calendar auto-generation
    from app.services.scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    
    yield
    
    # Shutdown scheduler on app exit
    stop_scheduler()


fastapi_app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Register custom exception handlers
register_exception_handlers(fastapi_app)

# Rate limiting
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
fastapi_app.add_middleware(SlowAPIMiddleware)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
)

fastapi_app.add_middleware(TimingMiddleware)
fastapi_app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# New Clean Architecture routes
from app.api.routes import entity_crud, entity_list, entity_options, entity_workflow, entity_actions, entity_attachments, entity_audit, entity_print, entity_tree, entity_children, entity_prefill, entity_fetch_from
from app.api.features import diagram, pm_calendar
from app.api.routes import reports as reports_router
from app.api.routes import profile as profile_router
from app.api.routes import branding_settings as branding_settings_router
from app.api.routes import email_notifications as email_notifications_router
from app.api.routes import setup as setup_router
from app.api.routes import dashboard as dashboard_router

# Legacy routes (to be migrated in future phases)
from app.routers.admin import router as admin_router
from app.routers import auth, workflow, import_export

# Register routes - Clean Architecture routes first
fastapi_app.include_router(meta.router, prefix=settings.API_PREFIX)

# New entity routes (Clean Architecture)
fastapi_app.include_router(entity_crud.router, prefix="/api/entity")
fastapi_app.include_router(entity_list.router, prefix="/api/entity")
fastapi_app.include_router(entity_options.router, prefix="/api/entity")
fastapi_app.include_router(entity_workflow.router, prefix="/api/entity")
fastapi_app.include_router(entity_actions.router, prefix="/api/entity")
fastapi_app.include_router(entity_attachments.router, prefix="/api/entity")
fastapi_app.include_router(entity_audit.router, prefix="/api/entity")
fastapi_app.include_router(entity_print.router, prefix="/api/entity")
fastapi_app.include_router(entity_tree.router, prefix="/api/entity")
fastapi_app.include_router(entity_children.router, prefix="/api/entity")
fastapi_app.include_router(entity_prefill.router, prefix="/api/entity")
fastapi_app.include_router(entity_fetch_from.router, prefix="/api/entity")

# Feature routes
fastapi_app.include_router(diagram.router, prefix="/api/features")
fastapi_app.include_router(pm_calendar.router, prefix="/api/features")
fastapi_app.include_router(reports_router.router, prefix="/api")
fastapi_app.include_router(profile_router.router, prefix="/api")
fastapi_app.include_router(branding_settings_router.router, prefix="/api")
fastapi_app.include_router(email_notifications_router.router, prefix="/api")
fastapi_app.include_router(setup_router.router, prefix="/api")
fastapi_app.include_router(dashboard_router.router, prefix="/api")

# Test routes (for development/testing)
from app.api import test_scheduler
fastapi_app.include_router(test_scheduler.router, prefix="/api")

# Legacy routes (will be migrated to Clean Architecture in future)
fastapi_app.include_router(admin_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(auth.router, prefix=settings.API_PREFIX)
fastapi_app.include_router(workflow.router, prefix=settings.API_PREFIX)
fastapi_app.include_router(import_export.router, prefix=settings.API_PREFIX)


@fastapi_app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@fastapi_app.get("/health")
async def health():
    from sqlalchemy import text
    from app.core.database import async_session_maker

    db_ok = False
    db_version = None
    try:
        async with async_session_maker() as session:
            row = await session.execute(text("SELECT version()"))
            db_version = row.scalar()
            db_ok = True
    except Exception as e:
        db_version = str(e)

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": {"connected": db_ok, "version": db_version},
    }


app = socketio.ASGIApp(sio, fastapi_app)
