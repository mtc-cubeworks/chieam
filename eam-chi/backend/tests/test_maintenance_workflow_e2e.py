"""
Maintenance Request, Work Order & Work Order Activity
Full Workflow E2E Test Suite

Covers:
  - Path A: Standard workflow (Draft → Pending Approval → Approved → Release → Completed)
  - Path B: Emergency workflow (Draft → Release, bypasses approval)
  - Reopen cascade (Completed → Release, cascades to WOA and WO)
  - Edge cases and validation checkpoints from Doc2_Maintenance_TestFlow.docx
  - Form state: field visibility rules in maintenance_request.json
  - Form state: editable_when in maintenance_request.json, work_order.json, work_order_activity.json

All tests are stateless (no DB) — they test business logic in isolation using mock doc objects.
"""
import pytest
import json
import os
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent / "app"
ENTITIES_DIR = BASE_DIR / "modules"


def load_entity_json(module: str, entity: str) -> dict:
    path = ENTITIES_DIR / module / "entities" / f"{entity}.json"
    with open(path) as f:
        return json.load(f)


class MockDoc:
    """Lightweight mock document that supports attribute get/set."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get(self, key, default=None):
        return getattr(self, key, default)


def make_db(
    get_doc_return=None,
    get_value_return=None,
    get_list_return=None,
):
    """Return an AsyncMock db with configurable return values."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


# ─────────────────────────────────────────────────────────────────────────────
# 1. JSON Form-State / Visibility Rules
# ─────────────────────────────────────────────────────────────────────────────

class TestMaintenanceRequestJSON:
    """Validate form_state and field visibility rules in maintenance_request.json."""

    def setup_method(self):
        self.data = load_entity_json("maintenance_mgmt", "maintenance_request")

    def test_workflow_states_defined(self):
        states = self.data["workflow"]["states"]
        assert "Draft" in states
        assert "Pending Approval" in states
        assert "Approved" in states
        assert "Release" in states
        assert "Completed" in states

    def test_workflow_transitions_complete(self):
        transitions = {(t["from"], t["action"]) for t in self.data["workflow"]["transitions"]}
        assert ("Draft", "Submit_for_Approval") in transitions
        assert ("Draft", "Submit_for_Emergency") in transitions
        assert ("Pending Approval", "Approve") in transitions
        assert ("Approved", "Submit_for_Resolution") in transitions
        assert ("Release", "Complete") in transitions
        assert ("Completed", "Reopen") in transitions

    def test_closed_date_only_visible_in_completed(self):
        fields = {f["name"]: f for f in self.data["fields"]}
        closed = fields.get("closed_date", {})
        show_when = closed.get("show_when", {})
        states = show_when.get("workflow_state", [])
        assert "completed" in states
        assert "draft" not in states
        assert "release" not in states

    def test_secondary_fields_hidden_on_new_and_draft(self):
        """Fields like asset, location, etc. should only appear from pending_approval onwards.
        Per spec: Draft state shows only Requestor, Requested Date, Description, Priority.
        Secondary fields appear after Submit for Approval (pending_approval state)."""
        fields = {f["name"]: f for f in self.data["fields"]}
        secondary = ["asset", "location", "site", "department", "position",
                     "planned_maintenance_activity", "due_date", "request_type"]
        for fname in secondary:
            f = fields.get(fname, {})
            sw = f.get("show_when", {})
            assert "workflow_state" in sw, f"Field '{fname}' missing show_when.workflow_state"
            # Should NOT include draft - only visible from pending_approval onwards
            assert "draft" not in sw["workflow_state"], f"Field '{fname}' should NOT be visible in draft"
            assert "pending_approval" in sw["workflow_state"], f"Field '{fname}' should be visible from pending_approval"

    def test_next_maintenance_request_visible_only_in_release_and_completed(self):
        fields = {f["name"]: f for f in self.data["fields"]}
        f = fields.get("next_maintenance_request", {})
        sw = f.get("show_when", {}).get("workflow_state", [])
        assert "release" in sw
        assert "completed" in sw
        assert "draft" not in sw

    def test_work_order_activity_always_hidden(self):
        fields = {f["name"]: f for f in self.data["fields"]}
        f = fields.get("work_order_activity", {})
        assert f.get("hidden") is True
        assert f.get("readonly") is True

    def test_form_state_editable_only_in_early_states(self):
        form_state = self.data.get("form_state", {})
        editable = form_state.get("editable_when", {}).get("workflow_state", [])
        assert "draft" in editable
        assert "pending_approval" in editable
        assert "approved" in editable
        # Must NOT be editable after release
        assert "release" not in editable
        assert "completed" not in editable

    def test_closed_date_is_readonly(self):
        fields = {f["name"]: f for f in self.data["fields"]}
        f = fields.get("closed_date", {})
        assert f.get("readonly") is True


