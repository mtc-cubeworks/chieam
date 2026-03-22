from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PurchaseRequestLine(BaseModel):
    """Purchase Request Line entity model."""
    __tablename__ = "purchase_request_line"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    purchase_request: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request.id"), nullable=True, default=None)
    financial_asset_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    row_no: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    base_currency: Mapped[str] = mapped_column(String(50), ForeignKey("currency.id"), nullable=True, default=None)
    qty_required: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    total_line_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    account_code: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    po_num: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_required: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    qty_received: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    base_currency_unit: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    base_currency_line_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    conversion_factor: Mapped[float] = mapped_column(Float, nullable=True, default=None)
