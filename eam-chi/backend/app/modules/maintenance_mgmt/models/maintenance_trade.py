from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceTrade(BaseModel):
    """Maintenance Trade entity model."""
    __tablename__ = "maintenance_trade"
    
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    trade: Mapped[str] = mapped_column(String(50), ForeignKey("trade.id"), nullable=True, default=None)
    required_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    required_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
