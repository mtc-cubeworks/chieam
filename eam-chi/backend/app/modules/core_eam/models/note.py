from datetime import date
from sqlalchemy import Boolean, Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Note(BaseModel):
    """Note entity model."""
    __tablename__ = "note"
    
    title: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    public: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    notify_on_login: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    notify_on_every_login: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    expire_notification_on: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    content: Mapped[str] = mapped_column(Text, nullable=True, default=None)
