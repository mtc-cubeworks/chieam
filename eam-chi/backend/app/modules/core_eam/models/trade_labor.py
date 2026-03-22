from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class TradeLabor(BaseModel):
    """Trade Labor entity model."""
    __tablename__ = "trade_labor"
    
    trade: Mapped[str] = mapped_column(String(50), ForeignKey("trade.id"), nullable=True, default=None)
    labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    laborer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    primary: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
