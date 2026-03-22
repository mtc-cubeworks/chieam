from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Rfqline(BaseModel):
    """RFQ Line entity model."""
    __tablename__ = "RfqLine"
    
    rfq_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    pr_line: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    item_description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    quantity: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    price: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
