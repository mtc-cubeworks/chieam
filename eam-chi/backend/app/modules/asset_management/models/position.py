from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Position(BaseModel):
    """Position entity model."""
    __tablename__ = "position"
    
    position_tag: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    attach_img: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    asset_class_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    system: Mapped[str] = mapped_column(String(50), ForeignKey("system.id"), nullable=True, default=None)
    system_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    current_asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
