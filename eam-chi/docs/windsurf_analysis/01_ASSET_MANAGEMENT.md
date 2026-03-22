# Asset Management Module — Business Logic Analysis

## Source Files (Frappe)
- `asset_management/doctype/asset/asset.py`
- `asset_management/doctype/asset_class/asset_class.py`
- `asset_management/doctype/asset_class_property/asset_class_property.py`
- `asset_management/doctype/asset_position/asset_position.py`
- `asset_management/doctype/asset_property/asset_property.py`
- `asset_management/doctype/asset_class_availability/asset_class_availability.py`
- `asset_management/doctype/position/position.py`

## Target Files (FastAPI)
- `modules/asset_management/hooks.py`
- `modules/asset_management/apis/asset.py`
- `modules/asset_management/apis/asset_class_hooks.py`
- `modules/asset_management/apis/position.py`
- `modules/asset_management/apis/breakdown.py`
- `modules/asset_management/apis/disposed.py`

---

## 1. Asset — Workflow Actions (`check_asset_state`)

| Action (Frappe) | Slug (FastAPI) | Creates | FastAPI Status |
|---|---|---|---|
| Failed Inspection | `failed_inspection` | Simple transition | ✅ Implemented |
| Complete | `complete` | Simple transition | ✅ Implemented |
| Finish Repair | `finish_repair` | Simple transition | ✅ Implemented |
| Retire Asset | `retire_asset` | Simple transition | ✅ Implemented |
| Decommission | `decommission` | Simple transition | ✅ Implemented |
| Recommission | `recommission` | Simple transition | ✅ Implemented |
| Inspect Asset | `inspect_asset` | WOA + MR (auto-approve) | ✅ Implemented |
| Maintain Asset | `maintain_asset` | WOA + MR (auto-approve) | ✅ Implemented |
| Internal Repair | `internal_repair` | WOA + MR (auto-approve) | ✅ Implemented |
| Send to Vendor | `send_to_vendor` | WOA + MR (auto-approve) | ✅ Implemented |
| Install Asset | `install_asset` | Bypass: AssetPosition / No bypass: WOA+MR | ✅ Implemented |
| Commission | `commission` | AssetPosition | ✅ Implemented |
| Putaway | `putaway` | Putaway record | ✅ Implemented |
| Issue Equipment | `issue_equipment` | ItemIssue record | ✅ Implemented |
| Remove Asset | `remove_asset` | Close AssetPosition | ✅ Implemented |
| Dispose | `dispose` | Disposed record | ✅ Implemented |

## 2. Asset — Post-Save (`generate_asset_prop`)

| Logic | FastAPI Status |
|---|---|
| Inherit Asset Class Properties to Asset Properties | ✅ `populate_asset_properties()` |
| Auto-create Inventory when bypass=True | ✅ `provision_inventory()` |
| Sync asset_tag to Inventory | ✅ `provision_inventory()` |

## 3. Asset Class — Post-Save (`populate_asset_class_prop_and_maint_plan`)

| Logic | FastAPI Status |
|---|---|
| Copy Asset Class Properties from parent | ✅ `populate_asset_class_prop_and_maint_plan()` |
| Copy Maintenance Plans from parent | ❌ **NOT IMPLEMENTED** — marked as "(Future)" |
| Copy Planned Maintenance Activities from parent's plans | ❌ **NOT IMPLEMENTED** — marked as "(Future)" |
| Add default properties from Function Config | ❌ **NOT IMPLEMENTED** — marked as "(Future)" |

## 4. Asset Class Property — Post-Save (`populate_asset_prop`)

| Logic | FastAPI Status |
|---|---|
| When new ACP created, propagate to all Assets of that class | ❌ **NOT IMPLEMENTED** |

## 5. Asset Position — Post-Save (`update_asset_position`)

| Logic | FastAPI Status |
|---|---|
| If date_removed set: clear Position.current_asset, apply "Remove Asset" workflow to Asset | ❌ **NOT IMPLEMENTED** |
| If no date_removed: set Position.current_asset, update Asset location/system/site/position, apply "Install Asset" workflow | ❌ **NOT IMPLEMENTED** |

## 6. Asset Property — Post-Save (`get_asset_class_prop_default_value` + `update_asset_prop_value`)

| Logic | FastAPI Status |
|---|---|
| When property_value saved, look up default from Asset Class Property and update | ❌ **NOT IMPLEMENTED** |

## 7. Asset Class Availability — Post-Save (`get_available_reserved_capacity`)

| Logic | FastAPI Status |
|---|---|
| Calculate available/reserved capacity from Equipment Availability Details | ❌ **NOT IMPLEMENTED** |

## 8. Position — Server Actions

| Action | Creates | FastAPI Status |
|---|---|---|
| `create_install_asset` | WOA + MR for install | ✅ Implemented |
| `create_swap_asset` | WOA + MR for remove + install | ✅ Implemented |
| `create_decommission_asset` | WOA + MR for decommission | ✅ Implemented |

---

## Gaps to Implement

1. **Asset Class post-save**: Add Maintenance Plan + PMA inheritance from parent
2. **Asset Class Property post-save**: Propagate new property to all Assets of that class
3. **Asset Position post-save**: Update Position.current_asset and Asset fields, apply workflow
4. **Asset Property post-save**: Look up default value from ACP
5. **Asset Class Availability post-save**: Calculate available/reserved capacity
