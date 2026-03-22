from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetMaintenanceHistory(BaseModel):
    """
    Tracks completed maintenance events against an asset.
    Automatically populated when a Work Order completes or closes.
    """
    __tablename__ = "asset_maintenance_history"

    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    completed_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    downtime_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    category_of_failure: Mapped[str] = mapped_column(String(50), ForeignKey("category_of_failure.id"), nullable=True, default=None)
    cause_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    remedy_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
