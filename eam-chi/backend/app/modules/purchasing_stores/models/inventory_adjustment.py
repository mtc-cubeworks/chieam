from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class InventoryAdjustment(BaseModel):
    """Inventory Adjustment entity model."""
    __tablename__ = "inventory_adjustment"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    source_stock_count: Mapped[str] = mapped_column(String(50), ForeignKey("stock_count.id"), nullable=True, default=None)
    reference_doctype: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    posting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    cost_center: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    remarks: Mapped[str] = mapped_column(Text, nullable=True, default=None)
