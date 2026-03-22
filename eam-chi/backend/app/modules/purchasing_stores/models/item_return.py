from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ItemReturn(BaseModel):
    """Item Return entity model."""
    __tablename__ = "item_return"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    return_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    returned_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    date_returned: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    # PR-1: Return reason tracking
    return_reason: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    return_reason_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    # PR-2: Inspection on return
    inspection_required: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    inspection_status: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    inspection_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
