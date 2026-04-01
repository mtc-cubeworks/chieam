# EAM-CHI — Added Features Report

**Date:** March 24, 2026
**Commits:** `49bde84` → `35ccd25` (15 commits on `main`)
**Scope:** Features, models, business logic, services, security, and documentation added on top of the base EAM platform

---

## Executive Summary

Starting from the base EAM platform (a generic FastAPI + SQLAlchemy + Nuxt 3 scaffold with basic CRUD, workflow engine, and ~100 entities), the following work was done across **6 development phases + 3 hardening rounds** to build a production-grade Enterprise Asset Management system for Composable Holdings Inc. (CHI) and its ITBA instance.

| Metric | Count |
|--------|-------|
| New entity models created | 22 |
| Existing models enhanced (new columns) | 15+ |
| New columns added across all tables | ~160+ |
| New service modules | 11 |
| New API action handlers | 8 |
| Workflow hooks implemented | 25+ |
| RBAC roles defined | 15 |
| Row-level data scopes | 4 |
| State machine extensions | 6 |
| Alembic migrations added | 10 |
| DSL model files generated | 12 |
| Documentation files | 14 |
| Edge case tests documented | 64 |

---

## 1. Workflow Gap Coverage (86 Gaps Resolved)

Identified 86 workflow gaps between the DSL design specifications and the base implementation. All 86 were resolved across six phases.

### Phase 1 — Core Workflow Infrastructure (`49bde84`)

| Feature | Description |
|---------|-------------|
| **Stock Ledger Service** | `stock_ledger.py` — Full inventory audit trail wired into all 5 mutation points: item issue, item return, purchase receipt, inventory adjustment, purchase return |
| **WO Auto-Complete** | Work Order automatically completes when all child Work Order Activities are finished |
| **Scheduler Service** | `scheduler.py` — Background task runner for SLA monitoring, daily reorder checks, overdue WO flagging |
| **Maintenance Hooks** | PMA auto-calendar scheduling, sensor-based condition monitoring → auto maintenance request |
| **Core EAM Hooks** | Leave application labor availability checks, labor name synchronization |
| **Incident Workflow** | Full lifecycle: report → investigate → resolve → close |
| **Transfer Workflows** | Asset transfer, transfer receipt, and purchase return workflow handlers |
| **PR/PO Auto-Totals** | Purchase request line row number generation, PR and PO total value auto-rollup |
| **WO Cost Rollup** | Automatic aggregation of labor + equipment + parts costs on work orders |
| **Reorder Auto-PR** | Inventory below reorder point automatically generates a purchase request |

### Phase 2 — Advanced Business Logic (`5ab5cdb`)

| Feature | Description |
|---------|-------------|
| **Audit Logging** | Workflow state transitions now generate full audit trail entries |
| **Parts Reservation** | `parts_reservation.py` — Auto-reserve inventory on WO approval, auto-release on cancel/complete |
| **Approval Engine** | `approval_engine.py` — Multi-level approval for purchase requests and purchase orders with configurable thresholds |
| **PR→PO Consolidation** | `pr_po_consolidation.py` — Server action to merge multiple approved PR lines into a single PO |
| **Downtime Tracking** | Work Order gains downtime_start, downtime_end, downtime_hours fields |
| **Failure Code Taxonomy** | New `cause_code` and `remedy_code` models for structured failure classification |
| **KPI Service** | `kpi.py` — Calculates MTBF, MTTR, PM Compliance, OEE, and other maintenance KPIs |
| **Asset Maintenance History** | Auto-logged when a Work Order completes — tracks all maintenance performed per asset |

### Phase 3+4 — New Entity Models (`d2b015c`)

11 new entities with full CRUD, workflow, and business logic:

