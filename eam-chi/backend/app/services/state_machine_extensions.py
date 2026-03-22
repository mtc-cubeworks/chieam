"""
State Machine Enhancements (SM-1 through SM-6)
================================================
Extends the core workflow engine with:
- SM-1: State-based field permission control
- SM-2: Required-field validation per workflow state
- SM-4: Backward transition justification enforcement
- SM-5: Per-state SLA escalation thresholds
- SM-6: Enhanced state transition audit logging

These hooks integrate with the existing workflow system without
modifying the core validate_transition() logic.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any

from app.application.hooks.registry import hook_registry

logger = logging.getLogger("state_machine")


# =============================================================================
# SM-1: State-based field permission configuration
# =============================================================================

# Map of entity → state → list of read-only field names.
# Fields listed here become non-editable when the entity is in that state.
STATE_FIELD_PERMISSIONS = {
    "work_order": {
        "completed": ["asset", "location", "site", "department", "job_plan", "work_order_type"],
        "closed": ["*"],  # ALL fields read-only when closed
        "cancelled": ["*"],
    },
    "purchase_order": {
        "open": ["vendor", "po_type"],  # Vendor and type locked after approval
        "closed": ["*"],
        "cancelled": ["*"],
    },
    "purchase_request": {
        "approved": ["site", "department", "budget_code"],
        "closed": ["*"],
    },
    "maintenance_request": {
        "approved": ["asset", "site", "department"],
        "completed": ["*"],
        "closed": ["*"],
    },
    "asset": {
        "disposed": ["*"],
    },
}


def get_readonly_fields(entity: str, state: str) -> list[str]:
    """
    SM-1: Get the list of fields that should be read-only for
    a given entity in a given workflow state.
    Returns ["*"] if ALL fields are read-only.
    """
    entity_perms = STATE_FIELD_PERMISSIONS.get(entity, {})
    state_lower = (state or "").lower().replace(" ", "_")
    return entity_perms.get(state_lower, [])


# =============================================================================
# SM-2: Required fields per workflow state
# =============================================================================

# Map of entity → action → list of required field names.
# These fields MUST be non-empty before the transition can proceed.
STATE_REQUIRED_FIELDS = {
    "work_order": {
        "approve": ["asset", "work_order_type"],
        "start": ["assigned_to"],
        "complete": ["actual_start_date", "actual_end_date"],
    },
    "purchase_request": {
        "submit_for_review": ["site"],
        "submit_for_approval": ["site"],
    },
    "purchase_order": {
        "approve": ["vendor"],
    },
    "maintenance_request": {
        "submit": ["asset", "description"],
        "approve": ["asset", "description", "priority"],
    },
    "incident": {
        "report": ["asset", "incident_date"],
        "resolve": ["resolution_notes"],
    },
}


async def validate_required_fields(entity: str, action: str, doc: Any) -> dict | None:
    """
    SM-2: Validate that all required fields for a transition are populated.
    Returns error dict if validation fails, None if OK.
    """
    action_lower = (action or "").lower().replace(" ", "_")
    entity_reqs = STATE_REQUIRED_FIELDS.get(entity, {})
    required = entity_reqs.get(action_lower, [])

    if not required:
        return None

    missing = []
    for field in required:
        val = getattr(doc, field, None) if hasattr(doc, field) else (
            doc.get(field) if isinstance(doc, dict) else None
        )
        if val is None or val == "" or val == 0:
            missing.append(field)

    if missing:
        return {
            "status": "error",
            "message": f"Required fields missing for '{action}': {', '.join(missing)}",
        }
    return None


# =============================================================================
# SM-4: Backward transition justification
# =============================================================================

# Map of entity → set of actions that are considered "backward" transitions.
# These require a justification/reason to be provided.
BACKWARD_TRANSITIONS = {
    "work_order": {"reopen", "revert", "reject", "send_back"},
    "purchase_request": {"revise_purchase_request", "reject_purchase_request"},
    "purchase_order": {"reject", "cancel"},
    "maintenance_request": {"reject", "reopen", "send_back"},
    "incident": {"reopen"},
}


def is_backward_transition(entity: str, action: str) -> bool:
    """Check if an action is a backward/reversal transition."""
    action_lower = (action or "").lower().replace(" ", "_")
    backward = BACKWARD_TRANSITIONS.get(entity, set())
    return action_lower in backward


# =============================================================================
# SM-5: Per-state SLA thresholds (hours)
# =============================================================================

# Map of entity → state → max hours allowed in that state.
# If exceeded, the record should be flagged for escalation.
STATE_SLA_THRESHOLDS = {
    "maintenance_request": {
        "draft": 48,
        "pending_approval": 24,
        "approved": 72,
    },
    "work_order": {
        "requested": 48,
        "approved": 24,
        "in_progress": 168,  # 7 days
    },
    "purchase_request": {
        "pending_review": 48,
        "pending_approval": 24,
    },
    "incident": {
        "reported": 24,
        "under_investigation": 168,
    },
}


def get_sla_threshold_hours(entity: str, state: str) -> int | None:
    """
    SM-5: Get the SLA threshold in hours for a given entity/state.
    Returns None if no threshold is configured.
    """
    state_lower = (state or "").lower().replace(" ", "_")
    entity_sla = STATE_SLA_THRESHOLDS.get(entity, {})
    return entity_sla.get(state_lower)


async def check_sla_breach(entity: str, doc: Any) -> dict | None:
    """
    SM-5: Check if a document has exceeded its per-state SLA.
    Returns breach info dict if breached, None otherwise.
    """
    state = getattr(doc, "workflow_state", None) or ""
    threshold = get_sla_threshold_hours(entity, state)
    if threshold is None:
        return None

    updated_at = getattr(doc, "updated_at", None) or getattr(doc, "created_at", None)
    if not updated_at:
        return None

    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at)
        except (ValueError, TypeError):
            return None

    hours_elapsed = (datetime.now() - updated_at).total_seconds() / 3600.0
    if hours_elapsed > threshold:
        return {
            "entity": entity,
            "record_id": getattr(doc, "id", None),
            "state": state,
            "threshold_hours": threshold,
            "actual_hours": round(hours_elapsed, 1),
            "breach_amount": round(hours_elapsed - threshold, 1),
        }
    return None


# =============================================================================
# SM-6: Enhanced state transition audit logging
# =============================================================================

async def log_enhanced_transition(
    db,
    entity: str,
    record_id: str,
    from_state: str,
    to_state: str,
    action: str,
    user: Any = None,
    justification: str | None = None,
    sla_breach: dict | None = None,
) -> None:
    """
    SM-6: Enhanced audit logging for state transitions.
    Records justification for backward transitions and SLA breach info.
    """
    from app.services.audit import audit_service

    user_id = getattr(user, "id", None) or getattr(user, "user_id", None)
    username = getattr(user, "username", None) or getattr(user, "full_name", None)

    # Standard workflow audit log
    await audit_service.log_workflow(
        db=db,
        entity_name=entity,
        record_id=record_id,
        from_state=from_state,
        to_state=to_state,
        action_slug=action,
        user_id=user_id,
        username=username,
    )

    # Additional metadata for backward transitions or SLA breaches
    if justification or sla_breach:
        from app.models.audit_log import AuditLog
        extra_data = {}
        if justification:
            extra_data["justification"] = justification
        if sla_breach:
            extra_data["sla_breach"] = sla_breach

        extra_entry = AuditLog(
            entity_name=entity,
            record_id=record_id,
            action="workflow_metadata",
            user_id=user_id,
            username=username,
            before_snapshot=json.dumps({"workflow_state": from_state}),
            after_snapshot=json.dumps({
                "workflow_state": to_state,
                "action": action,
                **extra_data,
            }, default=str),
            changed_fields=json.dumps(list(extra_data.keys())),
        )
        db.add(extra_entry)
        await db.flush()
