"""
Purchase Request Entity Business Logic

Server actions:
- generate_rfq(doc, db, user) – Generate a blank RFQ from an approved Purchase Request

Uses document helpers for Frappe-like syntax.
All mutating operations are wrapped in try/except with db.rollback() on error.
"""
from typing import Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_value, get_list, new_doc, save_doc


# =============================================================================
# Generate RFQ from Purchase Request
# =============================================================================

async def generate_rfq(doc: Any, db: AsyncSession, user: Any) -> dict:
    """
    Generate a blank RFQ from a Purchase Request.

    Business Rules:
    - PR must be in an eligible state (pending_review, pending_approval, approved)
    - Creates an RFQ in 'draft' state
    - RFQ Lines are initially blank (no automatic copy from PR Lines)
    - User will manually populate RFQ Lines during sourcing
    """
    if not doc:
        return {"status": "error", "message": "Purchase Request not specified"}

    pr_id = doc.id if hasattr(doc, 'id') else doc.get('id')
    if not pr_id:
        return {"status": "error", "message": "Purchase Request ID is required"}

    pr_state = getattr(doc, 'workflow_state', None)
    allowed_states = ("pending_review", "pending_approval", "approved")
    if pr_state not in allowed_states:
        return {
            "status": "error",
            "message": f"Cannot generate RFQ: Purchase Request must be in {', '.join(allowed_states)} state"
        }

    try:
        # Get requestor info from PR
        requestor = getattr(doc, 'requestor', None)
        due_date_val = getattr(doc, 'due_date', None)

        # Create RFQ with draft state – lines are blank
        rfq = await new_doc("request_for_quotation", db,
            requestor=requestor or None,
            due_date=due_date_val if due_date_val else None,
            date_issue=date.today(),
            remarks=f"Generated from PR: {pr_id}",
        )
        await save_doc(rfq, db)

        return {
            "status": "success",
            "message": "RFQ generated (lines are blank populate during sourcing)",
            "data": {
                "action": "generate_id",
                "path": f"/request_for_quotation/{rfq.id}",
                "id": rfq.id,
            },
        }

    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": f"Failed to generate RFQ: {str(e)}"}


# Server actions are auto-registered from entity JSON method paths.
# No manual decorator registration needed.