class TestWorkOrderJSON:
    """Validate form_state rules in work_order.json."""

    def setup_method(self):
        self.data = load_entity_json("work_mgmt", "work_order")

    def test_workflow_states_defined(self):
        states = self.data["workflow"]["states"]
        assert "Requested" in states
        assert "Approved" in states
        assert "In Progress" in states
        assert "Closed" in states

    def test_form_state_editable_only_in_requested(self):
        form_state = self.data.get("form_state", {})
        editable = form_state.get("editable_when", {}).get("workflow_state", [])
        assert "requested" in editable
        assert "approved" not in editable
        assert "in_progress" not in editable
        assert "closed" not in editable

    def test_workflow_transitions(self):
        transitions = {(t["from"], t["action"]) for t in self.data["workflow"]["transitions"]}
        assert ("Requested", "Approve") in transitions
        assert ("Approved", "Start") in transitions
        assert ("In Progress", "Complete") in transitions
        assert ("Closed", "Reopen") in transitions


class TestWorkOrderActivityJSON:
    """Validate form_state rules in work_order_activity.json."""

    def setup_method(self):
        self.data = load_entity_json("work_mgmt", "work_order_activity")

    def test_workflow_states_defined(self):
        states = self.data["workflow"]["states"]
        expected = ["Awaiting Resources", "Ready", "In Progress", "On Hold", "Completed", "Closed"]
        for s in expected:
            assert s in states

    def test_workflow_transitions(self):
        transitions = {(t["from"], t["action"]) for t in self.data["workflow"]["transitions"]}
        assert ("Awaiting Resources", "Allocate") in transitions
        assert ("Ready", "Start_Activity") in transitions
        assert ("In Progress", "Put_On_Hold") in transitions
        assert ("On Hold", "Resume") in transitions
        assert ("In Progress", "Complete") in transitions
        assert ("Completed", "Reopen") in transitions
        assert ("Completed", "Close") in transitions

    def test_form_state_editable_only_in_early_states(self):
        form_state = self.data.get("form_state", {})
        editable = form_state.get("editable_when", {}).get("workflow_state", [])
        assert "awaiting_resources" in editable
        assert "ready" in editable
        assert "in_progress" not in editable
        assert "completed" not in editable
        assert "closed" not in editable


# ─────────────────────────────────────────────────────────────────────────────
# 2. MR Workflow Handler — Action Routing
# ─────────────────────────────────────────────────────────────────────────────

