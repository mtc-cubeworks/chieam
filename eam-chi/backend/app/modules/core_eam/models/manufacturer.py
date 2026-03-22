from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Manufacturer(BaseModel):
    """Manufacturer entity model."""
    __tablename__ = "manufacturer"
    
    company_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    email: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
