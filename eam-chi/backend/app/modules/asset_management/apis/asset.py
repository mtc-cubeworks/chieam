"""
Asset Entity Business Logic

After-save hooks:
- populate_asset_names(doc, db)       – kept for compatibility (no-op)
- populate_asset_properties(doc, db)  – inherit properties from Asset Class
- provision_inventory(doc, db)        – auto-create Inventory if bypass enabled

Workflow handler:
- check_asset_workflow(doc, action, db, user)

Action routing (slugs from DB are lowercase):
  inspect_asset, maintain_asset, internal_repair, send_to_vendor
      → WOA + MR (auto submit_for_approval → approve)
  install_asset   → bypass ON: AssetPosition | bypass OFF: WOA + MR
  commission      → AssetPosition (date_installed)
  putaway         → Putaway record
  issue_equipment → ItemIssue record
  remove_asset    → close open AssetPosition (set date_removed)
  dispose         → Disposed record; Fixed Asset: validate open position first
  failed_inspection, complete, finish_repair,
  retire_asset, decommission, recommission → simple (no secondary docs)

All mutating operations wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


# =============================================================================
# Helpers
# =============================================================================

def _ga(doc: Any, attr: str) -> Any:
    """Get attribute from ORM object or dict."""
    if hasattr(doc, attr):
        return getattr(doc, attr)
    if isinstance(doc, dict):
        return doc.get(attr)
    return None


_ACTIVITY_TYPE_MAP = {
    "inspect_asset":   ("Inspection",      "Inspect Asset"),
    "maintain_asset":  ("Maintain Asset",  "Maintain Asset"),
    "internal_repair": ("Internal Repair", "Internal Repair"),
    "send_to_vendor":  ("Send to Vendor",  "Send to Vendor"),
    "install_asset":   ("Install Asset",   "Install Asset"),
    "remove_asset":    ("Remove Asset",    "Remove Asset"),
}


async def _get_activity_type(action_slug: str, db: AsyncSession) -> dict | None:
    """Look up request_activity_type by type or menu, trying multiple fallbacks."""
    entry = _ACTIVITY_TYPE_MAP.get(action_slug)
    if not entry:
        return None
    type_val, menu_val = entry
    rat = await get_value("request_activity_type", {"type": type_val}, "*", db)
    if not rat:
        rat = await get_value("request_activity_type", {"menu": menu_val}, "*", db)
    if not rat:
        rat = await get_value("request_activity_type", {"type": menu_val}, "*", db)
    return rat


async def _create_woa_and_mr(doc: Any, action_slug: str, db: AsyncSession) -> dict:
    """Create Work Order Activity + Maintenance Request, auto-advance MR to approved."""
    rat = await _get_activity_type(action_slug, db)
    if not rat:
        label = _ACTIVITY_TYPE_MAP.get(action_slug, action_slug)
        return {"status": "error", "message": f"Activity type '{label}' not found."}

    try:
        woa = await new_doc("work_order_activity", db,
            description=f"{rat['type']}: {_ga(doc, 'asset_tag')}",
            work_item_type="Asset",
            work_item=_ga(doc, "id"),
            activity_type=rat["id"],
            activity_type_name=rat["type"],
            location=_ga(doc, "location"),
            site=_ga(doc, "site"),
            department=_ga(doc, "department"),
            start_date=datetime.now(),
            workflow_state="awaiting_resources",
        )
        await save_doc(woa, db, commit=False)

        mr = await new_doc("maintenance_request", db,
            requested_date=date.today(),
            request_type=rat["id"],
            asset=_ga(doc, "id"),
            location=_ga(doc, "location"),
            due_date=date.today(),
            site=_ga(doc, "site"),
            department=_ga(doc, "department"),
            work_order_activity=woa.id,
            workflow_state="draft",
        )
        await save_doc(mr, db, commit=False)

        # Auto-advance MR: draft → submit_for_approval → approve
        from app.services.workflow import WorkflowDBService
        _, t1, _ = await WorkflowDBService.validate_transition(
            db, "maintenance_request", "draft", "submit_for_approval"
        )
        if t1:
            mr.workflow_state = t1
        _, t2, _ = await WorkflowDBService.validate_transition(
            db, "maintenance_request", mr.workflow_state, "approve"
        )
        if t2:
            mr.workflow_state = t2

        await db.commit()
        return {
            "status": "success",
            "message": f"Work Order Activity and Maintenance Request created ({mr.id}).",
            "action": "generate_id",
            "path": f"/maintenance_request/{mr.id}",
            "data": {"maintenance_request_id": mr.id, "work_order_activity_id": woa.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create WOA/MR: {str(e)}"}


# =============================================================================
# AFTER-SAVE HOOKS
# =============================================================================

async def populate_asset_names(doc: dict, db: AsyncSession) -> dict:
    """Kept for compatibility — no-op."""
    return doc


async def populate_asset_properties(doc: Any, db: AsyncSession) -> None:
    """Inherit Asset Class Properties on first save (idempotent)."""
    asset_class_id = _ga(doc, "asset_class")
    if not asset_class_id:
        return
    existing = await get_list("asset_property", {"asset": doc.id}, db=db, as_dict=False)
    if existing:
        return
    class_props = await get_list(
        "asset_class_property", {"asset_class": asset_class_id}, db=db, as_dict=False
    )
    for cp in class_props:
        prop = await new_doc("asset_property", db,
            asset=doc.id,
            property=cp.property,
            unit_of_measure=cp.unit_of_measure,
            property_value=cp.default_value,
        )
        if prop:
            await save_doc(prop, db, commit=False)
    if class_props:
        await db.commit()


async def provision_inventory(doc: Any, db: AsyncSession) -> None:
    """
    Auto-create Inventory when bypass_process=True and no inventory linked.
    Syncs asset_tag to existing inventory if already linked.
    """
    asset_id = _ga(doc, "id")
    if not asset_id:
        return

    existing_inv_id = _ga(doc, "inventory")

    if existing_inv_id:
        inv_doc = await get_doc("inventory", existing_inv_id, db)
        if inv_doc:
            asset_tag = _ga(doc, "asset_tag")
            if asset_tag and getattr(inv_doc, "asset_tag", None) != asset_tag:
                inv_doc.asset_tag = asset_tag
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
        return

    if not _ga(doc, "bypass_process"):
        return

    try:
        inv = await new_doc("inventory", db,
            asset_tag=_ga(doc, "asset_tag"),
            serial_number=_ga(doc, "serial_number"),
            item=_ga(doc, "item"),
            site=_ga(doc, "site"),
            actual_inv=1,
            freeze=False,
            warn=False,
        )
        await save_doc(inv, db, commit=False)
        asset_doc = await get_doc("asset", asset_id, db)
        if asset_doc:
            asset_doc.inventory = inv.id
        await db.commit()
    except Exception:
        await db.rollback()


# =============================================================================
# WORKFLOW HANDLER
# =============================================================================

async def check_asset_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Main workflow handler for Asset entity.
    `action` is the human-readable label from DB (e.g. "Inspect Asset").
    Normalize to slug for routing.
    """
    action_slug = action.lower().replace(" ", "_")

    simple = {
        "failed_inspection", "complete", "finish_repair",
        "retire_asset", "decommission", "recommission",
    }
    if action_slug in simple:
        return {"status": "success", "message": f"Asset transition '{action}' allowed."}

    if action_slug in ("inspect_asset", "maintain_asset", "internal_repair", "send_to_vendor"):
        return await _create_woa_and_mr(doc, action_slug, db)

    if action_slug == "install_asset":
        return await _handle_install_asset(doc, db)

    if action_slug == "commission":
        return await _handle_commission(doc, db)

    if action_slug == "putaway":
        return await _handle_putaway(doc, db)

    if action_slug == "issue_equipment":
        return await _handle_issue_equipment(doc, db)

    if action_slug == "remove_asset":
        return await _handle_remove_asset(doc, db)

    if action_slug == "dispose":
        return await _handle_dispose(doc, db)

    return {"status": "success", "message": f"Asset workflow '{action}' allowed."}


