from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Currency(BaseModel):
    """Currency entity model."""
    __tablename__ = "currency"
    
    currency_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    symbol: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    conversion_factor: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
