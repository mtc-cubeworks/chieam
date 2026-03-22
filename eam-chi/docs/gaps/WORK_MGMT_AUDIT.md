# Work Management — Entity Relationship Audit

**14 entities** in `work_mgmt` module.

No Excel master data file exists for this module. All work management entities are **transactional** — they are created during operations, not seeded.

For masterfile-level issues, see [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md).

---

## 1. Entity Hierarchy

```
work_order
 └── work_order_activity
      ├── work_order_labor
      │    ├── work_order_labor_assignment
      │    └── work_order_labor_actual_hours
      ├── work_order_equipment
      │    ├── work_order_equipment_assignment
      │    └── work_order_equipment_actual_hours
      ├── work_order_parts
      │    └── work_order_parts_reservation
      ├── work_order_checklist
      │    └── work_order_checklist_detail
      └── work_order_activity_logs
```

Plus one standalone reference entity:
- `category_of_failure`

---

## 2. Entity Dependency Map

| Entity | Depends On (own module) | Cross-Module Deps |
|--------|------------------------|-------------------|
| `category_of_failure` | — | ~~site~~ (core_eam) |
| `work_order` | category_of_failure | incident (asset_mgmt); site, department, cost_code (core_eam) |
| `work_order_activity` | work_order | asset, position, location (asset_mgmt); labor, site, department (core_eam) |
| `work_order_activity_logs` | work_order_activity | — |
| `work_order_labor` | work_order_activity | trade, labor (core_eam) |
| `work_order_labor_assignment` | work_order_labor | labor (core_eam) |
| `work_order_labor_actual_hours` | work_order_labor | ~~site~~, ~~department~~, ~~cost_code~~ (core_eam) |
| `work_order_equipment` | work_order_activity | item (p&s); equipment (asset_mgmt) |
| `work_order_equipment_assignment` | work_order_equipment | equipment (asset_mgmt) |
| `work_order_equipment_actual_hours` | work_order_equipment | ~~site~~, ~~department~~, ~~cost_code~~ (core_eam) |
| `work_order_parts` | work_order_activity | item, unit_of_measure (p&s) |
| `work_order_parts_reservation` | work_order_parts | unit_of_measure, inventory (p&s) |
| `work_order_checklist` | work_order_activity | checklist (maint_mgmt); employee (core_eam) |
| `work_order_checklist_detail` | work_order_checklist | — |

---

## 3. Issues Found

### 3.1 Category of Failure → Site (REMOVE)

`category_of_failure.json` has `site` → `site`.

Failure categories are global definitions ("Electrical Failure", "Bearing Wear", "Corrosion"). They should not be site-scoped. If you need site-level filtering, do it through the work order's site.

**Fix:** Remove `site` from `category_of_failure.json`.

---

### 3.2 WO Labor/Equipment Actual Hours — Redundant site/dept/cost_code

Both `work_order_labor_actual_hours` and `work_order_equipment_actual_hours` carry `site`, `department`, `cost_code`.

These are fully derivable:
- actual_hours → wo_labor → work_order_activity → work_order → site/department/cost_code
- actual_hours → wo_equipment → work_order_activity → work_order → site/department/cost_code

**Fix:** Remove `site`, `department`, `cost_code` from both entities.

---

### 3.3 All WO entities are correctly hierarchical

Every entity cleanly chains back to `work_order` through its parent link. No circular references. No broken links. The hierarchy is well-structured.

---

### 3.4 Cross-module dependencies are all valid

Work management correctly references:
- **core_eam:** employee, labor, trade, site, department, cost_code
- **asset_management:** asset, position, location, equipment, incident
- **maintenance_mgmt:** checklist
- **purchasing_stores:** item, unit_of_measure, inventory

These are all upstream entities that must exist before work orders are created. No backwards dependencies.

---

## 4. Unreferenced Entities

These work_mgmt entities have **no inbound links** from any other entity:

| Entity | Expected? | Notes |
|--------|-----------|-------|
| `work_order_equipment_assignment` | Yes | Child of wo_equipment. Should be in `work_order_equipment.links` config. |
| `work_order_labor_assignment` | Yes | Child of wo_labor. Should be in `work_order_labor.links` config. |
| `work_order_parts_reservation` | Yes | Child of wo_parts. Should be in `work_order_parts.links` config. |

**Verdict:** All are expected child entities. They need `links` config on their parent to show as related tabs.

---

## 5. Entity Catalog

| Entity | Fields | Status | Notes |
|--------|--------|--------|-------|
| `category_of_failure` | 4 | ❌ | Remove `site` |
| `work_order` | 11 | ✅ | Top-level transaction |
| `work_order_activity` | 17 | ✅ | Core work item |
| `work_order_activity_logs` | 4 | ✅ | |
| `work_order_labor` | 12 | ✅ | |
| `work_order_labor_assignment` | 8 | ✅ | |
| `work_order_labor_actual_hours` | 8 | ❌ | Remove `site`, `department`, `cost_code` |
| `work_order_equipment` | 11 | ✅ | |
| `work_order_equipment_assignment` | 7 | ✅ | |
| `work_order_equipment_actual_hours` | 8 | ❌ | Remove `site`, `department`, `cost_code` |
| `work_order_parts` | 12 | ✅ | |
| `work_order_parts_reservation` | 9 | ✅ | |
| `work_order_checklist` | 7 | ✅ | |
| `work_order_checklist_detail` | 5 | ✅ | |

---

## 6. Work Order Flow

```
Maintenance Request ──→ Work Order ──→ Work Order Activity
                                        ├── Labor (trade + employee assignment + actual hours)
                                        ├── Equipment (item + equipment assignment + actual hours)
                                        ├── Parts (item + reservation + issue/return)
                                        ├── Checklist (inspection items)
                                        └── Activity Logs

Incident ──→ Work Order (also a valid entry point)
```

Work orders can originate from:
1. **Maintenance Request** (planned or emergency)
2. **Incident** (reactive)

Both paths are correctly modeled. The WO → WOA → resources hierarchy is clean.