| New Entity | Module | Purpose |
|------------|--------|---------|
| `failure_analysis` | maintenance_mgmt | Root cause analysis linked to work orders |
| `corrective_action` | maintenance_mgmt | CAPA tracking linked to failure analysis |
| `job_plan` | work_mgmt | Reusable job templates for work orders |
| `job_plan_task` | work_mgmt | Task steps within a job plan |
| `inspection_route` | maintenance_mgmt | Planned inspection paths through assets |
| `inspection_point` | maintenance_mgmt | Individual checkpoints on a route |
| `safety_permit` | work_mgmt | Permit-to-work (LOTO, hot work, confined space) |
| `service_contract` | purchasing_stores | Vendor service agreements with SLAs |
| `warranty_claim` | asset_management | Warranty claim tracking per asset |
| `meter` | asset_management | Runtime hours / odometer / cycle tracking |
| `meter_reading` | asset_management | Individual meter reading records |

Business logic added:
- Meter reading hooks with automatic rollover detection
- Auto failure analysis creation when WO completes with failure codes
- Job plan apply-to-WO server action
- SLA escalation email notifications
- Sensor threshold alerting with automatic MR generation

### Phase 5 — Major Model Enhancements (`b1a7be8`)

**46 new columns across 4 core tables:**

| Model | Columns Added | Features Enabled |
|-------|---------------|-----------------|
| **Asset** (19 cols) | lifecycle_state, parent_asset, functional_location, criticality, risk_score, warranty_start/end/vendor/terms, manufacturer/model/serial, rated_power/voltage/current, purchase_date/cost, depreciation_method/rate/salvage_value | Full asset lifecycle, hierarchy, warranty, nameplate specs, depreciation |
| **Work Order** (19 cols) | job_plan, scheduled_start/finish, actual_start/finish, approved_by/date, estimated/actual cost of labor/equipment/parts, safety_required, loto_required, safety_instructions, feedback_rating/comments, follow_up_wo, parent_wo | Job plan linkage, scheduling, approval, cost tracking, safety, feedback |
| **Incident** (5 cols) | incident_subtype, osha_recordable, regulatory_report_required, regulatory_report_date, failure_analysis | OSHA/regulatory compliance tracking |
| **Maintenance Request** (5 cols) | sla_response_due, sla_resolution_due, sla_breached, sla_breach_date, request_category | SLA enforcement and tracking |

**3 new models:**

| New Entity | Purpose |
|------------|---------|
| `vendor_invoice` | Invoice tracking for 3-way matching |
| `vendor_invoice_line` | Line items on vendor invoices |
| `tool_checkout` | Tool/equipment checkout and return tracking |

**New business logic:**
- **MR Priority Auto-Calc**: asset criticality × severity → automatic priority
- **Duplicate MR Detection**: prevents duplicate requests for the same asset
- **3-Way Matching**: `three_way_matching.py` — PO vs Goods Receipt vs Invoice reconciliation
- **Follow-Up WO**: server action to create linked follow-up work orders

### Phase 6 — Complete Coverage (86/86) (`bbd3b70`)

**55+ new columns across 11 tables + 3 new tables:**

| Model | Key Additions |
|-------|--------------|
| `work_order_activity` | sequence, predecessor, dependency_type, acceptance_criteria |
| `work_order_labor` | shift, rate, rate_type, overtime_multiplier, labor_type |
| `item_return` | return_reason, inspection_required/status/notes |
| `item_issue` | work_order FK, issue_destination, require_wo |
| `purchase_request` | budget_code, budget_amount, total_amount |
| `vendor` | 11 fields (contact, rating, insurance, certifications, payment terms) |
| `purchase_order` | 10 fields (amendment tracking, blanket/contract PO, delivery terms) |
| `stock_count` | variance_threshold, auto_adjust, blind_count |
| `inventory` | lot_number, expiry_date |
| `item` | reorder_point/qty, min/max stock, lot tracking, cycle count frequency |

**3 new models:**

| New Entity | Purpose |
|------------|---------|
| `condition_monitoring` | IoT sensor-based condition tracking |
| `asset_transfer` | Asset movement between locations/sites |
| `master_data_change` | Change request workflow for master data modifications |

