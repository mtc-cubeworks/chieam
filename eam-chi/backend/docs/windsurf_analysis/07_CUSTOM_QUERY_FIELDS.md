# Custom Query Fields - Client Script Analysis

Extracted from Frappe client scripts at `ci_eam/frontend/src/client-scripts/forms/`.
These `setFieldQuery` calls define dynamic filtering on Link fields that must be
implemented as filtered endpoints in the FastAPI backend.

---

## Core EAM

### Department
| Field | Filters | Trigger |
|-------|---------|---------|
| *(commented out)* `cost_code` | `{ site: employee.site }` | onLoad |

### Employee
*(No custom queries)*

---

## Asset Management

### Asset
| Field | Filters | Trigger |
|-------|---------|---------|
| `system` | `{ location: form.location }` | onLoad, onFieldChange(`location`) |
| `model` | `{ manufacturer: form.manufacturer }` | onLoad, onFieldChange(`manufacturer`) |
| `department` | `{ site_id: form.site }` | onLoad, onFieldChange(`site`) |

**Server calls:** `get_description(doctype='Location', doc_id)` → prefills `site`

### Asset Class
| Field | Filters | Trigger |
|-------|---------|---------|
| `parent_asset_class_id` | `{ equipment: form.equipment }` | onLoad, onFieldChange(`equipment`) |

### Position
**Server calls:** `get_description(doctype='Location', doc_id)` → prefills `site`

### Equipment
| Field | Filters | Trigger |
|-------|---------|---------|
| `inventory` | **Custom query:** `search_equipment_query` with `{ site: currentSite }` | onLoad |

**Server calls:** `get_description(doctype='Inventory'|'Purchase Request Line', doc_id)` → prefills `description`

---

## Work Management

### Work Order Activity
| Field | Filters | Trigger |
|-------|---------|---------|
| `work_item` | `{ location: form.location }` | onLoad, onFieldChange(`location`) |
| `activity_type` | `{ menu: 'Asset', state: asset.workflow_state }` | onLoad (when work_item set), onFieldChange(`work_item`) |

**Server calls:**
- `get_asset_info(doc)` → prefills `location`, `site`, `department` + filters `activity_type`
- Fetches Work Order to prefill `site`, `department` for new docs

### Work Order Labor (Assignment)
| Field | Filters | Trigger |
|-------|---------|---------|
| `labor` | **Custom query:** `search_employee_query` with `{ trade, work_order_activity, site: currentSite }` | onLoad, onFieldChange(`trade`) |

### Work Order Equipment (Assignment)
| Field | Filters | Trigger |
|-------|---------|---------|
| `item` | `{ is_equipment: true }` | onLoad |
| `equipment` | **Custom query:** `search_equipment_query` with `{ item, work_order_activity, site: currentSite }` | onLoad, onFieldChange(`item`) |

### Work Order Parts
**Server calls:** `get_description(doctype='Item', doc_id)` → prefills `item_name`, `unit_of_measure`, `total_actual_qty`, `total_avail_qty`

### Work Order Checklist
*(No custom queries)*

---

## Maintenance Management

### Maintenance Request
| Field | Filters | Trigger |
|-------|---------|---------|
| `asset` | **Custom query:** `get_filtered_assets_for_maintenance_request` with `{ planned_maintenance_activity }` | onLoad, onFieldChange(`planned_maintenance_activity`) |
| `request_type` | `{ menu: 'Asset', state: asset.workflow_state }` | onLoad (when asset set), onFieldChange(`asset`) |
| `department` | `{ site_id: form.site }` | onLoad, onFieldChange(`site`) |

**Server calls:** `get_asset_info(doc)` → prefills `location`, `site`, `department`

### Maintenance Order
*(No custom queries — UI behavior only: disable edit/delete when work_order exists)*

### Maintenance Order Detail
| Field | Filters | Trigger |
|-------|---------|---------|
| `maint_req` | `{ workflow_state: 'Approved' }` | onLoad, onFieldChange |

**Server calls:** `get_maint_req_info(doc)` → prefills `asset`, `due_date`, `resource_availability_status`

### Maintenance Calendar
| Field | Filters | Trigger |
|-------|---------|---------|
| `planned_maintenance_activity` | `{ maintenance_schedule: 'Calendar Based' }` | onLoad, onFieldChange |
| `last_maintenance_date_property` | **Custom query:** `search_property_query` with `{ planned_maintenance_activity, site: currentSite }` | onLoad, onFieldChange(`planned_maintenance_activity`) |

### Maintenance Condition
| Field | Filters | Trigger |
|-------|---------|---------|
| `planned_maintenance_activity` | `{ maintenance_schedule: 'Condition Based' }` | onLoad, onFieldChange |
| `threshold_property` | **Custom query:** `search_property_query` with `{ planned_maintenance_activity, site: currentSite }` | onLoad, onFieldChange(`planned_maintenance_activity`) |

### Maintenance Interval
| Field | Filters | Trigger |
|-------|---------|---------|
| `planned_maintenance_activity` | `{ maintenance_schedule: 'Interval Based' }` | onLoad, onFieldChange |
| `running_interval_property` | **Custom query:** `search_property_query` with `{ planned_maintenance_activity, site: currentSite }` | onLoad, onFieldChange(`planned_maintenance_activity`) |
| `last_interval_property` | **Custom query:** `search_property_query` with `{ planned_maintenance_activity, site: currentSite }` | onLoad, onFieldChange(`planned_maintenance_activity`) |

