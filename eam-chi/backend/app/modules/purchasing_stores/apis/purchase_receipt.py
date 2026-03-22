"""
Purchase Receipt Entity Business Logic

Server actions:
- confirm_receipt(doc, db, user)         – Validate & process receipt, update inventory & procurement docs
- update_inventory_serialno(doc, db, user) – Batch assign serial numbers to inventory records

Uses document helpers for Frappe-like syntax.
All mutating operations are wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import datetime, date, timedelta
import secrets
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import (
    get_doc, get_value, get_list, new_doc, save_doc, apply_workflow_state,
)
from app.services.stock_ledger import ledger_for_receipt


# =============================================================================
# Confirm Receipt (Server Action)
# =============================================================================

async def confirm_receipt(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Confirm a Purchase Receipt and generate inventory/asset records.

    Business Rules (from full_purch_business_logic.md):
    1. Existence Check – verify receipt, linked PO Line, PR Line, Item Master
    2. Duplicate Prevention – check generated_inventory flag
    3. Item Type Restriction – block Service Item / Non-Inventory Item
    4. Over-Receiving – (current qty + previous received) must not exceed ordered qty
    5. Update PO Line & PR Line qty_received and workflow states
    6. Generate Inventory / Asset / Equipment / Maintenance Request records
    """
    if not doc:
        return {"status": "error", "message": "Purchase Receipt not specified"}

    receipt_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not receipt_id:
        return {"status": "error", "message": "Purchase Receipt ID is required"}

    # --- 1. Duplicate Prevention ---
    if getattr(doc, 'generated_inventory', None) in (True, 1):
        return {"status": "error", "message": "Inventory already generated for this receipt"}

    # --- 2. Existence Checks ---
    po_line_id = getattr(doc, 'purchase_order_line', None)
    if not po_line_id:
        return {"status": "error", "message": "Purchase Order Line is required"}

    po_line = await get_value("purchase_order_line", po_line_id, "*", db)
    if not po_line:
        return {"status": "error", "message": f"PO Line '{po_line_id}' not found"}

    pr_line_id = po_line.get("pr_line_id")
    pr_line = None
    if pr_line_id:
        pr_line = await get_value("purchase_request_line", pr_line_id, "*", db)

    item_id = po_line.get("item_id")
    if not item_id:
        return {"status": "error", "message": "PO Line has no item"}

    item = await get_value("item", item_id, "*", db)
    if not item:
        return {"status": "error", "message": f"Item '{item_id}' not found"}

    # --- 3. Item Type Restriction ---
    # Normalize: DB stores slugified values (e.g. "asset_item"), compare lowercase_underscore
    item_type_raw = item.get("item_type") or ""
    if not item_type_raw:
        return {"status": "error", "message": "Item Type is required on the Item master before confirming receipt. Please set Item Type (e.g. 'Asset Item', 'Inventory Item') on the item and try again."}
    item_type = item_type_raw.strip().lower().replace(" ", "_")
    if item_type in ("service_item", "non_inventory_item"):
        return {"status": "error", "message": f"Cannot generate inventory for {item_type_raw}"}

    # --- 4. Over-Receiving Logic ---
    qty_received = getattr(doc, 'quantity_received', 0) or 0
    if qty_received <= 0:
        return {"status": "error", "message": "Quantity received must be greater than 0"}

    qty_ordered = po_line.get("quantity_ordered") or 0
    prev_received = po_line.get("quantity_received") or 0
    total_after = prev_received + qty_received

    if total_after > qty_ordered:
        remaining = qty_ordered - prev_received
        return {
            "status": "error",
            "message": f"Cannot receive {qty_received} items. Only {remaining} remaining on PO Line."
        }

    try:
        # --- 5. Update PO Line ---
        po_line_doc = await get_doc("purchase_order_line", po_line_id, db)
        if po_line_doc:
            po_line_doc.quantity_received = total_after
            await save_doc(po_line_doc, db, commit=False)

            # Determine receive action slug
            if total_after >= qty_ordered:
                action_slug = "receive_all_items"
            else:
                action_slug = "receive_partial_items"

            wf_result = await apply_workflow_state(
                "purchase_order_line", po_line_doc, action_slug, db, commit=False
            )
            if wf_result.get("status") == "error":
                # If workflow transition fails, just set state directly as fallback
                target_state = "fully_received" if total_after >= qty_ordered else "partially_received"
                po_line_doc.workflow_state = target_state
                await save_doc(po_line_doc, db, commit=False)

        # --- 6. Update PR Line (synchronized movement) ---
        if pr_line_id and pr_line:
            pr_line_doc = await get_doc("purchase_request_line", pr_line_id, db)
            if pr_line_doc:
                current_pr_received = getattr(pr_line_doc, 'qty_received', 0) or 0
                pr_line_doc.qty_received = current_pr_received + qty_received
                await save_doc(pr_line_doc, db, commit=False)

                pr_qty_required = pr_line.get("qty_required") or 0
                if pr_line_doc.qty_received >= pr_qty_required and pr_qty_required > 0:
                    pr_action = "receive_all_items"
                else:
                    pr_action = "receive_partial_items"

                pr_wf = await apply_workflow_state(
                    "purchase_request_line", pr_line_doc, pr_action, db, commit=False
                )
                if pr_wf.get("status") == "error":
                    target = "fully_received" if pr_line_doc.qty_received >= pr_qty_required else "partially_received"
                    pr_line_doc.workflow_state = target
                    await save_doc(pr_line_doc, db, commit=False)

        # --- 7. Update Item master quantities ---
        item_doc = await get_doc("item", item["id"], db)
        if item_doc:
            actual = (getattr(item_doc, 'actual_qty_on_hand', 0) or 0) + qty_received
            reserved = getattr(item_doc, 'reserved_capacity', 0) or 0
            item_doc.actual_qty_on_hand = actual
            item_doc.available_capacity = actual - reserved
            await save_doc(item_doc, db, commit=False)

        # Stock ledger audit trail for receipt
        await ledger_for_receipt(
            db=db,
            receipt_id=receipt_id,
            item_id=item["id"],
            qty=qty_received,
            unit_cost=po_line.get("price") or 0,
            store=None,
            site=getattr(doc, 'site', None),
        )

        # --- 8. Generate Inventory / Asset / Equipment records ---
        site = getattr(doc, 'site', None)
        receiving_location = getattr(doc, 'receiving_location', None)
        base_unit_cost = po_line.get("price") or (pr_line.get("base_currency_unit") if pr_line else None)
        financial_asset_number = po_line.get("financial_asset_number") or (pr_line.get("financial_asset_number") if pr_line else None)
        is_serialized = item.get("is_serialized", False)
        is_equipment = item.get("is_equipment", False)
        inspection_required = item.get("inspection_required", False)

        result = await _generate_records(
            doc=doc,
            item=item,
            item_type=item_type,
            qty_received=qty_received,
            site=site,
            receiving_location=receiving_location,
            base_unit_cost=base_unit_cost,
            financial_asset_number=financial_asset_number,
            is_serialized=is_serialized,
            is_equipment=is_equipment,
            inspection_required=inspection_required,
            pr_line=pr_line or po_line,
            db=db,
        )

        if result.get("status") == "error":
            await db.rollback()
            return result

        # --- 9. Mark receipt as processed ---
        doc.generated_inventory = True
        doc.is_received = True
        await save_doc(doc, db, commit=False)

        await db.commit()
        return result

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Confirm Receipt failed: {str(e)}"}


