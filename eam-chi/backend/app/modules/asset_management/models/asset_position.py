from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetPosition(BaseModel):
    """Asset Position entity model."""
    __tablename__ = "asset_position"
    
    position: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    date_installed: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    date_removed: Mapped[date] = mapped_column(Date, nullable=True, default=None)
