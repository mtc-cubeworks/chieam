"""
Purchasing & Stores Module Hooks
==================================
Registers entity lifecycle hooks with the hook registry.
All workflow logic is routed through the central workflow_router.
"""
from app.application.hooks.registry import hook_registry
from app.services.document import get_list

# =============================================================================
# Before-Save Hooks
# =============================================================================

@hook_registry.before_save("purchase_request_line")
async def purchase_request_line_before_save(doc, ctx):
    """Generate row number for Purchase Request Line."""
    try:
        purchase_request = doc.get("purchase_request") if isinstance(doc, dict) else getattr(doc, "purchase_request", None)
        if not purchase_request:
            return doc, {"purchase_request": "Purchase Request not specified"}

        existing_lines = await get_list("purchase_request_line", {"purchase_request": purchase_request}, db=ctx.db)
        next_row = len(existing_lines) + 1

        if isinstance(doc, dict):
            if not doc.get("row_number"):
                doc["row_number"] = next_row
        else:
            if not getattr(doc, "row_number", None):
                doc.row_number = next_row

        return doc, None
    except Exception as e:
        await ctx.db.rollback()
        return doc, {"error": str(e)}


# =============================================================================
# After-Save Hooks
# =============================================================================

@hook_registry.after_save("purchase_request_line")
async def purchase_request_line_after_save(doc, ctx):
    """Calculate Line Total = Unit Cost x Qty Required and roll up to PR total."""
    from app.services.document import save_doc, get_doc
    unit_cost = getattr(doc, "unit_cost", None) or 0
    qty_required = getattr(doc, "qty_required", None) or 0
    calculated = round(float(unit_cost) * float(qty_required), 2)
    current = getattr(doc, "total_line_amount", None) or 0
    if float(current) != calculated:
        doc.total_line_amount = calculated
        await save_doc(doc, ctx.db)

    # Roll up total to parent Purchase Request
    pr_id = getattr(doc, "purchase_request", None)
    if pr_id:
        all_lines = await get_list("purchase_request_line", {"purchase_request": pr_id}, db=ctx.db)
        pr_total = sum(float(line.get("total_line_amount", 0) or 0) for line in all_lines)
        pr_doc = await get_doc("purchase_request", pr_id, ctx.db)
        if pr_doc:
            current_total = getattr(pr_doc, "total_amount", None) or 0
            if round(float(current_total), 2) != round(pr_total, 2):
                pr_doc.total_amount = round(pr_total, 2)
                await save_doc(pr_doc, ctx.db)

    return None


@hook_registry.after_save("purchase_order_line")
async def purchase_order_line_after_save(doc, ctx):
    """Roll up PO line totals to parent Purchase Order."""
    from app.services.document import save_doc, get_doc
    po_id = getattr(doc, "purchase_order", None)
    if not po_id:
        return None

    all_lines = await get_list("purchase_order_line", {"purchase_order": po_id}, db=ctx.db)
    po_total = 0.0
    for line in all_lines:
        qty = float(line.get("quantity_ordered", 0) or 0)
        price = float(line.get("price", 0) or 0)
        po_total += qty * price

    po_doc = await get_doc("purchase_order", po_id, ctx.db)
    if po_doc:
        current_total = getattr(po_doc, "total_amount", None) or 0
        if round(float(current_total), 2) != round(po_total, 2):
            po_doc.total_amount = round(po_total, 2)
            await save_doc(po_doc, ctx.db)

    return None


