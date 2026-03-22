# Maintenance Management — Entity Relationship Audit

**16 entities** in `maintenance_mgmt` module.

For masterfile-level issues (site, location, asset, etc.), see [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md).

---

## 1. Excel Sheet Order (Data Entry Sequence)

From `Maintenance_Management_Data_Validated.xlsx`:

| # | Sheet | Maps To Entity |
|---|-------|---------------|
| 1 | Maintenance Plan | `maintenance_plan` |
| 2 | Maintenance Activity | `maintenance_activity` |
| 3 | Planned Maint Activity | `planned_maintenance_activity` |
| 4 | Maintenance Calendar | `maintenance_calendar` |
| 5 | Maintenance Trade | `maintenance_trade` |
| 6 | Maintenance Equipment | `maintenance_equipment` |
| 7 | Maintenance Parts | `maintenance_parts` |
| 8 | Checklist | `checklist` |
| 9 | Checklist Details | `checklist_details` |
| 10 | Planned Maintenance Activity | `planned_maintenance_activity` (duplicate sheet) |
| 11 | Maintenance Interval | `maintenance_interval` |
| 12 | Maintenance Condition | `maintenance_condition` |
| 13 | Sensor | `sensor` |
| 14 | Sensor Data | `sensor_data` |
| 15 | Maintenance Request | `maintenance_request` |
| 16 | Maintenance Order | `maintenance_order` |
| 17 | Maintenance Order Detail | `maintenance_order_detail` |
| 18 | Maintenance Part | `maintenance_parts` (duplicate sheet) |

**Note:** Sheets 3/10 and 7/18 are duplicates.

---

## 2. Entity Dependency Map

| Entity | Depends On | Cross-Module Deps |
|--------|-----------|-------------------|
| `checklist` | — (standalone) | — |
| `checklist_details` | checklist | — |
| `maintenance_activity` | — (standalone) | — |
| `maintenance_trade` | maintenance_activity | trade (core_eam) |
| `maintenance_equipment` | maintenance_activity | equipment (asset_management) |
| `maintenance_parts` | maintenance_activity | item (purchasing_stores) |
| `maintenance_plan` | — | asset_class (asset_mgmt), manufacturer (core_eam), model (core_eam) |
| `planned_maintenance_activity` | maintenance_plan, maintenance_activity, checklist | request_activity_type (core_eam) |
| `maintenance_calendar` | planned_maintenance_activity | property (asset_mgmt) |
| `maintenance_interval` | planned_maintenance_activity | unit_of_measure (p&s), property (asset_mgmt) |
| `maintenance_condition` | planned_maintenance_activity, sensor | property (asset_mgmt) |
| `sensor` | — | asset (asset_mgmt), asset_property (asset_mgmt), site (core_eam) |
| `sensor_data` | sensor | — |
| `maintenance_request` | planned_maintenance_activity, maintenance_interval | employee, site, department (core_eam); asset, location, position, incident, property (asset_mgmt); work_order_activity (work_mgmt) |
| `maintenance_order` | — | work_order (work_mgmt) [ro] |
| `maintenance_order_detail` | maintenance_order | maintenance_request; asset (asset_mgmt) [ro] |
| `service_request` | — | asset, location, incident (asset_mgmt); site (core_eam); work_order (work_mgmt) |

---

## 3. Issues Found

### 3.1 Sensor → Site (REDUNDANT)

`sensor.json` has `site` → `site`.

Sensor already links to `asset`. Asset carries `site`. Derive from `asset.site`.

