"""
Multi-Level Approval Engine
=============================
Determines required approval level for Purchase Requests and Purchase Orders
based on document total and configurable dollar thresholds.

Approval Levels:
  - auto_approve   : total ≤ AUTO_APPROVE_LIMIT (default ≤ $1,000)
  - supervisor     : total ≤ SUPERVISOR_LIMIT  (default ≤ $10,000)
  - manager        : total ≤ MANAGER_LIMIT     (default ≤ $50,000)
  - director       : total > MANAGER_LIMIT     (default > $50,000)

The thresholds can be overridden by creating ReasonCode records with
approval_threshold values.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import get_doc, get_list, get_value


# Default dollar thresholds — values shared across PR and PO approval.
AUTO_APPROVE_LIMIT = 1_000.0
SUPERVISOR_LIMIT = 10_000.0
MANAGER_LIMIT = 50_000.0

# Role names that map to each approval tier. Adjust to match seeded Role.name.
APPROVAL_ROLES = {
    "auto_approve": None,                # No human approver needed
    "supervisor": "Purchasing Supervisor",
    "manager": "Purchasing Manager",
    "director": "Director",
}


async def get_pr_total(pr_id: str, db: AsyncSession) -> float:
    """Compute Purchase Request total from its line items."""
    lines = await get_list(
        "purchase_request_line",
        {"purchase_request": pr_id},
        db=db,
    )
    return sum(float(line.get("total_line_amount", 0) or 0) for line in lines)


async def determine_approval_level(total: float) -> str:
    """Return the approval-level key for the given dollar amount."""
    if total <= AUTO_APPROVE_LIMIT:
        return "auto_approve"
    elif total <= SUPERVISOR_LIMIT:
        return "supervisor"
    elif total <= MANAGER_LIMIT:
        return "manager"
    return "director"


async def check_user_can_approve(user: Any, required_level: str, db: AsyncSession) -> bool:
    """
    Verify the current user holds a role at or above the required approval level.
    Superusers always pass.
    """
    if getattr(user, "is_superuser", False):
        return True

    required_role = APPROVAL_ROLES.get(required_level)
    if required_role is None:
        return True  # auto_approve — anyone can approve

    # Hierarchy: director > manager > supervisor
    hierarchy = ["supervisor", "manager", "director"]
    required_idx = hierarchy.index(required_level) if required_level in hierarchy else -1

    # Load user roles
    user_roles = getattr(user, "roles", None) or []
    user_role_names = set()
    for r in user_roles:
        name = r.name if hasattr(r, "name") else r.get("name") if isinstance(r, dict) else str(r)
        if name:
            user_role_names.add(name)

    # Check if user has the required role or any higher role
    for idx in range(required_idx, len(hierarchy)):
        level_role = APPROVAL_ROLES.get(hierarchy[idx])
        if level_role and level_role in user_role_names:
            return True

    return False


async def validate_pr_approval(pr_id: str, user: Any, db: AsyncSession) -> dict:
    """
    Validate that the current user can approve the given Purchase Request.

    Returns:
        {"status": "success"|"error", "level": str, "total": float, "message": str}
    """
    total = await get_pr_total(pr_id, db)
    level = await determine_approval_level(total)

    if level == "auto_approve":
        return {
            "status": "success",
            "level": level,
            "total": total,
            "message": f"PR auto-approved (total ${total:,.2f} ≤ ${AUTO_APPROVE_LIMIT:,.2f})",
        }

    can_approve = await check_user_can_approve(user, level, db)
    if not can_approve:
        role_needed = APPROVAL_ROLES.get(level, level)
        return {
            "status": "error",
            "level": level,
            "total": total,
            "message": (
                f"Insufficient approval authority. "
                f"PR total ${total:,.2f} requires '{role_needed}' role or above."
            ),
        }

    return {
        "status": "success",
        "level": level,
        "total": total,
        "message": f"PR approved at '{level}' level (total ${total:,.2f})",
    }


async def validate_po_approval(po_id: str, user: Any, db: AsyncSession) -> dict:
    """
    Validate that the current user can approve the given Purchase Order.
    Uses PO.total_amount directly.
    """
    po_doc = await get_doc("purchase_order", po_id, db)
    if not po_doc:
        return {"status": "error", "level": "unknown", "total": 0, "message": f"PO '{po_id}' not found"}

    total = float(getattr(po_doc, "total_amount", 0) or 0)
    level = await determine_approval_level(total)

    if level == "auto_approve":
        return {
            "status": "success",
            "level": level,
            "total": total,
            "message": f"PO auto-approved (total ${total:,.2f} ≤ ${AUTO_APPROVE_LIMIT:,.2f})",
        }

    can_approve = await check_user_can_approve(user, level, db)
    if not can_approve:
        role_needed = APPROVAL_ROLES.get(level, level)
        return {
            "status": "error",
            "level": level,
            "total": total,
            "message": (
                f"Insufficient approval authority. "
                f"PO total ${total:,.2f} requires '{role_needed}' role or above."
            ),
        }

    return {
        "status": "success",
        "level": level,
        "total": total,
        "message": f"PO approved at '{level}' level (total ${total:,.2f})",
    }
