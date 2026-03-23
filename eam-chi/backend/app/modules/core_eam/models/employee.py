from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Employee(BaseModel):
    """Employee entity model."""
    __tablename__ = "employee"
    
    user: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=True, default=None)
    employee_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    position: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    reports_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
