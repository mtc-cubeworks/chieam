from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class VendorInvoiceLine(BaseModel):
    """Vendor Invoice Line for 3-way matching against PO lines and GR."""
    __tablename__ = "vendor_invoice_line"

    vendor_invoice: Mapped[str] = mapped_column(String(50), ForeignKey("vendor_invoice.id"), nullable=False)
    purchase_order_line: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_order_line.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    quantity_invoiced: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    line_total: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    row_number: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    match_status: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
