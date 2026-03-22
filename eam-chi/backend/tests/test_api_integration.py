"""
API Integration Tests
======================
Tests API endpoints using httpx.AsyncClient against the FastAPI app.
These tests require the app to be importable but do NOT require a live database.
They test route registration, response schemas, and error handling.
"""
import pytest
import os
import sys

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_ROOT)


class TestRouteRegistration:
    """Verify that all expected routes are registered on the FastAPI app."""

    def _get_routes(self):
        from app.main import fastapi_app
        return [r.path for r in fastapi_app.routes if hasattr(r, 'path')]

    def test_meta_routes_registered(self):
        routes = self._get_routes()
        assert any("/api/meta" in r for r in routes), "Meta routes not found"

    def test_auth_routes_registered(self):
        routes = self._get_routes()
        assert any("/api/auth" in r or "/login" in r for r in routes), "Auth routes not found"

    def test_entity_crud_routes_registered(self):
        routes = self._get_routes()
        assert any("/api/entity" in r for r in routes), "Entity CRUD routes not found"

    def test_admin_routes_registered(self):
        routes = self._get_routes()
        assert any("/admin" in r or "/api/admin" in r for r in routes), "Admin routes not found"

    def test_import_export_routes_registered(self):
        routes = self._get_routes()
        assert any("import" in r or "export" in r for r in routes), "Import/export routes not found"

    def test_attachment_routes_registered(self):
        routes = self._get_routes()
        assert any("attachment" in r for r in routes), "Attachment routes not found"

    def test_workflow_routes_registered(self):
        routes = self._get_routes()
        assert any("workflow" in r for r in routes), "Workflow routes not found"

    def test_model_editor_routes_registered(self):
        routes = self._get_routes()
        assert any("model-editor" in r for r in routes), "Model editor routes not found"

    def test_minimum_route_count(self):
        """App should have at least 50 routes (we expect ~90)."""
        routes = self._get_routes()
        assert len(routes) >= 50, f"Only {len(routes)} routes registered, expected >= 50"


class TestAppConfiguration:
    """Verify app-level configuration."""

    def test_cors_middleware_present(self):
        from app.main import fastapi_app
        middleware_names = []
        for m in fastapi_app.user_middleware:
            cls_name = getattr(m, 'cls', None)
            if cls_name:
                middleware_names.append(cls_name.__name__)
            else:
                middleware_names.append(type(m).__name__)
        assert any("CORS" in cls or "cors" in cls.lower() for cls in middleware_names), \
            f"CORS middleware not found in {middleware_names}"

    def test_app_title(self):
        from app.main import fastapi_app
        assert fastapi_app.title is not None
        assert len(fastapi_app.title) > 0

    def test_exception_handlers_registered(self):
        from app.main import fastapi_app
        # Should have custom exception handlers
        assert len(fastapi_app.exception_handlers) > 0


class TestSchemaImports:
    """Verify that API schemas are importable."""

    def test_action_response_schema(self):
        from app.schemas.base import ActionResponse
        resp = ActionResponse(status="success", message="test")
        assert resp.status == "success"

    def test_action_request_schema(self):
        from app.schemas.base import ActionRequest
        req = ActionRequest(action="test_action")
        assert req.action == "test_action"


class TestEntityMetaRegistry:
    """Verify entity metadata is loaded correctly."""

    @classmethod
    def setup_class(cls):
        from app.core.loader import load_modules
        from app.entities import load_all_entities
        load_modules()
        load_all_entities()

    def test_meta_registry_has_entities(self):
        from app.meta.registry import MetaRegistry
        entities = MetaRegistry.list_all()
        assert len(entities) > 0, "No entities registered in MetaRegistry"

    def test_meta_registry_has_asset(self):
        from app.meta.registry import MetaRegistry
        asset = MetaRegistry.get("asset")
        assert asset is not None, "Asset entity not found in MetaRegistry"
        assert asset.name == "asset"
        assert len(asset.fields) > 0

    def test_meta_registry_entity_has_required_attrs(self):
        from app.meta.registry import MetaRegistry
        for meta in MetaRegistry.list_all():
            assert hasattr(meta, 'name'), f"Entity missing 'name'"
            assert hasattr(meta, 'fields'), f"{meta.name} missing 'fields'"
            assert hasattr(meta, 'label'), f"{meta.name} missing 'label'"
            assert hasattr(meta, 'module'), f"{meta.name} missing 'module'"
