# RFQ & Server Actions Refactor

## Summary

This document covers the comprehensive refactoring of the RequestForQuotation (RFQ) entity and the server actions system across backend and frontend.

**Date:** 2026-02-06  
**Test Result:** 24/24 E2E tests passing  
**Test Script:** `backend/tests/test_pr_workflow_e2e.py`

---

## 1. Snake_case Entity Naming

### Problem
`RequestForQuotation` and `RfqLine` used PascalCase names in JSON metadata, causing mismatches with the snake_case `__tablename__` in SQLAlchemy models and the `_get_model()` lookup.

### Changes
| File | Change |
|------|--------|
| `entities/RequestForQuotation.json` → `entities/request_for_quotation.json` | Renamed file, `"name": "request_for_quotation"` |
| `entities/RfqLine.json` → `entities/rfq_line.json` | Renamed file, `"name": "rfq_line"` |
| `rfq_line.json` | `link_entity` values → snake_case (`request_for_quotation`, `purchase_request_line`, `item`) |
| `request_for_quotation.json` | `link_entity` values → snake_case (`vendor`, `employee`) |
| `apis/purchase_request.py` | `new_doc("RequestForQuotation", ...)` → `new_doc("request_for_quotation", ...)` |
| `models/RequestForQuotation.py` | **Deleted** — dead duplicate with wrong `__tablename__` |

---

## 2. Frappe-style Server Actions

### Problem
Actions in entity JSON used full endpoint URLs and HTTP methods:
```json
{
  "action": "generate_rfq",
  "endpoint": "/api/entity/purchase_request/{id}/action/generate_rfq",
  "method": "POST",
  "show_when": {"workflow_state": ["pending_review", ...]}
}
```
This was verbose, coupled frontend to specific URLs, and the `show_when` gate in the backend blocked actions before the handler could run its own validation.

### New Format (Frappe-style)
```json
{
  "action": "generate_rfq",
  "label": "Generate RFQ",
  "method": "app.modules.purchasing_stores.apis.purchase_request.generate_rfq"
}
```

- **`method`** — Python dotted path to the handler function
- **`show_when`** — Optional, frontend-only UI hint (NOT enforced by backend)
- **No `endpoint`** — Frontend calls standard `POST /api/entity/{entity}/{id}/action/{action_name}`

### Handler Signature
```python
async def generate_rfq(doc, db, user) -> dict:
    """Frappe-style server action.
    
    Args:
        doc: SQLAlchemy model instance of the record
        db: AsyncSession
        user: CurrentUser
    
    Returns:
        {"status": "success/error", "message": "...", ...}
    """
```

### Auto-Registration
Actions are auto-registered on startup from entity JSON `method` paths in `entities/__init__.py → _register_entity_actions()`. No manual `@server_actions.register()` decorators needed.

### Files Changed
| File | Change |
|------|--------|
| `meta/registry.py` | `ActionMeta` — removed `endpoint`, `method` is now Python dotted path |
| `entities/__init__.py` | Added `_register_entity_actions()` for auto-registration |
| `services/server_actions.py` | `load_from_handler_path()` wraps Frappe-style `(doc, db, user)` into `ActionContext` adapter; `execute()` no longer double-wraps results |
| `api/routes/entity_crud.py` | `document_action()` — removed `show_when` gate; handler does own validation |
| All 6 entity JSON files with actions | Converted to Frappe-style method paths |
| `apis/purchase_request.py` | Removed `@server_actions.register` decorator block |
| `apis/purchase_order.py` | Removed `@server_actions.register` decorator block |

### Entities Updated
- `purchase_request.json` — `generate_rfq`, `create_purchase_order`
- `stock_count.json` — `find_stock_count_lines`
- `disposed.json` — `create_purchase_request`
- `breakdown.json` — `create_update_equip_availability`
- `work_order_activity.json` — `generate_templated_pma`

---

## 3. Workflow State for RFQ

### Problem
`request_for_quotation` table had no `workflow_state` column. Creating an RFQ via `new_doc()` failed with `'workflow_state' is an invalid keyword argument`.

### Fix
- Added `workflow_state` column to `request_for_quotation` model (`String(50), nullable=True, default="draft"`)
- Added column to database via `ALTER TABLE`
- Added `workflow_state` hidden field to `request_for_quotation.json`
- Dropped orphan `"RequestForQuotation"` table (PascalCase, wrong schema)

---

## 4. Workflow Metadata Fallback

### Problem
The `/api/meta/{entity}` endpoint only loaded workflow from the database `workflows` table. Entities like RFQ that define workflow in JSON but have no DB workflow entry got `"workflow": null`.

### Fix
Added JSON fallback in `routers/meta.py`: if no DB workflow exists, serialize the `WorkflowMeta` from entity JSON (states, transitions, initial_state). This means any entity can define workflow in JSON without needing DB seeding.

---

## 5. Frontend Fixes

### Button Visibility Flash
**Problem:** Edit/Delete buttons briefly appeared then disappeared as permissions loaded.  
**Root Cause:** `canEdit` defaulted to `true` when `entityMeta.permissions` was undefined.  
**Fix:** `canEdit` returns `false` until `permissions` object exists. `canDelete` same.

### DocumentAction Interface
Removed `endpoint` and `method` (HTTP method) fields from the `DocumentAction` TypeScript interface. Frontend now only needs `action`, `label`, `confirm?`, `show_when?`.

---

## 6. Bug Fixes Found During Testing

### Bug 1: Empty String FK Violation (generate_rfq)
- **File:** `apis/purchase_request.py`
- **Root Cause:** `requestor=requestor or ""` sent empty string `""` as FK value
- **Fix:** Changed to `requestor or None`

### Bug 2: PO/PO Line Missing site/department (create_po_from_pr)
- **File:** `apis/purchase_order.py`
- **Root Cause:** PO creation pulled `site`/`department` from PR lines which often don't have them. `purchase_order.site` and `purchase_order_line.site` are NOT NULL with FK constraints.
- **Fix:** Pull site/department from parent PR doc first, fall back to PR line values, then use "UNASSIGNED" as last resort for PO header. PO lines inherit from PO header when line-level values are null.

### Bug 3: Workflow State Normalization (create_po_from_pr)
- **File:** `apis/purchase_order.py`  
- **Root Cause:** State comparison `pr_state != "approved"` failed when DB stored mixed-case values like `"Approved"` or `"approved"`.
- **Fix:** Normalize to lowercase slug before comparison.

---

## 7. Test Results

```
E2E Test: 24/24 PASSED

Phase 1: Authentication ✅
Phase 2: Entity Metadata Validation
  - RFQ metadata loads ✅
  - RFQ name is snake_case ✅
  - RFQ workflow from JSON fallback ✅
  - PR actions (Frappe-style, no endpoint) ✅
Phase 3: Create Purchase Request ✅
Phase 4: Add PR Lines ✅
Phase 5: Draft → Pending Review ✅
Phase 6: Generate RFQ (server action) ✅
Phase 7: Pending Review → Pending Approval ✅
Phase 8: Pending Approval → Approved ✅
Phase 9: Create Purchase Order (server action) ✅
Phase 10: Validation Tests
  - Generate RFQ from Draft fails ✅
  - Create PO from Draft fails ✅
```
