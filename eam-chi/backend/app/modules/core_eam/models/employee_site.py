from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EmployeeSite(BaseModel):
    """Employee Site entity model."""
    __tablename__ = "employee_site"
    
    employee: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    default: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
