from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Store(BaseModel):
    """Store entity model."""
    __tablename__ = "store"
    
    store_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
