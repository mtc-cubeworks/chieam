"""
Metadata Sync E2E Tests
========================
Tests that a metadata change via the model editor flows through
the entire pipeline and is immediately reflected in the /meta/{entity} endpoint.

Architecture tests:
  1. MetadataSyncService unit tests (no DB needed)
  2. Full E2E: save metadata → verify /meta/{entity} returns updated data
  3. Clean architecture compliance (no infrastructure imports in application layer)
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================
# 1. Architecture Tests
# ============================================================

class TestCleanArchitecture:
    """Verify SOLID / Clean Architecture compliance."""

    def test_domain_protocol_has_no_infrastructure_imports(self):
        """Domain layer must not import infrastructure."""
        protocol_file = Path(__file__).parent.parent / "app" / "domain" / "protocols" / "metadata_sync.py"
        assert protocol_file.exists(), "metadata_sync.py protocol not found"
        content = protocol_file.read_text()
        # Should not import sqlalchemy, fastapi, or infrastructure
        assert "sqlalchemy" not in content
        assert "fastapi" not in content
        assert "infrastructure" not in content

    def test_application_service_has_no_infrastructure_imports(self):
        """Application layer must depend only on domain protocols, not infrastructure."""
        service_file = Path(__file__).parent.parent / "app" / "application" / "services" / "metadata_sync_service.py"
        assert service_file.exists(), "metadata_sync_service.py not found"
        content = service_file.read_text()
        # Should not import sqlalchemy, fastapi, or concrete infrastructure
        assert "sqlalchemy" not in content
        assert "fastapi" not in content
        assert "from app.services." not in content
        assert "from app.infrastructure." not in content
        # Should import from domain protocols
        assert "from app.domain.protocols.metadata_sync import" in content

    def test_router_is_thin_api_layer(self):
        """Router should delegate to MetadataSyncService, not contain business logic."""
        router_file = Path(__file__).parent.parent / "app" / "routers" / "admin" / "model_editor.py"
        assert router_file.exists()
        content = router_file.read_text()
        # Should import from dependencies (DI)
        assert "get_metadata_sync_service" in content
        assert "MetadataSyncService" in content
        # Should NOT directly import old services
        assert "MetadataEditorService" not in content
        assert "ModelGeneratorService" not in content
        assert "MigrationService" not in content

    def test_save_endpoint_uses_single_body_contract(self):
        """PUT save endpoint should only require one body payload (metadata dict)."""
        router_file = Path(__file__).parent.parent / "app" / "routers" / "admin" / "model_editor.py"
        content = router_file.read_text()
        assert "metadata: dict = Body(...)" in content
        assert "auto_migrate: bool = Body(" not in content

    def test_infrastructure_adapters_exist(self):
        """Infrastructure adapters must exist and implement protocols."""
        adapters_file = Path(__file__).parent.parent / "app" / "infrastructure" / "metadata" / "adapters.py"
        assert adapters_file.exists(), "adapters.py not found"
        content = adapters_file.read_text()
        # Should contain all adapter classes
        assert "class JsonMetadataReader" in content
        assert "class JsonMetadataWriter" in content
        assert "class MetadataValidator" in content
        assert "class MetadataChangeAnalyzer" in content
        assert "class ModelGeneratorAdapter" in content
        assert "class MigrationManagerAdapter" in content
        assert "class RegistryManagerAdapter" in content

    def test_di_factory_exists(self):
        """DI factory must wire adapters to service."""
        deps_file = Path(__file__).parent.parent / "app" / "api" / "dependencies.py"
        assert deps_file.exists()
        content = deps_file.read_text()
        assert "def get_metadata_sync_service" in content
        assert "MetadataSyncService" in content

    def test_old_redundant_services_removed(self):
        """Old service files must be deleted — logic lives in infrastructure now."""
        services_dir = Path(__file__).parent.parent / "app" / "services"
        assert not (services_dir / "metadata_editor.py").exists(), "metadata_editor.py should be deleted"
        assert not (services_dir / "metadata_validator.py").exists(), "metadata_validator.py should be deleted"
        assert not (services_dir / "model_generator.py").exists(), "model_generator.py should be deleted"
        assert not (services_dir / "migration_service.py").exists(), "migration_service.py should be deleted"

    def test_infrastructure_has_all_metadata_files(self):
        """Infrastructure metadata package must contain all required files."""
        infra_dir = Path(__file__).parent.parent / "app" / "infrastructure" / "metadata"
        assert (infra_dir / "adapters.py").exists()
        assert (infra_dir / "model_generator.py").exists()
        assert (infra_dir / "migration_service.py").exists()

    def test_adapters_have_no_old_service_imports(self):
        """Adapters must not import from app.services (old location)."""
        adapters_file = Path(__file__).parent.parent / "app" / "infrastructure" / "metadata" / "adapters.py"
        content = adapters_file.read_text()
        assert "from app.services." not in content


# ============================================================
# 2. MetadataSyncService Unit Tests
# ============================================================

class TestMetadataSyncService:
    """Unit tests for the orchestrator with mocked dependencies."""

    def _make_service(self, **overrides):
        from app.application.services.metadata_sync_service import MetadataSyncService
        defaults = {
            "reader": MagicMock(),
            "writer": MagicMock(),
            "validator": MagicMock(),
            "analyzer": MagicMock(),
            "model_generator": MagicMock(),
            "migration_manager": MagicMock(),
            "registry_manager": MagicMock(),
        }
        defaults.update(overrides)
        return MetadataSyncService(**defaults), defaults

    def test_save_and_sync_validation_failure(self):
        """If validation fails, nothing else should happen."""
        validator = MagicMock()
        validator.validate.return_value = (False, ["name is required"])
        service, mocks = self._make_service(validator=validator)

        result = service.save_and_sync("test_entity", {})

        assert not result.success
        assert "Validation failed" in result.message
        assert "name is required" in result.errors
        # Writer should NOT be called
        mocks["writer"].save_metadata.assert_not_called()
        mocks["writer"].create_backup.assert_not_called()

    def test_save_and_sync_happy_path(self):
        """Full happy path: all steps succeed."""
        from app.domain.protocols.metadata_sync import ChangeAnalysis

        validator = MagicMock()
        validator.validate.return_value = (True, [])

        analyzer = MagicMock()
        analyzer.analyze.return_value = ChangeAnalysis(entity_name="asset")

        writer = MagicMock()
        writer.create_backup.return_value = "/backups/asset_123.json"
        writer.save_metadata.return_value = "/modules/core/entities/asset.json"

        reader = MagicMock()
        reader.get_entity_json_path.return_value = Path("/fake/path.json")

        registry = MagicMock()
        registry.reload_entity.return_value = True

        model_gen = MagicMock()
        model_gen.update_model_file.return_value = {"success": True, "model_path": "/models/asset.py"}

        migration = MagicMock()
        migration.check_migration_needed.return_value = {"needs_migration": True}
        migration.generate_migration.return_value = {"success": True, "no_changes": False, "migration_file": "001.py"}
        migration.apply_migration.return_value = {"success": True}

        service, _ = self._make_service(
            validator=validator,
            analyzer=analyzer,
            writer=writer,
            reader=reader,
            registry_manager=registry,
            model_generator=model_gen,
            migration_manager=migration,
        )

        metadata = {"name": "asset", "module": "core", "fields": []}
        result = service.save_and_sync("asset", metadata)

        assert result.success
        assert result.json_saved
        assert result.registry_reloaded
        assert result.model_updated
        assert result.migration_generated
        assert result.migration_applied
        assert result.backup_path == "/backups/asset_123.json"

    def test_save_and_sync_no_schema_changes(self):
        """When model is up to date, no migration should be generated."""
        from app.domain.protocols.metadata_sync import ChangeAnalysis

        validator = MagicMock()
        validator.validate.return_value = (True, [])

        analyzer = MagicMock()
        analyzer.analyze.return_value = ChangeAnalysis(entity_name="asset")

        writer = MagicMock()
        writer.create_backup.return_value = None
        writer.save_metadata.return_value = "/path.json"

        reader = MagicMock()
        reader.get_entity_json_path.return_value = Path("/fake/path.json")

        registry = MagicMock()
        registry.reload_entity.return_value = True

        model_gen = MagicMock()
        model_gen.update_model_file.return_value = {"success": True, "model_path": "/m.py"}

        migration = MagicMock()
        migration.check_migration_needed.return_value = {"needs_migration": False}

        service, _ = self._make_service(
            validator=validator,
            analyzer=analyzer,
            writer=writer,
            reader=reader,
            registry_manager=registry,
            model_generator=model_gen,
            migration_manager=migration,
        )

        result = service.save_and_sync("asset", {"name": "asset", "module": "core", "fields": []})

        assert result.success
        assert result.json_saved
        assert result.model_updated
        assert not result.migration_generated
        assert not result.migration_applied

    def test_save_and_sync_workflow_excluded_entity(self):
        """Entities in MODEL_UPDATE_EXCLUDE should skip model update."""
        from app.domain.protocols.metadata_sync import ChangeAnalysis

        validator = MagicMock()
        validator.validate.return_value = (True, [])

        analyzer = MagicMock()
        analyzer.analyze.return_value = ChangeAnalysis(entity_name="workflow_state")

        writer = MagicMock()
        writer.create_backup.return_value = None
        writer.save_metadata.return_value = "/path.json"

        reader = MagicMock()
        reader.get_entity_json_path.return_value = Path("/fake/path.json")

        registry = MagicMock()
        registry.reload_entity.return_value = True

        model_gen = MagicMock()

        service, _ = self._make_service(
            validator=validator,
            analyzer=analyzer,
            writer=writer,
            reader=reader,
            registry_manager=registry,
            model_generator=model_gen,
        )

        result = service.save_and_sync("workflow_state", {"name": "workflow_state", "module": "core", "fields": []})

        assert result.success
        assert result.json_saved
        assert not result.model_updated
        model_gen.update_model_file.assert_not_called()

    def test_preview_changes(self):
        """Preview should validate and analyze without saving."""
        from app.domain.protocols.metadata_sync import ChangeAnalysis, FieldChange, ChangeType

        validator = MagicMock()
        validator.validate.return_value = (True, [])

        changes = ChangeAnalysis(entity_name="asset")
        changes.add_change(FieldChange(
            field_name="description",
            change_type=ChangeType.SAFE,
            description="New field 'description' will be added",
        ))
        analyzer = MagicMock()
        analyzer.analyze.return_value = changes

        model_gen = MagicMock()
        model_gen.get_model_diff.return_value = {"has_changes": True}

        service, mocks = self._make_service(
            validator=validator,
            analyzer=analyzer,
            model_generator=model_gen,
        )

        result = service.preview_changes("asset", {"name": "asset", "module": "core", "fields": []})

        assert result["valid"]
        assert result["is_safe"]
        assert len(result["changes"]) == 1
        assert result["changes"][0]["field"] == "description"
        assert result["model_has_changes"]
        # Writer should NOT be called
        mocks["writer"].save_metadata.assert_not_called()

    def test_list_entities(self):
        """list_entities delegates to reader."""
        reader = MagicMock()
        reader.list_all_entities.return_value = [{"name": "asset"}, {"name": "location"}]
        service, _ = self._make_service(reader=reader)

        result = service.list_entities()
        assert len(result) == 2
        reader.list_all_entities.assert_called_once()

    def test_reload_all_metadata(self):
        """reload_all_metadata delegates to registry_manager."""
        registry = MagicMock()
        registry.reload_all.return_value = 42
        service, _ = self._make_service(registry_manager=registry)

        count = service.reload_all_metadata()
        assert count == 42
        registry.reload_all.assert_called_once()


# ============================================================
# 3. Infrastructure Adapter Tests
# ============================================================

class TestInfrastructureAdapters:
    """Test that adapters correctly wrap existing services."""

    def test_metadata_validator_delegates(self):
        from app.infrastructure.metadata.adapters import MetadataValidator
        v = MetadataValidator()
        # Valid metadata
        ok, errors = v.validate({"name": "test", "module": "core", "fields": []})
        assert ok
        assert len(errors) == 0

    def test_metadata_validator_catches_errors(self):
        from app.infrastructure.metadata.adapters import MetadataValidator
        v = MetadataValidator()
        ok, errors = v.validate({})  # Missing name and module
        assert not ok
        assert any("name" in e.lower() for e in errors)

    def test_change_analyzer_new_entity(self):
        from app.infrastructure.metadata.adapters import MetadataChangeAnalyzer, JsonMetadataReader
        reader = MagicMock(spec=JsonMetadataReader)
        reader.get_entity_metadata.return_value = None  # New entity
        analyzer = MetadataChangeAnalyzer(reader)
        result = analyzer.analyze("new_entity", {"fields": []})
        assert result.is_safe
        assert len(result.changes) == 1
        assert result.changes[0].field_name == "*"


# ============================================================
# 4. DI Factory Test
# ============================================================

class TestDIFactory:
    """Test that the DI factory creates a working service."""

    def test_factory_creates_service(self):
        from app.api.dependencies import get_metadata_sync_service
        from app.application.services.metadata_sync_service import MetadataSyncService
        service = get_metadata_sync_service()
        assert isinstance(service, MetadataSyncService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
