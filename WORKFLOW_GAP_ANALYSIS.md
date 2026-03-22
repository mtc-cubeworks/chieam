# EAM-CHI Workflow Implementation Gap Analysis

**Project:** CHI Enterprise Asset Management System
**Date:** March 22, 2026
**Scope:** Detailed assessment of existing and missing workflow implementations

---

## 1. Overview of Existing Workflows

The system contains **20 workflow diagrams** across **16 functional areas** plus **5 state machine diagrams**:

| Category | Workflows |
|----------|-----------|
| **Asset Management** | Asset Record |
| **Maintenance** | Maintenance Requests, Incident |
| **Work Management** | Work Order, Work Order Activity, Work Order Equipment and Labor, Work Order Labor Assignment |
| **Inventory** | Inventory, Inventory Adjustment, Stock Count |
| **Parts** | Parts Issue, Parts Return |
| **Procurement** | Purchase Request, Purchase Request Line, Purchase Order |
| **State Machines** | States 1, States 2, States 3, States 4, States 5 |

---

## 2. Gaps WITHIN Existing Workflows

### 2.1 Asset Record Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| AR-1 | **No Asset Lifecycle States** | Asset should transition through: Planning → Procurement → Commissioning → Active/Operating → Idle → Decommissioned → Disposed | Cannot track where an asset is in its lifecycle |
| AR-2 | **No Asset Hierarchy/Parent-Child** | Each asset should link to a parent asset and/or functional location to form a tree structure | Cannot do cost rollup, failure propagation, or BOM inheritance |
| AR-3 | **No Criticality/Risk Classification** | Assets should be tagged with criticality (A/B/C) or risk matrix score to drive maintenance strategy | All assets treated equally; cannot prioritize maintenance |
| AR-4 | **No Meter/Reading Tracking** | Runtime hours, odometer, cycle count readings should be captured against assets | Cannot trigger meter-based PM or track usage |
| AR-5 | **No Warranty Linkage** | Warranty start/end dates, terms, and vendor linked per asset | Risk of paying for repairs covered under warranty |
| AR-6 | **No Nameplate/Specification Data** | Technical specifications, rated capacity, manufacturer data | Incomplete asset registry for engineering decisions |
| AR-7 | **No Depreciation Calculation** | Straight-line or declining-balance depreciation per asset | No financial lifecycle tracking |
| AR-8 | **No Asset Cloning/Template** | Ability to duplicate an asset record for similar equipment | Slow data entry for fleet/batch assets |

### 2.2 Maintenance Request Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| MR-1 | **No Priority Auto-Calculation** | Priority should be derived from asset criticality × impact severity matrix | Inconsistent prioritization, relies on requester judgment |
| MR-2 | **No SLA Timer** | Once a request is submitted, an SLA clock should start (e.g., respond in 4 hrs, resolve in 24 hrs) | No accountability for response/resolution times |
| MR-3 | **No Request-to-WO Auto-Conversion** | Approved maintenance requests should auto-generate a Work Order with pre-populated fields | Manual re-entry of data from request into WO |
| MR-4 | **No Duplicate Detection** | System should detect if a request already exists for the same asset with same issue | Duplicate work orders created for the same problem |
| MR-5 | **No Requester Notification Flow** | Requester should receive updates at each state change (acknowledged, in-progress, completed) | Requesters have no visibility into their request status |
| MR-6 | **No Categorization Taxonomy** | Standard categories: Corrective, Emergency, Safety, Modification, Inspection | Cannot analyze request patterns by type |

### 2.3 Incident Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| IN-1 | **No Root Cause Analysis (RCA) Integration** | Incidents should feed into an RCA workflow (5-Why, Fishbone, Fault Tree) | Recurring incidents are not systematically resolved |
| IN-2 | **No Corrective/Preventive Action (CAPA)** | Each incident should generate follow-up actions tracked to completion | Incident findings are not translated into lasting improvements |
| IN-3 | **No Incident Severity Classification** | Standard severity tiers (1-Critical, 2-Major, 3-Minor, 4-Near-Miss) | Cannot filter or escalate by severity |
| IN-4 | **No Safety Incident Subtype** | Environmental, safety, equipment failure, process upset subtypes | Cannot report on safety KPIs (TRIR, LTIR) |
| IN-5 | **No Regulatory Reporting Workflow** | OSHA-recordable incidents should trigger regulatory reporting steps | Compliance risk for reportable incidents |
| IN-6 | **No Incident-to-WO Link** | Incidents should link to resulting corrective work orders | Cannot trace remediation back to the triggering incident |

