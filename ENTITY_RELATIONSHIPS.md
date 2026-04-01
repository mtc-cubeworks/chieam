# EAM-CHI — Entity Relationships & Data Model

**Date:** March 24, 2026
**System:** Enterprise Asset Management — CHI & ITBA
**Version:** 1.0

---

## Executive Summary

The EAM-CHI system comprises **159 entity models** across **5 functional modules**, connected by **250+ foreign key relationships** that form a deeply integrated data fabric. This document maps every entity-to-entity relationship, grouped by module, with cross-module dependencies highlighted.

---

## 1. Module Architecture Overview

| Module | Entities | Scope |
|--------|----------|-------|
| **Core EAM** | 31 | Organizations, sites, employees, labor, departments, cost codes, accounts, schedules |
| **Asset Management** | 29 | Assets, locations, equipment, meters, warranties, transfers, incidents, positions |
| **Maintenance Management** | 22 | PM plans, inspections, failure analysis, condition monitoring, maintenance requests |
| **Purchasing & Stores** | 37 | Purchase requests, POs, receipts, inventory, items, vendors, invoices, stock counts |
| **Work Management** | 20 | Work orders, activities, labor, equipment, parts, job plans, safety permits, tools |

---

## 2. Core EAM Module — Relationships

The Core EAM module acts as the **foundation layer** — almost every other entity references it.

### Organization → Site → Department Hierarchy

```
Organization
  └── Site (organization → organization.id)
        ├── site_manager → employee.id
        ├── default_cost_code → cost_code.id
        ├── location → location.id
        └── Department (site → site.id)
              ├── department_manager → employee.id
              ├── default_cost_code → cost_code.id
              ├── overhead_expense_account → account.id
              └── labor_expense_account_overwrite → account.id
```

### Employee & Labor

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Employee | user | Users | Employee → User account |
| Employee | reports_to | Employee | Self-referential supervisor hierarchy |
| Employee Site | employee | Employee | Employee ↔ Site assignment |
| Employee Site | site | Site | Multi-site assignment |
| Employee Site | department | Department | Employee department at site |
| Labor | employee | Employee | Labor resource → Employee |
| Labor | labor_group | Labor Group | Labor group membership |
| Labor | contractor | Contractor | External contractor link |
| Labor | location | Location | Home location |
| Trade Labor | trade | Trade | Trade skill |
| Trade Labor | labor | Labor | Labor with trade |
| Leave Application | labor | Labor | Leave for labor resource |
| Leave Application | leave_type | Leave Type | Type of leave |

### Financial & Scheduling

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Cost Code | site | Site | Site-specific cost code |
| Annual Budget | cost_code | Cost Code | Budget per cost code |
| Holiday | applicable_to_labor_grp | Labor Group | Holiday for labor group |
| Holiday | specific_labor | Labor | Holiday for specific labor |
| Work Schedule | applicable_to_labor_grp | Labor Group | Schedule for labor group |
| Work Schedule Details | work_schedule | Work Schedule | Schedule detail lines |
| Labor Availability | labor | Labor | Availability calendar |
| Labor Availability Details | labor_availability | Labor Availability | Availability time slots |
| Trade Availability | trade | Trade | Trade availability calendar |

### Master Data & Notes

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Model | manufacturer | Manufacturer | Equipment model → Manufacturer |
| Master Data Change | requested_by | Employee | Change requester |
| Master Data Change | approved_by | Employee | Change approver |
| Master Data Change | site | Site | Change scope to site |
| Note Seen By | note | Note | Read tracking |
| Note Seen By | user | Users | User who read note |

---

## 3. Asset Management Module — Relationships

### Asset Central Entity

The **Asset** entity is the most connected entity in the system — it is referenced by 25+ other entities.

```
Asset
  ├── asset_class → AssetClass
  ├── model → Model → Manufacturer
  ├── location → Location → Site
  ├── site → Site → Organization
  ├── department → Department
  ├── assigned_to → Employee
  ├── system → System → SystemType
  ├── position → Position
  ├── item → Item
  ├── inventory → Inventory
  ├── parent_asset → Asset (self-ref hierarchy)
  ├── functional_location → Location
  └── warranty_vendor → Vendor
```

