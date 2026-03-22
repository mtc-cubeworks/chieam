from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LaborAvailability(BaseModel):
    """Labor Availability entity model."""
    __tablename__ = "labor_availability"
    
    labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    laborer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
