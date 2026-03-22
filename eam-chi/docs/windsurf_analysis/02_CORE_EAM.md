# Core EAM Module — Business Logic Analysis

## Source Files (Frappe)
- `core_enterprise_asset_management/doctype/employee_site/employee_site.py`
- `core_enterprise_asset_management/doctype/trade_availability/trade_availability.py`

## Target Files (FastAPI)
- `modules/core_eam/hooks.py` (exists but empty — no hooks registered)

---

## 1. Employee Site — Post-Save (`populate_site_field`)

**Frappe Logic:**
When an Employee Site record is created, the Employee's `site` child table is updated to include the new site. This is a Frappe child-table pattern where Employee has a child table of sites.

**FastAPI Equivalent:**
In the FastAPI system, Employee does not have a child table for sites. The Employee Site entity is a standalone link table (`employee_site` table with `employee` and `site` FK columns). The Frappe logic of appending to a child table does not directly apply. However, we should still validate that the employee and site exist.

| Logic | FastAPI Status |
|---|---|
| Validate employee and site exist on save | ❌ **NOT IMPLEMENTED** |
| (Frappe-specific) Append site to Employee child table | N/A — different data model |

## 2. Employee Site — Post-Delete (`remove_site_field`)

**Frappe Logic:**
When an Employee Site record is deleted, remove the site from the Employee's `site` child table.

**FastAPI Equivalent:**
Same as above — the child table pattern doesn't apply. The delete of the `employee_site` row is sufficient.

| Logic | FastAPI Status |
|---|---|
| (Frappe-specific) Remove site from Employee child table | N/A — different data model |

## 3. Trade Availability — Post-Save (`get_available_reserved_capacity`)

**Frappe Logic:**
When a Trade Availability record is saved, calculate available and reserved capacity by:
1. Get all Trade Labor records for the trade
2. For each labor, check Labor Availability for the date
3. For each Labor Availability, check Labor Availability Details for the hour
4. Count Available and Reserved statuses
5. Update the Trade Availability record with calculated values

| Logic | FastAPI Status |
|---|---|
| Calculate available/reserved from Labor Availability Details | ❌ **NOT IMPLEMENTED** |

---

## Gaps to Implement

1. **Trade Availability post-save**: Calculate available/reserved capacity from Labor Availability Details
2. **Employee Site**: Minimal — just validation hooks (data model differs from Frappe)
