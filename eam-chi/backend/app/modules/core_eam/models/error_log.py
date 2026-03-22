from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class ErrorLog(BaseModel):
    """Error Log entity model."""
    __tablename__ = "error_log"
    
    status: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    title: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