### Asset Hierarchy & Classification

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Asset | parent_asset | Asset | Parent-child asset hierarchy |
| Asset | asset_class | Asset Class | Classification |
| Asset Class | parent_asset_class | Asset Class | Self-ref classification tree |
| Asset Class Property | asset_class, property | Asset Class, Property | Class-level property definitions |
| Asset Property | asset, property | Asset, Property | Instance-level property values |
| Sub Asset | main_asset, child_asset | Asset, Asset | Sub-component decomposition |
| Property | property_type | Property Type | Property categorization |
| Property | unit_of_measure | Unit of Measure | Measurement units |

### Location & Position System

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Location | parent_location | Location | Self-ref location tree |
| Location | location_type | Location Type | Location classification |
| Location | site | Site | Site ownership |
| System | parent_system | System | Self-ref system tree |
| System | system_type | System Type | System classification |
| System | location, site | Location, Site | Physical placement |
| Position | asset_class | Asset Class | Position type |
| Position | system | System | System position belongs to |
| Position | location, site | Location, Site | Physical placement |
| Position | current_asset | Asset | Currently installed asset |
| Position Relation | position_a, position_b | Position, Position | Position-to-position links |
| Asset Position | position, asset | Position, Asset | Asset ↔ Position mapping |

### Equipment Management

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Equipment | equipment_group | Equipment Group | Group classification |
| Equipment | custodian | Employee | Responsible person |
| Equipment | location, site | Location, Site | Physical placement |
| Equipment | inventory | Inventory | Inventory linkage |
| Equipment Schedule | equipment_group, equipment | Equipment Group, Equipment | Schedule assignment |
| Equipment Availability | equipment | Equipment | Availability calendar |
| Breakdown | equipment | Equipment | Breakdown records |

### Meters & Readings

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Meter | asset | Asset | Meter attached to asset |
| Meter Reading | meter | Meter | Reading for meter |
| Meter Reading | work_order | Work Order | Reading taken during WO |
| Meter Reading | recorded_by | Employee | Person who took reading |

### Transfers, Warranties & Incidents

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Asset Transfer | asset | Asset | Asset being transferred |
| Asset Transfer | from_site, to_site | Site, Site | Origin and destination sites |
| Asset Transfer | from_location, to_location | Location, Location | Origin and destination locations |
| Asset Transfer | from_department, to_department | Department, Department | Department change |
| Asset Transfer | transferred_by, received_by | Employee, Employee | Transfer personnel |
| Warranty Claim | asset | Asset | Claim for asset |
| Warranty Claim | vendor | Vendor | Claim against vendor |
| Warranty Claim | work_order | Work Order | Related work order |
| Incident | asset | Asset | Affected asset |
| Incident | location, site, department | Location, Site, Department | Where it happened |
| Incident | reported_by | Users | Who reported |
| Incident | assigned_to | Employee | Assigned investigator |
| Incident | failure_analysis | Failure Analysis | Linked RCA |
| Incident Employee | incident, employee | Incident, Employee | Involved personnel |
| Disposed | asset, site | Asset, Site | Disposal record |
| Asset Maintenance History | asset | Asset | Maintenance tracking |
| Asset Maintenance History | work_order | Work Order | Linked work order |
| Asset Maintenance History | work_order_activity | Work Order Activity | Specific activity |
| Asset Maintenance History | category_of_failure | Category of Failure | Failure class |

---

## 4. Maintenance Management Module — Relationships

### Maintenance Planning Chain

```
Maintenance Plan
  ├── asset_class → AssetClass
  ├── manufacturer → Manufacturer
  ├── model → Model
  └── Planned Maintenance Activity (maintenance_plan → maintenance_plan.id)
        ├── maintenance_activity → MaintenanceActivity
        ├── checklist → Checklist
        ├── maintenance_type → RequestActivityType
        ├── Maintenance Interval (planned_maintenance_activity → pma.id)
        ├── Maintenance Condition (planned_maintenance_activity → pma.id)
        └── Maintenance Calendar (planned_maintenance_activity → pma.id)
```

### Maintenance Request → Work Order Flow

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Maintenance Request | requestor | Employee | Who made the request |
| Maintenance Request | asset | Asset | Asset needing maintenance |
| Maintenance Request | location, site, department | Location, Site, Department | Where |
| Maintenance Request | position | Position | Position in system |
| Maintenance Request | incident | Incident | Triggered by incident |
| Maintenance Request | planned_maintenance_activity | PMA | Generated from PM schedule |
| Maintenance Request | next_maintenance_request | Maintenance Request | Self-ref chain |
| Maintenance Request | work_order_activity | Work Order Activity | Resulting WO activity |

