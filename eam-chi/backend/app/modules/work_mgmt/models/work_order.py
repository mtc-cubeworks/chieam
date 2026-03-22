from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrder(BaseModel):
    """Work Order entity model."""
    __tablename__ = "work_order"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    category_of_failure: Mapped[str] = mapped_column(String(50), ForeignKey("category_of_failure.id"), nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    priority: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    severity: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    # Downtime Tracking (WO-6)
    downtime_start: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    downtime_end: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    downtime_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    # Failure Analysis (WO-7)
    cause_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    remedy_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    failure_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
