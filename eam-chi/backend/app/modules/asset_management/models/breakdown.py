from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Breakdown(BaseModel):
    """Breakdown entity model."""
    __tablename__ = "breakdown"
    
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    breakdown_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    start_time: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    end_time: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cause: Mapped[str] = mapped_column(Text, nullable=True, default=None)
