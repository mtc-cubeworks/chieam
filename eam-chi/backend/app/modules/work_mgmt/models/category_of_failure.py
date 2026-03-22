from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class CategoryOfFailure(BaseModel):
    """Category of Failure entity model."""
    __tablename__ = "category_of_failure"
    
    failure_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
