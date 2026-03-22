from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_model import BaseModel


class Asset(BaseModel):
    """Asset entity model."""
    __tablename__ = "asset"
    
    workflow_state: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    asset_tag: Mapped[str] = mapped_column(String(255), nullable=True, unique=True, default=None)
    asset_class: Mapped[str] = mapped_column(String(50), ForeignKey("asset_class.id"), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    series: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    model: Mapped[str] = mapped_column(String(50), ForeignKey("model.id"), nullable=True, default=None)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_purchased: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    cost: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    block_number: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    number_of_repairs: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    site: Mapped[str] = mapped_column(String(50), ForeignKey("site.id"), nullable=True, default=None)
    department: Mapped[str] = mapped_column(String(50), ForeignKey("department.id"), nullable=True, default=None)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("employee.id"), nullable=True, default=None)
    inventory: Mapped[str] = mapped_column(String(50), ForeignKey("inventory.id"), nullable=True, default=None)
    system: Mapped[str] = mapped_column(String(50), ForeignKey("system.id"), nullable=True, default=None)
    position: Mapped[str] = mapped_column(String(50), ForeignKey("position.id"), nullable=True, default=None)
    item: Mapped[str] = mapped_column(String(50), ForeignKey("item.id"), nullable=True, default=None)
    defective: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    item_type: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_equipment: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    need_repair: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    bypass_process: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    # AR-1: Asset Lifecycle States
    lifecycle_state: Mapped[str] = mapped_column(String(50), nullable=True, default="Active")
    # AR-2: Asset Hierarchy
    parent_asset: Mapped[str] = mapped_column(String(50), ForeignKey("asset.id"), nullable=True, default=None)
    functional_location: Mapped[str] = mapped_column(String(50), ForeignKey("location.id"), nullable=True, default=None)
    # AR-3: Criticality Classification
    criticality: Mapped[str] = mapped_column(String(10), nullable=True, default=None)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    # AR-5: Warranty Linkage
    warranty_start: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    warranty_end: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    warranty_vendor: Mapped[str] = mapped_column(String(50), ForeignKey("vendor.id"), nullable=True, default=None)
    # AR-6: Nameplate / Specification Data
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    manufacturer_part_number: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    rated_capacity: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    rated_power: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    weight: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    technical_specs: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    # AR-7: Depreciation
    depreciation_method: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    useful_life_years: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    salvage_value: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    accumulated_depreciation: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    commissioning_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
