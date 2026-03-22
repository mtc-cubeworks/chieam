from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class PositionRelation(BaseModel):
    """Position Relation entity model."""
    __tablename__ = "position_relation"
    
    position_a: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    position_a_description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    position_relation_type: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    position_b: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    position_b_description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
