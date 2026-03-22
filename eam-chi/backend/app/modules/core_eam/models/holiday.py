from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Holiday(BaseModel):
    """Holiday entity model."""
    __tablename__ = "holiday"
    
    holiday_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    holiday_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    applicable_to_labor_grp: Mapped[str] = mapped_column(String(50), ForeignKey("labor_group.id"), nullable=True, default=None)
    specific_labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
