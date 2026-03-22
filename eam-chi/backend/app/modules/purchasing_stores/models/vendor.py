from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Vendor(BaseModel):
    """Vendor entity model."""
    __tablename__ = "vendor"
    
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
