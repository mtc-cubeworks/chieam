from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EquipmentGroup(BaseModel):
    """Equipment Group entity model."""
    __tablename__ = "equipment_group"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
