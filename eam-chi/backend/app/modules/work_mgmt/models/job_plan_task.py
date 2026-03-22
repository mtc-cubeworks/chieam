from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class JobPlanTask(BaseModel):
    """Individual task step within a Job Plan."""
    __tablename__ = "job_plan_task"

    job_plan: Mapped[str] = mapped_column(String(50), ForeignKey("job_plan.id"), nullable=True, default=None)
    sequence: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    task_description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    craft_required: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
