"""
Notification Service (MR-5 / MW-9)
====================================
SMTP email notifications for maintenance-related events:
- Maintenance Request submitted → notify assigned personnel
- MR approved/rejected → notify requester
- WO assigned → notify assigned labor
- SLA escalation → notify managers
"""
import logging
from typing import Any

from app.application.hooks.registry import hook_registry

logger = logging.getLogger("notifications")


async def _send_notification(db, recipient_employee_id: str, subject: str, body: str) -> bool:
    """
    Send an email notification to an employee.
    Looks up the employee's email and dispatches via SMTP.
    Falls back to logging if SMTP is unavailable.
    """
    from app.services.document import get_value

    if not recipient_employee_id:
        return False

    employee = await get_value("employee", recipient_employee_id, "*", db)
    if not employee:
        return False

    email = employee.get("email") or employee.get("work_email")
    if not email:
        logger.warning(f"No email for employee {recipient_employee_id}, skipping notification")
        return False

    try:
        from app.infrastructure.email.smtp_service import SmtpEmailService
        from app.domain.protocols.email_service import EmailMessage

        service = SmtpEmailService()
        message = EmailMessage(to=[email], subject=subject, body=body)
        await service.send(message)

        # Log the email
        from app.services.document import new_doc, save_doc
        from datetime import datetime
        email_log = await new_doc("email_log", db,
            recipient=email,
            subject=subject,
            body=body,
            sent_at=datetime.now(),
            status="Sent",
        )
        if email_log:
            await save_doc(email_log, db, commit=False)

        return True
    except Exception as e:
        logger.warning(f"Failed to send notification to {email}: {e}")
        # Log as failed
        try:
            from app.services.document import new_doc, save_doc
            from datetime import datetime
            email_log = await new_doc("email_log", db,
                recipient=email,
                subject=subject,
                body=body,
                sent_at=datetime.now(),
                status="Failed",
                error_message=str(e),
            )
            if email_log:
                await save_doc(email_log, db, commit=False)
        except Exception:
            pass
        return False


@hook_registry.after_save("maintenance_request")
async def notify_on_mr_save(doc, ctx):
    """MR-5: Notify relevant personnel when MR is submitted or state changes."""
    state = getattr(doc, "workflow_state", "")
    mr_id = doc.id if hasattr(doc, "id") else None
    description = getattr(doc, "description", "") or ""

    if state in ("Pending Approval", "pending_approval"):
        # Notify the assigned approver / site manager
        site = getattr(doc, "site", None)
        if site:
            from app.services.document import get_value
            site_data = await get_value("site", site, "*", ctx.db)
            manager = site_data.get("site_manager") if site_data else None
            if manager:
                await _send_notification(
                    ctx.db, manager,
                    f"[EAM] Maintenance Request {mr_id} Pending Approval",
                    f"Maintenance Request {mr_id} requires your approval.\n\n"
                    f"Description: {description}\n"
                    f"Asset: {getattr(doc, 'asset', 'N/A')}\n"
                    f"Priority: {getattr(doc, 'priority', 'N/A')}",
                )

    elif state in ("Approved", "approved"):
        # Notify the requester
        requester = getattr(doc, "requested_by", None) or getattr(doc, "created_by", None)
        if requester:
            await _send_notification(
                ctx.db, requester,
                f"[EAM] Maintenance Request {mr_id} Approved",
                f"Your Maintenance Request {mr_id} has been approved.\n\n"
                f"Description: {description}",
            )

    elif state in ("Rejected", "rejected"):
        requester = getattr(doc, "requested_by", None) or getattr(doc, "created_by", None)
        if requester:
            await _send_notification(
                ctx.db, requester,
                f"[EAM] Maintenance Request {mr_id} Rejected",
                f"Your Maintenance Request {mr_id} has been rejected.\n\n"
                f"Description: {description}\n"
                f"Please review and resubmit if necessary.",
            )

    return None


@hook_registry.after_save("work_order")
async def notify_on_wo_assignment(doc, ctx):
    """MW-9: Notify assigned labor when WO is assigned or state changes."""
    state = getattr(doc, "workflow_state", "")
    wo_id = doc.id if hasattr(doc, "id") else None

    if state in ("in_progress", "In Progress", "assigned"):
        assigned_to = getattr(doc, "assigned_to", None)
        if assigned_to:
            await _send_notification(
                ctx.db, assigned_to,
                f"[EAM] Work Order {wo_id} Assigned",
                f"Work Order {wo_id} has been assigned to you.\n\n"
                f"Description: {getattr(doc, 'description', 'N/A')}\n"
                f"Due Date: {getattr(doc, 'due_date', 'N/A')}\n"
                f"Priority: {getattr(doc, 'priority', 'N/A')}",
            )

    return None
