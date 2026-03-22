from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class VendorInvoice(BaseModel):
    """Vendor Invoice entity for 3-way matching (PO-1)."""
    __tablename__ = "vendor_invoice"

    workflow_state: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=False)
    purchase_order: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_order.id"), nullable=True, default=None)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    currency: Mapped[str] = mapped_column(String(50), ForeignKey("currency.id"), nullable=True, default=None)
    payment_terms: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    match_status: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    match_variance: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
