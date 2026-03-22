from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class RfqLine(BaseModel):
    """RFQ Line entity model."""
    __tablename__ = "rfq_line"
    
    rfq_id: Mapped[str] = mapped_column(String(50), ForeignKey("request_for_quotation.id"), nullable=True, default=None)
    pr_line: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request_line.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    item_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    price: Mapped[float] = mapped_column(Float, nullable=True, default=None)
