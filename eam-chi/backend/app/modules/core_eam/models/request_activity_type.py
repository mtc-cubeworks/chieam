from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class RequestActivityType(BaseModel):
    """Request Activity Type entity model."""
    __tablename__ = "request_activity_type"
    
    menu: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    role: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
