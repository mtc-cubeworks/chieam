from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderEquipmentAssignment(BaseModel):
    """Work Order Equipment Assignment entity model."""
    __tablename__ = "work_order_equipment_assignment"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_equipment: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_equipment.id"), nullable=True, default=None)
    asset_class_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    hours_used: Mapped[float] = mapped_column(Float, nullable=True, default=None)
