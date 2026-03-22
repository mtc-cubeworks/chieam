# Maintenance Management Module — Business Logic Analysis

## Source Files (Frappe)
- `maintenance_management/doctype/maintenance_request/maintenance_request.py`
- `maintenance_management/doctype/maintenance_order/maintenance_order.py`

## Target Files (FastAPI)
- `modules/maintenance_mgmt/hooks.py`
- `modules/maintenance_mgmt/apis/maintenance_request.py`
- `modules/maintenance_mgmt/apis/maintenance_order.py`

---

## 1. Maintenance Request — Workflow (`check_maint_request_state`)

| Action | Logic | FastAPI Status |
|---|---|---|
| Approve | Generate WO Activity (+ WO resources from PMA if exists), link to MR | ✅ Implemented |
| Submit for Emergency | Emergency priority: Create WO + WOA, auto-approve WO | ✅ Implemented |
| Submit for Resolution | Non-emergency: Create WO, link existing WOA, auto-approve WO | ✅ Implemented |
| Complete | Validate WOA is Completed, set closed_date | ✅ Implemented |
| Reopen | Reopen WOA + WO if closed | ✅ Implemented |

## 2. Maintenance Request — `generate_work_order()`

| Logic | FastAPI Status |
|---|---|
| Approve path: Create WOA from MR, create WO resources from PMA | ✅ `_generate_work_order()` + `_create_wo_resources_from_pma()` |
| Emergency path: Create WO + WOA, auto-approve | ✅ Implemented |
| Non-emergency path: Create WO, link existing WOA | ✅ Implemented |

## 3. Maintenance Request — `generate_maint_order()` (Server Action)

**Frappe Logic:**
Creates a Maintenance Order + Maintenance Order Detail from a Maintenance Request. Checks resource availability (trade, equipment, materials) and sets `resource_availability_status`.

| Logic | FastAPI Status |
|---|---|
| Create Maintenance Order from MR | ❌ **NOT IMPLEMENTED** as server action |
| Create Maintenance Order Detail with resource availability check | ❌ **NOT IMPLEMENTED** |

## 4. Maintenance Request — `create_purchase_request()` (Server Action)

**Frappe Logic:**
Creates a Purchase Request linked to a Work Order Activity or Maintenance Request for resource allocation.

| Logic | FastAPI Status |
|---|---|
| Create PR from WOA or MR | ❌ **NOT IMPLEMENTED** as server action |

## 5. Maintenance Request — `get_maint_req_info()` (Data Fetch)

| Logic | FastAPI Status |
|---|---|
| Fetch MR with resource availability status | ✅ `get_resource_availability_status()` |

## 6. Maintenance Order — Workflow (`generate_work_order`)

| Logic | FastAPI Status |
|---|---|
| Create WO from MO, link all MO Detail WOAs to WO, approve WO | ✅ `generate_work_order_from_maintenance_order()` |

## 7. Maintenance Order — Helper Functions

| Function | Creates | FastAPI Status |
|---|---|---|
| `create_work_order()` | Work Order record | ✅ Used in maintenance_request.py |
| `create_work_order_activity()` | WOA from MR | ✅ `_create_work_order_activity()` |
| `create_work_order_checklist()` | WO Checklist from Checklist | ✅ In `_create_wo_resources_from_pma()` |
| `create_work_order_checklist_detail()` | WO Checklist Detail | ✅ In `_create_wo_resources_from_pma()` |
| `create_work_order_equipment()` | WO Equipment from Maint Equipment | ✅ In `_create_wo_resources_from_pma()` |
| `create_work_order_labor()` | WO Labor from Maint Trade | ✅ In `_create_wo_resources_from_pma()` |
| `create_work_order_parts()` | WO Parts from Maint Parts | ✅ In `_create_wo_resources_from_pma()` |

---

## Gaps to Implement

1. **`generate_maint_order`** server action: Create Maintenance Order + Detail from MR
2. **`create_purchase_request`** server action: Create PR from WOA or MR
