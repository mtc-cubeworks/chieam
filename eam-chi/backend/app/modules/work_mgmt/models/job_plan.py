from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class JobPlan(BaseModel):
    """Reusable job template with predefined tasks, labor, parts, tools, and safety procedures."""
    __tablename__ = "job_plan"

    job_plan_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    work_order_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    estimated_hours: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    safety_procedures: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    checklist: Mapped[str] = mapped_column(String(50), ForeignKey("checklist.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
