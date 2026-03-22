from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AssetTransfer(BaseModel):
    """Asset Transfer entity model (MW-11).
    Tracks physical movement of assets between locations, sites, or departments
    with full audit trail.
    """
    __tablename__ = "asset_transfer"

    workflow_state: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=False)
    transfer_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    from_site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    to_site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    from_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    to_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    from_department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    to_department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    transferred_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    received_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    transfer_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    received_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
