from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ScheduledJobLog(BaseModel):
    """Scheduled Job Log entity model."""
    __tablename__ = "scheduled_job_log"
    
    job_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    job_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    records_created: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    details: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    trigger_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cron_expression: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
