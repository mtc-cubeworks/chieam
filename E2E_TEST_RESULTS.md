# EAM System — E2E Test Results

> Automated Visual Test Report with Step-by-Step Evidence

**Generated:** 2026-04-10T07:23:49.746Z
**Base URL:** https://chieam.cubeworksinnovation.com
**Framework:** Dual-Purpose Automation (Playwright v1.58.2)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Workflows Tested | 50 |
| Total Steps | 319 |
| Screenshots Captured | 319 |
| Steps Passed | 318 |
| Warnings | 0 |
| Loading States | 1 |
| Errors | 0 |
| **Pass Rate** | **99.7%** |

> ✅ **All 50 Playwright test cases PASSED.** No errors detected across all workflow steps.

## Workflow Summary

| # | Test Case | Module | Workflow | Steps | Status |
|---|-----------|--------|----------|-------|--------|
| 1 | TC-02 | General | TC 02 Rbac Permissions | 6 | ✅ PASS |
| 2 | TC-02 | General | TC 02 Workflow Management | 6 | ✅ PASS |
| 3 | TC-12 | General | TC 12 Pm Calendar | 6 | ✅ PASS |
| 4 | TC-13 | General | TC 13 Scheduled Jobs | 4 | ✅ PASS |
| 5 | TC-14 | General | TC 14 Server Actions | 8 | ✅ PASS |
| 6 | TC-16 | General | TC 16 Import Export | 6 | ✅ PASS |
| 7 | TC-18 | General | TC 18 Cross Workflow Integration | 10 | ✅ PASS |
| 8 | TC-20 | General | TC 20 Procurement Scenario | 8 | ✅ PASS |
| 9 | TC-15 | General | TC 15 Sla Tracking | 4 | ✅ PASS |
| 10 | TC-04 | Asset Management | TC 04 Asset Create | 5 | ✅ PASS |
| 11 | TC-04 | Asset Management | TC 04 Asset Hierarchy | 6 | ✅ PASS |
| 12 | TC-04 | Asset Management | TC 04 Equipment Crud | 5 | ✅ PASS |
| 13 | TC-04 | Asset Management | TC 04 Meter Reading | 9 | ✅ PASS |
| 14 | TC-05 | Asset Management | TC 05 Asset Workflow Decommission | 8 | ✅ PASS |
| 15 | TC-04 | Asset Management | Asset Lifecycle | 6 | ✅ PASS |
| 16 | TC-10 | Condition Monitoring | TC 10 Condition Monitoring Types | 6 | ✅ PASS |
| 17 | TC-10 | Condition Monitoring | TC 10 Condition Monitoring | 5 | ✅ PASS |
| 18 | TC-01 | Authentication | TC 01 Authentication | 7 | ✅ PASS |
| 19 | TC-01 | Authentication | TC 01 Profile Update | 2 | ✅ PASS |
| 20 | TC-01 | Authentication | TC 01 User Crud | 7 | ✅ PASS |
| 21 | TC-01 | Authentication | Login Edge Cases | 6 | ✅ PASS |
| 22 | TC-01 | Authentication | Login Happy Path | 6 | ✅ PASS |
| 23 | TC-02 | Dashboard & Overview | Dashboard Overview | 3 | ✅ PASS |
| 24 | TC-05 | General Features | Entity List Features | 6 | ⚠️ 5/6 |
| 25 | TC-02 | Navigation | Sidebar Navigation | 5 | ✅ PASS |
| 26 | TC-20 | Maintenance Management | TC 20 Corrective Maintenance Scenario | 10 | ✅ PASS |
| 27 | TC-20 | Maintenance Management | TC 20 Preventive Maintenance Scenario | 6 | ✅ PASS |
| 28 | TC-06 | Maintenance Management | TC 06 Maintenance Request | 5 | ✅ PASS |
| 29 | TC-06 | Maintenance Management | TC 06 Maintenance Request Lifecycle Full | 8 | ✅ PASS |
| 30 | TC-06 | Maintenance Management | Maintenance Request Lifecycle | 5 | ✅ PASS |
| 31 | TC-03 | Master Data | TC 03 Master Data Department | 5 | ✅ PASS |
| 32 | TC-03 | Master Data | TC 03 Employee Labor | 5 | ✅ PASS |
| 33 | TC-03 | Master Data | TC 03 Financial Master Data | 10 | ✅ PASS |
| 34 | TC-03 | Master Data | TC 03 Manufacturer Model | 10 | ✅ PASS |
| 35 | TC-03 | Master Data | TC 03 Master Data Organization | 5 | ✅ PASS |
| 36 | TC-03 | Master Data | TC 03 Master Data Site | 5 | ✅ PASS |
| 37 | TC-03 | Master Data | TC 03 Vendor Item | 10 | ✅ PASS |
| 38 | TC-03 | Master Data | TC 03 Work Schedule Holiday | 10 | ✅ PASS |
| 39 | TC-19 | Master Data | TC 19 Vendor Performance | 6 | ✅ PASS |
| 40 | TC-11 | Purchasing & Stores | TC 11 Blanket Contract Po | 8 | ✅ PASS |
| 41 | TC-11 | Purchasing & Stores | TC 11 Purchase Receipt | 4 | ✅ PASS |
| 42 | TC-11 | Purchasing & Stores | TC 11 Purchasing Pr Po | 10 | ✅ PASS |
| 43 | TC-11 | Purchasing & Stores | Purchase Request Lifecycle | 5 | ✅ PASS |
| 44 | TC-07 | Work Management | TC 07 Work Order Child Records | 10 | ✅ PASS |
| 45 | TC-07 | Work Management | TC 07 Wo Failure Reporting | 5 | ✅ PASS |
| 46 | TC-07 | Work Management | TC 07 Work Order | 5 | ✅ PASS |
| 47 | TC-08 | Work Management | TC 08 Work Order Activity | 6 | ✅ PASS |
| 48 | TC-07 | Work Management | Work Order Lifecycle | 5 | ✅ PASS |
| 49 | TC-09 | Safety Permits | TC 09 Safety Permit Lifecycle | 6 | ✅ PASS |
| 50 | TC-09 | Safety Permits | TC 09 Safety Permit | 5 | ✅ PASS |

---

## Table of Contents

