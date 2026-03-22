from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceInterval(BaseModel):
    """Maintenance Interval entity model."""
    __tablename__ = "maintenance_interval"
    
    planned_maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("planned_maintenance_activity.id"), nullable=True, default=None)
    maintenance_plan: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_plan.id"), nullable=True, default=None)
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    lead_interval: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    interval: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    interval_unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    running_interval_property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
    last_interval_property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
