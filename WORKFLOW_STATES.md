# EAM-CHI — Workflow States & Entity Lifecycle

**Date:** March 24, 2026
**System:** Enterprise Asset Management — CHI & ITBA
**Version:** 1.0

---

## Executive Summary

This document maps every workflow-enabled entity in the EAM-CHI system, its states, valid transitions, and cross-entity cascade behavior. The system includes **25 workflow-enabled entities** with state machines, **6 state machine extensions** (field permissions, required fields, backward justification, SLA escalation, audit logging), and **dead-end state recovery** patches.

---

## 1. Work Management Workflows

### 1.1 Work Order

The Work Order is the central execution entity. It cascades state changes to child Work Order Activities.

**States:** Requested → Approved → In Progress → Closed / Cancelled

| # | From State | Action | To State | Cascade / Side Effect |
|---|-----------|--------|----------|----------------------|
| 1 | Requested | Approve | Approved | — |
| 2 | Approved | Start | In Progress | All child WOAs move to Ready |
| 3 | In Progress | Complete | Closed | Auto-creates Asset Maintenance History; auto-creates Failure Analysis if failure codes present |
| 4 | In Progress | Cancel | Cancelled | All active WOAs cascade to Cancelled |
| 5 | Cancelled | Reopen | Requested | Clears downtime fields; reverts completed WOAs to In Progress *(dead-end fix)* |

**SLA Threshold:** In Progress state — 168 hours (7 days)

**Field Permissions (SM-1):** All fields locked in Closed state

**Required Fields (SM-2):** Approve requires asset + work_order_type

### 1.2 Work Order Activity

**States:** Awaiting Resources → Ready → In Progress → Completed / On Hold → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Awaiting Resources | Allocate | Ready | Resources confirmed |
| 2 | Ready | Start | In Progress | — |
| 3 | In Progress | Complete | Completed | Checks if all WOAs complete → auto-complete parent WO |
| 4 | In Progress | Hold | On Hold | — |
| 5 | On Hold | Resume | In Progress | — |
| 6 | Completed | Close | Closed | — |
| 7 | In Progress | Cancel | Cancelled | — |

### 1.3 Safety Permit

**States:** Draft → Requested → Approved → Active → Expired / Cancelled / Completed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Requested | — |
| 2 | Requested | Approve | Approved | — |
| 3 | Approved | Activate | Active | Permit becomes enforceable |
| 4 | Active | Expire | Expired | Time-based expiration |
| 5 | Active | Complete | Completed | Work finished safely |
| 6 | Requested | Reject | Cancelled | — |
| 7 | Active | Revoke | Cancelled | Emergency revocation |

**Permit Types:** Hot Work, Confined Space, LOTO, Excavation, Working at Height

### 1.4 Tool Checkout

**States:** Draft → Checked Out → Returned / Overdue

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Checkout | Checked Out | — |
| 2 | Checked Out | Return | Returned | Condition assessment recorded |
| 3 | Checked Out | Flag Overdue | Overdue | Scheduler-triggered |
| 4 | Overdue | Return | Returned | Late return recorded |

---

## 2. Asset Management Workflows

### 2.1 Asset Lifecycle

The most complex state machine — supports maintenance loops and decommissioning.

**States:** Acquired → Inspected → Active ↔ Inactive / Under Maintenance / Under Repair → Decommissioned

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Acquired | Inspect | Inspected | Initial inspection gate |
| 2 | Inspected | Commission | Active | Asset in service |
| 3 | Active | Deactivate | Inactive | Temporarily out of service |
| 4 | Inactive | Reactivate | Active | Return to service |
| 5 | Active | Send to Maintenance | Under Maintenance | PM/scheduled maintenance |
| 6 | Under Maintenance | Return to Service | Active | Maintenance complete |
| 7 | Active | Send to Repair | Under Repair | Breakdown/corrective |
| 8 | Under Repair | Return to Service | Active | Repair complete |
| 9 | Active | Decommission | Decommissioned | End of life |
| 10 | Inactive | Decommission | Decommissioned | — |
| 11 | Under Maintenance | Decommission | Decommissioned | Beyond repair |
| 12 | Under Repair | Decommission | Decommissioned | Beyond repair |
| 13 | Inspected | Reject | Acquired | Failed inspection |
| 14 | Decommissioned | Recommission | Active | Rare: asset restored |

### 2.2 Asset Transfer

