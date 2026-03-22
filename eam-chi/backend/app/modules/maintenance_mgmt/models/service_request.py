from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ServiceRequest(BaseModel):
    """Service Request entity model."""
    __tablename__ = "service_request"
    
    title: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    priority: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    date_reported: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    closed_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
