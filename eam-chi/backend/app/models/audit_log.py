"""
Audit Log Model
===============
Tracks entity record changes with before/after snapshots.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String(100), nullable=False, index=True)
    record_id = Column(String(50), nullable=False, index=True)
    action = Column(String(20), nullable=False)  # create, update, delete, workflow
    user_id = Column(String(50), nullable=True)
    username = Column(String(100), nullable=True)
    before_snapshot = Column(Text, nullable=True)  # JSON string
    after_snapshot = Column(Text, nullable=True)   # JSON string
    changed_fields = Column(Text, nullable=True)   # JSON list of field names
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
