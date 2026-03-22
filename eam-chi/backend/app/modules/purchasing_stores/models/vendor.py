from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Vendor(BaseModel):
    """Vendor entity model."""
    __tablename__ = "vendor"
    
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    # PO-3: Vendor performance tracking
    contact_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    contact_phone: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    address: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    vendor_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    delivery_rating: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    quality_rating: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    overall_rating: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    on_time_deliveries: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    rejected_deliveries: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
