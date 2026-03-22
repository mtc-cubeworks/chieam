from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LaborAvailabilityDetails(BaseModel):
    """Labor Availability Details entity model."""
    __tablename__ = "labor_availability_details"
    
    labor_availability: Mapped[str] = mapped_column(String(50), ForeignKey("labor_availability.id"), nullable=True, default=None)
    hour: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
