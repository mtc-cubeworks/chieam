import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_number: Mapped[str] = mapped_column(String(50), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    site: Mapped[str] = mapped_column(String(100), nullable=True)
    employee_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)  # TEMP: required disabled
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )
    permissions: Mapped[list["EntityPermission"]] = relationship(
        "EntityPermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class EntityPermission(Base):
    __tablename__ = "entity_permissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("roles.id"), nullable=True)  # TEMP: required disabled
    entity_name: Mapped[str] = mapped_column(String(100), nullable=True)  # TEMP: required disabled
    can_read: Mapped[bool] = mapped_column(Boolean, default=False)
    can_create: Mapped[bool] = mapped_column(Boolean, default=False)
    can_update: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    can_select: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    can_export: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    can_import: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    in_sidebar: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")


__all__ = ["User", "Role", "EntityPermission", "user_roles"]
