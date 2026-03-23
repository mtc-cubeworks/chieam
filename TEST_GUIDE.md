# EAM-CHI System Test Guide

**Enterprise Asset Management — CHI**
**Version 1.1 | June 2025**

---

## Table of Contents

1. [Test Overview](#1-test-overview)
2. [Prerequisites & Setup](#2-prerequisites--setup)
3. [TC-01: Authentication & User Management](#tc-01-authentication--user-management)
4. [TC-02: Role-Based Access Control (RBAC)](#tc-02-role-based-access-control-rbac)
5. [TC-03: Core EAM Master Data](#tc-03-core-eam-master-data)
6. [TC-04: Asset Management](#tc-04-asset-management)
7. [TC-05: Asset Workflow — Full Lifecycle](#tc-05-asset-workflow--full-lifecycle)
8. [TC-06: Maintenance Request Workflow](#tc-06-maintenance-request-workflow)
9. [TC-07: Work Order Workflow](#tc-07-work-order-workflow)
10. [TC-08: Work Order Activity Workflow](#tc-08-work-order-activity-workflow)
11. [TC-09: Safety Permit Workflow](#tc-09-safety-permit-workflow)
12. [TC-10: Condition Monitoring Workflow](#tc-10-condition-monitoring-workflow)
13. [TC-11: Purchasing Workflow (PR → PO → Receipt)](#tc-11-purchasing-workflow-pr--po--receipt)
14. [TC-12: PM Calendar](#tc-12-pm-calendar)
15. [TC-13: Scheduled Jobs & Auto-Generation](#tc-13-scheduled-jobs--auto-generation)
16. [TC-14: Server Actions](#tc-14-server-actions)
17. [TC-15: SLA Tracking & Escalation](#tc-15-sla-tracking--escalation)
18. [TC-16: Import & Export](#tc-16-import--export)
19. [TC-17: Notifications](#tc-17-notifications)
20. [TC-18: Cross-Workflow Integration](#tc-18-cross-workflow-integration)
21. [TC-19: Vendor Performance Auto-Calculation](#tc-19-vendor-performance-auto-calculation)
22. [TC-20: End-to-End Scenario Tests](#tc-20-end-to-end-scenario-tests)
23. [TC-21: Row-Level Data Scoping](#tc-21-row-level-data-scoping)
24. [TC-22: RBAC Bypass & Security](#tc-22-rbac-bypass--security)
25. [TC-23: Workflow Concurrency & Dead-End States](#tc-23-workflow-concurrency--dead-end-states)
26. [TC-24: Hierarchy Circular References](#tc-24-hierarchy-circular-references)
27. [TC-25: Naming Series & ID Generation](#tc-25-naming-series--id-generation)
28. [TC-26: Server Action Robustness](#tc-26-server-action-robustness)
29. [TC-27: Data Integrity & Boundary Values](#tc-27-data-integrity--boundary-values)
30. [TC-28: Backward Transitions & Field Resets](#tc-28-backward-transitions--field-resets)
31. [Defect Log Template](#defect-log-template)
32. [Sign-Off Sheet](#sign-off-sheet)

---

## 1. Test Overview

### 1.1 Purpose

This guide provides step-by-step test cases to validate all workflows, business logic, CRUD operations, and integrations in the EAM-CHI system. Execute each test case in order — later tests depend on data created in earlier ones.

### 1.2 Test Approach

| Category | Coverage |
|----------|----------|
| Functional | CRUD, workflows, business rules, validations |
| Integration | Cross-module data flow (MR → WO → Parts → PO) |
| Security | RBAC, field permissions, role-restricted transitions |
| Automation | Scheduled jobs, auto-calculations, notifications |
| UI | Forms, list views, calendar, navigation |

### 1.3 Result Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Pass |
| ❌ | Fail |
| ⚠️ | Pass with issues (note in Comments) |
| ⏭️ | Skipped (document reason) |
| 🔄 | Blocked (document blocker) |

---

## 2. Prerequisites & Setup

### 2.1 Environment

| Item | Value |
|------|-------|
| Application URL | *(fill in)* |
| Database | PostgreSQL |
| Test Date | *(fill in)* |
| Tested By | *(fill in)* |

### 2.2 Test Accounts

Create these accounts before starting (or verify they exist):

| Username | Role | Data Scope | Purpose |
|----------|------|------------|---------|
| `admin` | SystemManager | all | Full admin access |
| `exec1` | Executive | all | Executive-level read access |
| `sitemgr1` | SiteManager | site | Site-level management testing |
| `supervisor1` | Supervisor | team | Department/team-level testing |
| `tech1` | Technician | own | Technician — own records only |
| `viewer1` | Viewer | site | Read-only access testing |
| `assetmgr1` | AssetManager | site | Asset module testing |
| `purchmgr1` | PurchaseManager | site | Procurement management testing |
| `buyer1` | Buyer | site | PO creation/approval testing |
| `reqnr1` | Requisitioner | own | PR creation — own records only |
| `storemgr1` | StoresManager | site | Stores/inventory management |
| `storekeeper1` | Storekeeper | site | Stores operations testing |

### 2.3 Prerequisite Data

These records must exist (create in TC-03 if not present):

- [ ] At least 1 Organization
- [ ] At least 2 Sites
- [ ] At least 2 Departments (one per site)
- [ ] At least 3 Employees
- [ ] At least 2 Labor records
- [ ] At least 1 Trade
- [ ] At least 1 Manufacturer and Model
- [ ] At least 1 Asset Class
- [ ] At least 5 Items (inventory items)
- [ ] At least 2 Vendors
- [ ] At least 1 Store
- [ ] At least 1 Work Schedule

---

## TC-01: Authentication & User Management

### TC-01.1 — Login with Valid Credentials

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to the login page | Login form displays with Username and Password fields | | |
| 2 | Enter valid `admin` credentials | | | |
| 3 | Click **Login** | Redirected to Dashboard; sidebar shows entities per role permissions | | |
| 4 | Verify user avatar in top-right | Shows user name/initials | | |

### TC-01.2 — Login with Invalid Credentials

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Enter invalid username/password | | | |
| 2 | Click **Login** | Error message displayed; NOT redirected to Dashboard | | |
| 3 | Verify no session created | Refreshing page returns to login | | |

### TC-01.3 — Token Refresh

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login and remain idle past access token expiry | | | |
| 2 | Perform any action (navigate, save) | System auto-refreshes token; action succeeds without re-login | | |

### TC-01.4 — User CRUD (as admin)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to **Admin → Users** | User list displays | | |
| 2 | Click **+ New**, fill in username, email, full name, password | | | |
| 3 | Save | New user created with auto-generated ID | | |
| 4 | Edit the user — change email | Save succeeds; email updated | | |
| 5 | Assign a Role to the user | Role appears in user's role list | | |
| 6 | Remove the Role | Role removed; user access adjusts | | |
| 7 | Deactivate the user (is_active = false) | User can no longer login | | |

### TC-01.5 — Profile Update

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Click user avatar → **Profile** | Profile page opens | | |
| 2 | Update contact number | Save succeeds | | |
| 3 | Verify change persists after page refresh | Updated value displayed | | |

---

## TC-02: Role-Based Access Control (RBAC)

### TC-02.1 — Permission Matrix Configuration

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `admin` | | | |
| 2 | Navigate to **Admin → Permissions** | Permission matrix displays (Role × Entity grid) | | |
| 3 | Find the "Viewer" role row for "Work Order" | Only `can_read` is checked | | |
| 4 | Verify "Technician" role for "Work Order" | `can_read`, `can_create`, `can_update` checked; `can_delete` unchecked | | |

### TC-02.2 — Read-Only Access (Viewer Role)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `viewer1` (Viewer role) | | | |
| 2 | Navigate to any entity list | Records display correctly | | |
| 3 | Verify **+ New** button is NOT visible | No create button shown | | |
| 4 | Open a record detail | Form fields are read-only | | |
| 5 | Verify no **Delete** option | Delete is not available | | |

### TC-02.3 — Entity Sidebar Visibility

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `admin` | All entities visible in sidebar | | |
| 2 | Remove `in_sidebar` for "Holiday" for the Viewer role | | | |
| 3 | Login as `viewer1` | "Holiday" does NOT appear in sidebar | | |
| 4 | Re-enable `in_sidebar` | "Holiday" reappears for Viewer | | |

### TC-02.4 — Workflow Transition Role Restriction

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | As `admin`, configure a WO transition "Approve" with `allowed_roles: ["SystemManager"]` | | | |
| 2 | Login as `tech1` (Technician role, scope=own) | | | |
| 3 | Open a Work Order in "Requested" state | "Approve" action is NOT available | | |
| 4 | Login as `admin` (SystemManager) | "Approve" action IS available | | |

---

## TC-03: Core EAM Master Data

### TC-03.1 — Organization, Site, Department Hierarchy

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create an **Organization** | Record saved with auto-generated ID | | |
| 2 | Create **Site A** linked to the Organization | Site shows Organization link | | |
| 3 | Create **Site B** linked to the Organization | Two sites now exist | | |
| 4 | Create **Department X** linked to Site A | Department shows Site link | | |
| 5 | Create **Department Y** linked to Site B | | | |
| 6 | Verify cascade: Organization → Sites → Departments | Hierarchy displays correctly | | |

### TC-03.2 — Employee & Labor Setup

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Employee** "John Smith" linked to user `tech1`, Site A, Dept X | EMP-##### generated | | |
| 2 | Create **Employee** "Jane Doe" linked to user `sitemgr1`, Site A, Dept X | | | |
| 3 | Create **Employee** "Bob Wilson" (no user link), Site B | | | |
| 4 | Create **Trade** "Electrician" | | | |
| 5 | Create **Trade** "Mechanic" | | | |
| 6 | Create **Labor** record for John Smith with Trade "Electrician" | LAB-##### generated | | |
| 7 | Create **Labor** record for Bob Wilson with Trade "Mechanic" | | | |

### TC-03.3 — Manufacturer & Model

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Manufacturer** "Siemens" | | | |
| 2 | Create **Manufacturer** "ABB" | | | |
| 3 | Create **Model** "SIMOTICS GP 1LE0" linked to Siemens | | | |
| 4 | Create **Model** "ACS580" linked to ABB | | | |

### TC-03.4 — Work Schedule & Holiday

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Work Schedule** "Standard 5-Day" | | | |
| 2 | Add **Work Schedule Details**: Mon–Fri, 07:00–16:00 | 5 child records created | | |
| 3 | Create **Holiday** "National Day" on a future date | | | |

### TC-03.5 — Financial Master Data

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Account** "Maintenance Operating" | | | |
| 2 | Create **Cost Code** "MAINT-001" | | | |
| 3 | Create **Annual Budget** for current year, Dept X, linked to Account | | | |

---

## TC-04: Asset Management

### TC-04.1 — Create Asset with Full Details

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to **Asset Management → Asset** | Asset list view | | |
| 2 | Click **+ New** | Form opens | | |
| 3 | Fill: Description="Test Motor 001", Asset Class=(select one), Site=Site A, Dept=Dept X | | | |
| 4 | Save | Asset created with auto-ID (A-#####); initial state = Acquired | | |
| 5 | Set **Lifecycle State** = Active | Saved | | |
| 6 | Set **Criticality** = A-Critical, **Risk Score** = 85 | Saved | | |
| 7 | Set **Manufacturer** = Siemens, **Model** = SIMOTICS GP 1LE0 | Saved | | |
| 8 | Fill **Nameplate**: Rated Capacity=100kW, Rated Power=134HP, Weight=350kg | Saved | | |
| 9 | Fill **Warranty**: Start=today, End=+2 years, Vendor=(select) | Saved | | |
| 10 | Fill **Depreciation**: Method=Straight-Line, Useful Life=15 years, Salvage Value=5000, Commissioning Date=today | Saved | | |
| 11 | Verify all fields persist after page refresh | All data correct | | |

### TC-04.2 — Asset Hierarchy

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a second asset: "Test Motor 002" | A-##### assigned | | |
| 2 | Set **Parent Asset** = "Test Motor 001" | | | |
| 3 | On "Test Motor 001", verify **Sub-Asset** child table shows "Test Motor 002" | | | |
| 4 | Navigate tree view (if available) | Hierarchy visible | | |

### TC-04.3 — Meter & Meter Reading

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On "Test Motor 001", go to **Meter** child table | | | |
| 2 | Create **Meter**: type=Operating Hours | Meter created | | |
| 3 | Create **Meter Reading**: value=1000, date=today | Reading saved | | |
| 4 | Create second reading: value=1050, date=today+1 | Delta should calculate as 50 | | |
| 5 | Verify readings appear in chronological order | Correct order | | |

### TC-04.4 — Asset Property

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On "Test Motor 001", go to **Asset Property** child table | | | |
| 2 | Add custom property (e.g., "IP Rating" = "IP55") | Property saved | | |
| 3 | Add another property (e.g., "Insulation Class" = "F") | | | |

### TC-04.5 — Equipment CRUD

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Equipment**: Type=Owned, group, custodian, site | EQP-#### generated | | |
| 2 | Verify **Inventory** field appears (Type=Owned) | Field visible | | |
| 3 | Change Type to Rented | **PR Line No** field appears; Inventory field hides | | |
| 4 | Change back to Owned | Fields toggle correctly | | |

---

## TC-05: Asset Workflow — Full Lifecycle

### TC-05.1 — Complete Asset Lifecycle

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create new Asset | State = **Acquired** | | |
| 2 | Click **Receive** | State → **Inspected** | | |
| 3 | Click **Install Asset** | State → **Active** | | |
| 4 | Click **Putaway** | State → **Under Maintenance** | | |
| 5 | Click **Complete** | State → **Active** | | |
| 6 | Click **Internal Repair** | State → **Under Repair** | | |
| 7 | Click **Complete** | State → **Active** | | |
| 8 | Click **Retire Asset** | State → **Inactive** | | |
| 9 | Click **Remove Asset** | State → **Decommissioned** | | |
| 10 | Verify no further transitions available (or only Dispose) | Terminal state or Dispose only | | |
| 11 | Check audit trail for all 9 transitions | All logged with user and timestamp | | |

### TC-05.2 — Send to Vendor Path

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create new Asset → Receive → Install Asset → **Active** | | | |
| 2 | Click **Send to Vendor** | State → **Under Repair** | | |
| 3 | Click **Complete** | State → **Active** | | |

---

## TC-06: Maintenance Request Workflow

### TC-06.1 — Standard Approval Flow

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` | | | |
| 2 | Create **Maintenance Request**: Requestor=John Smith, Asset="Test Motor 001", Priority=High, Category=Corrective, Description="Motor vibration excessive", Site=Site A, Dept=Dept X | MTREQ-##### generated; State = **Draft** | | |
| 3 | Click **Submit for Approval** | State → **Pending Approval** | | |
| 4 | Verify description, asset, requestor are **read-only** in this state | Fields non-editable | | |
| 5 | Login as `sitemgr1` | | | |
| 6 | Open the MR | "Approve" action available | | |
| 7 | Click **Approve** | State → **Approved** | | |
| 8 | Click **Submit for Resolution** | State → **Release** | | |
| 9 | Click **Complete** | State → **Completed** | | |
| 10 | Verify full audit trail | All transitions logged | | |

### TC-06.2 — Emergency Bypass

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create MR with Priority=Emergency | State = **Draft** | | |
| 2 | Click **Submit for Emergency** | State → **Approved** (skips Pending Approval) | | |
| 3 | Complete the MR through remaining states | Works correctly | | |

### TC-06.3 — Reopen Completed MR

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Completed MR | | | |
| 2 | Click **Reopen** | State → **Draft** | | |
| 3 | Re-submit and complete again | Full cycle works | | |

### TC-06.4 — SLA Fields

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create and submit an MR | | | |
| 2 | Check **SLA Response Due** and **SLA Resolution Due** fields | Auto-populated based on priority | | |
| 3 | Check **SLA Status** | Shows "On Track" initially | | |

---

## TC-07: Work Order Workflow

### TC-07.1 — Full Work Order Lifecycle

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Work Order**: Type=Corrective Maintenance, Description="Repair excessive vibration on Test Motor 001", Priority=High, Site=Site A, Dept=Dept X, Asset="Test Motor 001", Due Date=+3 days | WO-##### generated; State = **Requested** | | |
| 2 | Click **Approve** | State → **Approved** | | |
| 3 | Click **Start** | State → **In Progress** | | |
| 4 | Fill: Actual Start=now, LOTO Required=Yes | | | |
| 5 | Click **Complete** | State → **Closed** | | |
| 6 | Fill: Actual End=now, Technician Findings, Work Performed, Recommendations | Saved | | |
| 7 | Verify audit trail | 4 state entries logged | | |

### TC-07.2 — Work Order Reopen

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open the Closed WO from TC-07.1 | | | |
| 2 | Click **Reopen** | State → **Requested** | | |
| 3 | Complete again | Full cycle works | | |

### TC-07.3 — Work Order Child Records

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Work Order | | | |
| 2 | Add **WO Labor**: Labor=John Smith, Hours=4, Rate=50 | Total = 200 auto-calculated | | |
| 3 | Add **WO Equipment**: Equipment=(select), Hours=2 | Saved | | |
| 4 | Add **WO Parts**: Item=(select), Quantity=3, Unit Price=25 | Total = 75 auto-calculated | | |
| 5 | Verify **Total Labor Cost** on WO header | Matches sum of labor line totals | | |
| 6 | Verify **Total Parts Cost** on WO header | Matches sum of parts line totals | | |
| 7 | Verify **Total Cost** on WO header | Sum of labor + equipment + parts | | |

### TC-07.4 — Work Order Downtime Tracking

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On a Work Order, set **Downtime Start** = yesterday 08:00 | | | |
| 2 | Set **Downtime End** = yesterday 14:00 | | | |
| 3 | Verify **Downtime Hours** = 6 | Auto-calculated | | |

### TC-07.5 — Work Order Failure Reporting

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On a WO, fill **Cause Code** = "Bearing Failure" | Saved | | |
| 2 | Fill **Remedy Code** = "Bearing Replacement" | Saved | | |
| 3 | Fill **Failure Notes** | Saved | | |

### TC-07.6 — Follow-Up Work Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On a completed WO, set **Follow-up Work Order** = new WO | Link established | | |
| 2 | Open the follow-up WO | **Parent Work Order** references the original | | |

---

## TC-08: Work Order Activity Workflow

### TC-08.1 — Full Activity Lifecycle

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On a Work Order, create **WO Activity**: Description="Replace bearings", Work Item Type=Asset, Work Item="Test Motor 001", Activity Type=(select) | WOACT-##### generated; State = **Awaiting Resources** | | |
| 2 | Click **Allocate** | State → **Ready** | | |
| 3 | Click **Start Activity** | State → **In Progress** | | |
| 4 | Click **Put On Hold** | State → **On Hold** | | |
| 5 | Click **Resume** | State → **In Progress** | | |
| 6 | Click **Complete** | State → **Completed** | | |
| 7 | Click **Close** | State → **Closed** | | |

### TC-08.2 — Reopen Activity

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Completed activity | | | |
| 2 | Click **Reopen** | State → **Ready** | | |

### TC-08.3 — Generate Templated PMA

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Completed WO Activity | | | |
| 2 | Click action **Generate Templated PMA** | A Planned Maintenance Activity is created from the activity details | | |
| 3 | Navigate to the created PMA | Verify fields are populated from the activity | | |

---

## TC-09: Safety Permit Workflow

### TC-09.1 — Full Permit Lifecycle

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Safety Permit**: Permit Type=LOTO, Work Order=(select), Asset="Test Motor 001", Requested By=John Smith, Valid From=today, Valid To=today+7, Hazards="Electrical shock, rotating equipment", Precautions="De-energize, lock and tag all sources", Emergency Procedures="Call site emergency team" | SP-##### generated; State = **Draft** | | |
| 2 | Click **Submit Request** | State → **Requested** | | |
| 3 | Click **Approve** (as manager) | State → **Approved**; Approved By populated | | |
| 4 | Click **Activate** | State → **Active** | | |
| 5 | Click **Expire** | State → **Expired** | | |
| 6 | Click **Renew** | State → **Draft** (new permit cycle) | | |

### TC-09.2 — Permit Cancellation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create and submit a Safety Permit | State = **Requested** | | |
| 2 | Click **Cancel** | State → **Cancelled** | | |
| 3 | Verify no further transitions available | Terminal state | | |

### TC-09.3 — All Permit Types

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create permit: Type = **Hot Work** | Saved | | |
| 2 | Create permit: Type = **Confined Space** | Saved | | |
| 3 | Create permit: Type = **Excavation** | Saved | | |
| 4 | Create permit: Type = **Working at Height** | Saved | | |
| 5 | Create permit: Type = **Electrical** | Saved | | |

---

## TC-10: Condition Monitoring Workflow

### TC-10.1 — Full Monitoring Lifecycle

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Condition Monitoring**: Asset="Test Motor 001", Monitoring Type=Vibration, Baseline Value=2.5, Warning Threshold=5.0, Critical Threshold=10.0, Reading Value=2.8, Alert Status=Normal, Trend Direction=Stable, Site=Site A | CM-##### generated; State = **Active** | | |
| 2 | Update Reading Value=6.0, Alert Status=Warning | | | |
| 3 | Click **Warn** | State → **Warning** | | |
| 4 | Update Reading Value=12.0, Alert Status=Critical | | | |
| 5 | Click **Escalate** | State → **Critical** | | |
| 6 | Update Reading Value=2.5, Alert Status=Normal | | | |
| 7 | Click **Resolve** | State → **Resolved** | | |

### TC-10.2 — All Monitoring Types

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create CM: Type = **Temperature** | Saved | | |
| 2 | Create CM: Type = **Pressure** | Saved | | |
| 3 | Create CM: Type = **Oil Analysis** | Saved | | |
| 4 | Create CM: Type = **Ultrasonic** | Saved | | |
| 5 | Create CM: Type = **Thermography** | Saved | | |
| 6 | Create CM: Type = **Current/Voltage** | Saved | | |

---

## TC-11: Purchasing Workflow (PR → PO → Receipt)

### TC-11.1 — Purchase Request

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Purchase Request**: Requestor=John Smith, Due Date=+14 days, Site=Site A, Dept=Dept X | PR-##### generated; State = **Draft** | | |
| 2 | Add **PR Lines**: Item="Bearing SKF 6206", Qty=2, Unit Price=45.00 | Line saved; Line Total = 90.00 | | |
| 3 | Add second line: Item="Seal Kit", Qty=1, Unit Price=120.00 | | | |
| 4 | Submit / Approve the PR | State → **Open** | | |

### TC-11.2 — Purchase Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Purchase Order**: Vendor=(select), PO Type=Standard, Site=Site A, Dept=Dept X | PO-##### generated; State = **Draft** | | |
| 2 | Add **PO Lines** matching the PR items | Lines saved with totals | | |
| 3 | Verify form is **editable** in Draft state | All fields editable | | |
| 4 | Click **Approve** | State → **Open** | | |
| 5 | Verify form is **read-only** in Open state | Fields non-editable | | |

### TC-11.3 — Blanket Purchase Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PO: Type = **Blanket**, Blanket Limit = 10000 | | | |
| 2 | Verify **Blanket Limit** field is visible | Visible | | |
| 3 | Verify **Released Amount** field exists (read-only) | Shows 0 initially | | |

### TC-11.4 — Contract Purchase Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PO: Type = **Contract** | | | |
| 2 | Verify **Contract Start** and **Contract End** fields appear | Both visible | | |
| 3 | Fill contract dates and save | Saved | | |

### TC-11.5 — PO Amendment

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | On an existing PO, create an amendment | **Original PO** links back | | |
| 2 | Set **Amendment Number** and **Amendment Reason** | Saved | | |

### TC-11.6 — Purchase Receipt

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Purchase Receipt**: PO=(select the Open PO), Received Date=today, Received Qty=2 | Saved | | |
| 2 | Verify vendor performance recalculation triggered | Vendor delivery/quality ratings updated | | |
| 3 | Complete the PO (all items received) | State → **Closed** | | |

### TC-11.7 — PO Rejection & Cancellation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a PO in Draft | | | |
| 2 | Click **Reject** | State → **Rejected** | | |
| 3 | Create another PO in Draft | | | |
| 4 | Click **Cancel** | State → **Cancelled** | | |

---

## TC-12: PM Calendar

### TC-12.1 — Calendar View

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to the **Calendar** page | Monthly calendar view displays | | |
| 2 | Select current year and month | Tasks for the month appear | | |
| 3 | Verify color coding | Draft=slate, Pending Approval=amber, Approved=blue, Release=violet, Completed=green | | |

### TC-12.2 — Seed Data

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Click **Seed** (or POST /pm-calendar/seed) | 32 activities, 6 team members, 31 holidays, and a full month of tasks created | | |
| 2 | Verify calendar shows populated tasks | Tasks visible on various days | | |
| 3 | Click any task to see details | Full detail view opens | | |

### TC-12.3 — Create PM Task

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Click on a future day or click **+ New Task** | Task creation form opens | | |
| 2 | Fill: Activity="Test PM Task", Due Date=selected day, Start Time=09:00, Assigned To=BENROD, Site=Site A, Notes="Test PM" | | | |
| 3 | Save | Task appears on the calendar | | |
| 4 | Verify system auto-created: Maintenance Activity, PMA, Work Order (Preventive Maintenance), WO Activity, Maintenance Request | All entities created and linked | | |

### TC-12.4 — Reschedule Task (Drag and Drop)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Drag the task from its current day to a different day | | | |
| 2 | Verify the due date updated | New date saved | | |
| 3 | Verify the start time is preserved | Same time, new date | | |
| 4 | Click the task to confirm details | All data correct | | |

### TC-12.5 — Update Task Status

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Click a task | Detail panel opens | | |
| 2 | Change workflow state from Draft to Pending Approval | Color changes to amber | | |
| 3 | Approve the task | Color changes to blue | | |
| 4 | Release the task | Color changes to violet | | |
| 5 | Complete the task | Color changes to green | | |

### TC-12.6 — Filter by Site/Department

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Select a specific Site filter | Only tasks for that site shown | | |
| 2 | Select a specific Department filter | Only tasks for that department shown | | |
| 3 | Clear filters | All tasks shown | | |

---

## TC-13: Scheduled Jobs & Auto-Generation

### TC-13.1 — PM Auto-Generation Job

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Ensure at least one `maintenance_calendar` entry exists with frequency set | | | |
| 2 | Set the last maintenance_request's date to be old enough that next_due ≤ today+7 | | | |
| 3 | Trigger the job manually or wait for 1:00 AM execution | | | |
| 4 | Check for newly created: Maintenance Request (state=Draft) and Work Order (state=Requested, type=Preventive Maintenance) | Records created | | |
| 5 | Verify **Scheduled Job Log** | Log entry shows job_id, status=success, records_created count | | |

### TC-13.2 — Job Logging

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to **Scheduled Job Log** entity | | | |
| 2 | Verify latest entries | Shows job_id, job_name, status, started_at, completed_at, duration_seconds, records_created/updated | | |
| 3 | If a job failed, check error_message and error_traceback | Error details populated | | |

---

## TC-14: Server Actions

### TC-14.1 — Clone Asset (AR-8)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open "Test Motor 001" | | | |
| 2 | Click action **Clone Asset** | A new asset record is created | | |
| 3 | Open the cloned asset | All fields copied from original (except unique identifiers) | | |
| 4 | Verify the clone has a new Asset Tag (A-#####) | Different from original | | |

### TC-14.2 — Calculate RPN (Failure Analysis)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create **Failure Analysis**: Asset="Test Motor 001", Failure Code="Bearing", Failure Mode="Wear", Severity Score=8, Occurrence Score=5, Detection Score=3 | | | |
| 2 | Click action **Calculate RPN** | RPN = 8 × 5 × 3 = 120; Risk Level auto-set | | |
| 3 | Verify RPN value = 120 | Correct | | |

### TC-14.3 — Generate 5-Why Template

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Failure Analysis record | | | |
| 2 | Click action **Generate 5-Why Template** | Structured template generated | | |
| 3 | Verify template has 5 "Why" levels | Template is complete | | |

### TC-14.4 — Generate Fishbone Template

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Failure Analysis record | | | |
| 2 | Click action **Generate Fishbone Template** | Ishikawa diagram template generated | | |
| 3 | Verify categories: Man, Machine, Material, Method, Measurement, Environment | All present | | |

### TC-14.5 — Generate Maintenance Order from MR

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open an Approved Maintenance Request | | | |
| 2 | Click action **Generate Maintenance Order** | MTORD-##### created | | |
| 3 | Open the generated Maintenance Order | Linked to the MR; work order reference set | | |

### TC-14.6 — Create Purchase Request from MR

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a Maintenance Request | | | |
| 2 | Click action **Create Purchase Request** | PR-##### created | | |
| 3 | Open the generated PR | Linked to MR; requestor and site populated | | |

---

## TC-15: SLA Tracking & Escalation

### TC-15.1 — SLA Timer on Maintenance Request

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create MR with Priority=High | | | |
| 2 | Submit for Approval | State = Pending Approval, SLA clock starts | | |
| 3 | Check **SLA Status** field | "On Track" (within 4h threshold) | | |
| 4 | Wait or simulate >4 hours in Pending Approval | | | |
| 5 | Verify **SLA Status** changes to "At Risk" or "Breached" | Status updated | | |
| 6 | Verify **Is Overdue** = Yes | Auto-flagged | | |

### TC-15.2 — SLA Timer on Work Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create WO and leave in Requested state | SLA = 8h | | |
| 2 | Approve WO and leave in Approved state | SLA = 24h | | |
| 3 | Start WO and leave in In Progress state | SLA = 72h | | |
| 4 | Verify SLA status at each stage | Consistent with thresholds | | |

---

## TC-16: Import & Export

### TC-16.1 — Export to Excel

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to **Asset** list view | | | |
| 2 | Apply a filter (e.g., Site=Site A) | Filtered list shows | | |
| 3 | Click **Export** | Excel file downloads | | |
| 4 | Open the file | Contains all filtered records with correct column headers | | |

### TC-16.2 — Download Import Template

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to **Asset** list view | | | |
| 2 | Click **Import** | Import dialog opens | | |
| 3 | Click **Download Template** | Excel template downloads | | |
| 4 | Open the template | Contains correct column headers, no data rows | | |

### TC-16.3 — Import with Validation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Fill the template with 3 valid asset records | | | |
| 2 | Upload the file | | | |
| 3 | Click **Validate** | Validation results show 3 valid records | | |
| 4 | Click **Execute** | 3 assets created with auto-assigned IDs | | |
| 5 | Verify records in list view | All 3 present with correct data | | |

### TC-16.4 — Import with Errors

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Fill template with 1 valid + 1 invalid record (missing required field) | | | |
| 2 | Upload and **Validate** | Shows 1 valid, 1 error with error details | | |
| 3 | Verify error message is clear and identifies the issue | Missing field identified | | |

---

## TC-17: Notifications

### TC-17.1 — Maintenance Request Notifications

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create MR and Submit for Approval | | | |
| 2 | Check if approvers receive notification | Notification sent (Socket.IO or email) | | |
| 3 | Approve the MR | | | |
| 4 | Check if requestor receives approval notification | Notification sent | | |

### TC-17.2 — Work Order Notifications

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Start a Work Order (transition to In Progress) | | | |
| 2 | Check if assigned labor receives notification | Notification sent | | |

### TC-17.3 — Real-Time Socket.IO

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open the same entity in two browser tabs/sessions | | | |
| 2 | Update a record in Tab 1 | | | |
| 3 | Verify Tab 2 receives a real-time update or notification | Update reflected | | |

---

## TC-18: Cross-Workflow Integration

### TC-18.1 — Maintenance Request → Work Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create and approve a Maintenance Request | | | |
| 2 | Use server action **Generate Maintenance Order** | Maintenance Order created | | |
| 3 | Verify the MO has a linked Work Order | WO reference populated | | |
| 4 | Open the Work Order | WO exists in Requested state, type=Corrective Maintenance | | |

### TC-18.2 — Maintenance Request → Purchase Request

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open an Approved Maintenance Request | | | |
| 2 | Use server action **Create Purchase Request** | PR created | | |
| 3 | Verify PR has correct requestor, site, department | Populated from MR | | |

### TC-18.3 — Work Order → Safety Permit

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a Work Order with LOTO Required = Yes | | | |
| 2 | Create a Safety Permit linked to this WO | Permit Type = LOTO | | |
| 3 | Verify WO → Safety Permit child link | Permit appears in WO children | | |

### TC-18.4 — PM Calendar → Full Chain

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a PM task via the calendar | | | |
| 2 | Verify: Maintenance Activity created | Exists | | |
| 3 | Verify: Planned Maintenance Activity created | Exists, links to activity | | |
| 4 | Verify: Work Order created (type=Preventive Maintenance) | Exists | | |
| 5 | Verify: Work Order Activity created | Exists, links to WO | | |
| 6 | Verify: Maintenance Request created | Exists, links to PMA and WO Activity | | |
| 7 | All entities are cross-linked | All links valid | | |

### TC-18.5 — Purchase Receipt → Vendor Performance

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Note vendor's current ratings (delivery, quality, overall) | Record baseline | | |
| 2 | Create a Purchase Receipt for that vendor's PO | | | |
| 3 | Open the Vendor record | Ratings recalculated | | |
| 4 | Verify total_orders incremented | Count increased by 1 | | |

---

## TC-19: Vendor Performance Auto-Calculation

### TC-19.1 — Delivery Rating Calculation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a Vendor with no orders | All ratings = 0 or default | | |
| 2 | Create PO for vendor, with delivery_date = today+7 | | | |
| 3 | Approve the PO | State = Open | | |
| 4 | Create Receipt with receipt_date = today+7 (on time) | | | |
| 5 | Check vendor: on_time_deliveries increased | Correct | | |
| 6 | Create another PO with delivery_date = today+3 | | | |
| 7 | Create Receipt with receipt_date = today+10 (late) | | | |
| 8 | Verify delivery_rating reflects both on-time and late | Rating adjusted downward | | |

---

## TC-20: End-to-End Scenario Tests

### TC-20.1 — Corrective Maintenance Scenario

> **Scenario:** A technician discovers excessive vibration on a motor. This triggers a maintenance request, work order, parts procurement, and failure analysis.

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` | | | |
| 2 | Create **Condition Monitoring** for "Test Motor 001": Type=Vibration, Reading=12.5mm/s (above Critical threshold) | CM-##### created; State=Active | | |
| 3 | Transition CM to **Critical** | State → Critical | | |
| 4 | Create **Maintenance Request**: Asset="Test Motor 001", Category=Corrective, Priority=High, Description="Excessive vibration detected by condition monitoring" | MTREQ-##### created | | |
| 5 | Submit for Approval → Approve (as manager) → Release | MR in Release state | | |
| 6 | Use action **Generate Maintenance Order** | MTORD-##### created with linked WO | | |
| 7 | Open the generated **Work Order** | WO in Requested state | | |
| 8 | Approve → Start the WO | WO in In Progress | | |
| 9 | Create **Safety Permit** (LOTO) linked to WO | SP-##### created | | |
| 10 | Process Safety Permit: Submit → Approve → Activate | SP Active | | |
| 11 | Add **WO Activity**: "Replace motor bearings" | WOACT-##### created | | |
| 12 | Add **WO Labor**: John Smith, 6 hours, rate=50/hr | Total=300 | | |
| 13 | Add **WO Parts**: "Bearing SKF 6206" × 2 @ $45 each | Total=90 | | |
| 14 | Verify WO **Total Cost** = $390 | Correct | | |
| 15 | Complete the WO Activity and WO | Both Completed/Closed | | |
| 16 | Fill technician findings, work performed, recommendations | Saved | | |
| 17 | Create **Failure Analysis**: Severity=8, Occurrence=5, Detection=3 | | | |
| 18 | Calculate RPN | RPN=120 | | |
| 19 | Complete the MR | MR in Completed state | | |
| 20 | Resolve the CM | CM in Resolved state | | |
| 21 | Expire the Safety Permit | SP Expired | | |
| 22 | Verify full audit trail across all entities | All transitions logged | | |

### TC-20.2 — Preventive Maintenance Scenario

> **Scenario:** Monthly PM schedule generates a task via the PM Calendar, which is executed and completed.

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Navigate to PM Calendar | | | |
| 2 | Create a PM task: Activity="Monthly Pump Inspection", Due Date=tomorrow, Assigned To=BENROD | Task created with full chain (Activity→PMA→WO→WO Activity→MR) | | |
| 3 | Verify WO type = Preventive Maintenance | Correct | | |
| 4 | Verify MR links to PMA | Link populated | | |
| 5 | Approve MR via standard workflow | MR → Approved → Release | | |
| 6 | Approve and Start the WO | WO → In Progress | | |
| 7 | Allocate and Start the WO Activity | Activity → In Progress | | |
| 8 | Add WO Labor (2 hours) | Saved | | |
| 9 | Complete WO Activity → Complete WO → Complete MR | All completed | | |
| 10 | On PM Calendar, verify task shows as **green** (Completed) | Color correct | | |

### TC-20.3 — Procurement Scenario

> **Scenario:** A maintenance request requires parts that are out of stock, triggering procurement.

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create MR with note about needed parts | MTREQ-##### | | |
| 2 | Approve MR | | | |
| 3 | Use action **Create Purchase Request** | PR-##### created | | |
| 4 | Add PR lines for needed items | Lines saved | | |
| 5 | Approve the PR | State = Open | | |
| 6 | Create **Purchase Order** for a vendor | PO-##### | | |
| 7 | Add PO lines matching PR items | | | |
| 8 | Approve the PO | State = Open | | |
| 9 | Create **Purchase Receipt** | Items received | | |
| 10 | Note vendor ratings recalculated | Performance updated | | |
| 11 | Complete the PO | State = Closed | | |
| 12 | Go back to WO, add the received parts to WO Parts | WO cost updated | | |

### TC-20.4 — Asset Decommission Scenario

> **Scenario:** An aging asset is taken through the full decommission path.

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open an Active asset | | | |
| 2 | Set Lifecycle State = Decommissioned | | | |
| 3 | Transition via workflow: Active → Retire Asset → **Inactive** | | | |
| 4 | Transition: Inactive → Remove Asset → **Decommissioned** | | | |
| 5 | Verify no further create actions possible on asset | Asset locked | | |
| 6 | Verify asset hierarchy: sub-assets flagged | Children updated or warned | | |

### TC-20.5 — Multi-User Concurrent Workflow

> **Scenario:** Two users interact with the same maintenance request simultaneously.

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | `tech1` creates MR and submits for approval | State = Pending Approval | | |
| 2 | Both `sitemgr1` and `admin` open the same MR | Both see the record | | |
| 3 | `sitemgr1` clicks Approve | State → Approved | | |
| 4 | `admin` (still on old view) clicks Approve | Should fail gracefully (already transitioned) or show updated state | | |
| 5 | Verify Socket.IO notification arrived | Real-time update | | |

---

## TC-21: Row-Level Data Scoping

> Tests for the row-level data scoping system based on Role `data_scope` (own/team/site/all), `created_by`/`modified_by` auto-injection, and scope filter enforcement across all routes.

### TC-21.1 — "own" Scope Visibility

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` (Technician, scope=own) | | | |
| 2 | Create a Maintenance Request (MR-A) | MR created; `created_by` = tech1's user ID | | |
| 3 | Navigate to Maintenance Request list | Only MR-A visible (plus any other records created by tech1) | | |
| 4 | Login as `admin` (SystemManager, scope=all) | | | |
| 5 | Create a Maintenance Request (MR-B) | MR-B created; `created_by` = admin's user ID | | |
| 6 | Login as `tech1` again | | | |
| 7 | Verify MR list does NOT show MR-B | MR-B invisible to tech1 | | |
| 8 | Attempt to access MR-B via direct URL/API | 404 or permission denied | | |

### TC-21.2 — "site" Scope Visibility

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `sitemgr1` (SiteManager, scope=site, assigned to Site-A) | | | |
| 2 | Create a Work Order at Site-A | WO created | | |
| 3 | Login as `admin`, create a Work Order at Site-B | WO created at Site-B | | |
| 4 | Login as `sitemgr1` again | | | |
| 5 | Verify WO list shows Site-A WO but NOT Site-B WO | Correct scope filtering | | |
| 6 | Attempt direct API access to Site-B WO | 404 or permission denied | | |

### TC-21.3 — "team" Scope Visibility (Department-Based)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `supervisor1` (Supervisor, scope=team, assigned to Dept-X) | | | |
| 2 | Create a Maintenance Request in Dept-X | MR created with dept=Dept-X | | |
| 3 | Login as `admin`, create MR in Dept-Y (different department) | MR created | | |
| 4 | Login as `supervisor1` | | | |
| 5 | Verify list shows Dept-X MR but NOT Dept-Y MR | Team scope filters by department | | |

### TC-21.4 — "all" Scope Visibility

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `admin` (SystemManager, scope=all) | | | |
| 2 | Navigate to any entity list | All records across all sites/depts visible | | |
| 3 | Verify no scope filter applied | Full dataset returned | | |

### TC-21.5 — created_by / modified_by Auto-Injection

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` | | | |
| 2 | Create any entity record (e.g., Maintenance Request) | `created_by` = tech1 user ID in DB | | |
| 3 | Login as `admin` | | | |
| 4 | Edit that same record (change description) | `modified_by` = admin user ID; `created_by` unchanged = tech1 | | |
| 5 | Verify `created_by` is immutable on update | `created_by` still tech1's ID | | |

### TC-21.6 — Legacy Records with NULL created_by

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via DB, set `created_by = NULL` on a test record | Record has no ownership | | |
| 2 | Login as `tech1` (scope=own) | | | |
| 3 | Verify the NULL-created_by record is NOT visible in list | SQL `NULL != user_id` → invisible | | |
| 4 | Login as `admin` (scope=all) | | | |
| 5 | Verify the record IS visible | All-scope users see everything | | |

### TC-21.7 — User with No Employee Linkage

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create user `noemployee1` with SiteManager role but no linked Employee | | | |
| 2 | Login as `noemployee1` | | | |
| 3 | Navigate to entity list (scope=site with empty site_ids) | Degrades to own-scope behavior; sees only self-created records | | |

### TC-21.8 — Scope on Update and Delete

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` (scope=own), create record R1 | | | |
| 2 | Login as `reqnr1` (scope=own, different user) | | | |
| 3 | Attempt to UPDATE R1 via API | Fails — record out of scope | | |
| 4 | Attempt to DELETE R1 via API | Fails — record out of scope | | |
| 5 | Login as `admin` (scope=all), update R1 | Succeeds | | |

---

## TC-22: RBAC Bypass & Security

> Tests for known RBAC bypass paths where scope filters are NOT applied.

### TC-22.1 — Export Bypasses Row-Level Scope

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `admin`, create records at Site-A and Site-B | | | |
| 2 | Login as `sitemgr1` (scope=site, Site-A only) | | | |
| 3 | Export the entity to Excel | **KNOWN GAP**: Exported file may contain ALL records, not just Site-A | | |
| 4 | Document whether export respects scope or exposes all data | Note actual behavior | | |

### TC-22.2 — Import Bypasses created_by Injection

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` | | | |
| 2 | Import records via Excel template | Records created in DB | | |
| 3 | Check DB: verify `created_by` on imported records | **KNOWN GAP**: May be NULL (import bypasses entity_crud.py) | | |
| 4 | Verify imported records are visible to the importer in list view | May be invisible if created_by is NULL and user is own-scope | | |

### TC-22.3 — Import Update Mode Bypasses Scope

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` (scope=own) | | | |
| 2 | Prepare import Excel with IDs of records NOT created by tech1 | | | |
| 3 | Import in update mode | **KNOWN GAP**: May update records outside user's scope | | |

### TC-22.4 — Server Action Endpoint Bypasses Scope

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` (scope=own) | | | |
| 2 | Execute a server action on a record NOT created by tech1 (using direct API call) | **KNOWN GAP**: Action may execute on any record (no scope filter on action endpoint) | | |

### TC-22.5 — Child Record Endpoint Scope

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `tech1` (scope=own) | | | |
| 2 | Access child records of a parent entity not owned by tech1 (via API) | **KNOWN GAP**: Child records may be returned without scope filter | | |

### TC-22.6 — Role data_scope Invalid Value

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via API or DB, set a Role's `data_scope` = `"galaxy"` (invalid value) | | | |
| 2 | Login as user with that role | | | |
| 3 | Navigate to entity list | Should degrade to "own" scope (safe default) — verify behavior | | |

### TC-22.7 — NULL data_scope on Role

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via DB, set a Role's `data_scope = NULL` | | | |
| 2 | Login as user with that role | | | |
| 3 | Navigate to entity list | **KNOWN GAP**: NULL coerces to `"all"` — unrestricted access | | |

---

## TC-23: Workflow Concurrency & Dead-End States

> Tests for race conditions in concurrent workflow transitions and states with no outgoing paths.

### TC-23.1 — Concurrent Approval Race Condition

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a Maintenance Request, submit for approval | State = Pending Approval | | |
| 2 | Open the MR in two separate browser sessions (User A and User B) | Both see Pending Approval | | |
| 3 | User A clicks "Approve" | MR → Approved; WO + WOA generated | | |
| 4 | User B (still seeing Pending Approval) clicks "Approve" | Should fail gracefully — no duplicate WO created | | |
| 5 | Verify only ONE Work Order was generated | Single WO exists | | |

### TC-23.2 — Concurrent Naming Series Race

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open two browser sessions as `admin` | | | |
| 2 | Simultaneously create two records of the same entity type | Both save successfully | | |
| 3 | Verify both records have UNIQUE IDs | No duplicate IDs (e.g., AST-0005 and AST-0006, not two AST-0005) | | |

### TC-23.3 — Asset Dead-End State: Inactive

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Transition an asset: Active → Retire Asset → **Inactive** | Asset now Inactive | | |
| 2 | Attempt to transition to any other state | **KNOWN GAP**: No outgoing transitions from Inactive. Asset is permanently stuck. | | |
| 3 | Verify no transition to Decommissioned is available | Missing transition: Inactive → Decommissioned | | |

### TC-23.4 — Condition Monitoring: No De-Escalation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Condition Monitoring (Active state) | | | |
| 2 | Escalate: Active → Warning → Critical | State = Critical | | |
| 3 | Attempt to de-escalate: Critical → Warning or Critical → Active | **KNOWN GAP**: No backward transitions. Cannot reflect improving conditions. | | |
| 4 | Attempt to go Active → Resolved directly | **KNOWN GAP**: Must escalate to Warning or Critical first to reach Resolved | | |

### TC-23.5 — Safety Permit: Cannot Cancel Active Permit

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create a Safety Permit, progress: Draft → Requested → Approved → Active | Permit is Active | | |
| 2 | Attempt to Cancel the Active permit | **KNOWN GAP**: No Active → Cancelled transition. Must wait for expiry. | | |

### TC-23.6 — Purchase Order: Rejected is Terminal

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PO, submit for approval | State = Open / Pending | | |
| 2 | Reject the PO | State = Rejected | | |
| 3 | Attempt to revise or resubmit | **KNOWN GAP**: No Rejected → Draft transition. PO is permanently stuck. | | |

### TC-23.7 — RFQ: No Cancel from Review

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create RFQ, submit for sourcing, progress to Review state | State = Review | | |
| 2 | All quotes are unacceptable — attempt to Cancel | **KNOWN GAP**: No Review → Cancelled transition | | |

### TC-23.8 — Work Order: Orphaned Activities on Cancel

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create WO with 3 WO Activities, start one activity | 1 WOA in In Progress | | |
| 2 | Cancel the parent Work Order | WO → Cancelled | | |
| 3 | Check status of WO Activities | **KNOWN GAP**: WOAs remain in their current state (In Progress), not cascade-cancelled | | |

### TC-23.9 — Inventory Adjustment: Double-Posting Risk

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Inventory Adjustment, Submit, Post | State = Posted, inventory quantities updated | | |
| 2 | Attempt to "Submit" the Posted adjustment | **KNOWN GAP**: Posted → Submitted is allowed — may enable double-posting | | |

### TC-23.10 — PR Line Rejection is Permanent

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PR with 3 lines, submit and reject Line 2 | Line 2 = Rejected | | |
| 2 | Revise the PR (Rejected → Draft) | PR returns to Draft | | |
| 3 | Verify Line 2 status | **KNOWN GAP**: Line stays Rejected permanently — no Rejected → Draft transition for lines | | |

---

## TC-24: Hierarchy Circular References

> Tests for self-referential FK fields that lack cycle detection.

### TC-24.1 — Asset Self-Parent

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Asset AST-001 | | | |
| 2 | Edit AST-001 and set `parent_asset` = AST-001 (self) | Should reject — circular reference. Document actual behavior. | | |
| 3 | If accepted, navigate to asset hierarchy view | May infinite-loop or show corrupted tree | | |

### TC-24.2 — Asset Circular Chain (A→B→A)

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Assets AST-A and AST-B | | | |
| 2 | Set AST-A.parent_asset = AST-B | | | |
| 3 | Set AST-B.parent_asset = AST-A | Should reject — circular chain. Document actual behavior. | | |

### TC-24.3 — Location Self-Parent

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Location LOC-001 | | | |
| 2 | Set LOC-001.parent_location = LOC-001 | Should reject. Document behavior. | | |

### TC-24.4 — Employee Reports-To Self

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Employee EMP-001 | | | |
| 2 | Set EMP-001.reports_to = EMP-001 | Should reject — employee cannot report to self. Document actual behavior. | | |

### TC-24.5 — Employee Circular Reporting Chain

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create EMP-A and EMP-B | | | |
| 2 | Set EMP-A.reports_to = EMP-B | | | |
| 3 | Set EMP-B.reports_to = EMP-A | Should reject — mutual reporting cycle. Document actual behavior. | | |

### TC-24.6 — Asset Class / Item Class / System Hierarchy Cycles

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create two Asset Classes: AC-A and AC-B | | | |
| 2 | Set AC-A.parent_asset_class = AC-B, then AC-B.parent_asset_class = AC-A | Should reject. Document behavior. | | |
| 3 | Repeat with Item Class and System hierarchies | Same test for all self-referential hierarchies | | |

---

## TC-25: Naming Series & ID Generation

> Tests for NamingService edge cases including series exhaustion, race conditions, and padding.

### TC-25.1 — Normal ID Generation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Check series table for entity prefix (e.g., `AST`) | Note current value | | |
| 2 | Create a new record | ID generated with correct prefix and zero-padded number | | |
| 3 | Verify series.current incremented by 1 | Correct | | |

### TC-25.2 — Series Overflow Past Digit Limit

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via DB, set series.current = 9998 for a test entity prefix | | | |
| 2 | Create record #9999 | ID = PREFIX-9999 | | |
| 3 | Create record #10000 | ID = PREFIX-10000 (5 digits — breaks 4-digit padding pattern) | | |
| 4 | Verify no error and sorting still works correctly | Document behavior | | |

### TC-25.3 — Negative Series Value

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via DB, set series.current = -1 for a test entity | | | |
| 2 | Create a new record | ID may be PREFIX--000 or PREFIX-0000. Document behavior. | | |

### TC-25.4 — Rapid Concurrent Creation

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Use API tool (curl/Postman) to send 10 create requests in rapid succession | All 10 records created | | |
| 2 | Verify all 10 records have unique IDs | No duplicates | | |
| 3 | Verify series.current = original + 10 | Correctly incremented | | |

---

## TC-26: Server Action Robustness

> Tests for server action edge cases including broken imports, idempotency, and missing ctx.doc.

### TC-26.1 — Generate Maintenance Order Idempotency

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create and approve a Maintenance Request | State = Approved | | |
| 2 | Execute "Generate Maintenance Order" action | MO + WO created | | |
| 3 | Execute "Generate Maintenance Order" again on same MR | Should prevent duplicate MO, or raise error. Document behavior. | | |

### TC-26.2 — Create Purchase Request from MR

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create and approve a Maintenance Request | | | |
| 2 | Execute "Create Purchase Request" action | PR created | | |
| 3 | Verify PR has correct requestor, site, department from MR | Fields populated | | |
| 4 | Verify PR has line items (or note if empty) | **KNOWN GAP**: PR may be created with zero line items | | |

### TC-26.3 — Clone Asset Action

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Open a fully-populated asset (with properties, positions) | | | |
| 2 | Execute "Clone Asset" action | New asset created with copied data | | |
| 3 | Verify cloned asset has own `created_by` and new ID | Not NULL, not same as original | | |
| 4 | Verify cloned asset is in initial workflow state | Not inherited from source | | |
| 5 | If action fails, document the error message | Note if "Server action not found" | | |

### TC-26.4 — Calculate RPN Action

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Failure Analysis with severity=8, occurrence=5, detection=3 | | | |
| 2 | Execute "Calculate RPN" | RPN = 8 × 5 × 3 = 120 | | |
| 3 | Try with non-numeric values or values > 10 | Should clamp or reject. Document behavior. | | |
| 4 | If action fails, document the error message | Note any AttributeError or import error | | |

### TC-26.5 — Server Action on Non-Existent Record

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via API, call a server action with a fake record ID | Should return 404 or meaningful error | | |
| 2 | Verify no partial data created | Clean rollback | | |

### TC-26.6 — Server Action Permission Check

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Login as `viewer1` (read-only) | | | |
| 2 | Attempt to execute any server action via API | Should be denied | | |

---

## TC-27: Data Integrity & Boundary Values

> Tests for field constraints, invalid data, and boundary conditions on critical model fields.

### TC-27.1 — Negative Financial Values

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Work Order Labor with `rate = -50` | Should reject or accept? Document behavior. | | |
| 2 | Create WO Parts with `quantity_required = -5` | Document behavior | | |
| 3 | Create Purchase Order Line with `price = 0` | Document behavior | | |
| 4 | Verify WO total_cost calculation with negative values | Verify mathematical correctness | | |

### TC-27.2 — Zero Division in Currency Conversion

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create or edit a Currency with `conversion_factor = 0` | | | |
| 2 | Create a PR Line referencing that currency | Should handle gracefully (no division by zero crash) | | |

### TC-27.3 — Float Precision for Financial Totals

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create WO Labor: rate=0.10, hours=3.00 | Expected total = 0.30 | | |
| 2 | Add another WO Labor: rate=0.20, hours=1.00 | Added = 0.20, Running = 0.50 | | |
| 3 | Verify WO total_labor_cost | Should be exactly 0.50 (check for 0.50000000001 type drift) | | |

### TC-27.4 — Meter Reading Backwards

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Meter for an asset, set last_reading = 5000 | | | |
| 2 | Create Meter Reading with reading_value = 3000 (lower than last) | Should warn or reject? Document behavior. | | |
| 3 | Verify meter.last_reading after save | Is it updated to 3000 or stayed at 5000? | | |

### TC-27.5 — Overlapping Date Ranges

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Work Schedule with `end_date` < `start_date` | Should reject. Document behavior. | | |
| 2 | Create Asset with `warranty_end` < `warranty_start` | Document behavior. | | |
| 3 | Create Safety Permit with `valid_to` < `valid_from` | Document behavior. | | |

### TC-27.6 — Over-Receipt of Purchase Order

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PO with line: quantity_ordered = 10 | | | |
| 2 | Create Receipt with quantity_received = 15 (more than ordered) | Should prevent or allow? Document behavior. | | |
| 3 | Check PO Line: quantity_received > quantity_ordered | Note if over-receipt is accepted | | |

### TC-27.7 — WO Parts Over-Issuance

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Add WO Parts with quantity_required = 5 | | | |
| 2 | Set quantity_issued = 10 | Should prevent or allow? Document behavior. | | |
| 3 | Set quantity_returned = 15 (more than issued) | Document behavior | | |

### TC-27.8 — Null/Empty Required Fields on Workflow Transitions

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create an Asset with NO site, NO department, NO class | Empty entity with just ID | | |
| 2 | Attempt to transition through workflow (Acquired → Inspected → Active) | Should it require site/dept before activation? Document behavior. | | |

### TC-27.9 — EmployeeSite Multiple Defaults

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create EmployeeSite for Employee A → Site-1 with `default = True` | | | |
| 2 | Create EmployeeSite for Employee A → Site-2 with `default = True` | **KNOWN GAP**: No unique constraint — both can be default | | |

### TC-27.10 — Free-Text Status Fields

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Via API, create a Safety Permit with `permit_type = "InvalidType"` | Should reject or accept? Document behavior. | | |
| 2 | Create an Asset with `criticality = "ZZZZZ"` | Document behavior | | |
| 3 | Create a WorkOrder with `priority = "Super Ultra Urgent"` | Document behavior | | |

---

## TC-28: Backward Transitions & Field Resets

> Tests that reopened/reverted records properly reset dependent fields and child states.

### TC-28.1 — Work Order Reopen Field Reset

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create WO, approve, start, complete, close | WO Closed with downtime_end, downtime_hours, actual_end_date set | | |
| 2 | Reopen the WO (Closed → In Progress) | State = In Progress | | |
| 3 | Verify `downtime_end` is cleared | **KNOWN GAP**: May retain stale value | | |
| 4 | Verify `downtime_hours` is cleared/reset | **KNOWN GAP**: May retain stale value | | |
| 5 | Verify `actual_end_date` is cleared | **KNOWN GAP**: May retain stale value | | |
| 6 | Verify child WO Activities remain in their current state | Check if WOAs are also reopened or stay closed | | |

### TC-28.2 — Maintenance Request Reopen Cascade

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Complete a Maintenance Request (full cycle) | MR Completed, `closed_date` set | | |
| 2 | Reopen the MR | MR → Release | | |
| 3 | Verify `closed_date` is cleared on MR | Should be NULL | | |
| 4 | Verify linked WOA `end_date` is cleared | **KNOWN GAP**: WOA end_date may retain stale value | | |
| 5 | Verify linked WO state is reset to In Progress | Check cascade | | |

### TC-28.3 — WO Activity Reopen and Asset State

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Complete WO Activity (asset transitions to Active on completion) | WOA Completed, Asset Active | | |
| 2 | Reopen WOA (Completed → In Progress) | WOA back In Progress | | |
| 3 | Verify Asset state | **KNOWN GAP**: Asset may stay Active when it should return to Under Maintenance | | |

### TC-28.4 — Purchase Request Revision with Rejected Lines

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create PR with 3 lines | | | |
| 2 | Submit, get Lines 1+3 approved, Line 2 rejected | Mixed line states | | |
| 3 | Revise the PR (Rejected → Draft) | PR back to Draft | | |
| 4 | Verify Line 2 state | **KNOWN GAP**: Line stays Rejected permanently; cannot be edited or re-approved | | |

### TC-28.5 — Safety Permit Renew Data Reset

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Safety Permit, progress through full cycle to Expired | Permit Expired, dates set | | |
| 2 | Renew (Expired → Draft) | Permit back to Draft | | |
| 3 | Verify `valid_from` and `valid_to` are cleared | **KNOWN GAP**: Dates may retain old expired values | | |
| 4 | Verify audit trail shows it was a renewal vs. original | Note if any indication exists | | |

### TC-28.6 — Service Contract Renew Overwrites History

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create Service Contract with terms, pricing, dates | Full contract | | |
| 2 | Progress to Expired | Contract Expired | | |
| 3 | Renew (Expired → Draft) | Contract back to Draft, same record | | |
| 4 | Verify original terms, dates, and pricing are preserved | **KNOWN GAP**: Previous values may be overwritten with no history | | |

### TC-28.7 — Parent-Child State Sync on Cancel

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create WO with 3 WO Activities, start 2 of them | 2 WOAs In Progress, 1 in Ready | | |
| 2 | Cancel the parent WO | WO → Cancelled | | |
| 3 | Check all 3 WOA states | **KNOWN GAP**: WOAs not cascade-cancelled — remain in their pre-cancel states | | |
| 4 | Cancel a PO with mixed-state lines | Check if partially-received lines block cancellation | | |

### TC-28.8 — Asset Decommission with Open Work

| Step | Action | Expected Result | Result | Comments |
|------|--------|----------------|--------|----------|
| 1 | Create an asset with open MRs, WOs, and active meters | Active asset with linked records | | |
| 2 | Decommission the asset | Asset → Decommissioned | | |
| 3 | Verify open MRs for this asset | **KNOWN GAP**: MRs remain active for a decommissioned asset | | |
| 4 | Verify open WOs for this asset | **KNOWN GAP**: WOs remain active | | |
| 5 | Verify meter readings can still be entered | Document behavior | | |

---

## Defect Log Template

Use this table to log any issues found during testing.

| Defect # | Test Case | Step | Severity | Description | Actual Result | Expected Result | Status | Assigned To | Resolution |
|----------|-----------|------|----------|-------------|---------------|-----------------|--------|-------------|------------|
| D-001 | | | | | | | Open | | |
| D-002 | | | | | | | Open | | |
| D-003 | | | | | | | Open | | |
| D-004 | | | | | | | Open | | |
| D-005 | | | | | | | Open | | |
| D-006 | | | | | | | Open | | |
| D-007 | | | | | | | Open | | |
| D-008 | | | | | | | Open | | |
| D-009 | | | | | | | Open | | |
| D-010 | | | | | | | Open | | |

**Severity Levels:**
- **Critical** — System unusable, data loss, security breach
- **High** — Major feature broken, no workaround
- **Medium** — Feature broken but workaround exists
- **Low** — Cosmetic issue, minor inconvenience

---

## Sign-Off Sheet

| Module | Test Cases | Pass | Fail | Blocked | Tested By | Date | Sign-Off |
|--------|-----------|------|------|---------|-----------|------|----------|
| Authentication (TC-01) | 5 | | | | | | |
| RBAC (TC-02) | 4 | | | | | | |
| Core Master Data (TC-03) | 5 | | | | | | |
| Asset Management (TC-04) | 5 | | | | | | |
| Asset Workflow (TC-05) | 2 | | | | | | |
| MR Workflow (TC-06) | 4 | | | | | | |
| WO Workflow (TC-07) | 6 | | | | | | |
| WO Activity Workflow (TC-08) | 3 | | | | | | |
| Safety Permit Workflow (TC-09) | 3 | | | | | | |
| Condition Monitoring (TC-10) | 2 | | | | | | |
| Purchasing (TC-11) | 7 | | | | | | |
| PM Calendar (TC-12) | 6 | | | | | | |
| Scheduled Jobs (TC-13) | 2 | | | | | | |
| Server Actions (TC-14) | 6 | | | | | | |
| SLA Tracking (TC-15) | 2 | | | | | | |
| Import/Export (TC-16) | 4 | | | | | | |
| Notifications (TC-17) | 3 | | | | | | |
| Cross-Workflow (TC-18) | 5 | | | | | | |
| Vendor Performance (TC-19) | 1 | | | | | | |
| E2E Scenarios (TC-20) | 5 | | | | | | |
| Row-Level Data Scoping (TC-21) | 8 | | | | | | |
| RBAC Bypass & Security (TC-22) | 7 | | | | | | |
| Workflow Concurrency & Dead-Ends (TC-23) | 10 | | | | | | |
| Hierarchy Circular Refs (TC-24) | 6 | | | | | | |
| Naming Series & ID Gen (TC-25) | 4 | | | | | | |
| Server Action Robustness (TC-26) | 6 | | | | | | |
| Data Integrity & Boundaries (TC-27) | 10 | | | | | | |
| Backward Transitions & Resets (TC-28) | 8 | | | | | | |
| **TOTAL** | **144** | | | | | | |

### Final Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA Lead | | | |
| Project Manager | | | |
| Product Owner | | | |
| Dev Lead | | | |

---

*End of Test Guide — EAM-CHI v1.0*