### Maintenance Equipment
| Field | Filters | Trigger |
|-------|---------|---------|
| `asset_class` | `{ equipment: 1 }` | onLoad, onFieldChange(`asset_class`) |

### Maintenance Parts
| Field | Filters | Trigger |
|-------|---------|---------|
| `item` | `{ item_type: ['in', ['Inventory Item', 'Non Inventory Item']] }` | onLoad, onFieldChange(`item`) |

### Maintenance Plan
| Field | Filters | Trigger |
|-------|---------|---------|
| `model` | `{ manufacturer: form.manufacturer }` | onLoad, onFieldChange(`manufacturer`) |

---

## Purchasing & Stores

### Inventory
| Field | Filters | Trigger |
|-------|---------|---------|
| `location` | `{ site: employee.site }` | onLoad (when assigned_to set), onFieldChange(`assigned_to`) |
| `store_location` | `{ location: form.location }` | onLoad, onFieldChange(`location`) |
| `zone` | `{ store: form.store_location }` | onLoad, onFieldChange(`store_location`) |
| `bin_location` | `{ store: form.store_location }` | onLoad, onFieldChange(`store_location`) |

**Server calls:** `get_description(doctype='Employee', doc_id)` → gets `site`; `get_item_info(doc)` → gets `uom`

### Item Issue
| Field | Filters | Trigger |
|-------|---------|---------|
| `work_order_activity` | `{ workflow_state: ['!=', 'Closed'] }` | onLoad |
| `cost_code` | `{ site: wo_activity.site }` | onLoad (when WOA set), onFieldChange(`work_order_activity`, `site`) |

### Item Issue Line
| Field | Filters | Trigger |
|-------|---------|---------|
| `work_order_parts` | `{ work_order_activity: parent.work_order_activity }` | onLoad (when issue_type='WO Parts Issue') |
| `work_order_equipment` | `{ work_order_activity: parent.work_order_activity }` | onLoad (when issue_type='WO Equipment Issue') |
| `inventory` | `{ item: wo_parts.item, inactive: 0, site: form.site }` | onFieldChange(`work_order_parts`) |
| `inventory` | `{ item: wo_equip.item, inactive: 0, site: currentSite }` | onFieldChange(`work_order_equipment`) |

### Item Return
| Field | Filters | Trigger |
|-------|---------|---------|
| `work_order_activity` | `{ workflow_state: ['!=', 'Closed'] }` | onLoad |
| `cost_code` | `{ site: wo_activity.site }` | onLoad (when WOA set), onFieldChange(`work_order_activity`, `site`) |

### Item Return Line
| Field | Filters | Trigger |
|-------|---------|---------|
| `work_order_parts` | `{ work_order_activity: parent.work_order_activity }` | onLoad (when return_type='WO Parts Issue') |
| `work_order_equipment` | `{ work_order_activity: parent.work_order_activity }` | onLoad (otherwise) |

### Purchase Request
*(No active custom queries — cost_code filter by site commented out)*

### Purchase Request Line
**Server calls:** `get_item_info(doc)` → prefills `vendor`, `unit_of_measure`, `unit_cost`, `account_code`, `description`

**Client-side calc:** `total_line_amount = qty_required * unit_cost`

### Purchase Receipt
*(See purchasing_stores module — handled separately)*

### Store
**Server calls:** `get_description(doctype='Location', doc_id)` → prefills `site`

### Bin
**Server calls:** `get_description(doctype='Store', doc_id)` → prefills `site`

### Zone
*(No custom queries in client script)*

### Transfer
**Server calls:** `get_description(doctype='Inventory'|'Labor'|'Equipment', doc_id)` → prefills `item_to_transfer`, `from_location`

### Stock Count / Stock Count Line / Stock Count Task
*(See purchasing_stores module — handled separately)*

---

## Summary: Custom Query Endpoints Needed in FastAPI

These are the **server-side custom query functions** referenced by client scripts that need FastAPI endpoint equivalents:

| Frappe Function | Module | Purpose |
|----------------|--------|---------|
| `search_employee_query` | work_mgmt | Filter employees by trade, WOA, site |
| `search_equipment_query` (work_order_equipment) | work_mgmt | Filter equipment by item, WOA, site |
| `search_equipment_query` (equipment) | asset_mgmt | Filter equipment inventory by site |
| `search_property_query` | asset_mgmt | Filter properties by planned_maintenance_activity, site |
| `get_filtered_assets_for_maintenance_request` | maintenance_mgmt | Filter assets by planned_maintenance_activity |
| `get_asset_info` | asset_mgmt | Get asset location/site/department/workflow_state |
| `get_item_info` | purchasing | Get item vendor/uom/cost/description |
| `get_maint_req_info` | maintenance_mgmt | Get MR asset/due_date/resource_availability_status |
| `get_description` | core (generic) | Get description/site from any entity by ID |
| `get_default_property` | core_eam | Get default property from Function Config |
