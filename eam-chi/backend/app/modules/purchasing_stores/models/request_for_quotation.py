from datetime import date
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class RequestForQuotation(BaseModel):
    """Request For Quotation entity model."""
    __tablename__ = "request_for_quotation"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    purchase_request: Mapped[str] = mapped_column(String(50), ForeignKey("purchase_request.id"), nullable=True, default=None)
    generated_by: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    supplier: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    date_issue: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    requestor: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    awarded_vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    terms_and_conditions: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    remarks: Mapped[str] = mapped_column(Text, nullable=True, default=None)
