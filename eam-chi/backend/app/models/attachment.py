"""
Attachment model for storing file attachments linked to any entity record.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.core.database import Base


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_name = Column(String, nullable=False, index=True)
    record_id = Column(String, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    mime_type = Column(String, nullable=True)
    uploaded_by = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