# =============================================================================
# Update Inventory Serial Numbers (Server Action)
# =============================================================================

async def update_inventory_serialno(doc: Any, db: AsyncSession, user: Any, payload: dict | None = None) -> dict:
    """
    Batch assign serial numbers to inventory records created by confirm_receipt.

    Serial numbers come from the frontend modal via payload:
      payload = {"serial_numbers": [{"inventory_id": "INV-00001", "serial_number": "SN-123"}, ...]}

    Falls back to doc.serial_numbers for backward compatibility.
    """
    if not doc:
        return {"status": "error", "message": "Purchase Receipt not specified"}

    receipt_id = doc.id if hasattr(doc, 'id') else doc.get('id')

    # Prefer payload data (from frontend modal), fall back to doc field
    serial_data = None
    if payload and payload.get("serial_numbers"):
        serial_data = payload["serial_numbers"]
    else:
        serial_data = getattr(doc, 'serial_numbers', None)

    if not serial_data:
        return {"status": "error", "message": f"[Receipt {receipt_id}] No serial number data provided. Submit serial numbers via the modal."}

    if isinstance(serial_data, str):
        import json
        try:
            serial_data = json.loads(serial_data)
        except (json.JSONDecodeError, TypeError):
            return {"status": "error", "message": f"[Receipt {receipt_id}] Invalid serial number data format — expected a JSON list."}

    if not isinstance(serial_data, list):
        return {"status": "error", "message": f"[Receipt {receipt_id}] Serial number data must be a list of {{inventory_id, serial_number}} objects."}

    try:
        updated = 0
        skipped = 0
        assets_updated = 0
        for entry in serial_data:
            inv_id = entry.get("inventory_id")
            serial_num = entry.get("serial_number", "").strip()
            if inv_id and serial_num:
                inv_doc = await get_doc("inventory", inv_id, db)
                if inv_doc:
                    # Update inventory record
                    inv_doc.serial_number = serial_num
                    inv_doc.asset_tag = serial_num
                    await save_doc(inv_doc, db, commit=False)
                    updated += 1
                    
                    # Also update the linked asset record if it exists
                    asset_id = getattr(inv_doc, 'asset', None)
                    if asset_id:
                        asset_doc = await get_doc("asset", asset_id, db)
                        if asset_doc:
                            asset_doc.serial_number = serial_num
                            asset_doc.asset_tag = serial_num
                            await save_doc(asset_doc, db, commit=False)
                            assets_updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1

        await db.commit()
        msg = f"[Receipt {receipt_id}] Updated {updated} inventory serial number(s)"
        if assets_updated > 0:
            msg += f" and {assets_updated} asset serial number(s)"
        msg += "."
        if skipped:
            msg += f" Skipped {skipped} entries (missing inventory_id or serial_number)."
        return {
            "status": "success",
            "message": msg,
            "data": {"updated_count": updated, "assets_updated": assets_updated, "skipped_count": skipped},
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"[Receipt {receipt_id}] Failed to update serial numbers: {str(e)}"}