### Failure Analysis & Corrective Action

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Failure Analysis | work_order | Work Order | WO that found the failure |
| Failure Analysis | incident | Incident | Related incident |
| Failure Analysis | asset | Asset | Failed asset |
| Failure Analysis | category_of_failure | Category of Failure | Failure classification |
| Failure Analysis | analyst, site | Employee, Site | Who analyzed, where |
| Corrective Action | failure_analysis | Failure Analysis | CAPA for this analysis |
| Corrective Action | assigned_to | Employee | Responsible person |
| Corrective Action | verified_by | Employee | Verification approver |
| Corrective Action | work_order | Work Order | WO to implement action |

### Inspection System

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Inspection Route | site, department | Site, Department | Route scope |
| Inspection Point | inspection_route | Inspection Route | Point on route |
| Inspection Point | asset | Asset | Asset to inspect |
| Inspection Point | location | Location | Inspection location |

### Condition Monitoring & Sensors

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Sensor | asset | Asset | Sensor on asset |
| Sensor | asset_property | Asset Property | What it measures |
| Sensor | site | Site | Sensor location |
| Sensor Data | sensor | Sensor | Data readings |
| Condition Monitoring | asset | Asset | Asset being monitored |
| Condition Monitoring | sensor | Sensor | Sensor providing data |
| Condition Monitoring | maintenance_request | Maintenance Request | Auto-generated MR |
| Condition Monitoring | site | Site | Site scope |

### Service Request

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Service Request | asset | Asset | Affected asset |
| Service Request | site, location | Site, Location | Where |
| Service Request | work_order | Work Order | Resulting WO |
| Service Request | incident | Incident | Related incident |

---

## 5. Work Management Module — Relationships

### Work Order Hierarchy

```
Work Order
  ├── category_of_failure → CategoryOfFailure
  ├── incident → Incident
  ├── site → Site
  ├── department → Department
  ├── cost_code → CostCode
  ├── job_plan → JobPlan
  ├── approved_by → Employee
  ├── safety_permit → SafetyPermit
  ├── follow_up_work_order → WorkOrder (self-ref)
  ├── parent_work_order → WorkOrder (self-ref)
  └── Work Order Activity (work_order → work_order.id)
        ├── work_item → Asset
        ├── position → Position
        ├── assigned_to → Labor
        ├── location, site, department → Location, Site, Department
        ├── predecessor → WorkOrderActivity (self-ref dependency)
        ├── WO Labor (work_order_activity → woa.id)
        │     ├── trade → Trade
        │     ├── labor → Labor
        │     ├── WO Labor Actual Hours
        │     └── WO Labor Assignment → Labor
        ├── WO Equipment (work_order_activity → woa.id)
        │     ├── item → Item
        │     ├── equipment → Equipment
        │     ├── WO Equipment Actual Hours
        │     └── WO Equipment Assignment → Equipment
        ├── WO Parts (work_order_activity → woa.id)
        │     ├── item → Item
        │     ├── unit_of_measure → UnitOfMeasure
        │     └── WO Parts Reservation → Inventory
        ├── WO Checklist (work_order_activity → woa.id)
        │     ├── checklist → Checklist
        │     ├── inspector_id → Employee
        │     └── WO Checklist Detail
        └── WO Activity Logs (work_order_activity → woa.id)
```

### Job Plans & Safety

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Job Plan | checklist | Checklist | Associated checklist |
| Job Plan Task | job_plan | Job Plan | Tasks within a plan |
| Job Plan Task | item | Item | Required item |
| Safety Permit | work_order | Work Order | Permit for WO |
| Safety Permit | asset | Asset | Asset requiring permit |
| Safety Permit | location | Location | Work location |
| Safety Permit | requested_by, approved_by | Employee, Employee | Permit personnel |
| Safety Permit | site | Site | Site scope |
| Tool Checkout | tool | Asset | Tool (tracked as asset) |
| Tool Checkout | checked_out_to | Employee | Person using tool |
| Tool Checkout | work_order | Work Order | WO needing tool |
| Tool Checkout | site | Site | Site scope |

### Failure Code Taxonomy

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Category of Failure | site | Site | Site scope |
| Cause Code | category_of_failure | Category of Failure | Cause within category |
| Cause Code | site | Site | Site scope |
| Remedy Code | category_of_failure | Category of Failure | Remedy for category |
| Remedy Code | site | Site | Site scope |

---

## 6. Purchasing & Stores Module — Relationships

### Procurement Chain

