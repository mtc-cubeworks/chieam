# Core EAM — Entity Relationship Audit

**28 entities** in `core_eam` module.

For masterfile-level issues (site ↔ location, site ↔ cost_code), see [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md).

---

## 1. Excel Sheet Order (Data Entry Sequence)

From `Core_EAM_Data.xlsx`:

| # | Sheet | Maps To Entity |
|---|-------|---------------|
| 1 | Manufacturer | `manufacturer` |
| 2 | Model | `model` |
| 3 | Trade | `trade` |

**Only 3 sheets.** Most core_eam entities are either system-level (organization, site, department — seeded via Asset Masterfiles) or operational (labor, employee — created during setup).

---

## 2. Entity Grouping

### Root / Organizational (top-level, seeded first)
- `organization`
- `site`
- `department`
- `account`
- `cost_code`

### Reference / Masterfile (created during initial setup)
- `manufacturer`
- `model`
- `contractor`
- `trade`
- `labor_group`
- `leave_type`
- `request_activity_type`

### Operational (created during system use)
- `employee`
- `employee_site`
- `labor`
- `trade_labor`
- `trade_availability`
- `labor_availability` → `labor_availability_details`
- `work_schedule` → `work_schedule_details`
- `holiday`
- `leave_application`
- `annual_budget`

### System
- `note` → `note_seen_by`
- `error_log`

---

## 3. Entity Dependency Map

| Entity | Depends On | Notes |
|--------|-----------|-------|
| `organization` | — (standalone) | Root. ✅ |
| `site` | organization, ~~cost_code~~, ~~location~~, employee | ❌ See issues below |
| `department` | site, employee, cost_code, account ×2 | ✅ |
| `account` | — (standalone) | ✅ |
| `cost_code` | site (conditional on scope=Per Site) | ✅ |
| `manufacturer` | — (standalone) | ✅ |
| `model` | manufacturer | ✅ |
| `contractor` | — (standalone) | ✅ |
| `trade` | — (standalone) | ✅ |
| `labor_group` | — (standalone) | ✅ |
| `leave_type` | — (standalone) | ✅ |
| `request_activity_type` | — (standalone) | ✅ |
| `employee` | users (system) | ✅ |
| `employee_site` | employee, site, department | ✅ Junction table |
| `labor` | labor_group, employee, contractor, location | ✅ Cross-module: location (asset_mgmt) |
| `trade_labor` | trade, labor | ✅ Junction table |
| `trade_availability` | trade | ✅ |
| `labor_availability` | labor | ✅ |
| `labor_availability_details` | labor_availability | ✅ |
| `work_schedule` | labor_group, labor | ✅ |
| `work_schedule_details` | work_schedule | ✅ |
| `holiday` | labor_group, labor | ✅ |
| `leave_application` | labor, leave_type | ✅ |
| `annual_budget` | cost_code | ✅ |
| `note` | — (standalone) | ✅ |
| `note_seen_by` | note, users | ✅ |
| `error_log` | — (standalone) | ✅ System entity |

---

## 4. Issues Found

### 4.1 Site → Location (WRONG DIRECTION)

`site.json` has `location` → `location` (asset_management).

Location depends on Site, not the other way around. This creates a circular dependency and violates masterfile creation order.

**Fix:** Remove `location` and `location_name` from `site.json`.

---

### 4.2 Site → Default Cost Code (CIRCULAR)

`site.json` has `default_cost_code` → `cost_code`. But `cost_code.json` has `site` → `site` (when scope = Per Site).

Neither can be created first cleanly.

**Fix:** Remove `default_cost_code` from `site.json`. If a site needs a default cost code, look it up by query (cost_codes where site = this site).

---

### 4.3 Department → Employee (mild ordering concern)

`department.json` has `department_manager` → `employee`.

Employee depends on having a user account. During initial data import, department might be created before employees exist.

**Verdict:** Acceptable — manager is optional. Just ensure the field is not `required`.

---

### 4.4 Labor → Location (cross-module)

`labor.json` has `location` → `location` (asset_management module).

This is fine — labor can be assigned to a physical location. No issue.

---

### 4.5 Site links config is overloaded

`site.json` has **19 related tabs** in its `links` config (department, cost_code, location, system, position, asset, maintenance_request, store, zone, bin, inventory, item_issue, item_return, stock_count, inventory_adjustment, purchase_request, purchase_request_line, purchase_return, work_order, work_order_activity).

This is a UX concern — showing 19+ tabs on a Site form is overwhelming.

**Recommendation:** Reduce to key tabs: Department, Location, Store, Asset, Work Order. The rest can be accessed via reports or filtered list views.

---

## 5. Unreferenced Entities

| Entity | Concern |
|--------|---------|
| `error_log` | System entity. No inbound links expected. ✅ |
| `leave_application` | Only links TO labor and leave_type. No entity links back. Should be in `labor.links` config as a related tab. |

---

## 6. Entity Catalog

| Entity | Fields | Status | Notes |
|--------|--------|--------|-------|
| `organization` | 4 | ✅ | Root |
| `site` | 8 | ❌ | Remove `location`, `default_cost_code` |
| `department` | 11 | ✅ | |
| `account` | 3 | ✅ | Standalone |
| `cost_code` | 5 | ✅ | Site conditional on scope |
| `manufacturer` | 2 | ✅ | |
| `model` | 3 | ✅ | |
| `contractor` | 1 | ✅ | |
| `trade` | 5 | ✅ | |
| `labor_group` | 1 | ✅ | |
| `leave_type` | 1 | ✅ | |
| `request_activity_type` | 4 | ✅ | |
| `employee` | 3 | ✅ | |
| `employee_site` | 4 | ✅ | Junction: employee ↔ site ↔ department |
| `labor` | 10 | ✅ | |
| `trade_labor` | 4 | ✅ | Junction: trade ↔ labor |
| `trade_availability` | 5 | ✅ | |
| `labor_availability` | 3 | ✅ | |
| `labor_availability_details` | 4 | ✅ | |
| `work_schedule` | 5 | ✅ | |
| `work_schedule_details` | 5 | ✅ | |
| `holiday` | 4 | ✅ | |
| `leave_application` | 5 | ✅ | |
| `annual_budget` | 4 | ✅ | |
| `note` | 6 | ✅ | System |
| `note_seen_by` | 2 | ✅ | System |
| `error_log` | 3 | ✅ | System |
