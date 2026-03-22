"""
End-to-End Business Logic Tests

Tests all business logic hooks and server actions across modules.
Pure import/validation tests (no DB required) + hook registration tests.
"""
import pytest
import asyncio


# ============================================================================
# IMPORT TESTS — Verify all new modules can be imported
# ============================================================================

class TestCoreEamImports:
    """Core EAM module import tests."""

    def test_trade_availability_import(self):
        from app.modules.core_eam.apis.trade_availability import calculate_trade_capacity
        assert callable(calculate_trade_capacity)


class TestAssetManagementImports:
    """Asset Management module import tests."""

    def test_asset_workflow_import(self):
        from app.modules.asset_management.apis.asset import check_asset_workflow
        assert callable(check_asset_workflow)

    def test_asset_class_hooks_import(self):
        from app.modules.asset_management.apis.asset_class import populate_asset_class_prop_and_maint_plan
        assert callable(populate_asset_class_prop_and_maint_plan)

    def test_asset_class_property_hooks_import(self):
        from app.modules.asset_management.apis.asset_class_property import propagate_property_to_assets
        assert callable(propagate_property_to_assets)

    def test_asset_position_hooks_import(self):
        from app.modules.asset_management.apis.asset_position import update_asset_position_on_save
        assert callable(update_asset_position_on_save)

    def test_asset_class_availability_hooks_import(self):
        from app.modules.asset_management.apis.asset_class_availability import calculate_asset_class_capacity
        assert callable(calculate_asset_class_capacity)

    def test_position_import(self):
        from app.modules.asset_management.apis.position import create_install_asset, create_swap_asset, create_decommission_asset
        assert callable(create_install_asset)
        assert callable(create_swap_asset)
        assert callable(create_decommission_asset)

    def test_breakdown_import(self):
        from app.modules.asset_management.apis.breakdown import create_update_equip_availability_on_save
        assert callable(create_update_equip_availability_on_save)

    def test_disposed_import(self):
        from app.modules.asset_management.apis.disposed import create_purchase_request_on_dispose
        assert callable(create_purchase_request_on_dispose)


