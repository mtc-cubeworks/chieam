from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Checklist(BaseModel):
    """Checklist entity model."""
    __tablename__ = "checklist"
    
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    checklist_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
