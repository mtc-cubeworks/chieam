from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LaborGroup(BaseModel):
    """Labor Group entity model."""
    __tablename__ = "labor_group"
    
    labor_group_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
