from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class LeaveType(BaseModel):
    """Leave Type entity model."""
    __tablename__ = "leave_type"
    
    leave_type_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
