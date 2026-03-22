from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ConditionMonitoring(BaseModel):
    """Condition Monitoring entity model (MW-5).
    Tracks vibration, temperature, and other condition-based readings
    with threshold alerting for predictive maintenance.
    """
    __tablename__ = "condition_monitoring"

    workflow_state: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), ForeignKey("sensor.id"), nullable=True, default=None)
    monitoring_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    reading_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    reading_unit: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    reading_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    baseline_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    alert_status: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    trend_direction: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    analysis_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    maintenance_request: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_request.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