**Major business logic additions:**
- **Asset Clone**: Server action to duplicate assets with all properties
- **Vendor Performance**: Auto-calculated from purchase receipts (quality, delivery, price scores)
- **Budget Validation**: PR submission checks against annual budget
- **WO Parts Shortage Auto-PR**: Missing parts automatically generate purchase requests
- **Failure Analysis Routing**: WO failure codes auto-create failure analysis records
- **FMEA Service**: `fmea_service.py` — 5-Why analysis, Fishbone diagrams, RPN calculation
- **SMTP Notification Service**: `notification_service.py` — Lifecycle email notifications for MR and WO
- **Master Data Change Approval**: Change requests with auto-apply on approval
- **Cycle Count Auto-Scheduling**: Daily 4AM scheduler for inventory cycle counts

---

## 2. State Machine Extensions

Six enhancements to the base workflow/state machine engine (`state_machine_extensions.py`):

| ID | Feature | Description |
|----|---------|-------------|
| SM-1 | **Field Permission Control** | Per-state read-only field enforcement — certain fields become uneditable in specific workflow states |
| SM-2 | **Required Field Validation** | Per-transition required field checks — ensures mandatory fields are filled before state change |
| SM-3 | **Document Mutation Guards** | Hooks for validating documents before allowing transitions |
| SM-4 | **Backward Transition Justification** | Forces users to provide a reason when moving a workflow backward (e.g., Approved → Draft) |
| SM-5 | **Per-State SLA Escalation** | Configurable SLA thresholds per workflow state with automatic escalation |
| SM-6 | **Enhanced Audit Logging** | State transitions record justification text, SLA breach metadata, and user context |

---

## 3. Row-Level RBAC Data Scoping (`d93633c`)

Implemented a full hierarchical data access control system:

### Architecture
- `data_scope` field added to Role model with 4 levels: **own → team → site → all**
- `created_by` / `modified_by` tracking on all ~140 entity tables via BaseModel
- `reports_to` self-FK on Employee for supervisor hierarchy lookup
- `build_scope_filter()` in RBACService generates WHERE clauses based on user's role scope

### Scope Levels

| Scope | Visibility | Use Case |
|-------|-----------|----------|
| `own` | Only records the user created | Technician, Requisitioner |
| `team` | Records from user's department(s) | Supervisor, MaintenanceSupervisor |
| `site` | Records from user's assigned site(s) | SiteManager, AssetManager, Buyer, etc. |
| `all` | All records, no filter | SystemManager, Executive |

### Applied To
- Entity list (`/list`)
- Entity list-view (`/list-view`)
- Entity detail (`/{id}`)
- Entity update (`/{id}`)
- Entity delete (`/{id}`)
- Import/export operations

---

## 4. RBAC Roles (15 Roles)

### General Roles (6)

| Role | Scope | Purpose |
|------|-------|---------|
| SystemManager | all | Full system access, all modules |
| Executive | all | Read-only access across all sites (dashboards/reports) |
| SiteManager | site | Full CRUD within assigned site(s) |
| Supervisor | team | Department-level oversight |
| Technician | own | CRUD on own records |
| Viewer | site | Read-only within assigned site |

### Asset Management (1)

| Role | Scope | Purpose |
|------|-------|---------|
| AssetManager | site | Manage assets, locations, systems within site |

### Procurement & Stores (5)

| Role | Scope | Purpose |
|------|-------|---------|
| PurchaseManager | site | Approve and manage all procurement |
| Buyer | site | Create/manage POs, RFQs, vendor invoices |
| Requisitioner | own | Create purchase requests, view status |
| StoresManager | site | Manage inventory, stores, stock counts |
| Storekeeper | site | Issue, receive, transfer, and count stock |

### Maintenance Management (3)

| Role | Scope | Purpose |
|------|-------|---------|
| MaintenanceManager | site | Manage all maintenance activities at site |
| Planner | site | Plan and schedule maintenance work |
| MaintenanceSupervisor | team | Supervise maintenance team, approve WOs |

---

## 5. Security Hardening (Rounds 1–3)

### Round 1 (`0bc7b10`)