class TestMRWorkflowActionRouting:

    @pytest.fixture
    def module(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        return check_maintenance_request_workflow

    @pytest.mark.asyncio
    async def test_missing_doc_returns_error(self, module):
        result = await module(None, "Approve", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "not specified" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_missing_id_returns_error(self, module):
        doc = MockDoc()
        result = await module(doc, "Approve", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "id" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self, module):
        doc = MockDoc(id="MR-001")
        result = await module(doc, "DoSomethingWild", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "invalid action" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_submit_for_approval_always_succeeds(self, module):
        doc = MockDoc(id="MR-001")
        result = await module(doc, "Submit for Approval", AsyncMock(), MagicMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_action_normalisation_with_spaces(self, module):
        """Action labels with spaces and capitals must be normalised."""
        doc = MockDoc(id="MR-001")
        result = await module(doc, "Submit for Approval", AsyncMock(), MagicMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Path A — Submit for Emergency validation
# ─────────────────────────────────────────────────────────────────────────────

class TestSubmitForEmergencyValidation:

    @pytest.fixture
    def module(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        return check_maintenance_request_workflow

    @pytest.mark.asyncio
    async def test_emergency_blocked_when_priority_not_emergency(self, module):
        doc = MockDoc(id="MR-002", priority="Medium", site="SITE-001", department="DEPT-ENG")
        result = await module(doc, "Submit for Emergency", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "emergency" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_emergency_blocked_when_priority_high(self, module):
        doc = MockDoc(id="MR-003", priority="High", site="SITE-001", department="DEPT-ENG")
        result = await module(doc, "Submit for Emergency", AsyncMock(), MagicMock())
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_emergency_blocked_when_priority_none(self, module):
        doc = MockDoc(id="MR-004", priority=None, site="SITE-001", department="DEPT-ENG")
        result = await module(doc, "Submit for Emergency", AsyncMock(), MagicMock())
        assert result["status"] == "error"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Submit for Resolution — must have WOA linked
# ─────────────────────────────────────────────────────────────────────────────

class TestSubmitForResolution:

    @pytest.fixture
    def module(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        return check_maintenance_request_workflow

    @pytest.mark.asyncio
    async def test_submit_for_resolution_blocked_when_no_woa(self, module):
        doc = MockDoc(id="MR-001", work_order_activity=None)
        result = await module(doc, "Submit for Resolution", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "work order activity" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_submit_for_resolution_blocked_when_woa_not_found(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-MISSING")
        db = AsyncMock()

        async def fake_get_doc(entity, record_id, session):
            return None  # WOA not found

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            result = await module(doc, "Submit for Resolution", db, MagicMock())
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_submit_for_resolution_succeeds_when_woa_linked(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001")
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="awaiting_resources")

        async def fake_get_doc(entity, record_id, session):
            if entity == "work_order_activity":
                return mock_woa
            return None

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            result = await module(doc, "Submit for Resolution", db, MagicMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 5. MR Complete — WOA must be Completed
# ─────────────────────────────────────────────────────────────────────────────

class TestMRComplete:

    @pytest.fixture
    def module(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        return check_maintenance_request_workflow

    @pytest.mark.asyncio
    async def test_complete_blocked_when_no_woa(self, module):
        doc = MockDoc(id="MR-001", work_order_activity=None)
        result = await module(doc, "Complete", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "work order activity" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_complete_blocked_when_woa_in_progress(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001")
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="in_progress")

        async def fake_get_doc(entity, record_id, session):
            if entity == "work_order_activity":
                return mock_woa
            return None

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "error"
        assert "completed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_complete_blocked_when_woa_awaiting_resources(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001")
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="awaiting_resources")

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_complete_succeeds_when_woa_completed(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=None)
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed")

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "success"
        assert doc.closed_date == date.today()

    @pytest.mark.asyncio
    async def test_complete_succeeds_when_woa_closed(self, module):
        """WOA in 'closed' state also counts as complete."""
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=None)
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="closed")

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "success"
        assert doc.closed_date == date.today()

    @pytest.mark.asyncio
    async def test_complete_sets_closed_date_to_today(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=None)
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed")

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                await module(doc, "Complete", db, MagicMock())
        assert doc.closed_date == date.today()


# ─────────────────────────────────────────────────────────────────────────────
# 6. MR Reopen — cascade to WOA and WO, clear closed_date
# ─────────────────────────────────────────────────────────────────────────────

class TestMRReopen:

    @pytest.fixture
    def module(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        return check_maintenance_request_workflow

    @pytest.mark.asyncio
    async def test_reopen_blocked_when_no_woa(self, module):
        doc = MockDoc(id="MR-001", work_order_activity=None)
        result = await module(doc, "Reopen", AsyncMock(), MagicMock())
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_reopen_clears_closed_date(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=date.today())
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed", work_order="WO-001")
        mock_wo = MockDoc(id="WO-001", workflow_state="closed")

        docs = {"WOA-001": mock_woa, "WO-001": mock_wo}

        async def fake_get_doc(entity, record_id, session):
            return docs.get(record_id)

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                result = await module(doc, "Reopen", db, MagicMock())
        assert result["status"] == "success"
        assert doc.closed_date is None

    @pytest.mark.asyncio
    async def test_reopen_cascades_woa_to_in_progress(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=date.today())
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed", work_order=None)

        async def fake_get_doc(entity, record_id, session):
            if entity == "work_order_activity":
                return mock_woa
            return None

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                await module(doc, "Reopen", db, MagicMock())
        assert mock_woa.workflow_state == "in_progress"

    @pytest.mark.asyncio
    async def test_reopen_cascades_closed_wo_to_in_progress(self, module):
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=date.today())
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed", work_order="WO-001")
        mock_wo = MockDoc(id="WO-001", workflow_state="closed")

        docs = {"WOA-001": mock_woa, "WO-001": mock_wo}

        async def fake_get_doc(entity, record_id, session):
            return docs.get(record_id)

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                await module(doc, "Reopen", db, MagicMock())
        assert mock_wo.workflow_state == "in_progress"

    @pytest.mark.asyncio
    async def test_reopen_does_not_change_in_progress_wo(self, module):
        """If WO is already in_progress, it should stay in_progress."""
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001", closed_date=date.today())
        db = AsyncMock()
        mock_woa = MockDoc(id="WOA-001", workflow_state="completed", work_order="WO-001")
        mock_wo = MockDoc(id="WO-001", workflow_state="in_progress")

        docs = {"WOA-001": mock_woa, "WO-001": mock_wo}

        async def fake_get_doc(entity, record_id, session):
            return docs.get(record_id)

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                result = await module(doc, "Reopen", db, MagicMock())
        assert result["status"] == "success"
        assert mock_wo.workflow_state == "in_progress"  # unchanged


# ─────────────────────────────────────────────────────────────────────────────
# 7. Path A — _approve_and_generate_wo validations
# ─────────────────────────────────────────────────────────────────────────────

class TestApproveGenerateWO:

    @pytest.fixture
    def fn(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import _approve_and_generate_wo
        return _approve_and_generate_wo

    @pytest.mark.asyncio
    async def test_approve_blocked_when_no_asset(self, fn):
        doc = MockDoc(id="MR-001", asset=None, site="SITE-001", department="DEPT-001")
        result = await fn(doc, AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "asset" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_approve_blocked_when_no_site(self, fn):
        doc = MockDoc(id="MR-001", asset="ASSET-001", site=None, department="DEPT-001")
        db = AsyncMock()
        result = await fn(doc, db, MagicMock())
        assert result["status"] == "error"
        assert "site" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_approve_blocked_when_no_department(self, fn):
        doc = MockDoc(id="MR-001", asset="ASSET-001", site="SITE-001", department=None)
        db = AsyncMock()
        result = await fn(doc, db, MagicMock())
        assert result["status"] == "error"
        assert "department" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_approve_blocked_when_asset_not_found(self, fn):
        doc = MockDoc(id="MR-001", asset="ASSET-GONE", site="SITE-001", department="DEPT-001",
                      priority="Medium", due_date=None, planned_maintenance_activity=None,
                      request_type=None, description="Test", location=None)
        db = AsyncMock()

        async def fake_get_doc(entity, record_id, session):
            return None

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            result = await fn(doc, db, MagicMock())
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_approve_creates_wo_and_woa(self, fn):
        doc = MockDoc(id="MR-001", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Medium", due_date=date(2025, 6, 8),
                      planned_maintenance_activity=None, request_type=None,
                      description="Test PM", location="LOC-001", work_order_activity=None)

        mock_asset = MockDoc(id="ASSET-001", description="Cooling Tower Fan Motor")
        mock_wo = MockDoc(id="WO-001", workflow_state="requested")
        mock_woa = MockDoc(id="WOA-001", workflow_state="awaiting_resources")

        db = AsyncMock()
        saved = []

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            if entity == "work_order":
                for k, v in kwargs.items():
                    setattr(mock_wo, k, v)
                return mock_wo
            if entity == "work_order_activity":
                for k, v in kwargs.items():
                    setattr(mock_woa, k, v)
                return mock_woa
            return MagicMock(id=f"NEW-{entity}")

        async def fake_save_doc(d, session, commit=True):
            saved.append(d)

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                        result = await fn(doc, db, MagicMock())

        assert result["status"] == "success"
        # WOA must be linked back to MR
        assert doc.work_order_activity == "WOA-001"
        # WO must be in Requested state (not pre-approved)
        assert mock_wo.workflow_state == "requested"
        # WOA must be in Awaiting Resources state
        assert mock_woa.workflow_state == "awaiting_resources"


# ─────────────────────────────────────────────────────────────────────────────
# 8. Path B — _emergency_generate_wo validations
# ─────────────────────────────────────────────────────────────────────────────

class TestEmergencyGenerateWO:

    @pytest.fixture
    def fn(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import _emergency_generate_wo
        return _emergency_generate_wo

    @pytest.mark.asyncio
    async def test_emergency_blocked_when_no_site(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site=None, department="DEPT-001", priority="Emergency")
        result = await fn(doc, AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "site" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_emergency_blocked_when_no_department(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department=None, priority="Emergency")
        result = await fn(doc, AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "department" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_emergency_wo_due_date_set_to_today(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Emergency", location=None, request_type=None,
                      description="Emergency test", work_order_activity=None)

        mock_asset = MockDoc(id="ASSET-001", description="Cooling Tower Fan Motor")
        mock_wo = MockDoc(id="WO-002", workflow_state="requested")
        mock_woa = MockDoc(id="WOA-002", workflow_state="awaiting_resources")

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            if entity == "work_order":
                for k, v in kwargs.items():
                    setattr(mock_wo, k, v)
                return mock_wo
            if entity == "work_order_activity":
                for k, v in kwargs.items():
                    setattr(mock_woa, k, v)
                return mock_woa
            return MagicMock(id=f"NEW-{entity}")

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                        result = await fn(doc, AsyncMock(), MagicMock())

        assert result["status"] == "success"
        assert mock_wo.due_date == date.today()
        assert mock_wo.priority == "Emergency"

    @pytest.mark.asyncio
    async def test_emergency_wo_state_is_requested(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Emergency", location=None, request_type=None,
                      description="Emergency", work_order_activity=None)
        mock_asset = MockDoc(id="ASSET-001", description="Fan")
        mock_wo = MockDoc(id="WO-002")
        mock_woa = MockDoc(id="WOA-002")

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            obj = mock_wo if entity == "work_order" else mock_woa
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return obj

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                        await fn(doc, AsyncMock(), MagicMock())

        assert mock_wo.workflow_state == "requested"

    @pytest.mark.asyncio
    async def test_emergency_woa_state_is_awaiting_resources(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Emergency", location=None, request_type=None,
                      description="Emergency", work_order_activity=None)
        mock_asset = MockDoc(id="ASSET-001", description="Fan")
        mock_wo = MockDoc(id="WO-002")
        mock_woa = MockDoc(id="WOA-002")

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            obj = mock_wo if entity == "work_order" else mock_woa
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return obj

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                        await fn(doc, AsyncMock(), MagicMock())

        assert mock_woa.workflow_state == "awaiting_resources"

    @pytest.mark.asyncio
    async def test_emergency_woa_linked_to_mr(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Emergency", location=None, request_type=None,
                      description="Emergency", work_order_activity=None)
        mock_asset = MockDoc(id="ASSET-001", description="Fan")
        mock_wo = MockDoc(id="WO-002")
        mock_woa = MockDoc(id="WOA-002")

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            obj = mock_wo if entity == "work_order" else mock_woa
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return obj

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                        await fn(doc, AsyncMock(), MagicMock())

        assert doc.work_order_activity == "WOA-002"

    @pytest.mark.asyncio
    async def test_emergency_woa_type_is_asset(self, fn):
        doc = MockDoc(id="MR-002", asset="ASSET-001", site="SITE-001", department="DEPT-001",
                      priority="Emergency", location="LOC-001", request_type=None,
                      description="Emergency", work_order_activity=None)
        mock_asset = MockDoc(id="ASSET-001", description="Fan")
        mock_wo = MockDoc(id="WO-002")
        mock_woa = MockDoc(id="WOA-002")

        async def fake_get_doc(entity, record_id, session):
            if entity == "asset":
                return mock_asset
            return None

        async def fake_get_value(*args, **kwargs):
            return None

        async def fake_new_doc(entity, session, **kwargs):
            obj = mock_wo if entity == "work_order" else mock_woa
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return obj

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_value", new=AsyncMock(side_effect=fake_get_value)):
                with patch("app.modules.maintenance_mgmt.apis.maintenance_request.new_doc", new=AsyncMock(side_effect=fake_new_doc)):
                    with patch("app.modules.maintenance_mgmt.apis.maintenance_request.save_doc", new=AsyncMock()):
                        await fn(doc, AsyncMock(), MagicMock())

        assert mock_woa.work_item_type == "Asset"


# ─────────────────────────────────────────────────────────────────────────────
# 9. Work Order Workflow
# ─────────────────────────────────────────────────────────────────────────────

class TestWorkOrderWorkflow:
    """
    work_order_workflow imports get_list/get_doc/save_doc inside its function body
    via 'from app.services.document import ...', so we patch app.services.document.
    """

    @pytest.fixture
    def module(self):
        from app.modules.work_mgmt.workflow_router import work_order_workflow
        return work_order_workflow

    @pytest.mark.asyncio
    async def test_approve_always_succeeds(self, module):
        doc = MockDoc(id="WO-001", workflow_state="requested")
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=[])):
            result = await module(doc, "Approve", db, MagicMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_start_blocked_when_no_activities(self, module):
        doc = MockDoc(id="WO-001", workflow_state="approved")
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=[])):
            result = await module(doc, "Start", db, MagicMock())
        assert result["status"] == "error"
        assert "activities" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_start_blocked_when_woa_not_all_ready(self, module):
        doc = MockDoc(id="WO-001")
        activities = [
            {"id": "WOA-001", "workflow_state": "ready"},
            {"id": "WOA-002", "workflow_state": "awaiting_resources"},
        ]
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            result = await module(doc, "Start", db, MagicMock())
        assert result["status"] == "error"
        assert "ready" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_start_succeeds_when_all_woas_ready(self, module):
        doc = MockDoc(id="WO-001")
        activities = [
            {"id": "WOA-001", "workflow_state": "ready"},
            {"id": "WOA-002", "workflow_state": "ready"},
        ]
        mock_woa1 = MockDoc(id="WOA-001", workflow_state="ready")
        mock_woa2 = MockDoc(id="WOA-002", workflow_state="ready")
        woa_docs = {"WOA-001": mock_woa1, "WOA-002": mock_woa2}
        db = AsyncMock()

        async def fake_get_doc(entity, record_id, session):
            return woa_docs.get(record_id)

        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            with patch("app.services.document.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
                with patch("app.services.document.save_doc", new=AsyncMock()):
                    result = await module(doc, "Start", db, MagicMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_start_cascades_woas_to_in_progress(self, module):
        """When WO starts, all child WOAs must transition to in_progress."""
        doc = MockDoc(id="WO-001")
        activities = [{"id": "WOA-001", "workflow_state": "ready"}]
        mock_woa = MockDoc(id="WOA-001", workflow_state="ready")
        db = AsyncMock()

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        async def fake_save_doc(d, session, commit=True):
            pass

        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            with patch("app.services.document.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
                with patch("app.services.document.save_doc", new=AsyncMock(side_effect=fake_save_doc)):
                    await module(doc, "Start", db, MagicMock())
        assert mock_woa.workflow_state == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_blocked_when_woa_in_progress(self, module):
        doc = MockDoc(id="WO-001")
        activities = [
            {"id": "WOA-001", "workflow_state": "completed"},
            {"id": "WOA-002", "workflow_state": "in_progress"},
        ]
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "error"
        assert "complete" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_complete_succeeds_when_all_woas_completed_or_closed(self, module):
        doc = MockDoc(id="WO-001")
        activities = [
            {"id": "WOA-001", "workflow_state": "completed"},
            {"id": "WOA-002", "workflow_state": "closed"},
        ]
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            result = await module(doc, "Complete", db, MagicMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_reopen_always_succeeds(self, module):
        doc = MockDoc(id="WO-001")
        db = AsyncMock()
        with patch("app.services.document.get_list", new=AsyncMock(return_value=[])):
            result = await module(doc, "Reopen", db, MagicMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 10. WOA Allocate — labor required; PMA requires equipment + parts too
# ─────────────────────────────────────────────────────────────────────────────

class TestWOAAllocate:

    @pytest.fixture
    def fn(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_allocate
        return _handle_allocate

    @pytest.mark.asyncio
    async def test_allocate_blocked_when_no_labor(self, fn):
        doc = MockDoc(id="WOA-001")
        result = await fn(doc, [], [], [], None, AsyncMock())
        assert result["status"] == "error"
        assert "labor" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_allocate_succeeds_when_labor_present_no_pma(self, fn):
        doc = MockDoc(id="WOA-001")
        wo_labor = [{"id": "WOL-001", "labor": "LAB-001"}]
        maint_req = None  # no PMA
        result = await fn(doc, wo_labor, [], [], maint_req, AsyncMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_allocate_blocked_when_pma_linked_but_no_equipment(self, fn):
        doc = MockDoc(id="WOA-001")
        wo_labor = [{"id": "WOL-001"}]
        wo_equip = []
        wo_parts = [{"id": "WOP-001"}]
        maint_req = {"id": "MR-001", "planned_maintenance_activity": "PMA-001"}
        db = AsyncMock()

        pma = {"id": "PMA-001", "maintenance_activity": "MA-001"}
        maint_equip = {"id": "MEQ-001", "asset_class": "AC-001"}

        async def fake_get_value(entity, filters, fields, session):
            if entity == "planned_maintenance_activity":
                return pma
            if entity == "maintenance_equipment":
                return maint_equip
            if entity == "maintenance_parts":
                return None
            return None

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value", new=AsyncMock(side_effect=fake_get_value)):
            result = await fn(doc, wo_labor, wo_equip, wo_parts, maint_req, db)
        assert result["status"] == "error"
        assert "equipment" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_allocate_blocked_when_pma_linked_but_no_parts(self, fn):
        doc = MockDoc(id="WOA-001")
        wo_labor = [{"id": "WOL-001"}]
        wo_equip = [{"id": "WOE-001"}]
        wo_parts = []
        maint_req = {"id": "MR-001", "planned_maintenance_activity": "PMA-001"}
        db = AsyncMock()

        pma = {"id": "PMA-001", "maintenance_activity": "MA-001"}
        maint_parts = {"id": "MP-001", "item": "ITEM-001"}

        async def fake_get_value(entity, filters, fields, session):
            if entity == "planned_maintenance_activity":
                return pma
            if entity == "maintenance_equipment":
                return None
            if entity == "maintenance_parts":
                return maint_parts
            return None

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value", new=AsyncMock(side_effect=fake_get_value)):
            result = await fn(doc, wo_labor, wo_equip, wo_parts, maint_req, db)
        assert result["status"] == "error"
        assert "parts" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_allocate_succeeds_with_pma_and_all_resources(self, fn):
        doc = MockDoc(id="WOA-001")
        wo_labor = [{"id": "WOL-001"}]
        wo_equip = [{"id": "WOE-001"}]
        wo_parts = [{"id": "WOP-001"}]
        maint_req = {"id": "MR-001", "planned_maintenance_activity": "PMA-001"}
        db = AsyncMock()

        pma = {"id": "PMA-001", "maintenance_activity": "MA-001"}
        maint_equip = {"id": "MEQ-001"}
        maint_parts = {"id": "MP-001"}

        async def fake_get_value(entity, filters, fields, session):
            if entity == "planned_maintenance_activity":
                return pma
            if entity == "maintenance_equipment":
                return maint_equip
            if entity == "maintenance_parts":
                return maint_parts
            return None

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value", new=AsyncMock(side_effect=fake_get_value)):
            result = await fn(doc, wo_labor, wo_equip, wo_parts, maint_req, db)
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 11. WOA Close — parts issued and actual hours required
# ─────────────────────────────────────────────────────────────────────────────

class TestWOAClose:

    @pytest.fixture
    def fn(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_close
        return _handle_close

    @pytest.mark.asyncio
    async def test_close_blocked_when_no_activity_logs(self, fn):
        doc = MockDoc(id="WOA-001")
        db = AsyncMock()

        async def fake_get_list(entity, filters, db=None, as_dict=False):
            return []

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            result = await fn(doc, "WOA-001", [], [], [], db)
        assert result["status"] == "error"
        assert "activity logs" in result["message"].lower() or "logs" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_close_blocked_when_parts_not_issued(self, fn):
        doc = MockDoc(id="WOA-001")
        db = AsyncMock()
        wo_parts = [{"id": "WOP-001", "quantity_required": 5, "quantity_issued": 0}]

        call_count = [0]

        async def fake_get_list(entity, filters, db=None, as_dict=False):
            if entity == "work_order_activity_logs":
                return [{"id": "LOG-001"}]  # has logs
            return []

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            result = await fn(doc, "WOA-001", [], [], wo_parts, db)
        assert result["status"] == "error"
        assert "part" in result["message"].lower() or "issuance" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_close_blocked_when_labor_missing_actual_hours(self, fn):
        doc = MockDoc(id="WOA-001", end_date=None)
        db = AsyncMock()
        wo_labor = [{"id": "WOL-001"}]

        async def fake_get_list(entity, filters, db=None, as_dict=False):
            if entity == "work_order_activity_logs":
                return [{"id": "LOG-001"}]
            if entity == "work_order_labor_actual_hours":
                return []  # no actual hours
            return []

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            result = await fn(doc, "WOA-001", wo_labor, [], [], db)
        assert result["status"] == "error"
        assert "actual hours" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_close_blocked_when_equipment_missing_actual_hours(self, fn):
        doc = MockDoc(id="WOA-001", end_date=None)
        db = AsyncMock()
        wo_equip = [{"id": "WOE-001"}]

        async def fake_get_list(entity, filters, db=None, as_dict=False):
            if entity == "work_order_activity_logs":
                return [{"id": "LOG-001"}]
            if entity == "work_order_equipment_actual_hours":
                return []
            return []

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            result = await fn(doc, "WOA-001", [], wo_equip, [], db)
        assert result["status"] == "error"
        assert "actual hours" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_close_succeeds_when_all_conditions_met(self, fn):
        doc = MockDoc(id="WOA-001", end_date=None)
        db = AsyncMock()
        wo_labor = [{"id": "WOL-001"}]
        wo_equip = [{"id": "WOE-001"}]
        wo_parts = [{"id": "WOP-001", "quantity_required": 2, "quantity_issued": 2}]

        async def fake_get_list(entity, filters, db=None, as_dict=False):
            if entity == "work_order_activity_logs":
                return [{"id": "LOG-001"}]
            if entity == "work_order_labor_actual_hours":
                return [{"id": "LAH-001", "actual_hours": 2.0}]
            if entity == "work_order_equipment_actual_hours":
                return [{"id": "EAH-001", "actual_hours": 1.0}]
            return []

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            with patch("app.modules.work_mgmt.apis.work_order_activity.save_doc", new=AsyncMock()):
                result = await fn(doc, "WOA-001", wo_labor, wo_equip, wo_parts, db)
        assert result["status"] == "success"
        assert doc.end_date is not None


# ─────────────────────────────────────────────────────────────────────────────
# 12. WOA Start Activity
# ─────────────────────────────────────────────────────────────────────────────

class TestWOAStartActivity:

    @pytest.fixture
    def fn(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_start_activity
        return _handle_start_activity

    @pytest.mark.asyncio
    async def test_start_blocked_when_no_work_order_linked(self, fn):
        doc = MockDoc(id="WOA-001", work_order=None, work_item_type="Asset", activity_type="RAT-001")
        result = await fn(doc, None, AsyncMock())
        assert result["status"] == "error"
        assert "work order" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_start_succeeds_when_work_order_linked(self, fn):
        doc = MockDoc(id="WOA-001", work_order="WO-001", work_item_type="Asset", activity_type="RAT-001")
        mock_wo = MockDoc(id="WO-001", workflow_state="approved")

        async def fake_get_value(*args, **kwargs):
            return {"id": "RAT-001", "menu": "Maintain Asset"}

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value", new=AsyncMock(side_effect=fake_get_value)):
            result = await fn(doc, mock_wo, AsyncMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 13. WOA Workflow Router — normalises action labels
# ─────────────────────────────────────────────────────────────────────────────

class TestWOAWorkflowRouter:

    @pytest.fixture
    def module(self):
        from app.modules.work_mgmt.apis.work_order_activity import check_work_order_activity_workflow
        return check_work_order_activity_workflow

    @pytest.mark.asyncio
    async def test_missing_doc_returns_error(self, module):
        result = await module(None, "allocate", AsyncMock(), MagicMock())
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_put_on_hold_and_resume_are_recognised(self, module):
        """put_on_hold and resume should not raise errors even with no data."""
        doc = MockDoc(id="WOA-001", work_order="WO-001")
        db = AsyncMock()

        async def fake_get_list(*args, **kwargs):
            return []

        async def fake_get_doc(entity, record_id, session):
            return None

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_list", new=AsyncMock(side_effect=fake_get_list)):
            with patch("app.modules.work_mgmt.apis.work_order_activity.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
                with patch("app.modules.work_mgmt.apis.work_order_activity.get_value", new=AsyncMock(return_value=None)):
                    result = await module(doc, "put_on_hold", db, MagicMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 14. Workflow Router Registration
# ─────────────────────────────────────────────────────────────────────────────

class TestWorkflowRouterRegistration:

    def test_maintenance_router_has_maintenance_request(self):
        from app.modules.maintenance_mgmt.workflow_router import _WORKFLOW_HANDLERS
        assert "maintenance_request" in _WORKFLOW_HANDLERS

    def test_maintenance_router_has_maintenance_order(self):
        from app.modules.maintenance_mgmt.workflow_router import _WORKFLOW_HANDLERS
        assert "maintenance_order" in _WORKFLOW_HANDLERS

    def test_work_router_has_work_order(self):
        from app.modules.work_mgmt.workflow_router import _WORKFLOW_HANDLERS
        assert "work_order" in _WORKFLOW_HANDLERS

    def test_work_router_has_work_order_activity(self):
        from app.modules.work_mgmt.workflow_router import _WORKFLOW_HANDLERS
        assert "work_order_activity" in _WORKFLOW_HANDLERS

    def test_work_router_has_work_order_parts(self):
        from app.modules.work_mgmt.workflow_router import _WORKFLOW_HANDLERS
        assert "work_order_parts" in _WORKFLOW_HANDLERS

    @pytest.mark.asyncio
    async def test_maintenance_router_routes_to_handler(self):
        from app.modules.maintenance_mgmt.workflow_router import route_workflow
        doc = MockDoc(id="MR-001")
        result = await route_workflow("maintenance_request", doc, "Submit for Approval", AsyncMock(), MagicMock())
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_work_router_routes_to_handler(self):
        from app.modules.work_mgmt.workflow_router import route_workflow
        doc = MockDoc(id="WO-001")
        with patch("app.services.document.get_list", new=AsyncMock(return_value=[])):
            result = await route_workflow("work_order", doc, "Approve", AsyncMock(), MagicMock())
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# 15. Edge Cases Summary (Doc2 Table 74)
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:
    """
    Edge cases from Doc2_Maintenance_TestFlow.docx — Table 74.
    Validates all documented error scenarios.
    """

    @pytest.mark.asyncio
    async def test_edge_submit_for_resolution_with_no_woa(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        doc = MockDoc(id="MR-001", work_order_activity=None)
        result = await check_maintenance_request_workflow(doc, "Submit for Resolution", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "work order activity" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_edge_complete_mr_with_woa_not_completed(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        doc = MockDoc(id="MR-001", work_order_activity="WOA-001")
        mock_woa = MockDoc(id="WOA-001", workflow_state="in_progress")

        async def fake_get_doc(entity, record_id, session):
            return mock_woa

        with patch("app.modules.maintenance_mgmt.apis.maintenance_request.get_doc", new=AsyncMock(side_effect=fake_get_doc)):
            result = await check_maintenance_request_workflow(doc, "Complete", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "completed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_edge_start_wo_with_woa_not_ready(self):
        from app.modules.work_mgmt.workflow_router import work_order_workflow
        doc = MockDoc(id="WO-001")
        activities = [{"id": "WOA-001", "workflow_state": "awaiting_resources"}]

        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            result = await work_order_workflow(doc, "Start", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "ready" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_edge_complete_wo_with_woa_not_completed(self):
        from app.modules.work_mgmt.workflow_router import work_order_workflow
        doc = MockDoc(id="WO-001")
        activities = [{"id": "WOA-001", "workflow_state": "in_progress"}]

        with patch("app.services.document.get_list", new=AsyncMock(return_value=activities)):
            result = await work_order_workflow(doc, "Complete", AsyncMock(), MagicMock())
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_edge_allocate_woa_with_no_labor(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_allocate
        doc = MockDoc(id="WOA-001")
        result = await _handle_allocate(doc, [], [], [], None, AsyncMock())
        assert result["status"] == "error"
        assert "labor" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_edge_emergency_with_non_emergency_priority(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        doc = MockDoc(id="MR-001", priority="Low", site="SITE-001", department="DEPT-001")
        result = await check_maintenance_request_workflow(doc, "Submit for Emergency", AsyncMock(), MagicMock())
        assert result["status"] == "error"
        assert "emergency" in result["message"].lower()
