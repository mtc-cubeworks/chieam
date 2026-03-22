from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class SystemType(BaseModel):
    """System Type entity model."""
    __tablename__ = "system_type"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
