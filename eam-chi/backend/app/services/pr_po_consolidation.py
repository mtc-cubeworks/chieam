"""
PR → PO Consolidation Service
================================
Groups approved Purchase Request lines across multiple PRs by vendor
and creates consolidated Purchase Orders.

Registered as a server action on purchase_request so users can trigger
"Consolidate to PO" from any approved PR (system finds all approved PRs).
"""
from datetime import date
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_list, new_doc, save_doc


async def consolidate_approved_prs_to_pos(
    db: AsyncSession,
    site: str | None = None,
) -> dict:
    """
    Find all approved PRs (optionally filtered by site) and consolidate
    their approved lines into POs grouped by vendor.

    Steps:
      1. Gather all approved PR lines across all approved PRs.
      2. Group by vendor.
      3. Create one PO per vendor with all matching lines.
      4. Update PR lines with the resulting PO number for traceability.

    Returns: {"status": "success"|"error", "data": {"created_pos": [...], "lines_consolidated": int}}
    """

    # 1. Find approved PRs
    pr_filters: dict[str, Any] = {"workflow_state": "approved"}
    if site:
        pr_filters["site"] = site
    approved_prs = await get_list("purchase_request", pr_filters, db=db)

    if not approved_prs:
        return {"status": "success", "message": "No approved Purchase Requests to consolidate", "data": {}}

    # 2. Collect all approved lines across those PRs
    all_approved_lines: list[dict] = []
    pr_meta: dict[str, dict] = {}  # pr_id -> PR header fields

    for pr_dict in approved_prs:
        pr_id = pr_dict["id"]
        pr_meta[pr_id] = pr_dict
        lines = await get_list(
            "purchase_request_line",
            {"purchase_request": pr_id, "workflow_state": "approved"},
            db=db,
        )
        # Skip lines that already have a PO assigned
        for line in lines:
            if not line.get("po_num"):
                line["_pr_id"] = pr_id
                all_approved_lines.append(line)

    if not all_approved_lines:
        return {"status": "success", "message": "All approved lines already have POs", "data": {}}

    # 3. Group by vendor
    vendor_groups: dict[str, list[dict]] = {}
    for line in all_approved_lines:
        vendor = line.get("vendor") or "__no_vendor__"
        vendor_groups.setdefault(vendor, []).append(line)

    created_pos: list[str] = []
    total_lines = 0

    try:
        for vendor_key, lines in vendor_groups.items():
            actual_vendor = vendor_key if vendor_key != "__no_vendor__" else None

            # Use site/dept from first line's PR header
            first_pr = pr_meta.get(lines[0]["_pr_id"], {})
            po_site = first_pr.get("site")
            po_dept = first_pr.get("department")
            po_cost_code = first_pr.get("cost_code")

            total_amount = 0.0
            for line in lines:
                qty = int(line.get("qty_required", 0) or 0)
                price = float(line.get("unit_cost", 0) or 0)
                total_amount += qty * price

            po = await new_doc("purchase_order", db,
                workflow_state="draft",
                source_rfq=None,
                vendor=actual_vendor,
                date_ordered=date.today(),
                total_amount=round(total_amount, 2),
                site=po_site,
                department=po_dept,
                cost_code=po_cost_code,
            )
            await save_doc(po, db, commit=False)

            for idx, pr_line in enumerate(lines, start=1):
                qty = int(pr_line.get("qty_required", 0) or 0)
                price = float(pr_line.get("unit_cost", 0) or 0)

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

                # Mark the PR line with the PO number for traceability
                pr_line_doc = await get_doc("purchase_request_line", pr_line["id"], db)
                if pr_line_doc:
                    pr_line_doc.po_num = po.id
                    await save_doc(pr_line_doc, db, commit=False)

                total_lines += 1

            created_pos.append(po.id)

        await db.commit()

        return {
            "status": "success",
            "message": f"Created {len(created_pos)} PO(s) consolidating {total_lines} line(s) from {len(approved_prs)} PR(s)",
            "data": {"created_pos": created_pos, "lines_consolidated": total_lines},
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"PR→PO consolidation failed: {str(e)}"}