**Fix:** Remove `site` from `sensor.json`. (Also noted in [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md#summary-of-required-fixes))

---

### 3.2 Maintenance Calendar/Interval/Condition — Redundant readonly fields

All three child entities carry both `maintenance_plan [ro]` and `maintenance_activity [ro]` in addition to their real parent `planned_maintenance_activity`.

- `maintenance_calendar` → planned_maintenance_activity, maintenance_plan [ro], maintenance_activity [ro]
- `maintenance_interval` → planned_maintenance_activity, maintenance_plan [ro], maintenance_activity [ro]
- `maintenance_condition` → planned_maintenance_activity, maintenance_plan [ro], maintenance_activity [ro]

These readonly fields are **derivable** from `planned_maintenance_activity` (which links to both `maintenance_plan` and `maintenance_activity`).

**Verdict:** Acceptable as UX convenience (avoids a join to display plan/activity names in list views). But strictly speaking, redundant. Mark these as intentional audit copies if keeping.

---

### 3.3 Excel Order Issue — Calendar before Checklist

The Excel has:
- Sheet 4: Maintenance Calendar
- Sheet 8: Checklist

But `planned_maintenance_activity` (Sheet 3) depends on `checklist`. So Checklist data should come BEFORE Planned Maintenance Activity.

**Correct order:**
1. Checklist
2. Checklist Details
3. Maintenance Activity
4. Maintenance Plan
5. Planned Maintenance Activity (depends on all above)
6. Maintenance Trade/Equipment/Parts (depend on Maintenance Activity)
7. Maintenance Calendar/Interval/Condition (depend on PMA)
8. Sensor / Sensor Data
9. Maintenance Request (transaction — depends on everything above)
10. Maintenance Order / Detail (transaction — depends on MR + Work Order)

---

### 3.4 Service Request — Not in Excel

`service_request` exists as an entity but is not in the Maintenance Management Excel. It links to asset, site, location, work_order, and incident.

**Verdict:** Either it's a separate workflow entry point (like a helpdesk ticket that becomes an MR), or it's orphaned. Clarify its business purpose.

---

### 3.5 Maintenance Request — Heavy cross-module dependency

`maintenance_request` links to **12 other entities** across 4 modules:
- core_eam: employee, site, department
- asset_management: asset, location, position, incident, property
- maintenance_mgmt: planned_maintenance_activity, maintenance_interval, self (next_maintenance_request)
- work_mgmt: work_order_activity [ro]

This is expected — MR is the central transaction document. No issues, just noting the complexity.

---

### 3.6 Maintenance Order → Work Order (readonly)

`maintenance_order.json` only has 2 fields: `created_date` and `work_order [ro]`.

This entity is essentially a lightweight wrapper/grouping record. The real content is in `maintenance_order_detail` which links MRs to the MO.

**Verdict:** OK. MO groups multiple MRs into a single Work Order batch.

---

## 4. Unreferenced Entities

These maintenance_mgmt entities are **not referenced by any other entity** (no inbound links or related tabs from other entities):

| Entity | Concern |
|--------|---------|
| `sensor_data` | Child of sensor. Should be in sensor's `links` config for related tab. |
| `service_request` | Standalone. No other entity points to it. Orphan or intentional entry point. |

---

## 5. Entity Catalog

| Entity | Fields | Status | Notes |
|--------|--------|--------|-------|
| `checklist` | 2 | ✅ | Standalone |
| `checklist_details` | 3 | ✅ | Child of checklist |
| `maintenance_activity` | 2 | ✅ | Standalone template |
| `maintenance_trade` | 4 | ✅ | Activity resource |
| `maintenance_equipment` | 4 | ✅ | Activity resource |
| `maintenance_parts` | 3 | ✅ | Activity resource |
| `maintenance_plan` | 7 | ✅ | Links to asset_class, manufacturer, model |
| `planned_maintenance_activity` | 8 | ✅ | Core config: plan + activity + checklist + type |
| `maintenance_calendar` | 6 | ⚠️ | Redundant ro fields (plan, activity) |
| `maintenance_interval` | 8 | ⚠️ | Redundant ro fields (plan, activity) |
| `maintenance_condition` | 8 | ⚠️ | Redundant ro fields (plan, activity) |
| `sensor` | 9 | ❌ | Remove `site` — derive from asset |
| `sensor_data` | 3 | ✅ | Child of sensor |
| `maintenance_request` | 20 | ✅ | Central transaction. Complex but valid. |
| `maintenance_order` | 2 | ✅ | Grouping record |
| `maintenance_order_detail` | 6 | ✅ | Links MRs to MO |
| `service_request` | 11 | ❓ | Business purpose unclear. Not in Excel data. |
