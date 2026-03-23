# EAM 2.1 — Workflow & Document Flow Guide

Comprehensive reference for the EAM workflow engine architecture, per-entity lifecycle workflows, and cross-entity document flows.

> **Version:** 2.1.2  
> **Last Updated:** 2026-06-20

---

## Table of Contents

1. [Workflow Engine Architecture](#1-workflow-engine-architecture)
2. [Database Schema](#2-database-schema)
3. [Transition Validation Flow](#3-transition-validation-flow)
4. [Hook System](#4-hook-system)
5. [Entity Lifecycle Workflows](#5-entity-lifecycle-workflows)
   - 5.1 [Maintenance Request](#51-maintenance-request)
   - 5.2 [Maintenance Order](#52-maintenance-order)
   - 5.3 [Work Order](#53-work-order)
   - 5.4 [Work Order Activity](#54-work-order-activity)
   - 5.5 [Purchase Request](#55-purchase-request)
   - 5.6 [Purchase Order](#56-purchase-order)
   - 5.7 [Purchase Order Line](#57-purchase-order-line)
   - 5.8 [Purchase Request Line](#58-purchase-request-line)
   - 5.9 [Request for Quotation (RFQ)](#59-request-for-quotation-rfq)
   - 5.10 [Purchase Receipt](#510-purchase-receipt)
   - 5.11 [Stock Count](#511-stock-count)
   - 5.12 [Item Issue / Item Return](#512-item-issue--item-return)
   - 5.13 [Inventory Adjustment](#513-inventory-adjustment)
   - 5.14 [Transfer](#514-transfer)
   - 5.15 [Vendor Invoice](#515-vendor-invoice)
   - 5.16 [Asset](#516-asset)
   - 5.17 [Master Data Change](#517-master-data-change)
6. [Cross-Entity Document Flows](#6-cross-entity-document-flows)
   - 6.1 [Maintenance Chain: MR → WO → WOA](#61-maintenance-chain-mr--wo--woa)
   - 6.2 [Maintenance Order Chain: MO → WO](#62-maintenance-order-chain-mo--wo)
   - 6.3 [Procurement Chain: PR → RFQ → PO → Receipt](#63-procurement-chain-pr--rfq--po--receipt)
   - 6.4 [Receipt → Inventory / Asset / Equipment](#64-receipt--inventory--asset--equipment)
   - 6.5 [Stock Count → Inventory Adjustment](#65-stock-count--inventory-adjustment)
   - 6.6 [Item Issue → Inventory / WO Parts](#66-item-issue--inventory--wo-parts)
   - 6.7 [Work Order Activity → Asset Operations](#67-work-order-activity--asset-operations)
   - 6.8 [Automatic Background Flows](#68-automatic-background-flows)
7. [Complete Cross-Entity Flow Reference](#7-complete-cross-entity-flow-reference)
8. [Workflow Seeding & Configuration](#8-workflow-seeding--configuration)
9. [Role-Based Access Control in Workflows](#9-role-based-access-control-in-workflows)
10. [Future: Dynamic Business Rules (Proposal)](#10-future-dynamic-business-rules-proposal)

---

## 1. Workflow Engine Architecture

The EAM workflow system uses a **two-layer architecture**:

```
┌─────────────────────────────────────────────────────┐
│  LAYER 1: Database-Driven State Machine (Dynamic)   │
│  ─────────────────────────────────────────────────── │
│  • workflow_states — global state catalog            │
│  • workflow_actions — global action catalog          │
│  • workflows — per-entity workflow definitions       │
│  • workflow_state_links — state ↔ workflow junction  │
│  • workflow_transitions — from_state+action→to_state │
│                                                      │
│  Managed via: Workflow.xlsx seed + admin UI           │
│  Configures: states, transitions, allowed_roles      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼ validate_transition()
┌─────────────────────────────────────────────────────┐
│  LAYER 2: Business Logic Hooks (Code)               │
│  ─────────────────────────────────────────────────── │
│  • Module workflow_router.py files                   │
│  • Registered via @hook_registry.workflow(entity)    │
│                                                      │
│  Implements: validation rules, side-effects,         │
│  cross-entity document creation, cascading states,   │
│  inventory updates, asset position operations        │
└─────────────────────────────────────────────────────┘
```

**Layer 1** handles the *what* — which states exist, which transitions are valid, and who can perform them. This is fully dynamic and configurable through the database (seeded from Excel).

**Layer 2** handles the *how* — what business logic runs when a transition occurs. This is implemented as Python hook functions in each module's `workflow_router.py`.

---

## 2. Database Schema

### 2.1 Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `workflow_states` | Global state catalog | `id`, `label`, `slug`, `color` |
| `workflow_actions` | Global action catalog | `id`, `label`, `slug` |
| `workflows` | Per-entity workflow definition | `id`, `name`, `target_entity`, `is_active` |
| `workflow_state_links` | Links states to workflows | `workflow_id`, `state_id`, `is_initial`, `sort_order` |
| `workflow_transitions` | Valid state transitions | `workflow_id`, `from_state_id`, `action_id`, `to_state_id`, `sort_order`, `allowed_roles` (JSON) |

### 2.2 Relationships

```
workflows ──1:N── workflow_state_links ──N:1── workflow_states
workflows ──1:N── workflow_transitions ──N:1── workflow_states (from)
                                        ──N:1── workflow_states (to)
                                        ──N:1── workflow_actions
```

### 2.3 Slug Generation

Slugs are auto-generated from labels via SQLAlchemy event listeners:

```
"Submit for Approval" → "submit_for_approval"
"In Progress"         → "in_progress"
```

---

## 3. Transition Validation Flow

When a user clicks a workflow action button on the frontend:

```
Frontend                    Backend
────────                    ───────
1. User clicks action  ──►  POST /api/entity/{id}/workflow/{action_slug}
                             │
                             ├─ 2. Load workflow from DB (get_workflow)
                             │     └─ selectinload: state_links, transitions
                             │
                             ├─ 3. Validate transition (validate_transition)
                             │     ├─ Match (current_state_slug, action_slug)
                             │     ├─ Check user roles vs. allowed_roles
                             │     └─ Return (is_valid, target_slug, error)
                             │
                             ├─ 4. Resolve action label (get_action_label)
                             │     └─ "submit_for_approval" → "Submit for Approval"
                             │
                             ├─ 5. Create WorkflowContext
                             │     └─ {db, user, entity, doc, record_id,
                             │         action, from_state, to_state}
                             │
                             ├─ 6. Execute hook (hook_registry.execute_workflow)
                             │     ├─ Call registered workflow hook
                             │     ├─ Hook runs business logic
                             │     ├─ Hook may create/update other documents
                             │     └─ Return {status, message, data?}
                             │
                             ├─ 7. Apply state (on success)
                             │     └─ doc.workflow_state = target_slug
                             │
                             ├─ 8. Commit + Audit Log
                             │
                             └─ 9. Emit Socket.IO event
                                    └─ Real-time UI update
```

**Optimistic Locking**: The document is loaded with `with_for_update()` to prevent concurrent state mutation.

---

## 4. Hook System

### 4.1 Hook Registration

Hooks are registered via decorators in each module's `hooks.py`:

```python
from app.application.hooks.registry import hook_registry

@hook_registry.workflow("maintenance_request")
async def maintenance_request_workflow_hook(ctx):
    # ctx.doc    — the document instance
    # ctx.action — the human-readable action label
    # ctx.db     — AsyncSession
    # ctx.user   — CurrentUser
    from app.modules.maintenance_mgmt.workflow_router import route_workflow
    return await route_workflow("maintenance_request", ctx.doc, ctx.action, ctx.db, ctx.user)
```

### 4.2 Hook Types

| Type | Decorator | Trigger | Purpose |
|------|-----------|---------|---------|
| Workflow | `@hook_registry.workflow(entity)` | Workflow transition | Business logic for state changes |
| Before Save | `@hook_registry.before_save(entity)` | Before record save | Validation, auto-computation |
| After Save | `@hook_registry.after_save(entity)` | After record save | Side-effects, notifications |

### 4.3 Execution Order

1. Hooks are sorted by priority (lower = first)
2. `execute_workflow()` runs hooks sequentially
3. Stops on first error or meaningful result
4. Error result prevents the state transition

### 4.4 Module Workflow Routers

Each module has a central `workflow_router.py` that dispatches by entity:

| Module | Router | Entities Handled |
|--------|--------|-----------------|
| `work_mgmt` | `workflow_router.py` | Work Order, Work Order Activity, Work Order Parts |
| `maintenance_mgmt` | `workflow_router.py` | Maintenance Request, Maintenance Order |
| `purchasing_stores` | `workflow_router.py` | Purchase Request, Purchase Order, PO Line, PR Line, RFQ, Purchase Receipt, Item Issue, Item Return, Inventory Adjustment, Transfer, Stock Count, Vendor Invoice |

---

## 5. Entity Lifecycle Workflows

### 5.1 Maintenance Request

```
Draft ──[Submit for Approval]──► Pending Approval
  │                                     │
  │                              [Approve] ──► Approved ──[Submit for Resolution]──► In Progress
  │                                     │                                               │
  │                              [Submit for Emergency]──► Emergency                [Complete] ──► Completed
  │                                                                                     │
  └───────────────────────────────────────────────────────── [Reopen] ◄──────────────────┘
```

**Key Business Rules:**
- **Approve**: Creates Work Order + Work Order Activity from PMA resources (Path A)
- **Submit for Emergency**: Validates Priority="Emergency", creates WO+WOA with defaults, due_date=today (Path B)
- **Submit for Resolution**: Validates WOA is linked
- **Complete**: Validates linked WOA is completed/closed, sets `closed_date`
- **Reopen**: Clears `closed_date`, cascades reopen to WOA and WO

### 5.2 Maintenance Order

```
Draft ──[Approve]──► Approved ──[Release]──► Released
```

**Key Business Rules:**
- **Approve**: Validates MO has details
- **Release**: Creates Work Order from MO details, links WOAs from child MRs, sets WO to "approved" state

### 5.3 Work Order

```
Requested ──[Approve]──► Approved ──[Start]──► In Progress ──[Complete]──► Completed
                                                                   │
                                                           [Cancel] ──► Cancelled
                                                                   │
                                                           [Reopen] ──► Reopened → In Progress
```

**Key Business Rules:**
- **Start**: All WOAs must be in "Ready" state; cascades `in_progress` to all WOAs; records `downtime_start`
- **Complete**: All WOAs must be completed/closed; calculates `downtime_hours`; creates `asset_maintenance_history` records; increments `asset.number_of_repairs`; auto-creates `failure_analysis` if failure codes present
- **Cancel**: Releases all parts reservations across all WOAs; **cascades cancel to all active WOAs**
- **Reopen**: Clears `downtime_end` and `downtime_hours`; **reverts completed/closed WOAs back to In Progress** (clears `end_date`)

### 5.4 Work Order Activity

```
Awaiting Resources ──[Allocate]──► Ready ──[Start Activity]──► In Progress
     │                                                            │
     │                                                    [Complete] ──► Completed ──[Close]──► Closed
     │                                                            │
     │                                                     [Reopen] ◄─────────────────────────────┘
```

**Key Business Rules:**
- **Allocate**: Validates resources are assigned (Labor required; Equipment/Parts if PMA specifies)
- **Start Activity**: If activity type is "Maintain Asset", moves asset to `under_maintenance` state
- **Complete**: Handles per activity type:
  - *Install Asset*: Creates `asset_position`, updates `position.current_asset`, updates `asset.location`
  - *Remove Asset*: Sets `asset_position.date_removed`, clears `position.current_asset`
  - *Maintain Asset*: Sets `asset.need_repair=false`, `asset.workflow_state=active`
  - Updates `maintenance_request.closed_date` if linked
  - Updates `asset_property` if configured
  - **Auto-completes parent WO** when all sibling WOAs are done
- **Close**: Validates activity logs exist, parts issued match required, equipment/labor have actual hours; sets `end_date`

### 5.5 Purchase Request

```
Draft ──[Submit for Review]──► Pending Review ──[Submit for Approval]──► Pending Approval
                                                                              │
                                                    [Approve] ──► Approved ──►│      [Close] ──► Closed
                                                                              │         ▲
                                         [Reject Purchase Request] ──► Rejected        │
                                                      │                         (auto when all
                                         [Revise Purchase Request] ──► Draft     lines complete)
```

**Key Business Rules:**
- **Submit for Approval**: Cascades all non-rejected PR Lines to `pending_approval`
- **Approve**: Multi-level approval via `approval_engine`; cascades all eligible PR Lines to `approved`
- **Reject**: Cascades all lines to `rejected`
- **Close**: Requires all lines in `complete` state
- **Revise**: Reverts PR to Draft; **non-rejected lines are reset back to Draft**; rejected lines stay locked
- Cannot advance without at least one PR Line

### 5.6 Purchase Order

```
Draft ──[Approve]──► Open ──[Complete]──► Closed
                       │
                  [Cancel] ──► Cancelled
                       │
                  [Reject] ──► Rejected
```

**Key Business Rules:**
- **Approve**: Multi-level approval via `approval_engine`; cascades all PO Lines to `approved`
- **Complete**: Only when ALL PO Lines are `complete`
- **Cancel**: Only if all PO Lines are still in `approved` state (no receiving started); cascades lines to `cancelled`; **reverts linked PR Lines back to `approved`** for re-procurement
- **Reject**: Cascades all PO Lines to `rejected`

### 5.7 Purchase Order Line

```
Draft ──[Approve]──► Approved ──[Receive Partial]──► Partially Received ──[Receive All]──► Fully Received ──[Complete]──► Complete
                       │
                  [Reject] ──► Rejected
                  [Cancel] ──► Cancelled
```

**Key Business Rules:**
- States are synchronized with PR Lines (both move together)
- Receipt state changes are driven by `confirm_receipt` (Purchase Receipt)
- On **Complete**: auto-closes parent PO if all sibling lines are complete; also cascades to close linked PR

### 5.8 Purchase Request Line

```
Draft ──[Add Line Item]──► Pending Approval ──[Approve]──► Approved
                                                  │
                                           [Reject] ──► Rejected
                                                  │
          [Receive Partial]──► Partially Received ──[Receive All]──► Fully Received ──[Complete]──► Complete
```

**Key Business Rules:**
- On **Complete**: auto-closes parent PR if all sibling lines are complete
- Receipt state changes synchronized with PO Line receiving

### 5.9 Request for Quotation (RFQ)

```
Draft ──[Submit Source]──► Sourcing ──[Submit for Review]──► Review ──[Award]──► Awarded ──[Create Purchase Order]──► Order
                                                                         │
                                                                    [Cancel] ──► Cancelled
```

**Key Business Rules:**
- **Submit Source**: Validates RFQ has at least one line
- **Award**: Validates `awarded_vendor` is set
- **Create Purchase Order**: Creates PO + PO Lines from RFQ lines; moves RFQ to Order state

### 5.10 Purchase Receipt

```
Draft ──[Confirm]──► Confirmed
```

**Key Business Rules:**
- **Confirm**: Complex multi-step process:
  1. Validates PO Line exists, item type is not service/non-inventory
  2. Over-receiving check (qty_received + previous ≤ qty_ordered)
  3. Updates PO Line and PR Line `qty_received` and workflow states
  4. Updates Item master quantities
  5. Creates stock ledger audit trail
  6. Generates Inventory / Asset / Equipment records based on item type matrix
  7. Creates Maintenance Request for inspection-required assets
  8. Marks receipt as processed (`generated_inventory = true`)

### 5.11 Stock Count

```
Planned ──[Start Stock Count]──► In Progress ──[Approve]──► Approved ──[Complete]──► Closed
```

**Key Business Rules:**
- **Start**: Captures `snapshot_at` timestamp; applies freeze/warn policy to inventory records
- **Approve**: Validates no negative inventory; creates Inventory Adjustment with variance lines; redirects to IA
- **Complete**: Final close, no additional logic

### 5.12 Item Issue / Item Return

```
Draft ──[Issue Item]──► Issued
```

**Key Business Rules:**
- **Issue Item**: Updates inventory and item quantities:
  - *WO Parts Issue*: Increments `work_order_parts.quantity_issued`
  - *WO Equipment Issue*: Updates equipment custodian, moves asset to `issued` state
  - Decrements `inventory.actual_inv`, `inventory.available_inv`
  - Decrements `item.actual_qty_on_hand`, `item.available_capacity`
  - Creates stock ledger audit trail
  - Validates sufficient inventory before issuing

### 5.13 Inventory Adjustment

```
Draft ──[Approve]──► Approved ──[Post]──► Posted
```

**Key Business Rules:**
- Updates inventory quantities based on adjustment lines
- Source can be Stock Count (auto-generated) or manual

### 5.14 Transfer

```
Draft ──[Submit]──► Submitted ──[Receive]──► Received
```

**Key Business Rules:**
- **Receive**: Auto-creates a `transfer_receipt` document

### 5.15 Vendor Invoice

```
Draft ──[Submit]──► Pending ──[Approve]──► Approved ──[Pay]──► Paid
```

### 5.16 Asset

```
Acquired ──[Activate]──► Active ──[Maintain Asset]──► Under Maintenance ──[Complete Maintenance]──► Active
                           │
                    [Decommission] ──► Decommissioned
                           │
                      [Issue] ──► Issued ──[Return] ──► Active
```

**Key Business Rules:**
- State changes are driven by Work Order Activity completion (Install Asset, Remove Asset, Maintain Asset)
- Item Issue moves asset to `issued` state

### 5.17 Master Data Change

```
Draft ──[Submit]──► Pending ──[Approve]──► Approved ──[Apply]──► Applied
```

**Key Business Rules:**
- **Apply**: Reads `entity_type`, `entity_id`, `field_name`, `new_value` from the change record and applies the value to the target entity field

---

## 6. Cross-Entity Document Flows

### 6.1 Maintenance Chain: MR → WO → WOA

The primary maintenance workflow creates a chain of three linked documents:

```
┌─────────────────────┐     Approve or       ┌───────────────┐    Auto-created    ┌─────────────────────┐
│ Maintenance Request │────Submit for ──────►│  Work Order   │───────────────────►│ Work Order Activity │
│ (MR)                │    Emergency         │  (WO)         │                    │ (WOA)               │
└─────────────────────┘                      └───────────────┘                    └─────────────────────┘
  MR.work_order_activity ◄──────────────────────────────────────── WOA.id (back-link)
                                              WO.workflow_state             WOA.work_order = WO.id
                                              = "requested"                WOA.workflow_state
                                                                           = "awaiting_resources"
```

**Path A — Standard Approval:**
1. User approves MR → creates WO (state: `requested`) + WOA (state: `awaiting_resources`)
2. If MR has a Planned Maintenance Activity (PMA), resources are auto-populated:
   - Work Order Checklist (from PMA's inspection checklist)
   - Work Order Equipment (from PMA's maintenance equipment)
   - Work Order Labor (from PMA's maintenance trade)
   - Work Order Parts (from PMA's maintenance parts)
3. WOA is linked back to MR via `MR.work_order_activity`

**Path B — Emergency:**
1. User submits MR for emergency (requires Priority = "Emergency")
2. Creates WO with `due_date = today()`, `priority = Emergency`
3. Creates WOA with no PMA resources (empty tabs)
4. Cost code auto-filled from department defaults

**Completion (reverse cascade):**
1. WOA completes → sets `MR.closed_date = today()`
2. All WOAs complete → auto-completes parent WO
3. MR Reopen → cascades reopen to WOA (`in_progress`) and WO (`in_progress`)

### 6.2 Maintenance Order Chain: MO → WO

```
┌────────────────────┐     Release      ┌───────────────┐
│ Maintenance Order  │────────────────►│  Work Order   │
│ (MO) + MO Details  │                 │  (WO)         │
└────────────────────┘                 └───────────────┘
                                        WO.state = "requested"
         MO.work_order = WO.id          → auto-set to "approved"
         
   ┌─ MO Detail 1 ─► MR1.work_order_activity ──► WOA1 ─── WOA1.work_order = WO.id
   ├─ MO Detail 2 ─► MR2.work_order_activity ──► WOA2 ─── WOA2.work_order = WO.id
   └─ MO Detail N ─► MRn.work_order_activity ──► WOAn ─── WOAn.work_order = WO.id
```

**Release Flow:**
1. MO Release creates a single Work Order
2. For each MO Detail → finds linked MR → finds linked WOA → assigns WOA to new WO
3. Updates each linked MR state to `release`
4. WO is auto-set to `approved` state
5. MO stores `work_order` reference

### 6.3 Procurement Chain: PR → RFQ → PO → Receipt

```
┌──────────────────┐   Create PO    ┌────────────────┐   Confirm    ┌──────────────────┐
│ Purchase Request │──from PR ────►│ Purchase Order  │◄──Receipt──►│ Purchase Receipt  │
│ (PR + PR Lines)  │               │ (PO + PO Lines) │             │                   │
└──────────────────┘               └────────────────┘             └──────────────────┘
         │                                  ▲                              │
         │   Award/Create PO   ┌────────────┘                             │
         │                     │                                           │
         └─────────────────► ┌──────────────┐                             │
               (optional)    │    RFQ       │                             │
                             │ (+ RFQ Lines)│                             │
                             └──────────────┘                             │
                                                                          │
                             ┌────────────────────────────────────────────┘
                             │
                             ▼
                ┌──────────────────────────────────────────┐
                │ Generates: Inventory, Asset, Equipment,  │
                │ Asset Properties, Maintenance Requests,  │
                │ Stock Ledger entries                      │
                └──────────────────────────────────────────┘
```

**PR → PO (Direct):**
1. Server action `create_po_from_pr`: groups approved PR Lines by vendor
2. Creates one PO per vendor with `draft` state
3. Creates PO Lines linked back to PR Lines via `pr_line_id`

**PR → RFQ → PO:**
1. RFQ is awarded with vendor selection
2. Server action `create_po_from_rfq`: creates PO + PO Lines from RFQ Lines
3. RFQ transitions to `order` state

**State Synchronization (PR Lines ↔ PO Lines):**

| PO Line Action | PO Line State | PR Line State |
|----------------|---------------|---------------|
| Approve | Approved | Approved |
| Receive Partial | Partially Received | Partially Received |
| Receive All | Fully Received | Fully Received |
| Complete | Complete | Complete |
| Reject | Rejected | Rejected |
| Cancel | Cancelled | — |

**Auto-Close Cascading:**
- When all PO Lines reach `complete` → PO auto-closes
- When all PR Lines reach `complete` → PR auto-closes
- PO Line completion triggers both checks

### 6.4 Receipt → Inventory / Asset / Equipment

```
Purchase Receipt (Confirm)
         │
         ├── item_type = "asset_item" or "fixed_asset_item"
         │   ├── is_serialized = True
         │   │   └── For each unit:
         │   │       ├── new Inventory (qty=1)
         │   │       ├── new Asset (acquired)
         │   │       ├── new Asset Properties (from asset class)
         │   │       ├── new Equipment (if is_equipment)
         │   │       └── new Maintenance Request (if inspection_required)
         │   │
         │   └── is_serialized = False
         │       ├── Inventory (create or update qty)
         │       ├── new Asset (if not already linked)
         │       └── new Equipment (if is_equipment)
         │
         └── item_type = "inventory_item"
             ├── is_serialized = True
             │   └── For each unit:
             │       ├── new Inventory (qty=1)
             │       └── new Equipment (if is_equipment)
             │
             └── is_serialized = False
                 ├── Inventory (create or update qty)
                 └── new Equipment (if is_equipment)
```

**Inspection-Required Assets:**
- When `item.inspection_required = true`, a Maintenance Request is auto-created
- A Work Order Activity is also created (state: `awaiting_resources`)
- MR is auto-approved (Draft → Pending Approval → Approved)

### 6.5 Stock Count → Inventory Adjustment

```
Stock Count (Approve)
     │
     ├── Finds variance lines (counted_qty ≠ snapshot_qty)
     │
     └── Creates:
         ├── Inventory Adjustment (IA) — state: Draft
         └── IA Lines — one per variance line
             ├── adjusted_qty = variance_qty
             ├── current_qty = snapshot_qty
             └── delta_value = variance_qty × unit_cost
```

**Freeze Policy:**
- On "Start Stock Count", inventory records are flagged:
  - `Freeze` → prevents issuance/receipt
  - `Warn` → allows with warning
  - `None` → no restrictions

### 6.6 Item Issue → Inventory / WO Parts

```
Item Issue (Issue Item)
     │
     ├── issue_type = "WO Parts Issue"
     │   └── Updates work_order_parts.quantity_issued
     │
     ├── issue_type = "WO Equipment Issue"
     │   ├── Updates equipment.custodian
     │   └── Moves asset → "issued" state
     │
     └── For each item_issue_line:
         ├── Decrements inventory.actual_inv / available_inv
         ├── Decrements item.actual_qty_on_hand / available_capacity
         └── Creates stock_ledger entry (audit trail)
```

### 6.7 Work Order Activity → Asset Operations

WOA completion triggers different asset operations based on the activity type:

```
WOA Complete
     │
     ├── activity_type.menu = "Install Asset"
     │   ├── Creates asset_position record (date_installed = now)
     │   ├── Updates position.current_asset = work_item
     │   └── Updates asset.location, asset.system, asset.position
     │
     ├── activity_type.menu = "Remove Asset"
     │   ├── Sets asset_position.date_removed = now
     │   └── Clears position.current_asset
     │
     ├── activity_type.menu = "Maintain Asset"
     │   ├── Sets asset.need_repair = false
     │   └── Sets asset.workflow_state = "active"
     │
     └── (all types)
         ├── Sets MR.closed_date = today (if linked)
         ├── Updates asset_property (if configured)
         └── Auto-completes parent WO (if all WOAs done)
```

**Asset State During Maintenance:**
```
Active ──[WOA Start Activity]──► Under Maintenance ──[WOA Complete]──► Active
```

### 6.8 Automatic Background Flows

These flows are triggered by save hooks (not by explicit workflow actions):

| Trigger | Hook | Creates | Condition |
|---------|------|---------|-----------|
| Sensor data saved | `sensor_data_after_save` | Maintenance Request | Threshold breached |
| Condition monitoring saved | `condition_monitoring_after_save` | Maintenance Request | Critical threshold exceeded |
| PMA saved | `planned_maintenance_activity_after_save` | Maintenance Calendar | Has schedule, no existing calendar |
| WO Parts saved | `wo_parts_auto_pr` | Purchase Request + PR Line | `qty_required > qty_on_hand - reserved` |
| MR before save | `maintenance_request_before_save` | — (computes) | Auto-calculates priority from asset criticality × severity |
| MO Detail saved | `maintenance_order_detail_after_save` | — (copies) | Copies MR description if blank |
| WOA saved | `create_wo_labor_on_save` | Work Order Labor | `assigned_to` is set and no existing labor |

**Priority Matrix (MR auto-calculation):**

| Criticality \ Severity | Critical | High | Medium | Low |
|------------------------|----------|------|--------|-----|
| **A** | Emergency | Urgent | High | Medium |
| **B** | Urgent | High | Medium | Low |
| **C** | High | Medium | Low | Low |

---

## 7. Complete Cross-Entity Flow Reference

| # | Trigger Entity | Trigger Action | Records Created/Updated | Side Effects |
|---|---------------|----------------|------------------------|--------------|
| 1 | Maintenance Request | Approve | WO (requested) + WOA (awaiting_resources) | PMA resources copied to WOA |
| 2 | Maintenance Request | Submit for Emergency | WO (requested) + WOA (awaiting_resources) | Emergency defaults, no PMA |
| 3 | Maintenance Request | Complete | MR.closed_date updated | Cascades from WOA |
| 4 | Maintenance Request | Reopen | MR + WOA + WO states reset | Cascading reopen |
| 5 | Maintenance Order | Release | WO (requested → approved) | Links MOD→MR→WOA to new WO |
| 6 | Work Order | Start | All WOAs → in_progress | Records downtime_start |
| 7 | Work Order | Complete | asset_maintenance_history, failure_analysis | Downtime calculation, repair count |
| 8 | Work Order | Cancel | Releases parts reservations | All WOA parts released |
| 9 | WOA | Start Activity | asset → under_maintenance | Only if "Maintain Asset" type |
| 10 | WOA | Complete (Install) | asset_position, position, asset updates | Position/location assignment |
| 11 | WOA | Complete (Remove) | asset_position.date_removed | Clears position current_asset |
| 12 | WOA | Complete (Maintain) | asset.need_repair=false, state=active | Auto-completes parent WO |
| 13 | WOA | Close | Sets end_date | Validates logs, parts, hours |
| 14 | Purchase Request | Submit for Approval | PR Lines → pending_approval | Via apply_workflow_state |
| 15 | Purchase Request | Approve | PR Lines → approved | Multi-level approval engine |
| 16 | Purchase Request | Reject | PR Lines → rejected | All lines cascaded |
| 17 | Purchase Order | Approve | PO Lines → approved | Multi-level approval engine |
| 18 | Purchase Order | Cancel | PO Lines → cancelled | Only if all lines still approved |
| 19 | PO Line | Complete | Auto-close PO + PR | Cascading parent closure |
| 20 | PR Line | Complete | Auto-close PR | Cascading parent closure |
| 21 | Purchase Receipt | Confirm | Inventory, Asset, Equipment, Asset Properties, MR, Stock Ledger | Full record generation matrix |
| 22 | Stock Count | Start | Inventory freeze/warn flags | Freeze policy application |
| 23 | Stock Count | Approve | Inventory Adjustment + IA Lines | Variance posting |
| 24 | Item Issue | Issue Item | WO Parts qty, Equipment custodian, Inventory/Item qty, Stock Ledger | Inventory decrementation |
| 25 | RFQ | Create PO | PO + PO Lines | RFQ → Order state |
| 26 | Transfer | Receive | Transfer Receipt | Auto-created receipt doc |
| 27 | Sensor Data | Save (hook) | Maintenance Request | Threshold breach detection |
| 28 | Condition Monitoring | Save (hook) | Maintenance Request | Critical alert |
| 29 | WO Parts | Save (hook) | Purchase Request + PR Line | Parts shortage auto-PR |
| 30 | PMA | Save (hook) | Maintenance Calendar | Schedule auto-creation |
| 31 | Master Data Change | Apply | Target entity field updated | Dynamic field patching |

---

## 8. Workflow Seeding & Configuration

### 8.1 Seed Scripts

| Script | Purpose | Data Source |
|--------|---------|-------------|
| `reset_workflow_catalog.py` | Seeds global states (33) and actions (45) | Hardcoded lists |
| `seed_workflows_from_excel.py` | Seeds per-entity workflows, state links, transitions | `Workflow.xlsx` |

### 8.2 Workflow.xlsx Format

The Excel file contains sheets per entity with columns:

| Column | Description |
|--------|-------------|
| Workflow Name | e.g., "Work Order Workflow" |
| Target Entity | e.g., "work_order" |
| State | State label |
| Is Initial | Boolean — marks the starting state |
| From State | Transition source |
| Action | Action label |
| To State | Transition target |
| Allowed Roles | Comma-separated role names (JSON array in DB) |

### 8.3 Adding a New Workflow

1. Add states to `reset_workflow_catalog.py` if new states are needed
2. Add actions to `reset_workflow_catalog.py` if new actions are needed
3. Add entity rows to `Workflow.xlsx`
4. Run seed: `python -m app.scripts.reset_workflow_catalog && python -m app.scripts.seed_workflows_from_excel`
5. (Optional) Add business logic hook in the appropriate module's `workflow_router.py`

---

## 9. Role-Based Access Control in Workflows

### 9.1 How It Works

Each `workflow_transition` record has an `allowed_roles` JSON field:

```json
["PurchaseManager", "Buyer", "SystemManager"]
```

During `validate_transition()`:
1. User's roles are extracted from the JWT token
2. If `allowed_roles` is populated, user must have at least one matching role
3. `SystemManager` bypasses all role checks
4. If `allowed_roles` is empty/null, the transition is open to all authenticated users

### 9.2 Current Roles

| Role | Data Scope | Primary Purpose |
|------|-----------|----------------|
| SystemManager | all | Full system access |
| Executive | all | Read-only oversight |
| SiteManager | site | Site-level management |
| Supervisor | team | Team-level work management |
| Technician | own | Own work orders only |
| Viewer | site | Read-only site access |
| AssetManager | site | Asset lifecycle management |
| PurchaseManager | site | Procurement approvals |
| Buyer | site | Purchase order creation |
| Requisitioner | own | Purchase request creation |
| StoresManager | site | Inventory management |
| Storekeeper | site | Stock operations |
| MaintenanceManager | site | Manage all maintenance activities within site(s) |
| Planner | site | Plan and schedule maintenance activities |
| MaintenanceSupervisor | team | Supervise maintenance team and approve work orders |

---

## 10. Future: Dynamic Business Rules (Proposal)

Currently, business logic (Layer 2) is hardcoded in Python. A proposed enhancement would make it database-configurable.

### Proposed: JSON Rule Columns on `workflow_transitions`

Add two JSON columns to the existing `workflow_transitions` table:

```sql
ALTER TABLE workflow_transitions
  ADD COLUMN pre_conditions JSONB DEFAULT '[]',
  ADD COLUMN post_actions   JSONB DEFAULT '[]';
```

**Pre-Conditions** (evaluated before transition):
```json
[
  {"type": "has_children", "entity": "purchase_request_line", "fk": "purchase_request", "min": 1},
  {"type": "field_not_null", "field": "awarded_vendor"},
  {"type": "children_in_state", "entity": "work_order_activity", "fk": "work_order", "states": ["completed", "closed"]}
]
```

**Post-Actions** (executed after transition):
```json
[
  {"type": "cascade_state", "entity": "purchase_order_line", "fk": "po_id", "action_slug": "approve_line"},
  {"type": "set_field", "field": "closed_date", "value": "$today"},
  {"type": "create_doc", "entity": "work_order", "fields": {"description": "$doc.description", "workflow_state": "requested"}}
]
```

This approach preserves backward compatibility — existing hooks continue to work — while allowing simpler rules to be managed through the database without code changes.

---

## Appendix: File Reference

| File | Purpose |
|------|---------|
| `backend/app/models/workflow.py` | DB models (WorkflowState, WorkflowAction, Workflow, WorkflowStateLink, WorkflowTransition) |
| `backend/app/services/workflow.py` | Core engine (get_workflow, validate_transition, get_workflow_meta) |
| `backend/app/api/routes/entity_workflow.py` | REST endpoint for workflow transitions |
| `backend/app/application/hooks/registry.py` | Hook registration and execution |
| `backend/app/application/hooks/context.py` | WorkflowContext definition |
| `backend/app/modules/work_mgmt/workflow_router.py` | Work Order, WOA, WO Parts handlers |
| `backend/app/modules/maintenance_mgmt/workflow_router.py` | MR, MO handlers |
| `backend/app/modules/purchasing_stores/workflow_router.py` | All purchasing/stores handlers |
| `backend/app/modules/work_mgmt/apis/work_order_activity.py` | WOA business logic (asset operations) |
| `backend/app/modules/maintenance_mgmt/apis/maintenance_request.py` | MR business logic (WO/WOA creation) |
| `backend/app/modules/maintenance_mgmt/apis/maintenance_order.py` | MO business logic (WO generation) |
| `backend/app/modules/purchasing_stores/apis/purchase_receipt.py` | Receipt confirmation (inventory/asset generation) |
| `backend/app/modules/purchasing_stores/apis/purchase_order.py` | PO creation from PR/RFQ |
| `backend/app/modules/purchasing_stores/apis/stock_count.py` | Stock count workflow + IA generation |
| `backend/scripts/seeds/patch_dead_end_transitions.py` | Fixes dead-end states (adds Reopen transitions) |
| `backend/app/modules/maintenance_mgmt/hooks.py` | Background hooks (sensor alerts, auto-PR, etc.) |
| `backend/app/scripts/reset_workflow_catalog.py` | Seeds 33 states + 45 actions |
| `backend/app/scripts/seed_workflows_from_excel.py` | Seeds workflows from Workflow.xlsx |
