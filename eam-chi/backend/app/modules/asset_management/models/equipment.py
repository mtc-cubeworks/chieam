from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Equipment(BaseModel):
    """Equipment entity model."""
    __tablename__ = "equipment"
    
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    equipment_group: Mapped[str] = mapped_column(String(50), ForeignKey("equipment_group.id"), nullable=True, default=None)
    equipment_group_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    custodian: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    pr_line_no: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request_line.id"), nullable=True, default=None)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    equipment_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
