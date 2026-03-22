"""
Email Notification Service Tests
==================================
Tests for domain protocols, infrastructure, and application layer.
Uses mock email service to avoid actual SMTP calls.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from app.domain.protocols.email_service import (
    EmailMessage,
    EmailResult,
    EmailServiceProtocol,
    EmailTemplateRendererProtocol,
)
from app.infrastructure.email.smtp_service import SmtpEmailService
from app.infrastructure.email.template_renderer import JinjaEmailTemplateRenderer
from app.application.services.email_notification_service import EmailNotificationService


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

class FakeEmailService:
    """In-memory email service for testing."""

    def __init__(self):
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> EmailResult:
        self.sent.append(message)
        return EmailResult(success=True, message="Sent", recipient_count=len(message.to))

    async def send_bulk(self, messages: list[EmailMessage]) -> list[EmailResult]:
        results = []
        for m in messages:
            results.append(await self.send(m))
        return results


class FakeTemplateRenderer:
    """Stub renderer that returns a predictable string."""

    def render(self, template_name: str, context: dict) -> str:
        return f"<html>Rendered {template_name} with subject={context.get('subject', '')}</html>"


def _make_service(fake_email=None, fake_renderer=None):
    return EmailNotificationService(
        email_service=fake_email or FakeEmailService(),
        template_renderer=fake_renderer or FakeTemplateRenderer(),
    )


# ---------------------------------------------------------------------------
# 1. Domain protocol conformance
# ---------------------------------------------------------------------------

class TestDomainProtocols:
    def test_email_message_creation(self):
        msg = EmailMessage(to=["a@b.com"], subject="Hi", html_body="<p>Hi</p>")
        assert msg.to == ["a@b.com"]
        assert msg.subject == "Hi"
        assert msg.cc is None
        assert msg.bcc is None

    def test_email_result_defaults(self):
        r = EmailResult(success=True, message="ok")
        assert r.recipient_count == 0

    def test_fake_email_service_satisfies_protocol(self):
        svc = FakeEmailService()
        assert isinstance(svc, EmailServiceProtocol)

    def test_fake_renderer_satisfies_protocol(self):
        renderer = FakeTemplateRenderer()
        assert isinstance(renderer, EmailTemplateRendererProtocol)

    def test_smtp_service_satisfies_protocol(self):
        svc = SmtpEmailService()
        assert isinstance(svc, EmailServiceProtocol)

    def test_jinja_renderer_satisfies_protocol(self):
        renderer = JinjaEmailTemplateRenderer()
        assert isinstance(renderer, EmailTemplateRendererProtocol)


# ---------------------------------------------------------------------------
# 2. Infrastructure — SmtpEmailService unit tests
# ---------------------------------------------------------------------------

class TestSmtpEmailService:
    def test_build_mime_basic(self):
        svc = SmtpEmailService(
            host="localhost", port=25, username="u", password="p",
            from_address="from@test.com", from_name="Test"
        )
        msg = EmailMessage(to=["a@b.com"], subject="Sub", html_body="<p>Hi</p>")
        mime = svc._build_mime(msg)
        assert mime["Subject"] == "Sub"
        assert "a@b.com" in mime["To"]
        assert "Test <from@test.com>" in mime["From"]

    def test_build_mime_with_cc(self):
        svc = SmtpEmailService(
            host="localhost", port=25, username="u", password="p",
            from_address="from@test.com", from_name="Test"
        )
        msg = EmailMessage(
            to=["a@b.com"], subject="Sub", html_body="<p>Hi</p>",
            cc=["cc@test.com"]
        )
        mime = svc._build_mime(msg)
        assert "cc@test.com" in mime["Cc"]

    def test_all_recipients(self):
        svc = SmtpEmailService(
            host="localhost", port=25, username="u", password="p",
        )
        msg = EmailMessage(
            to=["a@b.com"], subject="Sub", html_body="<p>Hi</p>",
            cc=["cc@test.com"], bcc=["bcc@test.com"]
        )
        recipients = svc._all_recipients(msg)
        assert set(recipients) == {"a@b.com", "cc@test.com", "bcc@test.com"}

    @pytest.mark.asyncio
    async def test_send_disabled(self):
        svc = SmtpEmailService()
        msg = EmailMessage(to=["a@b.com"], subject="Sub", html_body="<p>Hi</p>")
        with patch("app.infrastructure.email.smtp_service.settings") as mock_settings:
            mock_settings.EMAIL_ENABLED = False
            mock_settings.SMTP_HOST = "smtp.gmail.com"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_USE_TLS = True
            mock_settings.SMTP_USERNAME = "u"
            mock_settings.SMTP_PASSWORD = "p"
            mock_settings.EMAIL_FROM_ADDRESS = "from@test.com"
            mock_settings.EMAIL_FROM_NAME = "Test"
            svc2 = SmtpEmailService()
            result = await svc2.send(msg)
            assert not result.success
            assert "disabled" in result.message.lower()

    @pytest.mark.asyncio
    async def test_send_no_credentials(self):
        with patch("app.infrastructure.email.smtp_service.settings") as mock_settings:
            mock_settings.EMAIL_ENABLED = True
            mock_settings.SMTP_HOST = "localhost"
            mock_settings.SMTP_PORT = 25
            mock_settings.SMTP_USE_TLS = False
            mock_settings.SMTP_USERNAME = None
            mock_settings.SMTP_PASSWORD = None
            mock_settings.EMAIL_FROM_ADDRESS = None
            mock_settings.EMAIL_FROM_NAME = "Test"
            svc = SmtpEmailService()
            msg = EmailMessage(to=["a@b.com"], subject="Sub", html_body="<p>Hi</p>")
            result = await svc.send(msg)
            assert not result.success
            assert "credentials" in result.message.lower()


# ---------------------------------------------------------------------------
# 3. Infrastructure — JinjaEmailTemplateRenderer
# ---------------------------------------------------------------------------

class TestJinjaTemplateRenderer:
    def test_render_record_notification(self):
        renderer = JinjaEmailTemplateRenderer()
        html = renderer.render("record_notification.html", {
            "subject": "Test",
            "subtitle": "PR • PR-001",
            "greeting": "Hello,",
            "message": "A new record was created.",
            "record_fields": [
                {"name": "id", "label": "ID", "value": "PR-001"},
                {"name": "description", "label": "Description", "value": "Test item"},
            ],
            "entity_label": "Purchase Request",
            "action_url": "https://example.com/pr/PR-001",
        })
        assert "PR-001" in html
        assert "Test item" in html
        assert "Purchase Request" in html
        assert "https://example.com/pr/PR-001" in html

    def test_render_without_action_url(self):
        renderer = JinjaEmailTemplateRenderer()
        html = renderer.render("record_notification.html", {
            "subject": "Test",
            "subtitle": "",
            "greeting": "Hi,",
            "message": "Updated.",
            "record_fields": [],
            "entity_label": "Asset",
            "action_url": None,
        })
        assert "View Asset" not in html


# ---------------------------------------------------------------------------
# 4. Application — EmailNotificationService
# ---------------------------------------------------------------------------

class TestEmailNotificationService:
    @pytest.mark.asyncio
    async def test_notify_record_event(self):
        fake = FakeEmailService()
        svc = _make_service(fake_email=fake)
        result = await svc.notify_record_event(
            entity_name="purchase_request",
            record={"id": "PR-001", "description": "Supplies", "workflow_state": "draft"},
            recipients=["user@test.com"],
            event_type="created",
        )
        assert result.success
        assert len(fake.sent) == 1
        assert "user@test.com" in fake.sent[0].to
        assert "[EAM]" in fake.sent[0].subject
        assert "PR-001" in fake.sent[0].subject

    @pytest.mark.asyncio
    async def test_notify_no_recipients(self):
        svc = _make_service()
        result = await svc.notify_record_event(
            entity_name="asset",
            record={"id": "A-001"},
            recipients=[],
            event_type="updated",
        )
        assert not result.success
        assert "No recipients" in result.message

    @pytest.mark.asyncio
    async def test_send_custom_email(self):
        fake = FakeEmailService()
        svc = _make_service(fake_email=fake)
        result = await svc.send_custom_email(
            recipients=["a@b.com"],
            subject="Custom",
            html_body="<p>Hello</p>",
        )
        assert result.success
        assert fake.sent[0].subject == "Custom"

    @pytest.mark.asyncio
    async def test_send_test_email(self):
        fake = FakeEmailService()
        svc = _make_service(fake_email=fake)
        result = await svc.send_test_email("test@example.com")
        assert result.success
        assert len(fake.sent) == 1
        assert "test@example.com" in fake.sent[0].to
        assert "PR-00001" in fake.sent[0].subject

    @pytest.mark.asyncio
    async def test_subject_building(self):
        assert "[EAM] New:" in EmailNotificationService._build_subject("Asset", "A-1", "created")
        assert "[EAM] Updated:" in EmailNotificationService._build_subject("Asset", "A-1", "updated")
        assert "[EAM] Status Changed:" in EmailNotificationService._build_subject("WO", "W-1", "workflow_changed")

    def test_format_record_fields_no_meta(self):
        fields = EmailNotificationService._format_record_fields(
            "test_entity",
            {"id": "T-1", "name": "Test", "status": "Active"},
            None,
        )
        labels = [f["label"] for f in fields]
        assert "Id" in labels
        assert "Name" in labels

    def test_plain_text_fallback(self):
        text = EmailNotificationService._build_plain_text(
            "Purchase Request", "PR-001", "A new record.",
            [{"label": "ID", "value": "PR-001"}],
        )
        assert "PR-001" in text
        assert "automated notification" in text.lower()


# ---------------------------------------------------------------------------
# 5. DI factory
# ---------------------------------------------------------------------------

class TestDIFactory:
    def test_get_email_notification_service(self):
        from app.api.dependencies import get_email_notification_service
        svc = get_email_notification_service()
        assert isinstance(svc, EmailNotificationService)
