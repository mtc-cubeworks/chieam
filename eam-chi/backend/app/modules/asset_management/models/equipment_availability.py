from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EquipmentAvailability(BaseModel):
    """Equipment Availability entity model."""
    __tablename__ = "equipment_availability"
    
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    equipment_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
