from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class UnitOfMeasure(BaseModel):
    """Unit of Measure entity model."""
    __tablename__ = "unit_of_measure"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    short_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
