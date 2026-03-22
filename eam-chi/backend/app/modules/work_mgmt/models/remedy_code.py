from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class RemedyCode(BaseModel):
    """Remedy Code lookup for corrective actions on Work Orders."""
    __tablename__ = "remedy_code"

    code: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    remedy_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    category_of_failure: Mapped[str] = mapped_column(String(50), ForeignKey("category_of_failure.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
