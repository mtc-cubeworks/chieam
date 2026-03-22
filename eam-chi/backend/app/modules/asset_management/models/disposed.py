from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Disposed(BaseModel):
    """Disposed entity model."""
    __tablename__ = "disposed"
    
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    condition: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    disposal_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    disposal_reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    disposal_method: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    disposal_status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
