"""
Purchase Order Entity Business Logic

Server actions:
- create_po_from_pr(doc, db, user)   – Create PO(s) from an approved Purchase Request
- create_po_from_rfq(doc, db, user)  – Create PO from an awarded RFQ

Uses document helpers for Frappe-like syntax.
All mutating operations are wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc, apply_workflow_state


# =============================================================================
# Create Purchase Order from Purchase Request
# =============================================================================

async def create_po_from_pr(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Create Purchase Order(s) from an approved Purchase Request.

    Business Rules:
    - Check all PR lines, get all distinct vendors
    - Create one PO per vendor
    - Copy PR lines data to PO lines (grouped by vendor)
    - source_rfq is null (not from RFQ)
    - date_ordered = now
    - total_amount = sum of all lines (qty * price)
    """
    if not doc:
        return {"status": "error", "message": "Purchase Request not specified"}

    pr_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not pr_id:
        return {"status": "error", "message": "Purchase Request ID is required"}

    # Validate PR is in approved state (normalize to lowercase slug)
    pr_state = getattr(doc, 'workflow_state', None)
    pr_state_slug = pr_state.lower().replace(' ', '_') if pr_state else ''
    if pr_state_slug != "approved":
        return {"status": "error", "message": "Purchase Request must be in Approved state to create Purchase Order"}

    # Get site/department from the PR doc for PO header
    pr_site = getattr(doc, 'site', None) or None
    pr_department = getattr(doc, 'department', None) or None
    pr_cost_code = getattr(doc, 'cost_code', None) or None

    # Get all approved PR lines
    pr_lines = await get_list("purchase_request_line", {"purchase_request": pr_id}, db=db)
    if not pr_lines:
        return {"status": "error", "message": "No Purchase Request Lines found"}

    approved_lines = [l for l in pr_lines if l.get("workflow_state") == "approved"]
    if not approved_lines:
        return {"status": "error", "message": "No approved Purchase Request Lines found"}

    # Group lines by vendor
    vendor_groups: dict[str, list[dict]] = {}
    for line in approved_lines:
        vendor_id = line.get("vendor") or "__no_vendor__"
        vendor_groups.setdefault(vendor_id, []).append(line)

    try:
        created_pos = []

        for vendor_id, lines in vendor_groups.items():
            actual_vendor = vendor_id if vendor_id != "__no_vendor__" else None

            # Calculate total amount
            total_amount = 0.0
            for line in lines:
                qty = line.get("qty_required") or 0
                price = line.get("unit_cost") or 0.0
                total_amount += qty * price

            # Create Purchase Order - use PR-level site/dept, fall back to line-level
            po_site = pr_site or lines[0].get("site") or "UNASSIGNED"
            po_dept = pr_department or lines[0].get("department") or "UNASSIGNED"
            po_cost_code = pr_cost_code or lines[0].get("cost_code")

            po = await new_doc("purchase_order", db,
                workflow_state="draft",
                source_rfq=None,
                vendor=actual_vendor,
                date_ordered=date.today(),
                total_amount=total_amount,
                site=po_site,
                department=po_dept,
                cost_code=po_cost_code,
            )
            await save_doc(po, db, commit=False)

            # Create PO Lines from PR Lines
            for idx, pr_line in enumerate(lines, start=1):
                qty = pr_line.get("qty_required") or 0
                price = pr_line.get("unit_cost") or 0.0

                po_line = await new_doc("purchase_order_line", db,
                    workflow_state="draft",
                    po_id=po.id,
                    pr_line_id=pr_line.get("id"),
                    line_row_num=idx,
                    financial_asset_number=pr_line.get("financial_asset_number"),
                    item_id=pr_line.get("item"),
                    item_description=pr_line.get("item_description"),
                    quantity_ordered=qty,
                    price=price,
                    quantity_received=0,
                    site=pr_line.get("site") or po_site,
                    department=pr_line.get("department") or po_dept,
                    cost_code=pr_line.get("cost_code") or po_cost_code,
                )
                await save_doc(po_line, db, commit=False)

            created_pos.append(po.id)

        await db.commit()

        if len(created_pos) == 1:
            return {
                "status": "success",
                "message": "Purchase Order created",
                "data": {
                    "action": "generate_id",
                    "path": f"/purchase_order/{created_pos[0]}",
                    "id": created_pos[0],
                },
            }

        return {
            "status": "success",
            "message": f"{len(created_pos)} Purchase Order(s) created (one per vendor)",
            "data": {"ids": created_pos},
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Purchase Order: {str(e)}"}


# =============================================================================
# Create Purchase Order from RFQ
# =============================================================================

async def create_po_from_rfq(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Create Purchase Order from an awarded RFQ.

    Business Rules:
    - Connect source RFQ
    - Get awarded_vendor from RFQ and use it to fill Vendor
    - Copy RFQ lines data to PO lines
    - date_ordered = now
    - total_amount = sum of all lines (qty * price)
    """
    if not doc:
        return {"status": "error", "message": "RFQ not specified"}

    rfq_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not rfq_id:
        return {"status": "error", "message": "RFQ ID is required"}

    # Validate RFQ is in awarded state
    rfq_state = getattr(doc, 'workflow_state', None)
    if rfq_state != "awarded":
        return {"status": "error", "message": "RFQ must be in Awarded state to create Purchase Order"}

    # Get awarded vendor
    awarded_vendor = getattr(doc, 'awarded_vendor', None) or getattr(doc, 'supplier', None)
    if not awarded_vendor:
        return {"status": "error", "message": "Awarded Vendor is not set on RFQ"}

    # Get RFQ lines
    rfq_lines = await get_list("rfq_line", {"rfq_id": rfq_id}, db=db)
    if not rfq_lines:
        return {"status": "error", "message": "No RFQ Lines found"}

    try:
        # Inherit site/department from the parent Purchase Request
        # Try direct link first, then trace through RFQ lines → PR lines → PR
        pr_id = getattr(doc, 'purchase_request', None)
        pr_site = None
        pr_dept = None
        pr_cost_code = None
        if pr_id:
            pr_data = await get_value("purchase_request", pr_id, "*", db)
            if pr_data:
                pr_site = pr_data.get("site")
                pr_dept = pr_data.get("department")
                pr_cost_code = pr_data.get("cost_code")

        # Fallback: trace through first RFQ line → PR line → PR
        if not pr_site and rfq_lines:
            first_pr_line_id = rfq_lines[0].get("pr_line")
            if first_pr_line_id:
                pr_line_data = await get_value("purchase_request_line", first_pr_line_id, "*", db)
                if pr_line_data:
                    parent_pr_id = pr_line_data.get("purchase_request")
                    if parent_pr_id:
                        pr_data = await get_value("purchase_request", parent_pr_id, "*", db)
                        if pr_data:
                            pr_site = pr_data.get("site")
                            pr_dept = pr_data.get("department")
                            pr_cost_code = pr_data.get("cost_code")

        # Calculate total amount
        total_amount = 0.0
        for line in rfq_lines:
            qty = _to_float(line.get("quantity"))
            price = _to_float(line.get("price"))
            total_amount += qty * price

        # Create Purchase Order
        po = await new_doc("purchase_order", db,
            workflow_state="draft",
            source_rfq=rfq_id,
            vendor=awarded_vendor,
            date_ordered=date.today(),
            total_amount=total_amount,
            site=pr_site,
            department=pr_dept,
            cost_code=pr_cost_code,
        )
        await save_doc(po, db, commit=False)

        # Create PO Lines from RFQ Lines
        for idx, rfq_line in enumerate(rfq_lines, start=1):
            qty = _to_float(rfq_line.get("quantity"))
            price = _to_float(rfq_line.get("price"))

            po_line = await new_doc("purchase_order_line", db,
                workflow_state="draft",
                po_id=po.id,
                pr_line_id=rfq_line.get("pr_line"),
                line_row_num=idx,
                item_id=rfq_line.get("item"),
                item_description=rfq_line.get("item_description"),
                quantity_ordered=int(qty) if qty else 0,
                price=price,
                quantity_received=0,
                site=pr_site,
                department=pr_dept,
                cost_code=pr_cost_code,
            )
            await save_doc(po_line, db, commit=False)

        # Move RFQ to 'order' state via apply_workflow_state
        rfq_doc = await get_doc("request_for_quotation", rfq_id, db)
        if rfq_doc:
            wf_result = await apply_workflow_state(
                "request_for_quotation", rfq_doc, "close", db, commit=False
            )
            if wf_result["status"] == "error":
                await db.rollback()
                return wf_result

        await db.commit()

        return {
            "status": "success",
            "message": "Purchase Order created from RFQ",
            "data": {
                "action": "generate_id",
                "path": f"/purchase_order/{po.id}",
                "id": po.id,
            },
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Purchase Order from RFQ: {str(e)}"}


# =============================================================================
# Helpers
# =============================================================================

def _to_float(val: Any) -> float:
    """Safely convert a value to float."""
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# Server actions are auto-registered from entity JSON method paths.
# No manual decorator registration needed.
