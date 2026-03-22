"""
3-Way Matching Service
========================
Compares Purchase Order lines ↔ Goods Receipt (PurchaseReceipt) ↔ Vendor Invoice lines.
Updates match_status on VendorInvoice and individual VendorInvoiceLines.

Match statuses:
  - "Matched"    : qty & price match across PO, GR, and Invoice within tolerance
  - "Partial"    : some lines match, others do not
  - "Mismatched" : variance exceeds tolerance
"""
from app.application.hooks.registry import hook_registry

# Acceptable variance percentage for price matching (2%)
PRICE_TOLERANCE_PCT = 0.02
# Acceptable variance for quantity matching (absolute units)
QTY_TOLERANCE = 0.01


@hook_registry.after_save("vendor_invoice_line")
async def vendor_invoice_line_after_save_match(doc, ctx):
    """After saving an invoice line, run line-level match and roll up to header."""
    from app.services.document import get_value, get_list, get_doc, save_doc

    vi_id = getattr(doc, "vendor_invoice", None)
    if not vi_id:
        return None

    vi = await get_doc("vendor_invoice", vi_id, ctx.db)
    if not vi:
        return None

    po_id = getattr(vi, "purchase_order", None)
    if not po_id:
        return None

    # Match this individual line against PO line + GR
    po_line_id = getattr(doc, "purchase_order_line", None)
    line_status = "Mismatched"

    if po_line_id:
        po_line = await get_value("purchase_order_line", po_line_id, "*", ctx.db)
        if po_line:
            po_qty = float(po_line.get("quantity_ordered", 0) or 0)
            po_price = float(po_line.get("price", 0) or 0)
            inv_qty = float(getattr(doc, "quantity_invoiced", 0) or 0)
            inv_price = float(getattr(doc, "unit_price", 0) or 0)

            # Check GR received qty for this PO line item
            item_id = po_line.get("item")
            gr_qty = 0.0
            if item_id:
                receipts = await get_list(
                    "purchase_receipt",
                    {"purchase_order": po_id},
                    db=ctx.db,
                )
                for r in receipts:
                    state = r.get("workflow_state", "")
                    if state in ("cancelled", "Cancelled"):
                        continue
                    if r.get("item") == item_id:
                        gr_qty += float(r.get("quantity_received", 0) or 0)

            qty_ok = abs(inv_qty - po_qty) <= QTY_TOLERANCE and abs(inv_qty - gr_qty) <= QTY_TOLERANCE
            price_ok = po_price == 0 or abs(inv_price - po_price) / max(po_price, 0.01) <= PRICE_TOLERANCE_PCT

            if qty_ok and price_ok:
                line_status = "Matched"

    if getattr(doc, "match_status", None) != line_status:
        doc.match_status = line_status
        await save_doc(doc, ctx.db, commit=False)

    # Roll up to invoice header
    all_lines = await get_list("vendor_invoice_line", {"vendor_invoice": vi_id}, db=ctx.db)
    statuses = [l.get("match_status", "Mismatched") for l in all_lines]

    if all(s == "Matched" for s in statuses):
        header_status = "Matched"
        variance = 0.0
    elif any(s == "Matched" for s in statuses):
        header_status = "Partial"
        variance = _calc_variance(all_lines)
    else:
        header_status = "Mismatched"
        variance = _calc_variance(all_lines)

    changed = False
    if getattr(vi, "match_status", None) != header_status:
        vi.match_status = header_status
        changed = True
    if getattr(vi, "match_variance", None) != variance:
        vi.match_variance = variance
        changed = True
    if changed:
        await save_doc(vi, ctx.db)

    return None


def _calc_variance(lines):
    """Sum of absolute line-total differences (simple variance metric)."""
    total_var = 0.0
    for l in lines:
        inv_total = float(l.get("line_total", 0) or 0)
        # Variance = difference between invoiced amount and expected
        qty = float(l.get("quantity_invoiced", 0) or 0)
        price = float(l.get("unit_price", 0) or 0)
        expected = qty * price
        total_var += abs(inv_total - expected)
    return round(total_var, 2)
