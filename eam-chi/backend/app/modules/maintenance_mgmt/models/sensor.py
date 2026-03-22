from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Sensor(BaseModel):
    """Sensor entity model."""
    __tablename__ = "sensor"
    
    sensor_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    asset_name: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    asset_property: Mapped[str] = mapped_column(String(50), ForeignKey("asset_property.id"), nullable=True, default=None)
    uom_short_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    property_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    root_topic_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    collection_frequency: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
