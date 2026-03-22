from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EquipmentScheduleDetails(BaseModel):
    """Equipment Schedule Details entity model."""
    __tablename__ = "equipment_schedule_details"
    
    equipment_schedule: Mapped[str] = mapped_column(String(50), ForeignKey("equipment_schedule.id"), nullable=True, default=None)
    day: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    start_time: Mapped[str] = mapped_column(String(20), nullable=True, default=None)
    end_time: Mapped[str] = mapped_column(String(20), nullable=True, default=None)
    is_operating: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
