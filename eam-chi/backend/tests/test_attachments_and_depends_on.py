"""
Comprehensive tests for:
1. Attachment service (model, metadata, CRUD endpoints)
2. depends_on metadata (display_depends_on, mandatory_depends_on)
3. Extended entity metadata (attachment_config)
4. Metadata editor validation for new fields
"""
import json
import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import asdict

# Ensure backend app is importable
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_ROOT)


# ============================================================
# 1. Registry dataclass tests
# ============================================================

class TestFieldMetaDependsOn:
    """Test FieldMeta dataclass with display_depends_on and mandatory_depends_on."""

    def test_field_meta_defaults(self):
        from app.meta.registry import FieldMeta
        f = FieldMeta(name="test", label="Test", field_type="string")
        assert f.display_depends_on is None
        assert f.mandatory_depends_on is None

    def test_field_meta_with_display_depends_on(self):
        from app.meta.registry import FieldMeta
        f = FieldMeta(
            name="reject_reason",
            label="Reject Reason",
            field_type="text",
            display_depends_on="eval:doc.workflow_state=='rejected'",
        )
        assert f.display_depends_on == "eval:doc.workflow_state=='rejected'"
        assert f.mandatory_depends_on is None

    def test_field_meta_with_mandatory_depends_on(self):
        from app.meta.registry import FieldMeta
        f = FieldMeta(
            name="approval_notes",
            label="Approval Notes",
            field_type="text",
            mandatory_depends_on="eval:doc.status=='approved'",
        )
        assert f.mandatory_depends_on == "eval:doc.status=='approved'"

    def test_field_meta_with_both_depends_on(self):
        from app.meta.registry import FieldMeta
        f = FieldMeta(
            name="notes",
            label="Notes",
            field_type="text",
            display_depends_on="eval:doc.show_notes",
            mandatory_depends_on="eval:doc.require_notes",
        )
        assert f.display_depends_on == "eval:doc.show_notes"
        assert f.mandatory_depends_on == "eval:doc.require_notes"


class TestAttachmentConfig:
    """Test AttachmentConfig dataclass."""

    def test_attachment_config_defaults(self):
        from app.meta.registry import AttachmentConfig
        config = AttachmentConfig()
        assert config.allow_attachments is False
        assert config.max_attachments == 10
        assert config.allowed_extensions is None
        assert config.max_file_size_mb == 10

    def test_attachment_config_custom(self):
        from app.meta.registry import AttachmentConfig
        config = AttachmentConfig(
            allow_attachments=True,
            max_attachments=5,
            allowed_extensions=["pdf", "jpg", "png"],
            max_file_size_mb=20,
        )
        assert config.allow_attachments is True
        assert config.max_attachments == 5
        assert config.allowed_extensions == ["pdf", "jpg", "png"]
        assert config.max_file_size_mb == 20


class TestEntityMetaAttachmentConfig:
    """Test EntityMeta with attachment_config."""

    def test_entity_meta_no_attachment_config(self):
        from app.meta.registry import EntityMeta
        meta = EntityMeta(
            name="test", label="Test", module="core", table_name="test"
        )
        assert meta.attachment_config is None

    def test_entity_meta_with_attachment_config(self):
        from app.meta.registry import EntityMeta, AttachmentConfig
        config = AttachmentConfig(allow_attachments=True, max_attachments=3)
        meta = EntityMeta(
            name="test", label="Test", module="core", table_name="test",
            attachment_config=config,
        )
        assert meta.attachment_config is not None
        assert meta.attachment_config.allow_attachments is True
        assert meta.attachment_config.max_attachments == 3


# ============================================================
# 2. MetaRegistry serialization tests
# ============================================================

