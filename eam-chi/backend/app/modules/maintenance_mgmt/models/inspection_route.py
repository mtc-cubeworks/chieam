from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class InspectionRoute(BaseModel):
    """Grouped sequence of inspection points for operator rounds."""
    __tablename__ = "inspection_route"

    route_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    frequency: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Daily, Shift, Weekly
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
