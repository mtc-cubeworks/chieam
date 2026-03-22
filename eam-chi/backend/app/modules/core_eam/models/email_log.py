from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class EmailLog(BaseModel):
    """Email Log entity model."""
    __tablename__ = "email_log"
    
    subject: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    recipients: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    cc: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    bcc: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    from_address: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    record_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    event_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    html_body: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    recipient_count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    sent_by: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