```
Purchase Request (requestor → Employee, site → Site, department → Department)
  ├── maintenance_request → MaintenanceRequest
  ├── work_activity_id → WorkOrderActivity
  └── Purchase Request Line (purchase_request → purchase_request.id)
        ├── item → Item
        ├── vendor → Vendor
        ├── unit_of_measure → UnitOfMeasure
        ├── currency → Currency
        └── Request for Quotation (purchase_request → purchase_request.id)
              ├── supplier, awarded_vendor → Vendor
              ├── generated_by, requestor → Employee
              └── RFQ Line (rfq_id → rfq.id)
                    ├── pr_line → PurchaseRequestLine
                    └── item → Item

Purchase Order (vendor → Vendor, original_po → PurchaseOrder self-ref)
  ├── site → Site, department → Department, cost_code → CostCode
  └── Purchase Order Line (po_id → purchase_order.id)
        ├── pr_line_id → PurchaseRequestLine
        ├── item_id → Item
        └── Purchase Receipt (purchase_order_line → pol.id)
              ├── purchase_request_line → PurchaseRequestLine
              ├── item → Item
              └── receiving_location → Location
```

### Vendor Invoice & 3-Way Matching

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Vendor Invoice | vendor | Vendor | Invoice from vendor |
| Vendor Invoice | purchase_order | Purchase Order | Against this PO |
| Vendor Invoice | currency | Currency | Invoice currency |
| Vendor Invoice | site | Site | Site scope |
| Vendor Invoice Line | vendor_invoice | Vendor Invoice | Line items |
| Vendor Invoice Line | purchase_order_line | Purchase Order Line | Matches PO line |
| Vendor Invoice Line | item | Item | Invoiced item |

### Inventory & Stock

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Inventory | item | Item | Inventory of which item |
| Inventory | store_location | Store | In which store |
| Inventory | zone | Zone | In which zone |
| Inventory | bin_location | Bin | In which bin |
| Inventory | asset | Asset | Linked asset |
| Inventory | site, location | Site, Location | Physical location |
| Inventory | unit_of_measure | Unit of Measure | Stocking UOM |
| Item Class | asset_class | Asset Class | Item-asset classification link |
| Item Class | parent_item_class | Item Class | Self-ref hierarchy |
| Item Class | default_uom | Unit of Measure | Default UOM |
| Item Class | account | Account | Default account |
| Stock Ledger Entry | item | Item | Ledger for item |
| Stock Ledger Entry | store | Store | In which store |
| Stock Ledger Entry | bin | Bin | In which bin |
| Stock Ledger Entry | site | Site | Site scope |

### Stock Count

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Stock Count | store | Store | Count for store |
| Stock Count | site | Site | Site scope |
| Stock Count Task | stock_count | Stock Count | Task within count |
| Stock Count Task | assigned_to | Users | Counter |
| Stock Count Task | bin | Bin | Bin to count |
| Stock Count Line | stock_count | Stock Count | Count result |
| Stock Count Line | inventory, item | Inventory, Item | What was counted |
| Stock Count Line | bin, zone | Bin, Zone | Where |
| Stock Count Line | variance_reason | Reason Code | Explanation |

### Item Issue, Return & Transfer

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Item Issue | issue_to | Employee | Issued to whom |
| Item Issue | work_order_activity | Work Order Activity | Charge to WOA |
| Item Issue | work_order | Work Order | Charge to WO |
| Item Issue | site, department, cost_code | Site, Department, Cost Code | Financial coding |
| Item Return | returned_by | Employee | Who returned |
| Item Return | work_order_activity | Work Order Activity | Return from WOA |
| Item Return Line | item_return | Item Return | Return line |
| Item Return Line | work_order_parts | Work Order Parts | Parts being returned |
| Transfer | inventory | Inventory | Item being moved |
| Transfer | moved_by | Employee | Person transferring |
| Transfer | work_order_activity | Work Order Activity | WO-driven transfer |
| Transfer | from_location → to_location | Location → Location | Movement path |
| Transfer | from_store → to_store | Store → Store | Store transfer |
| Transfer Receipt | transfer_request | Transfer | Receipt of transfer |
| Transfer Receipt | inventory | Inventory | Received item |
| Purchase Return | inventory, item | Inventory, Item | Item returned to vendor |

### Other

