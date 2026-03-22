from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MeterReading(BaseModel):
    """Individual meter reading captured against an asset meter."""
    __tablename__ = "meter_reading"

    meter: Mapped[str] = mapped_column(String(50), ForeignKey("meter.id"), nullable=True, default=None)
    reading_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    reading_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    recorded_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