**States:** Draft → Pending Approval → Approved → In Transit → Received / Cancelled

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Pending Approval | — |
| 2 | Pending Approval | Approve | Approved | — |
| 3 | Approved | Ship | In Transit | — |
| 4 | In Transit | Receive | Received | Auto-updates asset location, site, department |
| 5 | Pending Approval | Reject | Cancelled | — |

### 2.3 Warranty Claim

**States:** Draft → Submitted → Under Review → Approved / Rejected → Credited / Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Submitted | — |
| 2 | Submitted | Review | Under Review | — |
| 3 | Under Review | Approve | Approved | — |
| 4 | Under Review | Reject | Rejected | — |
| 5 | Approved | Credit | Credited | Records credited amount |
| 6 | Credited | Close | Closed | — |
| 7 | Rejected | Resubmit | Draft | Resubmission allowed |
| 8 | Approved | Close | Closed | Closed without credit |

---

## 3. Maintenance Management Workflows

### 3.1 Maintenance Request

**States:** Draft → Pending Approval → Approved → Release → Completed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Pending Approval | Auto-calculates priority from asset criticality × severity |
| 2 | Pending Approval | Approve | Approved | — |
| 3 | Approved | Release | Release | Generates Work Order |
| 4 | Release | Complete | Completed | — |
| 5 | Pending Approval | Reject | Draft | Send back with reason |
| 6 | Draft | Emergency | Release | Bypass approval for emergencies |

**SLA Threshold:** Draft state — 48 hours

**Categories:** Corrective, Emergency, Safety, Modification, Inspection

### 3.2 Condition Monitoring

**States:** Active → Warning → Critical → Resolved

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Active | Warn | Warning | Threshold exceeded — alert generated |
| 2 | Warning | Escalate | Critical | Auto-generates Maintenance Request |
| 3 | Critical | Resolve | Resolved | Issue addressed |
| 4 | Warning | De-escalate | Active | Readings returned to normal |
| 5 | Critical | De-escalate | Warning | Partial improvement |

### 3.3 Failure Analysis

**States:** Draft → In Analysis → Review → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Start Analysis | In Analysis | — |
| 2 | In Analysis | Submit for Review | Review | — |
| 3 | Review | Close | Closed | — |
| 4 | Review | Send Back | In Analysis | Requires more investigation |

### 3.4 Corrective Action (CAPA)

**States:** Draft → Assigned → In Progress → Verification → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Assign | Assigned | — |
| 2 | Assigned | Start | In Progress | — |
| 3 | In Progress | Submit for Verification | Verification | — |
| 4 | Verification | Verify & Close | Closed | — |
| 5 | Verification | Reject | In Progress | Verification failed |

---

## 4. Purchasing & Stores Workflows

### 4.1 Purchase Request

**States:** Draft → Pending Review → Pending Approval → Approved / Rejected → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Pending Review | — |
| 2 | Pending Review | Review | Pending Approval | — |
| 3 | Pending Approval | Approve | Approved | Multi-level approval engine checks authority limit |
| 4 | Pending Approval | Reject | Rejected | — |
| 5 | Approved | Close | Closed | All PR lines completed |
| 6 | Rejected | Revise | Draft | Reset non-rejected lines to draft *(dead-end fix)* |

**SLA Threshold:** Pending Approval state — 24 hours

**Budget Validation:** Submission checks against annual budget for cost code

### 4.2 Purchase Request Line

**States:** Draft → Pending Approval → Approved → Partially Received → Fully Received → Complete

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Pending Approval | Follows parent PR |
| 2 | Pending Approval | Approve | Approved | — |
| 3 | Approved | Partial | Partially Received | — |
| 4 | Partially Received | Receive All | Fully Received | — |
| 5 | Fully Received | Complete | Complete | Auto-closes parent PR when all lines complete |

### 4.3 Purchase Order

**States:** Draft → Open → Closed / Cancelled / Rejected

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Open | Open | Multi-level approval verified |
| 2 | Open | Close | Closed | All PO lines complete |
| 3 | Open | Cancel | Cancelled | Reverts linked PR Lines to "approved" for re-procurement |
| 4 | Draft | Reject | Rejected | — |
| 5 | Cancelled | Reopen | Draft | *(dead-end fix)* |
| 6 | Rejected | Reopen | Draft | *(dead-end fix)* |

**Amendment Tracking:** PO changes auto-increment amendment_number; original_po tracks chain

