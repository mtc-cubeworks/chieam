from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class BaseModel(Base):
    """
    Abstract base model with common fields.
    
    All entities inherit from this to get:
    - id: Human-readable naming code (e.g., AST-0001) - set by NamingService
    - created_at: Auto-set on insert
    - updated_at: Auto-updated on every change
    - created_by: User ID of record creator (set by CRUD handler)
    - modified_by: User ID of last modifier (set by CRUD handler)
    
    Note: id is NOT auto-generated here. It must be set by NamingService
    before insert based on the entity's naming configuration.
    """
    __abstract__ = True
    
    # ID is the naming code (e.g., AST-0001), NOT a UUID
    # Must be set before insert by NamingService
    id: Mapped[str] = mapped_column(
        String(50), 
        primary_key=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )

    created_by: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        index=True
    )

    modified_by: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        index=True
    )
