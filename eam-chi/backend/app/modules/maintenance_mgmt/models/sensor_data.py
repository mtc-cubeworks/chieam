from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class SensorData(BaseModel):
    """Sensor Data entity model."""
    __tablename__ = "sensor_data"
    
    sensor: Mapped[str] = mapped_column(String(50), ForeignKey("sensor.id"), nullable=True, default=None)
    value: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    timestamp: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
