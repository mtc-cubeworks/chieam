from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class SalesOrderItem(BaseModel):
    """Sales Order Item entity model."""
    __tablename__ = "sales_order_item"
    
    sales_order: Mapped[str] = mapped_column(String(50), ForeignKey("sales_order.id"), nullable=True, default=None)
    row_no: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
