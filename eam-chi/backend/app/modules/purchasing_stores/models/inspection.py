from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Inspection(BaseModel):
    """Inspection entity model."""
    __tablename__ = "inspection"
    
    inspection_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    inspector: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    inspection_result: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    action_required: Mapped[str] = mapped_column(Text, nullable=True, default=None)
