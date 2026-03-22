from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Meter(BaseModel):
    """Meter entity for tracking runtime hours, odometer, cycle counts on assets."""
    __tablename__ = "meter"

    meter_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    meter_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Runtime Hours, Odometer, Cycles, Production Count
    unit_of_measure: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Hours, km, cycles
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    last_reading: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    rollover_point: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
