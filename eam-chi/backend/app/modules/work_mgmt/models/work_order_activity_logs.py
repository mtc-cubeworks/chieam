from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderActivityLogs(BaseModel):
    """Work Order Activity Logs entity model."""
    __tablename__ = "work_order_activity_logs"
    
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    work_order_activity_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    log: Mapped[str] = mapped_column(Text, nullable=True, default=None)
