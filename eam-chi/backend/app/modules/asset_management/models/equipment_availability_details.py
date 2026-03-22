from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EquipmentAvailabilityDetails(BaseModel):
    """Equipment Availability Details entity model."""
    __tablename__ = "equipment_availability_details"
    
    equipment_availability: Mapped[str] = mapped_column(String(50), ForeignKey("equipment_availability.id"), nullable=True, default=None)
    hour: Mapped[str] = mapped_column(String(20), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
