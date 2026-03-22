"""
Vendor Performance Calculation Hook
======================================
PO-3: Auto-calculate vendor delivery_rating, quality_rating, and
overall_rating after a Purchase Receipt is confirmed.
"""
from app.application.hooks.registry import hook_registry


@hook_registry.after_save("purchase_receipt")
async def update_vendor_performance_on_receipt(doc, ctx):
    """
    When a Purchase Receipt is saved/confirmed, recalculate
    the vendor's performance ratings based on all historical receipts.
    """
    from app.services.document import get_doc, get_list, get_value, save_doc

    po_id = getattr(doc, "purchase_order", None)
    if not po_id:
        return None

    po = await get_value("purchase_order", po_id, "*", ctx.db)
    if not po:
        return None

    vendor_id = po.get("vendor")
    if not vendor_id:
        return None

    vendor_doc = await get_doc("vendor", vendor_id, ctx.db)
    if not vendor_doc:
        return None

    # Get all POs for this vendor
    all_pos = await get_list("purchase_order", {"vendor": vendor_id}, db=ctx.db)
    total_orders = len(all_pos)

    on_time = 0
    rejected = 0

    for po_rec in all_pos:
        po_state = po_rec.get("workflow_state", "")
        if po_state in ("cancelled", "rejected"):
            rejected += 1
            continue

        # Check if PO was delivered on time
        receipts = await get_list("purchase_receipt", {"purchase_order": po_rec["id"]}, db=ctx.db)
        if receipts:
            expected_date = po_rec.get("delivery_date") or po_rec.get("due_date")
            if expected_date:
                from datetime import date as date_type
                for receipt in receipts:
                    receipt_date = receipt.get("receipt_date") or receipt.get("created_at")
                    if receipt_date:
                        if hasattr(receipt_date, "date"):
                            receipt_date = receipt_date.date()
                        if hasattr(expected_date, "date"):
                            expected_date = expected_date.date()
                        if isinstance(receipt_date, date_type) and isinstance(expected_date, date_type):
                            if receipt_date <= expected_date:
                                on_time += 1
                            break

    # Calculate ratings
    if total_orders > 0:
        delivery_rating = round((on_time / total_orders) * 5.0, 2)
        quality_rating = round(((total_orders - rejected) / total_orders) * 5.0, 2)
        overall_rating = round((delivery_rating + quality_rating) / 2.0, 2)
    else:
        delivery_rating = 0.0
        quality_rating = 0.0
        overall_rating = 0.0

    changed = False
    if getattr(vendor_doc, "total_orders", None) != total_orders:
        vendor_doc.total_orders = total_orders
        changed = True
    if getattr(vendor_doc, "on_time_deliveries", None) != on_time:
        vendor_doc.on_time_deliveries = on_time
        changed = True
    if getattr(vendor_doc, "rejected_deliveries", None) != rejected:
        vendor_doc.rejected_deliveries = rejected
        changed = True
    if getattr(vendor_doc, "delivery_rating", None) != delivery_rating:
        vendor_doc.delivery_rating = delivery_rating
        changed = True
    if getattr(vendor_doc, "quality_rating", None) != quality_rating:
        vendor_doc.quality_rating = quality_rating
        changed = True
    if getattr(vendor_doc, "overall_rating", None) != overall_rating:
        vendor_doc.overall_rating = overall_rating
        changed = True

    if changed:
        await save_doc(vendor_doc, ctx.db)

    return None
