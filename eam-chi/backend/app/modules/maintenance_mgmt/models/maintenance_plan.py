from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class MaintenancePlan(BaseModel):
    """Maintenance Plan entity model."""
    __tablename__ = "maintenance_plan"
    
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    asset_class_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    manufacturer: Mapped[str] = mapped_column(String(50), ForeignKey("manufacturer.id"), nullable=True, default=None)
    manufacturer_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    model: Mapped[str] = mapped_column(String(50), ForeignKey("model.id"), nullable=True, default=None)
    model_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
