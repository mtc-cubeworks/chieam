from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PurchaseOrderLine(BaseModel):
    """Purchase Order Line entity model."""
    __tablename__ = "purchase_order_line"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None, index=True)
    po_id: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_order.id"), nullable=True, default=None, index=True)
    pr_line_id: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request_line.id"), nullable=True, default=None)
    line_row_num: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    financial_asset_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item_id: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None, index=True)
    item_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    quantity_ordered: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    price: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
