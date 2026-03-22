from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class StockCount(BaseModel):
    """Stock Count entity model."""
    __tablename__ = "stock_count"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    method: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    basis: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    abc_code: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    freeze_policy: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
