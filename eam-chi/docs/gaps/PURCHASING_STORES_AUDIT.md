# Purchasing & Stores — Entity Relationship Audit

**32 entities** in `purchasing_stores` module.

For masterfile-level issues (site, location, asset, etc.), see [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md).

---

## 1. Excel Sheet Order (Data Entry Sequence)

From `Purchasing_And_Stores_Data.xlsx`:

| # | Sheet | Maps To Entity |
|---|-------|---------------|
| 1 | Vendor | `vendor` |
| 2 | Item Class | `item_class` |
| 3 | Item | `item` |

**Only 3 sheets.** The rest of the 32 entities are transactional and not seeded via master data import.

---

## 2. Entity Grouping

### Masterfile / Reference (created once, reused)
- `currency`
- `unit_of_measure`
- `vendor`
- `item_class`
- `item`
- `reason_code`
- `store`
- `zone`
- `bin`

### Transaction Documents (created during operations)
- `purchase_request` → `purchase_request_line`
- `request_for_quotation` → `rfq_line`
- `purchase_order` → `purchase_order_line`
- `purchase_receipt`
- `purchase_return`
- `item_issue` → `item_issue_line`
- `item_return` → `item_return_line`
- `transfer` → `transfer_receipt`
- `putaway`
- `sales_order` → `sales_order_item`
- `stock_count` → `stock_count_line`, `stock_count_task`
- `inventory_adjustment` → `inventory_adjustment_line`
- `inspection`

### Core Records
- `inventory` (central stock ledger record)
- `stock_ledger_entry` (immutable audit trail)

---

## 3. Entity Dependency Map

| Entity | Depends On | Cross-Module Deps |
|--------|-----------|-------------------|
| `currency` | — (standalone) | — |
| `unit_of_measure` | — (standalone) | — |
| `vendor` | ~~site~~ | site (core_eam) — **should remove** |
| `item_class` | parent item_class (self), uom | asset_class (asset_mgmt), account (core_eam) |
| `item` | item_class, ~~inventory_adjustment~~, vendor, uom | asset_class (asset_mgmt), account (core_eam) |
| `reason_code` | — | account (core_eam) ×2 |
| `store` | location | location (asset_mgmt), ~~site~~ (core_eam) |
| `zone` | store | ~~site~~ (core_eam) |
| `bin` | store | ~~site~~ (core_eam) |
| `inventory` | item, uom, asset, store, zone, bin, location | site, employee (core_eam); asset (asset_mgmt) |
| `purchase_request` | employee, site, dept, cost_code | woa (work_mgmt), mr (maint_mgmt) |
| `purchase_request_line` | purchase_request, item, uom, vendor, currency | account, cost_code, ~~site~~, ~~dept~~ (core_eam) |
| `request_for_quotation` | purchase_request, vendor | employee (core_eam) |
| `rfq_line` | rfq, pr_line, item | — |
| `purchase_order` | vendor, site, dept, cost_code | — |
| `purchase_order_line` | po, pr_line, item | ~~site~~, ~~dept~~, ~~cost_code~~ (core_eam) |
| `purchase_receipt` | po_line | location (asset_mgmt); ~~site~~, ~~dept~~, ~~cost_code~~, account (core_eam) |
| `purchase_return` | inventory, item, uom | site, dept, cost_code (core_eam) |
| `item_issue` | employee, woa | site, dept, cost_code (core_eam) |
| `item_issue_line` | item_issue, inventory, store, bin, zone | wo_parts, wo_equipment (work_mgmt) |
| `item_return` | employee, woa | site, dept, cost_code (core_eam) |
| `item_return_line` | item_return, item | wo_parts, wo_equipment (work_mgmt) |
| `transfer` | inventory, employee | labor, equipment (cross-module); site, locations, stores, bins, zones, vendor, woa, pr_line |
| `transfer_receipt` | transfer, inventory, uom | location (asset_mgmt), site (core_eam) |
| `putaway` | transfer, item_return_line, item | asset (asset_mgmt); site, store, bin, zone |
| `sales_order` | currency | site (core_eam) |
| `sales_order_item` | sales_order, item, uom | ~~site~~, dept (core_eam) |
| `stock_count` | store | site (core_eam) |
| `stock_count_line` | stock_count, inventory, item, bin, zone, uom, reason_code | — |
| `stock_count_task` | stock_count, bin | users (system), ~~site~~ (core_eam) |
| `inventory_adjustment` | stock_count [ro], location, store | site, account (core_eam) |
| `inventory_adjustment_line` | inv_adjustment, inventory, item, bin, zone, uom | account (core_eam) ×2 |
| `inspection` | inventory | employee, site (core_eam) |
| `stock_ledger_entry` | item, store, bin | site (core_eam) |

---

## 4. Issues Found

### 4.1 Item → Inventory Adjustment (WRONG LINK)

`item.json` field `inventory_adjustment_account` links to `inventory_adjustment` entity.

This is a GL account field. It should link to `account`.

