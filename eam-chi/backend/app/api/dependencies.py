"""
API Dependencies
=================
FastAPI Depends() factories for injecting application services.
Wires infrastructure implementations to application-layer services.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Infrastructure
from app.infrastructure.database.repositories.entity_repository import EntityRepository
from app.infrastructure.database.repositories.auth_repository import AuthRepository
from app.infrastructure.database.repositories.workflow_repository import WorkflowRepository
from app.infrastructure.database.repositories.naming_repository import NamingRepository
from app.infrastructure.database.repositories.fetch_from_repository import FetchFromRepository
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.password_service import PasswordService
from app.services.socketio_manager import socket_manager

# Application services
from app.application.services.entity_service import EntityService
from app.application.services.auth_service import AuthService
from app.application.services.rbac_service import RBACAppService
from app.application.services.workflow_service import WorkflowAppService
from app.application.services.fetch_from_service import FetchFromService


# ---------------------------------------------------------------------------
# Repository factories
# ---------------------------------------------------------------------------

def get_entity_repo(db: AsyncSession = Depends(get_db)) -> EntityRepository:
    return EntityRepository(db)


def get_auth_repo(db: AsyncSession = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_workflow_repo(db: AsyncSession = Depends(get_db)) -> WorkflowRepository:
    return WorkflowRepository(db)


def get_naming_repo(db: AsyncSession = Depends(get_db)) -> NamingRepository:
    return NamingRepository(db)


def get_fetch_from_repo(db: AsyncSession = Depends(get_db)) -> FetchFromRepository:
    return FetchFromRepository(db)


# ---------------------------------------------------------------------------
# Infrastructure service singletons
# ---------------------------------------------------------------------------

_jwt_service = JWTService()
_password_service = PasswordService()


def get_jwt_service() -> JWTService:
    return _jwt_service


def get_password_service() -> PasswordService:
    return _password_service


# ---------------------------------------------------------------------------
# Application service factories
# ---------------------------------------------------------------------------

def get_entity_service(
    entity_repo: EntityRepository = Depends(get_entity_repo),
    naming_repo: NamingRepository = Depends(get_naming_repo),
    workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> EntityService:
    rbac = RBACAppService(auth_repo)
    return EntityService(
        entity_repo=entity_repo,
        naming_repo=naming_repo,
        rbac_service=rbac,
        workflow_repo=workflow_repo,
        socket_manager=socket_manager,
    )


def get_auth_service(
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> AuthService:
    return AuthService(
        auth_repo=auth_repo,
        jwt_service=_jwt_service,
        password_service=_password_service,
    )


def get_rbac_service(
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> RBACAppService:
    return RBACAppService(auth_repo)


def get_workflow_service(
    workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
    entity_repo: EntityRepository = Depends(get_entity_repo),
) -> WorkflowAppService:
    return WorkflowAppService(workflow_repo=workflow_repo, entity_repo=entity_repo)


def get_fetch_from_service(
    repo: FetchFromRepository = Depends(get_fetch_from_repo),
) -> FetchFromService:
    return FetchFromService(repo)


# ---------------------------------------------------------------------------
# Email Notification service factory
# ---------------------------------------------------------------------------

def get_email_notification_service():
    """Factory for EmailNotificationService with infrastructure wired."""
    from app.infrastructure.email.smtp_service import SmtpEmailService
    from app.infrastructure.email.template_renderer import JinjaEmailTemplateRenderer
    from app.application.services.email_notification_service import EmailNotificationService

    return EmailNotificationService(
        email_service=SmtpEmailService(),
        template_renderer=JinjaEmailTemplateRenderer(),
    )


# ---------------------------------------------------------------------------
# Metadata Sync service factory
# ---------------------------------------------------------------------------

def get_metadata_sync_service():
    """Factory for MetadataSyncService with all infrastructure adapters wired."""
    from app.infrastructure.metadata.adapters import (
        JsonMetadataReader,
        JsonMetadataWriter,
        MetadataValidator,
        MetadataChangeAnalyzer,
        ModelGeneratorAdapter,
        MigrationManagerAdapter,
        RegistryManagerAdapter,
    )
    from app.application.services.metadata_sync_service import MetadataSyncService

    reader = JsonMetadataReader()
    return MetadataSyncService(
        reader=reader,
        writer=JsonMetadataWriter(reader),
        validator=MetadataValidator(),
        analyzer=MetadataChangeAnalyzer(reader),
        model_generator=ModelGeneratorAdapter(),
        migration_manager=MigrationManagerAdapter(),
        registry_manager=RegistryManagerAdapter(),
    )


# ---------------------------------------------------------------------------
# Legacy service factories (for gradual migration of routes to Depends())
# ---------------------------------------------------------------------------

def get_legacy_rbac(db: AsyncSession = Depends(get_db)):
    """Factory for legacy RBACService used in existing routes."""
    from app.services.rbac import RBACService
    return RBACService(db)


def get_legacy_naming(db: AsyncSession = Depends(get_db)):
    """Factory for legacy NamingService."""
    from app.services.naming import NamingService
    return NamingService


def get_legacy_workflow_db(db: AsyncSession = Depends(get_db)):
    """Factory for legacy WorkflowDBService."""
    from app.services.workflow import WorkflowDBService
    return WorkflowDBService(db)
