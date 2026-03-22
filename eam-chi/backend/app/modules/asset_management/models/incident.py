from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Incident(BaseModel):
    """Incident entity model."""
    __tablename__ = "incident"
    
    title: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    incident_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    incident_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    date_reported: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    reported_by: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    severity: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    immediate_action_taken: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    preventive_actions: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    closed_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
