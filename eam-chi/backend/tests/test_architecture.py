"""
Architecture Enforcement Tests
================================
Validates that Clean Architecture layer boundaries are respected.
"""
import ast
import os
import pytest

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.join(BACKEND_ROOT, "app")


def _get_imports(filepath: str) -> list[str]:
    """Extract all import module paths from a Python file."""
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _collect_py_files(directory: str) -> list[str]:
    """Collect all .py files in a directory recursively."""
    files = []
    for root, _, filenames in os.walk(directory):
        for fn in filenames:
            if fn.endswith(".py"):
                files.append(os.path.join(root, fn))
    return files


class TestDomainLayerBoundaries:
    """Domain layer must not import from infrastructure, application, or API layers."""

    def test_domain_has_no_framework_imports(self):
        domain_dir = os.path.join(APP_ROOT, "domain")
        if not os.path.isdir(domain_dir):
            pytest.skip("domain/ not yet created")

        forbidden = ["fastapi", "sqlalchemy", "jose", "bcrypt", "socketio"]
        violations = []

        for filepath in _collect_py_files(domain_dir):
            imports = _get_imports(filepath)
            for imp in imports:
                for fb in forbidden:
                    if imp.startswith(fb):
                        rel = os.path.relpath(filepath, BACKEND_ROOT)
                        violations.append(f"{rel} imports {imp}")

        assert not violations, "Domain layer must not import framework libs:\n" + "\n".join(violations)

    def test_domain_does_not_import_infra_or_api(self):
        domain_dir = os.path.join(APP_ROOT, "domain")
        if not os.path.isdir(domain_dir):
            pytest.skip("domain/ not yet created")

        forbidden_prefixes = [
            "app.infrastructure",
            "app.application",
            "app.api",
            "app.routers",
            "app.services",
        ]
        violations = []

        for filepath in _collect_py_files(domain_dir):
            imports = _get_imports(filepath)
            for imp in imports:
                for fp in forbidden_prefixes:
                    if imp.startswith(fp):
                        rel = os.path.relpath(filepath, BACKEND_ROOT)
                        violations.append(f"{rel} imports {imp}")

        assert not violations, "Domain layer must not import outer layers:\n" + "\n".join(violations)


class TestApplicationLayerBoundaries:
    """Application layer must not import from API layer or direct SQLAlchemy."""

    def test_application_does_not_import_api_layer(self):
        app_dir = os.path.join(APP_ROOT, "application")
        if not os.path.isdir(app_dir):
            pytest.skip("application/ not yet created")

        forbidden_prefixes = ["app.api", "app.routers"]
        violations = []

        for filepath in _collect_py_files(app_dir):
            imports = _get_imports(filepath)
            for imp in imports:
                for fp in forbidden_prefixes:
                    if imp.startswith(fp):
                        rel = os.path.relpath(filepath, BACKEND_ROOT)
                        violations.append(f"{rel} imports {imp}")

        assert not violations, "Application layer must not import API layer:\n" + "\n".join(violations)


class TestNoReverseServiceToRouterDependency:
    """Services must not import from routers (reverse dependency)."""

    def test_services_do_not_import_routers(self):
        services_dir = os.path.join(APP_ROOT, "services")
        if not os.path.isdir(services_dir):
            pytest.skip("services/ not yet created")

        violations = []
        for filepath in _collect_py_files(services_dir):
            imports = _get_imports(filepath)
            for imp in imports:
                if imp.startswith("app.routers"):
                    rel = os.path.relpath(filepath, BACKEND_ROOT)
                    violations.append(f"{rel} imports {imp}")

        assert not violations, "Services must not import from routers:\n" + "\n".join(violations)


class TestHookRegistryCompleteness:
    """Verify hook registry has entries for all entities that had hooks in the old system."""

    def test_all_hooked_entities_registered(self):
        from app.core.loader import load_modules
        from app.entities import load_all_entities

        load_modules()
        load_all_entities()

        from app.application.hooks.registry import hook_registry

        expected_entities = {
            "asset", "asset_class", "breakdown", "disposed",
            "work_order", "work_order_activity", "work_order_parts",
            "work_order_labor_assignment", "work_order_equipment_assignment",
            "maintenance_request", "maintenance_order",
            "purchase_request", "purchase_receipt",
            "item_issue", "item_return",
            "organization", "site",
        }

        registered = hook_registry.list_entities()
        missing = expected_entities - registered
        assert not missing, f"Missing hook registrations: {missing}"
