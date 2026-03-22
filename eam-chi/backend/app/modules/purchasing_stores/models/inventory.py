from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Inventory(BaseModel):
    """Inventory entity model."""
    __tablename__ = "inventory"
    
    workflow_state: Mapped[str] = mapped_column(String(50), ForeignKey("workflow_states.id"), nullable=True, default=None)
    transaction_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    financial_asset_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    store_location: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
    bin_location: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    asset_tag: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    base_unit_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    actual_inv: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    available_inv: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    reserved_inv: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    freeze: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    warn: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
