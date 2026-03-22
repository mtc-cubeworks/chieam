from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Transfer(BaseModel):
    """Transfer entity model."""
    __tablename__ = "transfer"
    
    transfer_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    moved_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    date_moved: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    work_order_activity: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_activity.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    equipment: Mapped[str] = mapped_column(String(50), ForeignKey("equipment.id"), nullable=True, default=None)
    item_to_transfer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    purchase_request_line: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request_line.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    from_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    from_store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    from_bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    from_zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
    to_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    to_vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    to_store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    to_bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    to_zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
