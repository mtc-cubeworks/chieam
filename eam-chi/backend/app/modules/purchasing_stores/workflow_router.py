"""
Purchasing & Stores Module - Central Workflow Router
=====================================================
Single entry point for all workflow logic in the Purchasing & Stores module.

This module centralizes workflow routing so that:
1. All entity workflow handlers are discoverable in one place
2. Business rules are consistently applied
3. New entities can be added by registering a handler function

Each handler follows the signature:
    async def handler(doc, action, db, user) -> dict

Action strings use **human-readable labels** (e.g. "Submit for Approval")
matching the workflow_actions.label column in the database.  The slug is
only used internally by apply_workflow_state().

Returns:
    {"status": "success"|"error", "message": str, ...}

Error handling:
    Every handler MUST wrap mutating work in try/except and call
    ``await db.rollback()`` before returning an error so that partial
    writes are never persisted.
"""
from typing import Any, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession


# Type alias for workflow handler functions
WorkflowHandler = Callable[[Any, str, AsyncSession, Any], Awaitable[dict]]

# Registry of workflow handlers per entity
_WORKFLOW_HANDLERS: dict[str, WorkflowHandler] = {}


def register_workflow(entity: str):
    """Decorator to register a workflow handler for an entity."""
    def decorator(func: WorkflowHandler) -> WorkflowHandler:
        _WORKFLOW_HANDLERS[entity] = func
        return func
    return decorator


