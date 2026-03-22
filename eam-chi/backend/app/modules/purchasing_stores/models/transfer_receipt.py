from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class TransferReceipt(BaseModel):
    """Transfer Receipt entity model."""
    __tablename__ = "transfer_receipt"
    
    transfer_request: Mapped[str] = mapped_column(String(50), ForeignKey("transfer.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    date_received: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    receiving_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
