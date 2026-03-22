from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
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
