"""
Document Mutation Service
=========================
Write operations for documents (SRP: mutations only).

Provides:
- new_doc: Create a new document instance (not saved)
- save_doc: Save a document (insert or update)
- insert_doc: Insert a new document
- delete_doc: Delete a document
- apply_workflow_state: Validate and apply a workflow transition
"""
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document_query import _get_model, get_meta, _record_to_dict


# =============================================================================
# new_doc
# =============================================================================

async def new_doc(
    entity: str,
    db: AsyncSession,
    **kwargs
) -> Optional[Any]:
    """Create a new document instance (not saved to database yet)."""
    model = _get_model(entity)
    if not model:
        return None

    meta = get_meta(entity)

    # Generate ID if naming is enabled and no ID provided
    if meta and meta.naming and meta.naming.enabled and "id" not in kwargs:
        from app.services.naming import NamingService
        generated_id = await NamingService.generate_id(db, meta.naming)
        if generated_id:
            kwargs["id"] = generated_id

    # Set initial workflow state if workflow enabled and no state provided
    if (meta and meta.workflow and meta.workflow.enabled and
        meta.workflow.state_field and meta.workflow.initial_state and
        meta.workflow.state_field not in kwargs):
        kwargs[meta.workflow.state_field] = meta.workflow.initial_state

    doc = model(**kwargs)
    return doc


# =============================================================================
# save_doc
# =============================================================================

async def save_doc(
    doc: Any,
    db: AsyncSession,
    commit: bool = True
) -> Any:
    """Save a document to the database (insert or update)."""
    from sqlalchemy import inspect

    insp = inspect(doc)
    if insp.transient:
        db.add(doc)

    if commit:
        await db.commit()
        await db.refresh(doc)
    else:
        await db.flush()

    return doc


# =============================================================================
# insert_doc
# =============================================================================

async def insert_doc(
    doc: Any,
    db: AsyncSession,
    commit: bool = True
) -> Any:
    """Insert a new document."""
    db.add(doc)
    if commit:
        await db.commit()
        await db.refresh(doc)
    else:
        await db.flush()
    return doc


# =============================================================================
# delete_doc
# =============================================================================

async def delete_doc(
    entity: str,
    id: str,
    db: AsyncSession,
    commit: bool = True
) -> bool:
    """Delete a document by entity name and ID."""
    from app.services.document_query import get_doc
    doc = await get_doc(entity, id, db)
    if not doc:
        return False

    await db.delete(doc)
    if commit:
        await db.commit()

    return True


# =============================================================================
# apply_workflow_state
# =============================================================================

async def apply_workflow_state(
    entity: str,
    doc: Any,
    action_slug: str,
    db: AsyncSession,
    commit: bool = False,
) -> dict:
    """
    Validate a workflow transition and apply the new state to a document.

    This is the ONLY correct way to change workflow_state on a document.
    Never set workflow_state directly — always go through this function so
    that the transition is validated against the workflow configuration in
    the database.

    Integrates SM-1 through SM-6 state machine enhancements:
    - SM-2: Required field validation before transition
    - SM-4: Backward transition justification check
    - SM-6: Enhanced audit logging
    """
    import re
    from app.services.workflow import WorkflowDBService

    current_state_raw = getattr(doc, "workflow_state", None) or ""
    current_state = current_state_raw.lower().strip()
    current_state = re.sub(r'[^a-z0-9\s_]', '', current_state)
    current_state = re.sub(r'\s+', '_', current_state)

    if not current_state:
        initial = await WorkflowDBService.get_initial_state(db, entity)
        if initial:
            current_state = initial
        else:
            return {"status": "error", "message": f"No workflow configured for '{entity}'"}

    # SM-2: Validate required fields for this transition
    from app.services.state_machine_extensions import validate_required_fields
    req_error = await validate_required_fields(entity, action_slug, doc)
    if req_error:
        return req_error

    # SM-4: Check backward transition justification
    from app.services.state_machine_extensions import is_backward_transition
    if is_backward_transition(entity, action_slug):
        justification = getattr(doc, "justification", None) or getattr(doc, "rejection_reason", None)
        if not justification:
            return {
                "status": "error",
                "message": f"A justification/reason is required for backward transition '{action_slug}'",
            }

    is_valid, target_state, error = await WorkflowDBService.validate_transition(
        db, entity, current_state, action_slug, user=None
    )

    if not is_valid:
        return {
            "status": "error",
            "message": error or f"Action '{action_slug}' not valid from state '{current_state}'"
        }

    doc.workflow_state = target_state

    # SM-6: Enhanced audit logging
    try:
        from app.services.state_machine_extensions import log_enhanced_transition, check_sla_breach
        sla_breach = await check_sla_breach(entity, doc)
        justification = getattr(doc, "justification", None) or getattr(doc, "rejection_reason", None)
        record_id = getattr(doc, "id", None) or getattr(doc, "name", None)
        if record_id:
            await log_enhanced_transition(
                db, entity, record_id, current_state, target_state,
                action_slug, justification=justification, sla_breach=sla_breach,
            )
    except Exception:
        pass  # Audit logging should not block the transition

    if commit:
        await db.flush()

    return {
        "status": "success",
        "from_state": current_state,
        "to_state": target_state,
    }