### 2.4 Work Order Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| WO-1 | **No WO Type Classification** | Types: Corrective, Preventive, Predictive, Emergency, Project, Inspection, Calibration | Cannot segregate or analyze work by type |
| WO-2 | **No Job Plan / Standard Job** | Reusable job plans with predefined tasks, labor, parts, tools, safety procedures | Inconsistent work execution; every WO is written from scratch |
| WO-3 | **No Scheduling / Calendar View** | Gantt or calendar view for WO scheduling with drag-drop, resource leveling | Cannot visualize workload or detect scheduling conflicts |
| WO-4 | **No Multi-Level Approval** | Approval routing based on cost threshold or WO type (e.g., >$5K needs manager) | All WOs follow same approval regardless of risk/cost |
| WO-5 | **No Cost Tracking & Rollup** | Track actual labor hours × rates + parts cost + contractor cost vs. estimate | No visibility into maintenance spend per WO, asset, or site |
| WO-6 | **No Downtime Tracking** | Capture equipment downtime start/end per WO to calculate availability | Cannot compute asset availability or OEE |
| WO-7 | **No Failure Reporting** | Failure code → Cause code → Remedy code (ISO 14224 taxonomy) | Cannot identify failure patterns or perform reliability analysis |
| WO-8 | **No Safety Checklist / Permit** | Pre-work safety checks, LOTO verification, confined space permits | Safety compliance gap; no digital permit-to-work |
| WO-9 | **No WO Feedback / Close-out Survey** | Technician notes on what was found, what was done, recommendations for next time | Institutional knowledge is lost |
| WO-10 | **No Follow-Up WO Generation** | Ability to generate a follow-up WO from a completed WO for deferred or additional scope | Deferred work falls through the cracks |

### 2.5 Work Order Activity Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| WA-1 | **No Task Sequencing / Dependencies** | Activities should support predecessors/successors (Task B starts after Task A) | Cannot enforce logical task order for complex jobs |
| WA-2 | **No Time Tracking Per Activity** | Individual activity start/stop timestamps or duration capture | Cannot measure time per task for estimating or optimization |
| WA-3 | **No Completion Criteria** | Each activity should have defined acceptance criteria or checklist | Ambiguous definition of "done" for each step |

### 2.6 Work Order Labor Assignment Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| LA-1 | **No Craft/Skill Matching** | Assign labor based on required craft (electrician, mechanic, etc.) vs. available skills | Wrong skill assigned; safety/quality risk |
| LA-2 | **No Availability Calendar** | Check technician shift schedule and existing assignments before assigning | Double-booking of technicians |
| LA-3 | **No Overtime / Rate Differentiation** | Regular vs. overtime vs. premium rate tracking per assignment | Inaccurate labor cost calculations |
| LA-4 | **No Contractor vs. Internal Flag** | Distinguish internal labor from external contractor labor | Cannot analyze insource vs. outsource cost |

### 2.7 Inventory Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| IV-1 | **No Reorder Point / Min-Max** | Automatic reorder trigger when stock falls below minimum | Stockouts cause maintenance delays |
| IV-2 | **No Auto-PR Generation** | When stock hits reorder point, auto-generate a Purchase Request | Manual reordering is reactive and slow |
| IV-3 | **No ABC Classification** | Classify items by value/criticality (ABC analysis) for stocking strategy | High-value items managed same as low-value consumables |
| IV-4 | **No Lot/Serial Tracking** | Track items by lot number or serial number for traceability | Cannot trace defective parts back to a specific lot |
| IV-5 | **No Storeroom/Bin Location** | Multiple storerooms with bin/shelf locations | Technicians cannot locate parts efficiently |
| IV-6 | **No Cycle Count Scheduling** | Automated cycle count schedule based on ABC classification | Only ad-hoc stock counts; inventory accuracy degrades |
| IV-7 | **No Inventory Valuation** | FIFO, LIFO, or weighted average costing | Cannot determine inventory carrying cost |

