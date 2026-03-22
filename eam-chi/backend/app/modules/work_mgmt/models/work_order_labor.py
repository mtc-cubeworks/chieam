from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderLabor(BaseModel):
    """Work Order Labor entity model."""
    __tablename__ = "work_order_labor"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    work_order_activity_desc: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    trade: Mapped[str] = mapped_column(String(50), ForeignKey("trade.id"), nullable=True, default=None)
    trade_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    laborer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    lead: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    total_hours_used: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
