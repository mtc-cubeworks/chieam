from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PurchaseRequest(BaseModel):
    """Purchase Request entity model."""
    __tablename__ = "purchase_request"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None, index=True)
    date_requested: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    requestor: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    pr_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    work_activity_id: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    maintenance_request: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_request.id"), nullable=True, default=None)
    reject_reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None, index=True)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None, index=True)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    # PQ-1: Budget / cost center validation
    budget_code: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    budget_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
