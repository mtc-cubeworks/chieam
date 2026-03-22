from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceEquipment(BaseModel):
    """Maintenance Equipment entity model."""
    __tablename__ = "maintenance_equipment"
    
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    required_qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    required_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
