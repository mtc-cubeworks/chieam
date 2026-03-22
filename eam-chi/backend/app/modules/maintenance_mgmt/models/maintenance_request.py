from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceRequest(BaseModel):
    """Maintenance Request entity model."""
    __tablename__ = "maintenance_request"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    requestor: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    requested_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    priority: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    request_type: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    position: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
    planned_maintenance_activity: Mapped[str] = mapped_column(String(50), ForeignKey("planned_maintenance_activity.id"), nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    next_maintenance_request: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_request.id"), nullable=True, default=None)
    closed_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
    maintenance_interval_property: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_interval.id"), nullable=True, default=None)
    running_interval_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
