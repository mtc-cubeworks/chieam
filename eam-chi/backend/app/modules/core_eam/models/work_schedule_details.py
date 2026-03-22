from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkScheduleDetails(BaseModel):
    """Work Schedule Details entity model."""
    __tablename__ = "work_schedule_details"
    
    work_schedule: Mapped[str] = mapped_column(String(50), ForeignKey("work_schedule.id"), nullable=True, default=None)
    day: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    start_time: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    end_time: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_working: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
