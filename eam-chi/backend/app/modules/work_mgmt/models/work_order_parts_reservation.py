from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderPartsReservation(BaseModel):
    """Work Order Parts Reservation entity model."""
    __tablename__ = "work_order_parts_reservation"
    
    work_order_parts: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_parts.id"), nullable=True, default=None)
    item_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    avail_quantity_data: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_reserved: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    quantity_reserved: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
