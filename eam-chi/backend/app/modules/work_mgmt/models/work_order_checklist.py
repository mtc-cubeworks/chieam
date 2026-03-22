from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderChecklist(BaseModel):
    """Work Order Checklist entity model."""
    __tablename__ = "work_order_checklist"
    
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    checklist: Mapped[str] = mapped_column(String(50), ForeignKey("checklist.id"), nullable=True, default=None)
    inspector_id: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    inspector_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    inspection_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    remarks: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
