from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Department(BaseModel):
    """Department entity model."""
    __tablename__ = "department"
    
    department_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    department_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    site_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    department_manager: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    default_cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    overhead_method: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    overhead_percent: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    overhead_rp_hour: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    overhead_expense_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    labor_expense_account_overwrite: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
