from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class StockCountLine(BaseModel):
    """Stock Count Line entity model."""
    __tablename__ = "stock_count_line"
    
    stock_count: Mapped[str] = mapped_column(String(50), ForeignKey("stock_count.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    asset_tag: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    serial_nos: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
    uom: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    snapshot_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    counted_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    variance_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    variance_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    variance_reason: Mapped[str] = mapped_column(String(50), ForeignKey("reason_code.id"), nullable=True, default=None)
    is_reconciled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
