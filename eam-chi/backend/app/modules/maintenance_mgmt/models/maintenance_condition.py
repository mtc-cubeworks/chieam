from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceCondition(BaseModel):
    """Maintenance Condition entity model."""
    __tablename__ = "maintenance_condition"
    
    planned_maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("planned_maintenance_activity.id"), nullable=True, default=None)
    maintenance_plan: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_plan.id"), nullable=True, default=None)
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    sensor: Mapped[str] = mapped_column(String(50), ForeignKey("sensor.id"), nullable=True, default=None)
    uom_short_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    property_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    comparison_operator: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    threshold_property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
