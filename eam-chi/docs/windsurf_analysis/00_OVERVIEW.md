# Business Logic Gap Analysis — Overview

**Date:** 2026-02-18  
**Source:** Frappe ci_eam app  
**Target:** EAM FastAPI backend  

## Trigger Mechanisms (Frappe → FastAPI)

| Frappe Mechanism | File | FastAPI Equivalent |
|---|---|---|
| `ci_eam_workflow.py` — `dynamic_application_workflow_state()` | Central workflow router | `@hook_registry.workflow("entity")` decorators in each module's `hooks.py` |
| `ci_eam_post_saving.py` — `hook_post_saving()` / `dynamic_post_saving()` | After-insert hook | `@hook_registry.after_save("entity")` decorators in each module's `hooks.py` |
| `ci_eam_post_delete.py` — `hook_post_delete()` / `dynamic_post_delete()` | After-delete hook | `@hook_registry.after_delete("entity")` (needs implementation for some) |
| Server Actions in doctype JSON `"actions": [...]` | Frontend calls `method` path | `@server_actions.register("entity", "action")` in `apis/*.py` |

## Field Name Mapping (Frappe → FastAPI)

| Frappe Field | FastAPI Field | Notes |
|---|---|---|
| `name` (primary key) | `id` | All entities use `id` as PK |
| `parent_asset_class_id` | `parent_asset_class` | Link field |
| `store_location` | `store` | Inventory store field |
| `bin_location` | `bin` | Inventory bin field |
| `current_asset_id` | `current_asset` | Position link to asset |
| `workflow_state` values (Title Case) | `workflow_state` values (snake_case) | e.g. "Awaiting Resources" → "awaiting_resources" |
| `doctype` (used for workflow) | Not needed | Workflow uses entity_name directly |

## Modules Summary

| Module | Frappe Files | FastAPI Status | Gap Level |
|---|---|---|---|
| **Asset Management** | 7 .py files with logic | Mostly implemented | **Medium** — missing post-save hooks for asset_class_property, asset_position, asset_property, asset_class_availability |
| **Core EAM** | 2 .py files (employee_site, trade_availability) | **Not implemented** | **High** — missing employee_site post-save/delete, trade_availability post-save |
| **Maintenance Management** | 2 .py files (maintenance_request, maintenance_order) | Mostly implemented | **Low** — missing generate_maint_order server action, create_purchase_request |
| **Work Management** | 4 .py files (work_order, work_order_activity, work_order_checklist, work_order_labor) | Mostly implemented | **Medium** — missing work_order_checklist post-save, work_order_labor lead/assign post-save |
| **Purchasing & Stores** | Already implemented | Fully implemented | **None** — cross-check only |