**Fix:** Change `link_entity` from `inventory_adjustment` to `account`. (Also in [ENTITY_RELATIONSHIP_AUDIT.md](./ENTITY_RELATIONSHIP_AUDIT.md#21-site--location-wrong-direction))

---

### 4.2 Vendor → Site (REMOVE)

Vendors are external companies. Not site-scoped.

**Fix:** Remove `site` from `vendor.json`.

---

### 4.3 Store / Zone / Bin → Site (REDUNDANT)

- `store` has `location` + `site`. Site derivable from `location.site`.
- `zone` has `store` + `site`. Site derivable from `store → location.site`.
- `bin` has `store` + `site`. Same path.

**Fix:** Remove `site` from all three.

---

### 4.4 PO Line / PR Line / Purchase Receipt — Redundant site/dept/cost_code

These child/line entities duplicate header-level fields:

| Entity | Redundant Fields | Inherits From |
|--------|-----------------|---------------|
| `purchase_order_line` | site, department, cost_code | `purchase_order` header |
| `purchase_request_line` | site, department | `purchase_request` header |
| `purchase_receipt` | site, department, cost_code | `purchase_order_line → purchase_order` |

**Note on `purchase_request_line.cost_code`:** Could be intentional if lines can have different cost codes than the PR header. If so, document that intent.

**Fix:** Remove redundant fields. Lines inherit from parent document.

---

### 4.5 WO Actual Hours entities — Redundant site/dept/cost_code

`work_order_labor_actual_hours` and `work_order_equipment_actual_hours` both carry `site`, `department`, `cost_code`. These are derivable: actual_hours → wo_labor → woa → wo → site/dept/cost_code.

**Fix:** Remove all 3 from both entities.

---

### 4.6 Stock Count Task → Site (REDUNDANT)

Derivable from `stock_count.site`.

**Fix:** Remove `site`.

---

### 4.7 Sales Order Item → Site (REDUNDANT)

Derivable from `sales_order.site`.

**Fix:** Remove `site`.

---

### 4.8 Sales Order Item has `department` but Sales Order doesn't

`sales_order_item` has `department` but `sales_order` (parent) does not. Either:
- Add `department` to `sales_order` (if dept-level tracking matters), or
- Remove `department` from `sales_order_item` (if it doesn't)

---

## 5. Unreferenced Entities

These purchasing_stores entities have **no inbound links** from any other entity:

| Entity | Expected? | Notes |
|--------|-----------|-------|
| `inspection` | Yes | Standalone quality check record. Could add to `inventory.links` config. |
| `item_issue_line` | Yes | Child of `item_issue`. Should be in `item_issue.links` config. |
| `rfq_line` | Yes | Child of `rfq`. Should be in `request_for_quotation.links` config. |
| `sales_order_item` | Yes | Child of `sales_order`. Should be in `sales_order.links` config. |
| `stock_count_line` | Yes | Child of `stock_count`. Should be in `stock_count.links` config. |
| `stock_count_task` | Yes | Child of `stock_count`. Should be in `stock_count.links` config. |
| `stock_ledger_entry` | Yes | Audit trail. Could add to `item.links` or `inventory.links` config. |
| `transfer_receipt` | Yes | Child of `transfer`. Should be in `transfer.links` config. |

**Verdict:** All are expected child/detail entities. They need `links` config on their parent entity JSON to show as related tabs. Missing `links` config means they won't appear in the UI.

---

## 6. Procurement Flow

```
Purchase Request → RFQ → Purchase Order → Purchase Receipt → Inventory
       ↑                                                        ↓
  (from WO Activity                                     Item Issue/Return
   or Maint Request)                                    Transfer / Putaway
                                                        Stock Count → Adj
```

This flow is correctly modeled. PR Lines carry forward through RFQ Lines → PO Lines → Receipt.

---

## 7. Entity Catalog

| Entity | Fields | Status | Notes |
|--------|--------|--------|-------|
| `currency` | 4 | ✅ | Standalone |
| `unit_of_measure` | 2 | ✅ | Standalone |
| `vendor` | 2 | ❌ | Remove `site` |
| `item_class` | 11 | ✅ | Tree entity |
| `item` | 17 | ❌ | Fix `inventory_adjustment_account` link |
| `reason_code` | 6 | ✅ | |
| `store` | 4 | ❌ | Remove `site` |
| `zone` | 4 | ❌ | Remove `site` |
| `bin` | 6 | ❌ | Remove `site` |
| `inventory` | 24 | ✅ | Central stock record |
| `purchase_request` | 12 | ✅ | |
| `purchase_request_line` | 22 | ❌ | Remove `site`, `department` |
| `request_for_quotation` | 10 | ✅ | |
| `rfq_line` | 6 | ✅ | |
| `purchase_order` | 9 | ✅ | |
| `purchase_order_line` | 13 | ❌ | Remove `site`, `department`, `cost_code` |
| `purchase_receipt` | 13 | ❌ | Remove `site`, `department`, `cost_code` |
| `purchase_return` | 9 | ✅ | Standalone return transaction |
| `item_issue` | 8 | ✅ | |
| `item_issue_line` | 10 | ✅ | |
| `item_return` | 8 | ✅ | |
| `item_return_line` | 6 | ✅ | |
| `transfer` | 19 | ✅ | Complex but valid |
| `transfer_receipt` | 6 | ✅ | |
| `putaway` | 11 | ✅ | |
| `sales_order` | 7 | ✅ | |
| `sales_order_item` | 10 | ⚠️ | Remove `site`; clarify `department` |
| `stock_count` | 8 | ✅ | |
| `stock_count_line` | 14 | ✅ | |
| `stock_count_task` | 5 | ❌ | Remove `site` |
| `inventory_adjustment` | 9 | ✅ | |
| `inventory_adjustment_line` | 14 | ✅ | |
| `inspection` | 6 | ✅ | |
| `stock_ledger_entry` | 14 | ✅ | Audit log — site is fine |
