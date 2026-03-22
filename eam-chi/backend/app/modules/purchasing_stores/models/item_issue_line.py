from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ItemIssueLine(BaseModel):
    """Item Issue Line entity model."""
    __tablename__ = "item_issue_line"
    
    item_issue: Mapped[str] = mapped_column(String(50), ForeignKey("item_issue.id"), nullable=True, default=None)
    work_order_parts: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_parts.id"), nullable=True, default=None)
    work_order_equipment: Mapped[str] = mapped_column(String(50), ForeignKey("work_order_equipment.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    item_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
    quantity_issued: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
