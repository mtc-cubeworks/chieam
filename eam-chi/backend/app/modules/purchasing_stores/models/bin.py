from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Bin(BaseModel):
    """Bin entity model."""
    __tablename__ = "bin"
    
    rack_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    shelf_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    bin_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    store_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
