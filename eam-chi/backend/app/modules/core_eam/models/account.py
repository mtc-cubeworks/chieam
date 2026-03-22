from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Account(BaseModel):
    """Account entity model."""
    __tablename__ = "account"
    
    account_code: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    account_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    account_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
