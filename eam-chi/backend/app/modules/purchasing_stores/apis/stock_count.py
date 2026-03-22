"""
Stock Count Entity Business Logic

Server actions:
- find_stock_count_lines(doc, db, user) – Fetch inventory records and create Stock Count Lines

Workflow handlers (called from workflow_router.py):
- check_stock_count_workflow(doc, action, db, user)
    - "Start Stock Count": capture snapshot_at, apply freeze/warn policy to inventory
    - "Approve": validate no negative inventory, create Inventory Adjustment (selective posting)
    - "Complete": final close, no additional logic

Uses document helpers for Frappe-like syntax.
All mutating operations are wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


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
# Find Stock Count Lines (Server Action)
# =============================================================================

async def find_stock_count_lines(doc: Any, db: AsyncSession, user: Any = None) -> dict:
    """
    Fetch inventory records and create Stock Count Lines.

    Business Rules:
    - Only available in "Planned" state (enforced by show_when in JSON)
    - Basis Full: all inventory in the selected store
    - Basis ABC: inventory filtered by item ABC code
    - Basis Selection: user manually adds lines (this action is a no-op for Selection)
    - Exclude inventory already linked to an "In Progress" stock count (mutual exclusivity)
    - Exclude inventory with freeze or warn flags already set
    - Prevent duplicate lines (same stock_count + item + bin + zone)
    - snapshot_qty = actual_inv from inventory (hidden if Method = Blind)
    """
    if not doc:
        return {"status": "error", "message": "Document is required."}

    doc_id = _get_id(doc)
    basis = _get_attr(doc, 'basis')
    store = _get_attr(doc, 'store')
    method = _get_attr(doc, 'method')

    if not doc_id:
        return {"status": "error", "message": "Missing stock count ID."}
    if not basis:
        return {"status": "error", "message": "Basis is required (Full | ABC | Selection)."}

    if basis == 'Selection':
        return {
            "status": "success",
            "message": "Basis is 'Selection' — add lines manually.",
            "created_count": 0,
        }

    # --- Fetch candidate inventory records ---
    inventory_lines: list[dict] = []

    if basis == 'Full':
        if not store:
            return {"status": "error", "message": "Store is required for Full basis."}
        inventory_lines = await get_list("inventory", {"store_location": store}, db=db)

    elif basis == 'ABC':
        abc_code = _get_attr(doc, 'abc_code')
        if not abc_code:
            return {"status": "error", "message": "ABC Code is required for ABC basis."}
        if not store:
            return {"status": "error", "message": "Store is required for ABC basis."}

        items_with_abc = await get_list("item", {"abc_code": abc_code}, db=db)
        item_ids = {item["id"] for item in items_with_abc}
        if not item_ids:
            return {
                "status": "success",
                "message": f"No items found with ABC code '{abc_code}'.",
                "created_count": 0,
            }

        all_inventory = await get_list("inventory", {"store_location": store}, db=db)
        inventory_lines = [inv for inv in all_inventory if inv.get("item") in item_ids]

    # --- Filter out inventory already frozen/warned by another process ---
    unfrozen = [l for l in inventory_lines if not l.get('freeze') and not l.get('warn')]
    excluded_frozen_warn = len(inventory_lines) - len(unfrozen)

    created = 0
    skipped_duplicates = 0
    excluded_in_progress = 0
    created_names: list[str] = []

    try:
        for inv in unfrozen:
            inv_id = inv.get("id")
            inv_item = inv.get("item")
            inv_bin = inv.get("bin_location")
            inv_zone = inv.get("zone")

            # --- Mutual exclusivity: skip if item/bin/zone is in another "In Progress" SC ---
            sibling_lines = await get_list("stock_count_line", {
                "item": inv_item,
                "bin": inv_bin,
                "zone": inv_zone,
            }, db=db)

            skip_line = False
            for scl in sibling_lines:
                parent_sc_id = scl.get("stock_count")
                if parent_sc_id and parent_sc_id != doc_id:
                    sc_state = await get_value("stock_count", parent_sc_id, "workflow_state", db)
                    if sc_state and sc_state.lower().replace(" ", "_") == "in_progress":
                        excluded_in_progress += 1
                        skip_line = True
                        break

            if skip_line:
                continue

            # --- Duplicate prevention within this stock count ---
            existing = await get_list("stock_count_line", {
                "stock_count": doc_id,
                "item": inv_item,
                "bin": inv_bin,
                "zone": inv_zone,
            }, db=db)
            if existing:
                skipped_duplicates += 1
                continue

            # snapshot_qty: always capture actual_inv; frontend hides it when Method=Blind
            snapshot_qty = _to_int(inv.get("actual_inv"))

            sc_line = await new_doc("stock_count_line", db,
                stock_count=doc_id,
                inventory=inv_id,
                item=inv_item,
                asset_tag=inv.get("asset_tag"),
                serial_nos=inv.get("serial_number"),
                bin=inv_bin,
                zone=inv_zone,
                uom=inv.get("unit_of_measure"),
                snapshot_qty=snapshot_qty,
                counted_qty=0,
                variance_qty=0,
                variance_value=0.0,
            )
            await save_doc(sc_line, db, commit=False)
            created += 1
            created_names.append(sc_line.id)

        await db.commit()

        return {
            "status": "success",
            "message": (
                f"Created {created} Stock Count Line(s). "
                f"Skipped {skipped_duplicates} duplicate(s). "
                f"Excluded {excluded_frozen_warn} frozen/warned and "
                f"{excluded_in_progress} in-progress item(s)."
            ),
            "created_count": created,
            "skipped_duplicates": skipped_duplicates,
            "excluded_frozen_warn": excluded_frozen_warn,
            "excluded_in_progress": excluded_in_progress,
            "created_names": created_names,
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Stock Count Lines: {str(e)}"}


# =============================================================================
# Stock Count Workflow Handler
# =============================================================================

async def check_stock_count_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Workflow handler for Stock Count.

    States: Planned → In Progress → Approved → Closed

    "Start Stock Count":
        - Capture snapshot_at = now()
        - Apply freeze_policy to all linked inventory records

    "Approve":
        - Validate no line would result in negative inventory (snapshot_qty + variance_qty >= 0)
        - Create Inventory Adjustment with selective posting (only lines where variance_qty != 0
          or inventory record is missing)
        - Redirect to the created Inventory Adjustment

    "Complete":
        - Final close; no additional logic required
    """
    if not doc:
        return {"status": "error", "message": "Stock Count not specified"}

    doc_id = _get_id(doc)
    if not doc_id:
        return {"status": "error", "message": "Stock Count ID is required."}

    # -------------------------------------------------------------------------
    # Start Stock Count: capture snapshot_at + apply freeze policy
    # -------------------------------------------------------------------------
    action_slug = action.lower().replace(" ", "_")

    if action_slug == "start_stock_count":
        freeze_policy = _get_attr(doc, 'freeze_policy') or 'None'

        try:
            # Capture snapshot timestamp on the stock count itself
            sc_doc = await get_doc("stock_count", doc_id, db)
            if sc_doc:
                sc_doc.snapshot_at = datetime.now()
                await save_doc(sc_doc, db, commit=False)

            if freeze_policy in ('Freeze', 'Warn'):
                sc_lines = await get_list("stock_count_line", {"stock_count": doc_id}, db=db)
                for line in sc_lines:
                    inv_id = line.get("inventory")
                    if not inv_id:
                        continue
                    inv_doc = await get_doc("inventory", inv_id, db)
                    if not inv_doc:
                        continue

                    # Mutual exclusivity: setting one policy clears the other
                    if freeze_policy == 'Freeze':
                        inv_doc.freeze = True
                        inv_doc.warn = False
                    else:  # Warn
                        inv_doc.freeze = False
                        inv_doc.warn = True

                    await save_doc(inv_doc, db, commit=False)

            await db.commit()
            return {
                "status": "success",
                "message": f"Stock Count started. Snapshot captured. Freeze policy '{freeze_policy}' applied.",
            }

        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": f"Failed to start Stock Count: {str(e)}"}

    # -------------------------------------------------------------------------
    # Approve: validate + create Inventory Adjustment (selective posting)
    # -------------------------------------------------------------------------
    elif action_slug == "approve":
        stock_lines = await get_list("stock_count_line", {"stock_count": doc_id}, db=db)
        if not stock_lines:
            return {"status": "error", "message": "Cannot approve: Stock Count has no lines."}

        # --- Negative inventory guardrail ---
        negative_items: list[str] = []
        for row in stock_lines:
            snapshot = _to_int(row.get("snapshot_qty"))
            variance = _to_int(row.get("variance_qty"))
            if snapshot + variance < 0:
                negative_items.append(row.get("item") or row.get("id"))

        if negative_items:
            return {
                "status": "error",
                "message": (
                    f"Approval blocked: {len(negative_items)} line(s) would result in negative inventory. "
                    f"Items: {', '.join(negative_items[:5])}{'...' if len(negative_items) > 5 else ''}"
                ),
            }

        # --- Selective posting: only lines with variance != 0 or missing inventory ---
        posting_lines = [
            row for row in stock_lines
            if _to_int(row.get("variance_qty")) != 0 or not row.get("inventory")
        ]

        if not posting_lines:
            return {
                "status": "success",
                "message": "Stock Count approved. No variance lines to post (all quantities match).",
            }

        try:
            store_id = _get_attr(doc, 'store')
            site_id = _get_attr(doc, 'site')

            # Resolve location from store
            location_id = None
            if store_id:
                store_doc = await get_doc("store", store_id, db)
                if store_doc:
                    location_id = getattr(store_doc, 'location', None)

            # Create Inventory Adjustment header
            inv_adj = await new_doc("inventory_adjustment", db,
                workflow_state="Draft",
                reference_doctype="Inventory",
                location=location_id,
                store=store_id,
                site=site_id,
                source_stock_count=doc_id,
                remarks=f"Generated from Stock Count: {doc_id}",
            )
            await save_doc(inv_adj, db, commit=False)

            # Create Inventory Adjustment Lines
            for row in posting_lines:
                item_id = row.get("item")
                unit_cost = 0.0
                if item_id:
                    item_data = await get_value("item", item_id, "*", db)
                    if item_data:
                        unit_cost = _to_float(item_data.get("unit_cost") or item_data.get("base_unit_cost"))

                variance_qty = _to_int(row.get("variance_qty"))
                variance_value = _to_float(row.get("variance_value")) or (variance_qty * unit_cost)

                adj_line = await new_doc("inventory_adjustment_line", db,
                    inventory_adjustment=inv_adj.id,
                    inventory=row.get("inventory") or None,
                    item=item_id,
                    asset_tag=row.get("asset_tag"),
                    serial_nos=row.get("serial_nos"),
                    bin=row.get("bin"),
                    zone=row.get("zone"),
                    uom=row.get("uom"),
                    current_qty=_to_int(row.get("snapshot_qty")),
                    adjusted_qty=variance_qty,
                    current_rate=unit_cost,
                    delta_value=variance_value,
                )
                await save_doc(adj_line, db, commit=False)

                # Mark stock count line as reconciled
                sc_line_doc = await get_doc("stock_count_line", row.get("id"), db)
                if sc_line_doc:
                    sc_line_doc.is_reconciled = True
                    await save_doc(sc_line_doc, db, commit=False)

            await db.commit()

            return {
                "status": "success",
                "message": (
                    f"Stock Count approved. Inventory Adjustment {inv_adj.id} created "
                    f"with {len(posting_lines)} line(s)."
                ),
                "action": "generate_id",
                "path": f"/inventory_adjustment/{inv_adj.id}",
            }

        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": f"Failed to approve Stock Count: {str(e)}"}

    # -------------------------------------------------------------------------
    # Complete: final close
    # -------------------------------------------------------------------------
    elif action_slug == "complete":
        return {"status": "success", "message": "Stock Count closed."}

    return {"status": "success", "message": f"Stock Count workflow '{action}' allowed"}


# Also handle mutual-exclusivity check using lowercase slug in get_value call
# (the sc_state from DB is already lowercase)



# =============================================================================
# Server Action Registration
# =============================================================================

from app.services.server_actions import server_actions, ActionContext


@server_actions.register("stock_count", "find_stock_count_lines")
async def find_stock_count_lines_action(ctx: ActionContext):
    """Server action wrapper for find_stock_count_lines."""
    doc = ctx.params.get("doc")
    return await find_stock_count_lines(doc, ctx.db, ctx.user)