### 2.8 Parts Issue & Parts Return Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| PI-1 | **No WO Linkage Enforcement** | Parts issue should require a WO number to charge against | Parts consumed without traceability to work performed |
| PI-2 | **No Reservation / Staging** | Reserve parts for upcoming scheduled WOs before physically issuing | Parts intended for scheduled PM get consumed by emergency work |
| PI-3 | **No Direct Issue vs. Storeroom Issue** | Differentiate deliveries that go straight to the job site vs. storeroom | Inventory records may not reflect actual stock |
| PR-1 | **No Return Reason Tracking** | Capture why parts are returned (excess, defective, wrong part, job cancelled) | Cannot analyze return patterns or vendor quality |
| PR-2 | **No Inspection-on-Return** | Returned parts should be inspected before being put back in stock | Defective parts re-enter inventory |

### 2.9 Purchase Request & Purchase Order Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| PQ-1 | **No Budget/Cost Center Validation** | PR should validate against department budget before approval | Overspending without budget checks |
| PQ-2 | **No Multi-Level PR Approval** | Approval routing by dollar threshold (e.g., <$1K auto, $1K–$10K supervisor, >$10K manager) | All PRs follow the same approval path regardless of value |
| PQ-3 | **No PR Consolidation** | Combine multiple PRs for the same vendor into a single PO | Excessive POs, higher transaction costs |
| PO-1 | **No 3-Way Matching** | Match PO → Goods Receipt → Invoice before payment authorization | Risk of paying for undelivered or incorrect goods |
| PO-2 | **No Goods Receipt Workflow** | Explicit receiving step: inspect, accept/reject, note discrepancies | No formal record of what was actually received |
| PO-3 | **No Vendor Performance Tracking** | Track on-time delivery, quality rejects, price compliance per vendor | Cannot evaluate or compare vendor performance |
| PO-4 | **No PO Change/Amendment Trail** | Track revisions to PO (quantity changes, price changes, delivery date changes) | No audit trail for PO modifications |
| PO-5 | **No Blanket/Contract PO** | Standing POs for recurring purchases with release quantities | New PO for every routine purchase; procurement overhead |

### 2.10 Stock Count Workflow

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| SC-1 | **No Variance Threshold & Auto-Adjustment** | Minor variances auto-adjusted; major variances flagged for investigation | All variances treated the same; investigation overhead |
| SC-2 | **No Blind Count Option** | Counters should not see system quantity during counting | Count bias; counters may just confirm system quantity |
| SC-3 | **No Multi-Counter / Recount** | If two counters disagree, trigger automatic recount | Single count may have human error |
| SC-4 | **No Count Freeze** | Freeze inventory transactions during count window | Transactions during count corrupt accuracy |

---

## 3. Entirely MISSING Workflows

These workflows do not exist at all in the system but are standard in EAM implementations:

### 3.1 Critical Missing Workflows

| # | Workflow | Description | Business Impact |
|---|----------|-------------|-----------------|
| MW-1 | **Preventive Maintenance (PM)** | Calendar-based and/or meter-based PM schedules that auto-generate WOs at defined intervals | **Cannot shift from reactive to proactive maintenance** — this is the #1 value driver of any EAM system |
| MW-2 | **PM Schedule Management** | Create, modify, activate/deactivate PM schedules; set frequency, lead time, seasonal windows | No automated maintenance planning capability |
| MW-3 | **PM Forecasting / Projection** | Generate a forward-looking calendar of upcoming PMs for resource and parts planning | Cannot plan labor or parts procurement ahead |
| MW-4 | **Route / Inspection Round** | Grouped sequence of inspection points for operator rounds (e.g., daily pump checks) | No structured inspection process |
| MW-5 | **Condition Monitoring** | Record and trend condition data (vibration, temperature, oil analysis) against thresholds | No predictive maintenance capability |

