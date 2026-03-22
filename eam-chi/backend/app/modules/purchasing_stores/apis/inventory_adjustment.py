"""
Inventory Adjustment Entity Business Logic

Workflow handlers (called from workflow_router.py):
- check_inventory_adjustment_workflow(doc, action, db, user)
    - "Submit": validate lines exist, move to Submitted
    - "Post": validate lines, apply adjustments to inventory (additive update or new record),
              reset freeze/warn flags, set posting_datetime
    - "Cancel": cancel the adjustment

Uses document helpers for Frappe-like syntax.
All mutating operations are wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc
from app.services.stock_ledger import ledger_for_adjustment


# =============================================================================
# Helpers
# =============================================================================

def _get_id(doc: Any) -> str | None:
    return doc.id if hasattr(doc, 'id') else doc.get('id') if isinstance(doc, dict) else None


def _get_attr(doc: Any, attr: str) -> Any:
    if hasattr(doc, attr):
        return getattr(doc, attr)
    if isinstance(doc, dict):
        return doc.get(attr)
    return None


def _to_float(val: Any) -> float:
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _to_int(val: Any) -> int:
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


# =============================================================================
# Inventory Adjustment Workflow Handler
# =============================================================================

async def check_inventory_adjustment_workflow(
    doc: Any, action: str, db: AsyncSession, user: Any
) -> dict:
    """
    Workflow handler for Inventory Adjustment.

    States: Draft → Submitted → Posted
                             → Cancelled

    "Submit":
        - Validate at least one line exists

    "Post":
        - Validate at least one line exists
        - Negative inventory guardrail: final result (current_qty + adjusted_qty) must be >= 0
        - For each line:
            Case A (Existing Inventory): additive update — actual_inv += adjusted_qty,
                                          available_inv += adjusted_qty, reset freeze/warn
            Case B (New Inventory): create a new Inventory record initialized with adjusted_qty
        - Set posting_datetime = now()

    "Cancel":
        - No additional logic; state transition handles it
    """
    if not doc:
        return {"status": "error", "message": "Inventory Adjustment not specified"}

    doc_id = _get_id(doc)
    if not doc_id:
        return {"status": "error", "message": "Inventory Adjustment ID is required."}

    # -------------------------------------------------------------------------
    # Submit: validate lines exist
    # -------------------------------------------------------------------------
    action_slug = action.lower().replace(" ", "_")

    if action_slug == "submit":
        adj_lines = await get_list("inventory_adjustment_line", {"inventory_adjustment": doc_id}, db=db)
        if not adj_lines:
            return {
                "status": "error",
                "message": "Cannot submit: Inventory Adjustment has no lines.",
            }
        return {"status": "success", "message": "Inventory Adjustment submitted."}

    # -------------------------------------------------------------------------
    # Post: apply adjustments to inventory master records
    # -------------------------------------------------------------------------
    elif action_slug == "post":
        adj_lines = await get_list("inventory_adjustment_line", {"inventory_adjustment": doc_id}, db=db)
        if not adj_lines:
            return {
                "status": "error",
                "message": "Cannot post: Inventory Adjustment has no lines.",
            }

        # --- Negative inventory guardrail (pre-flight check) ---
        negative_items: list[str] = []
        for line in adj_lines:
            inv_id = line.get("inventory")
            if inv_id:
                current_qty = _to_int(line.get("current_qty"))
                adjusted_qty = _to_int(line.get("adjusted_qty"))
                if current_qty + adjusted_qty < 0:
                    negative_items.append(line.get("item") or line.get("id"))

        if negative_items:
            return {
                "status": "error",
                "message": (
                    f"Post blocked: {len(negative_items)} line(s) would result in negative inventory. "
                    f"Items: {', '.join(negative_items[:5])}{'...' if len(negative_items) > 5 else ''}"
                ),
            }

        try:
            # Inherit location/store/site from the adjustment header for new inventory records
            adj_location = _get_attr(doc, 'location')
            adj_store = _get_attr(doc, 'store')
            adj_site = _get_attr(doc, 'site')

            for line in adj_lines:
                inv_id = line.get("inventory")
                adjusted_qty = _to_int(line.get("adjusted_qty"))

                if inv_id:
                    # --- Case A: Existing Inventory record — additive update ---
                    inv_doc = await get_doc("inventory", inv_id, db)
                    if not inv_doc:
                        return {
                            "status": "error",
                            "message": f"Inventory record '{inv_id}' not found.",
                        }

                    current_actual = _to_int(getattr(inv_doc, 'actual_inv', 0))
                    current_available = _to_int(getattr(inv_doc, 'available_inv', 0))

                    inv_doc.actual_inv = current_actual + adjusted_qty
                    inv_doc.available_inv = current_available + adjusted_qty

                    # Reset freeze/warn flags per business rule §6
                    inv_doc.freeze = False
                    inv_doc.warn = False

                    await save_doc(inv_doc, db, commit=False)

                    # Stock ledger audit trail
                    await ledger_for_adjustment(
                        db=db,
                        adjustment_id=doc_id,
                        item_id=line.get("item") or getattr(inv_doc, 'item', None),
                        qty_change=adjusted_qty,
                        unit_cost=_to_float(line.get("current_rate")),
                        store=getattr(inv_doc, 'store_location', None),
                        site=getattr(inv_doc, 'site', None),
                    )

                else:
                    # --- Case B: No Inventory record — create new master record ---
                    item_id = line.get("item")
                    unit_cost = _to_float(line.get("current_rate"))

                    new_inv = await new_doc("inventory", db,
                        transaction_type="Add",
                        date=datetime.now().date(),
                        item=item_id,
                        asset_tag=line.get("asset_tag"),
                        serial_number=line.get("serial_nos"),
                        bin_location=line.get("bin"),
                        zone=line.get("zone"),
                        unit_of_measure=line.get("uom"),
                        store_location=adj_store,
                        location=adj_location,
                        site=adj_site,
                        base_unit_cost=unit_cost,
                        actual_inv=adjusted_qty,
                        available_inv=adjusted_qty,
                        reserved_inv=0,
                        freeze=False,
                        warn=False,
                    )
                    await save_doc(new_inv, db, commit=False)

                    # Stock ledger audit trail for new inventory
                    await ledger_for_adjustment(
                        db=db,
                        adjustment_id=doc_id,
                        item_id=item_id,
                        qty_change=adjusted_qty,
                        unit_cost=unit_cost,
                        store=adj_store,
                        site=adj_site,
                    )

                    # Update the adjustment line with the new inventory reference
                    adj_line_doc = await get_doc("inventory_adjustment_line", line.get("id"), db)
                    if adj_line_doc:
                        adj_line_doc.inventory = new_inv.id
                        await save_doc(adj_line_doc, db, commit=False)

            # Set posting_datetime on the adjustment header
            adj_doc = await get_doc("inventory_adjustment", doc_id, db)
            if adj_doc:
                adj_doc.posting_datetime = datetime.now()
                await save_doc(adj_doc, db, commit=False)

            await db.commit()

            return {
                "status": "success",
                "message": (
                    f"Inventory Adjustment posted. "
                    f"{len(adj_lines)} inventory record(s) updated/created."
                ),
            }

        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": f"Failed to post Inventory Adjustment: {str(e)}"}

    # -------------------------------------------------------------------------
    # Cancel
    # -------------------------------------------------------------------------
    elif action_slug == "cancel":
        return {"status": "success", "message": "Inventory Adjustment cancelled."}

    return {"status": "success", "message": f"Inventory Adjustment workflow '{action}' allowed"}


# Server actions are auto-registered from entity JSON method paths.
# No manual decorator registration needed here.
