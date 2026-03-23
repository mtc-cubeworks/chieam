from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class SafetyPermit(BaseModel):
    """Permit-to-Work entity for LOTO, hot work, confined space, etc."""
    __tablename__ = "safety_permit"

    permit_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # LOTO, Hot Work, Confined Space, Excavation
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    requested_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    approved_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    valid_to: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    hazards_identified: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    precautions: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    emergency_procedures: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