# =============================================================================
# Action handlers
# =============================================================================

async def _handle_install_asset(doc: Any, db: AsyncSession) -> dict:
    """
    Install Asset:
    - Validates no open AssetPosition exists for this asset.
    - bypass_process ON  → directly create AssetPosition
    - bypass_process OFF → create WOA + MR (formal approval path)
    """
    asset_id = _ga(doc, "id")

    # Removal validation: must close open position before re-installing
    open_positions = await get_list("asset_position", {"asset": asset_id}, db=db)
    for pos in open_positions:
        if not pos.get("date_removed"):
            return {
                "status": "error",
                "message": (
                    "Asset still has an open position record. "
                    "Set 'Date Removed' on the existing Asset Position before installing again."
                ),
            }

    if _ga(doc, "bypass_process"):
        return await _handle_commission(doc, db)
    else:
        return await _create_woa_and_mr(doc, "install_asset", db)


async def _handle_commission(doc: Any, db: AsyncSession) -> dict:
    """Create AssetPosition with date_installed = today (Fixed Asset commissioning)."""
    try:
        pos = await new_doc("asset_position", db,
            asset=_ga(doc, "id"),
            date_installed=date.today(),
        )
        await save_doc(pos, db, commit=True)
        return {
            "status": "success",
            "message": f"Asset Position created ({pos.id}).",
            "action": "generate_id",
            "path": f"/asset_position/{pos.id}",
            "data": {"asset_position_id": pos.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Asset Position: {str(e)}"}


async def _handle_putaway(doc: Any, db: AsyncSession) -> dict:
    """Create Putaway record linked to the asset's inventory."""
    inv_id = _ga(doc, "inventory")
    if not inv_id:
        return {"status": "error", "message": "Asset has no inventory record linked."}

    inventory = await get_value("inventory", inv_id, "*", db)
    if not inventory:
        return {"status": "error", "message": f"Inventory record {inv_id} not found."}

    try:
        putaway = await new_doc("putaway", db,
            putaway_type="Asset",
            source_data_asset=_ga(doc, "id"),
            item=inventory.get("item"),
            serial_number=inventory.get("serial_number"),
            qty=inventory.get("actual_inv") or 1,
            site=_ga(doc, "site"),
        )
        await save_doc(putaway, db, commit=True)
        return {
            "status": "success",
            "message": f"Putaway record created ({putaway.id}).",
            "action": "generate_id",
            "path": f"/putaway/{putaway.id}",
            "data": {"putaway_id": putaway.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Putaway: {str(e)}"}


async def _handle_issue_equipment(doc: Any, db: AsyncSession) -> dict:
    """
    Create ItemIssue for issuing equipment from store.
    item_issue table has: issue_type, issue_to, date_issued, work_order_activity, site, department.
    """
    try:
        item_issue = await new_doc("item_issue", db,
            issue_type="Asset",
            site=_ga(doc, "site"),
            department=_ga(doc, "department"),
            date_issued=date.today(),
            workflow_state="draft",
        )
        await save_doc(item_issue, db, commit=True)
        return {
            "status": "success",
            "message": f"Item Issue created ({item_issue.id}).",
            "action": "generate_id",
            "path": f"/item_issue/{item_issue.id}",
            "data": {"item_issue_id": item_issue.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Item Issue: {str(e)}"}


async def _handle_remove_asset(doc: Any, db: AsyncSession) -> dict:
    """
    Close the most recent open AssetPosition by setting date_removed = today.
    """
    asset_id = _ga(doc, "id")
    open_positions = await get_list("asset_position", {"asset": asset_id}, db=db)

    open_pos = None
    for pos in open_positions:
        if not pos.get("date_removed"):
            open_pos = pos
            break

    if not open_pos:
        return {"status": "success", "message": "No open Asset Position found — transition allowed."}

    try:
        pos_doc = await get_doc("asset_position", open_pos["id"], db)
        if pos_doc:
            pos_doc.date_removed = date.today()
            await db.commit()
        return {
            "status": "success",
            "message": f"Asset Position {open_pos['id']} closed (date_removed set).",
            "action": "generate_id",
            "path": f"/asset_position/{open_pos['id']}",
            "data": {"asset_position_id": open_pos["id"]},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to close Asset Position: {str(e)}"}


async def _handle_dispose(doc: Any, db: AsyncSession) -> dict:
    """
    Dispose asset:
    - Fixed Asset Item: validate no open AssetPosition (must be removed first).
    - Create Disposed record.
    """
    asset_id = _ga(doc, "id")
    item_type = _ga(doc, "item_type")

    # Fixed Asset: must have closed all positions before disposal
    if item_type == "Fixed Asset Item":
        open_positions = await get_list("asset_position", {"asset": asset_id}, db=db)
        for pos in open_positions:
            if not pos.get("date_removed"):
                return {
                    "status": "error",
                    "message": (
                        "Cannot dispose Fixed Asset: asset is still installed at a position. "
                        "Remove the asset from its position before disposing."
                    ),
                }

    try:
        disposed = await new_doc("disposed", db,
            asset=asset_id,
            disposal_date=date.today(),
            disposal_reason="Asset disposed via workflow",
            disposal_method="Scrap",
            disposal_status="Draft",
            site=_ga(doc, "site"),
        )
        await save_doc(disposed, db, commit=True)
        return {
            "status": "success",
            "message": f"Disposed record created ({disposed.id}).",
            "action": "generate_id",
            "path": f"/disposed/{disposed.id}",
            "data": {"disposed_id": disposed.id},
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to create Disposed record: {str(e)}"}
