from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class CorrectiveAction(BaseModel):
    """Corrective/Preventive Action (CAPA) tracking linked to a Failure Analysis."""
    __tablename__ = "corrective_action"

    failure_analysis: Mapped[str] = mapped_column(String(50), ForeignKey("failure_analysis.id"), nullable=True, default=None)
    action_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Corrective, Preventive, Containment
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    priority: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    completion_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    verification_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    verified_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    verification_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
