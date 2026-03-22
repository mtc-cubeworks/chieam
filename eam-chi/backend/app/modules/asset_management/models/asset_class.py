from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetClass(BaseModel):
    """Asset Class entity model."""
    __tablename__ = "asset_class"
    
    name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    class_icon: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    due_date_lead_time: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    parent_asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
