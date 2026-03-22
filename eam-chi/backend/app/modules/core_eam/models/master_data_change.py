from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MasterDataChange(BaseModel):
    """Master Data Change Management entity model (MW-18).
    Provides approval workflow for changes to critical master data
    (assets, items, vendors, locations) to ensure data integrity.
    """
    __tablename__ = "master_data_change"

    workflow_state: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    entity_id: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    change_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    field_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    old_value: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    new_value: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    requested_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    approved_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    requested_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    approved_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    justification: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
