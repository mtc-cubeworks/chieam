from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class WorkOrder(BaseModel):
    """Work Order entity model."""
    __tablename__ = "work_order"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    work_order_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    category_of_failure: Mapped[str] = mapped_column(String(50), ForeignKey("category_of_failure.id"), nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    priority: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    severity: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    incident: Mapped[str] = mapped_column(String(50), ForeignKey("incident.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    cost_code: Mapped[str] = mapped_column(String(50), ForeignKey("cost_code.id"), nullable=True, default=None)
    # Downtime Tracking (WO-6)
    downtime_start: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    downtime_end: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    downtime_hours: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    # Failure Analysis (WO-7)
    cause_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    remedy_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    failure_notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    # WO-2: Job Plan linkage
    job_plan: Mapped[str] = mapped_column(String(50), ForeignKey("job_plan.id"), nullable=True, default=None)
    # WO-3: Scheduling
    scheduled_start: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    actual_start: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    actual_end: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    # WO-4: Multi-level Approval
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    approval_level: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    approved_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    # WO-5: Cost Tracking
    total_labor_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_equipment_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_parts_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    total_cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    # WO-8: Safety Permit linkage
    safety_permit: Mapped[str] = mapped_column(String(50), ForeignKey("safety_permit.id"), nullable=True, default=None)
    loto_required: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    # WO-9: Feedback / Closeout
    technician_findings: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    work_performed: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    recommendations: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    # WO-10: Follow-up WO
    follow_up_work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
    parent_work_order: Mapped[str] = mapped_column(String(50), ForeignKey("work_order.id"), nullable=True, default=None)