async def route_workflow(entity: str, doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Central workflow router for the Purchasing & Stores module.

    Dispatches to the appropriate handler based on entity name.
    Returns a success pass-through if no handler is registered.
    """
    handler = _WORKFLOW_HANDLERS.get(entity)
    if handler:
        return await handler(doc, action, db, user)
    return {"status": "success", "message": f"No workflow handler for '{entity}'"}


# =============================================================================
# Helpers
# =============================================================================

def _get_id(doc: Any) -> str | None:
    """Extract ID from doc (model instance or dict)."""
    return doc.id if hasattr(doc, 'id') else doc.get('id') if isinstance(doc, dict) else None


def _get_attr(doc: Any, attr: str) -> Any:
    """Get attribute from model instance or dict."""
    if hasattr(doc, attr):
        return getattr(doc, attr)
    if isinstance(doc, dict):
        return doc.get(attr)
    return None


async def _apply_line_workflow(
    entity: str,
    line_id: str,
    action_slug: str,
    db: "AsyncSession",
) -> dict:
    """
    Apply a workflow transition to a single child line via apply_workflow_state.
    Returns the result dict from apply_workflow_state.
    """
    from app.services.document import get_doc, apply_workflow_state

    line_doc = await get_doc(entity, line_id, db)
    if not line_doc:
        return {"status": "error", "message": f"{entity} '{line_id}' not found"}

    result = await apply_workflow_state(entity, line_doc, action_slug, db, commit=False)
    return result


async def _auto_close_parent(
    parent_entity: str,
    parent_id: str,
    child_entity: str,
    child_fk_field: str,
    close_action_slug: str,
    db: "AsyncSession",
) -> dict | None:
    """
    Check if all child lines of a parent are 'complete'.
    If so, automatically close the parent entity via apply_workflow_state.
    Returns a result dict if parent was closed, None otherwise.
    """
    from app.services.document import get_doc, get_list, apply_workflow_state

    children = await get_list(child_entity, {child_fk_field: parent_id}, db=db)
    if not children:
        return None

    all_complete = all(c.get("workflow_state") == "complete" for c in children)
    if not all_complete:
        return None

    parent_doc = await get_doc(parent_entity, parent_id, db)
    if not parent_doc:
        return None

    result = await apply_workflow_state(parent_entity, parent_doc, close_action_slug, db, commit=False)
    if result["status"] != "success":
        return None

    return {
        "status": "success",
        "message": f"{parent_entity} automatically closed (all lines complete)",
        "auto_closed": True,
        "parent_entity": parent_entity,
        "parent_id": parent_id,
    }


# =============================================================================
# Purchase Request Workflow
# =============================================================================

@register_workflow("purchase_request")
async def purchase_request_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Request workflow handler.

    States: Draft → Pending Review → Pending Approval → Approved → Closed
                                                      → Rejected → Draft (revise)

    Business Rules:
    - Cannot advance from Draft without at least one PR Line
    - Submit for Review: lines remain in Draft
    - Submit for Approval: moves lines to 'pending_approval' via apply_workflow_state
    - Approve: moves lines to 'approved' via apply_workflow_state
    - Reject Purchase Request: moves all lines to 'rejected'
    - Close: requires all lines in 'complete' state
    - Revise Purchase Request: PR becomes editable, rejected lines stay locked
    """
    from app.services.document import get_list

    if not doc:
        return {"status": "error", "message": "Purchase Request not specified"}

    pr_id = _get_id(doc)
    if not pr_id:
        return {"status": "error", "message": "Purchase Request ID is required"}

    try:
        pr_lines = await get_list("purchase_request_line", {"purchase_request": pr_id}, db=db)

        # Line requirement validation for forward transitions
        if action in ("Submit for Review", "Submit for Approval", "Approve") and not pr_lines:
            return {"status": "error", "message": "Cannot proceed: Purchase Request has no lines"}

        if action == "Submit for Review":
            return {"status": "success", "message": "Purchase Request submitted for review"}

        elif action == "Submit for Approval":
            for line in pr_lines:
                if line.get("workflow_state") != "rejected":
                    result = await _apply_line_workflow(
                        "purchase_request_line", line["id"], "add_line_item", db
                    )
                    if result["status"] == "error":
                        await db.rollback()
                        return result
            return {"status": "success", "message": "All Purchase Request Lines moved to Pending Approval"}

        elif action == "Approve":
            for line in pr_lines:
                if line.get("workflow_state") not in ("rejected", "approved"):
                    result = await _apply_line_workflow(
                        "purchase_request_line", line["id"], "approve_line", db
                    )
                    if result["status"] == "error":
                        await db.rollback()
                        return result
            return {"status": "success", "message": "All Purchase Request Lines approved"}

        elif action == "Reject Purchase Request":
            for line in pr_lines:
                if line.get("workflow_state") not in ("rejected",):
                    result = await _apply_line_workflow(
                        "purchase_request_line", line["id"], "reject_line", db
                    )
                    if result["status"] == "error":
                        await db.rollback()
                        return result
            return {"status": "success", "message": "All Purchase Request Lines rejected"}

        elif action == "Close":
            incomplete = [l for l in pr_lines if l.get("workflow_state") not in ("complete", "rejected")]
            if incomplete:
                return {
                    "status": "error",
                    "message": f"Cannot close: {len(incomplete)} line(s) are not complete"
                }
            return {"status": "success", "message": "Purchase Request closed"}

        elif action == "Revise Purchase Request":
            return {"status": "success", "message": "Purchase Request reverted to Draft for revision"}

        return {"status": "success", "message": f"Purchase Request workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Purchase Request workflow error: {str(e)}"}


# =============================================================================
# Purchase Order Workflow
# =============================================================================

@register_workflow("purchase_order")
async def purchase_order_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Order workflow handler.

    States: Draft → Open → Closed / Cancelled
                  → Rejected

    Business Rules:
    - Draft → Open (Approve): all PO Lines move to 'approved' (not editable, cannot add lines)
    - Draft → Rejected (Reject): all PO Lines move to 'rejected' (not editable, cannot add lines)
    - Open → Closed (Complete): only when ALL PO Lines are 'complete'
    - Open → Cancelled (Cancel): only if all PO Lines are still 'approved' (no receiving in progress).
      Once cancelled, all PO Lines become 'cancelled'.
      NOTE FOR REVIEW: what happens if one PO line is not in 'approved' state when trying to cancel?
    """
    from app.services.document import get_list

    if not doc:
        return {"status": "error", "message": "Purchase Order not specified"}

    po_id = _get_id(doc)
    if not po_id:
        return {"status": "error", "message": "Purchase Order ID is required"}

    try:
        po_lines = await get_list("purchase_order_line", {"po_id": po_id}, db=db)
        if action == "Approve":
            # Draft → Open: move all PO lines to 'approved'
            for line in po_lines:
                result = await _apply_line_workflow(
                    "purchase_order_line", line["id"], "approve_line", db
                )
                if result["status"] == "error":
                    await db.rollback()
                    return result
            return {"status": "success", "message": "Purchase Order approved, all lines moved to Approved"}

        elif action == "Reject":
            # Draft → Rejected: move all PO lines to 'rejected'
            for line in po_lines:
                result = await _apply_line_workflow(
                    "purchase_order_line", line["id"], "reject_line", db
                )
                if result["status"] == "error":
                    await db.rollback()
                    return result
            return {"status": "success", "message": "Purchase Order rejected, all lines rejected"}

        elif action == "Complete":
            # Open → Closed: only when all PO Lines are 'complete'
            incomplete = [l for l in po_lines if l.get("workflow_state") != "complete"]
            if incomplete:
                return {
                    "status": "error",
                    "message": f"Cannot close: {len(incomplete)} line(s) are not complete"
                }
            return {"status": "success", "message": "Purchase Order closed"}

        elif action == "Cancel":
            # Open → Cancelled: only if all lines are still in 'approved' state
            # NOTE FOR REVIEW: what happens if one PO line is not in 'approved' state?
            non_approved = [
                l for l in po_lines
                if l.get("workflow_state") not in ("approved", "draft")
            ]
            if non_approved:
                return {
                    "status": "error",
                    "message": (
                        f"Cannot cancel: {len(non_approved)} line(s) have progressed beyond Approved state. "
                        "Cancel is only allowed when all lines are still in Approved state."
                    )
                }
            for line in po_lines:
                result = await _apply_line_workflow(
                    "purchase_order_line", line["id"], "cancel", db
                )
                if result["status"] == "error":
                    await db.rollback()
                    return result
            return {"status": "success", "message": "Purchase Order cancelled, all lines cancelled"}

        return {"status": "success", "message": f"Purchase Order workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Purchase Order workflow error: {str(e)}"}


# =============================================================================
# Purchase Order Line Workflow
# =============================================================================

@register_workflow("purchase_order_line")
async def purchase_order_line_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Order Line workflow handler.

    States: Draft → Approved → Partially Received → Fully Received → Complete → (auto-close PO)
                   → Rejected
                   → Cancelled

    Business Rules:
    - PO Line and PR Line move at the same time (synchronized)
    - Only Purchase Receipt can change receipt-related states
    - Fully Received / Partially Received based on qty_received vs qty_ordered
    - On every 'Complete' transition: check if ALL PO lines in parent PO are complete,
      if so, auto-close the PO header. Copy same logic to PR Lines.
    - If a PO line is manually cancelled, hide Purchase Receipt tab in PO form
    """
    from app.services.document import get_doc, apply_workflow_state

    if not doc:
        return {"status": "error", "message": "Purchase Order Line not specified"}

    pol_id = _get_id(doc)
    if not pol_id:
        return {"status": "error", "message": "Purchase Order Line ID is required"}

    try:
        if action == "Complete":
            # Fully Received → Complete
            # After completing this line, check if all sibling PO lines are complete
            po_id = _get_attr(doc, 'po_id')
            if po_id:
                auto_result = await _auto_close_parent(
                    parent_entity="purchase_order",
                    parent_id=po_id,
                    child_entity="purchase_order_line",
                    child_fk_field="po_id",
                    close_action_slug="complete",
                    db=db,
                )
                if auto_result:
                    # Also try to auto-close the linked PR
                    pr_line_id = _get_attr(doc, 'pr_line_id')
                    if pr_line_id:
                        pr_line_doc = await get_doc("purchase_request_line", pr_line_id, db)
                        if pr_line_doc:
                            pr_id = _get_attr(pr_line_doc, 'purchase_request')
                            if pr_id:
                                await _auto_close_parent(
                                    parent_entity="purchase_request",
                                    parent_id=pr_id,
                                    child_entity="purchase_request_line",
                                    child_fk_field="purchase_request",
                                    close_action_slug="close",
                                    db=db,
                                )
                    return auto_result

            return {"status": "success", "message": "Purchase Order Line completed"}

        elif action == "Cancel":
            return {"status": "success", "message": "Purchase Order Line cancelled"}

        return {"status": "success", "message": f"Purchase Order Line workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Purchase Order Line workflow error: {str(e)}"}


# =============================================================================
# Purchase Request Line Workflow
# =============================================================================

@register_workflow("purchase_request_line")
async def purchase_request_line_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Request Line workflow handler.

    Business Rules:
    - On every 'Complete' transition: check if ALL PR lines in parent PR are complete,
      if so, auto-close the PR header.
    """
    if not doc:
        return {"status": "error", "message": "Purchase Request Line not specified"}

    prl_id = _get_id(doc)
    if not prl_id:
        return {"status": "error", "message": "Purchase Request Line ID is required"}

    try:
        if action == "Complete":
            pr_id = _get_attr(doc, 'purchase_request')
            if pr_id:
                auto_result = await _auto_close_parent(
                    parent_entity="purchase_request",
                    parent_id=pr_id,
                    child_entity="purchase_request_line",
                    child_fk_field="purchase_request",
                    close_action_slug="close",
                    db=db,
                )
                if auto_result:
                    return auto_result

            return {"status": "success", "message": "Purchase Request Line completed"}

        return {"status": "success", "message": f"Purchase Request Line workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Purchase Request Line workflow error: {str(e)}"}


# =============================================================================
# RFQ Workflow
# =============================================================================

@register_workflow("request_for_quotation")
async def rfq_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Request For Quotation workflow handler.

    States: Draft → Sourcing → Review → Awarded → Order
                                       → Cancelled

    Business Rules:
    - Cannot Submit Source if there are no RFQ lines
    - Cannot award if Awarded Vendor is null or empty
    - Awarded state: cannot add/edit lines, cannot edit RFQ, show Create PO button
    - Cancelled state: form and lines disabled/uneditable
    """
    from app.services.document import get_list

    if not doc:
        return {"status": "error", "message": "RFQ not specified"}

    rfq_id = _get_id(doc)
    if not rfq_id:
        return {"status": "error", "message": "RFQ ID is required"}

    try:
        if action == "Submit Source":
            rfq_lines = await get_list("rfq_line", {"rfq_id": rfq_id}, db=db)
            if not rfq_lines:
                return {"status": "error", "message": "Cannot submit: RFQ has no lines"}
            return {"status": "success", "message": "RFQ submitted for sourcing"}

        elif action == "Submit for Review":
            return {"status": "success", "message": "RFQ submitted for review"}

        elif action == "Award":
            awarded_vendor = _get_attr(doc, 'awarded_vendor') or _get_attr(doc, 'supplier')
            if not awarded_vendor:
                return {"status": "error", "message": "Cannot award: Awarded Vendor is not set"}
            return {"status": "success", "message": "RFQ awarded"}

        elif action == "Create Purchase Order":
            return {"status": "success", "message": "RFQ moved to Order state"}

        elif action == "Cancel":
            return {"status": "success", "message": "RFQ cancelled"}

        return {"status": "success", "message": f"RFQ workflow '{action}' allowed"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"RFQ workflow error: {str(e)}"}


# =============================================================================
# Purchase Receipt Workflow
# =============================================================================

@register_workflow("purchase_receipt")
async def purchase_receipt_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Receipt workflow handler.

    States: Draft → Confirmed

    Business Rules:
    - Confirm Receipt is a server action (not a workflow action), but the
      workflow transition Draft → Confirmed happens after successful confirmation.
    - No additional business logic needed here beyond pass-through.
    """
    if not doc:
        return {"status": "error", "message": "Purchase Receipt not specified"}

    return {"status": "success", "message": f"Purchase Receipt workflow '{action}' allowed"}


# =============================================================================
# Item Issue Workflow
# =============================================================================

@register_workflow("item_issue")
async def item_issue_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Item Issue workflow handler.
    Delegates to the existing business logic in apis/item_issue.py.
    """
    from app.modules.purchasing_stores.apis.item_issue import check_item_issue_workflow
    return await check_item_issue_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Item Return Workflow
# =============================================================================

@register_workflow("item_return")
async def item_return_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Item Return workflow handler.
    Delegates to the existing business logic in apis/item_return.py.
    """
    from app.modules.purchasing_stores.apis.item_return import check_item_return_workflow
    return await check_item_return_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Stock Count Workflow
# =============================================================================

@register_workflow("stock_count")
async def stock_count_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Stock Count workflow handler.
    Delegates to the existing business logic in apis/stock_count.py.
    """
    from app.modules.purchasing_stores.apis.stock_count import check_stock_count_workflow
    return await check_stock_count_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Inventory Adjustment Workflow
# =============================================================================

@register_workflow("inventory_adjustment")
async def inventory_adjustment_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Inventory Adjustment workflow handler.
    Delegates to the business logic in apis/inventory_adjustment.py.
    """
    from app.modules.purchasing_stores.apis.inventory_adjustment import check_inventory_adjustment_workflow
    return await check_inventory_adjustment_workflow(doc=doc, action=action, db=db, user=user)


# =============================================================================
# Transfer Workflow
# =============================================================================

@register_workflow("transfer")
async def transfer_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Transfer workflow handler.
    States: Draft → In Transit → Received → Closed / Cancelled

    Actions:
    - dispatch: Validate items, set to In Transit
    - receive: Create Transfer Receipt, update locations
    - close: Final close
    - cancel: Cancel transfer
    """
    from app.services.document import get_list, new_doc, save_doc

    transfer_id = _get_id(doc)
    if not transfer_id:
        return {"status": "error", "message": "Transfer ID is required"}

    try:
        if action == "dispatch":
            from_store = _get_attr(doc, "from_store")
            to_store = _get_attr(doc, "to_store")
            if not from_store or not to_store:
                return {"status": "error", "message": "Both source and destination stores are required"}
            if from_store == to_store:
                return {"status": "error", "message": "Source and destination stores cannot be the same"}
            return {"status": "success", "message": "Transfer dispatched"}

        elif action == "receive":
            # Auto-create Transfer Receipt
            receipt = await new_doc("transfer_receipt", db,
                workflow_state="Draft",
                transfer_request=transfer_id,
                transfer_type=_get_attr(doc, "transfer_type"),
                receiving_location=_get_attr(doc, "to_location") or _get_attr(doc, "to_store"),
                inventory=_get_attr(doc, "inventory"),
            )
            if receipt:
                await save_doc(receipt, db)

            return {
                "status": "success",
                "message": "Transfer received. Transfer Receipt created.",
                "action": "generate_id",
                "path": f"/transfer_receipt/{receipt.id}" if receipt else None,
            }

        elif action == "close":
            return {"status": "success", "message": "Transfer closed"}

        elif action == "cancel":
            return {"status": "success", "message": "Transfer cancelled"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Transfer workflow error: {str(e)}"}

    return {"status": "success", "message": f"Transfer workflow '{action}' allowed"}


# =============================================================================
# Transfer Receipt Workflow
# =============================================================================

@register_workflow("transfer_receipt")
async def transfer_receipt_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Transfer Receipt workflow handler.
    Delegates to functions in apis/transfer_receipt.py.

    Actions:
    - confirm: Update item locations
    - inspect: Create inspection WOA for repaired assets
    """
    from app.modules.purchasing_stores.apis.transfer_receipt import (
        update_item_location, create_asset_repair_inspection
    )

    transfer_receipt_id = _get_id(doc)
    if not transfer_receipt_id:
        return {"status": "error", "message": "Transfer Receipt ID is required"}

    try:
        if action in ("confirm", "receive"):
            result = await update_item_location(doc, db)
            return result

        elif action == "inspect":
            result = await create_asset_repair_inspection(doc, db, user)
            return result

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Transfer Receipt workflow error: {str(e)}"}

    return {"status": "success", "message": f"Transfer Receipt workflow '{action}' allowed"}


# =============================================================================
# Purchase Return Workflow
# =============================================================================

@register_workflow("purchase_return")
async def purchase_return_workflow(doc: Any, action: str, db: AsyncSession, user: Any) -> dict:
    """
    Purchase Return workflow handler.
    States: Draft → Submitted → Approved → Returned → Closed / Cancelled

    Actions:
    - submit: Validate return lines exist
    - approve: Authorize the return
    - process_return: Update inventory quantities (reverse of receipt), update PO line
    - cancel: Cancel the return
    """
    from app.services.document import get_list, get_doc, save_doc
    from app.services.stock_ledger import ledger_for_purchase_return

    return_id = _get_id(doc)
    if not return_id:
        return {"status": "error", "message": "Purchase Return ID is required"}

    try:
        if action == "submit":
            return {"status": "success", "message": "Purchase Return submitted for approval"}

        elif action == "approve":
            return {"status": "success", "message": "Purchase Return approved"}

        elif action == "process_return":
            po_id = _get_attr(doc, "purchase_order")
            if not po_id:
                return {"status": "error", "message": "Purchase Order is required"}

            # Reverse inventory for returned items
            return_qty = _to_float(_get_attr(doc, "quantity_returned"))
            inventory_id = _get_attr(doc, "inventory")
            item_id = _get_attr(doc, "item")

            if inventory_id and return_qty > 0:
                inv_doc = await get_doc("inventory", inventory_id, db)
                if inv_doc:
                    actual = _to_float(getattr(inv_doc, "actual_inv", 0))
                    available = _to_float(getattr(inv_doc, "available_inv", 0))
                    inv_doc.actual_inv = actual - return_qty
                    inv_doc.available_inv = available - return_qty
                    await save_doc(inv_doc, db, commit=False)

                if item_id:
                    item_doc = await get_doc("item", item_id, db)
                    if item_doc:
                        item_actual = _to_float(getattr(item_doc, "actual_qty_on_hand", 0))
                        item_available = _to_float(getattr(item_doc, "available_capacity", 0))
                        item_doc.actual_qty_on_hand = item_actual - return_qty
                        item_doc.available_capacity = item_available - return_qty
                        await save_doc(item_doc, db, commit=False)

            # Stock ledger audit trail for purchase return
            if item_id and return_qty > 0:
                await ledger_for_purchase_return(
                    db=db,
                    return_id=return_id,
                    item_id=item_id,
                    qty=int(return_qty),
                    unit_cost=_to_float(_get_attr(doc, "unit_cost")),
                    site=_get_attr(doc, "site"),
                )

            await db.commit()
            return {"status": "success", "message": "Purchase Return processed. Inventory updated."}

        elif action == "cancel":
            return {"status": "success", "message": "Purchase Return cancelled"}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Purchase Return workflow error: {str(e)}"}

    return {"status": "success", "message": f"Purchase Return workflow '{action}' allowed"}
