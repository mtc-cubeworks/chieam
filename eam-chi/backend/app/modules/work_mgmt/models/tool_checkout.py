from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ToolCheckout(BaseModel):
    """Tool / Equipment Checkout tracking (MW-14)."""
    __tablename__ = "tool_checkout"

    workflow_state: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    tool: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=False)
    checked_out_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    checkout_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    expected_return_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    actual_return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    condition_at_checkout: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    condition_at_return: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    calibration_due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
