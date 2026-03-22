from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceActivity(BaseModel):
    """Maintenance Activity entity model."""
    __tablename__ = "maintenance_activity"
    
    activity_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
