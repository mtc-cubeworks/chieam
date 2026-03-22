from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Item(BaseModel):
    """Item entity model."""
    __tablename__ = "item"
    
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    item_class: Mapped[str] = mapped_column(String(50), ForeignKey("item_class.id"), nullable=True, default=None)
    item_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    abc_code: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    expense_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    inventory_adjustment_account: Mapped[str] = mapped_column(String(50), ForeignKey("inventory_adjustment.id"), nullable=True, default=None)
    primary_vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    uom: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    actual_qty_on_hand: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    reserved_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    is_serialized: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    inspection_required: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    is_equipment: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    # IV-1: Min-max levels
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    reorder_quantity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    maximum_stock: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    # IV-4: Lot tracking flag
    is_lot_tracked: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    # IV-6: Cycle count frequency
    cycle_count_frequency: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