# =============================================================================
# Record Generation (Internal)
# =============================================================================

async def _generate_records(
    doc: Any,
    item: dict,
    item_type: str,
    qty_received: int,
    site: str,
    receiving_location: str,
    base_unit_cost: float,
    financial_asset_number: str,
    is_serialized: bool,
    is_equipment: bool,
    inspection_required: bool,
    pr_line: dict,
    db: AsyncSession,
) -> dict:
    """
    Generate Inventory / Asset / Equipment / Maintenance records based on
    item type and serialization settings (matrix from business logic doc).
    """
    # item_type is already normalized to lowercase_underscore (e.g. "asset_item")
    is_asset_type = item_type in ("asset_item", "fixed_asset_item")
    is_fixed = item_type == "fixed_asset_item"

    if is_asset_type:
        if is_serialized:
            # 1-to-1: individual Inventory + Asset per unit
            list_inv = []
            for _ in range(qty_received):
                inv = await _create_inventory(base_unit_cost, site, receiving_location, financial_asset_number, item, 1, db, item_type=item_type)
                asset = await _create_asset(inv, item, pr_line, is_fixed, db)

                if inspection_required:
                    await _create_maint_request(asset, pr_line, db)
                else:
                    if is_equipment:
                        asset.workflow_state = "inactive"
                    elif is_fixed:
                        asset.workflow_state = "acquired"
                    else:
                        asset.workflow_state = "acquired"
                    await save_doc(asset, db, commit=False)

                if is_equipment:
                    await _create_equipment(site, inv, item, receiving_location, db)

                list_inv.append(inv.id)

            return {
                "status": "success",
                "message": "Created inventory and asset records",
                "data": {"action": "need_update_serial_num", "inventory_ids": list_inv},
            }
        else:
            # Batch: update existing or create new inventory + single asset
            existing_inv = await get_value("inventory", {"item": item["id"], "location": receiving_location}, "*", db)

            if existing_inv:
                inv_doc = await get_doc("inventory", existing_inv["id"], db)
                if inv_doc:
                    actual = (getattr(inv_doc, 'actual_inv', 0) or 0) + qty_received
                    reserved = getattr(inv_doc, 'reserved_inv', 0) or 0
                    inv_doc.actual_inv = actual
                    inv_doc.available_inv = actual - reserved
                    await save_doc(inv_doc, db, commit=False)

                    # Create asset if not yet linked to this inventory
                    if not getattr(inv_doc, 'asset', None):
                        asset = await _create_asset(inv_doc, item, pr_line, is_fixed, db)
                        if not inspection_required:
                            asset.workflow_state = "inactive" if is_equipment else "acquired"
                            await save_doc(asset, db, commit=False)
                        if is_equipment:
                            await _create_equipment(site, inv_doc, item, receiving_location, db)
                        return {
                            "status": "success",
                            "message": "Updated inventory and created asset record",
                            "data": {"action": "generate_id", "path": f"/asset/{asset.id}"},
                        }

                return {
                    "status": "success",
                    "message": "Updated inventory record",
                    "data": {"action": "generate_id", "path": f"/inventory/{existing_inv['id']}"},
                }
            else:
                inv = await _create_inventory(base_unit_cost, site, receiving_location, financial_asset_number, item, qty_received, db, item_type=item_type)
                asset = await _create_asset(inv, item, pr_line, is_fixed, db)

                if inspection_required:
                    maint_req = await _create_maint_request(asset, pr_line, db)
                    if is_equipment:
                        await _create_equipment(site, inv, item, receiving_location, db)
                    return {
                        "status": "success",
                        "message": "Created inventory, asset and maintenance request",
                        "data": {"action": "generate_id", "path": f"/maintenance_request/{maint_req.id}"},
                    }
                else:
                    asset.workflow_state = "inactive" if is_equipment else "acquired"
                    await save_doc(asset, db, commit=False)
                    if is_equipment:
                        await _create_equipment(site, inv, item, receiving_location, db)
                    return {
                        "status": "success",
                        "message": "Created inventory and asset record",
                        "data": {"action": "generate_id", "path": f"/asset/{asset.id}"},
                    }
    else:
        # Regular inventory item
        if is_serialized:
            list_inv = []
            for _ in range(qty_received):
                inv = await _create_inventory(base_unit_cost, site, receiving_location, financial_asset_number, item, 1, db, item_type=item_type)
                if is_equipment:
                    await _create_equipment(site, inv, item, receiving_location, db)
                list_inv.append(inv.id)

            return {
                "status": "success",
                "message": "Created serialized inventory records",
                "data": {"action": "need_update_serial_num", "inventory_ids": list_inv},
            }
        else:
            existing_inv = await get_value("inventory", {"item": item["id"], "location": receiving_location}, "*", db)

            if existing_inv:
                inv_doc = await get_doc("inventory", existing_inv["id"], db)
                if inv_doc:
                    actual = (getattr(inv_doc, 'actual_inv', 0) or 0) + qty_received
                    reserved = getattr(inv_doc, 'reserved_inv', 0) or 0
                    inv_doc.actual_inv = actual
                    inv_doc.available_inv = actual - reserved
                    await save_doc(inv_doc, db, commit=False)

                return {
                    "status": "success",
                    "message": "Updated inventory record",
                    "data": {"action": "generate_id", "path": f"/inventory/{existing_inv['id']}"},
                }
            else:
                inv = await _create_inventory(base_unit_cost, site, receiving_location, financial_asset_number, item, qty_received, db, item_type=item_type)
                if is_equipment:
                    await _create_equipment(site, inv, item, receiving_location, db)
                return {
                    "status": "success",
                    "message": "Created inventory record",
                    "data": {"action": "generate_id", "path": f"/inventory/{inv.id}"},
                }


