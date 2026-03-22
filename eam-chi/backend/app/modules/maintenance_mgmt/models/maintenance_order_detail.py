from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenanceOrderDetail(BaseModel):
    """Maintenance Order Detail entity model."""
    __tablename__ = "maintenance_order_detail"
    
    maintenance_order: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_order.id"), nullable=True, default=None)
    seq_num: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    maint_req: Mapped[str] = mapped_column(String(50), ForeignKey("maintenance_request.id"), nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    due_date: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    resource_availability_status: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
