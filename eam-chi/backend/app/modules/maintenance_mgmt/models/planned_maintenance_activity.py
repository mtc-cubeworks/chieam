from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PlannedMaintenanceActivity(BaseModel):
    """Planned Maintenance Activity entity model."""
    __tablename__ = "planned_maintenance_activity"
    
    maintenance_plan: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_plan.id"), nullable=True, default=None)
    maintenance_plan_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_activity.id"), nullable=True, default=None)
    maintenance_activity_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    checklist: Mapped[str] = mapped_column(String(50), ForeignKey("checklist.id"), nullable=True, default=None)
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    maintenance_schedule: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    maintenance_type: Mapped[str] = mapped_column(String(50), ForeignKey("request_activity_type.id"), nullable=True, default=None)
