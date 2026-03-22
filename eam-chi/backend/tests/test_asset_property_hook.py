"""
Test for Asset Property before-save hook - copy Unit of Measure from Property
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.asset_management.apis.asset_property import copy_unit_of_measure_from_property


@pytest.mark.asyncio
async def test_copy_unit_of_measure_from_property_null_to_value():
    """Test that UoM is copied when Asset Property has null and Property has UoM."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock property document with UoM
    property_doc = MagicMock()
    property_doc.unit_of_measure = "uom_123"
    
    # Mock asset property document with null UoM
    asset_prop = MagicMock()
    asset_prop.unit_of_measure = None
    asset_prop.property = "prop_789"
    
    with pytest.MonkeyPatch().context() as m:
        # Mock the get_doc function
        async def mock_get_doc(entity, doc_id, db_session):
            if entity == "property":
                return property_doc
            return None
        
        m.setattr("app.modules.asset_management.apis.asset_property.get_doc", mock_get_doc)
        
        # Call the function
        result = await copy_unit_of_measure_from_property(asset_prop, db)
        
        # Verify the result is the same document
        assert result == asset_prop
        
        # Verify the asset property was updated
        assert asset_prop.unit_of_measure == "uom_123"


@pytest.mark.asyncio
async def test_copy_unit_of_measure_already_equal():
    """Test that function doesn't change when UoM values are already equal."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock property document with UoM
    property_doc = MagicMock()
    property_doc.unit_of_measure = "uom_123"
    
    # Mock asset property document with same UoM
    asset_prop = MagicMock()
    asset_prop.unit_of_measure = "uom_123"
    asset_prop.property = "prop_789"
    
    with pytest.MonkeyPatch().context() as m:
        # Mock the get_doc function
        async def mock_get_doc(entity, doc_id, db_session):
            if entity == "property":
                return property_doc
            return None
        
        m.setattr("app.modules.asset_management.apis.asset_property.get_doc", mock_get_doc)
        
        # Call the function
        result = await copy_unit_of_measure_from_property(asset_prop, db)
        
        # Verify the result is the same document
        assert result == asset_prop
        
        # Verify the asset property was NOT changed (still the same)
        assert asset_prop.unit_of_measure == "uom_123"


@pytest.mark.asyncio
async def test_copy_unit_of_measure_override():
    """Test that UoM is overridden when Asset Property has different UoM than Property."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock property document with UoM
    property_doc = MagicMock()
    property_doc.unit_of_measure = "uom_new"
    
    # Mock asset property document with different UoM
    asset_prop = MagicMock()
    asset_prop.unit_of_measure = "uom_old"
    asset_prop.property = "prop_789"
    
    with pytest.MonkeyPatch().context() as m:
        # Mock the get_doc function
        async def mock_get_doc(entity, doc_id, db_session):
            if entity == "property":
                return property_doc
            return None
        
        m.setattr("app.modules.asset_management.apis.asset_property.get_doc", mock_get_doc)
        
        # Call the function
        result = await copy_unit_of_measure_from_property(asset_prop, db)
        
        # Verify the result is the same document
        assert result == asset_prop
        
        # Verify the asset property was updated to Property's UoM
        assert asset_prop.unit_of_measure == "uom_new"


@pytest.mark.asyncio
async def test_copy_unit_of_measure_no_property_uom():
    """Test that function skips when Property has no UoM."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock property document without UoM
    property_doc = MagicMock()
    property_doc.unit_of_measure = None
    
    # Mock asset property document with null UoM
    asset_prop = MagicMock()
    asset_prop.unit_of_measure = None
    asset_prop.property = "prop_789"
    
    with pytest.MonkeyPatch().context() as m:
        # Mock the get_doc function
        async def mock_get_doc(entity, doc_id, db_session):
            if entity == "property":
                return property_doc
            return None
        
        m.setattr("app.modules.asset_management.apis.asset_property.get_doc", mock_get_doc)
        
        # Call the function
        result = await copy_unit_of_measure_from_property(asset_prop, db)
        
        # Verify the result is the same document
        assert result == asset_prop
        
        # Verify the asset property was NOT changed
        assert asset_prop.unit_of_measure is None


@pytest.mark.asyncio
async def test_copy_unit_of_measure_no_property_linked():
    """Test that function skips when no Property is linked."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock asset property document with no property linked
    asset_prop = MagicMock()
    asset_prop.unit_of_measure = None
    asset_prop.property = None
    
    # Call the function (no mocking needed since get_doc won't be called)
    result = await copy_unit_of_measure_from_property(asset_prop, db)
    
    # Verify the result is the same document
    assert result == asset_prop
    
    # Verify the asset property was NOT changed
    assert asset_prop.unit_of_measure is None


@pytest.mark.asyncio
async def test_copy_unit_of_measure_with_dict():
    """Test that function works with dict documents (not just ORM objects)."""
    
    # Mock database session
    db = AsyncMock(spec=AsyncSession)
    
    # Mock property document with UoM
    property_doc = MagicMock()
    property_doc.unit_of_measure = "uom_123"
    
    # Mock asset property as dict with null UoM
    asset_prop = {
        "unit_of_measure": None,
        "property": "prop_789"
    }
    
    with pytest.MonkeyPatch().context() as m:
        # Mock the get_doc function
        async def mock_get_doc(entity, doc_id, db_session):
            if entity == "property":
                return property_doc
            return None
        
        m.setattr("app.modules.asset_management.apis.asset_property.get_doc", mock_get_doc)
        
        # Call the function
        result = await copy_unit_of_measure_from_property(asset_prop, db)
        
        # Verify the result is the same document
        assert result == asset_prop
        
        # Verify the asset property was updated
        assert asset_prop["unit_of_measure"] == "uom_123"
