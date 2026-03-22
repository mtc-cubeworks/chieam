from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PurchaseOrder(BaseModel):
    """Purchase Order entity model."""
    __tablename__ = "purchase_order"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    source_rfq: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_ordered: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
