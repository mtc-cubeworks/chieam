from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ServiceContract(BaseModel):
    """External service agreement with SLAs, expiry dates, and renewal tracking."""
    __tablename__ = "service_contract"

    contract_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    contract_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Full Service, Parts Only, Labor Only
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    start_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    end_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    annual_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    sla_response_hours: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    sla_resolution_hours: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    renewal_terms: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
