from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetClassAvailability(BaseModel):
    """Asset Class Availability entity model."""
    __tablename__ = "asset_class_availability"
    
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    specific_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    remaining_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    reserved_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
