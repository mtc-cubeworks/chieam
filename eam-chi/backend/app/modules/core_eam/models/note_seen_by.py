from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class NoteSeenBy(BaseModel):
    """Note Seen By entity model."""
    __tablename__ = "note_seen_by"
    
    note: Mapped[str] = mapped_column(String(50), ForeignKey("note.id"), nullable=True, default=None)
    user: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=True, default=None)
