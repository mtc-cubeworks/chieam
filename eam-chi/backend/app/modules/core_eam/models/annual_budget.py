from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class AnnualBudget(BaseModel):
    """Annual Budget entity model."""
    __tablename__ = "annual_budget"
    
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    cost_code_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    year: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    budgetary_amount: Mapped[float] = mapped_column(Float, nullable=True, default=None)
