from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrderActivity(BaseModel):
    """Work Order Activity entity model."""
    __tablename__ = "work_order_activity"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    work_order_name: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_item_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    work_item: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    asset_name: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    activity_type_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    position: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    does_it_need_repair: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    # WA-1: Task sequencing / dependencies
    sequence: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    predecessor: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    dependency_type: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    # WA-3: Completion criteria
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    completion_status: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
