from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LeaveApplication(BaseModel):
    """Leave Application entity model."""
    __tablename__ = "leave_application"
    
    labor: Mapped[str] = mapped_column(String(50), ForeignKey("labor.id"), nullable=True, default=None)
    leave_type: Mapped[str] = mapped_column(String(50), ForeignKey("leave_type.id"), nullable=True, default=None)
    from_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    to_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default=None)
