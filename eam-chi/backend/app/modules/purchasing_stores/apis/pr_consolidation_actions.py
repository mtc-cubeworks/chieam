"""
PR → PO Consolidation Server Action
=======================================
Registered as a server action on purchase_request entity.
"""
from app.services.server_actions import server_actions, ActionContext


@server_actions.register("purchase_request", "consolidate_prs_to_pos")
async def consolidate_prs_to_pos_action(ctx: ActionContext):
    """
    Consolidate all approved Purchase Requests into Purchase Orders
    grouped by vendor. Callable from any approved PR.
    """
    from app.services.pr_po_consolidation import consolidate_approved_prs_to_pos

    # Optionally scope to the PR's site
    doc = ctx.params.get("doc")
    site = None
    if doc:
        site = getattr(doc, "site", None) if hasattr(doc, "site") else doc.get("site") if isinstance(doc, dict) else None

    return await consolidate_approved_prs_to_pos(ctx.db, site=site)
