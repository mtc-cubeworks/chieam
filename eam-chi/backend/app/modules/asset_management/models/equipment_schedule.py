from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EquipmentSchedule(BaseModel):
    """Equipment Schedule entity model."""
    __tablename__ = "equipment_schedule"
    
    schedule_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    equipment_group: Mapped[str] = mapped_column(String(50), ForeignKey("equipment_group.id"), nullable=True, default=None)
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    start_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    end_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
