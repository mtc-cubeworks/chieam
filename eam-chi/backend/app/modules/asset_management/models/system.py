from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class System(BaseModel):
    """System entity model."""
    __tablename__ = "system"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    system_type: Mapped[str] = mapped_column(String(50), ForeignKey("system_type.id"), nullable=True, default=None)
    system_type_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    parent_system: Mapped[str] = mapped_column(String(50), ForeignKey("system.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
