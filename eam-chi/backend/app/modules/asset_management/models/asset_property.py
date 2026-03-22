from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetProperty(BaseModel):
    """Asset Property entity model."""
    __tablename__ = "asset_property"
    
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    property: Mapped[str] = mapped_column(String(50), ForeignKey("property.id"), nullable=True, default=None)
    property_value: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    unit_of_measure: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    property_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
