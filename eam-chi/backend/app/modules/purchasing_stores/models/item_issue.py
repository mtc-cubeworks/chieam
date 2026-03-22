from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ItemIssue(BaseModel):
    """Item Issue entity model."""
    __tablename__ = "item_issue"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    issue_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    issue_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    date_issued: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    # PI-1: WO linkage enforcement
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    # PI-3: Direct issue vs. storeroom distinction
    issue_destination: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    require_wo: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