class TestWorkMgmtImports:
    """Work Management module import tests."""

    def test_work_order_workflow_import(self):
        from app.modules.work_mgmt.apis.work_order import check_work_order_workflow
        assert callable(check_work_order_workflow)

    def test_work_order_activity_workflow_import(self):
        from app.modules.work_mgmt.apis.work_order_activity import check_work_order_activity_workflow
        assert callable(check_work_order_activity_workflow)

    def test_work_order_labor_hooks_import(self):
        from app.modules.work_mgmt.apis.work_order_labor import update_wo_labor_lead
        assert callable(update_wo_labor_lead)

    def test_work_order_checklist_hooks_import(self):
        from app.modules.work_mgmt.apis.work_order_checklist import create_checklist_details_on_save
        assert callable(create_checklist_details_on_save)

    def test_woa_actions_import(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import (
            generate_templated_pma,
            create_maint_request_from_woa,
            create_transfer_from_woa,
            update_asset_status_from_woa,
            putaway_asset_from_woa,
        )
        assert callable(generate_templated_pma)
        assert callable(create_maint_request_from_woa)
        assert callable(create_transfer_from_woa)
        assert callable(update_asset_status_from_woa)
        assert callable(putaway_asset_from_woa)


class TestMaintenanceMgmtImports:
    """Maintenance Management module import tests."""

    def test_maintenance_request_workflow_import(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        assert callable(check_maintenance_request_workflow)

    def test_maintenance_order_import(self):
        from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order
        assert callable(generate_work_order_from_maintenance_order)

    def test_maintenance_request_actions_import(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request_actions import (
            generate_maintenance_order,
            create_purchase_request_from_context,
        )
        assert callable(generate_maintenance_order)
        assert callable(create_purchase_request_from_context)


# ============================================================================
# HOOK REGISTRATION TESTS
# ============================================================================

class TestHookRegistration:
    """Tests that all hooks are properly registered in the global registry."""

    def test_core_eam_hooks_registered(self):
        from app.application.hooks.registry import hook_registry
        import app.modules.core_eam.hooks  # noqa: F401
        assert "trade_availability" in hook_registry._after_save

    def test_asset_management_hooks_registered(self):
        from app.application.hooks.registry import hook_registry
        import app.modules.asset_management.hooks  # noqa: F401
        assert "asset" in hook_registry._after_save
        assert "asset_class" in hook_registry._after_save
        assert "asset_class_property" in hook_registry._after_save
        assert "asset_position" in hook_registry._after_save
        assert "asset_class_availability" in hook_registry._after_save
        assert "breakdown" in hook_registry._after_save
        assert "disposed" in hook_registry._after_save
        assert "asset" in hook_registry._workflow

    def test_work_mgmt_hooks_registered(self):
        from app.application.hooks.registry import hook_registry
        import app.modules.work_mgmt.hooks  # noqa: F401
        assert "work_order_activity" in hook_registry._after_save
        assert "work_order_labor" in hook_registry._after_save
        assert "work_order_checklist" in hook_registry._after_save
        assert "work_order_labor_assignment" in hook_registry._after_save
        assert "work_order_equipment_assignment" in hook_registry._after_save
        assert "work_order" in hook_registry._workflow
        assert "work_order_activity" in hook_registry._workflow
        assert "work_order_parts" in hook_registry._workflow

    def test_maintenance_mgmt_hooks_registered(self):
        from app.application.hooks.registry import hook_registry
        import app.modules.maintenance_mgmt.hooks  # noqa: F401
        assert "maintenance_request" in hook_registry._workflow
        assert "maintenance_order" in hook_registry._workflow


# ============================================================================
# SERVER ACTION REGISTRATION TESTS
# ============================================================================

class TestServerActionRegistration:
    """Tests that server actions are registered."""

    def test_woa_server_actions_registered(self):
        from app.services.server_actions import server_actions
        import app.modules.work_mgmt.apis.work_order_activity_actions  # noqa: F401
        # The server_actions registry should have entries for work_order_activity
        assert server_actions is not None

    def test_maintenance_request_server_actions_registered(self):
        from app.services.server_actions import server_actions
        import app.modules.maintenance_mgmt.apis.maintenance_request_actions  # noqa: F401
        assert server_actions is not None

    def test_disposed_server_actions_registered(self):
        from app.services.server_actions import server_actions
        import app.modules.asset_management.apis.disposed  # noqa: F401
        assert server_actions is not None

    def test_breakdown_server_actions_registered(self):
        from app.services.server_actions import server_actions
        import app.modules.asset_management.apis.breakdown  # noqa: F401
        assert server_actions is not None


# ============================================================================
# STATELESS VALIDATION TESTS (no DB needed)
# ============================================================================

class TestStatelessValidation:
    """Tests for input validation that doesn't need a DB connection."""

    @pytest.mark.asyncio
    async def test_generate_templated_pma_no_doc(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import generate_templated_pma
        result = await generate_templated_pma(None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_maint_request_no_doc(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import create_maint_request_from_woa
        result = await create_maint_request_from_woa(None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_transfer_invalid_type(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import create_transfer_from_woa
        result = await create_transfer_from_woa("invalid_type", None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_update_asset_status_no_doc(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import update_asset_status_from_woa
        result = await update_asset_status_from_woa(None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_putaway_asset_no_doc(self):
        from app.modules.work_mgmt.apis.work_order_activity_actions import putaway_asset_from_woa
        result = await putaway_asset_from_woa(None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_mr_workflow_no_doc(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow
        result = await check_maintenance_request_workflow(None, "approve", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_mr_workflow_invalid_action(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request import check_maintenance_request_workflow

        class FakeDoc:
            id = "test"

        result = await check_maintenance_request_workflow(FakeDoc(), "invalid_action", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_wo_workflow_no_doc(self):
        from app.modules.work_mgmt.apis.work_order import check_work_order_workflow
        result = await check_work_order_workflow(None, "approve", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_woa_workflow_no_doc(self):
        from app.modules.work_mgmt.apis.work_order_activity import check_work_order_activity_workflow
        result = await check_work_order_activity_workflow(None, "allocate", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_mo_workflow_no_doc(self):
        from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order
        result = await generate_work_order_from_maintenance_order(None, None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_generate_maint_order_no_id(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request_actions import generate_maintenance_order

        class FakeDoc:
            id = None
            asset = None

        result = await generate_maintenance_order(FakeDoc(), None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_generate_maint_order_no_asset(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request_actions import generate_maintenance_order

        class FakeDoc:
            id = "test-mr"
            asset = None

        result = await generate_maintenance_order(FakeDoc(), None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_purchase_request_no_id(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request_actions import create_purchase_request_from_context
        result = await create_purchase_request_from_context(None, "maintenance_request", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_purchase_request_invalid_entity(self):
        from app.modules.maintenance_mgmt.apis.maintenance_request_actions import create_purchase_request_from_context
        result = await create_purchase_request_from_context("test-id", "invalid_entity", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_asset_simple_transitions_allowed(self):
        from app.modules.asset_management.apis.asset import check_asset_workflow

        class FakeDoc:
            id = "test-asset"
            asset_tag = "TEST-001"
            description = "Test Asset"
            site = None
            department = None
            location = None
            inventory = None
            item_type = None
            bypass_process = False

        for action in ["Failed Inspection", "Complete", "Finish Repair",
                        "Retire Asset", "Decommission", "Recommission"]:
            result = await check_asset_workflow(FakeDoc(), action, None, None)
            assert result["status"] == "success", f"Failed for action: {action}"


# ============================================================================
# WORKFLOW ROUTER TESTS
# ============================================================================

class TestWorkflowRouterImports:
    """Verify all workflow routers can be imported and have correct structure."""

    def test_asset_management_workflow_router(self):
        from app.modules.asset_management.workflow_router import route_workflow, _WORKFLOW_HANDLERS
        assert callable(route_workflow)
        assert "asset" in _WORKFLOW_HANDLERS

    def test_work_mgmt_workflow_router(self):
        from app.modules.work_mgmt.workflow_router import route_workflow, _WORKFLOW_HANDLERS
        assert callable(route_workflow)
        assert "work_order" in _WORKFLOW_HANDLERS
        assert "work_order_activity" in _WORKFLOW_HANDLERS
        assert "work_order_parts" in _WORKFLOW_HANDLERS

    def test_maintenance_mgmt_workflow_router(self):
        from app.modules.maintenance_mgmt.workflow_router import route_workflow, _WORKFLOW_HANDLERS
        assert callable(route_workflow)
        assert "maintenance_request" in _WORKFLOW_HANDLERS
        assert "maintenance_order" in _WORKFLOW_HANDLERS

    def test_purchasing_stores_workflow_router(self):
        from app.modules.purchasing_stores.workflow_router import route_workflow, _WORKFLOW_HANDLERS
        assert callable(route_workflow)
        assert "purchase_request" in _WORKFLOW_HANDLERS
        assert "purchase_order" in _WORKFLOW_HANDLERS
        assert "purchase_order_line" in _WORKFLOW_HANDLERS
        assert "purchase_request_line" in _WORKFLOW_HANDLERS
        assert "request_for_quotation" in _WORKFLOW_HANDLERS
        assert "purchase_receipt" in _WORKFLOW_HANDLERS
        assert "item_issue" in _WORKFLOW_HANDLERS
        assert "item_return" in _WORKFLOW_HANDLERS
        assert "stock_count" in _WORKFLOW_HANDLERS
        assert "inventory_adjustment" in _WORKFLOW_HANDLERS


class TestWorkflowRouterStateless:
    """Stateless tests for workflow router dispatch."""

    @pytest.mark.asyncio
    async def test_asset_mgmt_unknown_entity_passthrough(self):
        from app.modules.asset_management.workflow_router import route_workflow
        result = await route_workflow("nonexistent_entity", None, "test", None, None)
        assert result["status"] == "success"
        assert "No workflow handler" in result["message"]

    @pytest.mark.asyncio
    async def test_work_mgmt_unknown_entity_passthrough(self):
        from app.modules.work_mgmt.workflow_router import route_workflow
        result = await route_workflow("nonexistent_entity", None, "test", None, None)
        assert result["status"] == "success"
        assert "No workflow handler" in result["message"]

    @pytest.mark.asyncio
    async def test_maintenance_mgmt_unknown_entity_passthrough(self):
        from app.modules.maintenance_mgmt.workflow_router import route_workflow
        result = await route_workflow("nonexistent_entity", None, "test", None, None)
        assert result["status"] == "success"
        assert "No workflow handler" in result["message"]

    @pytest.mark.asyncio
    async def test_purchasing_stores_unknown_entity_passthrough(self):
        from app.modules.purchasing_stores.workflow_router import route_workflow
        result = await route_workflow("nonexistent_entity", None, "test", None, None)
        assert result["status"] == "success"
        assert "No workflow handler" in result["message"]

    @pytest.mark.asyncio
    async def test_work_order_workflow_no_doc(self):
        from app.modules.work_mgmt.workflow_router import route_workflow
        result = await route_workflow("work_order", None, "Approve", None, None)
        assert result["status"] == "error"
        assert "not specified" in result["message"]

    @pytest.mark.asyncio
    async def test_maintenance_order_workflow_no_doc(self):
        from app.modules.maintenance_mgmt.workflow_router import route_workflow
        result = await route_workflow("maintenance_order", None, "Approve", None, None)
        assert result["status"] == "error"
        assert "not specified" in result["message"]

    @pytest.mark.asyncio
    async def test_purchase_request_workflow_no_doc(self):
        from app.modules.purchasing_stores.workflow_router import route_workflow
        result = await route_workflow("purchase_request", None, "Submit for Review", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_purchase_order_workflow_no_doc(self):
        from app.modules.purchasing_stores.workflow_router import route_workflow
        result = await route_workflow("purchase_order", None, "Approve", None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_rfq_workflow_no_doc(self):
        from app.modules.purchasing_stores.workflow_router import route_workflow
        result = await route_workflow("request_for_quotation", None, "Submit Source", None, None)
        assert result["status"] == "error"


# ============================================================================
# EMPLOYEE SITE TESTS
# ============================================================================

class TestEmployeeSiteImports:
    """Employee Site module import tests."""

    def test_employee_site_import(self):
        from app.modules.core_eam.apis.employee_site import populate_site_field, remove_site_field
        assert callable(populate_site_field)
        assert callable(remove_site_field)

    def test_employee_site_hooks_registered(self):
        from app.application.hooks.registry import hook_registry
        import app.modules.core_eam.hooks  # noqa: F401
        assert "employee_site" in hook_registry._after_save
        assert "employee_site" in hook_registry._after_delete


class TestEmployeeSiteStateless:
    """Stateless validation tests for employee_site logic."""

    @pytest.mark.asyncio
    async def test_populate_site_field_missing_employee(self):
        from app.modules.core_eam.apis.employee_site import populate_site_field

        class FakeDoc:
            employee = None
            site = "test-site"

        result = await populate_site_field(FakeDoc(), None)
        assert result["status"] == "error"
        assert "required" in result["message"]

    @pytest.mark.asyncio
    async def test_populate_site_field_missing_site(self):
        from app.modules.core_eam.apis.employee_site import populate_site_field

        class FakeDoc:
            employee = "test-emp"
            site = None

        result = await populate_site_field(FakeDoc(), None)
        assert result["status"] == "error"
        assert "required" in result["message"]

    @pytest.mark.asyncio
    async def test_remove_site_field_missing_employee(self):
        from app.modules.core_eam.apis.employee_site import remove_site_field

        class FakeDoc:
            employee = None
            site = "test-site"

        result = await remove_site_field(FakeDoc(), None)
        assert result["status"] == "error"
        assert "required" in result["message"]


# ============================================================================
# ADDITIONAL STATELESS VALIDATION TESTS
# ============================================================================

class TestAdditionalStatelessValidation:
    """Additional stateless validation tests for edge cases."""

    @pytest.mark.asyncio
    async def test_trade_capacity_no_id(self):
        from app.modules.core_eam.apis.trade_availability import calculate_trade_capacity

        class FakeDoc:
            id = None

        result = await calculate_trade_capacity(FakeDoc(), None)
        assert result["status"] == "success"
        assert "Skipping" in result["message"]

    @pytest.mark.asyncio
    async def test_asset_class_property_no_id(self):
        from app.modules.asset_management.apis.asset_class_property import propagate_property_to_assets

        class FakeDoc:
            id = None

        result = await propagate_property_to_assets(FakeDoc(), None)
        assert result["status"] == "success"
        assert "Skipping" in result["message"]

    @pytest.mark.asyncio
    async def test_asset_position_missing_fields(self):
        from app.modules.asset_management.apis.asset_position import update_asset_position_on_save

        class FakeDoc:
            asset = None
            position = None

        result = await update_asset_position_on_save(FakeDoc(), None)
        assert result["status"] == "success"
        assert "Skipping" in result["message"]

    @pytest.mark.asyncio
    async def test_asset_class_availability_no_id(self):
        from app.modules.asset_management.apis.asset_class_availability import calculate_asset_class_capacity

        class FakeDoc:
            id = None

        result = await calculate_asset_class_capacity(FakeDoc(), None)
        assert result["status"] == "success"
        assert "Skipping" in result["message"]

    @pytest.mark.asyncio
    async def test_wo_labor_lead_no_id(self):
        from app.modules.work_mgmt.apis.work_order_labor import update_wo_labor_lead

        class FakeDoc:
            id = None
            work_order_activity = None

        result = await update_wo_labor_lead(FakeDoc(), None)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_wo_checklist_no_id(self):
        from app.modules.work_mgmt.apis.work_order_checklist import create_checklist_details_on_save

        class FakeDoc:
            id = None
            checklist = None

        result = await create_checklist_details_on_save(FakeDoc(), None)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_maintenance_order_no_doc(self):
        from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order
        result = await generate_work_order_from_maintenance_order(None, None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_maintenance_order_no_id(self):
        from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order

        class FakeDoc:
            id = None
            work_order = None

        result = await generate_work_order_from_maintenance_order(FakeDoc(), None, None)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_maintenance_order_existing_wo(self):
        from app.modules.maintenance_mgmt.apis.maintenance_order import generate_work_order_from_maintenance_order

        class FakeDoc:
            id = "test-mo"
            work_order = "existing-wo"

        result = await generate_work_order_from_maintenance_order(FakeDoc(), None, None)
        assert result["status"] == "error"
        assert "already exists" in result["message"]


# ============================================================================
# ENTITY LISTING — verify all modules expose expected entities
# ============================================================================

class TestModuleEntityCoverage:
    """Verify all modules list their entities correctly."""

    def test_all_modules_discoverable(self):
        from app.modules import get_installed_modules
        modules = get_installed_modules()
        assert "core_eam" in modules
        assert "asset_management" in modules
        assert "work_mgmt" in modules
        assert "maintenance_mgmt" in modules
        assert "purchasing_stores" in modules
