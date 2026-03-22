from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class StockCountTask(BaseModel):
    """Stock Count Task entity model."""
    __tablename__ = "stock_count_task"
    
    stock_count: Mapped[str] = mapped_column(String(50), ForeignKey("stock_count.id"), nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
