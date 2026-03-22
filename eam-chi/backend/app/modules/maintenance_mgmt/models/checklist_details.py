from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ChecklistDetails(BaseModel):
    """Checklist Details entity model."""
    __tablename__ = "checklist_details"
    
    checklist: Mapped[str] = mapped_column(String(50), ForeignKey("checklist.id"), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
