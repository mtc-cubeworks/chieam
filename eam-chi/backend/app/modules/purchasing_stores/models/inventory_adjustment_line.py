from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class InventoryAdjustmentLine(BaseModel):
    """Inventory Adjustment Line entity model."""
    __tablename__ = "inventory_adjustment_line"
    
    inventory_adjustment: Mapped[str] = mapped_column(String(50), ForeignKey("inventory_adjustment.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    asset_tag: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    serial_nos: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
    uom: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    current_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    adjusted_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    current_rate: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    delta_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    inventory_adjustment_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    inventory_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