# =============================================================================
# Record Creation Helpers
# =============================================================================

async def _create_inventory(
    base_unit_cost: float, site: str, location: str,
    financial_asset_number: str, item: dict, quantity: int, db: AsyncSession,
    item_type: str = "",
) -> Any:
    """Create inventory record."""
    store = await get_value("store", {"location": location}, "*", db)

    new_inventory = await new_doc("inventory", db,
        transaction_type="Add",
        location=location,
        asset_tag=f"Temp-Tag-{secrets.token_hex(3)}",
        store_location=store.get("store") if store else None,
        site=site,
        date=datetime.now(),
        item=item["id"],
        item_name=item.get("item_name"),
        item_type=item_type or item.get("item_type"),
        financial_asset_number=financial_asset_number,
        unit_of_measure=item.get("uom"),
        actual_inv=quantity,
        available_inv=quantity,
        base_unit_cost=base_unit_cost,
    )
    await save_doc(new_inventory, db, commit=False)
    return new_inventory


async def _create_asset(
    inventory: Any, item: dict, pr_line: dict, is_fixed: bool, db: AsyncSession,
) -> Any:
    """Create asset record with property inheritance from asset class."""
    new_asset = await new_doc("asset", db,
        asset_tag=f"Temp-Tag-{secrets.token_hex(3)}",
        description=item.get("item_name"),
        asset_class=item.get("asset_class"),
        location=inventory.location,
        serial_number=getattr(inventory, 'serial_number', None),
        cost=item.get("unit_cost"),
        date_purchased=datetime.now(),
        site=pr_line.get("site"),
        department=pr_line.get("department"),
        workflow_state="acquired",
        inventory=inventory.id,
        is_equipment=item.get("is_equipment"),
        item=item["id"],
        item_type=item.get("item_type"),
    )
    await save_doc(new_asset, db, commit=False)

    # Property inheritance from asset class
    if item.get("asset_class"):
        asset_class_props = await get_list(
            "asset_class_property", {"asset_class": item["asset_class"]}, db=db
        )
        for prop in asset_class_props:
            asset_prop = await new_doc("asset_property", db,
                asset=new_asset.id,
                property=prop.get("property"),
                property_name=prop.get("property_name"),
                unit_of_measure=prop.get("unit_of_measure"),
                property_value=prop.get("default_value"),
            )
            await save_doc(asset_prop, db, commit=False)

    # Bi-directional linking
    inventory.asset = new_asset.id
    await save_doc(inventory, db, commit=False)

    return new_asset


