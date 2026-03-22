from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Putaway(BaseModel):
    """Putaway entity model."""
    __tablename__ = "putaway"
    
    putaway_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    source_data_repair: Mapped[str] = mapped_column(String(50), ForeignKey("transfer.id"), nullable=True, default=None)
    source_data_parts_return: Mapped[str] = mapped_column(String(50), ForeignKey("item_return_line.id"), nullable=True, default=None)
    source_data_asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    qty: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    store: Mapped[str] = mapped_column(String(50), ForeignKey("store.id"), nullable=True, default=None)
    bin: Mapped[str] = mapped_column(String(50), ForeignKey("bin.id"), nullable=True, default=None)
    zone: Mapped[str] = mapped_column(String(50), ForeignKey("zone.id"), nullable=True, default=None)
