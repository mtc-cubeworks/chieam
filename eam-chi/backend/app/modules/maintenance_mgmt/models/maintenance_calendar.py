from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceCalendar(BaseModel):
    """Maintenance Calendar entity model."""
    __tablename__ = "maintenance_calendar"
    
    planned_maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("planned_maintenance_activity.id"), nullable=True, default=None)
    maintenance_plan: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_plan.id"), nullable=True, default=None)
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    frequency: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    lead_calendar_days: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    last_maintenance_date_property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
