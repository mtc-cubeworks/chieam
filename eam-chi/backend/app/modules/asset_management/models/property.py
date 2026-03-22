from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Property(BaseModel):
    """Property entity model."""
    __tablename__ = "property"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    property_type: Mapped[str] = mapped_column(String(50), ForeignKey("property_type.id"), nullable=True, default=None)
    system: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    inactive: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