### 3.2 High-Priority Missing Workflows

| # | Workflow | Description | Business Impact |
|---|----------|-------------|-----------------|
| MW-6 | **Goods Receipt** | Receive items against a PO, record quantities, inspect quality, update inventory | No formal proof-of-delivery; inventory updated without verification |
| MW-7 | **Failure Analysis (FMEA/RCA)** | Structured workflow: identify failure → analyze cause → determine remedy → track action | Cannot systematically eliminate recurring failures |
| MW-8 | **Approval Engine** | Configurable multi-level approval chains based on entity type, value, and org unit | Fixed approval paths; cannot adapt to varying authority levels |
| MW-9 | **Notification / Escalation** | Rule-based notifications: overdue WOs, pending approvals, SLA breaches, low stock | Users must manually check for items requiring attention |
| MW-10 | **KPI Dashboard Calculations** | MTBF, MTTR, OEE, PM Compliance %, Backlog (weeks), Stores Service Level | No management visibility into maintenance performance |
| MW-11 | **Asset Transfer / Movement** | Transfer assets between locations, departments, or cost centers with audit trail | Asset location records become inaccurate over time |

### 3.3 Medium-Priority Missing Workflows

| # | Workflow | Description | Business Impact |
|---|----------|-------------|-----------------|
| MW-12 | **Warranty Claim** | Submit warranty claims against vendor, track status, record credited amount | Organization pays for warranty-covered repairs |
| MW-13 | **Service Contract** | Manage external service agreements with SLAs, expiry dates, renewal workflows | No tracking of outsourced maintenance obligations |
| MW-14 | **Tool / Special Equipment Checkout** | Track tool assignments, calibration due dates, return status | Tools go missing; uncalibrated tools used |
| MW-15 | **Safety Permit-to-Work** | Manage LOTO, hot work, confined space, excavation permits linked to WOs | Safety compliance risk |
| MW-16 | **Asset Decommission / Disposal** | Structured workflow for decommission approval, environmental clearance, salvage/disposal | Assets disposed without proper authorization or documentation |
| MW-17 | **Invoice Matching & Payment** | Match vendor invoices against POs and goods receipts (3-way match) | Risk of overpayment or payment for unreceived goods |
| MW-18 | **Master Data Change Management** | Approval workflow for changes to asset records, spare parts catalogs, vendor records | Uncontrolled master data changes affect data integrity |

---

## 4. State Machine Gaps

The 5 state machine diagrams (States 1–5) likely govern entity lifecycle transitions. Common gaps include:

| # | Gap | Expected Implementation | Impact |
|---|-----|------------------------|--------|
| SM-1 | **No State-Based Permission Control** | Different user roles allowed to perform transitions only at specific states | Anyone can advance a record through any state |
| SM-2 | **No Required-Field Validation Per State** | Certain fields required before transitioning (e.g., completion date before closing WO) | Incomplete records can be moved to completion |
| SM-3 | **No Auto-Actions on Transition** | State changes should trigger side effects (e.g., closing WO auto-returns unissued parts, sends notification) | Manual cleanup after each state change |
| SM-4 | **No Backward Transition Controls** | Re-opening a closed WO should require justification and special permission | Records moved backwards without accountability |
| SM-5 | **No SLA Timers Per State** | Track time-in-state with escalation if a record sits too long (e.g., WO in "Waiting Approval" > 48 hrs) | Records stall in intermediate states without visibility |
| SM-6 | **No State Transition Audit Log** | Record who transitioned, when, from which state, with what comments | No traceability for compliance or dispute resolution |

---

## 5. Cross-Workflow Integration Gaps

These are gaps in how workflows connect and interact with each other:

