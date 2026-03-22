from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class SalesOrder(BaseModel):
    """Sales Order entity model."""
    __tablename__ = "sales_order"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    currency: Mapped[str] = mapped_column(String(50), ForeignKey("currency.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
