from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class FailureAnalysis(BaseModel):
    """Root Cause Analysis (RCA) entity linked to a Work Order or Incident."""
    __tablename__ = "failure_analysis"

    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    category_of_failure: Mapped[str] = mapped_column(String(50), ForeignKey("category_of_failure.id"), nullable=True, default=None)
    cause_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    remedy_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    analysis_method: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # 5-Why, Fishbone, Fault Tree
    root_cause_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    contributing_factors: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    analyst: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
