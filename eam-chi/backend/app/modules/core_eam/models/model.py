from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Model(BaseModel):
    """Model entity model."""
    __tablename__ = "model"
    
    model_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    manufacturer: Mapped[str] = mapped_column(String(50), ForeignKey("manufacturer.id"), nullable=True, default=None)
    manufacturer_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
