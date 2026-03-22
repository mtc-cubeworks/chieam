from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Site(BaseModel):
    """Site entity model."""
    __tablename__ = "site"
    
    site_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    organization: Mapped[str] = mapped_column(String(50), ForeignKey("organization.id"), nullable=True, default=None)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    default_cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    site_manager: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