class TestMetaRegistrySerialization:
    """Test MetaRegistry.to_dict() includes new fields."""

    def test_to_dict_includes_depends_on_fields(self):
        from app.meta.registry import MetaRegistry, EntityMeta, FieldMeta
        meta = EntityMeta(
            name="test_entity",
            label="Test Entity",
            module="core",
            table_name="test_entity",
            fields=[
                FieldMeta(
                    name="reason",
                    label="Reason",
                    field_type="text",
                    display_depends_on="eval:doc.status=='rejected'",
                    mandatory_depends_on="eval:doc.status=='approved'",
                ),
            ],
        )
        d = MetaRegistry.to_dict(meta)
        # Find the 'reason' field in the serialized dict (skip system fields)
        reason_field = next(
            (f for f in d["fields"] if f["name"] == "reason"), None
        )
        assert reason_field is not None
        assert reason_field["display_depends_on"] == "eval:doc.status=='rejected'"
        assert reason_field["mandatory_depends_on"] == "eval:doc.status=='approved'"

    def test_to_dict_depends_on_null_by_default(self):
        from app.meta.registry import MetaRegistry, EntityMeta, FieldMeta
        meta = EntityMeta(
            name="test_entity2",
            label="Test Entity 2",
            module="core",
            table_name="test_entity2",
            fields=[
                FieldMeta(name="name", label="Name", field_type="string"),
            ],
        )
        d = MetaRegistry.to_dict(meta)
        name_field = next(
            (f for f in d["fields"] if f["name"] == "name"), None
        )
        assert name_field is not None
        assert name_field["display_depends_on"] is None
        assert name_field["mandatory_depends_on"] is None

    def test_to_dict_includes_attachment_config(self):
        from app.meta.registry import MetaRegistry, EntityMeta, AttachmentConfig
        config = AttachmentConfig(
            allow_attachments=True,
            max_attachments=5,
            allowed_extensions=["pdf", "jpg"],
            max_file_size_mb=15,
        )
        meta = EntityMeta(
            name="test_entity3",
            label="Test Entity 3",
            module="core",
            table_name="test_entity3",
            attachment_config=config,
        )
        d = MetaRegistry.to_dict(meta)
        assert d["attachment_config"] is not None
        assert d["attachment_config"]["allow_attachments"] is True
        assert d["attachment_config"]["max_attachments"] == 5
        assert d["attachment_config"]["allowed_extensions"] == ["pdf", "jpg"]
        assert d["attachment_config"]["max_file_size_mb"] == 15

    def test_to_dict_attachment_config_null_when_not_set(self):
        from app.meta.registry import MetaRegistry, EntityMeta
        meta = EntityMeta(
            name="test_entity4",
            label="Test Entity 4",
            module="core",
            table_name="test_entity4",
        )
        d = MetaRegistry.to_dict(meta)
        assert d["attachment_config"] is None


# ============================================================
# 3. Entity JSON loader tests
# ============================================================

