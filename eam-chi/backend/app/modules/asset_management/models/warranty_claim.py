from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WarrantyClaim(BaseModel):
    """Warranty claim tracking per asset against a vendor."""
    __tablename__ = "warranty_claim"

    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    claim_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    warranty_start: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    warranty_end: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    failure_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    claim_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    credited_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    vendor_reference: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
