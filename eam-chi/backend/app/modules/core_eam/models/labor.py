from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Labor(BaseModel):
    """Labor entity model."""
    __tablename__ = "labor"
    
    labor_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    labor_group: Mapped[str] = mapped_column(String(50), ForeignKey("labor_group.id"), nullable=True, default=None)
    labor_group_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    employee: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    contractor: Mapped[str] = mapped_column(String(50), ForeignKey("contractor.id"), nullable=True, default=None)
    laborer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    location_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    pr_line_no: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    labor_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