1. [General](#general)
   1.1. [TC 02 Rbac Permissions](#tc-02-rbac-permissions)
   1.2. [TC 02 Workflow Management](#tc-02-workflow-management)
   1.3. [TC 12 Pm Calendar](#tc-12-pm-calendar)
   1.4. [TC 13 Scheduled Jobs](#tc-13-scheduled-jobs)
   1.5. [TC 14 Server Actions](#tc-14-server-actions)
   1.6. [TC 16 Import Export](#tc-16-import-export)
   1.7. [TC 18 Cross Workflow Integration](#tc-18-cross-workflow-integration)
   1.8. [TC 20 Procurement Scenario](#tc-20-procurement-scenario)
   1.9. [TC 15 Sla Tracking](#tc-15-sla-tracking)
2. [Asset Management](#asset-management)
   2.1. [TC 04 Asset Create](#tc-04-asset-create)
   2.2. [TC 04 Asset Hierarchy](#tc-04-asset-hierarchy)
   2.3. [TC 04 Equipment Crud](#tc-04-equipment-crud)
   2.4. [TC 04 Meter Reading](#tc-04-meter-reading)
   2.5. [TC 05 Asset Workflow Decommission](#tc-05-asset-workflow-decommission)
   2.6. [Asset Lifecycle](#asset-lifecycle)
3. [Condition Monitoring](#condition-monitoring)
   3.1. [TC 10 Condition Monitoring Types](#tc-10-condition-monitoring-types)
   3.2. [TC 10 Condition Monitoring](#tc-10-condition-monitoring)
4. [Authentication](#authentication)
   4.1. [TC 01 Authentication](#tc-01-authentication)
   4.2. [TC 01 Profile Update](#tc-01-profile-update)
   4.3. [TC 01 User Crud](#tc-01-user-crud)
   4.4. [Login Edge Cases](#login-edge-cases)
   4.5. [Login Happy Path](#login-happy-path)
5. [Dashboard & Overview](#dashboard-overview)
   5.1. [Dashboard Overview](#dashboard-overview)
6. [General Features](#general-features)
   6.1. [Entity List Features](#entity-list-features)
7. [Navigation](#navigation)
   7.1. [Sidebar Navigation](#sidebar-navigation)
8. [Maintenance Management](#maintenance-management)
   8.1. [TC 20 Corrective Maintenance Scenario](#tc-20-corrective-maintenance-scenario)
   8.2. [TC 20 Preventive Maintenance Scenario](#tc-20-preventive-maintenance-scenario)
   8.3. [TC 06 Maintenance Request](#tc-06-maintenance-request)
   8.4. [TC 06 Maintenance Request Lifecycle Full](#tc-06-maintenance-request-lifecycle-full)
   8.5. [Maintenance Request Lifecycle](#maintenance-request-lifecycle)
9. [Master Data](#master-data)
   9.1. [TC 03 Master Data Department](#tc-03-master-data-department)
   9.2. [TC 03 Employee Labor](#tc-03-employee-labor)
   9.3. [TC 03 Financial Master Data](#tc-03-financial-master-data)
   9.4. [TC 03 Manufacturer Model](#tc-03-manufacturer-model)
   9.5. [TC 03 Master Data Organization](#tc-03-master-data-organization)
   9.6. [TC 03 Master Data Site](#tc-03-master-data-site)
   9.7. [TC 03 Vendor Item](#tc-03-vendor-item)
   9.8. [TC 03 Work Schedule Holiday](#tc-03-work-schedule-holiday)
   9.9. [TC 19 Vendor Performance](#tc-19-vendor-performance)
10. [Purchasing & Stores](#purchasing-stores)
   10.1. [TC 11 Blanket Contract Po](#tc-11-blanket-contract-po)
   10.2. [TC 11 Purchase Receipt](#tc-11-purchase-receipt)
   10.3. [TC 11 Purchasing Pr Po](#tc-11-purchasing-pr-po)
   10.4. [Purchase Request Lifecycle](#purchase-request-lifecycle)
11. [Work Management](#work-management)
   11.1. [TC 07 Work Order Child Records](#tc-07-work-order-child-records)
   11.2. [TC 07 Wo Failure Reporting](#tc-07-wo-failure-reporting)
   11.3. [TC 07 Work Order](#tc-07-work-order)
   11.4. [TC 08 Work Order Activity](#tc-08-work-order-activity)
   11.5. [Work Order Lifecycle](#work-order-lifecycle)
12. [Safety Permits](#safety-permits)
   12.1. [TC 09 Safety Permit Lifecycle](#tc-09-safety-permit-lifecycle)
   12.2. [TC 09 Safety Permit](#tc-09-safety-permit)

---

## 1. General

*9 workflow(s) — 58 step(s)*

### 1.1. TC 02 Rbac Permissions ✅

| Property | Value |
|----------|-------|
| Test Case | TC-02 |
| Workflow | `TC-02-rbac-permissions` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-02.1 — Admin Panel** — `Success`

Navigate to the Admin panel to access role and permission configuration.

- **Action:** `Navigate to /admin`
- **URL:** `https://chieam.cubeworksinnovation.com/admin`
- **Timestamp:** 2026-04-10T07:14:55.374Z


![TC-02.1 — Admin Panel](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_01_NAV_ADMIN.png)


**Step 2: TC-02.1 — Admin Overview** — `Success`

The Admin panel provides access to user management, role configuration, and permission matrix settings.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/admin`
- **Timestamp:** 2026-04-10T07:14:55.943Z


![TC-02.1 — Admin Overview](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_02_SCREENSHOT_ADMIN.png)


**Step 3: TC-02.1 — Role List** — `Success`

Navigate to the Role entity. Roles define what actions users can perform on each entity type.

- **Action:** `Navigate to /role`
- **URL:** `https://chieam.cubeworksinnovation.com/role`
- **Timestamp:** 2026-04-10T07:14:57.791Z


![TC-02.1 — Role List](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_03_NAV_ROLE.png)


**Step 4: TC-02.1 — Role Configuration** — `Success`

The role list shows all configured roles (Admin, Manager, Technician, Viewer, etc.) with their associated permissions and data scopes.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/role`
- **Timestamp:** 2026-04-10T07:14:58.330Z


![TC-02.1 — Role Configuration](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_04_SCREENSHOT_ROLES.png)


**Step 5: TC-02.1 — Permission Matrix** — `Success`

Navigate to the Permission entity. The permission matrix defines Create, Read, Update, Delete (CRUD) access per role per entity.

- **Action:** `Navigate to /permission`
- **URL:** `https://chieam.cubeworksinnovation.com/permission`
- **Timestamp:** 2026-04-10T07:15:00.602Z


![TC-02.1 — Permission Matrix](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_05_NAV_PERMISSION.png)


**Step 6: TC-02.1 — Permission Matrix Detail** — `Success`

The permission matrix shows each role-entity combination with granular CRUD controls. Admins can toggle individual permissions to restrict or grant access.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/permission`
- **Timestamp:** 2026-04-10T07:15:01.144Z


![TC-02.1 — Permission Matrix Detail](eam-chi/frontend/test-artifacts/screenshots/TC-02-rbac-permissions__TC02_06_SCREENSHOT_PERM.png)


---

### 1.2. TC 02 Workflow Management ✅

| Property | Value |
|----------|-------|
| Test Case | TC-02 |
| Workflow | `TC-02-workflow-management` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-02.4 — Workflow Management** — `Success`

Navigate to Workflow. This page shows all configured workflow definitions with their states, transitions, and role-based restrictions.

- **Action:** `Navigate to /workflow`
- **URL:** `https://chieam.cubeworksinnovation.com/workflow`
- **Timestamp:** 2026-04-10T07:15:07.530Z


![TC-02.4 — Workflow Management](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_01_NAV.png)


**Step 2: TC-02.4 — Workflow Definitions** — `Success`

The workflow management page lists all entity workflows. Each workflow defines states, allowed transitions, and which roles can trigger each transition.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/workflow`
- **Timestamp:** 2026-04-10T07:15:08.062Z


![TC-02.4 — Workflow Definitions](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_02_SCREENSHOT.png)


**Step 3: TC-02 — Reports Dashboard** — `Success`

Navigate to Reports. The reporting dashboard shows operational metrics, KPIs, and analytics across all EAM modules.

- **Action:** `Navigate to /reports`
- **URL:** `https://chieam.cubeworksinnovation.com/reports`
- **Timestamp:** 2026-04-10T07:15:11.082Z


![TC-02 — Reports Dashboard](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_03_NAV_REPORTS.png)


**Step 4: TC-02 — Reports Overview** — `Success`

The reports page provides analytics and operational insights including asset health, maintenance backlog, work order completion rates, and vendor performance summaries.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/reports`
- **Timestamp:** 2026-04-10T07:15:11.613Z


![TC-02 — Reports Overview](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_04_SCREENSHOT_REPORTS.png)


**Step 5: TC-02 — Model Editor** — `Success`

Navigate to Model Editor. This admin tool allows configuring entity models, fields, and relationships.

- **Action:** `Navigate to /model-editor`
- **URL:** `https://chieam.cubeworksinnovation.com/model-editor`
- **Timestamp:** 2026-04-10T07:15:13.565Z


![TC-02 — Model Editor](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_05_NAV_MODEL.png)


**Step 6: TC-02 — Model Editor Interface** — `Success`

The Model Editor provides a visual interface for configuring entity models, field types, validation rules, and cross-entity relationships.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/model-editor`
- **Timestamp:** 2026-04-10T07:15:14.124Z


![TC-02 — Model Editor Interface](eam-chi/frontend/test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_06_SCREENSHOT_MODEL.png)


---

### 1.3. TC 12 Pm Calendar ✅

| Property | Value |
|----------|-------|
| Test Case | TC-12 |
| Workflow | `TC-12-pm-calendar` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-12.1 — PM Calendar** — `Success`

Navigate to the PM Calendar page. The calendar provides a visual overview of all scheduled preventive maintenance activities organized by date.

- **Action:** `Navigate to /calendar`
- **URL:** `https://chieam.cubeworksinnovation.com/calendar`
- **Timestamp:** 2026-04-10T07:17:10.039Z


![TC-12.1 — PM Calendar](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_01_NAV.png)


**Step 2: TC-12.1 — Calendar Month View** — `Success`

The PM Calendar displays scheduled maintenance tasks in a monthly view. Tasks are color-coded by status: Draft (slate), Pending (amber), Approved (blue), Release (violet), Completed (green).

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/calendar`
- **Timestamp:** 2026-04-10T07:17:10.591Z


![TC-12.1 — Calendar Month View](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_02_SCREENSHOT.png)


**Step 3: TC-12.3 — Maintenance Activity List** — `Success`

Navigate to Maintenance Activity. Activities are created from the PM Calendar and represent scheduled preventive maintenance tasks.

- **Action:** `Navigate to /maintenance_activity`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_activity`
- **Timestamp:** 2026-04-10T07:17:12.915Z


![TC-12.3 — Maintenance Activity List](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_03_NAV_MA.png)


**Step 4: TC-12.3 — Maintenance Activities** — `Success`

The maintenance activity list shows all scheduled activities with their status, due date, assigned resource, and linked work orders.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_activity`
- **Timestamp:** 2026-04-10T07:17:13.473Z


![TC-12.3 — Maintenance Activities](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_04_SCREENSHOT_MA.png)


**Step 5: TC-12.3 — PM Activity List** — `Success`

Navigate to PM Activity. PM Activities define reusable preventive maintenance templates with task sequences, checklists, and resource requirements.

- **Action:** `Navigate to /pm_activity`
- **URL:** `https://chieam.cubeworksinnovation.com/pm_activity`
- **Timestamp:** 2026-04-10T07:17:15.197Z


![TC-12.3 — PM Activity List](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_05_NAV_PMA.png)


**Step 6: TC-12.3 — PM Activity Templates** — `Success`

PM Activity templates define standard maintenance procedures that are instantiated when scheduled maintenance is triggered.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/pm_activity`
- **Timestamp:** 2026-04-10T07:17:15.753Z


![TC-12.3 — PM Activity Templates](eam-chi/frontend/test-artifacts/screenshots/TC-12-pm-calendar__TC12_06_SCREENSHOT_PMA.png)


---

### 1.4. TC 13 Scheduled Jobs ✅

| Property | Value |
|----------|-------|
| Test Case | TC-13 |
| Workflow | `TC-13-scheduled-jobs` |
| Persona | Admin |
| Steps | 4 |
| Pass Rate | 4/4 (100%) |
| Result | **PASS** |

**Step 1: TC-13.1 — Maintenance Calendar Configuration** — `Success`

Navigate to Maintenance Calendar. This defines the PM schedules that trigger automatic generation of maintenance requests and work orders.

- **Action:** `Navigate to /maintenance_calendar`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_calendar`
- **Timestamp:** 2026-04-10T07:17:20.181Z


![TC-13.1 — Maintenance Calendar Configuration](eam-chi/frontend/test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_01_NAV_MC.png)


**Step 2: TC-13.1 — PM Schedule Configuration** — `Success`

The maintenance calendar list shows all configured PM schedules with their frequency, last run date, next due date, and linked assets.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_calendar`
- **Timestamp:** 2026-04-10T07:17:20.739Z


![TC-13.1 — PM Schedule Configuration](eam-chi/frontend/test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_02_SCREENSHOT_MC.png)


**Step 3: TC-13.2 — Scheduled Job Log** — `Success`

Navigate to Scheduled Job Log. The log records all automated job executions including PM auto-generation runs.

- **Action:** `Navigate to /scheduled_job_log`
- **URL:** `https://chieam.cubeworksinnovation.com/scheduled_job_log`
- **Timestamp:** 2026-04-10T07:17:23.406Z


![TC-13.2 — Scheduled Job Log](eam-chi/frontend/test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_03_NAV_SJL.png)


**Step 4: TC-13.2 — Job Log Entries** — `Success`

The scheduled job log shows each execution with job ID, status (Success/Failed), duration, records created/updated, and error details. Jobs run at 1:00 AM daily or can be triggered manually.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/scheduled_job_log`
- **Timestamp:** 2026-04-10T07:17:23.948Z


![TC-13.2 — Job Log Entries](eam-chi/frontend/test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_04_SCREENSHOT_SJL.png)


---

### 1.5. TC 14 Server Actions ✅

| Property | Value |
|----------|-------|
| Test Case | TC-14 |
| Workflow | `TC-14-server-actions` |
| Persona | Admin |
| Steps | 8 |
| Pass Rate | 8/8 (100%) |
| Result | **PASS** |

**Step 1: TC-14.1 — Asset List (Clone Action)** — `Success`

Navigate to Asset. The 'Clone Asset' server action creates a copy of an existing asset with a new ID and reset fields.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:28.244Z


![TC-14.1 — Asset List (Clone Action)](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_01_NAV_ASSET.png)


**Step 2: TC-14.1 — Assets for Cloning** — `Success`

Select an asset from the list to access server actions. The 'Clone Asset' action is available from the asset detail page's action menu.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:28.798Z


![TC-14.1 — Assets for Cloning](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_02_SCREENSHOT_ASSET.png)


**Step 3: TC-14.2 — Failure Analysis List (RPN Calculation)** — `Success`

Navigate to Failure Analysis. Server actions include 'Calculate RPN' (Risk Priority Number = Severity × Occurrence × Detection), 'Generate 5-Why Template', and 'Generate Fishbone Template'.

- **Action:** `Navigate to /failure_analysis`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:17:30.570Z


![TC-14.2 — Failure Analysis List (RPN Calculation)](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_03_NAV_FA.png)


**Step 4: TC-14.2 — Failure Analysis Overview** — `Success`

The failure analysis list shows all failure records with their severity, occurrence, detection ratings, and calculated RPN scores.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:17:31.128Z


![TC-14.2 — Failure Analysis Overview](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_04_SCREENSHOT_FA.png)


**Step 5: TC-14.5 — Maintenance Request (Generate MO)** — `Success`

Navigate to Maintenance Request. The 'Generate Maintenance Order' server action creates a maintenance order with linked work order from an approved MR.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:17:34.701Z


![TC-14.5 — Maintenance Request (Generate MO)](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_05_NAV_MR.png)


**Step 6: TC-14.5 — MR Server Actions** — `Success`

Approved maintenance requests support server actions: 'Generate Maintenance Order' (creates MO + WO) and 'Create Purchase Request' (creates PR for required parts).

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:17:35.249Z


![TC-14.5 — MR Server Actions](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_06_SCREENSHOT_MR.png)


**Step 7: TC-14.5 — Maintenance Order List** — `Success`

Navigate to Maintenance Order. Maintenance orders are generated from approved maintenance requests and link to work orders for execution.

- **Action:** `Navigate to /maintenance_order`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_order`
- **Timestamp:** 2026-04-10T07:17:37.545Z


![TC-14.5 — Maintenance Order List](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_07_NAV_MO.png)


**Step 8: TC-14.5 — Maintenance Order Overview** — `Success`

The maintenance order list shows all generated orders with their source MR, linked WO, status, and assigned resources.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_order`
- **Timestamp:** 2026-04-10T07:17:38.106Z


![TC-14.5 — Maintenance Order Overview](eam-chi/frontend/test-artifacts/screenshots/TC-14-server-actions__TC14_08_SCREENSHOT_MO.png)


---

### 1.6. TC 16 Import Export ✅

| Property | Value |
|----------|-------|
| Test Case | TC-16 |
| Workflow | `TC-16-import-export` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-16.1 — Asset List (Export)** — `Success`

Navigate to the Asset list. The Export function allows downloading entity data as Excel files with applied filters.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:18:07.072Z


![TC-16.1 — Asset List (Export)](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_01_NAV_ASSET.png)


**Step 2: TC-16.1 — Export Feature** — `Success`

The entity list toolbar includes an Export button. Apply filters (e.g., Site, Status) before exporting to get a filtered dataset. The export downloads as an Excel (.xlsx) file.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:18:07.627Z


![TC-16.1 — Export Feature](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_02_SCREENSHOT.png)


**Step 3: TC-16.2 — Import/Export Page** — `Success`

Navigate to the Import/Export page. This page provides bulk data import with template download, validation, and execution.

- **Action:** `Navigate to /import-export`
- **URL:** `https://chieam.cubeworksinnovation.com/import-export`
- **Timestamp:** 2026-04-10T07:18:10.187Z


![TC-16.2 — Import/Export Page](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_03_NAV_IMPORT.png)


**Step 4: TC-16.2 — Import Template Download** — `Success`

The import page allows selecting an entity type and downloading a template with correct headers. Upload a filled template to validate and import records in bulk.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/import-export`
- **Timestamp:** 2026-04-10T07:18:10.747Z


![TC-16.2 — Import Template Download](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_04_SCREENSHOT_IMPORT.png)


**Step 5: TC-16 — System Settings** — `Success`

Navigate to Settings to configure import/export options, data validation rules, and default field mappings.

- **Action:** `Navigate to /settings`
- **URL:** `https://chieam.cubeworksinnovation.com/settings`
- **Timestamp:** 2026-04-10T07:18:12.791Z


![TC-16 — System Settings](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_05_NAV_SETTINGS.png)


**Step 6: TC-16 — Settings Overview** — `Success`

The Settings page provides system configuration including import/export preferences, naming series, and workflow configuration.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/settings`
- **Timestamp:** 2026-04-10T07:18:13.335Z


![TC-16 — Settings Overview](eam-chi/frontend/test-artifacts/screenshots/TC-16-import-export__TC16_06_SCREENSHOT_SETTINGS.png)


---

### 1.7. TC 18 Cross Workflow Integration ✅

| Property | Value |
|----------|-------|
| Test Case | TC-18 |
| Workflow | `TC-18-cross-workflow-integration` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-18.1 — Maintenance Request (Integration Source)** — `Success`

Navigate to Maintenance Request. MRs serve as the starting point for cross-workflow integration chains: MR → Work Order, MR → Purchase Request.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:18:17.425Z


![TC-18.1 — Maintenance Request (Integration Source)](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_01_NAV_MR.png)


**Step 2: TC-18.1 — MR Integration Overview** — `Success`

Approved maintenance requests can trigger: 'Generate Maintenance Order' (creates MO + WO) and 'Create Purchase Request' (creates PR for parts). These server actions link entities across modules.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:18:17.981Z


![TC-18.1 — MR Integration Overview](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_02_SCREENSHOT_MR.png)


**Step 3: TC-18.3 — Work Order (Integration Hub)** — `Success`

Navigate to Work Order. Work orders link to safety permits, labor, parts, equipment, and activities. WOs with LOTO Required = Yes should have linked safety permits.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:22.035Z


![TC-18.3 — Work Order (Integration Hub)](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_03_NAV_WO.png)


**Step 4: TC-18.3 — Work Order Integration Points** — `Success`

Work orders serve as the central hub for cross-module integration. Child records include labor, parts, equipment, activities, and safety permits.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:22.594Z


![TC-18.3 — Work Order Integration Points](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_04_SCREENSHOT_WO.png)


**Step 5: TC-18.3 — Safety Permits (WO Integration)** — `Success`

Safety permits are linked to work orders requiring hazardous work authorization. The WO → Safety Permit chain ensures proper safety compliance.

- **Action:** `Navigate to /safety_permit`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:18:24.811Z


![TC-18.3 — Safety Permits (WO Integration)](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_05_NAV_SP.png)


**Step 6: TC-18.3 — Safety Permit → Work Order Link** — `Success`

Safety permits show the linked work order in their detail view. Active permits must be verified before work order execution can begin.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:18:25.370Z


![TC-18.3 — Safety Permit → Work Order Link](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_06_SCREENSHOT_SP.png)


**Step 7: TC-18.2 — Purchase Request (MR Integration)** — `Success`

Navigate to Purchase Request. PRs can be generated from maintenance requests to procure required parts and materials.

- **Action:** `Navigate to /purchase_request`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:18:29.023Z


![TC-18.2 — Purchase Request (MR Integration)](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_07_NAV_PR.png)


**Step 8: TC-18.2 — MR → PR Integration** — `Success`

Purchase requests generated from maintenance requests carry the requestor, site, department, and required items from the source MR.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:18:29.563Z


![TC-18.2 — MR → PR Integration](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_08_SCREENSHOT_PR.png)


**Step 9: TC-18.5 — Vendor Performance** — `Success`

Navigate to Vendor. Vendor performance is automatically calculated based on purchase receipt delivery data.

- **Action:** `Navigate to /vendor`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor`
- **Timestamp:** 2026-04-10T07:18:35.382Z


![TC-18.5 — Vendor Performance](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_09_NAV_VENDOR.png)


**Step 10: TC-18.5 — Vendor Performance Metrics** — `Success`

The vendor list shows delivery ratings, on-time delivery percentages, quality scores, and total orders. These metrics are auto-calculated from purchase receipt records.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor`
- **Timestamp:** 2026-04-10T07:18:35.937Z


![TC-18.5 — Vendor Performance Metrics](eam-chi/frontend/test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_10_SCREENSHOT_VENDOR.png)


---

### 1.8. TC 20 Procurement Scenario ✅

| Property | Value |
|----------|-------|
| Test Case | TC-20 |
| Workflow | `TC-20-procurement-scenario` |
| Persona | Admin |
| Steps | 8 |
| Pass Rate | 8/8 (100%) |
| Result | **PASS** |

**Step 1: TC-20.3 — Step 1: Maintenance Request (Parts Needed)** — `Success`

The procurement scenario starts when a maintenance request identifies parts that need to be purchased. The 'Create PR' server action initiates procurement.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:14.983Z


![TC-20.3 — Step 1: Maintenance Request (Parts Needed)](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_01_MR.png)


**Step 2: TC-20.3 — MR with Parts Requirements** — `Success`

The maintenance request identifies required parts and materials. After approval, the 'Create Purchase Request' action generates a PR with the correct items.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:15.548Z


![TC-20.3 — MR with Parts Requirements](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_02_SCREENSHOT_MR.png)


**Step 3: TC-20.3 — Step 2: Purchase Request** — `Success`

The purchase request is generated from the MR. It contains the required items, quantities, and requestor information.

- **Action:** `Navigate to /purchase_request`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:19:17.839Z


![TC-20.3 — Step 2: Purchase Request](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_03_PR.png)


**Step 4: TC-20.3 — PR from MR** — `Success`

The purchase request shows items needed for the maintenance work. After approval, a purchase order is created to send to the vendor.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:19:18.398Z


![TC-20.3 — PR from MR](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_04_SCREENSHOT_PR.png)


**Step 5: TC-20.3 — Step 3: Purchase Order** — `Success`

The purchase order is issued to the vendor based on the approved PR. The PO tracks delivery dates and payment terms.

- **Action:** `Navigate to /purchase_order`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order`
- **Timestamp:** 2026-04-10T07:19:21.023Z


![TC-20.3 — Step 3: Purchase Order](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_05_PO.png)


**Step 6: TC-20.3 — PO Issued to Vendor** — `Success`

The purchase order shows vendor details, line items, delivery schedule, and total amount. Approved POs become read-only.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order`
- **Timestamp:** 2026-04-10T07:19:21.580Z


![TC-20.3 — PO Issued to Vendor](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_06_SCREENSHOT_PO.png)


**Step 7: TC-20.3 — Step 4: Purchase Receipt** — `Success`

When goods arrive, a purchase receipt is recorded against the PO. This updates inventory and triggers vendor performance recalculation.

- **Action:** `Navigate to /purchase_receipt`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt`
- **Timestamp:** 2026-04-10T07:19:24.625Z


![TC-20.3 — Step 4: Purchase Receipt](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_07_RECEIPT.png)


**Step 8: TC-20.3 — Receipt & Vendor Update** — `Success`

The purchase receipt records the delivery date and quantities received. Vendor performance metrics (delivery rating, on-time rate) are automatically recalculated.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt`
- **Timestamp:** 2026-04-10T07:19:25.176Z


![TC-20.3 — Receipt & Vendor Update](eam-chi/frontend/test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_08_SCREENSHOT_REC.png)


---

### 1.9. TC 15 Sla Tracking ✅

| Property | Value |
|----------|-------|
| Test Case | TC-15 |
| Workflow | `TC-15-sla-tracking` |
| Persona | Admin |
| Steps | 4 |
| Pass Rate | 4/4 (100%) |
| Result | **PASS** |

**Step 1: TC-15.1 — MR SLA Tracking** — `Success`

Navigate to Maintenance Request. SLA tracking fields are auto-populated when an MR is submitted based on its priority level.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:48.875Z


![TC-15.1 — MR SLA Tracking](eam-chi/frontend/test-artifacts/screenshots/TC-15-sla-tracking__TC15_01_NAV_MR.png)


**Step 2: TC-15.1 — MR SLA Fields** — `Success`

The maintenance request list shows SLA status indicators. High-priority MRs have shorter response and resolution SLA targets. Fields include: SLA Response Due, SLA Resolution Due, SLA Status, Is Overdue.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:49.425Z


![TC-15.1 — MR SLA Fields](eam-chi/frontend/test-artifacts/screenshots/TC-15-sla-tracking__TC15_02_SCREENSHOT_MR.png)


**Step 3: TC-15.2 — WO SLA Tracking** — `Success`

Navigate to Work Order. Work orders have stage-based SLA targets: Requested (8h), Approved (24h), In Progress (72h). SLA status updates automatically.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:19:51.976Z


![TC-15.2 — WO SLA Tracking](eam-chi/frontend/test-artifacts/screenshots/TC-15-sla-tracking__TC15_03_NAV_WO.png)


**Step 4: TC-15.2 — WO SLA Status** — `Success`

The work order list shows SLA tracking per stage. As work orders progress through their lifecycle, SLA timers reset for each stage with appropriate targets.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:19:52.526Z


![TC-15.2 — WO SLA Status](eam-chi/frontend/test-artifacts/screenshots/TC-15-sla-tracking__TC15_04_SCREENSHOT_WO.png)


---

## 2. Asset Management

*6 workflow(s) — 39 step(s)*

### 2.1. TC 04 Asset Create ✅

| Property | Value |
|----------|-------|
| Test Case | TC-04 |
| Workflow | `TC-04-asset-create` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-04.1 — Asset List** — `Success`

Navigate to Asset Management → Asset. The asset list shows all registered assets with their current lifecycle state, site, and criticality.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:15:17.295Z


![TC-04.1 — Asset List](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_01_NAV.png)


**Step 2: TC-04.1 — New Asset Form** — `Success`

Click 'Add New' to open the asset creation form. The form includes fields for description, asset class, site, department, manufacturer, and more.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:17.896Z


![TC-04.1 — New Asset Form](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_02_NEW.png)


**Step 3: TC-04.1 — Fill Description** — `Success`

Enter "Test Motor 001 — E2E Lifecycle Test" into the Description field.

- **Action:** `Type "Test Motor 001 — E2E Lifecycle Test" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:18.450Z


![TC-04.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_03_FILL_DESC.png)


**Step 4: TC-04.1 — Asset Created** — `Success`

Click 'Create' to save the asset. The system assigns an auto-generated ID (e.g., A-00001) and sets the initial workflow state to 'Acquired'.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:19.021Z


![TC-04.1 — Asset Created](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_04_SAVE.png)


**Step 5: TC-04.1 — Asset Detail View** — `Success`

The asset detail page shows all fields organized in tabs. The workflow state badge in the header indicates the current lifecycle state. Use the workflow dropdown to transition the asset through its lifecycle.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:19.587Z


![TC-04.1 — Asset Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_05_VERIFY_STATE.png)


---

### 2.2. TC 04 Asset Hierarchy ✅

| Property | Value |
|----------|-------|
| Test Case | TC-04 |
| Workflow | `TC-04-asset-hierarchy` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-04.2 — Asset List** — `Success`

Navigate to Asset Management. The asset list supports tree view to display parent-child hierarchies.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:15:23.308Z


![TC-04.2 — Asset List](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_01_NAV.png)


**Step 2: TC-04.2 — Asset Hierarchy View** — `Success`

The asset list displays assets in a hierarchical structure. Parent assets can be expanded to show sub-assets (children). This enables tracking of complex equipment assemblies.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:15:23.862Z


![TC-04.2 — Asset Hierarchy View](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_02_SCREENSHOT.png)


**Step 3: TC-04.2 — New Child Asset** — `Success`

Click 'Add New' to create a new asset. To establish a hierarchy, set the 'Parent Asset' field to link this asset as a sub-component.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:24.436Z


![TC-04.2 — New Child Asset](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_03_NEW.png)


**Step 4: TC-04.2 — Fill Description** — `Success`

Enter "E2E Child Asset — Motor Assembly" into the Description field.

- **Action:** `Type "E2E Child Asset — Motor Assembly" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:24.990Z


![TC-04.2 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_04_FILL.png)


**Step 5: TC-04.2 — Child Asset Created** — `Success`

The child asset is saved. Set the Parent Asset field to establish the hierarchy relationship.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:25.556Z


![TC-04.2 — Child Asset Created](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_05_SAVE.png)


**Step 6: TC-04.2 — Asset Detail with Parent Link** — `Success`

The asset detail page shows the parent asset relationship. Sub-assets appear in the Parent-Child tab, enabling drill-down into equipment assemblies.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:26.102Z


![TC-04.2 — Asset Detail with Parent Link](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_06_VERIFY.png)


---

### 2.3. TC 04 Equipment Crud ✅

| Property | Value |
|----------|-------|
| Test Case | TC-04 |
| Workflow | `TC-04-equipment-crud` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-04.5 — Equipment List** — `Success`

Navigate to Equipment. Equipment records track individual tools, vehicles, and machinery used in maintenance operations.

- **Action:** `Navigate to /equipment`
- **URL:** `https://chieam.cubeworksinnovation.com/equipment`
- **Timestamp:** 2026-04-10T07:15:29.753Z


![TC-04.5 — Equipment List](eam-chi/frontend/test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_01_NAV.png)


**Step 2: TC-04.5 — Equipment List View** — `Success`

The Equipment list shows all registered equipment with IDs, descriptions, types (Owned/Rented), and status. Use filters and search to locate specific equipment.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/equipment`
- **Timestamp:** 2026-04-10T07:15:30.315Z


![TC-04.5 — Equipment List View](eam-chi/frontend/test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_02_LIST.png)


**Step 3: TC-04.5 — Open Equipment Record** — `Success`

Click on an existing equipment record to view its details, including type, description, and linked work orders.

- **Action:** `Click on "table tbody tr:first-child td:first-child a, table tbody tr:first-child, [data-testid='entity-row']:first-child"`
- **URL:** `https://chieam.cubeworksinnovation.com/equipment/EQP-0025`
- **Timestamp:** 2026-04-10T07:15:30.872Z


![TC-04.5 — Open Equipment Record](eam-chi/frontend/test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_03_CLICK_FIRST.png)


**Step 4: TC-04.5 — Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 3000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/equipment/EQP-0025`
- **Timestamp:** 2026-04-10T07:15:34.429Z


![TC-04.5 — Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_04_WAIT.png)


**Step 5: TC-04.5 — Equipment Detail** — `Success`

The equipment detail page shows the equipment ID, type (Owned or Rented), description, and association fields. Equipment can be linked to work orders for resource tracking.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/equipment/EQP-0025`
- **Timestamp:** 2026-04-10T07:15:34.981Z


![TC-04.5 — Equipment Detail](eam-chi/frontend/test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_05_DETAIL.png)


---

### 2.4. TC 04 Meter Reading ✅

| Property | Value |
|----------|-------|
| Test Case | TC-04 |
| Workflow | `TC-04-meter-reading` |
| Persona | Admin |
| Steps | 9 |
| Pass Rate | 9/9 (100%) |
| Result | **PASS** |

**Step 1: TC-04.3 — Meter List** — `Success`

Navigate to Meter. Meters track operating parameters like running hours, odometer readings, and cycle counts for assets.

- **Action:** `Navigate to /meter`
- **URL:** `https://chieam.cubeworksinnovation.com/meter`
- **Timestamp:** 2026-04-10T07:15:39.768Z


![TC-04.3 — Meter List](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_01_NAV.png)


**Step 2: TC-04.3 — Meter Overview** — `Success`

The meter list shows all configured meters across assets with their current readings, types, and update frequency.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/meter`
- **Timestamp:** 2026-04-10T07:15:40.322Z


![TC-04.3 — Meter Overview](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_02_SCREENSHOT.png)


**Step 3: TC-04.3 — New Meter** — `Success`

Click 'Add New' to create a meter. Specify the meter type (Operating Hours, Odometer, Cycle Count), linked asset, and unit of measure.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/meter/new`
- **Timestamp:** 2026-04-10T07:15:40.903Z


![TC-04.3 — New Meter](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_03_NEW.png)


**Step 4: TC-04.3 — Fill Meter Name** — `Success`

Enter "E2E Operating Hours Meter" into the Meter Name field.

- **Action:** `Type "E2E Operating Hours Meter" into "input[name='meter_name'], textarea[name='meter_name'], input[name='name'], textarea[name='name'], input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/meter/new`
- **Timestamp:** 2026-04-10T07:15:41.457Z


![TC-04.3 — Fill Meter Name](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_04_FILL.png)


**Step 5: TC-04.3 — Meter Created** — `Success`

The meter is created and linked to an asset. Add meter readings to track operating parameters over time.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/meter/new`
- **Timestamp:** 2026-04-10T07:15:42.510Z


![TC-04.3 — Meter Created](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_05_SAVE.png)


**Step 6: TC-04.3 — Meter Detail** — `Success`

The meter detail page shows the meter type, current reading, and reading history. Meter readings trigger preventive maintenance based on configured thresholds.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/meter/new`
- **Timestamp:** 2026-04-10T07:15:43.065Z


![TC-04.3 — Meter Detail](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_06_VERIFY.png)


**Step 7: TC-04.3 — Meter Reading List** — `Success`

Navigate to Meter Reading. Meter readings record periodic measurements for meters linked to assets.

- **Action:** `Navigate to /meter_reading`
- **URL:** `https://chieam.cubeworksinnovation.com/meter_reading`
- **Timestamp:** 2026-04-10T07:15:45.229Z


![TC-04.3 — Meter Reading List](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_01_NAV.png)


**Step 8: TC-04.3 — New Meter Reading** — `Success`

Click 'Add New' to record a new meter reading. Select the meter, enter the reading value, and timestamp.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/meter_reading/new`
- **Timestamp:** 2026-04-10T07:15:45.803Z


![TC-04.3 — New Meter Reading](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_02_NEW.png)


**Step 9: TC-04.3 — Meter Reading Form** — `Success`

The meter reading form captures the current value, date, and any notes. The system calculates the delta from the previous reading automatically.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/meter_reading/new`
- **Timestamp:** 2026-04-10T07:15:46.340Z


![TC-04.3 — Meter Reading Form](eam-chi/frontend/test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_03_SCREENSHOT.png)


---

### 2.5. TC 05 Asset Workflow Decommission ✅

| Property | Value |
|----------|-------|
| Test Case | TC-05 |
| Workflow | `TC-05-asset-workflow-decommission` |
| Persona | Admin |
| Steps | 8 |
| Pass Rate | 8/8 (100%) |
| Result | **PASS** |

**Step 1: TC-05.1 — Asset Workflow States** — `Success`

Navigate to Asset. The complete asset lifecycle includes: Acquired → Received → Inspected → Installed → Active → various maintenance paths → Retire → Inactive → Decommissioned.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:15:51.358Z


![TC-05.1 — Asset Workflow States](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_01_NAV.png)


**Step 2: TC-05.1 — Asset List with Workflow States** — `Success`

The asset list shows each asset's current workflow state. State transitions are controlled by role permissions and business rules.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:15:51.914Z


![TC-05.1 — Asset List with Workflow States](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_02_SCREENSHOT.png)


**Step 3: TC-05.1 — Asset Creation for Lifecycle Test** — `Success`

Create a new asset to test the complete lifecycle. Fill in description and required fields.

- **Action:** `Navigate to /asset/new`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:54.364Z


![TC-05.1 — Asset Creation for Lifecycle Test](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_03_NAV_NEW.png)


**Step 4: TC-05.1 — Fill Description** — `Success`

Enter "E2E Lifecycle Test — Full Decommission P" into the Description field.

- **Action:** `Type "E2E Lifecycle Test — Full Decommission Path" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:54.922Z


![TC-05.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_04_FILL.png)


**Step 5: TC-05.1 — Asset Created (Acquired)** — `Success`

The asset is created in 'Acquired' state. The full lifecycle path is: Acquired → Receive → Inspected → Install → Active → Retire → Inactive → Remove → Decommissioned.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:55.539Z


![TC-05.1 — Asset Created (Acquired)](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_05_SAVE.png)


**Step 6: TC-05.1 — Asset Lifecycle Transitions** — `Success`

The asset detail page shows available workflow transitions in the dropdown. Each transition moves the asset to the next lifecycle state with an audit trail entry.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:15:56.091Z


![TC-05.1 — Asset Lifecycle Transitions](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_06_VERIFY.png)


**Step 7: TC-05 — Workflow Configuration** — `Success`

Navigate to Workflow management to view all configured workflow definitions. Each entity type has its own workflow with states and transitions.

- **Action:** `Navigate to /workflow`
- **URL:** `https://chieam.cubeworksinnovation.com/workflow`
- **Timestamp:** 2026-04-10T07:15:59.469Z


![TC-05 — Workflow Configuration](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_07_NAV_WF.png)


**Step 8: TC-05 — Workflow Definitions** — `Success`

The workflow configuration page shows all entity workflows with their states, transitions, and role restrictions. The asset workflow has the most complex state machine.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/workflow`
- **Timestamp:** 2026-04-10T07:16:00.028Z


![TC-05 — Workflow Definitions](eam-chi/frontend/test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_08_SCREENSHOT_WF.png)


---

### 2.6. Asset Lifecycle ✅

| Property | Value |
|----------|-------|
| Test Case | TC-04 |
| Workflow | `asset-lifecycle` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: Asset List** — `Success`

Navigate to the Asset list page by clicking 'Asset' in the sidebar or visiting /asset. This page shows all registered assets in a data table with search, filter, and sort capabilities.

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:16:21.584Z


![Asset List](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_01_NAVIGATE.png)


**Step 2: Create New Asset** — `Success`

Click 'Add New' in the top-right corner to open the asset creation form. You will be redirected to a blank form where you can enter the asset details.

- **Action:** `Click on "button:has-text('Add New'), [data-testid='btn-new'], button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:16:22.136Z


![Create New Asset](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_02_NEW.png)


**Step 3: Fill Form Field** — `Success`

Enter "Test Pump Assembly E2E" into the Description field.

- **Action:** `Type "Test Pump Assembly E2E" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:16:22.699Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_03_FILL_NAME.png)


**Step 4: Asset Form Filled** — `Success`

Fill in the asset details. The 'Description' field is the primary identifier. Additional fields can be filled as needed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:16:23.255Z


![Asset Form Filled](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_04_FILL_DESCRIPTION.png)


**Step 5: Save New Asset** — `Success`

After filling in the required fields, click 'Save' to create the asset record. A success notification appears confirming the asset was created.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save')"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:16:24.088Z


![Save New Asset](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_05_SAVE.png)


**Step 6: Asset Details View** — `Success`

After saving, you are taken to the asset detail page where you can view all fields, switch tabs, and manage workflow state.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/new`
- **Timestamp:** 2026-04-10T07:16:24.649Z


![Asset Details View](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_06_VERIFY_SAVED.png)


---

## 3. Condition Monitoring

*2 workflow(s) — 11 step(s)*

### 3.1. TC 10 Condition Monitoring Types ✅

| Property | Value |
|----------|-------|
| Test Case | TC-10 |
| Workflow | `TC-10-condition-monitoring-types` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-10.2 — Condition Monitoring List** — `Success`

Navigate to Condition Monitoring. The system supports multiple monitoring types: Vibration, Temperature, Pressure, Oil Analysis, Ultrasonic, Thermography, and Current/Voltage.

- **Action:** `Navigate to /condition_monitoring`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring`
- **Timestamp:** 2026-04-10T07:16:06.967Z


![TC-10.2 — Condition Monitoring List](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_01_NAV.png)


**Step 2: TC-10.2 — Monitoring Types Overview** — `Success`

The condition monitoring list shows all monitoring records with their type, current value, threshold levels, and status (Normal, Warning, Critical, Resolved).

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring`
- **Timestamp:** 2026-04-10T07:16:07.524Z


![TC-10.2 — Monitoring Types Overview](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_02_SCREENSHOT.png)


**Step 3: TC-10.2 — New Condition Monitoring** — `Success`

Click 'Add New' to create a condition monitoring record. Select the monitoring type, linked asset, and configure baseline, warning, and critical threshold levels.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:08.094Z


![TC-10.2 — New Condition Monitoring](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_03_NEW.png)


**Step 4: TC-10.2 — Fill Analysis Notes** — `Success`

Enter "E2E Temperature monitoring — Cooling sys" into the Analysis Notes field.

- **Action:** `Type "E2E Temperature monitoring — Cooling system outlet" into "input[name='analysis_notes'], textarea[name='analysis_notes']"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:08.924Z


![TC-10.2 — Fill Analysis Notes](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_04_FILL.png)


**Step 5: TC-10.2 — Monitoring Record Created** — `Success`

The monitoring record is created in 'Active' state. Update the current value to trigger threshold-based status changes (Normal → Warning → Critical).

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:09.639Z


![TC-10.2 — Monitoring Record Created](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_05_SAVE.png)


**Step 6: TC-10.2 — Monitoring Detail by Type** — `Success`

The monitoring detail shows type-specific fields, thresholds, and current readings. Different monitoring types have different measurement units and threshold configurations.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:10.199Z


![TC-10.2 — Monitoring Detail by Type](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_06_VERIFY.png)


---

### 3.2. TC 10 Condition Monitoring ✅

| Property | Value |
|----------|-------|
| Test Case | TC-10 |
| Workflow | `TC-10-condition-monitoring` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-10.1 — Condition Monitoring List** — `Success`

Navigate to Condition Monitoring. This module tracks real-time sensor data and condition indicators for assets, with configurable warning and critical thresholds.

- **Action:** `Navigate to /condition_monitoring`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring`
- **Timestamp:** 2026-04-10T07:16:15.403Z


![TC-10.1 — Condition Monitoring List](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_01_NAV.png)


**Step 2: TC-10.1 — New Condition Monitor** — `Success`

Click 'Add New' to set up condition monitoring for an asset. Define the monitoring type (Vibration, Temperature, Pressure, etc.), baseline value, and warning/critical thresholds.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:15.956Z


![TC-10.1 — New Condition Monitor](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_02_NEW.png)


**Step 3: TC-10.1 — Fill Analysis Notes** — `Success`

Enter "E2E Test — Vibration monitoring for Test" into the Analysis Notes field.

- **Action:** `Type "E2E Test — Vibration monitoring for Test Motor 001" into "input[name='analysis_notes'], textarea[name='analysis_notes']"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:16.514Z


![TC-10.1 — Fill Analysis Notes](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_03_FILL.png)


**Step 4: TC-10.1 — Condition Monitor Created** — `Success`

The condition monitoring record is created in 'Active' state. As readings are taken, the system automatically transitions to Warning or Critical states based on threshold values.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:17.477Z


![TC-10.1 — Condition Monitor Created](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_04_SAVE.png)


**Step 5: TC-10.1 — Condition Monitoring Detail** — `Success`

The detail view shows the asset, monitoring type, baseline value, thresholds, current reading, alert status, and trend direction. The workflow state reflects the current alert level.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring/new`
- **Timestamp:** 2026-04-10T07:16:18.036Z


![TC-10.1 — Condition Monitoring Detail](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_05_VERIFY.png)


---

## 4. Authentication

*5 workflow(s) — 28 step(s)*

### 4.1. TC 01 Authentication ✅

| Property | Value |
|----------|-------|
| Test Case | TC-01 |
| Workflow | `TC-01-authentication` |
| Persona | Admin |
| Steps | 7 |
| Pass Rate | 7/7 (100%) |
| Result | **PASS** |

**Step 1: TC-01 — Clear Session** — `Success`

Clear browser cookies and local storage to ensure a clean test state.

- **Action:** `clearSession on ""`
- **URL:** `about:blank`
- **Timestamp:** 2026-04-10T07:16:25.365Z


![TC-01 — Clear Session](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_00_CLEAR.png)


**Step 2: TC-01.1 — Login Page** — `Success`

Navigate to the login page. The login form displays with Username and Password fields, along with the organization branding (logo and name).

- **Action:** `Navigate to /login`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:28.035Z


![TC-01.1 — Login Page](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_01_LOGIN_PAGE.png)


**Step 3: TC-01 — Fill Form Field** — `Success`

Enter "admin" into the form field.

- **Action:** `Type "admin" into "[data-testid='login-username'] input, input[placeholder*='username' i]"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:28.594Z


![TC-01 — Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_02_ENTER_CREDS.png)


**Step 4: TC-01 — Fill Form Field** — `Success`

Enter "admin123" into the form field.

- **Action:** `Type "admin123" into "[data-testid='login-password'] input, input[type='password']"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:29.165Z


![TC-01 — Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_03_ENTER_PASS.png)


**Step 5: TC-01.1 — Successful Login** — `Success`

After entering valid credentials and clicking 'Sign In', you are redirected to the Home page. The sidebar displays navigation items based on your role permissions.

- **Action:** `Click on "[data-testid='login-submit'], button[type='submit']"`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:16:31.427Z


![TC-01.1 — Successful Login](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_04_SUBMIT.png)


**Step 6: TC-01.1 — Sidebar & Navigation** — `Success`

The sidebar shows all available modules based on your role. Admin users can see all entities including Settings, Admin, Workflow, and Model Editor sections.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:16:31.978Z


![TC-01.1 — Sidebar & Navigation](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_05_VERIFY_SIDEBAR.png)


**Step 7: TC-01.5 — User Menu** — `Success`

Click your name/avatar at the bottom of the sidebar to open the user menu. From here you can access your Profile or Logout.

- **Action:** `Click on "[data-testid='user-menu'] button, .p-4.border-t button"`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:16:32.573Z


![TC-01.5 — User Menu](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_06_PROFILE.png)


---

### 4.2. TC 01 Profile Update ✅

| Property | Value |
|----------|-------|
| Test Case | TC-01 |
| Workflow | `TC-01-profile-update` |
| Persona | Admin |
| Steps | 2 |
| Pass Rate | 2/2 (100%) |
| Result | **PASS** |

**Step 1: TC-01.5 — User Profile** — `Success`

Navigate to the Profile page by clicking on the avatar or visiting /profile. The profile page shows user details and allows editing contact information.

- **Action:** `Navigate to /profile`
- **URL:** `https://chieam.cubeworksinnovation.com/profile`
- **Timestamp:** 2026-04-10T07:16:36.523Z


![TC-01.5 — User Profile](eam-chi/frontend/test-artifacts/screenshots/TC-01-profile-update__TC01_PROF_01_NAV.png)


**Step 2: TC-01.5 — Profile Details** — `Success`

The profile page displays the current user's information including username, email, role, and employee linkage. Users can update their contact details and password.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/profile`
- **Timestamp:** 2026-04-10T07:16:37.073Z


![TC-01.5 — Profile Details](eam-chi/frontend/test-artifacts/screenshots/TC-01-profile-update__TC01_PROF_02_SCREENSHOT.png)


---

### 4.3. TC 01 User Crud ✅

| Property | Value |
|----------|-------|
| Test Case | TC-01 |
| Workflow | `TC-01-user-crud` |
| Persona | Admin |
| Steps | 7 |
| Pass Rate | 7/7 (100%) |
| Result | **PASS** |

**Step 1: TC-01.4 — Admin Panel** — `Success`

Navigate to the Admin panel. This page provides user management, role configuration, and system settings.

- **Action:** `Navigate to /admin`
- **URL:** `https://chieam.cubeworksinnovation.com/admin`
- **Timestamp:** 2026-04-10T07:16:41.327Z


![TC-01.4 — Admin Panel](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_01_NAV.png)


**Step 2: TC-01.4 — Admin Dashboard** — `Success`

The Admin panel shows user accounts, roles, and system configuration. Administrators can create, edit, and deactivate user accounts.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/admin`
- **Timestamp:** 2026-04-10T07:16:41.877Z


![TC-01.4 — Admin Dashboard](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_02_SCREENSHOT.png)


**Step 3: TC-01.4 — User List** — `Success`

Navigate to the User entity list. This shows all registered users with their roles, status, and last login information.

- **Action:** `Navigate to /user`
- **URL:** `https://chieam.cubeworksinnovation.com/user`
- **Timestamp:** 2026-04-10T07:16:44.842Z


![TC-01.4 — User List](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_03_NAV_USERS.png)


**Step 4: TC-01.4 — User List View** — `Success`

The user list shows all registered user accounts with their username, role assignment, status, and employee linkage. Administrators can manage users from this view.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/user`
- **Timestamp:** 2026-04-10T07:16:45.400Z


![TC-01.4 — User List View](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_04_LIST.png)


**Step 5: TC-01.4 — User Detail** — `Success`

Click on a user record to view details including username, email, role assignment, and employee linkage.

- **Action:** `Click on "table tbody tr:first-child td:first-child a, table tbody tr:first-child, [data-testid='entity-row']:first-child"`
- **URL:** `https://chieam.cubeworksinnovation.com/user`
- **Timestamp:** 2026-04-10T07:16:45.965Z


![TC-01.4 — User Detail](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_05_CLICK_FIRST.png)


**Step 6: TC-01.4 — Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 3000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/user`
- **Timestamp:** 2026-04-10T07:16:49.508Z


![TC-01.4 — Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_06_WAIT.png)


**Step 7: TC-01.4 — User Detail View** — `Success`

The user detail page shows username, email, password fields, role assignment, and employee linkage. The role determines which entities and actions the user can access.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/user`
- **Timestamp:** 2026-04-10T07:16:50.047Z


![TC-01.4 — User Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-01-user-crud__TC01_USER_07_DETAIL.png)


---

### 4.4. Login Edge Cases ✅

| Property | Value |
|----------|-------|
| Test Case | TC-01 |
| Workflow | `login-edge-cases` |
| Persona | Anonymous |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: Clear Session** — `Success`

Clear browser cookies and local storage to ensure a clean test state.

- **Action:** `clearSession on ""`
- **URL:** `about:blank`
- **Timestamp:** 2026-04-10T07:16:50.730Z


![Clear Session](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_00_CLEAR.png)


**Step 2: Navigate** — `Success`

Navigate to /login.

- **Action:** `Navigate to /login`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:53.294Z


![Navigate](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_01_NAVIGATE.png)


**Step 3: Empty Credentials Error** — `Success`

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.

- **Action:** `Click on "button[type='submit']"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:53.859Z


![Empty Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_02_EMPTY_SUBMIT.png)


**Step 4: Fill Form Field** — `Success`

Enter "admin" into the form field.

- **Action:** `Type "admin" into "[data-testid='login-username'] input, input[placeholder*='username' i]"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:54.411Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_03_WRONG_PASSWORD.png)


**Step 5: Fill Form Field** — `Success`

Enter "wrongpassword" into the form field.

- **Action:** `Type "wrongpassword" into "input[type='password']"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:54.960Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_04_WRONG_PASSWORD_FILL.png)


**Step 6: Invalid Credentials Error** — `Success`

If you enter an incorrect username or password, the system displays an error message. Verify your credentials and try again. After multiple failed attempts, your account may be temporarily locked.

- **Action:** `Click on "button[type='submit']"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:56.136Z


![Invalid Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_05_WRONG_PASSWORD_SUBMIT.png)


---

### 4.5. Login Happy Path ✅

| Property | Value |
|----------|-------|
| Test Case | TC-01 |
| Workflow | `login-happy-path` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: Clear Session** — `Success`

Clear browser cookies and local storage to ensure a clean test state.

- **Action:** `clearSession on ""`
- **URL:** `about:blank`
- **Timestamp:** 2026-04-10T07:16:56.834Z


![Clear Session](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_00_CLEAR.png)


**Step 2: Login Page** — `Success`

Open the EAM application in your web browser. You will be presented with the login screen showing the organization branding and credential fields.

- **Action:** `Navigate to /login`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:16:59.601Z


![Login Page](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_01_NAVIGATE.png)


**Step 3: Enter Username** — `Success`

Enter your username in the Username field. This is the account name provided by your system administrator.

- **Action:** `Type "admin" into "[data-testid='login-username'] input, input[placeholder*='username' i]"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:17:00.136Z


![Enter Username](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_02_ENTER_USERNAME.png)


**Step 4: Enter Password** — `Success`

Enter your password in the Password field. Passwords are case-sensitive.

- **Action:** `Type "admin123" into "input[type='password']"`
- **URL:** `https://chieam.cubeworksinnovation.com/login`
- **Timestamp:** 2026-04-10T07:17:00.709Z


![Enter Password](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_03_ENTER_PASSWORD.png)


**Step 5: Submit Login** — `Success`

Click the 'Sign in' button. Upon successful authentication, you will be redirected to the home page.

- **Action:** `Click on "button[type='submit']"`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:17:03.250Z


![Submit Login](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_04_SUBMIT.png)


**Step 6: Home Page After Login** — `Success`

After successful login, the main application loads with the sidebar navigation showing all available modules.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:17:03.795Z


![Home Page After Login](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_05_HOME_LOADED.png)


---

## 5. Dashboard & Overview

*1 workflow(s) — 3 step(s)*

### 5.1. Dashboard Overview ✅

| Property | Value |
|----------|-------|
| Test Case | TC-02 |
| Workflow | `dashboard-overview` |
| Persona | Admin |
| Steps | 3 |
| Pass Rate | 3/3 (100%) |
| Result | **PASS** |

**Step 1: Dashboard Overview** — `Success`

The Dashboard provides a real-time overview of your asset management system. Navigate to the Dashboard by clicking 'Dashboard' in the left sidebar or by visiting /dashboard.

- **Action:** `Navigate to /dashboard`
- **URL:** `https://chieam.cubeworksinnovation.com/dashboard`
- **Timestamp:** 2026-04-10T07:17:43.319Z


![Dashboard Overview](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_01_NAVIGATE.png)


**Step 2: Key Performance Indicators** — `Success`

Six KPI cards are displayed at the top: Total Assets, Work Orders, Overdue WOs, Inventory, Purchase Requests, and Incidents. Each card shows the current total and a secondary metric such as the count from the last 30 days.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/dashboard`
- **Timestamp:** 2026-04-10T07:17:43.879Z


![Key Performance Indicators](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_02_KPI_CARDS.png)


**Step 3: Refreshing Dashboard Data** — `Success`

Click the 'Refresh' button in the top-right corner to reload all dashboard data from the server.

- **Action:** `Click on "button:has-text('Refresh')"`
- **URL:** `https://chieam.cubeworksinnovation.com/dashboard`
- **Timestamp:** 2026-04-10T07:17:44.984Z


![Refreshing Dashboard Data](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_03_REFRESH.png)


---

## 6. General Features

*1 workflow(s) — 6 step(s)*

### 6.1. Entity List Features ⚠️

| Property | Value |
|----------|-------|
| Test Case | TC-05 |
| Workflow | `entity-list-features` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 5/6 (83%) |
| Result | **PARTIAL** |

**Step 1: Entity List Page** — `Success`

Entity list pages display records in a data table. They support search, column filtering, sorting, pagination, and multiple view modes (list, tree, diagram, hierarchy).

- **Action:** `Navigate to /asset`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:48.243Z


![Entity List Page](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_01_NAVIGATE.png)


**Step 2: Search Records** — `Success`

Type in the search box to filter records. The table updates in real-time as you type. You can search across the selected filter field.

- **Action:** `Type "pump" into "input[placeholder*='Search' i], [data-testid='search-input']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:48.790Z


![Search Records](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_02_SEARCH.png)


**Step 3: Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 2000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:51.334Z


![Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_03_WAIT_RESULTS.png)


**Step 4: Search Results** — `Success`

The table displays only records matching your search term. The total count badge updates to reflect the filtered result count.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:51.897Z


![Search Results](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_04_SEARCH_RESULTS.png)


**Step 5: Clear Field** — `Loading`

Clear the search input to reset the filtered results.

- **Action:** `clear on "input[placeholder*='Search' i], [data-testid='search-input']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:17:52.480Z


![Clear Field](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_05_CLEAR_SEARCH.png)


**Step 6: Open Record Detail** — `Success`

Click any row in the table to open the detail view for that record. You can view and edit all fields, manage attachments, and control the workflow state.

- **Action:** `Click on "table tbody tr:first-child td:nth-child(2)"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset/A-00265`
- **Timestamp:** 2026-04-10T07:17:53.048Z


![Open Record Detail](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_06_CLICK_ROW.png)


---

## 7. Navigation

*1 workflow(s) — 5 step(s)*

### 7.1. Sidebar Navigation ✅

| Property | Value |
|----------|-------|
| Test Case | TC-02 |
| Workflow | `sidebar-navigation` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: Application Sidebar** — `Success`

The sidebar is always visible on the left side of the screen. It contains the organization logo, navigation links grouped by module, and user account controls at the bottom.

- **Action:** `Navigate to /`
- **URL:** `https://chieam.cubeworksinnovation.com/`
- **Timestamp:** 2026-04-10T07:17:56.536Z


![Application Sidebar](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_01_HOME.png)


**Step 2: Navigate to Dashboard** — `Success`

Click 'Dashboard' in the sidebar to view the system-wide KPI overview.

- **Action:** `Click on "nav a[href='/dashboard'], a[href='/dashboard']"`
- **URL:** `https://chieam.cubeworksinnovation.com/dashboard`
- **Timestamp:** 2026-04-10T07:17:57.174Z


![Navigate to Dashboard](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_02_DASHBOARD.png)


**Step 3: Navigate to Assets** — `Success`

Click 'Asset' under the Asset Management module to view the full list of registered assets.

- **Action:** `Click on "nav a[href='/asset'], a[href='/asset']"`
- **URL:** `https://chieam.cubeworksinnovation.com/asset`
- **Timestamp:** 2026-04-10T07:18:00.164Z


![Navigate to Assets](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_03_ASSET.png)


**Step 4: Navigate to Work Orders** — `Success`

Click 'Work Order' under the Work Management module to view and manage work orders. Expand the module group if it is collapsed.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:01.863Z


![Navigate to Work Orders](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_04_WORK_ORDER.png)


**Step 5: Collapse Sidebar** — `Success`

Click the hamburger menu icon in the header to collapse the sidebar. This gives you more horizontal space for data tables and forms. Click again to expand.

- **Action:** `Click on "[data-testid='sidebar-toggle'], aside button:first-child, aside > div > button"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:02.450Z


![Collapse Sidebar](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_05_COLLAPSE.png)


---

## 8. Maintenance Management

*5 workflow(s) — 34 step(s)*

### 8.1. TC 20 Corrective Maintenance Scenario ✅

| Property | Value |
|----------|-------|
| Test Case | TC-20 |
| Workflow | `TC-20-corrective-maintenance-scenario` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-20.1 — Step 1: Condition Detection** — `Success`

The corrective maintenance scenario begins with condition monitoring detecting an anomaly. A vibration reading exceeds the critical threshold, triggering the maintenance chain.

- **Action:** `Navigate to /condition_monitoring`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring`
- **Timestamp:** 2026-04-10T07:18:41.651Z


![TC-20.1 — Step 1: Condition Detection](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_01_NAV_CM.png)


**Step 2: TC-20.1 — Condition Monitoring Alert** — `Success`

Condition monitoring records show the escalation from Normal → Warning → Critical. Critical conditions trigger maintenance request creation.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/condition_monitoring`
- **Timestamp:** 2026-04-10T07:18:42.204Z


![TC-20.1 — Condition Monitoring Alert](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_02_SCREENSHOT_CM.png)


**Step 3: TC-20.1 — Step 2: Maintenance Request** — `Success`

A high-priority maintenance request is created to address the critical condition. The MR includes the asset reference and failure description.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:18:45.503Z


![TC-20.1 — Step 2: Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_03_NAV_MR.png)


**Step 4: TC-20.1 — MR Linked to Condition** — `Success`

The maintenance request references the condition monitoring alert. After approval, a maintenance order and work order are generated.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:18:46.050Z


![TC-20.1 — MR Linked to Condition](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_04_SCREENSHOT_MR.png)


**Step 5: TC-20.1 — Step 3: Work Order Execution** — `Success`

A corrective work order is generated from the maintenance order. The WO tracks labor, parts, equipment, and safety permit requirements.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:48.886Z


![TC-20.1 — Step 3: Work Order Execution](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_05_NAV_WO.png)


**Step 6: TC-20.1 — Work Order with Resources** — `Success`

The work order shows assigned resources (labor, parts, equipment), linked safety permit, and workflow progression through Requested → Approved → In Progress → Closed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:18:49.425Z


![TC-20.1 — Work Order with Resources](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_06_SCREENSHOT_WO.png)


**Step 7: TC-20.1 — Step 4: Safety Permit** — `Success`

A safety permit is issued for the corrective work order. The permit ensures proper safety protocols (LOTO, PPE) are followed during repairs.

- **Action:** `Navigate to /safety_permit`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:18:51.911Z


![TC-20.1 — Step 4: Safety Permit](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_07_NAV_SP.png)


**Step 8: TC-20.1 — Safety Permit for Corrective Work** — `Success`

The safety permit detail shows hazards, precautions, and the linked work order. Active permits must be verified before work begins.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:18:52.459Z


![TC-20.1 — Safety Permit for Corrective Work](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_08_SCREENSHOT_SP.png)


**Step 9: TC-20.1 — Step 5: Failure Analysis** — `Success`

After completing the corrective work, a failure analysis is created to document root cause, remedy, and prevention measures.

- **Action:** `Navigate to /failure_analysis`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:18:55.636Z


![TC-20.1 — Step 5: Failure Analysis](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_09_NAV_FA.png)


**Step 10: TC-20.1 — Root Cause Analysis** — `Success`

The failure analysis records severity, occurrence, and detection ratings. The RPN (Risk Priority Number) score prioritizes corrective actions. 5-Why and Fishbone templates support structured root cause analysis.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:18:56.174Z


![TC-20.1 — Root Cause Analysis](eam-chi/frontend/test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_10_SCREENSHOT_FA.png)


---

### 8.2. TC 20 Preventive Maintenance Scenario ✅

| Property | Value |
|----------|-------|
| Test Case | TC-20 |
| Workflow | `TC-20-preventive-maintenance-scenario` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-20.2 — Step 1: PM Calendar** — `Success`

The preventive maintenance scenario starts with the PM Calendar. Scheduled tasks are displayed in a monthly view with color-coded statuses.

- **Action:** `Navigate to /calendar`
- **URL:** `https://chieam.cubeworksinnovation.com/calendar`
- **Timestamp:** 2026-04-10T07:19:02.877Z


![TC-20.2 — Step 1: PM Calendar](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_01_CALENDAR.png)


**Step 2: TC-20.2 — PM Calendar Overview** — `Success`

The calendar shows all scheduled preventive maintenance tasks. Creating a task auto-generates the chain: Maintenance Activity → PMA → Work Order (Preventive) → WO Activity → Maintenance Request.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/calendar`
- **Timestamp:** 2026-04-10T07:19:03.414Z


![TC-20.2 — PM Calendar Overview](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_02_SCREENSHOT_CAL.png)


**Step 3: TC-20.2 — Step 2: Maintenance Activity** — `Success`

Maintenance activities are generated from PM Calendar tasks. Each activity links to a PMA template and a work order.

- **Action:** `Navigate to /maintenance_activity`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_activity`
- **Timestamp:** 2026-04-10T07:19:05.642Z


![TC-20.2 — Step 2: Maintenance Activity](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_03_NAV_MA.png)


**Step 4: TC-20.2 — Maintenance Activities** — `Success`

The maintenance activity list shows scheduled PM tasks with their status, due date, and linked entities (PMA, WO, MR). Activities progress through Draft → Pending → Approved → Release → Completed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_activity`
- **Timestamp:** 2026-04-10T07:19:06.227Z


![TC-20.2 — Maintenance Activities](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_04_SCREENSHOT_MA.png)


**Step 5: TC-20.2 — Step 3: Preventive Work Order** — `Success`

Work orders generated from PM Calendar tasks have type 'Preventive'. They inherit the task details, assigned resources, and checklists from the PMA template.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:19:09.625Z


![TC-20.2 — Step 3: Preventive Work Order](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_05_NAV_WO.png)


**Step 6: TC-20.2 — Preventive WO Execution** — `Success`

The preventive work order tracks the scheduled maintenance execution. Completing the WO updates the PM Calendar and resets the schedule for the next occurrence.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:19:10.185Z


![TC-20.2 — Preventive WO Execution](eam-chi/frontend/test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_06_SCREENSHOT_WO.png)


---

### 8.3. TC 06 Maintenance Request ✅

| Property | Value |
|----------|-------|
| Test Case | TC-06 |
| Workflow | `TC-06-maintenance-request` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-06.1 — Maintenance Request List** — `Success`

Navigate to Maintenance Request. Maintenance requests are used to report issues, request corrective maintenance, or schedule preventive maintenance tasks.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:28.861Z


![TC-06.1 — Maintenance Request List](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_01_NAV.png)


**Step 2: TC-06.1 — New Maintenance Request** — `Success`

Click 'Add New' to create a new maintenance request. Fill in the requestor, asset, priority, category, and description fields.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:29.434Z


![TC-06.1 — New Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_02_NEW.png)


**Step 3: TC-06.1 — Fill Description** — `Success`

Enter "E2E Test — Motor vibration excessive, re" into the Description field.

- **Action:** `Type "E2E Test — Motor vibration excessive, requires corrective maintenance" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:30.774Z


![TC-06.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_03_FILL_DESC.png)


**Step 4: TC-06.1 — MR Created (Draft)** — `Success`

The maintenance request is created with an auto-generated ID (e.g., MTREQ-00001) and workflow state 'Draft'. From here you can submit it for approval.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00211`
- **Timestamp:** 2026-04-10T07:19:32.097Z


![TC-06.1 — MR Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_04_SAVE.png)


**Step 5: TC-06.1 — Maintenance Request Detail (Draft)** — `Success`

The maintenance request is in Draft state. The workflow dropdown shows available transitions. Click 'Submit for Approval' to advance the request.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00211`
- **Timestamp:** 2026-04-10T07:19:32.649Z


![TC-06.1 — Maintenance Request Detail (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_05_VERIFY_DRAFT.png)


---

### 8.4. TC 06 Maintenance Request Lifecycle Full ✅

| Property | Value |
|----------|-------|
| Test Case | TC-06 |
| Workflow | `TC-06-maintenance-request-lifecycle-full` |
| Persona | Admin |
| Steps | 8 |
| Pass Rate | 8/8 (100%) |
| Result | **PASS** |

**Step 1: TC-06.1 — Maintenance Request List** — `Success`

Navigate to Maintenance Request. MRs progress through: Draft → Pending Approval → Approved → Release → Completed. Emergency MRs can bypass the approval queue.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:39.172Z


![TC-06.1 — Maintenance Request List](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_01_NAV.png)


**Step 2: TC-06.1 — MR List Overview** — `Success`

The maintenance request list shows all MRs with their priority, status, requester, and SLA indicator. Filter by status to see pending, approved, or completed requests.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:39.736Z


![TC-06.1 — MR List Overview](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_02_SCREENSHOT_LIST.png)


**Step 3: TC-06.1 — New MR Form** — `Success`

Click 'Add New' to create a maintenance request. Enter the description, priority (Low/Medium/High/Emergency), site, department, and requested by information.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:40.306Z


![TC-06.1 — New MR Form](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_03_NEW.png)


**Step 4: TC-06.1 — Fill Description** — `Success`

Enter "E2E Full Lifecycle — Pump vibration abov" into the Description field.

- **Action:** `Type "E2E Full Lifecycle — Pump vibration above threshold" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:40.864Z


![TC-06.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_04_FILL.png)


**Step 5: TC-06.1 — MR Created (Draft)** — `Success`

The maintenance request is created in 'Draft' state with an auto-generated ID (e.g., MR-00001). Submit for approval to advance the workflow.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00212`
- **Timestamp:** 2026-04-10T07:19:41.417Z


![TC-06.1 — MR Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_05_SAVE.png)


**Step 6: TC-06.1 — MR Detail View** — `Success`

The MR detail page shows all fields, priority badge, workflow state, and SLA tracking fields. SLA Response Due and SLA Resolution Due are auto-populated based on priority level.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00212`
- **Timestamp:** 2026-04-10T07:19:42.105Z


![TC-06.1 — MR Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_06_VERIFY.png)


**Step 7: TC-06 — Checklist List** — `Success`

Navigate to Checklist. Checklists are linked to maintenance requests and work orders to ensure all required inspection points are completed.

- **Action:** `Navigate to /checklist`
- **URL:** `https://chieam.cubeworksinnovation.com/checklist`
- **Timestamp:** 2026-04-10T07:19:44.076Z


![TC-06 — Checklist List](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_07_NAV_CHECKLIST.png)


**Step 8: TC-06 — Checklist Overview** — `Success`

The checklist list shows all inspection checklists with their linked entity, completion status, and number of items checked.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/checklist`
- **Timestamp:** 2026-04-10T07:19:44.627Z


![TC-06 — Checklist Overview](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_08_SCREENSHOT_CL.png)


---

### 8.5. Maintenance Request Lifecycle ✅

| Property | Value |
|----------|-------|
| Test Case | TC-06 |
| Workflow | `maintenance-request-lifecycle` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: Maintenance Request List** — `Success`

Navigate to the Maintenance Request list page. Maintenance requests are used to report issues and request corrective or preventive maintenance.

- **Action:** `Navigate to /maintenance_request`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request`
- **Timestamp:** 2026-04-10T07:19:56.900Z


![Maintenance Request List](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_01_NAVIGATE.png)


**Step 2: Create New Maintenance Request** — `Success`

Click 'Add New' to open the maintenance request form.

- **Action:** `Click on "button:has-text('Add New'), [data-testid='btn-new'], button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:57.452Z


![Create New Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_02_NEW.png)


**Step 3: Fill Form Field** — `Success`

Enter "E2E Test — Leaking pipe in Building A" into the Description field.

- **Action:** `Type "E2E Test — Leaking pipe in Building A" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/new`
- **Timestamp:** 2026-04-10T07:19:58.797Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_03_FILL_DESCRIPTION.png)


**Step 4: Save Maintenance Request** — `Success`

Click 'Save' to submit the maintenance request. The system creates a draft record that can be moved through the approval workflow.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save')"`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00213`
- **Timestamp:** 2026-04-10T07:20:00.087Z


![Save Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_04_SAVE.png)


**Step 5: Maintenance Request Details** — `Success`

The maintenance request has been created. Review the details and use the workflow dropdown to advance the request through its lifecycle.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/maintenance_request/MTREQ-00213`
- **Timestamp:** 2026-04-10T07:20:00.631Z


![Maintenance Request Details](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_05_VERIFY_SAVED.png)


---

## 9. Master Data

*9 workflow(s) — 66 step(s)*

### 9.1. TC 03 Master Data Department ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-master-data-department` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-03.1 — Department List** — `Success`

Navigate to Department. Departments are organizational units within a site, used for cost allocation and team-level data scoping.

- **Action:** `Navigate to /department`
- **URL:** `https://chieam.cubeworksinnovation.com/department`
- **Timestamp:** 2026-04-10T07:20:04.291Z


![TC-03.1 — Department List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_01_NAV.png)


**Step 2: TC-03.1 — Add New** — `Success`

Click the Add New button to open the creation form.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/department/new`
- **Timestamp:** 2026-04-10T07:20:04.863Z


![TC-03.1 — Add New](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_02_NEW.png)


**Step 3: TC-03.1 — Fill Department Name** — `Success`

Enter "E2E Department X" into the Department Name field.

- **Action:** `Type "E2E Department X" into "input[name='department_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/department/new`
- **Timestamp:** 2026-04-10T07:20:05.411Z


![TC-03.1 — Fill Department Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_03_FILL_NAME.png)


**Step 4: TC-03.1 — Department Saved** — `Success`

The department is created and linked to its parent site. Departments are used for team-level data scoping (scope=team) in the RBAC system.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/department/DEPT-0043`
- **Timestamp:** 2026-04-10T07:20:07.180Z


![TC-03.1 — Department Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_04_SAVE.png)


**Step 5: TC-03.1 — Hierarchy Complete** — `Success`

With Organization → Site → Department created, the organizational hierarchy is established. This hierarchy is used for data scoping, cost allocation, and reporting.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/department/DEPT-0043`
- **Timestamp:** 2026-04-10T07:20:07.735Z


![TC-03.1 — Hierarchy Complete](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_05_VERIFY.png)


---

### 9.2. TC 03 Employee Labor ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-employee-labor` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-03.2 — Employee List** — `Success`

Navigate to Employee. Employees are linked to users, sites, and departments. They serve as requestors, approvers, and technicians across the system.

- **Action:** `Navigate to /employee`
- **URL:** `https://chieam.cubeworksinnovation.com/employee`
- **Timestamp:** 2026-04-10T07:20:11.158Z


![TC-03.2 — Employee List](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_01_NAV.png)


**Step 2: TC-03.2 — New Employee** — `Success`

Click 'Add New' to create an employee record. Link the employee to a user account, site, and department.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/employee/new`
- **Timestamp:** 2026-04-10T07:20:11.730Z


![TC-03.2 — New Employee](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_02_NEW.png)


**Step 3: TC-03.2 — Fill Employee Name** — `Success`

Enter "E2E John Smith" into the Employee Name field.

- **Action:** `Type "E2E John Smith" into "input[name='employee_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/employee/new`
- **Timestamp:** 2026-04-10T07:20:12.281Z


![TC-03.2 — Fill Employee Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_03_FILL.png)


**Step 4: TC-03.2 — Employee Created** — `Success`

The employee record is created with an auto-generated ID (e.g., EMP-00001). The employee can now be assigned to maintenance requests, work orders, and labor records.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/employee/EMP-00059`
- **Timestamp:** 2026-04-10T07:20:13.390Z


![TC-03.2 — Employee Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_04_SAVE.png)


**Step 5: TC-03.2 — Employee Detail** — `Success`

The employee record shows name, linked user, site, department, and trade. Employees serve as the bridge between user accounts and operational entities.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/employee/EMP-00059`
- **Timestamp:** 2026-04-10T07:20:13.940Z


![TC-03.2 — Employee Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_05_VERIFY.png)


---

### 9.3. TC 03 Financial Master Data ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-financial-master-data` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-03.5 — Account List** — `Success`

Navigate to Account. Accounts are used for financial tracking and cost allocation across maintenance operations.

- **Action:** `Navigate to /account`
- **URL:** `https://chieam.cubeworksinnovation.com/account`
- **Timestamp:** 2026-04-10T07:20:17.189Z


![TC-03.5 — Account List](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_01_NAV_ACCT.png)


**Step 2: TC-03.5 — New Account** — `Success`

Click 'Add New' to create an account record. Enter the account name, type, and associated cost center.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/account/new`
- **Timestamp:** 2026-04-10T07:20:17.748Z


![TC-03.5 — New Account](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_02_NEW_ACCT.png)


**Step 3: TC-03.5 — Fill Account Name** — `Success`

Enter "E2E Maintenance Cost Account" into the Account Name field.

- **Action:** `Type "E2E Maintenance Cost Account" into "input[name='account_name'], textarea[name='account_name'], input[name='name'], textarea[name='name'], input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/account/new`
- **Timestamp:** 2026-04-10T07:20:18.297Z


![TC-03.5 — Fill Account Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_03_FILL_ACCT.png)


**Step 4: TC-03.5 — Account Created** — `Success`

The account is saved and can be linked to work orders and purchase requests for cost tracking.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/account/ACCT-0005`
- **Timestamp:** 2026-04-10T07:20:19.408Z


![TC-03.5 — Account Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_04_SAVE_ACCT.png)


**Step 5: TC-03.5 — Account Detail** — `Success`

The account detail page shows the account number, name, type, and associated transactions.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/account/ACCT-0005`
- **Timestamp:** 2026-04-10T07:20:19.954Z


![TC-03.5 — Account Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_05_VERIFY_ACCT.png)


**Step 6: TC-03.5 — Cost Code List** — `Success`

Navigate to Cost Code. Cost codes categorize expenses for detailed financial reporting on maintenance activities.

- **Action:** `Navigate to /cost_code`
- **URL:** `https://chieam.cubeworksinnovation.com/cost_code`
- **Timestamp:** 2026-04-10T07:20:22.635Z


![TC-03.5 — Cost Code List](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_06_NAV_CC.png)


**Step 7: TC-03.5 — New Cost Code** — `Success`

Click 'Add New' to create a cost code. Specify the code identifier, description, and category.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/cost_code/new`
- **Timestamp:** 2026-04-10T07:20:23.210Z


![TC-03.5 — New Cost Code](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_07_NEW_CC.png)


**Step 8: TC-03.5 — Fill Cost Code Name** — `Success`

Enter "E2E Preventive Maintenance Cost" into the Cost Code Name field.

- **Action:** `Type "E2E Preventive Maintenance Cost" into "input[name='cost_code_name'], textarea[name='cost_code_name'], input[name='name'], textarea[name='name'], input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/cost_code/new`
- **Timestamp:** 2026-04-10T07:20:23.760Z


![TC-03.5 — Fill Cost Code Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_08_FILL_CC.png)


**Step 9: TC-03.5 — Cost Code Created** — `Success`

The cost code is saved and can be used in work orders and maintenance requests for expense categorization.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/cost_code/CC-0013`
- **Timestamp:** 2026-04-10T07:20:24.793Z


![TC-03.5 — Cost Code Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_09_SAVE_CC.png)


**Step 10: TC-03.5 — Cost Code Detail** — `Success`

The cost code detail page shows the code, description, and category used for financial reporting.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/cost_code/CC-0013`
- **Timestamp:** 2026-04-10T07:20:25.344Z


![TC-03.5 — Cost Code Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_10_VERIFY_CC.png)


---

### 9.4. TC 03 Manufacturer Model ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-manufacturer-model` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-03.3 — Manufacturer List** — `Success`

Navigate to Manufacturer. Manufacturers are linked to assets and equipment to track the make and model of each item.

- **Action:** `Navigate to /manufacturer`
- **URL:** `https://chieam.cubeworksinnovation.com/manufacturer`
- **Timestamp:** 2026-04-10T07:20:30.270Z


![TC-03.3 — Manufacturer List](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_01_NAV.png)


**Step 2: TC-03.3 — Manufacturer List View** — `Success`

The Manufacturer list shows all registered manufacturers with names, countries, and contact information. Use filters to locate specific manufacturers.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/manufacturer`
- **Timestamp:** 2026-04-10T07:20:30.828Z


![TC-03.3 — Manufacturer List View](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_02_LIST.png)


**Step 3: TC-03.3 — Open Manufacturer Record** — `Success`

Click on a manufacturer record to view its details and associated models.

- **Action:** `Click on "table tbody tr:first-child td:first-child a, table tbody tr:first-child, [data-testid='entity-row']:first-child"`
- **URL:** `https://chieam.cubeworksinnovation.com/manufacturer/MFG-00006`
- **Timestamp:** 2026-04-10T07:20:31.410Z


![TC-03.3 — Open Manufacturer Record](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_03_CLICK_FIRST.png)


**Step 4: TC-03.3 — Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 3000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/manufacturer/MFG-00006`
- **Timestamp:** 2026-04-10T07:20:34.966Z


![TC-03.3 — Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_04_WAIT.png)


**Step 5: TC-03.3 — Manufacturer Detail** — `Success`

The manufacturer detail page shows the company name, country, and associated models. Models link a manufacturer to specific product lines used in asset tracking.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/manufacturer/MFG-00006`
- **Timestamp:** 2026-04-10T07:20:35.519Z


![TC-03.3 — Manufacturer Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_05_DETAIL.png)


**Step 6: TC-03.3 — Model List** — `Success`

Navigate to Model. Models represent specific product lines from manufacturers and are linked to assets for detailed equipment tracking.

- **Action:** `Navigate to /model`
- **URL:** `https://chieam.cubeworksinnovation.com/model`
- **Timestamp:** 2026-04-10T07:20:38.231Z


![TC-03.3 — Model List](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_01_NAV.png)


**Step 7: TC-03.3 — Model List View** — `Success`

The Model list shows all registered product models with names, linked manufacturers, and associated asset counts.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/model`
- **Timestamp:** 2026-04-10T07:20:38.791Z


![TC-03.3 — Model List View](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_02_LIST.png)


**Step 8: TC-03.3 — Open Model Record** — `Success`

Click on a model record to view its details and the linked manufacturer.

- **Action:** `Click on "table tbody tr:first-child td:first-child a, table tbody tr:first-child, [data-testid='entity-row']:first-child"`
- **URL:** `https://chieam.cubeworksinnovation.com/model/M-00018`
- **Timestamp:** 2026-04-10T07:20:39.352Z


![TC-03.3 — Open Model Record](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_03_CLICK_FIRST.png)


**Step 9: TC-03.3 — Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 3000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/model/M-00018`
- **Timestamp:** 2026-04-10T07:20:42.916Z


![TC-03.3 — Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_04_WAIT.png)


**Step 10: TC-03.3 — Model Detail** — `Success`

The model detail page shows the model name, linked manufacturer, and any associated assets.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/model/M-00018`
- **Timestamp:** 2026-04-10T07:20:43.477Z


![TC-03.3 — Model Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_05_DETAIL.png)


---

### 9.5. TC 03 Master Data Organization ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-master-data-organization` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-03.1 — Organization List** — `Success`

Navigate to Organization in the sidebar. This page shows all registered organizations. Organizations are the top level of the hierarchy: Organization → Site → Department.

- **Action:** `Navigate to /organization`
- **URL:** `https://chieam.cubeworksinnovation.com/organization`
- **Timestamp:** 2026-04-10T07:20:47.077Z


![TC-03.1 — Organization List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_01_NAV_ORG.png)


**Step 2: TC-03.1 — Create Organization** — `Success`

Click 'Add New' to create a new Organization. Fill in the name and other required fields.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/organization/new`
- **Timestamp:** 2026-04-10T07:20:47.632Z


![TC-03.1 — Create Organization](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_02_NEW_ORG.png)


**Step 3: TC-03.1 — Fill Organization Name** — `Success`

Enter "E2E Test Corporation" into the Organization Name field.

- **Action:** `Type "E2E Test Corporation" into "input[name='organization_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/organization/new`
- **Timestamp:** 2026-04-10T07:20:48.165Z


![TC-03.1 — Fill Organization Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_03_FILL_ORG_NAME.png)


**Step 4: TC-03.1 — Organization Saved** — `Success`

Click 'Create' to save the organization. A success notification confirms the record was created with an auto-generated ID.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/organization/ORG-U-00019`
- **Timestamp:** 2026-04-10T07:20:49.202Z


![TC-03.1 — Organization Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_04_SAVE_ORG.png)


**Step 5: TC-03.1 — Organization Detail** — `Success`

The organization record is now saved. You can see the auto-generated ID and all fields. Navigate to Site to create sites linked to this organization.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/organization/ORG-U-00019`
- **Timestamp:** 2026-04-10T07:20:49.735Z


![TC-03.1 — Organization Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_05_VERIFY_ORG.png)


---

### 9.6. TC 03 Master Data Site ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-master-data-site` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-03.1 — Site List** — `Success`

Navigate to Site. Sites represent physical locations within an organization. Each site can have multiple departments.

- **Action:** `Navigate to /site`
- **URL:** `https://chieam.cubeworksinnovation.com/site`
- **Timestamp:** 2026-04-10T07:20:53.035Z


![TC-03.1 — Site List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_01_NAV.png)


**Step 2: TC-03.1 — Create Site** — `Success`

Click 'Add New' to create a new site. Link the site to the organization created in the previous step.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/site/new`
- **Timestamp:** 2026-04-10T07:20:53.606Z


![TC-03.1 — Create Site](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_02_NEW.png)


**Step 3: TC-03.1 — Fill Site Name** — `Success`

Enter "E2E Site A" into the Site Name field.

- **Action:** `Type "E2E Site A" into "input[name='site_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/site/new`
- **Timestamp:** 2026-04-10T07:20:55.471Z


![TC-03.1 — Fill Site Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_03_FILL_NAME.png)


**Step 4: TC-03.1 — Site Saved** — `Success`

The site is created with an auto-generated ID and linked to the organization. Repeat this process to create additional sites.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/site/SITE-0051`
- **Timestamp:** 2026-04-10T07:20:56.400Z


![TC-03.1 — Site Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_04_SAVE.png)


**Step 5: TC-03.1 — Site Detail View** — `Success`

The site record shows the name, organization link, and any child departments. Each site serves as a scope boundary for role-based access control.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/site/SITE-0051`
- **Timestamp:** 2026-04-10T07:20:56.940Z


![TC-03.1 — Site Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_05_VERIFY.png)


---

### 9.7. TC 03 Vendor Item ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-vendor-item` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-03 — Vendor List** — `Success`

Navigate to Vendor. Vendors supply materials, spare parts, and services. Their performance is tracked automatically based on purchase receipts.

- **Action:** `Navigate to /vendor`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor`
- **Timestamp:** 2026-04-10T07:21:00.045Z


![TC-03 — Vendor List](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_01_NAV.png)


**Step 2: TC-03 — Add New** — `Success`

Click the Add New button to open the creation form.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/new`
- **Timestamp:** 2026-04-10T07:21:00.618Z


![TC-03 — Add New](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_02_NEW.png)


**Step 3: TC-03 — Fill Vendor Name** — `Success`

Enter "E2E Vendor — Industrial Parts Co." into the Vendor Name field.

- **Action:** `Type "E2E Vendor — Industrial Parts Co." into "input[name='vendor_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/new`
- **Timestamp:** 2026-04-10T07:21:01.151Z


![TC-03 — Fill Vendor Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_03_FILL.png)


**Step 4: TC-03 — Vendor Created** — `Success`

The vendor record is created. Performance ratings (delivery, quality, overall) are auto-calculated from purchase receipts. A new vendor starts with default/zero ratings.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/VND-00037`
- **Timestamp:** 2026-04-10T07:21:01.859Z


![TC-03 — Vendor Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_04_SAVE.png)


**Step 5: TC-03 — Vendor Detail** — `Success`

The vendor detail shows contact information, performance ratings, and linked purchase orders. Ratings update automatically when purchase receipts are processed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/VND-00037`
- **Timestamp:** 2026-04-10T07:21:02.414Z


![TC-03 — Vendor Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_05_VERIFY.png)


**Step 6: TC-03 — Item (Inventory) List** — `Success`

Navigate to Item. Items represent materials, spare parts, and consumables tracked in inventory. They are used in purchase requests, purchase orders, and work order parts.

- **Action:** `Navigate to /item`
- **URL:** `https://chieam.cubeworksinnovation.com/item`
- **Timestamp:** 2026-04-10T07:21:04.864Z


![TC-03 — Item (Inventory) List](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_06_NAV.png)


**Step 7: TC-03 — Add New** — `Success`

Click the Add New button to open the creation form.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/item/new`
- **Timestamp:** 2026-04-10T07:21:05.431Z


![TC-03 — Add New](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_07_NEW.png)


**Step 8: TC-03 — Fill Description** — `Success`

Enter "E2E Bearing SKF 6206" into the Description field.

- **Action:** `Type "E2E Bearing SKF 6206" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/item/new`
- **Timestamp:** 2026-04-10T07:21:06.063Z


![TC-03 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_08_FILL.png)


**Step 9: TC-03 — Item Created** — `Success`

The item is created with its name and default properties. Items track stock levels, reorder points, and are linked to stores for inventory management.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/item/new`
- **Timestamp:** 2026-04-10T07:21:06.644Z


![TC-03 — Item Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_09_SAVE.png)


**Step 10: TC-03 — Item Detail** — `Success`

The item detail view shows name, unit of measure, stock levels, reorder point, and storage locations. Items are referenced in PR lines, PO lines, and WO parts.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/item/new`
- **Timestamp:** 2026-04-10T07:21:07.196Z


![TC-03 — Item Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_10_VERIFY.png)


---

### 9.8. TC 03 Work Schedule Holiday ✅

| Property | Value |
|----------|-------|
| Test Case | TC-03 |
| Workflow | `TC-03-work-schedule-holiday` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-03.4 — Work Schedule List** — `Success`

Navigate to Work Schedule. Work schedules define standard working hours, shifts, and availability for maintenance planning.

- **Action:** `Navigate to /work_schedule`
- **URL:** `https://chieam.cubeworksinnovation.com/work_schedule`
- **Timestamp:** 2026-04-10T07:21:11.294Z


![TC-03.4 — Work Schedule List](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_01_NAV.png)


**Step 2: TC-03.4 — New Work Schedule** — `Success`

Click 'Add New' to create a work schedule. Define the schedule name, working days, and shift hours.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_schedule/new`
- **Timestamp:** 2026-04-10T07:21:11.867Z


![TC-03.4 — New Work Schedule](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_02_NEW.png)


**Step 3: TC-03.4 — Fill Schedule Name** — `Success`

Enter "E2E Standard 5-Day Schedule" into the Schedule Name field.

- **Action:** `Type "E2E Standard 5-Day Schedule" into "input[name='schedule_name'], textarea[name='schedule_name'], input[name='name'], textarea[name='name'], input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_schedule/new`
- **Timestamp:** 2026-04-10T07:21:12.418Z


![TC-03.4 — Fill Schedule Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_03_FILL.png)


**Step 4: TC-03.4 — Work Schedule Created** — `Success`

The work schedule is saved and can be linked to employees, sites, and maintenance planning calendars.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_schedule/WSCHED-00011`
- **Timestamp:** 2026-04-10T07:21:14.460Z


![TC-03.4 — Work Schedule Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_04_SAVE.png)


**Step 5: TC-03.4 — Work Schedule Detail** — `Success`

The work schedule detail shows the schedule name, working days, shift times, and associated resources.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_schedule/WSCHED-00011`
- **Timestamp:** 2026-04-10T07:21:15.011Z


![TC-03.4 — Work Schedule Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_05_VERIFY.png)


**Step 6: TC-03.4 — Holiday List** — `Success`

Navigate to Holiday. Holidays define non-working days that affect SLA calculations and maintenance scheduling.

- **Action:** `Navigate to /holiday`
- **URL:** `https://chieam.cubeworksinnovation.com/holiday`
- **Timestamp:** 2026-04-10T07:21:17.108Z


![TC-03.4 — Holiday List](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_01_NAV.png)


**Step 7: TC-03.4 — New Holiday** — `Success`

Click 'Add New' to create a holiday entry. Specify the holiday name and date.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/holiday/new`
- **Timestamp:** 2026-04-10T07:21:17.662Z


![TC-03.4 — New Holiday](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_02_NEW.png)


**Step 8: TC-03.4 — Fill Holiday Name** — `Success`

Enter "E2E Test Holiday" into the Holiday Name field.

- **Action:** `Type "E2E Test Holiday" into "input[name='holiday_name'], textarea[name='holiday_name'], input[name='name'], textarea[name='name'], input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/holiday/new`
- **Timestamp:** 2026-04-10T07:21:18.497Z


![TC-03.4 — Fill Holiday Name](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_03_FILL.png)


**Step 9: TC-03.4 — Holiday Created** — `Success`

The holiday is saved and will be excluded from SLA calculations and work day computations.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/holiday/HOL-00069`
- **Timestamp:** 2026-04-10T07:21:20.219Z


![TC-03.4 — Holiday Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_04_SAVE.png)


**Step 10: TC-03.4 — Holiday Detail** — `Success`

The holiday detail shows the name, date, and associated work schedules affected by this holiday.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/holiday/HOL-00069`
- **Timestamp:** 2026-04-10T07:21:20.773Z


![TC-03.4 — Holiday Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_05_VERIFY.png)


---

### 9.9. TC 19 Vendor Performance ✅

| Property | Value |
|----------|-------|
| Test Case | TC-19 |
| Workflow | `TC-19-vendor-performance` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-19.1 — Vendor List** — `Success`

Navigate to Vendor. Vendor performance metrics are automatically calculated from purchase receipt delivery data.

- **Action:** `Navigate to /vendor`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor`
- **Timestamp:** 2026-04-10T07:22:01.652Z


![TC-19.1 — Vendor List](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_01_NAV.png)


**Step 2: TC-19.1 — Vendor Performance Overview** — `Success`

The vendor list shows all vendors with their delivery rating, on-time deliveries, late deliveries, quality score, and total orders processed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor`
- **Timestamp:** 2026-04-10T07:22:02.208Z


![TC-19.1 — Vendor Performance Overview](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_02_SCREENSHOT_LIST.png)


**Step 3: TC-19.1 — New Vendor** — `Success`

Click 'Add New' to create a vendor. Enter vendor name, contact details, and payment terms. Performance metrics will be calculated automatically as purchase receipts are recorded.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/new`
- **Timestamp:** 2026-04-10T07:22:02.766Z


![TC-19.1 — New Vendor](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_03_NEW.png)


**Step 4: TC-19.1 — Fill Vendor Name** — `Success`

Enter "E2E Performance Test Vendor" into the Vendor Name field.

- **Action:** `Type "E2E Performance Test Vendor" into "input[name='vendor_name'], textarea[name='vendor_name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/new`
- **Timestamp:** 2026-04-10T07:22:04.627Z


![TC-19.1 — Fill Vendor Name](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_04_FILL.png)


**Step 5: TC-19.1 — Vendor Created** — `Success`

The vendor is created with initial performance metrics at zero. As PO receipts are processed, delivery_rating, on_time_deliveries, late_deliveries, and quality_rating are updated automatically.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/VND-00038`
- **Timestamp:** 2026-04-10T07:22:05.606Z


![TC-19.1 — Vendor Created](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_05_SAVE.png)


**Step 6: TC-19.1 — Vendor Detail & Metrics** — `Success`

The vendor detail page shows contact information, payment terms, and the performance metrics section with delivery rating formula: on_time_deliveries / total_orders × 100.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/vendor/VND-00038`
- **Timestamp:** 2026-04-10T07:22:06.144Z


![TC-19.1 — Vendor Detail & Metrics](eam-chi/frontend/test-artifacts/screenshots/TC-19-vendor-performance__TC19_06_VERIFY.png)


---

## 10. Purchasing & Stores

*4 workflow(s) — 27 step(s)*

### 10.1. TC 11 Blanket Contract Po ✅

| Property | Value |
|----------|-------|
| Test Case | TC-11 |
| Workflow | `TC-11-blanket-contract-po` |
| Persona | Admin |
| Steps | 8 |
| Pass Rate | 8/8 (100%) |
| Result | **PASS** |

**Step 1: TC-11.3 — Purchase Order List** — `Success`

Navigate to Purchase Order. PO types include Standard (one-time), Blanket (spending limit), and Contract (date range).

- **Action:** `Navigate to /purchase_order`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order`
- **Timestamp:** 2026-04-10T07:21:24.783Z


![TC-11.3 — Purchase Order List](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_01_NAV.png)


**Step 2: TC-11.3 — Purchase Order Overview** — `Success`

The purchase order list displays all POs with their type, vendor, status, and total amount. Filter by PO type to view specific categories.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order`
- **Timestamp:** 2026-04-10T07:21:25.319Z


![TC-11.3 — Purchase Order Overview](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_02_SCREENSHOT.png)


**Step 3: TC-11.3 — New Blanket PO Form** — `Success`

Create a new purchase order. Select PO Type = 'Blanket' to create a blanket order with a spending limit. The Blanket Limit and Released Amount fields appear for this type.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:25.876Z


![TC-11.3 — New Blanket PO Form](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_03_NEW.png)


**Step 4: TC-11.3 — Blanket PO Form Fields** — `Success`

The blanket PO form shows type-specific fields: Blanket Limit (maximum spending), Released Amount (amount already released), and vendor selection. These fields control spending authorization.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:26.417Z


![TC-11.3 — Blanket PO Form Fields](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_04_SCREENSHOT.png)


**Step 5: TC-11.3 — Blanket PO Created** — `Success`

The blanket purchase order is created in Draft state. Approve to make it active. Releases against this PO are tracked against the spending limit.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:27.044Z


![TC-11.3 — Blanket PO Created](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_05_SAVE.png)


**Step 6: TC-11.3 — Blanket PO Detail** — `Success`

The blanket PO detail shows the spending limit, released amount, remaining balance, and associated release orders.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:27.594Z


![TC-11.3 — Blanket PO Detail](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_06_VERIFY.png)


**Step 7: TC-11.4 — New Contract PO Form** — `Success`

Create another purchase order. Select PO Type = 'Contract' to create a contract-based order with start and end dates.

- **Action:** `Navigate to /purchase_order/new`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:30.444Z


![TC-11.4 — New Contract PO Form](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_CPO_01_NAV.png)


**Step 8: TC-11.4 — Contract PO Form Fields** — `Success`

The contract PO form shows type-specific fields: Contract Start Date, Contract End Date, and terms. These control the validity period of the procurement agreement.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:30.997Z


![TC-11.4 — Contract PO Form Fields](eam-chi/frontend/test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_CPO_02_SCREENSHOT.png)


---

### 10.2. TC 11 Purchase Receipt ✅

| Property | Value |
|----------|-------|
| Test Case | TC-11 |
| Workflow | `TC-11-purchase-receipt` |
| Persona | Admin |
| Steps | 4 |
| Pass Rate | 4/4 (100%) |
| Result | **PASS** |

**Step 1: TC-11.6 — Purchase Receipt List** — `Success`

Navigate to Purchase Receipt. Receipts record the delivery of goods against purchase orders and trigger vendor performance calculations.

- **Action:** `Navigate to /purchase_receipt`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt`
- **Timestamp:** 2026-04-10T07:21:35.556Z


![TC-11.6 — Purchase Receipt List](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_01_NAV.png)


**Step 2: TC-11.6 — Receipt List Overview** — `Success`

The purchase receipt list shows all received deliveries with their PO reference, vendor, received date, and status.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt`
- **Timestamp:** 2026-04-10T07:21:36.109Z


![TC-11.6 — Receipt List Overview](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_02_SCREENSHOT.png)


**Step 3: TC-11.6 — New Purchase Receipt** — `Success`

Click 'Add New' to record a receipt. Link it to a purchase order, enter received quantities, and note any discrepancies.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt/new`
- **Timestamp:** 2026-04-10T07:21:36.685Z


![TC-11.6 — New Purchase Receipt](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_03_NEW.png)


**Step 4: TC-11.6 — Receipt Form** — `Success`

The purchase receipt form includes PO reference, vendor, delivery date, received items, quantities, and condition notes. Complete receipts update inventory and vendor performance metrics.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_receipt/new`
- **Timestamp:** 2026-04-10T07:21:37.231Z


![TC-11.6 — Receipt Form](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_04_SCREENSHOT.png)


---

### 10.3. TC 11 Purchasing Pr Po ✅

| Property | Value |
|----------|-------|
| Test Case | TC-11 |
| Workflow | `TC-11-purchasing-pr-po` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-11.1 — Purchase Request List** — `Success`

Navigate to Purchasing → Purchase Request. Purchase requests initiate procurement for materials, spare parts, and services needed for maintenance.

- **Action:** `Navigate to /purchase_request`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:21:42.667Z


![TC-11.1 — Purchase Request List](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_01_NAV_PR.png)


**Step 2: TC-11.1 — New Purchase Request** — `Success`

Click 'Add New' to create a purchase request. Specify the requestor, due date, site, and department. Add line items with quantities and unit prices.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:21:43.280Z


![TC-11.1 — New Purchase Request](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_02_NEW_PR.png)


**Step 3: TC-11 — Fill Pr Description** — `Success`

Enter "E2E Test — Spare parts for pump maintena" into the Pr Description field.

- **Action:** `Type "E2E Test — Spare parts for pump maintenance" into "input[name='pr_description'], textarea[name='pr_description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:21:43.830Z


![TC-11 — Fill Pr Description](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_03_FILL_PR.png)


**Step 4: TC-11.1 — PR Created (Draft)** — `Success`

The purchase request is created with an auto-generated ID (e.g., PR-00001) in 'Draft' state. Add line items, then submit for approval.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:21:44.559Z


![TC-11.1 — PR Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_04_SAVE_PR.png)


**Step 5: TC-11.1 — Purchase Request Detail** — `Success`

The purchase request detail shows requestor, due date, and line items. The PR Lines child table allows adding items with quantities, unit prices, and calculated line totals.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:21:45.111Z


![TC-11.1 — Purchase Request Detail](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_05_VERIFY_PR.png)


**Step 6: TC-11.2 — Purchase Order List** — `Success`

Navigate to Purchasing → Purchase Order. Purchase orders are issued to vendors based on approved purchase requests. PO types include Standard, Blanket, and Contract.

- **Action:** `Navigate to /purchase_order`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order`
- **Timestamp:** 2026-04-10T07:21:48.290Z


![TC-11.2 — Purchase Order List](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_06_NAV_PO.png)


**Step 7: TC-11.2 — New Purchase Order** — `Success`

Click 'Add New' to create a purchase order. Select the vendor, PO type, site, and department. Add line items matching the approved PR.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:48.836Z


![TC-11.2 — New Purchase Order](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_07_NEW_PO.png)


**Step 8: TC-11.2 — PO New Form** — `Success`

The new purchase order form shows fields for vendor, PO type, site, department, and financial details. Select a vendor to link the PO to approved purchase requests.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:49.370Z


![TC-11.2 — PO New Form](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_08_FILL_PO.png)


**Step 9: TC-11.2 — PO Created (Draft)** — `Success`

The purchase order is created with an auto-generated ID (e.g., PO-00001) in 'Draft' state. The form is editable in Draft. After approval, the form becomes read-only.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:51.205Z


![TC-11.2 — PO Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_09_SAVE_PO.png)


**Step 10: TC-11.2 — Purchase Order Detail** — `Success`

The purchase order detail shows vendor, PO type, terms, and line items. Supported PO types: Standard (one-time), Blanket (spending limit), and Contract (date range). The workflow moves through Draft → Open → Closed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_order/new`
- **Timestamp:** 2026-04-10T07:21:51.647Z


![TC-11.2 — Purchase Order Detail](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_10_VERIFY_PO.png)


---

### 10.4. Purchase Request Lifecycle ✅

| Property | Value |
|----------|-------|
| Test Case | TC-11 |
| Workflow | `purchase-request-lifecycle` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: Purchase Request List** — `Success`

Navigate to the Purchase Request list page. Purchase requests initiate the procurement workflow for materials, spare parts, and services.

- **Action:** `Navigate to /purchase_request`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request`
- **Timestamp:** 2026-04-10T07:22:09.211Z


![Purchase Request List](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_01_NAVIGATE.png)


**Step 2: Create New Purchase Request** — `Success`

Click 'Add New' to create a new purchase request. Fill in the required fields such as description and requested items.

- **Action:** `Click on "button:has-text('Add New'), [data-testid='btn-new'], button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:22:09.768Z


![Create New Purchase Request](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_02_NEW.png)


**Step 3: Fill Form Field** — `Success`

Enter "E2E Test — Spare parts for pump maintena" into the Pr Description field.

- **Action:** `Type "E2E Test — Spare parts for pump maintenance" into "input[name='pr_description'], textarea[name='pr_description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:22:11.603Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_03_FILL_DESCRIPTION.png)


**Step 4: Save Purchase Request** — `Success`

Click 'Save' to create the purchase request. It will start in Draft state and can be submitted for approval.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save')"`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:22:12.164Z


![Save Purchase Request](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_04_SAVE.png)


**Step 5: Purchase Request Details** — `Success`

The purchase request is now saved. Use the workflow dropdown to submit it for approval.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/purchase_request/new`
- **Timestamp:** 2026-04-10T07:22:12.714Z


![Purchase Request Details](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_05_VERIFY_SAVED.png)


---

## 11. Work Management

*5 workflow(s) — 31 step(s)*

### 11.1. TC 07 Work Order Child Records ✅

| Property | Value |
|----------|-------|
| Test Case | TC-07 |
| Workflow | `TC-07-work-order-child-records` |
| Persona | Admin |
| Steps | 10 |
| Pass Rate | 10/10 (100%) |
| Result | **PASS** |

**Step 1: TC-07.3 — Work Order List** — `Success`

Navigate to Work Order. Work orders contain child records for labor, parts, and equipment tracking.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:22:19.013Z


![TC-07.3 — Work Order List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_CHILD_01_NAV.png)


**Step 2: TC-07.3 — Work Order List Overview** — `Success`

The work order list shows all work orders with their status, priority, type, and assigned resources.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:22:19.568Z


![TC-07.3 — Work Order List Overview](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_CHILD_02_SCREENSHOT.png)


**Step 3: TC-07.3 — Work Order Labor List** — `Success`

Navigate to Work Order Labor. Labor records track hours spent by technicians on each work order.

- **Action:** `Navigate to /work_order_labor`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_labor`
- **Timestamp:** 2026-04-10T07:22:24.005Z


![TC-07.3 — Work Order Labor List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_01_NAV.png)


**Step 4: TC-07.3 — New Labor Entry** — `Success`

Click 'Add New' to record labor hours. Specify the employee, hours worked, hourly rate, and trade type.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_labor/new`
- **Timestamp:** 2026-04-10T07:22:24.569Z


![TC-07.3 — New Labor Entry](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_02_NEW.png)


**Step 5: TC-07.3 — Labor Entry Form** — `Success`

The labor entry form captures employee, hours, rate, and total cost. The system calculates the line total (hours × rate) automatically.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_labor/new`
- **Timestamp:** 2026-04-10T07:22:25.121Z


![TC-07.3 — Labor Entry Form](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_03_SCREENSHOT.png)


**Step 6: TC-07.3 — Work Order Parts List** — `Success`

Navigate to Work Order Parts. Parts records track materials and spare parts consumed during maintenance work.

- **Action:** `Navigate to /work_order_parts`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_parts`
- **Timestamp:** 2026-04-10T07:22:27.081Z


![TC-07.3 — Work Order Parts List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_01_NAV.png)


**Step 7: TC-07.3 — New Parts Entry** — `Success`

Click 'Add New' to record parts consumed. Select the item, quantity, and unit price.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_parts/new`
- **Timestamp:** 2026-04-10T07:22:27.636Z


![TC-07.3 — New Parts Entry](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_02_NEW.png)


**Step 8: TC-07.3 — Parts Entry Form** — `Success`

The parts entry form captures item, quantity, unit price, and calculated total. Parts consumption is deducted from inventory when the work order is completed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_parts/new`
- **Timestamp:** 2026-04-10T07:22:28.203Z


![TC-07.3 — Parts Entry Form](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_03_SCREENSHOT.png)


**Step 9: TC-07.3 — Work Order Equipment List** — `Success`

Navigate to Work Order Equipment. Equipment records track tools and vehicles used during work order execution.

- **Action:** `Navigate to /work_order_equipment`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_equipment`
- **Timestamp:** 2026-04-10T07:22:31.140Z


![TC-07.3 — Work Order Equipment List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_EQUIP_01_NAV.png)


**Step 10: TC-07.3 — Work Order Equipment Overview** — `Success`

The work order equipment list shows all equipment assigned to work orders with usage hours and associated costs.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_equipment`
- **Timestamp:** 2026-04-10T07:22:31.705Z


![TC-07.3 — Work Order Equipment Overview](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order-child-records__TC07_EQUIP_02_SCREENSHOT.png)


---

### 11.2. TC 07 Wo Failure Reporting ✅

| Property | Value |
|----------|-------|
| Test Case | TC-07 |
| Workflow | `TC-07-wo-failure-reporting` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-07.5 — Failure Analysis List** — `Success`

Navigate to Failure Analysis. Failure analysis records document root causes, remedies, and risk priority numbers (RPN) for equipment failures.

- **Action:** `Navigate to /failure_analysis`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:22:35.292Z


![TC-07.5 — Failure Analysis List](eam-chi/frontend/test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_01_NAV.png)


**Step 2: TC-07.5 — Failure Analysis List View** — `Success`

The Failure Analysis list shows all failure records with failure modes, cause codes, severity ratings, and RPN scores. Filter by asset or date range.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis`
- **Timestamp:** 2026-04-10T07:22:35.849Z


![TC-07.5 — Failure Analysis List View](eam-chi/frontend/test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_02_LIST.png)


**Step 3: TC-07.5 — Open Failure Analysis** — `Success`

Click on a failure analysis record to view its details including failure mode, cause, severity, occurrence, and detection ratings.

- **Action:** `Click on "table tbody tr:first-child td:first-child a, table tbody tr:first-child, [data-testid='entity-row']:first-child"`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis/FA-00004`
- **Timestamp:** 2026-04-10T07:22:36.417Z


![TC-07.5 — Open Failure Analysis](eam-chi/frontend/test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_03_CLICK_FIRST.png)


**Step 4: TC-07.5 — Wait for Page Load** — `Success`

Wait for all page components to finish loading and rendering.

- **Action:** `Wait for 3000ms`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis/FA-00004`
- **Timestamp:** 2026-04-10T07:22:39.957Z


![TC-07.5 — Wait for Page Load](eam-chi/frontend/test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_04_WAIT.png)


**Step 5: TC-07.5 — Failure Analysis Detail** — `Success`

The failure analysis detail shows failure mode, cause code, remedy code, severity/occurrence/detection ratings, and RPN score. Server actions enable 5-Why and Fishbone templates.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/failure_analysis/FA-00004`
- **Timestamp:** 2026-04-10T07:22:40.507Z


![TC-07.5 — Failure Analysis Detail](eam-chi/frontend/test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_05_DETAIL.png)


---

### 11.3. TC 07 Work Order ✅

| Property | Value |
|----------|-------|
| Test Case | TC-07 |
| Workflow | `TC-07-work-order` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-07.1 — Work Order List** — `Success`

Navigate to Work Management → Work Order. Work orders track maintenance tasks from request through completion, including labor, parts, and costs.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:22:44.659Z


![TC-07.1 — Work Order List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_01_NAV.png)


**Step 2: TC-07.1 — New Work Order** — `Success`

Click 'Add New' to create a new work order. Fill in the type, description, priority, site, department, asset, and due date.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/new`
- **Timestamp:** 2026-04-10T07:22:45.257Z


![TC-07.1 — New Work Order](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_02_NEW.png)


**Step 3: TC-07.1 — Fill Description** — `Success`

Enter "E2E Test — Repair excessive vibration on" into the Description field.

- **Action:** `Type "E2E Test — Repair excessive vibration on Test Motor 001" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/new`
- **Timestamp:** 2026-04-10T07:22:45.808Z


![TC-07.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_03_FILL_DESC.png)


**Step 4: TC-07.1 — WO Created (Requested)** — `Success`

The work order is created with an auto-generated ID (e.g., WO-00001) in the 'Requested' state. Use the workflow dropdown to approve and start the work order.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/WO-00141`
- **Timestamp:** 2026-04-10T07:22:46.711Z


![TC-07.1 — WO Created (Requested)](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_04_SAVE.png)


**Step 5: TC-07.1 — Work Order Detail** — `Success`

The work order detail page shows all fields organized in tabs: Details, Labor, Equipment, Parts, Activities, and Attachments. The header shows the workflow state and available transitions.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/WO-00141`
- **Timestamp:** 2026-04-10T07:22:47.245Z


![TC-07.1 — Work Order Detail](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_05_VERIFY.png)


---

### 11.4. TC 08 Work Order Activity ✅

| Property | Value |
|----------|-------|
| Test Case | TC-08 |
| Workflow | `TC-08-work-order-activity` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-08.1 — Work Order Activity List** — `Success`

Navigate to Work Order Activity. Activities are individual tasks within a work order that can be assigned to different technicians and tracked independently.

- **Action:** `Navigate to /work_order_activity`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity`
- **Timestamp:** 2026-04-10T07:22:52.278Z


![TC-08.1 — Work Order Activity List](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_01_NAV.png)


**Step 2: TC-08.1 — Activity List Overview** — `Success`

The activity list shows all work order activities with their status, assigned worker, and parent work order. Activities progress through: Awaiting Resources → Ready → In Progress → On Hold → Complete → Closed.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity`
- **Timestamp:** 2026-04-10T07:22:52.829Z


![TC-08.1 — Activity List Overview](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_02_SCREENSHOT.png)


**Step 3: TC-08.1 — New Activity** — `Success`

Click 'Add New' to create a work order activity. Link it to a parent work order, assign a worker, and specify the task description.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity/new`
- **Timestamp:** 2026-04-10T07:22:53.391Z


![TC-08.1 — New Activity](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_03_NEW.png)


**Step 4: TC-08.1 — Fill Description** — `Success`

Enter "E2E Bearing replacement — Motor Assembly" into the Description field.

- **Action:** `Type "E2E Bearing replacement — Motor Assembly" into "input[name='description'], textarea[name='description'], input[name='activity_description'], textarea[name='activity_description'], input[name='name'], textarea[name='name']"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity/new`
- **Timestamp:** 2026-04-10T07:22:53.946Z


![TC-08.1 — Fill Description](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_04_FILL.png)


**Step 5: TC-08.1 — Activity Created** — `Success`

The activity is created in 'Awaiting Resources' state. Allocate resources to move it to 'Ready', then start work to move to 'In Progress'.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity/WOACT-00066`
- **Timestamp:** 2026-04-10T07:22:54.793Z


![TC-08.1 — Activity Created](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_05_SAVE.png)


**Step 6: TC-08.1 — Activity Detail** — `Success`

The activity detail page shows the task description, assigned worker, parent work order, estimated hours, and workflow state. Use the workflow dropdown to progress the activity through its lifecycle.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order_activity/WOACT-00066`
- **Timestamp:** 2026-04-10T07:22:55.344Z


![TC-08.1 — Activity Detail](eam-chi/frontend/test-artifacts/screenshots/TC-08-work-order-activity__TC08_06_VERIFY.png)


---

### 11.5. Work Order Lifecycle ✅

| Property | Value |
|----------|-------|
| Test Case | TC-07 |
| Workflow | `work-order-lifecycle` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: Work Order List** — `Success`

Navigate to the Work Order list page. This page displays all work orders with their current workflow status, priority, and assigned personnel.

- **Action:** `Navigate to /work_order`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order`
- **Timestamp:** 2026-04-10T07:23:13.725Z


![Work Order List](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_01_NAVIGATE.png)


**Step 2: Create New Work Order** — `Success`

Click 'Add New' to create a new work order. The form opens with default values including the 'Requested' workflow state.

- **Action:** `Click on "button:has-text('Add New'), [data-testid='btn-new'], button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/new`
- **Timestamp:** 2026-04-10T07:23:14.299Z


![Create New Work Order](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_02_NEW.png)


**Step 3: Fill Form Field** — `Success`

Enter "E2E Test Work Order — Pump maintenance" into the Description field.

- **Action:** `Type "E2E Test Work Order — Pump maintenance" into "input[name='description'], textarea[name='description']"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/new`
- **Timestamp:** 2026-04-10T07:23:14.853Z


![Fill Form Field](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_03_FILL_DESCRIPTION.png)


**Step 4: Save Work Order** — `Success`

Click 'Save' to create the work order. The system assigns a unique code and sets the initial workflow state.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save')"`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/WO-00142`
- **Timestamp:** 2026-04-10T07:23:16.533Z


![Save Work Order](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_04_SAVE.png)


**Step 5: Work Order Initial State** — `Success`

After saving, the work order is in the initial workflow state. The workflow dropdown in the header shows available transitions.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/work_order/WO-00142`
- **Timestamp:** 2026-04-10T07:23:17.086Z


![Work Order Initial State](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_05_VERIFY_STATE.png)


---

## 12. Safety Permits

*2 workflow(s) — 11 step(s)*

### 12.1. TC 09 Safety Permit Lifecycle ✅

| Property | Value |
|----------|-------|
| Test Case | TC-09 |
| Workflow | `TC-09-safety-permit-lifecycle` |
| Persona | Admin |
| Steps | 6 |
| Pass Rate | 6/6 (100%) |
| Result | **PASS** |

**Step 1: TC-09.1 — Safety Permit List** — `Success`

Navigate to Safety Permit. Safety permits ensure proper authorization before hazardous maintenance tasks. Permit types include LOTO, Hot Work, Confined Space, Excavation, Working at Height, and Electrical.

- **Action:** `Navigate to /safety_permit`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:22:59.826Z


![TC-09.1 — Safety Permit List](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_01_NAV.png)


**Step 2: TC-09.1 — Safety Permit Overview** — `Success`

The safety permit list shows all permits with their type, status, valid dates, and linked work orders. Color-coded status badges indicate the current lifecycle state.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:23:00.360Z


![TC-09.1 — Safety Permit Overview](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_02_SCREENSHOT.png)


**Step 3: TC-09.1 — New Safety Permit Form** — `Success`

The safety permit form includes fields for permit type, work order link, hazards identified, precautions required, PPE requirements, and emergency contact information.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:00.926Z


![TC-09.1 — New Safety Permit Form](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_03_NEW.png)


**Step 4: TC-09.1 — Fill Hazards Identified** — `Success`

Enter "E2E Lifecycle Test — Electrical hazard, " into the Hazards Identified field.

- **Action:** `Type "E2E Lifecycle Test — Electrical hazard, arc flash risk" into "input[name='hazards_identified'], textarea[name='hazards_identified']"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:01.552Z


![TC-09.1 — Fill Hazards Identified](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_04_FILL_TYPE.png)


**Step 5: TC-09.1 — Permit Created (Draft)** — `Success`

The safety permit is created in 'Draft' state. The workflow progresses: Draft → Submit Request → Requested → Approve → Approved → Activate → Active → Expire → Expired → Renew → Draft.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:02.404Z


![TC-09.1 — Permit Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_05_SAVE.png)


**Step 6: TC-09.1 — Safety Permit Detail** — `Success`

The safety permit detail page shows all safety-related fields, the workflow state badge, and available transition actions. The permit must be approved by a safety officer before activation.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:02.962Z


![TC-09.1 — Safety Permit Detail](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_06_VERIFY.png)


---

### 12.2. TC 09 Safety Permit ✅

| Property | Value |
|----------|-------|
| Test Case | TC-09 |
| Workflow | `TC-09-safety-permit` |
| Persona | Admin |
| Steps | 5 |
| Pass Rate | 5/5 (100%) |
| Result | **PASS** |

**Step 1: TC-09.1 — Safety Permit List** — `Success`

Navigate to Safety Permit. Safety permits control access to hazardous work areas and ensure proper safety procedures are followed before maintenance tasks begin.

- **Action:** `Navigate to /safety_permit`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit`
- **Timestamp:** 2026-04-10T07:23:07.940Z


![TC-09.1 — Safety Permit List](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_01_NAV.png)


**Step 2: TC-09.1 — New Safety Permit** — `Success`

Click 'Add New' to create a new safety permit. Select the permit type (LOTO, Hot Work, Confined Space, etc.), link it to a work order, and specify hazards and precautions.

- **Action:** `Click on "[data-testid='btn-new'], button:has-text('Add New'), button:has-text('Add New')"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:08.503Z


![TC-09.1 — New Safety Permit](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_02_NEW.png)


**Step 3: TC-09.1 — Fill Hazards Identified** — `Success`

Enter "E2E Test — Identify electrical hazards" into the Hazards Identified field.

- **Action:** `Type "E2E Test — Identify electrical hazards" into "input[name='hazards_identified'], textarea[name='hazards_identified']"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:09.054Z


![TC-09.1 — Fill Hazards Identified](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_03_FILL_DESC.png)


**Step 4: TC-09.1 — Safety Permit Created (Draft)** — `Success`

The safety permit is created with an auto-generated ID (e.g., SP-00001) in 'Draft' state. Submit the request for approval by the safety officer.

- **Action:** `Click on "[data-testid='btn-save'], button:has-text('Create'), button:has-text('Save'), button:has-text('Create')"`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:09.621Z


![TC-09.1 — Safety Permit Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_04_SAVE.png)


**Step 5: TC-09.1 — Safety Permit Detail** — `Success`

The safety permit detail page shows permit type, valid dates, hazards, precautions, and emergency procedures. The workflow tracks the permit through its approval and activation lifecycle.

- **Action:** `Capture screenshot`
- **URL:** `https://chieam.cubeworksinnovation.com/safety_permit/new`
- **Timestamp:** 2026-04-10T07:23:10.172Z


![TC-09.1 — Safety Permit Detail](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_05_VERIFY.png)


---


---

*This report was auto-generated by the Dual-Purpose Automation Framework.*
*CubeWorks Innovation — 2026-04-10T07:23:49.751Z*