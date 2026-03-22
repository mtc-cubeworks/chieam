from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceParts(BaseModel):
    """Maintenance Parts entity model."""
    __tablename__ = "maintenance_parts"
    
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
