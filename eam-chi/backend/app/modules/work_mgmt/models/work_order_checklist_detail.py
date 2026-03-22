from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderChecklistDetail(BaseModel):
    """Work Order Checklist Detail entity model."""
    __tablename__ = "work_order_checklist_detail"
    
    work_order_checklist: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_checklist.id"), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    remarks: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
