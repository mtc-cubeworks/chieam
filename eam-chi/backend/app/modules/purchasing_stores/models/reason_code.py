from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ReasonCode(BaseModel):
    """Reason Code entity model."""
    __tablename__ = "reason_code"
    
    code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    movement_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    default_debit_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    default_credit_account: Mapped[str] = mapped_column(String(50), ForeignKey("account.id"), nullable=True, default=None)
    approval_threshold: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