async def _create_maint_request(
    asset: Any, pr_line: dict, db: AsyncSession,
) -> Any:
    """Create maintenance request for asset inspection with auto-approval."""
    get_state = await get_value(
        "request_activity_type", {"menu": "Asset", "state": "Acquired"}, "*", db
    )

    wo_activity = await new_doc("work_order_activity", db,
        description=f"{get_state.get('type', 'Inspect')} for Asset: {asset.asset_tag}" if get_state else f"Inspect Asset: {asset.asset_tag}",
        work_item_type="Asset",
        work_item=asset.id,
        asset_name=getattr(asset, 'description', None),
        activity_type=get_state.get("id") if get_state else None,
        activity_type_name=get_state.get("type") if get_state else None,
        location=asset.location,
        site=pr_line.get("site"),
        department=pr_line.get("department"),
        workflow_state="awaiting_resources",
    )
    await save_doc(wo_activity, db, commit=False)

    due = date.today() + timedelta(days=7)
    maint_request = await new_doc("maintenance_request", db,
        requested_date=datetime.now(),
        request_type=get_state.get("id") if get_state else None,
        asset=asset.id,
        location=asset.location,
        due_date=due,
        site=pr_line.get("site"),
        department=pr_line.get("department"),
        work_order_activity=wo_activity.id,
        workflow_state="draft",
    )
    await save_doc(maint_request, db, commit=False)

    # Auto-approval: Draft → Pending Approval → Approved
    maint_request.workflow_state = "pending_approval"
    await save_doc(maint_request, db, commit=False)
    maint_request.workflow_state = "approved"
    await save_doc(maint_request, db, commit=False)

    return maint_request


async def _create_equipment(
    site: str, inventory: Any, item: dict, location: str, db: AsyncSession,
) -> Any:
    """Create equipment record."""
    equipment = await new_doc("equipment", db,
        equipment_type="Owned",
        inventory=inventory.id,
        description=item.get("item_name"),
        location=location,
        site=site,
    )
    await save_doc(equipment, db, commit=False)
    return equipment
