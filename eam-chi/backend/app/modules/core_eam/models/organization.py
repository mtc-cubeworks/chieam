from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Organization(BaseModel):
    """Organization entity model."""
    __tablename__ = "organization"
    
    organization_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    organizational_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
