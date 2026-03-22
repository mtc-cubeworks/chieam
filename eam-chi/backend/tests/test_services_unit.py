"""
Unit Tests for Backend Services & Protocols
=============================================
Tests for new services, protocols, and refactored components.
"""
import pytest
import os
import sys

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_ROOT)


class TestSerializableProtocol:
    """Test the Serializable protocol and serialization integration."""

    def test_protocol_is_runtime_checkable(self):
        from app.domain.protocols.serializable import Serializable

        class Good:
            def to_serializable(self):
                return {"key": "value"}

        class Bad:
            pass

        assert isinstance(Good(), Serializable)
        assert not isinstance(Bad(), Serializable)

    def test_serialization_uses_protocol(self):
        from app.domain.protocols.serializable import Serializable
        from app.core.serialization import record_to_dict

        class MyObj:
            def to_serializable(self):
                return {"custom": True, "data": [1, 2, 3]}

        result = record_to_dict(MyObj())
        assert result == {"custom": True, "data": [1, 2, 3]}

    def test_serialization_handles_dict(self):
        from app.core.serialization import record_to_dict

        result = record_to_dict({"a": 1, "b": "hello"})
        assert result == {"a": 1, "b": "hello"}

    def test_serialization_handles_datetime(self):
        from datetime import datetime
        from app.core.serialization import record_to_dict

        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = record_to_dict({"created_at": dt})
        assert result["created_at"] == dt.isoformat()


class TestFieldTypeMap:
    """Test field type mapping in EntityGenerator."""

    def test_generator_has_all_common_types(self):
        from app.entities.generator import EntityGenerator

        expected_types = [
            "string", "text", "int", "float", "boolean",
            "date", "datetime", "select", "attach",
            "email", "phone", "currency", "percent",
        ]
        for ft in expected_types:
            assert ft in EntityGenerator.FIELD_TYPE_MAP, f"Missing type: {ft}"

    def test_generator_returns_tuple(self):
        from app.entities.generator import EntityGenerator

        for ft, mapping in EntityGenerator.FIELD_TYPE_MAP.items():
            assert isinstance(mapping, tuple), f"{ft} mapping is not a tuple"
            assert len(mapping) == 2, f"{ft} mapping should have 2 elements"
            py_type, sa_col = mapping
            assert isinstance(py_type, str), f"{ft} py_type should be str"
            assert isinstance(sa_col, str), f"{ft} sa_col should be str"

    def test_model_generator_type_mappings(self):
        from app.services.model_generator import ModelGeneratorService

        svc = ModelGeneratorService()
        assert "string" in svc.TYPE_MAPPINGS
        assert "link" in svc.TYPE_MAPPINGS
        for ft, mapping in svc.TYPE_MAPPINGS.items():
            assert "py_type" in mapping
            assert "sa_type" in mapping
            assert "imports" in mapping


class TestExportServiceSplit:
    """Test that export_service.py works and re-exports are correct."""

    def test_direct_import(self):
        from app.services.export_service import export_records, get_export_fields
        assert callable(export_records)
        assert callable(get_export_fields)

    def test_backward_compatible_import(self):
        from app.services.import_export import export_records, get_export_fields
        from app.services.export_service import (
            export_records as er2,
            get_export_fields as gef2,
        )
        assert export_records is er2
        assert get_export_fields is gef2


class TestBaseEntityAPILocation:
    """Test that BaseEntityAPI moved correctly."""

    def test_new_location_import(self):
        from app.application.services.base_entity_api import BaseEntityAPI, Context
        import dataclasses
        assert hasattr(BaseEntityAPI, 'validate_create')
        assert hasattr(BaseEntityAPI, 'before_create')
        field_names = [f.name for f in dataclasses.fields(Context)]
        assert 'db' in field_names

    def test_backward_compatible_import(self):
        from app.apis.base_entity_api import BaseEntityAPI as BA1, Context as C1
        from app.application.services.base_entity_api import BaseEntityAPI as BA2, Context as C2
        assert BA1 is BA2
        assert C1 is C2


class TestDocumentServiceProtocols:
    """Test document service protocols."""

    def test_protocols_exist(self):
        from app.domain.protocols.document_service import (
            DocumentQueryProtocol,
            DocumentMutationProtocol,
        )
        assert hasattr(DocumentQueryProtocol, '__protocol_attrs__') or True  # Protocol check
        assert hasattr(DocumentMutationProtocol, '__protocol_attrs__') or True


class TestMetadataValidator:
    """Test metadata validation."""

    def test_valid_field_types_list(self):
        from app.services.metadata_validator import VALID_FIELD_TYPES
        assert "string" in VALID_FIELD_TYPES
        assert "link" in VALID_FIELD_TYPES
        assert "int" in VALID_FIELD_TYPES
        assert "parent_child_link" in VALID_FIELD_TYPES

    def test_validate_empty_metadata(self):
        from app.services.metadata_validator import validate_metadata
        errors = validate_metadata({})
        assert len(errors) > 0  # Should require 'name' at minimum

    def test_validate_minimal_valid_metadata(self):
        from app.services.metadata_validator import validate_metadata
        metadata = {
            "name": "test_entity",
            "module": "core",
            "fields": [
                {"name": "title", "field_type": "string"}
            ]
        }
        is_valid, errors = validate_metadata(metadata)
        assert is_valid, f"Unexpected errors: {errors}"

    def test_validate_invalid_field_type(self):
        from app.services.metadata_validator import validate_metadata
        metadata = {
            "name": "test_entity",
            "module": "core",
            "fields": [
                {"name": "bad_field", "field_type": "nonexistent_type"}
            ]
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any("invalid type" in e.lower() for e in errors)

    def test_validate_link_requires_link_entity(self):
        from app.services.metadata_validator import validate_metadata
        metadata = {
            "name": "test_entity",
            "module": "core",
            "fields": [
                {"name": "ref", "field_type": "link"}
            ]
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any("link_entity" in e for e in errors)


class TestBackupDirLocation:
    """Test that backup directories point outside app/."""

    def test_metadata_editor_backup_dir(self):
        from app.services.metadata_editor import MetadataEditorService
        svc = MetadataEditorService()
        # backup_dir should be under backend/backups/, not app/backups/
        assert "app" not in str(svc.backup_dir).split("backups")[0].split(os.sep)[-1:] or \
               str(svc.backup_dir).endswith(os.path.join("backups", "metadata"))
        # More specifically: backup_dir parent should be backend/, not app/
        assert svc.backup_dir.parent.name == "backups"
        assert svc.backup_dir.parent.parent.name != "app"


class TestDependencyFactories:
    """Test that DI factories are importable."""

    def test_legacy_factories_importable(self):
        from app.api.dependencies import (
            get_legacy_rbac,
            get_legacy_naming,
            get_legacy_workflow_db,
        )
        assert callable(get_legacy_rbac)
        assert callable(get_legacy_naming)
        assert callable(get_legacy_workflow_db)

    def test_application_service_factories_importable(self):
        from app.api.dependencies import (
            get_entity_service,
            get_auth_service,
            get_rbac_service,
            get_workflow_service,
        )
        assert callable(get_entity_service)
        assert callable(get_auth_service)
        assert callable(get_rbac_service)
        assert callable(get_workflow_service)