| Source Entity | FK Column | Target Entity | Relationship |
|---------------|-----------|---------------|-------------|
| Vendor | site | Site | Vendor site assignment |
| Store | location, site | Location, Site | Store physical location |
| Reason Code | default_debit_account, default_credit_account | Account, Account | GL accounts |
| Sales Order | currency, site | Currency, Site | Customer order |
| Sales Order Item | sales_order | Sales Order | Order line |
| Sales Order Item | item | Item | Ordered item |
| Inspection | inspector, site | Employee, Site | Quality inspection |
| Inspection | inventory | Inventory | Inspected stock |
| Inventory Adjustment | source_stock_count | Stock Count | Adjustment origin |
| Inventory Adjustment | store, location, site | Store, Location, Site | Where |
| Putaway | item | Item | Item to put away |
| Putaway | store, bin, zone, site | Store, Bin, Zone, Site | Destination |

---

## 7. Cross-Module Integration Map

These are the critical entity-to-entity links that span across modules:

### Asset Management ↔ Work Management

| Relationship | Description |
|-------------|-------------|
| WorkOrder → Incident | WO raised from incident |
| WorkOrderActivity → Asset | Work performed on asset |
| WorkOrderActivity → Position | Work at position |
| WorkOrderActivity → Location | Work at location |
| WorkOrder → SafetyPermit | Permit required for WO |
| WorkOrder → JobPlan | Job template applied |
| ToolCheckout → Asset | Tool tracked as asset |
| ToolCheckout → WorkOrder | Tool used on WO |
| MeterReading → WorkOrder | Reading during WO |
| AssetMaintenanceHistory → WorkOrder | History from WO completion |
| WarrantyClaim → WorkOrder | Claim linked to WO |

### Asset Management ↔ Maintenance Management

| Relationship | Description |
|-------------|-------------|
| MaintenanceRequest → Asset | MR for asset |
| FailureAnalysis → Asset | RCA on asset |
| ConditionMonitoring → Asset | Monitoring asset condition |
| Sensor → Asset | Sensor on asset |
| InspectionPoint → Asset | Inspect asset |
| CorrectiveAction → WorkOrder | CAPA via WO |
| Incident → FailureAnalysis | Incident triggers RCA |

### Work Management ↔ Purchasing & Stores

| Relationship | Description |
|-------------|-------------|
| WorkOrderParts → Item | Parts needed for WO |
| WorkOrderPartsReservation → Inventory | Reserve stock for WO |
| WorkOrderEquipment → Item | Equipment items on WO |
| ItemIssue → WorkOrder, WorkOrderActivity | Parts charged to WO |
| ItemReturn → WorkOrderActivity | Parts returned from WO |
| PurchaseRequest → WorkOrderActivity | PR generated from WO |
| Transfer → WorkOrderActivity | Transfer for WO |

### Work Management ↔ Maintenance Management

| Relationship | Description |
|-------------|-------------|
| MaintenanceRequest → WorkOrderActivity | MR creates WOA |
| FailureAnalysis → WorkOrder | RCA from WO completion |
| CorrectiveAction → WorkOrder | CAPA implemented via WO |
| ServiceRequest → WorkOrder | Service request → WO |

### Purchasing ↔ Asset Management

| Relationship | Description |
|-------------|-------------|
| Inventory → Asset | Asset tracked as inventory |
| Equipment → Inventory | Equipment linked to stock |
| Putaway → Asset | Asset putaway |
| Disposed → Asset | Disposal record |

---

## 8. Self-Referential Hierarchies

These entities support unlimited nesting:

| Entity | Self-FK Column | Purpose |
|--------|---------------|---------|
| Asset | parent_asset | Asset decomposition tree |
| Asset Class | parent_asset_class | Classification hierarchy |
| Location | parent_location | Location tree (building → floor → room) |
| System | parent_system | System decomposition |
| Item Class | parent_item_class | Item classification tree |
| Employee | reports_to | Organizational chart |
| Work Order | parent_work_order | Parent-child WO relationship |
| Work Order | follow_up_work_order | Follow-up WO chain |
| Purchase Order | original_po | PO amendment chain |
| Maintenance Request | next_maintenance_request | MR sequence chain |
| Work Order Activity | predecessor | Task dependency chain |

---

## 9. Entity Count Summary by Module

| Module | Models | Inbound FKs (referenced by others) | Outbound FKs (references others) |
|--------|--------|-------------------------------------|----------------------------------|
| Core EAM | 31 | ~120 | ~30 |
| Asset Management | 29 | ~60 | ~55 |
| Maintenance Mgmt | 22 | ~15 | ~50 |
| Purchasing & Stores | 37 | ~25 | ~75 |
| Work Management | 20 | ~30 | ~65 |
| **Total** | **159** | **~250** | **~275** |