class TestEntityJsonLoader:
    """Test load_entity_from_json with new fields."""

    def _create_temp_json(self, data: dict) -> Path:
        """Create a temporary JSON file for testing."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(data, tmp)
        tmp.close()
        return Path(tmp.name)

    def test_load_depends_on_fields(self):
        from app.entities import load_entity_from_json
        json_data = {
            "name": "test_loader",
            "label": "Test Loader",
            "module": "core",
            "table_name": "test_loader",
            "fields": [
                {
                    "name": "reason",
                    "label": "Reason",
                    "field_type": "text",
                    "display_depends_on": "eval:doc.workflow_state=='rejected'",
                    "mandatory_depends_on": "eval:doc.status=='approved'",
                },
                {
                    "name": "name",
                    "label": "Name",
                    "field_type": "string",
                },
            ],
        }
        path = self._create_temp_json(json_data)
        try:
            meta = load_entity_from_json(path)
            assert meta is not None
            reason = next(f for f in meta.fields if f.name == "reason")
            assert reason.display_depends_on == "eval:doc.workflow_state=='rejected'"
            assert reason.mandatory_depends_on == "eval:doc.status=='approved'"

            name = next(f for f in meta.fields if f.name == "name")
            assert name.display_depends_on is None
            assert name.mandatory_depends_on is None
        finally:
            os.unlink(path)

    def test_load_attachment_config(self):
        from app.entities import load_entity_from_json
        json_data = {
            "name": "test_attach",
            "label": "Test Attach",
            "module": "core",
            "table_name": "test_attach",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "max_attachments": 5,
                "allowed_extensions": ["pdf", "jpg"],
                "max_file_size_mb": 20,
            },
        }
        path = self._create_temp_json(json_data)
        try:
            meta = load_entity_from_json(path)
            assert meta is not None
            assert meta.attachment_config is not None
            assert meta.attachment_config.allow_attachments is True
            assert meta.attachment_config.max_attachments == 5
            assert meta.attachment_config.allowed_extensions == ["pdf", "jpg"]
            assert meta.attachment_config.max_file_size_mb == 20
        finally:
            os.unlink(path)

    def test_load_no_attachment_config(self):
        from app.entities import load_entity_from_json
        json_data = {
            "name": "test_no_attach",
            "label": "Test No Attach",
            "module": "core",
            "table_name": "test_no_attach",
            "fields": [],
        }
        path = self._create_temp_json(json_data)
        try:
            meta = load_entity_from_json(path)
            assert meta is not None
            assert meta.attachment_config is None
        finally:
            os.unlink(path)

    def test_load_attachment_config_defaults(self):
        from app.entities import load_entity_from_json
        json_data = {
            "name": "test_attach_defaults",
            "label": "Test Attach Defaults",
            "module": "core",
            "table_name": "test_attach_defaults",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
            },
        }
        path = self._create_temp_json(json_data)
        try:
            meta = load_entity_from_json(path)
            assert meta is not None
            assert meta.attachment_config is not None
            assert meta.attachment_config.allow_attachments is True
            assert meta.attachment_config.max_attachments == 10  # default
            assert meta.attachment_config.allowed_extensions is None  # default
            assert meta.attachment_config.max_file_size_mb == 10  # default
        finally:
            os.unlink(path)


# ============================================================
# 4. Metadata editor validation tests
# ============================================================

class TestMetadataEditorValidation:
    """Test MetadataEditorService.validate_metadata with new fields."""

    def _get_service(self):
        from app.services.metadata_editor import MetadataEditorService
        return MetadataEditorService()

    def test_valid_attachment_config(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "max_attachments": 5,
                "max_file_size_mb": 10,
                "allowed_extensions": ["pdf", "jpg"],
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert is_valid, f"Expected valid, got errors: {errors}"

    def test_invalid_attachment_config_not_object(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": "invalid",
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("attachment_config must be an object" in e for e in errors)

    def test_invalid_max_attachments_zero(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "max_attachments": 0,
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("max_attachments must be a positive integer" in e for e in errors)

    def test_invalid_max_attachments_negative(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "max_attachments": -1,
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("max_attachments must be a positive integer" in e for e in errors)

    def test_invalid_max_file_size_zero(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "max_file_size_mb": 0,
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("max_file_size_mb must be a positive number" in e for e in errors)

    def test_invalid_allowed_extensions_not_list(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "allowed_extensions": "pdf",
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("allowed_extensions must be a list of strings" in e for e in errors)

    def test_invalid_allowed_extensions_not_strings(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [],
            "attachment_config": {
                "allow_attachments": True,
                "allowed_extensions": [1, 2],
            },
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("allowed_extensions must be a list of strings" in e for e in errors)

    def test_valid_depends_on_fields(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [
                {
                    "name": "reason",
                    "label": "Reason",
                    "field_type": "text",
                    "display_depends_on": "eval:doc.workflow_state=='rejected'",
                    "mandatory_depends_on": "eval:doc.status=='approved'",
                },
            ],
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert is_valid, f"Expected valid, got errors: {errors}"

    def test_invalid_display_depends_on_not_string(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [
                {
                    "name": "reason",
                    "label": "Reason",
                    "field_type": "text",
                    "display_depends_on": {"field": "value"},
                },
            ],
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("display_depends_on must be a string" in e for e in errors)

    def test_invalid_mandatory_depends_on_not_string(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [
                {
                    "name": "reason",
                    "label": "Reason",
                    "field_type": "text",
                    "mandatory_depends_on": 123,
                },
            ],
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert not is_valid
        assert any("mandatory_depends_on must be a string" in e for e in errors)

    def test_no_attachment_config_is_valid(self):
        svc = self._get_service()
        metadata = {
            "name": "test",
            "module": "core",
            "fields": [
                {"name": "name", "label": "Name", "field_type": "string"},
            ],
        }
        is_valid, errors = svc.validate_metadata(metadata)
        assert is_valid, f"Expected valid, got errors: {errors}"


# ============================================================
# 5. Attachment model tests
# ============================================================

class TestAttachmentModel:
    """Test Attachment SQLAlchemy model."""

    def test_attachment_model_exists(self):
        from app.models.attachment import Attachment
        assert Attachment.__tablename__ == "attachment"

    def test_attachment_model_columns(self):
        from app.models.attachment import Attachment
        columns = {c.name for c in Attachment.__table__.columns}
        expected = {
            "id", "entity_name", "record_id", "file_name",
            "original_name", "file_path", "file_size", "mime_type",
            "uploaded_by", "description", "created_at",
        }
        assert expected.issubset(columns), f"Missing columns: {expected - columns}"

    def test_attachment_in_models_init(self):
        from app.models import Attachment
        assert Attachment is not None


# ============================================================
# 6. End-to-end round-trip: JSON → load → to_dict
# ============================================================

class TestRoundTrip:
    """Test that new metadata fields survive a full round-trip."""

    def test_depends_on_round_trip(self):
        import tempfile, json, os
        from app.entities import load_entity_from_json
        from app.meta.registry import MetaRegistry

        data = {
            "name": "rt_test",
            "label": "Round Trip Test",
            "module": "core",
            "table_name": "rt_test",
            "fields": [
                {
                    "name": "notes",
                    "label": "Notes",
                    "field_type": "text",
                    "display_depends_on": "eval:doc.is_active",
                    "mandatory_depends_on": "eval:doc.status=='final'",
                },
            ],
            "attachment_config": {
                "allow_attachments": True,
                "max_attachments": 3,
                "allowed_extensions": ["pdf"],
                "max_file_size_mb": 5,
            },
        }

        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(data, tmp)
        tmp.close()

        try:
            meta = load_entity_from_json(Path(tmp.name))
            assert meta is not None

            # Serialize back
            d = MetaRegistry.to_dict(meta)

            # Check depends_on survived
            notes = next(f for f in d["fields"] if f["name"] == "notes")
            assert notes["display_depends_on"] == "eval:doc.is_active"
            assert notes["mandatory_depends_on"] == "eval:doc.status=='final'"

            # Check attachment_config survived
            ac = d["attachment_config"]
            assert ac is not None
            assert ac["allow_attachments"] is True
            assert ac["max_attachments"] == 3
            assert ac["allowed_extensions"] == ["pdf"]
            assert ac["max_file_size_mb"] == 5
        finally:
            os.unlink(tmp.name)


# ============================================================
# 7. Attachment route helper tests
# ============================================================

class TestAttachmentRouteHelpers:
    """Test attachment route helper functions."""

    def test_get_attachment_config_returns_none_for_unknown_entity(self):
        from app.api.routes.entity_attachments import _get_attachment_config
        result = _get_attachment_config("nonexistent_entity_xyz")
        assert result is None

    def test_get_attachment_config_returns_none_when_not_enabled(self):
        from app.api.routes.entity_attachments import _get_attachment_config
        from app.meta.registry import MetaRegistry, EntityMeta, AttachmentConfig

        # Register a test entity with attachments disabled
        meta = EntityMeta(
            name="_test_no_attach",
            label="Test No Attach",
            module="core",
            table_name="_test_no_attach",
            attachment_config=AttachmentConfig(allow_attachments=False),
        )
        MetaRegistry.register(meta)
        try:
            result = _get_attachment_config("_test_no_attach")
            assert result is None
        finally:
            MetaRegistry._entities.pop("_test_no_attach", None)

    def test_get_attachment_config_returns_config_when_enabled(self):
        from app.api.routes.entity_attachments import _get_attachment_config
        from app.meta.registry import MetaRegistry, EntityMeta, AttachmentConfig

        config = AttachmentConfig(
            allow_attachments=True, max_attachments=5,
            allowed_extensions=["pdf"], max_file_size_mb=20,
        )
        meta = EntityMeta(
            name="_test_with_attach",
            label="Test With Attach",
            module="core",
            table_name="_test_with_attach",
            attachment_config=config,
        )
        MetaRegistry.register(meta)
        try:
            result = _get_attachment_config("_test_with_attach")
            assert result is not None
            assert result.allow_attachments is True
            assert result.max_attachments == 5
        finally:
            MetaRegistry._entities.pop("_test_with_attach", None)


# ============================================================
# 8. Existing entity JSON files still load correctly
# ============================================================

class TestExistingEntitiesStillLoad:
    """Ensure existing entity JSON files load without errors after changes."""

    def test_asset_json_loads(self):
        from app.entities import load_entity_from_json
        path = Path(__file__).parent.parent / "app" / "modules" / "asset_management" / "entities" / "asset.json"
        if not path.exists():
            pytest.skip("asset.json not found")
        meta = load_entity_from_json(path)
        assert meta is not None
        assert meta.name == "asset"
        # Should have no attachment_config since it's not in the JSON
        assert meta.attachment_config is None
        # Fields should not have depends_on set
        for f in meta.fields:
            assert f.display_depends_on is None
            assert f.mandatory_depends_on is None

    def test_all_entity_jsons_load(self):
        """Smoke test: all entity JSONs should still load without error."""
        from app.entities import load_entity_from_json
        modules_dir = Path(__file__).parent.parent / "app" / "modules"
        if not modules_dir.exists():
            pytest.skip("modules dir not found")

        errors = []
        count = 0
        for module_dir in modules_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            entities_dir = module_dir / "entities"
            if not entities_dir.exists():
                continue
            for item in entities_dir.iterdir():
                json_file = None
                if item.is_file() and item.suffix == ".json":
                    json_file = item
                elif item.is_dir():
                    nested = item / f"{item.name}.json"
                    if nested.exists():
                        json_file = nested
                if json_file:
                    try:
                        meta = load_entity_from_json(json_file)
                        if meta is None:
                            errors.append(f"{json_file}: returned None")
                        count += 1
                    except Exception as e:
                        errors.append(f"{json_file}: {e}")

        assert count > 0, "No entity JSONs found"
        assert not errors, f"Failed to load entities:\n" + "\n".join(errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
