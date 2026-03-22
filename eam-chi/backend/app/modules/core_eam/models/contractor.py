from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Contractor(BaseModel):
    """Contractor entity model."""
    __tablename__ = "contractor"
    
    contractor_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