@hook_registry.after_save("inventory")
async def inventory_after_save_reorder_check(doc, ctx):
    """Check if inventory fell below reorder point and auto-generate Purchase Request."""
    from app.services.document import get_doc, get_value, new_doc, save_doc

    item_id = getattr(doc, "item", None)
    if not item_id:
        return None

    item = await get_value("item", item_id, "*", ctx.db)
    if not item:
        return None

    reorder_point = float(item.get("reorder_point", 0) or 0)
    if reorder_point <= 0:
        return None

    actual_inv = float(getattr(doc, "actual_inv", 0) or 0)
    if actual_inv >= reorder_point:
        return None

    # Check if an open PR already exists for this item
    from app.services.document_query import _get_model
    from sqlalchemy import select, and_
    pr_line_model = _get_model("purchase_request_line")
    pr_model = _get_model("purchase_request")
    if pr_line_model and pr_model:
        result = await ctx.db.execute(
            select(pr_line_model).join(
                pr_model, pr_line_model.purchase_request == pr_model.id
            ).where(
                and_(
                    pr_line_model.item == item_id,
                    pr_model.workflow_state.notin_(["closed", "rejected", "cancelled"])
                )
            ).limit(1)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return None

    # Auto-generate PR
    reorder_qty = float(item.get("reorder_quantity", 0) or 0)
    if reorder_qty <= 0:
        reorder_qty = reorder_point * 2  # Default to 2x reorder point

    pr = await new_doc("purchase_request", ctx.db,
        workflow_state="Draft",
        pr_description=f"Auto-Reorder: {item.get('item_name', item_id)} below minimum ({actual_inv}/{reorder_point})",
        site=getattr(doc, "site", None),
    )
    if pr:
        await save_doc(pr, ctx.db, commit=False)

        pr_line = await new_doc("purchase_request_line", ctx.db,
            purchase_request=pr.id,
            item=item_id,
            qty_required=reorder_qty,
            unit_cost=float(item.get("unit_cost", 0) or 0),
            row_number=1,
        )
        if pr_line:
            pr_line.total_line_amount = round(reorder_qty * float(item.get("unit_cost", 0) or 0), 2)
            await save_doc(pr_line, ctx.db)

    return None


# =============================================================================
# Workflow Hooks - All routed through central workflow_router
# =============================================================================

@hook_registry.workflow("purchase_request")
async def purchase_request_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_request", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("purchase_request_line")
async def purchase_request_line_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_request_line", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("purchase_order")
async def purchase_order_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_order", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("purchase_order_line")
async def purchase_order_line_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_order_line", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("request_for_quotation")
async def rfq_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("request_for_quotation", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("purchase_receipt")
async def purchase_receipt_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_receipt", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("item_issue")
async def item_issue_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("item_issue", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("item_return")
async def item_return_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("item_return", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("stock_count")
async def stock_count_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("stock_count", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("inventory_adjustment")
async def inventory_adjustment_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("inventory_adjustment", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("transfer")
async def transfer_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("transfer", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("transfer_receipt")
async def transfer_receipt_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("transfer_receipt", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("purchase_return")
async def purchase_return_workflow_hook(ctx):
    from app.modules.purchasing_stores.workflow_router import route_workflow
    return await route_workflow("purchase_return", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.after_save("putaway")
async def putaway_after_save(doc, ctx):
    """Update inventory bin/zone location after putaway."""
    from app.services.document import get_doc, save_doc
    inventory_id = getattr(doc, "inventory", None)
    if not inventory_id:
        return None

    inv_doc = await get_doc("inventory", inventory_id, ctx.db)
    if not inv_doc:
        return None

    bin_val = getattr(doc, "bin", None)
    zone_val = getattr(doc, "zone", None)
    store_val = getattr(doc, "store", None)

    changed = False
    if bin_val and getattr(inv_doc, "bin_location", None) != bin_val:
        inv_doc.bin_location = bin_val
        changed = True
    if zone_val and getattr(inv_doc, "zone", None) != zone_val:
        inv_doc.zone = zone_val
        changed = True
    if store_val and getattr(inv_doc, "store_location", None) != store_val:
        inv_doc.store_location = store_val
        changed = True

    if changed:
        await save_doc(inv_doc, ctx.db)

    return None


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.purchasing_stores.apis.purchase_request  # noqa: F401
    import app.modules.purchasing_stores.apis.purchase_order  # noqa: F401
    import app.modules.purchasing_stores.apis.purchase_receipt  # noqa: F401
    import app.modules.purchasing_stores.apis.stock_count  # noqa: F401
    import app.modules.purchasing_stores.apis.inventory_adjustment  # noqa: F401
    import app.modules.purchasing_stores.apis.transfer_receipt  # noqa: F401