### 4.4 Purchase Order Line

**States:** Draft → Approved → Partially Received → Fully Received → Complete

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Approve | Approved | — |
| 2 | Approved | Partial | Partially Received | — |
| 3 | Partially Received | Receive All | Fully Received | — |
| 4 | Fully Received | Complete | Complete | Auto-closes parent PO when all lines complete |
| 5 | Approved | Cancel | Cancelled | Reverts linked PR Line to "approved" |
| 6 | Cancelled | Reopen | Draft | *(dead-end fix)* |

### 4.5 Request for Quotation (RFQ)

**States:** Draft → Sourcing → Review → Awarded → Order / Cancelled

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Send | Sourcing | Sent to vendors |
| 2 | Sourcing | Receive Responses | Review | — |
| 3 | Review | Award | Awarded | Vendor selected |
| 4 | Awarded | Create PO | Order | Generates Purchase Order |
| 5 | Review | Cancel | Cancelled | — |
| 6 | Cancelled | Reopen | Draft | *(dead-end fix)* |

### 4.6 Stock Count

**States:** Planned → In Progress → Approved → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Planned | Start | In Progress | — |
| 2 | In Progress | Submit | Approved | — |
| 3 | Approved | Finalize | Closed | Auto-generates Inventory Adjustments for variances |

### 4.7 Item Issue

**States:** Requested → Issued → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Requested | Issue | Issued | Decrements inventory; creates stock ledger entry |
| 2 | Issued | Close | Closed | — |
| 3 | Issued | Reopen | Draft | *(dead-end fix)* |

### 4.8 Item Return

**States:** Received → Returned → Closed

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Received | Process | Returned | Inspection if required |
| 2 | Returned | Close | Closed | Increments inventory; creates stock ledger entry |

### 4.9 Inventory Adjustment

**States:** Draft → Submitted → Posted / Cancelled

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Submitted | — |
| 2 | Submitted | Post | Posted | Updates inventory quantities; creates stock ledger entry |
| 3 | Submitted | Cancel | Cancelled | — |
| 4 | Posted | Resubmit | Submitted | Correction allowed |

### 4.10 Vendor Invoice

**States:** Draft → Submitted → Matched → Approved → Paid / Disputed → Resolved

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Submitted | — |
| 2 | Submitted | Match | Matched | 3-way match: PO + Receipt + Invoice |
| 3 | Matched | Approve | Approved | — |
| 4 | Approved | Pay | Paid | Payment recorded |
| 5 | Submitted | Dispute | Disputed | Discrepancy found |
| 6 | Disputed | Resolve | Resolved | — |

### 4.11 Service Contract

**States:** Draft → Under Review → Active → Expired / Terminated

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Under Review | — |
| 2 | Under Review | Activate | Active | SLA tracking begins |
| 3 | Active | Expire | Expired | Auto or manual expiration |
| 4 | Active | Terminate | Terminated | Early termination |
| 5 | Expired | Renew | Draft | Renewal cycle |

### 4.12 Sales Order

**States:** Draft → Submitted → Approved / Cancelled

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Submitted | — |
| 2 | Submitted | Approve | Approved | — |
| 3 | Submitted | Reject | Draft | — |
| 4 | Submitted | Cancel | Cancelled | — |

---

## 5. Core EAM Workflows

### 5.1 Master Data Change

**States:** Draft → Pending Approval → Approved → Applied / Rejected

| # | From State | Action | To State | Side Effect |
|---|-----------|--------|----------|-------------|
| 1 | Draft | Submit | Pending Approval | — |
| 2 | Pending Approval | Approve | Approved | — |
| 3 | Approved | Apply | Applied | Auto-applies changes to target entity |
| 4 | Pending Approval | Reject | Rejected | — |
| 5 | Rejected | Revise | Draft | Resubmission |

---

## 6. State Machine Extensions

### SM-1: State-Based Field Permissions

Controls which fields become read-only in specific states:

| Entity | State | Read-Only Fields |
|--------|-------|-----------------|
| Work Order | Closed | All fields |
| Work Order | In Progress | type, asset, category_of_failure |
| Purchase Request | Approved | All fields except notes |
| Purchase Order | Closed | All fields |

### SM-2: Required Fields per Transition

| Entity | Transition | Required Fields |
|--------|-----------|-----------------|
| Work Order | → Approved | asset, work_order_type |
| Purchase Request | → Pending Approval | requestor, at least 1 PR line |
| Safety Permit | → Active | approved_by, valid_from, valid_to |

