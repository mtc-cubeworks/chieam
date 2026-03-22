from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class InspectionPoint(BaseModel):
    """Individual checkpoint within an inspection route."""
    __tablename__ = "inspection_point"

    inspection_route: Mapped[str] = mapped_column(String(50), ForeignKey("inspection_route.id"), nullable=True, default=None)
    sequence: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    measurement_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)  # Visual, Reading, Pass/Fail
    expected_value: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    tolerance: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
