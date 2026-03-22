from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ItemClass(BaseModel):
    """Item Class entity model."""
    __tablename__ = "item_class"
    
    item_class_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    item_class_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    parent_item_class: Mapped[str] = mapped_column(String(50), ForeignKey("item_class.id"), nullable=True, default=None)
    default_uom: Mapped[str] = mapped_column(String(50), ForeignKey("unit_of_measure.id"), nullable=True, default=None)
    valuation_method: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    inventory_tracking: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    is_serialized: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