### SM-4: Backward Transition Justification

These transitions require a mandatory reason/justification:

| Entity | Backward Transition | Reason Required |
|--------|--------------------|----|
| Work Order | Cancelled → Requested | Yes |
| Purchase Request | Rejected → Draft | Yes |
| Purchase Order | Cancelled → Draft | Yes |
| Failure Analysis | Review → In Analysis | Yes |
| Corrective Action | Verification → In Progress | Yes |

### SM-5: Per-State SLA Thresholds

| Entity | State | SLA Threshold | Escalation |
|--------|-------|--------------|-----------|
| Maintenance Request | Draft | 48 hours | Notify supervisor |
| Work Order | In Progress | 168 hours (7 days) | Notify manager |
| Purchase Request | Pending Approval | 24 hours | Escalate to next approver |

### SM-6: Enhanced Audit Logging

Every state transition records:
- **Who:** User ID and username
- **When:** Timestamp
- **From/To:** Previous and new state
- **Justification:** Required for backward transitions
- **SLA Breach:** Whether transition exceeded SLA threshold
- **Metadata:** IP address, session context

---

## 7. Cross-Entity Cascade Flows

### 7.1 Work Order Completion Cascade

```
Work Order → Closed
  ├── All WO Activities checked (if all Completed → OK)
  ├── Auto-create Asset Maintenance History
  ├── Auto-create Failure Analysis (if failure codes present)
  ├── Release parts reservations
  └── Calculate total cost (labor + equipment + parts)
```

### 7.2 Purchase Request → Purchase Order Flow

```
Purchase Request (Approved)
  ├── PR Lines (Approved)
  │     └── PR→PO Consolidation (server action)
  │           └── Purchase Order (Draft → Open)
  │                 ├── PO Lines → PR Lines linked
  │                 └── PO Cancel → PR Lines revert to "Approved"
  └── Auto-PR from WO Parts Shortage
```

### 7.3 3-Way Matching Flow

```
Purchase Order (Open)
  └── PO Line (Approved)
        ├── Purchase Receipt (confirms delivery)
        └── Vendor Invoice Line (confirms billing)
              └── 3-Way Match Service validates:
                    PO qty/price ≈ Receipt qty ≈ Invoice qty/price
```

### 7.4 Condition Monitoring → Work Order Flow

```
Sensor → Sensor Data (readings)
  └── Condition Monitoring (Active)
        ├── Threshold exceeded → Warning
        │     └── Escalate → Critical
        │           └── Auto-generate Maintenance Request
        │                 └── Release → Work Order created
        └── Normal readings → stays Active
```

### 7.5 Inventory Reorder Flow

```
Inventory (quantity_on_hand < reorder_point)
  └── Scheduler detects low stock
        └── Auto-generate Purchase Request
              └── PR Lines for items below reorder point
                    └── Normal PR→PO flow continues
```

### 7.6 WO Cancel Cascade

```
Work Order → Cancelled
  ├── All active WO Activities → Cancelled
  ├── Parts reservations → Released
  └── Downtime fields → Cleared
```

### 7.7 PO Cancel → PR Revert

```
Purchase Order → Cancelled
  └── For each PO Line:
        └── Linked PR Line → reverted to "Approved"
              (available for new PO assignment)
```

---

## 8. Dead-End State Recovery Patches

The `patch_dead_end_transitions.py` script adds recovery transitions for states that had no outgoing transitions:

| Entity | Dead-End State | Recovery Action | Destination |
|--------|---------------|-----------------|-------------|
| Work Order | Cancelled | Reopen | Requested |
| Purchase Request | Rejected | Revise | Draft |
| Purchase Order | Cancelled | Reopen | Draft |
| Purchase Order | Rejected | Reopen | Draft |
| Purchase Order Line | Cancelled | Reopen | Draft |
| Purchase Order Line | Rejected | Reopen | Draft |
| Item Issue | Issued | Reopen | Draft |
| RFQ | Cancelled | Reopen | Draft |

---

## 9. Workflow Summary Statistics

| Metric | Count |
|--------|-------|
| Total workflow-enabled entities | 25 |
| Total defined states | ~85 |
| Total transitions | ~120 |
| Dead-end fixes applied | 8 |
| SLA-monitored entities | 3 |
| State machine extensions | 6 |
| Cross-entity cascades | 7+ |
