# EAM-CHI System Test Guide

**Enterprise Asset Management — CHI**
**Version 1.0 | March 2026**

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
23. [Defect Log Template](#defect-log-template)
24. [Sign-Off Sheet](#sign-off-sheet)

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

| Username | Role | Purpose |
|----------|------|---------|
| `admin` | SystemManager | Full admin access |
| `manager1` | Editor + approvals | Manager workflow testing |
| `tech1` | Editor (limited) | Technician workflow testing |
| `viewer1` | Viewer | Read-only access testing |
| `store1` | Editor (purchasing module) | Procurement testing |

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
| 4 | Verify "Editor" role for "Work Order" | `can_read`, `can_create`, `can_update` checked; `can_delete` unchecked | | |

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
| 2 | Login as `tech1` (Editor role, not SystemManager) | | | |
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
| 2 | Create **Employee** "Jane Doe" linked to user `manager1`, Site A, Dept X | | | |
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
| 5 | Login as `manager1` | | | |
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
| 2 | Both `manager1` and `admin` open the same MR | Both see the record | | |
| 3 | `manager1` clicks Approve | State → Approved | | |
| 4 | `admin` (still on old view) clicks Approve | Should fail gracefully (already transitioned) or show updated state | | |
| 5 | Verify Socket.IO notification arrived | Real-time update | | |

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
| **TOTAL** | **80** | | | | | | |

### Final Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA Lead | | | |
| Project Manager | | | |
| Product Owner | | | |
| Dev Lead | | | |

---

*End of Test Guide — EAM-CHI v1.0*
