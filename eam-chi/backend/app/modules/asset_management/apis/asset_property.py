"""
Asset Property Before-Save Business Logic

Before-save hook:
- copy_unit_of_measure_from_property(doc, db) - Copies UoM from Property entity with optimized comparison
"""
from typing import Any, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc


def _get_field_value(doc: Any, field: str) -> Any:
    """Get field value from ORM object or dict."""
    if hasattr(doc, field):
        return getattr(doc, field)
    if isinstance(doc, dict):
        return doc.get(field)
    return None


def _set_field_value(doc: Any, field: str, value: Any) -> None:
    """Set field value on ORM object or dict."""
    if hasattr(doc, field):
        setattr(doc, field, value)
    elif isinstance(doc, dict):
        doc[field] = value


async def copy_unit_of_measure_from_property(doc: Any, db: AsyncSession) -> Any:
    """
    Before-save hook: Optimize Unit of Measure by comparing with Property entity.
    
    Logic:
    1. Get current UoM from Asset Property
    2. Get UoM from linked Property entity
    3. If Property has no UoM → keep current (no change)
    4. If current UoM equals Property UoM → keep current (no change)
    5. If current UoM is null and Property has UoM → copy from Property
    6. If current UoM differs from Property UoM → use Property UoM (override)
    """
    # Get the linked property ID
    property_id = _get_field_value(doc, 'property')
    if not property_id:
        return doc  # No property linked, no change needed

    # Get the property document
    property_doc = await get_doc("property", property_id, db)
    if not property_doc:
        return doc  # Property not found, no change needed

    # Get UoM from property
    property_uom = _get_field_value(property_doc, 'unit_of_measure')
    if not property_uom:
        return doc  # Property has no UoM, no change needed

    # Get current UoM from asset property
    current_uom = _get_field_value(doc, 'unit_of_measure')
    
    # Compare and update if needed
    if current_uom != property_uom:
        # Update the asset property UoM
        _set_field_value(doc, 'unit_of_measure', property_uom)
        
        # Also update the short name if available from property
        # (This would require additional lookup to unit_of_measure entity if needed)
        # For now, we'll keep any existing uom_short_name as is
    
    return doc