| Fix | Description |
|-----|-------------|
| **Rate Limiter** | SlowAPI rate limiter attached to FastAPI; 5/minute on `/login` and `/boot` |
| **Logout Endpoint** | `POST /auth/logout` to clear refresh_token cookie |
| **SECRET_KEY Validation** | Blocks startup if SECRET_KEY is the default/weak value |
| **Database Indexes** | `index=True` on `created_at`, `created_by`, `modified_by` in BaseModel; workflow_state, site, department, key FKs across 11 models |
| **Missing Workflow Hooks** | Registered 8 missing handlers: safety_permit, tool_checkout, warranty_claim, sales_order, service_contract, condition_monitoring, corrective_action, failure_analysis |
| **Admin Workflow Save** | Implemented the admin `/workflow/save` endpoint (was returning "Not implemented") |

### Round 2 (`12547ef`)

| Fix | Description |
|-----|-------------|
| **Auth Bypass Fix** | Unauthenticated requests now return 401 instead of falling through as anonymous |
| **Security Headers Middleware** | X-Content-Type-Options, X-Frame-Options, Referrer-Policy, X-XSS-Protection |
| **Stronger SECRET_KEY** | Checks against known weak values + enforces minimum 32 characters |
| **NGINX Hardening** | Security headers, `client_max_body_size 15M`, proxy timeouts |
| **Frontend Port Fix** | Corrected 3010→3015 to match NGINX reverse proxy config |
| **Performance Indexes** | 234 indexes created on CHI database; 240 on ITBA |

### Round 3 (`35ccd25`)

| Fix | Description |
|-----|-------------|
| **Model–DB Schema Alignment** | Fixed 7 entity models whose columns didn't match the actual database tables, causing 500 errors on list-view endpoints: warranty_claim, meter, job_plan, corrective_action, inspection_point, safety_permit, service_contract |

---

## 6. Edge Case Fixes (`399259d`, `7a3c8c6`)

### Critical Bug Fixes

| Category | Fixes |
|----------|-------|
| **RBAC Bypass** | Import/export now respects row-level scoping; closed anonymous fallback path |
| **Race Conditions** | Optimistic locking on concurrent workflow transitions |
| **Double Hook Prevention** | Guard against workflow hooks firing twice in the same transaction |
| **Optimistic Locking** | Version-based conflict detection on concurrent document updates |

### Workflow Improvements

| Feature | Description |
|---------|-------------|
| **Dead-End State Fixes** | `patch_dead_end_transitions.py` — Identifies and repairs states with no outgoing transitions |
| **WO Reopen** | Clears downtime fields, reverts completed WOAs to in_progress |
| **WO Cancel Cascade** | Cascades cancel to all active Work Order Activities |
| **PO Cancel → PR Revert** | Canceling a PO reverts linked PR Lines back to "approved" for re-procurement |
| **PR Revise** | Resets non-rejected PR lines back to draft |

---

## 7. New Services Summary

| Service File | Purpose |
|--------------|---------|
| `approval_engine.py` | Multi-level configurable approval workflows |
| `document_mutation.py` | Pre-save document hooks and guards |
| `fmea_service.py` | Failure Mode & Effects Analysis (5-Why, Fishbone, RPN) |
| `kpi.py` | Maintenance KPIs: MTBF, MTTR, PM Compliance, OEE |
| `notification_service.py` | SMTP email notifications for MR/WO lifecycle events |
| `parts_reservation.py` | Auto-reserve/release inventory for work order parts |
| `pr_po_consolidation.py` | Merge multiple approved PR lines into a single purchase order |
| `scheduler.py` | Background tasks: SLA monitoring, reorder checks, cycle counts |
| `state_machine_extensions.py` | 6 workflow engine enhancements (see Section 2) |
| `stock_ledger.py` | Inventory audit trail for all stock movements |
| `three_way_matching.py` | PO vs Goods Receipt vs Invoice reconciliation |

---

## 8. New API Actions & Server Actions

