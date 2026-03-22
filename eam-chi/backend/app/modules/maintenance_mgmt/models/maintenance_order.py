from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceOrder(BaseModel):
    """Maintenance Order entity model."""
    __tablename__ = "maintenance_order"
    
    created_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
