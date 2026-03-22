from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderEquipment(BaseModel):
    """Work Order Equipment entity model."""
    __tablename__ = "work_order_equipment"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    work_order_activity_desc: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    equipment_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    total_hours_used: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