| Action Handler | Purpose |
|----------------|---------|
| `asset_clone_actions.py` | Clone an asset with all properties and sub-records |
| `follow_up_wo_actions.py` | Create a linked follow-up work order |
| `job_plan_actions.py` | Apply a job plan template to a work order |
| `parts_reservation_actions.py` | Manual parts reserve/release from WO |
| `pr_consolidation_actions.py` | Consolidate PR lines into a PO |
| `vendor_performance_hooks.py` | Auto-calculate vendor ratings on receipt |

---

## 9. DSL Models Generated (12)

Full domain-specific language models covering the entire EAM domain:

| DSL File | Domain |
|----------|--------|
| `asset_management.dbml` | Asset hierarchy, meters, warranties, transfers |
| `core_eam.dbml` | Organizations, employees, labor, sites |
| `maintenance_mgmt.dbml` | PM plans, inspections, failure analysis, condition monitoring |
| `purchasing_stores.dbml` | Procurement, inventory, vendors, contracts |
| `work_mgmt.dbml` | Work orders, job plans, safety permits, tools |
| `eam_business_logic.blml` | Business rules and validation logic |
| `eam_ml_model.aiml` | Machine learning / predictive maintenance model |
| `eam_ot_model.otml` | Operational technology / IoT integration model |
| `eam_reporting.lrml` | Reporting and analytics definitions |
| `eam_security.sdml` | Security policies and access control model |
| `eam_ux.uxml` | User experience / UI component specifications |
| `eam_web_design.wdml` | Web design system and layout specifications |

---

## 10. Documentation Deliverables

| Document | Format | Content |
|----------|--------|---------|
| **USER_MANUAL** | MD + DOCX | Full user guide v1.1 with 14 chapters, 12 role definitions, row-level scoping, known limitations |
| **TEST_GUIDE** | MD + DOCX | 144 test cases (80 base + 64 edge case) across 28 test categories (TC-01 through TC-28) |
| **WORKFLOW_GUIDE** | MD + DOCX | Comprehensive workflow engine docs, entity lifecycle diagrams, cross-entity flow descriptions |
| **GAP_ANALYSIS** | MD | 86 identified workflow gaps with status tracking |
| **WORKFLOW_GAP_ANALYSIS** | MD | Detailed gap-by-gap analysis with implementation notes |
| **ARCHITECTURE** | MD | System architecture documentation |
| **SEEDING_GUIDE** | MD | Database seeding procedures |

---

## 11. Database Migrations Added (10)

| Migration | Purpose |
|-----------|---------|
| `f1a2b3c4d5e6` | WO downtime and failure fields |
| `g2b3c4d5e6f7` | Cause code and remedy code tables |
| `h3c4d5e6f7g8` | Asset maintenance history table |
| `i4d5e6f7g8h9` | Phase 3+4 tables (11 new entities) |
| `j5e6f7g8h9i0` | Remaining gap fields and tables |
| `k6f7g8h9i0j1` | Phase 6 coverage fields and tables |
| `m1_merge_heads` | Merge migration heads |
| `n2_rbac_row_level_scoping` | RBAC data_scope, created_by/modified_by, reports_to |
| `add_performance_indexes` | Performance indexes across all tables |

---

## 12. Infrastructure & Deployment

| Item | Description |
|------|-------------|
| **NGINX Config** | `chieam.cubeworksinnovation.com.nginx` — Reverse proxy with security headers, body size limits, timeouts |
| **Sync Script** | `sync_chi_to_itba.sh` — Automated CHI→ITBA database/code synchronization |
| **Clone Script** | `clone_to_chi.sh` — Instance cloning utility |
| **Frontend Port** | Corrected ecosystem.config.cjs for port 3015 |
| **Dual Deployment** | Both CHI (port 8015/3015) and ITBA (port 8014/3014) instances maintained |

---

## Codebase Statistics

| Category | Count |
|----------|-------|
| Total entity JSON configs | 136 |
| Total SQLAlchemy models | 159 |
| Total service modules | 23 |
| Total workflow hook files | 5 |
| Total API action files | 38 |
| Total Alembic migrations | 46 |
| Total DSL model files | 12 |
| Total RBAC roles | 15 |
| Total commits | 15 |
| Files changed | 153 |
| Lines added | ~29,500+ |
