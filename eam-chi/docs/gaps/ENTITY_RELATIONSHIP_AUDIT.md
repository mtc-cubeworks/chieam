# Entity Relationship Audit

**113 entities** across 5 modules: `core_eam`, `asset_management`, `maintenance_mgmt`, `purchasing_stores`, `work_mgmt`.

---

## Table of Contents

1. [Masterfile Creation Order](#1-masterfile-creation-order)
2. [Critical Issues](#2-critical-issues)
3. [Circular References](#3-circular-references)
4. [Redundant Fields on Child Entities](#4-redundant-fields-on-child-entities)
5. [Illogical Dependencies](#5-illogical-dependencies)
6. [Full Entity Catalog](#6-full-entity-catalog)

---

## 1. Masterfile Creation Order

From the Asset Masterfiles Excel, the intended data entry order is:

| # | Entity | Depends On |
|---|--------|-----------|
| 1 | Organization | — (root) |
| 2 | Site | Organization |
| 3 | Department | Site |
| 4 | Location Type | — (standalone) |
| 5 | Location | Location Type, Site, (parent Location) |
| 6 | System Type | — (standalone) |
| 7 | System | System Type, Location, Site, (parent System) |
| 8 | Unit of Measure | — (standalone) |
| 9 | Property | Unit of Measure, Property Type |
| 10 | Manufacturer | — (standalone) |
| 11 | Model | Manufacturer |
| 12 | Vendor | — (standalone, but currently links Site) |
| 13 | Asset Class | (parent Asset Class) |
| 14 | Asset Class Property | Asset Class, Property |
| 15 | Item | Item Class, Unit of Measure, Vendor, Asset Class |
| 16 | Position | Asset Class, System, Location, Site |
| 17 | Position Relation | Position, Position |
| 18 | Asset | Asset Class, Location, Site, Department, System, Position, Item |
| 19 | Asset Property | Asset, Property |
| 20 | Asset Position | Position, Asset |

---

## 2. Critical Issues

### 2.1 Site → Location (WRONG DIRECTION)

**`site.json`** has a `location` field linking to `location`.

**Problem:** Location depends on Site (a Location belongs to a Site). Site does NOT depend on Location. The masterfile order is: Site (#2) → Location (#5). You cannot pick a Location when creating a Site because Locations don't exist yet.

**Fix:** Remove `location` and `location_name` fields from `site.json`.

---

### 2.2 Site ↔ Cost Code (CIRCULAR)

- `site.json` has `default_cost_code` → `cost_code`
- `cost_code.json` has `site` → `site`

**Problem:** This is a circular dependency. Cost Code has a `scope` field (Global vs Per Site). When scope is "Per Site", the `site` link makes sense. But Site also has `default_cost_code` pointing back. Neither can be created first cleanly.

**Fix:** Remove `default_cost_code` from `site.json`. Instead, Cost Code should stand on its own. If a Site needs a "default" cost code, that's a configuration lookup (find cost codes where site = this site), not a field on Site.

---

### 2.3 Vendor → Site (DOESN'T MAKE SENSE)

**`vendor.json`** has only 2 fields: `vendor_name` and `site` → `site`.

**Problem:** A Vendor is an external company. Vendors are not owned by a Site — they supply to potentially many sites. The masterfile order has Vendor (#12) as standalone.

**Fix:** Remove `site` from `vendor.json`. If you need to track which sites a vendor supplies to, use a child table (e.g., `vendor_site`).

---

### 2.4 Category of Failure → Site (QUESTIONABLE)

**`category_of_failure.json`** has `site` → `site`.

**Problem:** Failure categories (e.g., "Electrical Failure", "Mechanical Wear") are typically global definitions, not site-specific. Having `site` makes filtering harder and forces duplication if the same category applies to multiple sites.

**Fix:** Remove `site` from `category_of_failure.json`. If site-specific filtering is needed, do it through the work order's site.

---

### 2.5 Item → Inventory Adjustment (WRONG LINK)

**`item.json`** has `inventory_adjustment_account` → `inventory_adjustment`.

**Problem:** This field should link to `account`, not `inventory_adjustment`. An "Inventory Adjustment Account" is a GL account code, not an inventory adjustment transaction.

**Fix:** Change `link_entity` from `inventory_adjustment` to `account`.

---

### 2.6 Equipment → Purchase Request Line (DOESN'T MAKE SENSE)

**`equipment.json`** has `pr_line_no` → `purchase_request_line`.

**Problem:** Equipment is a masterfile-level entity. A PR Line is a transactional document. Masterfiles should not reference transactions. The PR line that procured the equipment is historical context — it belongs on the inventory/receipt record, not on the equipment record.

**Fix:** Remove `pr_line_no` from `equipment.json`. Procurement history is traceable through Inventory → Purchase Receipt → PO Line → PR Line.

---

### 2.7 Bin → Site (REDUNDANT)

**`bin.json`** has both `store` → `store` and `site` → `site`.

**Problem:** Store already has a `site` field. Bin → Store → Site is the correct path. Having `site` directly on Bin is redundant.

**Fix:** Remove `site` from `bin.json`. Derive it from `store.site`.

---

### 2.8 Zone → Site (REDUNDANT)

Same as Bin. `zone.json` has `store` and `site`. Site is derivable from Store.

**Fix:** Remove `site` from `zone.json`.

---

### 2.9 Store → Site (REDUNDANT)

**`store.json`** has `location` → `location` and `site` → `site`.

**Problem:** Location already has a `site` field. Store → Location → Site.

**Fix:** Remove `site` from `store.json`. Derive from `location.site`.

---

### 2.10 System → Site (REDUNDANT)

**`system.json`** has `location` → `location` and `site` → `site`.

**Problem:** Location already carries Site. System → Location → Site.

**Fix:** Remove `site` from `system.json`. Derive from `location.site`.

---

### 2.11 Position → Site (REDUNDANT)

**`position.json`** has `location`, `system`, and `site`.

**Problem:** Both Location and System already carry Site.

**Fix:** Remove `site` from `position.json`. Derive from `location.site`.

---

## 3. Circular References

| Entity A | Entity B | Forward | Backward | Verdict |
|----------|----------|---------|----------|---------|
| **site** | **cost_code** | `site.default_cost_code → cost_code` | `cost_code.site → site` | **BAD** — Remove `default_cost_code` from Site |
| **site** | **location** | `site.location → location` | `location.site → site` | **BAD** — Remove `location` from Site |
| **asset** | **inventory** | `asset.inventory → inventory` | `inventory.asset → asset` | **OK** — Bidirectional link (asset knows its inventory, inventory knows its asset). Both are `[ro]`. System-managed. |
| **asset** | **position** | `asset.position → position` | `position.current_asset → asset` | **OK** — Bidirectional. Both reflect current assignment. `position.current_asset` is `[ro]`. |
| asset_class | asset_class | `parent_asset_class → asset_class` | (self) | **OK** — Tree structure |
| location | location | `parent_location → location` | (self) | **OK** — Tree structure |
| system | system | `parent_system → system` | (self) | **OK** — Tree structure |
| item_class | item_class | `parent_item_class → item_class` | (self) | **OK** — Tree structure |
| maintenance_request | maintenance_request | `next_maintenance_request → maintenance_request` | (self) | **OK** — Linked list |

---

## 4. Redundant Fields on Child Entities

These are fields that exist on both a parent entity and its child. In many cases these are **intentional audit/UX copies** (prefilled from parent, stored for quick filtering/reporting). But some are wasteful.

### 4.1 Intentional Redundancy (OK — for audit/filtering)

Transaction entities (purchase_request, work_order, etc.) carrying `site`, `department`, `cost_code` even though their parent or linked entity already has them. These are **acceptable** because:
- They enable direct filtering without joins
- They serve as audit snapshots (the site at time of transaction)
- They are typically prefilled by the system

**Examples that are fine:**
- `purchase_request` has `site`, `department`, `cost_code` (transaction-level audit)
- `work_order` has `site`, `department`, `cost_code` (transaction-level audit)
- `maintenance_request` has `site`, `department` (transaction-level audit)
- `item_issue` / `item_return` has `site`, `department`, `cost_code` (transaction-level audit)
- `work_order_activity` has `site`, `department` (activity could span different depts)

### 4.2 Wasteful Redundancy (SHOULD REMOVE)

These child/line entities duplicate `site`, `department`, `cost_code` from their parent document when there is NO business reason for them to differ:

| Child Entity | Redundant Field | Already On Parent | Fix |
|-------------|----------------|-------------------|-----|
| `purchase_order_line.site` | site | `purchase_order.site` | Remove — PO Line inherits from PO |
| `purchase_order_line.department` | department | `purchase_order.department` | Remove |
| `purchase_order_line.cost_code` | cost_code | `purchase_order.cost_code` | Remove |
| `purchase_request_line.site` | site | `purchase_request.site` | Remove — PR Line inherits from PR |
| `purchase_request_line.department` | department | `purchase_request.department` | Remove |
| `purchase_request_line.cost_code` | cost_code | `purchase_request.cost_code` | Remove |
| `purchase_receipt.site` | site | `purchase_order_line → purchase_order.site` | Remove |
| `purchase_receipt.department` | department | same path | Remove |
| `purchase_receipt.cost_code` | cost_code | same path | Remove |
| `work_order_equipment_actual_hours.site` | site | Derivable from WO Equipment → WOA → WO | Remove |
| `work_order_equipment_actual_hours.department` | department | same | Remove |
| `work_order_equipment_actual_hours.cost_code` | cost_code | same | Remove |
| `work_order_labor_actual_hours.site` | site | Derivable from WO Labor → WOA → WO | Remove |
| `work_order_labor_actual_hours.department` | department | same | Remove |
| `work_order_labor_actual_hours.cost_code` | cost_code | same | Remove |
| `sales_order_item.site` | site | `sales_order.site` | Remove |
| `sales_order_item.department` | department | Not on sales_order at all | Remove field entirely or add to parent |
| `stock_count_task.site` | site | `stock_count.site` | Remove |
| `disposed.site` | site | `disposed.asset → asset.site` | Remove |
| `sensor.site` | site | `sensor.asset → asset.site` | Remove |

**Note:** If business requires line-level cost center overrides (e.g., PR Line can have different cost_code than PR header), keep those fields but document that intent clearly.

---

## 5. Illogical Dependencies

### 5.1 Masterfile entities linking to transaction entities

| Entity | Field | Links To | Problem |
|--------|-------|----------|---------|
| `item` | `inventory_adjustment_account` | `inventory_adjustment` | Should link to `account`. Wrong link_entity. |
| `equipment` | `pr_line_no` | `purchase_request_line` | Masterfile should not reference a transaction. Remove. |

### 5.2 Standalone entities that shouldn't have Site

| Entity | Why Site is wrong |
|--------|------------------|
| `vendor` | External company. Not site-scoped. |
| `category_of_failure` | Global definition. Filter via work order site instead. |

### 5.3 Department → Cost Code ordering issue

`department.json` has `default_cost_code` → `cost_code`. In the masterfile order, Department (#3) comes before Cost Code (not in masterfile, but logically after Department). This creates a mild dependency concern. However, since Cost Code is a reference table that can be pre-loaded, this is **acceptable** but should be documented.

### 5.4 Department → Employee (ordering)

`department.json` has `department_manager` → `employee`. Employee is not in the masterfile order. Employee depends on having a user account. This is **acceptable** — manager assignment is optional and happens after initial setup.

### 5.5 Missing parent_child relationships

Some entities use `link` fields where they should probably be `children` (child table via the `links` config on the parent):

- `checklist_details` → `checklist` (should be a child of Checklist)
- `work_schedule_details` → `work_schedule` (should be a child of Work Schedule)
- `labor_availability_details` → `labor_availability` (should be a child)
- `maintenance_calendar` → `planned_maintenance_activity` (should be a child)
- `maintenance_condition` → `planned_maintenance_activity` (should be a child)
- `maintenance_interval` → `planned_maintenance_activity` (should be a child)

These work as-is (related tab in UI), but semantically they're "detail rows" not standalone entities.

---

## 6. Full Entity Catalog

### 6.1 Core EAM (15 entities)

| Entity | Fields | Links To | Notes |
|--------|--------|----------|-------|
| `organization` | 4 | — | Root entity. No dependencies. ✅ |
| `site` | 8 | organization, ~~cost_code~~, employee, ~~location~~ | ❌ Remove `location`, `default_cost_code` |
| `department` | 11 | site, employee, cost_code, account ×2 | ✅ OK |
| `cost_code` | 5 | site | ✅ Site link conditional on scope=Per Site |
| `account` | 3 | — | Standalone. ✅ |
| `employee` | 3 | users | ✅ |
| `employee_site` | 4 | employee, site, department | ✅ Junction table |
| `manufacturer` | 2 | — | Standalone. ✅ |
| `model` | 3 | manufacturer | ✅ |
| `contractor` | 1 | — | Standalone. ✅ |
| `labor_group` | 1 | — | Standalone. ✅ |
| `labor` | 10 | labor_group, employee, contractor, location | ✅ |
| `trade` | 5 | — | Standalone. ✅ |
| `note` | 6 | — | Standalone. ✅ |
| `request_activity_type` | 4 | — | Standalone. ✅ |

**Plus child/detail entities:** `annual_budget`, `employee_site`, `error_log`, `holiday`, `labor_availability`, `labor_availability_details`, `leave_application`, `leave_type`, `note_seen_by`, `trade_availability`, `trade_labor`, `work_schedule`, `work_schedule_details`

### 6.2 Asset Management (21 entities)

| Entity | Fields | Links To | Notes |
|--------|--------|----------|-------|
| `location_type` | 1 | — | Standalone. ✅ |
| `location` | 9 | location_type, parent location, site | ✅ Tree entity |
| `system_type` | 1 | — | Standalone. ✅ |
| `system` | 7 | system_type, parent system, location, ~~site~~ | ❌ Remove `site` (derive from location) |
| `property_type` | 1 | — | Standalone. ✅ |
| `property` | 6 | unit_of_measure, property_type | ✅ |
| `asset_class` | 4 | parent asset_class | ✅ Tree entity |
| `asset_class_property` | 4 | asset_class, property, uom | ✅ |
| `asset_class_availability` | 5 | asset_class | ✅ |
| `position` | 11 | asset_class, system, location, ~~site~~, asset[ro] | ❌ Remove `site` |
| `position_relation` | 5 | position ×2 | ✅ |
| `asset` | 24 | asset_class, location, site, department, employee, inventory[ro], system, position, item[ro] | ✅ Site is the canonical owner |
| `asset_property` | 5 | asset, property, uom | ✅ |
| `asset_position` | 4 | position, asset | ✅ History table |
| `sub_asset` | 2 | asset ×2 | ✅ |
| `equipment_group` | 1 | — | Standalone. ✅ |
| `equipment` | 11 | equipment_group, employee, location, site, inventory, ~~purchase_request_line~~ | ❌ Remove `pr_line_no` |
| `breakdown` | 5 | equipment | ✅ |
| `incident` | 15 | location, asset, users, site, department, employee | ✅ Transaction |
| `incident_employee` | 8 | incident, employee | ✅ |
| `disposed` | 7 | asset, ~~site~~ | ❌ Remove `site` (derive from asset) |

### 6.3 Maintenance Management (16 entities)

| Entity | Fields | Links To | Notes |
|--------|--------|----------|-------|
| `maintenance_activity` | 2 | — | Standalone. ✅ |
| `maintenance_trade` | 4 | maintenance_activity, trade | ✅ |
| `maintenance_parts` | 3 | maintenance_activity, item | ✅ |
| `maintenance_equipment` | 4 | maintenance_activity, equipment | ✅ |
| `checklist` | 2 | — | Standalone. ✅ |
| `checklist_details` | 3 | checklist | ✅ |
| `maintenance_plan` | 7 | asset_class, manufacturer, model | ✅ |
| `planned_maintenance_activity` | 8 | maintenance_plan, maintenance_activity, checklist, request_activity_type | ✅ |
| `maintenance_calendar` | 6 | planned_maintenance_activity, maintenance_plan[ro], maintenance_activity[ro], property | ✅ |
| `maintenance_condition` | 8 | planned_maintenance_activity, maintenance_plan[ro], maintenance_activity[ro], sensor, property | ✅ |
| `maintenance_interval` | 8 | planned_maintenance_activity, maintenance_plan[ro], maintenance_activity[ro], uom, property ×2 | ✅ |
| `maintenance_request` | 20 | employee, asset, location, site, department, position, incident, pma, maintenance_request, woa[ro], property, maintenance_interval | ✅ Complex but valid |
| `maintenance_order` | 2 | work_order[ro] | ✅ |
| `maintenance_order_detail` | 6 | maintenance_order[ro], maintenance_request, asset[ro] | ✅ |
| `sensor` | 9 | asset, asset_property, ~~site~~ | ❌ Remove `site` |
| `sensor_data` | 3 | sensor | ✅ |
| `service_request` | 11 | asset, site, location, work_order, incident | ✅ |

### 6.4 Purchasing & Stores (32 entities)

| Entity | Fields | Links To | Notes |
|--------|--------|----------|-------|
| `currency` | 4 | — | Standalone. ✅ |
| `unit_of_measure` | 2 | — | Standalone. ✅ |
| `item_class` | 11 | asset_class, parent item_class, uom, account | ✅ |
| `item` | 17 | item_class, account, ~~inventory_adjustment~~, vendor, asset_class, uom | ❌ Fix `inventory_adjustment_account` → link to `account` |
| `vendor` | 2 | ~~site~~ | ❌ Remove `site` |
| `reason_code` | 6 | account ×2 | ✅ |
| `store` | 4 | location, ~~site~~ | ❌ Remove `site` |
| `zone` | 4 | store, ~~site~~ | ❌ Remove `site` |
| `bin` | 6 | store, ~~site~~ | ❌ Remove `site` |
| `inventory` | 24 | workflow_states, employee, site, location, store, zone, bin, item, uom, asset | ✅ Core transaction |
| `inspection` | 6 | employee, site, inventory | ✅ |
| `purchase_request` | 12 | employee, woa, maintenance_request, site, department, cost_code | ✅ |
| `purchase_request_line` | 22 | purchase_request, item, uom, currency, account, cost_code, ~~site~~, ~~department~~, vendor | ❌ Remove `site`, `department` — inherit from PR header |
| `request_for_quotation` | 10 | purchase_request, employee ×2, vendor ×2 | ✅ |
| `rfq_line` | 6 | rfq, pr_line, item | ✅ |
| `purchase_order` | 9 | vendor, site, department, cost_code | ✅ |
| `purchase_order_line` | 13 | purchase_order, pr_line, item, ~~site~~, ~~department~~, ~~cost_code~~ | ❌ Remove `site`, `department`, `cost_code` — inherit from PO header |
| `purchase_receipt` | 13 | po_line, pr_line[ro], item[ro], location, ~~site~~, ~~department~~, ~~cost_code~~, account | ❌ Remove `site`, `department`, `cost_code` |
| `purchase_return` | 9 | inventory, item[ro], uom[ro], site, department, cost_code | ✅ Standalone return transaction |
| `inventory_adjustment` | 9 | stock_count[ro], location, store, site, account | ✅ |
| `inventory_adjustment_line` | 14 | inventory_adjustment, inventory, item, bin, zone, uom, account ×2 | ✅ |
| `stock_count` | 8 | store, site | ✅ |
| `stock_count_line` | 14 | stock_count, inventory, item, bin, zone, uom, reason_code | ✅ |
| `stock_count_task` | 5 | stock_count, users, bin, ~~site~~ | ❌ Remove `site` |
| `stock_ledger_entry` | 14 | item, store, bin, site | ✅ Audit log — site is fine |
| `item_issue` | 8 | employee, woa, site, department, cost_code | ✅ |
| `item_issue_line` | 10 | item_issue, wo_parts, wo_equipment, inventory, store, bin, zone | ✅ |
| `item_return` | 8 | employee, woa, site, department, cost_code | ✅ |
| `item_return_line` | 6 | item_return, wo_parts, wo_equipment, item | ✅ |
| `transfer` | 19 | employee, woa, inventory, labor, equipment, pr_line, site, locations, stores, bins, zones, vendor | ✅ Complex but valid |
| `transfer_receipt` | 6 | transfer, inventory, uom, location, site | ✅ |
| `sales_order` | 7 | currency, site | ✅ |
| `sales_order_item` | 10 | sales_order, item, uom, ~~site~~, department | ❌ Remove `site` |
| `putaway` | 11 | transfer, item_return_line, asset, item, site, store, bin, zone | ✅ |

### 6.5 Work Management (13 entities)

| Entity | Fields | Links To | Notes |
|--------|--------|----------|-------|
| `category_of_failure` | 4 | ~~site~~ | ❌ Remove `site` |
| `work_order` | 11 | category_of_failure, incident, site, department, cost_code | ✅ |
| `work_order_activity` | 17 | work_order, asset, position, labor, location, site, department | ✅ |
| `work_order_activity_logs` | 4 | work_order_activity | ✅ |
| `work_order_checklist` | 7 | work_order_activity, checklist, employee | ✅ |
| `work_order_checklist_detail` | 5 | work_order_checklist | ✅ |
| `work_order_labor` | 12 | work_order_activity, trade, labor | ✅ |
| `work_order_labor_assignment` | 8 | work_order_labor, labor | ✅ |
| `work_order_labor_actual_hours` | 8 | work_order_labor, ~~site~~, ~~department~~, ~~cost_code~~ | ❌ Remove all 3 — derive from WO |
| `work_order_equipment` | 11 | work_order_activity, item, equipment | ✅ |
| `work_order_equipment_assignment` | 7 | work_order_equipment, equipment | ✅ |
| `work_order_equipment_actual_hours` | 8 | work_order_equipment, ~~site~~, ~~department~~, ~~cost_code~~ | ❌ Remove all 3 — derive from WO |
| `work_order_parts` | 12 | work_order_activity, item, uom | ✅ |
| `work_order_parts_reservation` | 9 | work_order_parts, uom, inventory | ✅ |

---

## Summary of Required Fixes

### Must Fix (Wrong/Broken)

| # | Entity | Field | Issue | Action |
|---|--------|-------|-------|--------|
| 1 | `site` | `location` | Site cannot depend on Location | **Remove** `location` + `location_name` |
| 2 | `site` | `default_cost_code` | Circular with cost_code.site | **Remove** `default_cost_code` |
| 3 | `item` | `inventory_adjustment_account` | Links to `inventory_adjustment` instead of `account` | **Change** link_entity to `account` |
| 4 | `vendor` | `site` | Vendors are not site-scoped | **Remove** `site` |
| 5 | `equipment` | `pr_line_no` | Masterfile linking to transaction | **Remove** `pr_line_no` |

### Should Fix (Redundant)

| # | Entity | Field | Derive From | Action |
|---|--------|-------|-------------|--------|
| 6 | `system` | `site` | location.site | **Remove** |
| 7 | `position` | `site` | location.site | **Remove** |
| 8 | `store` | `site` | location.site | **Remove** |
| 9 | `bin` | `site` | store → location.site | **Remove** |
| 10 | `zone` | `site` | store → location.site | **Remove** |
| 11 | `disposed` | `site` | asset.site | **Remove** |
| 12 | `sensor` | `site` | asset.site | **Remove** |
| 13 | `category_of_failure` | `site` | Not site-scoped | **Remove** |
| 14 | `purchase_order_line` | `site`, `department`, `cost_code` | purchase_order | **Remove all 3** |
| 15 | `purchase_request_line` | `site`, `department` | purchase_request | **Remove both** |
| 16 | `purchase_receipt` | `site`, `department`, `cost_code` | purchase_order_line → PO | **Remove all 3** |
| 17 | `wo_labor_actual_hours` | `site`, `department`, `cost_code` | wo_labor → woa → wo | **Remove all 3** |
| 18 | `wo_equip_actual_hours` | `site`, `department`, `cost_code` | wo_equip → woa → wo | **Remove all 3** |
| 19 | `stock_count_task` | `site` | stock_count.site | **Remove** |
| 20 | `sales_order_item` | `site` | sales_order.site | **Remove** |

### Keep As-Is (Intentional Redundancy)

These transaction-level entities correctly carry `site`/`department`/`cost_code` for audit and filtering:
- `purchase_request`, `purchase_order`, `purchase_return`
- `work_order`, `work_order_activity`
- `maintenance_request`
- `item_issue`, `item_return`
- `inventory`, `inventory_adjustment`
- `stock_ledger_entry` (audit log)
- `transfer`, `transfer_receipt`
- `incident`

**Note on `purchase_request_line.cost_code`:** Keep this one if business requires line-level cost code override (different from PR header). Remove only `site` and `department`.
