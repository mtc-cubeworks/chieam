from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderEquipmentActualHours(BaseModel):
    """Work Order Equipment Actual Hours entity model."""
    __tablename__ = "work_order_equipment_actual_hours"
    
    wo_equip_id: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_equipment.id"), nullable=True, default=None)
    date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    hour: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    comment: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
