from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class IncidentEmployee(BaseModel):
    """Incident Employee entity model."""
    __tablename__ = "incident_employee"
    
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
    employee: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    role_in_incident: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    injured: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    injury_severity: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    injury_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    ppe_used: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    treatment: Mapped[str] = mapped_column(Text, nullable=True, default=None)
