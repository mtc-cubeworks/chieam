from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderParts(BaseModel):
    """Work Order Parts entity model."""
    __tablename__ = "work_order_parts"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    work_order_activity_desc: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    total_actual_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    total_avail_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    date_required: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    quantity_required: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    quantity_issued: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    quantity_returned: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
