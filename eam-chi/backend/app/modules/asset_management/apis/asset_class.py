"""
Asset Class Post-Saving Business Logic

Implements the business logic for Asset Class entity as documented in POST_SAVING_DOCUMENTATION.md.

Functions:
    populate_asset_class_prop_and_maint_plan: Populates Asset Class Properties and Maintenance Plans from parent.
"""
from app.application.hooks.context import HookContext
from app.services.document import get_list, new_doc, save_doc
from sqlalchemy.ext.asyncio import AsyncSession


async def populate_asset_class_prop_and_maint_plan(doc, ctx: HookContext):
    """
    Populates Asset Class Properties and Maintenance Plans from parent Asset Class.
    
    Logic:
    1. If parent_asset_class exists:
       - Copies all Asset Class Properties from parent
       - (Future) Copies all Maintenance Plans from parent
       - (Future) Copies all Planned Maintenance Activities from parent's plans
    
    2. (Future) Adds default properties from Function Config:
       - running_interval_property
       - last_interval_property
       - last_maintenance_date_property
       - threshold_property
    
    Related Doctypes:
    - Asset Class Property
    - (Future) Maintenance Plan
    - (Future) Planned Maintenance Activity
    - Property
    - (Future) Function Config
    """
    
    db = ctx.db
    
    # Get the parent_asset_class from the doc
    parent_asset_class_id = getattr(doc, 'parent_asset_class', None)
    
    if not parent_asset_class_id:
        return {
            "status": "success", 
            "message": f"Asset Class '{getattr(doc, 'name', doc.id)}' created without parent - no properties to inherit"
        }
    
    # Check if this asset class already has properties (avoid duplicates on update)
    existing_props = await get_list("asset_class_property", {"asset_class": doc.id}, db=db, as_dict=False)
    
    if existing_props:
        return {
            "status": "success", 
            "message": f"Asset Class '{getattr(doc, 'name', doc.id)}' already has properties - inheritance skipped"
        }
    
    # Get all Asset Class Properties from parent
    parent_props = await get_list("asset_class_property", {"asset_class": parent_asset_class_id}, db=db, as_dict=False)
    
    if not parent_props:
        return {
            "status": "success", 
            "message": f"Parent Asset Class '{parent_asset_class_id}' has no properties to inherit"
        }
    
    # Copy each property to the new asset class
    copied_count = 0
    for parent_prop in parent_props:
        # Create new property using new_doc (handles ID generation if enabled)
        new_prop = await new_doc("asset_class_property", db,
            asset_class=doc.id,
            property=parent_prop.property,
            unit_of_measure=parent_prop.unit_of_measure,
            default_value=parent_prop.default_value,
        )
        
        if new_prop:
            await save_doc(new_prop, db, commit=False)
            copied_count += 1
    
    # Commit the new properties
    if parent_props:
        await db.commit()
    
    return {
        "status": "success", 
        "message": f"Asset Class '{getattr(doc, 'name', doc.id)}' inherited {copied_count} properties from parent '{parent_asset_class_id}'",
        "inherited_properties": copied_count,
        "parent_asset_class": parent_asset_class_id
    }


async def set_asset_class_name_on_create(doc: dict, ctx: HookContext) -> dict:
    """
    Before create hook to ensure asset class name is set.
    This is a placeholder for any pre-processing needed.
    """
    return doc
