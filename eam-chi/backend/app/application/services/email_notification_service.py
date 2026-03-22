"""
Email Notification Service
============================
Application-layer orchestrator for sending email notifications.
Composes email content from entity records and sends via the email service.
Depends on domain protocols, not concrete implementations.
"""
import logging
from typing import Any, Optional
from datetime import datetime, date

from app.domain.protocols.email_service import (
    EmailServiceProtocol,
    EmailTemplateRendererProtocol,
    EmailMessage,
    EmailResult,
)
from app.meta.registry import MetaRegistry

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Orchestrates building and sending entity-based email notifications."""

    def __init__(
        self,
        email_service: EmailServiceProtocol,
        template_renderer: EmailTemplateRendererProtocol,
    ):
        self._email_service = email_service
        self._template_renderer = template_renderer

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def notify_record_event(
        self,
        entity_name: str,
        record: dict[str, Any],
        recipients: list[str],
        event_type: str = "created",
        custom_message: Optional[str] = None,
        action_url: Optional[str] = None,
    ) -> EmailResult:
        """
        Send an email notification about an entity record event.

        Args:
            entity_name: Snake-case entity name (e.g. 'purchase_request').
            record: The record data dict.
            recipients: List of email addresses.
            event_type: One of 'created', 'updated', 'workflow_changed', 'action', etc.
            custom_message: Optional override for the body message.
            action_url: Optional deep-link URL to the record in the frontend.
        """
        if not recipients:
            return EmailResult(success=False, message="No recipients provided")

        meta = MetaRegistry.get(entity_name)
        entity_label = meta.label if meta else entity_name.replace("_", " ").title()

        record_id = record.get("id", "N/A")
        subject = self._build_subject(entity_label, record_id, event_type)
        greeting = "Hello,"
        message = custom_message or self._build_default_message(
            entity_label, record_id, event_type
        )

        record_fields = self._format_record_fields(entity_name, record, meta)

        html_body = self._template_renderer.render(
            "record_notification.html",
            {
                "subject": subject,
                "subtitle": f"{entity_label} • {record_id}",
                "greeting": greeting,
                "message": message,
                "record_fields": record_fields,
                "entity_label": entity_label,
                "action_url": action_url,
            },
        )

        email = EmailMessage(
            to=recipients,
            subject=subject,
            html_body=html_body,
            plain_body=self._build_plain_text(entity_label, record_id, message, record_fields),
        )

        result = await self._email_service.send(email)

        # Log the email send attempt
        try:
            from app.infrastructure.logging.email_logger import log_email_send
            await log_email_send(
                message=email,
                result=result,
                entity_name=entity_name,
                record_id=str(record_id),
                event_type=event_type,
            )
        except Exception:
            logger.warning("Failed to log email send attempt", exc_info=True)

        return result

    async def send_custom_email(
        self,
        recipients: list[str],
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
    ) -> EmailResult:
        """Send a fully custom email (no template rendering)."""
        if not recipients:
            return EmailResult(success=False, message="No recipients provided")

        email = EmailMessage(
            to=recipients,
            subject=subject,
            html_body=html_body,
            plain_body=plain_body,
        )
        result = await self._email_service.send(email)

        # Log the email send attempt
        try:
            from app.infrastructure.logging.email_logger import log_email_send
            await log_email_send(message=email, result=result)
        except Exception:
            logger.warning("Failed to log custom email send attempt", exc_info=True)

        return result

    async def send_test_email(self, recipient: str) -> EmailResult:
        """Send a test email to verify SMTP configuration."""
        sample_record = {
            "id": "PR-00001",
            "description": "Office supplies for Q1 2026",
            "requestor": "John Doe",
            "department": "IT Department",
            "site": "Main Building",
            "priority": "High",
            "workflow_state": "Draft",
            "created_at": datetime.now().isoformat(),
        }

        return await self.notify_record_event(
            entity_name="purchase_request",
            record=sample_record,
            recipients=[recipient],
            event_type="created",
            custom_message=(
                "This is a <b>test email</b> from the EAM Notification System. "
                "Below is a sample record to demonstrate the email format."
            ),
            action_url="https://eamvue.cubeworksinnovation.com/purchase_request/PR-00001",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_subject(entity_label: str, record_id: str, event_type: str) -> str:
        event_labels = {
            "created": "New",
            "updated": "Updated",
            "workflow_changed": "Status Changed",
            "action": "Action Required",
            "deleted": "Deleted",
        }
        prefix = event_labels.get(event_type, event_type.replace("_", " ").title())
        return f"[EAM] {prefix}: {entity_label} {record_id}"

    @staticmethod
    def _build_default_message(entity_label: str, record_id: str, event_type: str) -> str:
        templates = {
            "created": f"A new <b>{entity_label}</b> (<b>{record_id}</b>) has been created and requires your attention.",
            "updated": f"The <b>{entity_label}</b> (<b>{record_id}</b>) has been updated.",
            "workflow_changed": f"The status of <b>{entity_label}</b> (<b>{record_id}</b>) has changed.",
            "action": f"An action is required on <b>{entity_label}</b> (<b>{record_id}</b>).",
            "deleted": f"The <b>{entity_label}</b> (<b>{record_id}</b>) has been deleted.",
        }
        return templates.get(
            event_type,
            f"A notification was triggered for <b>{entity_label}</b> (<b>{record_id}</b>).",
        )

    @staticmethod
    def _format_record_fields(
        entity_name: str,
        record: dict[str, Any],
        meta: Any,
    ) -> list[dict[str, str]]:
        """Build a list of {name, label, value} dicts for template rendering."""
        skip_fields = {"hashed_password", "updated_at"}
        fields = []

        if meta and meta.fields:
            for f in meta.fields:
                name = f.name
                if name in skip_fields:
                    continue
                value = record.get(name)
                if value is None:
                    continue
                if isinstance(value, (datetime, date)):
                    value = value.isoformat()
                fields.append({
                    "name": name,
                    "label": f.label or name.replace("_", " ").title(),
                    "value": str(value),
                })
        else:
            for key, value in record.items():
                if key in skip_fields:
                    continue
                if value is None:
                    continue
                if isinstance(value, (datetime, date)):
                    value = value.isoformat()
                fields.append({
                    "name": key,
                    "label": key.replace("_", " ").title(),
                    "value": str(value),
                })

        return fields

    @staticmethod
    def _build_plain_text(
        entity_label: str,
        record_id: str,
        message: str,
        record_fields: list[dict[str, str]],
    ) -> str:
        """Build a plain-text fallback for the email."""
        import re
        clean_msg = re.sub(r"<[^>]+>", "", message)
        lines = [
            f"{entity_label} — {record_id}",
            "",
            clean_msg,
            "",
            "Record Details:",
            "-" * 40,
        ]
        for field in record_fields:
            lines.append(f"  {field['label']}: {field['value']}")
        lines.append("-" * 40)
        lines.append("")
        lines.append("This is an automated notification from the EAM System.")
        return "\n".join(lines)
