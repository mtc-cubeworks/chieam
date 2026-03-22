"""
Tests for the workflow infrastructure changes:
1. apply_workflow_state() validates transitions
2. Human-readable action labels are resolved
3. Rollback on errors prevents partial data
4. Redirect pattern for record-creating actions

Patching strategy:
- workflow_router.py uses lazy imports inside functions, so we patch at the
  source module (app.services.document) rather than at the consumer module.
- For _apply_line_workflow we patch the module-level function directly.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# 1. apply_workflow_state() tests
# =============================================================================

class TestApplyWorkflowState:
    """Test apply_workflow_state validates transitions before setting state."""

    @pytest.mark.asyncio
    async def test_valid_transition_sets_state(self):
        """apply_workflow_state should set workflow_state when transition is valid."""
        from app.services.document import apply_workflow_state

        mock_db = AsyncMock()

        with patch("app.services.workflow.WorkflowService.get_workflow") as mock_get_wf, \
             patch("app.services.workflow.WorkflowService.validate_transition",
                   return_value=(True, "pending_review", None)), \
             patch("app.services.workflow.WorkflowService.get_initial_state",
                   return_value="draft"):

            class Doc:
                workflow_state = "draft"

            doc = Doc()
            result = await apply_workflow_state("purchase_request", doc, "submit_for_review", mock_db)

            assert result["status"] == "success"
            assert result["from_state"] == "draft"
            assert result["to_state"] == "pending_review"
            assert doc.workflow_state == "pending_review"

    @pytest.mark.asyncio
    async def test_invalid_transition_returns_error(self):
        """apply_workflow_state should return error and NOT change state for invalid transition."""
        from app.services.document import apply_workflow_state

        mock_db = AsyncMock()

        with patch("app.services.workflow.WorkflowService.validate_transition",
                   return_value=(False, None, "Action 'approve' not available from state 'draft'")):

            class Doc:
                workflow_state = "draft"

            doc = Doc()
            result = await apply_workflow_state("purchase_request", doc, "approve", mock_db)

            assert result["status"] == "error"
            assert "not available" in result["message"]
            assert doc.workflow_state == "draft"  # unchanged

    @pytest.mark.asyncio
    async def test_empty_state_falls_back_to_initial(self):
        """apply_workflow_state should use initial state when workflow_state is empty."""
        from app.services.document import apply_workflow_state

        mock_db = AsyncMock()

        with patch("app.services.workflow.WorkflowService.get_initial_state",
                   return_value="draft") as mock_initial, \
             patch("app.services.workflow.WorkflowService.validate_transition",
                   return_value=(True, "pending_review", None)):

            class Doc:
                workflow_state = ""

            doc = Doc()
            result = await apply_workflow_state("purchase_request", doc, "submit_for_review", mock_db)

            assert result["status"] == "success"
            assert result["from_state"] == "draft"
            mock_initial.assert_called_once()


# =============================================================================
# 2. Human-readable action label resolution
# =============================================================================

class TestActionLabelResolution:
    """Test that WorkflowDBService.get_action_label returns human-readable labels."""

    @pytest.mark.asyncio
    async def test_get_action_label_returns_label(self):
        """get_action_label should return the label for a known action slug."""
        from app.services.workflow import WorkflowService

        mock_action = MagicMock()
        mock_action.slug = "submit_for_approval"
        mock_action.label = "Submit for Approval"

        mock_transition = MagicMock()
        mock_transition.action_ref = mock_action

        mock_workflow = MagicMock()
        mock_workflow.transitions = [mock_transition]

        mock_db = AsyncMock()

        with patch.object(WorkflowService, "get_workflow", return_value=mock_workflow):
            label = await WorkflowService.get_action_label(mock_db, "purchase_request", "submit_for_approval")
            assert label == "Submit for Approval"

    @pytest.mark.asyncio
    async def test_get_action_label_returns_none_for_unknown(self):
        """get_action_label should return None for unknown action slug."""
        from app.services.workflow import WorkflowService

        mock_workflow = MagicMock()
        mock_workflow.transitions = []

        mock_db = AsyncMock()

        with patch.object(WorkflowService, "get_workflow", return_value=mock_workflow):
            label = await WorkflowService.get_action_label(mock_db, "purchase_request", "nonexistent")
            assert label is None


# =============================================================================
# 3. Workflow router uses human-readable labels
# =============================================================================

class TestWorkflowRouterHumanReadable:
    """Test that workflow_router handlers match on human-readable action labels."""

    @pytest.mark.asyncio
    async def test_pr_workflow_matches_human_readable_actions(self):
        """PR workflow handler should match 'Submit for Review', not 'submit_for_review'."""
        from app.modules.purchasing_stores.workflow_router import purchase_request_workflow

        class MockDoc:
            id = "PR-001"
            workflow_state = "draft"

        mock_db = AsyncMock()

        with patch("app.services.document.get_list", return_value=[]):
            result = await purchase_request_workflow(MockDoc(), "Submit for Review", mock_db, None)
            assert result["status"] == "error"
            assert "no lines" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_pr_workflow_submit_for_review_with_lines(self):
        """PR workflow 'Submit for Review' should succeed when lines exist."""
        from app.modules.purchasing_stores.workflow_router import purchase_request_workflow

        class MockDoc:
            id = "PR-001"
            workflow_state = "draft"

        mock_db = AsyncMock()
        mock_lines = [{"id": "PRL-001", "workflow_state": "draft"}]

        with patch("app.services.document.get_list", return_value=mock_lines):
            result = await purchase_request_workflow(MockDoc(), "Submit for Review", mock_db, None)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_po_workflow_cancel_validation(self):
        """PO Cancel should fail if lines have progressed beyond approved."""
        from app.modules.purchasing_stores.workflow_router import purchase_order_workflow

        class MockDoc:
            id = "PO-001"
            workflow_state = "open"

        mock_db = AsyncMock()
        mock_lines = [
            {"id": "POL-001", "workflow_state": "approved"},
            {"id": "POL-002", "workflow_state": "partially_received"},
        ]

        with patch("app.services.document.get_list", return_value=mock_lines):
            result = await purchase_order_workflow(MockDoc(), "Cancel", mock_db, None)
            assert result["status"] == "error"
            assert "progressed beyond" in result["message"]

    @pytest.mark.asyncio
    async def test_old_slug_action_does_not_match(self):
        """Old slug-style actions like 'submit_for_review' should NOT match any branch."""
        from app.modules.purchasing_stores.workflow_router import purchase_request_workflow

        class MockDoc:
            id = "PR-001"
            workflow_state = "draft"

        mock_db = AsyncMock()
        mock_lines = [{"id": "PRL-001", "workflow_state": "draft"}]

        with patch("app.services.document.get_list", return_value=mock_lines):
            result = await purchase_request_workflow(MockDoc(), "submit_for_review", mock_db, None)
            # Falls through to the generic "allowed" return
            assert result["status"] == "success"
            assert "submit_for_review" in result["message"]
            assert "allowed" in result["message"]


# =============================================================================
# 4. Rollback on error
# =============================================================================

class TestRollbackOnError:
    """Test that workflow handlers rollback on exceptions."""

    @pytest.mark.asyncio
    async def test_pr_workflow_rollback_on_exception(self):
        """PR workflow should rollback and return error on unexpected exception."""
        from app.modules.purchasing_stores.workflow_router import purchase_request_workflow

        class MockDoc:
            id = "PR-001"
            workflow_state = "pending_approval"

        mock_db = AsyncMock()

        with patch("app.services.document.get_list", side_effect=RuntimeError("DB error")):
            result = await purchase_request_workflow(MockDoc(), "Approve", mock_db, None)
            assert result["status"] == "error"
            assert "error" in result["message"].lower()
            mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_po_workflow_rollback_on_line_apply_failure(self):
        """PO Approve should rollback if a line workflow transition fails."""
        import app.modules.purchasing_stores.workflow_router as wr
        from app.modules.purchasing_stores.workflow_router import purchase_order_workflow

        class MockDoc:
            id = "PO-001"
            workflow_state = "draft"

        mock_db = AsyncMock()
        mock_lines = [{"id": "POL-001", "workflow_state": "draft"}]

        original_apply = wr._apply_line_workflow

        with patch("app.services.document.get_list", return_value=mock_lines), \
             patch.object(wr, "_apply_line_workflow",
                          new=AsyncMock(return_value={"status": "error", "message": "Invalid transition"})):
            result = await purchase_order_workflow(MockDoc(), "Approve", mock_db, None)
            assert result["status"] == "error"
            mock_db.rollback.assert_called()


# =============================================================================
# 5. Redirect pattern
# =============================================================================

class TestRedirectPattern:
    """Test that record-creating actions return the redirect pattern."""

    @pytest.mark.asyncio
    async def test_generate_rfq_returns_redirect(self):
        """generate_rfq should return action=generate_id with path."""
        from app.modules.purchasing_stores.apis.purchase_request import generate_rfq

        class MockDoc:
            id = "PR-001"
            workflow_state = "approved"
            requestor = "EMP-001"
            due_date = "2026-03-01"

        class MockRfq:
            id = "RFQ-NEW-001"

        mock_db = AsyncMock()

        with patch("app.modules.purchasing_stores.apis.purchase_request.new_doc",
                   new=AsyncMock(return_value=MockRfq())), \
             patch("app.modules.purchasing_stores.apis.purchase_request.save_doc",
                   new=AsyncMock(return_value=MockRfq())):
            result = await generate_rfq(MockDoc(), mock_db, None)
            assert result["status"] == "success"
            assert result["action"] == "generate_id"
            assert "/request_for_quotation/RFQ-NEW-001" in result["path"]

    @pytest.mark.asyncio
    async def test_create_po_from_pr_returns_redirect(self):
        """create_po_from_pr should return redirect for single PO."""
        from app.modules.purchasing_stores.apis.purchase_order import create_po_from_pr

        class MockDoc:
            id = "PR-001"
            workflow_state = "approved"

        class MockPO:
            id = "PO-NEW-001"

        class MockPOLine:
            id = "POL-NEW-001"

        mock_db = AsyncMock()
        mock_lines = [
            {"id": "PRL-001", "workflow_state": "approved", "vendor": "V-001",
             "qty_required": 10, "unit_cost": 5.0, "site": "S1", "department": "D1",
             "cost_code": "CC1", "financial_asset_number": None, "item": "ITM-001",
             "item_description": "Test Item"}
        ]

        with patch("app.modules.purchasing_stores.apis.purchase_order.get_list",
                   new=AsyncMock(return_value=mock_lines)), \
             patch("app.modules.purchasing_stores.apis.purchase_order.new_doc",
                   new=AsyncMock(side_effect=[MockPO(), MockPOLine()])), \
             patch("app.modules.purchasing_stores.apis.purchase_order.save_doc",
                   new=AsyncMock(return_value=None)):
            result = await create_po_from_pr(MockDoc(), mock_db, None)
            assert result["status"] == "success"
            assert result["action"] == "generate_id"
            assert "/purchase_order/PO-NEW-001" in result["path"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
