from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class StockLedgerEntry(BaseModel):
    """Stock Ledger Entry entity model."""
    __tablename__ = "stock_ledger_entry"
    
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    serial_no: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    posting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    qty_in: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    qty_out: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    value_in: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    value_out: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    balance_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    balance_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    voucher_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    voucher_no: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
