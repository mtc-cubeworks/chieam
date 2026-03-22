from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Location(BaseModel):
    """Location entity model."""
    __tablename__ = "location"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    location_type: Mapped[str] = mapped_column(String(50), ForeignKey("location_type.id"), nullable=True, default=None)
    location_type_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    parent_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    latitude: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    longitude: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    address: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
