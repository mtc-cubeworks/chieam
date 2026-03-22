from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Trade(BaseModel):
    """Trade entity model."""
    __tablename__ = "trade"
    
    trade_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    on_staff: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    licensed: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