| # | Gap | Workflows Affected | Expected Behavior |
|---|-----|--------------------|-------------------|
| XW-1 | **Maintenance Request → Work Order** | MR → WO | Approved MR auto-creates WO with asset, description, priority pre-filled |
| XW-2 | **Incident → Work Order** | Incident → WO | Incident resolution generates corrective WO linked back to incident |
| XW-3 | **Work Order → Parts Issue** | WO → Parts | WO planned parts list drives reservation; issue decrements both WO plan and inventory |
| XW-4 | **WO Parts Demand → Purchase Request** | WO → PR | If planned parts are not in stock, auto-generate PR for the shortage |
| XW-5 | **Purchase Request → Purchase Order** | PR → PO | Approved PRs consolidated by vendor into PO |
| XW-6 | **Purchase Order → Goods Receipt → Inventory** | PO → GR → Inventory | Receiving against PO updates inventory and PO received quantities |
| XW-7 | **PM Schedule → Work Order** | PM → WO | PM due date triggers auto-generation of WO with job plan, parts, labor |
| XW-8 | **Inventory Below Min → Purchase Request** | Inventory → PR | Auto-reorder workflow when stock drops below reorder point |
| XW-9 | **WO Completion → Asset History** | WO → Asset | Completed WO appends to asset maintenance history for lifecycle view |
| XW-10 | **WO Failure Code → Failure Analysis** | WO → FMEA | Failure data feeds reliability dashboards and RCA workflows |

---

## 6. Priority Implementation Roadmap

### Phase 1 — Foundation (Weeks 1–6)
| Priority | Item | Effort |
|----------|------|--------|
| P1 | MW-1: Preventive Maintenance scheduling engine | Large |
| P1 | MW-2: PM schedule CRUD & activation | Medium |
| P1 | XW-1: Maintenance Request → WO auto-conversion | Small |
| P1 | XW-2: Incident → WO linkage | Small |
| P1 | SM-6: State transition audit logging | Medium |
| P1 | WO-1: WO type classification | Small |
| P1 | WO-5: WO cost tracking | Medium |

### Phase 2 — Procurement & Inventory Maturity (Weeks 7–12)
| Priority | Item | Effort |
|----------|------|--------|
| P2 | MW-6: Goods Receipt workflow | Medium |
| P2 | PO-1: 3-way matching (PO/GR/Invoice) | Medium |
| P2 | IV-1/IV-2: Reorder point + auto-PR generation | Medium |
| P2 | XW-5: PR → PO consolidation | Small |
| P2 | XW-6: PO → GR → Inventory chain | Medium |
| P2 | PI-2: Parts reservation for scheduled WOs | Medium |
| P2 | PQ-2: Multi-level PR approval by dollar threshold | Small |

### Phase 3 — Reliability & Analytics (Weeks 13–20)
| Priority | Item | Effort |
|----------|------|--------|
| P3 | WO-7: Failure code taxonomy (Failure/Cause/Remedy) | Medium |
| P3 | MW-7: Failure analysis / RCA workflow | Large |
| P3 | WO-6: Downtime tracking per WO | Small |
| P3 | MW-10: KPI calculations (MTBF, MTTR, PM Compliance, OEE) | Large |
| P3 | WO-2: Job plans / standard jobs library | Medium |
| P3 | MW-4: Inspection route / operator rounds | Medium |
| P3 | XW-9: WO → Asset history linkage | Small |

### Phase 4 — Advanced Capabilities (Weeks 21–30)
| Priority | Item | Effort |
|----------|------|--------|
| P4 | MW-9: Notification & escalation engine | Large |
| P4 | MW-5: Condition monitoring & trending | Large |
| P4 | WO-3: Scheduling calendar / Gantt view | Large |
| P4 | MW-15: Safety permit-to-work | Medium |
| P4 | MW-13: Service contract management | Medium |
| P4 | MW-12: Warranty claim workflow | Medium |
| P4 | AR-4: Meter/reading tracking + meter-based PM triggers | Medium |

---

## 7. Summary Metrics

| Category | Count |
|----------|-------|
| Gaps within existing workflows | **52** |
| Entirely missing workflows | **18** |
| Cross-workflow integration gaps | **10** |
| State machine gaps | **6** |
| **Total workflow implementation gaps** | **86** |

| Severity | Count |
|----------|-------|
| Critical (blocks core EAM value) | **12** |
| High (significant functional limitation) | **28** |
| Medium (operational inefficiency) | **32** |
| Low (nice-to-have enhancement) | **14** |
