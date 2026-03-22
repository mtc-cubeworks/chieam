from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LocationType(BaseModel):
    """Location Type entity model."""
    __tablename__ = "location_type"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
