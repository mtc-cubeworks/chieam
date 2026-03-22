from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ItemReturnLine(BaseModel):
    """Item Return Line entity model."""
    __tablename__ = "item_return_line"
    
    item_return: Mapped[str] = mapped_column(String(50), ForeignKey("item_return.id"), nullable=True, default=None)
    work_order_parts: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_parts.id"), nullable=True, default=None)
    work_order_equipment: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_equipment.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    quantity_returned: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
