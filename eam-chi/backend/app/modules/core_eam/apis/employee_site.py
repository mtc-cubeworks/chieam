"""
Employee Site Post-Save / Post-Delete Business Logic

Mirrors: ci_eam/core_enterprise_asset_management/doctype/employee_site/employee_site.py
- populate_site_field(doc): Add site to Employee's site child table on create
- remove_site_field(doc): Remove site from Employee's site child table on delete
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


async def populate_site_field(doc: Any, db: AsyncSession) -> dict:
    """
    After-save hook: When an Employee Site is created, add the site
    to the Employee's site child table if not already present.
    """
    employee_id = getattr(doc, 'employee', None)
    site_id = getattr(doc, 'site', None)

    if not employee_id or not site_id:
        return {"status": "error", "message": "Employee and Site are required"}

    try:
        employee_doc = await get_doc("employee", employee_id, db)
        if not employee_doc:
            return {"status": "error", "message": f"Employee {employee_id} not found"}

        # Check if site already exists in employee's site child table
        existing_sites = await get_list(
            "employee_site_detail",
            {"employee": employee_id, "site": site_id},
            db=db
        )

        if existing_sites:
            return {
                "status": "success",
                "message": f"Site {site_id} already exists for employee {employee_id}"
            }

        # Add new site to the child table
        new_site_row = await new_doc("employee_site_detail", db,
            employee=employee_id,
            site=site_id,
        )
        if new_site_row:
            await save_doc(new_site_row, db)

        return {
            "status": "success",
            "message": f"Site {site_id} added to employee {employee_id}"
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}


async def remove_site_field(doc: Any, db: AsyncSession) -> dict:
    """
    After-delete hook: When an Employee Site is deleted, remove the site
    from the Employee's site child table.
    """
    employee_id = getattr(doc, 'employee', None)
    site_id = getattr(doc, 'site', None)

    if not employee_id or not site_id:
        return {"status": "error", "message": "Employee and Site are required"}

    try:
        # Find and delete the matching employee_site_detail row
        existing_sites = await get_list(
            "employee_site_detail",
            {"employee": employee_id, "site": site_id},
            db=db
        )

        if not existing_sites:
            return {
                "status": "success",
                "message": f"Site {site_id} was not found in employee {employee_id}"
            }

        for site_row in existing_sites:
            site_row_id = site_row.get("id")
            if site_row_id:
                site_row_doc = await get_doc("employee_site_detail", site_row_id, db)
                if site_row_doc:
                    await db.delete(site_row_doc)

        await db.commit()
        return {
            "status": "success",
            "message": f"Site {site_id} removed from employee {employee_id}"
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}
