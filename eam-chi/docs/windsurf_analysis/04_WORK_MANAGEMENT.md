# Work Management Module — Business Logic Analysis

## Source Files (Frappe)
- `work_management/doctype/work_order/work_order.py`
- `work_management/doctype/work_order_activity/work_order_activity.py`
- `work_management/doctype/work_order_checklist/work_order_checklist.py`
- `work_management/doctype/work_order_labor/work_order_labor.py`

## Target Files (FastAPI)
- `modules/work_mgmt/hooks.py`
- `modules/work_mgmt/apis/work_order.py`
- `modules/work_mgmt/apis/work_order_activity.py`
- `modules/work_mgmt/apis/work_order_activity_actions.py`
- `modules/work_mgmt/apis/work_order_parts.py`
- `modules/work_mgmt/apis/work_order_labor_assignment.py`
- `modules/work_mgmt/apis/work_order_equipment_assignment.py`

---

## 1. Work Order — Workflow (`check_wo_order_state`)

| Action | Logic | FastAPI Status |
|---|---|---|
| Approve | Always allowed | ✅ Implemented |
| Start | All WOAs must be "Ready"; auto-start each WOA | ✅ Validation implemented; ❌ **Missing**: auto-apply "Start Activity" to each WOA |
| Complete | All WOAs must be "Completed" or "Closed" | ✅ Implemented |
| Reopen | Always allowed | ✅ Implemented |

**Gap**: On "Start", Frappe iterates all WOAs and applies `custom_apply_workflow(wo_activity, 'Start Activity', True)`. FastAPI only validates but doesn't cascade the state change.

## 2. Work Order Activity — Workflow (`check_wo_activity_state`)

| Action | Logic | FastAPI Status |
|---|---|---|
| Allocate | Validate labor/equip/parts assigned (PMA-aware) | ✅ Implemented |
| Start Activity | Start parent WO if Approved; apply "Maintain Asset" to Asset if applicable | ✅ Partial — validation only, no WO cascade |
| Complete | Complex: update MR closed_date, update Asset Properties, install/uninstall position, apply asset workflow | ✅ Mostly implemented |
| Reopen | Reopen MR + WO | ✅ Implemented |
| Close | Validate: activity logs exist, parts issued, equip/labor actual hours logged | ✅ Implemented |

**Gaps in Complete handler:**
- ✅ MR closed_date update
- ✅ Install/Uninstall asset position
- ❌ **Missing**: Update Asset Property `property_value` with formatted date when `maint_req.property` is set
- ❌ **Missing**: Update Asset Property for `maintenance_interval_property` with `running_interval_value`
- ❌ **Missing**: "Maintain Asset" complete logic — if `does_it_need_repair` is false, apply "Complete" to asset; set `need_repair` on asset
- ❌ **Missing**: "Retire Asset" with position — uninstall position before retiring

## 3. Work Order Activity — Post-Save (`create_wo_labor`)

| Logic | FastAPI Status |
|---|---|
| When `assigned_to` is set, create WO Labor record with trade from Trade Labor | ✅ `create_wo_labor_on_save()` |

## 4. Work Order Activity — Server Actions

| Action | Logic | FastAPI Status |
|---|---|---|
| `create_maint_request` | Create MR from WOA, auto-advance to approved | ❌ **NOT IMPLEMENTED** |
| `create_transfer` | Create Transfer record (Labor/Equipment/Inventory type) | ❌ **NOT IMPLEMENTED** |
| `generate_templated_pma` | Create Maintenance Activity + Trade + Equipment + Parts + PMA from WOA data | ❌ **NOT IMPLEMENTED** |
| `update_asset_status` | For Inspection: fail/retire asset based on workflow state | ❌ **NOT IMPLEMENTED** |
| `creation_install_asset` | For Inspection: create install MR if asset is "Receiving" | ❌ **NOT IMPLEMENTED** |
| `creation_replace_asset` | For Inspection: create replace + install MRs | ❌ **NOT IMPLEMENTED** |
| `putaway_asset` | For Inspection: apply "Putaway" workflow to asset | ❌ **NOT IMPLEMENTED** |

## 5. Work Order Checklist — Post-Save (`create_checklist_dtl`)

| Logic | FastAPI Status |
|---|---|
| When WO Checklist created with checklist link, auto-create WO Checklist Detail from Checklist Details | ❌ **NOT IMPLEMENTED** |

## 6. Work Order Labor — Post-Save

| Logic | FastAPI Status |
|---|---|
| `update_wo_labor_lead`: Ensure only one lead per WOA; first labor is auto-lead | ❌ **NOT IMPLEMENTED** |
| `assign_wo_labor`: Assign WOA to employee user via Labor → Employee → User chain | ❌ **NOT IMPLEMENTED** (Frappe-specific assign_to pattern) |

## 7. Work Order Labor — Workflow (`check_wo_labor_state`)

| Action | Logic | FastAPI Status |
|---|---|---|
| Start | All assignments must be "In Progress"; auto-start WOA if "Scheduled" | ❌ **NOT IMPLEMENTED** |
| Complete | All assignments must be "Complete" | ❌ **NOT IMPLEMENTED** |

## 8. Work Order Labor — `update_wolabor_labor_avail`

| Logic | FastAPI Status |
|---|---|
| Update Trade Availability (decrement available, increment reserved) | ❌ **NOT IMPLEMENTED** |
| Update Labor Availability Details (mark hours as "Reserved") | ❌ **NOT IMPLEMENTED** |
| Create Purchase Receipt for contractor labor | ❌ **NOT IMPLEMENTED** |

---

## Gaps to Implement (Priority Order)

1. **WO Start cascade**: Apply "Start Activity" to all WOAs when WO starts
2. **WOA Complete - asset property updates**: Update property_value and maintenance_interval
3. **WOA Complete - maintain asset logic**: Handle does_it_need_repair, need_repair flag
4. **WO Labor post-save**: Lead management + assignment
5. **WO Checklist post-save**: Auto-create checklist details
6. **WOA server actions**: create_maint_request, create_transfer, generate_templated_pma, update_asset_status, etc.
7. **WO Labor workflow**: Start/Complete validation
8. **WO Labor availability update**: Trade/Labor availability reservation
