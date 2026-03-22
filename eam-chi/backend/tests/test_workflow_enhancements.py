"""
Workflow Enhancements & Prefill Test Suite

Covers:
  1. WOA Start Activity: Asset → 'under_maintenance' when activity_type is 'Maintain Asset'
  2. WOA Complete (Maintain Asset): Asset → 'active', need_repair cleared
  3. Purchase Request Line: qty_received + po_num hidden, total_line_amount readonly/calculated
  4. Prefill endpoint: resolves "today"/"now" tokens from entity JSON prefill rules
  5. Model Editor: save_json_only + sync_pending methods
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


# ═════════════════════════════════════════════════════════════════════════════
# 1. WOA Start Activity — Asset → under_maintenance
# ═════════════════════════════════════════════════════════════════════════════

class TestWOAStartActivityAssetStatus:
    """When WOA Start Activity fires for 'Maintain Asset', the linked Asset
    workflow_state should change to 'under_maintenance'."""

    @pytest.mark.asyncio
    async def test_start_activity_sets_asset_under_maintenance(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_start_activity

        doc = MockDoc(
            id="WOA-001",
            work_item_type="Asset",
            activity_type="RAT-001",
            work_order="WO-001",
            work_item="ASSET-001",
        )
        asset_doc = MockDoc(id="ASSET-001", workflow_state="active")

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value") as mock_get_value, \
             patch("app.modules.work_mgmt.apis.work_order_activity.get_doc") as mock_get_doc, \
             patch("app.modules.work_mgmt.apis.work_order_activity.save_doc") as mock_save_doc:

            # request_activity_type lookup returns 'Maintain Asset'
            mock_get_value.return_value = {"id": "RAT-001", "menu": "Maintain Asset"}
            mock_get_doc.return_value = asset_doc
            mock_save_doc.return_value = None

            work_order = MockDoc(id="WO-001")
            result = await _handle_start_activity(doc, work_order, AsyncMock())

            assert result["status"] == "success"
            assert asset_doc.workflow_state == "under_maintenance"
            mock_save_doc.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_activity_non_maintain_asset_no_change(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_start_activity

        doc = MockDoc(
            id="WOA-002",
            work_item_type="Asset",
            activity_type="RAT-002",
            work_order="WO-002",
            work_item="ASSET-002",
        )

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value") as mock_get_value, \
             patch("app.modules.work_mgmt.apis.work_order_activity.get_doc") as mock_get_doc, \
             patch("app.modules.work_mgmt.apis.work_order_activity.save_doc") as mock_save_doc:

            # Not 'Maintain Asset'
            mock_get_value.return_value = {"id": "RAT-002", "menu": "Install Asset"}
            mock_get_doc.return_value = None
            mock_save_doc.return_value = None

            work_order = MockDoc(id="WO-002")
            result = await _handle_start_activity(doc, work_order, AsyncMock())

            assert result["status"] == "success"
            # save_doc should NOT have been called
            mock_save_doc.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_activity_no_work_order_returns_error(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_start_activity

        doc = MockDoc(id="WOA-003", work_item_type="Asset", activity_type="RAT-001", work_order=None)
        result = await _handle_start_activity(doc, None, AsyncMock())
        assert result["status"] == "error"
        assert "no Work Order linked" in result["message"]


# ═════════════════════════════════════════════════════════════════════════════
# 2. WOA Complete (Maintain Asset) — Asset → active
# ═════════════════════════════════════════════════════════════════════════════

class TestWOACompleteAssetStatus:
    """When WOA Complete fires for 'Maintain Asset', the linked Asset
    workflow_state should change back to 'active' and need_repair cleared."""

    @pytest.mark.asyncio
    async def test_complete_maintain_asset_sets_active(self):
        from app.modules.work_mgmt.apis.work_order_activity import _handle_complete

        doc = MockDoc(
            id="WOA-010",
            activity_type="RAT-001",
            work_item="ASSET-010",
            position=None,
        )
        asset_doc = MockDoc(
            id="ASSET-010",
            workflow_state="under_maintenance",
            need_repair=True,
        )
        db = AsyncMock()
        db.commit = AsyncMock()

        with patch("app.modules.work_mgmt.apis.work_order_activity.get_value") as mock_get_value, \
             patch("app.modules.work_mgmt.apis.work_order_activity.get_doc") as mock_get_doc, \
             patch("app.modules.work_mgmt.apis.work_order_activity.save_doc") as mock_save_doc:

            mock_get_value.return_value = {"id": "RAT-001", "menu": "Maintain Asset"}
            mock_get_doc.return_value = asset_doc
            mock_save_doc.return_value = None

            maint_req = None  # no linked MR for this test
            user = MagicMock()
            result = await _handle_complete(doc, maint_req, db, user)

            assert result["status"] == "success"
            assert asset_doc.workflow_state == "active"
            assert asset_doc.need_repair is False
            assert "Active" in result["message"]


# ═════════════════════════════════════════════════════════════════════════════
# 3. Purchase Request Line — field visibility & line total calculation
# ═════════════════════════════════════════════════════════════════════════════

class TestPurchaseRequestLineJSON:
    """purchase_request_line.json field visibility rules."""

    @classmethod
    def setup_class(cls):
        cls.data = load_entity_json("purchasing_stores", "purchase_request_line")
        cls.fields = {f["name"]: f for f in cls.data["fields"]}

    def test_qty_received_is_hidden(self):
        f = self.fields.get("qty_received", {})
        assert f.get("hidden") is True, "qty_received should be hidden"

    def test_po_num_is_hidden(self):
        f = self.fields.get("po_num", {})
        assert f.get("hidden") is True, "po_num should be hidden"

    def test_total_line_amount_is_readonly(self):
        f = self.fields.get("total_line_amount", {})
        assert f.get("readonly") is True, "total_line_amount should be readonly (calculated)"

    def test_total_line_amount_label(self):
        f = self.fields.get("total_line_amount", {})
        assert f.get("label") == "Line Total"

    def test_visible_fields_present(self):
        """Key fields should exist and not be hidden."""
        expected_visible = ["item", "item_description", "unit_of_measure", "unit_cost", "qty_required", "total_line_amount"]
        for name in expected_visible:
            f = self.fields.get(name)
            assert f is not None, f"Field '{name}' should exist"
            assert not f.get("hidden", False), f"Field '{name}' should not be hidden"


class TestPurchaseRequestLineCalcHook:
    """After-save hook calculates total_line_amount = unit_cost * qty_required."""

    @pytest.mark.asyncio
    async def test_line_total_calculated(self):
        from app.modules.purchasing_stores.hooks import purchase_request_line_after_save

        doc = MockDoc(
            id="PRL-001",
            unit_cost=25.50,
            qty_required=4,
            total_line_amount=0,
        )
        ctx = MagicMock()
        ctx.db = AsyncMock()

        with patch("app.services.document.save_doc", new_callable=AsyncMock) as mock_save:
            result = await purchase_request_line_after_save(doc, ctx)

        assert result["status"] == "success"
        assert "message" in result
        assert doc.total_line_amount == 102.0
        mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_line_total_no_update_when_same(self):
        from app.modules.purchasing_stores.hooks import purchase_request_line_after_save

        doc = MockDoc(
            id="PRL-002",
            unit_cost=10.0,
            qty_required=5,
            total_line_amount=50.0,  # Already correct
        )
        ctx = MagicMock()
        ctx.db = AsyncMock()

        with patch("app.services.document.save_doc", new_callable=AsyncMock) as mock_save:
            result = await purchase_request_line_after_save(doc, ctx)

        assert result["status"] == "success"
        # Should NOT save since value hasn't changed
        mock_save.assert_not_called()

    @pytest.mark.asyncio
    async def test_line_total_handles_none_values(self):
        """When unit_cost and qty_required are None, calculated=0.0 and
        current=(None or 0)=0 → float(0)==0.0, so no save is triggered."""
        from app.modules.purchasing_stores.hooks import purchase_request_line_after_save

        doc = MockDoc(
            id="PRL-003",
            unit_cost=None,
            qty_required=None,
            total_line_amount=None,
        )
        ctx = MagicMock()
        ctx.db = AsyncMock()

        with patch("app.services.document.save_doc", new_callable=AsyncMock) as mock_save:
            result = await purchase_request_line_after_save(doc, ctx)

        assert result["status"] == "success"
        # No save needed: calculated 0.0 == float(None or 0) == 0.0
        mock_save.assert_not_called()

    @pytest.mark.asyncio
    async def test_line_total_updates_from_zero(self):
        """When total_line_amount is 0 but unit_cost*qty_required > 0, save triggers."""
        from app.modules.purchasing_stores.hooks import purchase_request_line_after_save

        doc = MockDoc(
            id="PRL-004",
            unit_cost=15.0,
            qty_required=3,
            total_line_amount=0,
        )
        ctx = MagicMock()
        ctx.db = AsyncMock()

        with patch("app.services.document.save_doc", new_callable=AsyncMock) as mock_save:
            result = await purchase_request_line_after_save(doc, ctx)

        assert result["status"] == "success"
        assert "message" in result
        assert doc.total_line_amount == 45.0
        mock_save.assert_called_once()


# ═════════════════════════════════════════════════════════════════════════════
# 4. Prefill endpoint
# ═════════════════════════════════════════════════════════════════════════════

class TestPrefillResolver:
    """Tests for the prefill token resolver logic."""

    def test_today_token_resolves(self):
        from app.api.routes.entity_prefill import _PREFILL_RESOLVERS
        result = _PREFILL_RESOLVERS["today"]()
        assert result == str(date.today())

    def test_now_token_resolves(self):
        from app.api.routes.entity_prefill import _PREFILL_RESOLVERS
        result = _PREFILL_RESOLVERS["now"]()
        # Should be a valid ISO datetime string
        parsed = datetime.fromisoformat(result)
        assert parsed.date() == date.today()


class TestPrefillEntityJSON:
    """Entity JSONs with prefill rules."""

    def test_maintenance_request_has_prefill(self):
        data = load_entity_json("maintenance_mgmt", "maintenance_request")
        assert "prefill" in data
        assert data["prefill"].get("requested_date") == "today"

    def test_purchase_request_has_prefill(self):
        data = load_entity_json("purchasing_stores", "purchase_request")
        assert "prefill" in data
        assert data["prefill"].get("date_requested") == "today"


# ═════════════════════════════════════════════════════════════════════════════
# 5. Model Editor: save_json_only & sync_pending
# ═════════════════════════════════════════════════════════════════════════════

class TestMetadataSyncDraftSave:
    """MetadataSyncService.save_json_only should save JSON + reload registry
    but NOT update model or apply migration."""

    def test_save_json_only_skips_model_and_migration(self):
        from app.application.services.metadata_sync_service import MetadataSyncService

        reader = MagicMock()
        writer = MagicMock()
        validator = MagicMock()
        analyzer = MagicMock()
        model_gen = MagicMock()
        migration = MagicMock()
        registry = MagicMock()

        validator.validate.return_value = (True, [])
        writer.create_backup.return_value = "/tmp/backup.json"
        writer.save_metadata.return_value = "/tmp/entity.json"
        reader.get_entity_json_path.return_value = "/tmp/entity.json"
        registry.reload_entity.return_value = True

        svc = MetadataSyncService(
            reader=reader,
            writer=writer,
            validator=validator,
            analyzer=analyzer,
            model_generator=model_gen,
            migration_manager=migration,
            registry_manager=registry,
        )

        result = svc.save_json_only("test_entity", {"name": "test_entity"})

        assert result.success is True
        assert result.json_saved is True
        assert result.registry_reloaded is True
        assert result.model_updated is False
        assert result.migration_generated is False
        assert result.migration_applied is False
        # Model generator and migration manager should NOT have been called
        model_gen.update_model_file.assert_not_called()
        migration.generate_migration.assert_not_called()
        migration.apply_migration.assert_not_called()

    def test_save_json_only_validation_fails(self):
        from app.application.services.metadata_sync_service import MetadataSyncService

        reader = MagicMock()
        writer = MagicMock()
        validator = MagicMock()
        analyzer = MagicMock()
        model_gen = MagicMock()
        migration = MagicMock()
        registry = MagicMock()

        validator.validate.return_value = (False, ["name is required"])

        svc = MetadataSyncService(
            reader=reader,
            writer=writer,
            validator=validator,
            analyzer=analyzer,
            model_generator=model_gen,
            migration_manager=migration,
            registry_manager=registry,
        )

        result = svc.save_json_only("test_entity", {})

        assert result.success is False
        assert "Validation failed" in result.message

    def test_sync_pending_updates_models_and_migrates(self):
        from app.application.services.metadata_sync_service import MetadataSyncService

        reader = MagicMock()
        writer = MagicMock()
        validator = MagicMock()
        analyzer = MagicMock()
        model_gen = MagicMock()
        migration = MagicMock()
        registry = MagicMock()

        reader.list_all_entities.return_value = [
            {"name": "asset"},
            {"name": "site"},
        ]
        reader.get_entity_metadata.side_effect = lambda n: {"name": n}
        model_gen.update_model_file.return_value = {"success": True, "skipped": False}
        migration.check_migration_needed.return_value = {"needs_migration": True}
        migration.generate_migration.return_value = {"success": True, "migration_file": "001_sync.py"}
        migration.apply_migration.return_value = {"success": True}
        registry.reload_all.return_value = 2

        svc = MetadataSyncService(
            reader=reader,
            writer=writer,
            validator=validator,
            analyzer=analyzer,
            model_generator=model_gen,
            migration_manager=migration,
            registry_manager=registry,
        )

        result = svc.sync_pending()

        assert result["success"] is True
        assert "asset" in result["updated_models"]
        assert "site" in result["updated_models"]
        assert result["migration_applied"] is True


# ═════════════════════════════════════════════════════════════════════════════
# 6. EntityMeta.prefill parsed from JSON
# ═════════════════════════════════════════════════════════════════════════════

class TestEntityMetaPrefill:
    """EntityMeta should have a prefill field parsed from JSON."""

    def test_prefill_field_exists_on_entity_meta(self):
        from app.meta.registry import EntityMeta
        import dataclasses
        field_names = [f.name for f in dataclasses.fields(EntityMeta)]
        assert "prefill" in field_names

    def test_load_entity_parses_prefill(self):
        from app.entities import load_entity_from_json
        json_path = ENTITIES_DIR / "maintenance_mgmt" / "entities" / "maintenance_request.json"
        meta = load_entity_from_json(str(json_path))
        assert meta is not None
        assert meta.prefill is not None
        assert meta.prefill.get("requested_date") == "today"
