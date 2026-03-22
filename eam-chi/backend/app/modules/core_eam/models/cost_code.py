from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class CostCode(BaseModel):
    """Cost Code entity model."""
    __tablename__ = "cost_code"
    
    code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    scope: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    site_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
