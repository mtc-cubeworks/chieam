from datetime import date
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PurchaseReceipt(BaseModel):
    """Purchase Receipt entity model."""
    __tablename__ = "purchase_receipt"
    
    purchase_order_line: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_order_line.id"), nullable=True, default=None)
    purchase_request_line: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request_line.id"), nullable=True, default=None)
    pr_row_no: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    is_received: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    date_received: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    receiving_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    generated_inventory: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    account_code: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
