# EAM System — User Manual

> Auto-generated from 319 screenshots across 50 workflows.
> Generated at: 2026-04-10T07:23:17.139Z

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
5. [Dashboard](#dashboard)
   5.1. [Dashboard Overview](#dashboard-overview)
6. [General Features](#general-features)
   6.1. [Entity List Features](#entity-list-features)
7. [Navigation](#navigation)
   7.1. [Sidebar Navigation](#sidebar-navigation)
8. [Maintenance](#maintenance)
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
10. [Purchasing & Stores](#purchasing-&-stores)
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
13. [Troubleshooting](#troubleshooting)

---

## 1. General

### 1.1. TC 02 Rbac Permissions

Navigate to the Admin panel to access role and permission configuration.

**Step 1: TC-02.1 — Admin Panel**

Navigate to the Admin panel to access role and permission configuration.


![TC-02.1 — Admin Panel](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_01_NAV_ADMIN.png)

**Step 2: TC-02.1 — Admin Overview**

The Admin panel provides access to user management, role configuration, and permission matrix settings.


![TC-02.1 — Admin Overview](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_02_SCREENSHOT_ADMIN.png)

**Step 3: TC-02.1 — Role List**

Navigate to the Role entity. Roles define what actions users can perform on each entity type.


![TC-02.1 — Role List](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_03_NAV_ROLE.png)

**Step 4: TC-02.1 — Role Configuration**

The role list shows all configured roles (Admin, Manager, Technician, Viewer, etc.) with their associated permissions and data scopes.


![TC-02.1 — Role Configuration](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_04_SCREENSHOT_ROLES.png)

**Step 5: TC-02.1 — Permission Matrix**

Navigate to the Permission entity. The permission matrix defines Create, Read, Update, Delete (CRUD) access per role per entity.


![TC-02.1 — Permission Matrix](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_05_NAV_PERMISSION.png)

**Step 6: TC-02.1 — Permission Matrix Detail**

The permission matrix shows each role-entity combination with granular CRUD controls. Admins can toggle individual permissions to restrict or grant access.


![TC-02.1 — Permission Matrix Detail](test-artifacts/screenshots/TC-02-rbac-permissions__TC02_06_SCREENSHOT_PERM.png)

---

### 1.2. TC 02 Workflow Management

Navigate to Workflow. This page shows all configured workflow definitions with their states, transitions, and role-based restrictions.

**Step 1: TC-02.4 — Workflow Management**

Navigate to Workflow. This page shows all configured workflow definitions with their states, transitions, and role-based restrictions.


![TC-02.4 — Workflow Management](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_01_NAV.png)

**Step 2: TC-02.4 — Workflow Definitions**

The workflow management page lists all entity workflows. Each workflow defines states, allowed transitions, and which roles can trigger each transition.


![TC-02.4 — Workflow Definitions](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_02_SCREENSHOT.png)

**Step 3: TC-02 — Reports Dashboard**

Navigate to Reports. The reporting dashboard shows operational metrics, KPIs, and analytics across all EAM modules.


![TC-02 — Reports Dashboard](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_03_NAV_REPORTS.png)

**Step 4: TC-02 — Reports Overview**

The reports page provides analytics and operational insights including asset health, maintenance backlog, work order completion rates, and vendor performance summaries.


![TC-02 — Reports Overview](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_04_SCREENSHOT_REPORTS.png)

**Step 5: TC-02 — Model Editor**

Navigate to Model Editor. This admin tool allows configuring entity models, fields, and relationships.


![TC-02 — Model Editor](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_05_NAV_MODEL.png)

**Step 6: TC-02 — Model Editor Interface**

The Model Editor provides a visual interface for configuring entity models, field types, validation rules, and cross-entity relationships.


![TC-02 — Model Editor Interface](test-artifacts/screenshots/TC-02-workflow-management__TC02_WF_06_SCREENSHOT_MODEL.png)

---

### 1.3. TC 12 Pm Calendar

Navigate to the PM Calendar page. The calendar provides a visual overview of all scheduled preventive maintenance activities organized by date.

**Step 1: TC-12.1 — PM Calendar**

Navigate to the PM Calendar page. The calendar provides a visual overview of all scheduled preventive maintenance activities organized by date.


![TC-12.1 — PM Calendar](test-artifacts/screenshots/TC-12-pm-calendar__TC12_01_NAV.png)

**Step 2: TC-12.1 — Calendar Month View**

The PM Calendar displays scheduled maintenance tasks in a monthly view. Tasks are color-coded by status: Draft (slate), Pending (amber), Approved (blue), Release (violet), Completed (green).


![TC-12.1 — Calendar Month View](test-artifacts/screenshots/TC-12-pm-calendar__TC12_02_SCREENSHOT.png)

**Step 3: TC-12.3 — Maintenance Activity List**

Navigate to Maintenance Activity. Activities are created from the PM Calendar and represent scheduled preventive maintenance tasks.


![TC-12.3 — Maintenance Activity List](test-artifacts/screenshots/TC-12-pm-calendar__TC12_03_NAV_MA.png)

**Step 4: TC-12.3 — Maintenance Activities**

The maintenance activity list shows all scheduled activities with their status, due date, assigned resource, and linked work orders.


![TC-12.3 — Maintenance Activities](test-artifacts/screenshots/TC-12-pm-calendar__TC12_04_SCREENSHOT_MA.png)

**Step 5: TC-12.3 — PM Activity List**

Navigate to PM Activity. PM Activities define reusable preventive maintenance templates with task sequences, checklists, and resource requirements.


![TC-12.3 — PM Activity List](test-artifacts/screenshots/TC-12-pm-calendar__TC12_05_NAV_PMA.png)

**Step 6: TC-12.3 — PM Activity Templates**

PM Activity templates define standard maintenance procedures that are instantiated when scheduled maintenance is triggered.


![TC-12.3 — PM Activity Templates](test-artifacts/screenshots/TC-12-pm-calendar__TC12_06_SCREENSHOT_PMA.png)

---

### 1.4. TC 13 Scheduled Jobs

Navigate to Maintenance Calendar. This defines the PM schedules that trigger automatic generation of maintenance requests and work orders.

**Step 1: TC-13.1 — Maintenance Calendar Configuration**

Navigate to Maintenance Calendar. This defines the PM schedules that trigger automatic generation of maintenance requests and work orders.


![TC-13.1 — Maintenance Calendar Configuration](test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_01_NAV_MC.png)

**Step 2: TC-13.1 — PM Schedule Configuration**

The maintenance calendar list shows all configured PM schedules with their frequency, last run date, next due date, and linked assets.


![TC-13.1 — PM Schedule Configuration](test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_02_SCREENSHOT_MC.png)

**Step 3: TC-13.2 — Scheduled Job Log**

Navigate to Scheduled Job Log. The log records all automated job executions including PM auto-generation runs.


![TC-13.2 — Scheduled Job Log](test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_03_NAV_SJL.png)

**Step 4: TC-13.2 — Job Log Entries**

The scheduled job log shows each execution with job ID, status (Success/Failed), duration, records created/updated, and error details. Jobs run at 1:00 AM daily or can be triggered manually.


![TC-13.2 — Job Log Entries](test-artifacts/screenshots/TC-13-scheduled-jobs__TC13_04_SCREENSHOT_SJL.png)

---

### 1.5. TC 14 Server Actions

Navigate to Asset. The 'Clone Asset' server action creates a copy of an existing asset with a new ID and reset fields.

**Step 1: TC-14.1 — Asset List (Clone Action)**

Navigate to Asset. The 'Clone Asset' server action creates a copy of an existing asset with a new ID and reset fields.


![TC-14.1 — Asset List (Clone Action)](test-artifacts/screenshots/TC-14-server-actions__TC14_01_NAV_ASSET.png)

**Step 2: TC-14.1 — Assets for Cloning**

Select an asset from the list to access server actions. The 'Clone Asset' action is available from the asset detail page's action menu.


![TC-14.1 — Assets for Cloning](test-artifacts/screenshots/TC-14-server-actions__TC14_02_SCREENSHOT_ASSET.png)

**Step 3: TC-14.2 — Failure Analysis List (RPN Calculation)**

Navigate to Failure Analysis. Server actions include 'Calculate RPN' (Risk Priority Number = Severity × Occurrence × Detection), 'Generate 5-Why Template', and 'Generate Fishbone Template'.


![TC-14.2 — Failure Analysis List (RPN Calculation)](test-artifacts/screenshots/TC-14-server-actions__TC14_03_NAV_FA.png)

**Step 4: TC-14.2 — Failure Analysis Overview**

The failure analysis list shows all failure records with their severity, occurrence, detection ratings, and calculated RPN scores.


![TC-14.2 — Failure Analysis Overview](test-artifacts/screenshots/TC-14-server-actions__TC14_04_SCREENSHOT_FA.png)

**Step 5: TC-14.5 — Maintenance Request (Generate MO)**

Navigate to Maintenance Request. The 'Generate Maintenance Order' server action creates a maintenance order with linked work order from an approved MR.


![TC-14.5 — Maintenance Request (Generate MO)](test-artifacts/screenshots/TC-14-server-actions__TC14_05_NAV_MR.png)

**Step 6: TC-14.5 — MR Server Actions**

Approved maintenance requests support server actions: 'Generate Maintenance Order' (creates MO + WO) and 'Create Purchase Request' (creates PR for required parts).


![TC-14.5 — MR Server Actions](test-artifacts/screenshots/TC-14-server-actions__TC14_06_SCREENSHOT_MR.png)

**Step 7: TC-14.5 — Maintenance Order List**

Navigate to Maintenance Order. Maintenance orders are generated from approved maintenance requests and link to work orders for execution.


![TC-14.5 — Maintenance Order List](test-artifacts/screenshots/TC-14-server-actions__TC14_07_NAV_MO.png)

**Step 8: TC-14.5 — Maintenance Order Overview**

The maintenance order list shows all generated orders with their source MR, linked WO, status, and assigned resources.


![TC-14.5 — Maintenance Order Overview](test-artifacts/screenshots/TC-14-server-actions__TC14_08_SCREENSHOT_MO.png)

---

### 1.6. TC 16 Import Export

Navigate to the Asset list. The Export function allows downloading entity data as Excel files with applied filters.

**Step 1: TC-16.1 — Asset List (Export)**

Navigate to the Asset list. The Export function allows downloading entity data as Excel files with applied filters.


![TC-16.1 — Asset List (Export)](test-artifacts/screenshots/TC-16-import-export__TC16_01_NAV_ASSET.png)

**Step 2: TC-16.1 — Export Feature**

The entity list toolbar includes an Export button. Apply filters (e.g., Site, Status) before exporting to get a filtered dataset. The export downloads as an Excel (.xlsx) file.


![TC-16.1 — Export Feature](test-artifacts/screenshots/TC-16-import-export__TC16_02_SCREENSHOT.png)

**Step 3: TC-16.2 — Import/Export Page**

Navigate to the Import/Export page. This page provides bulk data import with template download, validation, and execution.


![TC-16.2 — Import/Export Page](test-artifacts/screenshots/TC-16-import-export__TC16_03_NAV_IMPORT.png)

**Step 4: TC-16.2 — Import Template Download**

The import page allows selecting an entity type and downloading a template with correct headers. Upload a filled template to validate and import records in bulk.


![TC-16.2 — Import Template Download](test-artifacts/screenshots/TC-16-import-export__TC16_04_SCREENSHOT_IMPORT.png)

**Step 5: TC-16 — System Settings**

Navigate to Settings to configure import/export options, data validation rules, and default field mappings.


![TC-16 — System Settings](test-artifacts/screenshots/TC-16-import-export__TC16_05_NAV_SETTINGS.png)

**Step 6: TC-16 — Settings Overview**

The Settings page provides system configuration including import/export preferences, naming series, and workflow configuration.


![TC-16 — Settings Overview](test-artifacts/screenshots/TC-16-import-export__TC16_06_SCREENSHOT_SETTINGS.png)

---

### 1.7. TC 18 Cross Workflow Integration

Navigate to Maintenance Request. MRs serve as the starting point for cross-workflow integration chains: MR → Work Order, MR → Purchase Request.

**Step 1: TC-18.1 — Maintenance Request (Integration Source)**

Navigate to Maintenance Request. MRs serve as the starting point for cross-workflow integration chains: MR → Work Order, MR → Purchase Request.


![TC-18.1 — Maintenance Request (Integration Source)](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_01_NAV_MR.png)

**Step 2: TC-18.1 — MR Integration Overview**

Approved maintenance requests can trigger: 'Generate Maintenance Order' (creates MO + WO) and 'Create Purchase Request' (creates PR for parts). These server actions link entities across modules.


![TC-18.1 — MR Integration Overview](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_02_SCREENSHOT_MR.png)

**Step 3: TC-18.3 — Work Order (Integration Hub)**

Navigate to Work Order. Work orders link to safety permits, labor, parts, equipment, and activities. WOs with LOTO Required = Yes should have linked safety permits.


![TC-18.3 — Work Order (Integration Hub)](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_03_NAV_WO.png)

**Step 4: TC-18.3 — Work Order Integration Points**

Work orders serve as the central hub for cross-module integration. Child records include labor, parts, equipment, activities, and safety permits.


![TC-18.3 — Work Order Integration Points](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_04_SCREENSHOT_WO.png)

**Step 5: TC-18.3 — Safety Permits (WO Integration)**

Safety permits are linked to work orders requiring hazardous work authorization. The WO → Safety Permit chain ensures proper safety compliance.


![TC-18.3 — Safety Permits (WO Integration)](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_05_NAV_SP.png)

**Step 6: TC-18.3 — Safety Permit → Work Order Link**

Safety permits show the linked work order in their detail view. Active permits must be verified before work order execution can begin.


![TC-18.3 — Safety Permit → Work Order Link](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_06_SCREENSHOT_SP.png)

**Step 7: TC-18.2 — Purchase Request (MR Integration)**

Navigate to Purchase Request. PRs can be generated from maintenance requests to procure required parts and materials.


![TC-18.2 — Purchase Request (MR Integration)](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_07_NAV_PR.png)

**Step 8: TC-18.2 — MR → PR Integration**

Purchase requests generated from maintenance requests carry the requestor, site, department, and required items from the source MR.


![TC-18.2 — MR → PR Integration](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_08_SCREENSHOT_PR.png)

**Step 9: TC-18.5 — Vendor Performance**

Navigate to Vendor. Vendor performance is automatically calculated based on purchase receipt delivery data.


![TC-18.5 — Vendor Performance](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_09_NAV_VENDOR.png)

**Step 10: TC-18.5 — Vendor Performance Metrics**

The vendor list shows delivery ratings, on-time delivery percentages, quality scores, and total orders. These metrics are auto-calculated from purchase receipt records.


![TC-18.5 — Vendor Performance Metrics](test-artifacts/screenshots/TC-18-cross-workflow-integration__TC18_10_SCREENSHOT_VENDOR.png)

---

### 1.8. TC 20 Procurement Scenario

The procurement scenario starts when a maintenance request identifies parts that need to be purchased. The 'Create PR' server action initiates procurement.

**Step 1: TC-20.3 — Step 1: Maintenance Request (Parts Needed)**

The procurement scenario starts when a maintenance request identifies parts that need to be purchased. The 'Create PR' server action initiates procurement.


![TC-20.3 — Step 1: Maintenance Request (Parts Needed)](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_01_MR.png)

**Step 2: TC-20.3 — MR with Parts Requirements**

The maintenance request identifies required parts and materials. After approval, the 'Create Purchase Request' action generates a PR with the correct items.


![TC-20.3 — MR with Parts Requirements](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_02_SCREENSHOT_MR.png)

**Step 3: TC-20.3 — Step 2: Purchase Request**

The purchase request is generated from the MR. It contains the required items, quantities, and requestor information.


![TC-20.3 — Step 2: Purchase Request](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_03_PR.png)

**Step 4: TC-20.3 — PR from MR**

The purchase request shows items needed for the maintenance work. After approval, a purchase order is created to send to the vendor.


![TC-20.3 — PR from MR](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_04_SCREENSHOT_PR.png)

**Step 5: TC-20.3 — Step 3: Purchase Order**

The purchase order is issued to the vendor based on the approved PR. The PO tracks delivery dates and payment terms.


![TC-20.3 — Step 3: Purchase Order](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_05_PO.png)

**Step 6: TC-20.3 — PO Issued to Vendor**

The purchase order shows vendor details, line items, delivery schedule, and total amount. Approved POs become read-only.


![TC-20.3 — PO Issued to Vendor](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_06_SCREENSHOT_PO.png)

**Step 7: TC-20.3 — Step 4: Purchase Receipt**

When goods arrive, a purchase receipt is recorded against the PO. This updates inventory and triggers vendor performance recalculation.


![TC-20.3 — Step 4: Purchase Receipt](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_07_RECEIPT.png)

**Step 8: TC-20.3 — Receipt & Vendor Update**

The purchase receipt records the delivery date and quantities received. Vendor performance metrics (delivery rating, on-time rate) are automatically recalculated.


![TC-20.3 — Receipt & Vendor Update](test-artifacts/screenshots/TC-20-procurement-scenario__TC20_PROC_08_SCREENSHOT_REC.png)

---

### 1.9. TC 15 Sla Tracking

Navigate to Maintenance Request. SLA tracking fields are auto-populated when an MR is submitted based on its priority level.

**Step 1: TC-15.1 — MR SLA Tracking**

Navigate to Maintenance Request. SLA tracking fields are auto-populated when an MR is submitted based on its priority level.


![TC-15.1 — MR SLA Tracking](test-artifacts/screenshots/TC-15-sla-tracking__TC15_01_NAV_MR.png)

**Step 2: TC-15.1 — MR SLA Fields**

The maintenance request list shows SLA status indicators. High-priority MRs have shorter response and resolution SLA targets. Fields include: SLA Response Due, SLA Resolution Due, SLA Status, Is Overdue.


![TC-15.1 — MR SLA Fields](test-artifacts/screenshots/TC-15-sla-tracking__TC15_02_SCREENSHOT_MR.png)

**Step 3: TC-15.2 — WO SLA Tracking**

Navigate to Work Order. Work orders have stage-based SLA targets: Requested (8h), Approved (24h), In Progress (72h). SLA status updates automatically.


![TC-15.2 — WO SLA Tracking](test-artifacts/screenshots/TC-15-sla-tracking__TC15_03_NAV_WO.png)

**Step 4: TC-15.2 — WO SLA Status**

The work order list shows SLA tracking per stage. As work orders progress through their lifecycle, SLA timers reset for each stage with appropriate targets.


![TC-15.2 — WO SLA Status](test-artifacts/screenshots/TC-15-sla-tracking__TC15_04_SCREENSHOT_WO.png)

---

## 2. Asset Management

### 2.1. TC 04 Asset Create

Navigate to Asset Management → Asset. The asset list shows all registered assets with their current lifecycle state, site, and criticality.

**Step 1: TC-04.1 — Asset List**

Navigate to Asset Management → Asset. The asset list shows all registered assets with their current lifecycle state, site, and criticality.


![TC-04.1 — Asset List](test-artifacts/screenshots/TC-04-asset-create__TC04_01_NAV.png)

**Step 2: TC-04.1 — New Asset Form**

Click 'Add New' to open the asset creation form. The form includes fields for description, asset class, site, department, manufacturer, and more.


![TC-04.1 — New Asset Form](test-artifacts/screenshots/TC-04-asset-create__TC04_02_NEW.png)

**Step 3: TC-04.1 — Fill Description**

Enter "Test Motor 001 — E2E Lifecycle Test" into the Description field.


![TC-04.1 — Fill Description](test-artifacts/screenshots/TC-04-asset-create__TC04_03_FILL_DESC.png)

**Step 4: TC-04.1 — Asset Created**

Click 'Create' to save the asset. The system assigns an auto-generated ID (e.g., A-00001) and sets the initial workflow state to 'Acquired'.


![TC-04.1 — Asset Created](test-artifacts/screenshots/TC-04-asset-create__TC04_04_SAVE.png)

**Step 5: TC-04.1 — Asset Detail View**

The asset detail page shows all fields organized in tabs. The workflow state badge in the header indicates the current lifecycle state. Use the workflow dropdown to transition the asset through its lifecycle.


![TC-04.1 — Asset Detail View](test-artifacts/screenshots/TC-04-asset-create__TC04_05_VERIFY_STATE.png)

---

### 2.2. TC 04 Asset Hierarchy

Navigate to Asset Management. The asset list supports tree view to display parent-child hierarchies.

**Step 1: TC-04.2 — Asset List**

Navigate to Asset Management. The asset list supports tree view to display parent-child hierarchies.


![TC-04.2 — Asset List](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_01_NAV.png)

**Step 2: TC-04.2 — Asset Hierarchy View**

The asset list displays assets in a hierarchical structure. Parent assets can be expanded to show sub-assets (children). This enables tracking of complex equipment assemblies.


![TC-04.2 — Asset Hierarchy View](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_02_SCREENSHOT.png)

**Step 3: TC-04.2 — New Child Asset**

Click 'Add New' to create a new asset. To establish a hierarchy, set the 'Parent Asset' field to link this asset as a sub-component.


![TC-04.2 — New Child Asset](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_03_NEW.png)

**Step 4: TC-04.2 — Fill Description**

Enter "E2E Child Asset — Motor Assembly" into the Description field.


![TC-04.2 — Fill Description](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_04_FILL.png)

**Step 5: TC-04.2 — Child Asset Created**

The child asset is saved. Set the Parent Asset field to establish the hierarchy relationship.


![TC-04.2 — Child Asset Created](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_05_SAVE.png)

**Step 6: TC-04.2 — Asset Detail with Parent Link**

The asset detail page shows the parent asset relationship. Sub-assets appear in the Parent-Child tab, enabling drill-down into equipment assemblies.


![TC-04.2 — Asset Detail with Parent Link](test-artifacts/screenshots/TC-04-asset-hierarchy__TC04_HIER_06_VERIFY.png)

---

### 2.3. TC 04 Equipment Crud

Navigate to Equipment. Equipment records track individual tools, vehicles, and machinery used in maintenance operations.

**Step 1: TC-04.5 — Equipment List**

Navigate to Equipment. Equipment records track individual tools, vehicles, and machinery used in maintenance operations.


![TC-04.5 — Equipment List](test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_01_NAV.png)

**Step 2: TC-04.5 — Equipment List View**

The Equipment list shows all registered equipment with IDs, descriptions, types (Owned/Rented), and status. Use filters and search to locate specific equipment.


![TC-04.5 — Equipment List View](test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_02_LIST.png)

**Step 3: TC-04.5 — Open Equipment Record**

Click on an existing equipment record to view its details, including type, description, and linked work orders.


![TC-04.5 — Open Equipment Record](test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_03_CLICK_FIRST.png)

**Step 4: TC-04.5 — Wait for Page Load**

Wait for all page components to finish loading and rendering.


![TC-04.5 — Wait for Page Load](test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_04_WAIT.png)

**Step 5: TC-04.5 — Equipment Detail**

The equipment detail page shows the equipment ID, type (Owned or Rented), description, and association fields. Equipment can be linked to work orders for resource tracking.


![TC-04.5 — Equipment Detail](test-artifacts/screenshots/TC-04-equipment-crud__TC04_EQ_05_DETAIL.png)

---

### 2.4. TC 04 Meter Reading

Navigate to Meter. Meters track operating parameters like running hours, odometer readings, and cycle counts for assets.

**Step 1: TC-04.3 — Meter List**

Navigate to Meter. Meters track operating parameters like running hours, odometer readings, and cycle counts for assets.


![TC-04.3 — Meter List](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_01_NAV.png)

**Step 2: TC-04.3 — Meter Overview**

The meter list shows all configured meters across assets with their current readings, types, and update frequency.


![TC-04.3 — Meter Overview](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_02_SCREENSHOT.png)

**Step 3: TC-04.3 — New Meter**

Click 'Add New' to create a meter. Specify the meter type (Operating Hours, Odometer, Cycle Count), linked asset, and unit of measure.


![TC-04.3 — New Meter](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_03_NEW.png)

**Step 4: TC-04.3 — Fill Meter Name**

Enter "E2E Operating Hours Meter" into the Meter Name field.


![TC-04.3 — Fill Meter Name](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_04_FILL.png)

**Step 5: TC-04.3 — Meter Created**

The meter is created and linked to an asset. Add meter readings to track operating parameters over time.


![TC-04.3 — Meter Created](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_05_SAVE.png)

**Step 6: TC-04.3 — Meter Detail**

The meter detail page shows the meter type, current reading, and reading history. Meter readings trigger preventive maintenance based on configured thresholds.


![TC-04.3 — Meter Detail](test-artifacts/screenshots/TC-04-meter-reading__TC04_MTR_06_VERIFY.png)

**Step 7: TC-04.3 — Meter Reading List**

Navigate to Meter Reading. Meter readings record periodic measurements for meters linked to assets.


![TC-04.3 — Meter Reading List](test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_01_NAV.png)

**Step 8: TC-04.3 — New Meter Reading**

Click 'Add New' to record a new meter reading. Select the meter, enter the reading value, and timestamp.


![TC-04.3 — New Meter Reading](test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_02_NEW.png)

**Step 9: TC-04.3 — Meter Reading Form**

The meter reading form captures the current value, date, and any notes. The system calculates the delta from the previous reading automatically.


![TC-04.3 — Meter Reading Form](test-artifacts/screenshots/TC-04-meter-reading__TC04_MR_03_SCREENSHOT.png)

---

### 2.5. TC 05 Asset Workflow Decommission

Navigate to Asset. The complete asset lifecycle includes: Acquired → Received → Inspected → Installed → Active → various maintenance paths → Retire → Inactive → Decommissioned.

**Step 1: TC-05.1 — Asset Workflow States**

Navigate to Asset. The complete asset lifecycle includes: Acquired → Received → Inspected → Installed → Active → various maintenance paths → Retire → Inactive → Decommissioned.


![TC-05.1 — Asset Workflow States](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_01_NAV.png)

**Step 2: TC-05.1 — Asset List with Workflow States**

The asset list shows each asset's current workflow state. State transitions are controlled by role permissions and business rules.


![TC-05.1 — Asset List with Workflow States](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_02_SCREENSHOT.png)

**Step 3: TC-05.1 — Asset Creation for Lifecycle Test**

Create a new asset to test the complete lifecycle. Fill in description and required fields.


![TC-05.1 — Asset Creation for Lifecycle Test](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_03_NAV_NEW.png)

**Step 4: TC-05.1 — Fill Description**

Enter "E2E Lifecycle Test — Full Decommission P" into the Description field.


![TC-05.1 — Fill Description](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_04_FILL.png)

**Step 5: TC-05.1 — Asset Created (Acquired)**

The asset is created in 'Acquired' state. The full lifecycle path is: Acquired → Receive → Inspected → Install → Active → Retire → Inactive → Remove → Decommissioned.


![TC-05.1 — Asset Created (Acquired)](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_05_SAVE.png)

**Step 6: TC-05.1 — Asset Lifecycle Transitions**

The asset detail page shows available workflow transitions in the dropdown. Each transition moves the asset to the next lifecycle state with an audit trail entry.


![TC-05.1 — Asset Lifecycle Transitions](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_06_VERIFY.png)

**Step 7: TC-05 — Workflow Configuration**

Navigate to Workflow management to view all configured workflow definitions. Each entity type has its own workflow with states and transitions.


![TC-05 — Workflow Configuration](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_07_NAV_WF.png)

**Step 8: TC-05 — Workflow Definitions**

The workflow configuration page shows all entity workflows with their states, transitions, and role restrictions. The asset workflow has the most complex state machine.


![TC-05 — Workflow Definitions](test-artifacts/screenshots/TC-05-asset-workflow-decommission__TC05_08_SCREENSHOT_WF.png)

---

### 2.6. Asset Lifecycle

Navigate to the Asset list page by clicking 'Asset' in the sidebar or visiting /asset. This page shows all registered assets in a data table with search, filter, and sort capabilities.

**Step 1: Asset List**

Navigate to the Asset list page by clicking 'Asset' in the sidebar or visiting /asset. This page shows all registered assets in a data table with search, filter, and sort capabilities.


![Asset List](test-artifacts/screenshots/asset-lifecycle__ASSET_01_NAVIGATE.png)

**Step 2: Create New Asset**

Click 'Add New' in the top-right corner to open the asset creation form. You will be redirected to a blank form where you can enter the asset details.


![Create New Asset](test-artifacts/screenshots/asset-lifecycle__ASSET_02_NEW.png)

**Step 3: Fill Form Field**

Enter "Test Pump Assembly E2E" into the Description field.


![Fill Form Field](test-artifacts/screenshots/asset-lifecycle__ASSET_03_FILL_NAME.png)

**Step 4: Asset Form Filled**

Fill in the asset details. The 'Description' field is the primary identifier. Additional fields can be filled as needed.


![Asset Form Filled](test-artifacts/screenshots/asset-lifecycle__ASSET_04_FILL_DESCRIPTION.png)

**Step 5: Save New Asset**

After filling in the required fields, click 'Save' to create the asset record. A success notification appears confirming the asset was created.


![Save New Asset](test-artifacts/screenshots/asset-lifecycle__ASSET_05_SAVE.png)

**Step 6: Asset Details View**

After saving, you are taken to the asset detail page where you can view all fields, switch tabs, and manage workflow state.


![Asset Details View](test-artifacts/screenshots/asset-lifecycle__ASSET_06_VERIFY_SAVED.png)

---

## 3. Condition Monitoring

### 3.1. TC 10 Condition Monitoring Types

Navigate to Condition Monitoring. The system supports multiple monitoring types: Vibration, Temperature, Pressure, Oil Analysis, Ultrasonic, Thermography, and Current/Voltage.

**Step 1: TC-10.2 — Condition Monitoring List**

Navigate to Condition Monitoring. The system supports multiple monitoring types: Vibration, Temperature, Pressure, Oil Analysis, Ultrasonic, Thermography, and Current/Voltage.


![TC-10.2 — Condition Monitoring List](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_01_NAV.png)

**Step 2: TC-10.2 — Monitoring Types Overview**

The condition monitoring list shows all monitoring records with their type, current value, threshold levels, and status (Normal, Warning, Critical, Resolved).


![TC-10.2 — Monitoring Types Overview](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_02_SCREENSHOT.png)

**Step 3: TC-10.2 — New Condition Monitoring**

Click 'Add New' to create a condition monitoring record. Select the monitoring type, linked asset, and configure baseline, warning, and critical threshold levels.


![TC-10.2 — New Condition Monitoring](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_03_NEW.png)

**Step 4: TC-10.2 — Fill Analysis Notes**

Enter "E2E Temperature monitoring — Cooling sys" into the Analysis Notes field.


![TC-10.2 — Fill Analysis Notes](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_04_FILL.png)

**Step 5: TC-10.2 — Monitoring Record Created**

The monitoring record is created in 'Active' state. Update the current value to trigger threshold-based status changes (Normal → Warning → Critical).


![TC-10.2 — Monitoring Record Created](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_05_SAVE.png)

**Step 6: TC-10.2 — Monitoring Detail by Type**

The monitoring detail shows type-specific fields, thresholds, and current readings. Different monitoring types have different measurement units and threshold configurations.


![TC-10.2 — Monitoring Detail by Type](test-artifacts/screenshots/TC-10-condition-monitoring-types__TC10_TYPE_06_VERIFY.png)

---

### 3.2. TC 10 Condition Monitoring

Navigate to Condition Monitoring. This module tracks real-time sensor data and condition indicators for assets, with configurable warning and critical thresholds.

**Step 1: TC-10.1 — Condition Monitoring List**

Navigate to Condition Monitoring. This module tracks real-time sensor data and condition indicators for assets, with configurable warning and critical thresholds.


![TC-10.1 — Condition Monitoring List](test-artifacts/screenshots/TC-10-condition-monitoring__TC10_01_NAV.png)

**Step 2: TC-10.1 — New Condition Monitor**

Click 'Add New' to set up condition monitoring for an asset. Define the monitoring type (Vibration, Temperature, Pressure, etc.), baseline value, and warning/critical thresholds.


![TC-10.1 — New Condition Monitor](test-artifacts/screenshots/TC-10-condition-monitoring__TC10_02_NEW.png)

**Step 3: TC-10.1 — Fill Analysis Notes**

Enter "E2E Test — Vibration monitoring for Test" into the Analysis Notes field.


![TC-10.1 — Fill Analysis Notes](test-artifacts/screenshots/TC-10-condition-monitoring__TC10_03_FILL.png)

**Step 4: TC-10.1 — Condition Monitor Created**

The condition monitoring record is created in 'Active' state. As readings are taken, the system automatically transitions to Warning or Critical states based on threshold values.


![TC-10.1 — Condition Monitor Created](test-artifacts/screenshots/TC-10-condition-monitoring__TC10_04_SAVE.png)

**Step 5: TC-10.1 — Condition Monitoring Detail**

The detail view shows the asset, monitoring type, baseline value, thresholds, current reading, alert status, and trend direction. The workflow state reflects the current alert level.


![TC-10.1 — Condition Monitoring Detail](test-artifacts/screenshots/TC-10-condition-monitoring__TC10_05_VERIFY.png)

---

## 4. Authentication

### 4.1. TC 01 Authentication

Clear browser cookies and local storage to ensure a clean test state.

**Step 1: TC-01 — Clear Session**

Clear browser cookies and local storage to ensure a clean test state.


![TC-01 — Clear Session](test-artifacts/screenshots/TC-01-authentication__TC01_00_CLEAR.png)

**Step 2: TC-01.1 — Login Page**

Navigate to the login page. The login form displays with Username and Password fields, along with the organization branding (logo and name).


![TC-01.1 — Login Page](test-artifacts/screenshots/TC-01-authentication__TC01_01_LOGIN_PAGE.png)

**Step 3: TC-01 — Fill Form Field**

Enter "admin" into the form field.


![TC-01 — Fill Form Field](test-artifacts/screenshots/TC-01-authentication__TC01_02_ENTER_CREDS.png)

**Step 4: TC-01 — Fill Form Field**

Enter "admin123" into the form field.


![TC-01 — Fill Form Field](test-artifacts/screenshots/TC-01-authentication__TC01_03_ENTER_PASS.png)

**Step 5: TC-01.1 — Successful Login**

After entering valid credentials and clicking 'Sign In', you are redirected to the Home page. The sidebar displays navigation items based on your role permissions.


![TC-01.1 — Successful Login](test-artifacts/screenshots/TC-01-authentication__TC01_04_SUBMIT.png)

**Step 6: TC-01.1 — Sidebar & Navigation**

The sidebar shows all available modules based on your role. Admin users can see all entities including Settings, Admin, Workflow, and Model Editor sections.


![TC-01.1 — Sidebar & Navigation](test-artifacts/screenshots/TC-01-authentication__TC01_05_VERIFY_SIDEBAR.png)

**Step 7: TC-01.5 — User Menu**

Click your name/avatar at the bottom of the sidebar to open the user menu. From here you can access your Profile or Logout.


![TC-01.5 — User Menu](test-artifacts/screenshots/TC-01-authentication__TC01_06_PROFILE.png)

---

### 4.2. TC 01 Profile Update

Navigate to the Profile page by clicking on the avatar or visiting /profile. The profile page shows user details and allows editing contact information.

**Step 1: TC-01.5 — User Profile**

Navigate to the Profile page by clicking on the avatar or visiting /profile. The profile page shows user details and allows editing contact information.


![TC-01.5 — User Profile](test-artifacts/screenshots/TC-01-profile-update__TC01_PROF_01_NAV.png)

**Step 2: TC-01.5 — Profile Details**

The profile page displays the current user's information including username, email, role, and employee linkage. Users can update their contact details and password.


![TC-01.5 — Profile Details](test-artifacts/screenshots/TC-01-profile-update__TC01_PROF_02_SCREENSHOT.png)

---

### 4.3. TC 01 User Crud

Navigate to the Admin panel. This page provides user management, role configuration, and system settings.

**Step 1: TC-01.4 — Admin Panel**

Navigate to the Admin panel. This page provides user management, role configuration, and system settings.


![TC-01.4 — Admin Panel](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_01_NAV.png)

**Step 2: TC-01.4 — Admin Dashboard**

The Admin panel shows user accounts, roles, and system configuration. Administrators can create, edit, and deactivate user accounts.


![TC-01.4 — Admin Dashboard](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_02_SCREENSHOT.png)

**Step 3: TC-01.4 — User List**

Navigate to the User entity list. This shows all registered users with their roles, status, and last login information.


![TC-01.4 — User List](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_03_NAV_USERS.png)

**Step 4: TC-01.4 — User List View**

The user list shows all registered user accounts with their username, role assignment, status, and employee linkage. Administrators can manage users from this view.


![TC-01.4 — User List View](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_04_LIST.png)

**Step 5: TC-01.4 — User Detail**

Click on a user record to view details including username, email, role assignment, and employee linkage.


![TC-01.4 — User Detail](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_05_CLICK_FIRST.png)

**Step 6: TC-01.4 — Wait for Page Load**

Wait for all page components to finish loading and rendering.


![TC-01.4 — Wait for Page Load](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_06_WAIT.png)

**Step 7: TC-01.4 — User Detail View**

The user detail page shows username, email, password fields, role assignment, and employee linkage. The role determines which entities and actions the user can access.


![TC-01.4 — User Detail View](test-artifacts/screenshots/TC-01-user-crud__TC01_USER_07_DETAIL.png)

---

### 4.4. Login Edge Cases

Clear browser cookies and local storage to ensure a clean test state.

**Step 1: Clear Session**

Clear browser cookies and local storage to ensure a clean test state.


![Clear Session](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_00_CLEAR.png)

**Step 2: Navigate**

Navigate to /login.


![Navigate](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_01_NAVIGATE.png)

**Step 3: Empty Credentials Error**

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.


![Empty Credentials Error](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_02_EMPTY_SUBMIT.png)

**Step 4: Fill Form Field**

Enter "admin" into the form field.


![Fill Form Field](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_03_WRONG_PASSWORD.png)

**Step 5: Fill Form Field**

Enter "wrongpassword" into the form field.


![Fill Form Field](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_04_WRONG_PASSWORD_FILL.png)

**Step 6: Invalid Credentials Error**

If you enter an incorrect username or password, the system displays an error message. Verify your credentials and try again. After multiple failed attempts, your account may be temporarily locked.


![Invalid Credentials Error](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_05_WRONG_PASSWORD_SUBMIT.png)

---

### 4.5. Login Happy Path

Clear browser cookies and local storage to ensure a clean test state.

**Step 1: Clear Session**

Clear browser cookies and local storage to ensure a clean test state.


![Clear Session](test-artifacts/screenshots/login-happy-path__LOGIN_00_CLEAR.png)

**Step 2: Login Page**

Open the EAM application in your web browser. You will be presented with the login screen showing the organization branding and credential fields.


![Login Page](test-artifacts/screenshots/login-happy-path__LOGIN_01_NAVIGATE.png)

**Step 3: Enter Username**

Enter your username in the Username field. This is the account name provided by your system administrator.


![Enter Username](test-artifacts/screenshots/login-happy-path__LOGIN_02_ENTER_USERNAME.png)

**Step 4: Enter Password**

Enter your password in the Password field. Passwords are case-sensitive.


![Enter Password](test-artifacts/screenshots/login-happy-path__LOGIN_03_ENTER_PASSWORD.png)

**Step 5: Submit Login**

Click the 'Sign in' button. Upon successful authentication, you will be redirected to the home page.


![Submit Login](test-artifacts/screenshots/login-happy-path__LOGIN_04_SUBMIT.png)

**Step 6: Home Page After Login**

After successful login, the main application loads with the sidebar navigation showing all available modules.


![Home Page After Login](test-artifacts/screenshots/login-happy-path__LOGIN_05_HOME_LOADED.png)

---

## 5. Dashboard

### 5.1. Dashboard Overview

The Dashboard provides a real-time overview of your asset management system. Navigate to the Dashboard by clicking 'Dashboard' in the left sidebar or by visiting /dashboard.

**Step 1: Dashboard Overview**

The Dashboard provides a real-time overview of your asset management system. Navigate to the Dashboard by clicking 'Dashboard' in the left sidebar or by visiting /dashboard.


![Dashboard Overview](test-artifacts/screenshots/dashboard-overview__DASH_01_NAVIGATE.png)

**Step 2: Key Performance Indicators**

Six KPI cards are displayed at the top: Total Assets, Work Orders, Overdue WOs, Inventory, Purchase Requests, and Incidents. Each card shows the current total and a secondary metric such as the count from the last 30 days.


![Key Performance Indicators](test-artifacts/screenshots/dashboard-overview__DASH_02_KPI_CARDS.png)

**Step 3: Refreshing Dashboard Data**

Click the 'Refresh' button in the top-right corner to reload all dashboard data from the server.


![Refreshing Dashboard Data](test-artifacts/screenshots/dashboard-overview__DASH_03_REFRESH.png)

---

## 6. General Features

### 6.1. Entity List Features

Entity list pages display records in a data table. They support search, column filtering, sorting, pagination, and multiple view modes (list, tree, diagram, hierarchy).

**Step 1: Entity List Page**

Entity list pages display records in a data table. They support search, column filtering, sorting, pagination, and multiple view modes (list, tree, diagram, hierarchy).


![Entity List Page](test-artifacts/screenshots/entity-list-features__LIST_01_NAVIGATE.png)

**Step 2: Search Records**

Type in the search box to filter records. The table updates in real-time as you type. You can search across the selected filter field.


![Search Records](test-artifacts/screenshots/entity-list-features__LIST_02_SEARCH.png)

**Step 3: Wait for Page Load**

Wait for all page components to finish loading and rendering.


![Wait for Page Load](test-artifacts/screenshots/entity-list-features__LIST_03_WAIT_RESULTS.png)

**Step 4: Search Results**

The table displays only records matching your search term. The total count badge updates to reflect the filtered result count.


![Search Results](test-artifacts/screenshots/entity-list-features__LIST_04_SEARCH_RESULTS.png)

**Step 5: Clear Field**

Clear the search input to reset the filtered results.


![Clear Field](test-artifacts/screenshots/entity-list-features__LIST_05_CLEAR_SEARCH.png)

**Step 6: Open Record Detail**

Click any row in the table to open the detail view for that record. You can view and edit all fields, manage attachments, and control the workflow state.


![Open Record Detail](test-artifacts/screenshots/entity-list-features__LIST_06_CLICK_ROW.png)

---

## 7. Navigation

### 7.1. Sidebar Navigation

The sidebar is always visible on the left side of the screen. It contains the organization logo, navigation links grouped by module, and user account controls at the bottom.

**Step 1: Application Sidebar**

The sidebar is always visible on the left side of the screen. It contains the organization logo, navigation links grouped by module, and user account controls at the bottom.


![Application Sidebar](test-artifacts/screenshots/sidebar-navigation__NAV_01_HOME.png)

**Step 2: Navigate to Dashboard**

Click 'Dashboard' in the sidebar to view the system-wide KPI overview.


![Navigate to Dashboard](test-artifacts/screenshots/sidebar-navigation__NAV_02_DASHBOARD.png)

**Step 3: Navigate to Assets**

Click 'Asset' under the Asset Management module to view the full list of registered assets.


![Navigate to Assets](test-artifacts/screenshots/sidebar-navigation__NAV_03_ASSET.png)

**Step 4: Navigate to Work Orders**

Click 'Work Order' under the Work Management module to view and manage work orders. Expand the module group if it is collapsed.


![Navigate to Work Orders](test-artifacts/screenshots/sidebar-navigation__NAV_04_WORK_ORDER.png)

**Step 5: Collapse Sidebar**

Click the hamburger menu icon in the header to collapse the sidebar. This gives you more horizontal space for data tables and forms. Click again to expand.


![Collapse Sidebar](test-artifacts/screenshots/sidebar-navigation__NAV_05_COLLAPSE.png)

---

## 8. Maintenance

### 8.1. TC 20 Corrective Maintenance Scenario

The corrective maintenance scenario begins with condition monitoring detecting an anomaly. A vibration reading exceeds the critical threshold, triggering the maintenance chain.

**Step 1: TC-20.1 — Step 1: Condition Detection**

The corrective maintenance scenario begins with condition monitoring detecting an anomaly. A vibration reading exceeds the critical threshold, triggering the maintenance chain.


![TC-20.1 — Step 1: Condition Detection](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_01_NAV_CM.png)

**Step 2: TC-20.1 — Condition Monitoring Alert**

Condition monitoring records show the escalation from Normal → Warning → Critical. Critical conditions trigger maintenance request creation.


![TC-20.1 — Condition Monitoring Alert](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_02_SCREENSHOT_CM.png)

**Step 3: TC-20.1 — Step 2: Maintenance Request**

A high-priority maintenance request is created to address the critical condition. The MR includes the asset reference and failure description.


![TC-20.1 — Step 2: Maintenance Request](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_03_NAV_MR.png)

**Step 4: TC-20.1 — MR Linked to Condition**

The maintenance request references the condition monitoring alert. After approval, a maintenance order and work order are generated.


![TC-20.1 — MR Linked to Condition](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_04_SCREENSHOT_MR.png)

**Step 5: TC-20.1 — Step 3: Work Order Execution**

A corrective work order is generated from the maintenance order. The WO tracks labor, parts, equipment, and safety permit requirements.


![TC-20.1 — Step 3: Work Order Execution](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_05_NAV_WO.png)

**Step 6: TC-20.1 — Work Order with Resources**

The work order shows assigned resources (labor, parts, equipment), linked safety permit, and workflow progression through Requested → Approved → In Progress → Closed.


![TC-20.1 — Work Order with Resources](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_06_SCREENSHOT_WO.png)

**Step 7: TC-20.1 — Step 4: Safety Permit**

A safety permit is issued for the corrective work order. The permit ensures proper safety protocols (LOTO, PPE) are followed during repairs.


![TC-20.1 — Step 4: Safety Permit](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_07_NAV_SP.png)

**Step 8: TC-20.1 — Safety Permit for Corrective Work**

The safety permit detail shows hazards, precautions, and the linked work order. Active permits must be verified before work begins.


![TC-20.1 — Safety Permit for Corrective Work](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_08_SCREENSHOT_SP.png)

**Step 9: TC-20.1 — Step 5: Failure Analysis**

After completing the corrective work, a failure analysis is created to document root cause, remedy, and prevention measures.


![TC-20.1 — Step 5: Failure Analysis](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_09_NAV_FA.png)

**Step 10: TC-20.1 — Root Cause Analysis**

The failure analysis records severity, occurrence, and detection ratings. The RPN (Risk Priority Number) score prioritizes corrective actions. 5-Why and Fishbone templates support structured root cause analysis.


![TC-20.1 — Root Cause Analysis](test-artifacts/screenshots/TC-20-corrective-maintenance-scenario__TC20_10_SCREENSHOT_FA.png)

---

### 8.2. TC 20 Preventive Maintenance Scenario

The preventive maintenance scenario starts with the PM Calendar. Scheduled tasks are displayed in a monthly view with color-coded statuses.

**Step 1: TC-20.2 — Step 1: PM Calendar**

The preventive maintenance scenario starts with the PM Calendar. Scheduled tasks are displayed in a monthly view with color-coded statuses.


![TC-20.2 — Step 1: PM Calendar](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_01_CALENDAR.png)

**Step 2: TC-20.2 — PM Calendar Overview**

The calendar shows all scheduled preventive maintenance tasks. Creating a task auto-generates the chain: Maintenance Activity → PMA → Work Order (Preventive) → WO Activity → Maintenance Request.


![TC-20.2 — PM Calendar Overview](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_02_SCREENSHOT_CAL.png)

**Step 3: TC-20.2 — Step 2: Maintenance Activity**

Maintenance activities are generated from PM Calendar tasks. Each activity links to a PMA template and a work order.


![TC-20.2 — Step 2: Maintenance Activity](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_03_NAV_MA.png)

**Step 4: TC-20.2 — Maintenance Activities**

The maintenance activity list shows scheduled PM tasks with their status, due date, and linked entities (PMA, WO, MR). Activities progress through Draft → Pending → Approved → Release → Completed.


![TC-20.2 — Maintenance Activities](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_04_SCREENSHOT_MA.png)

**Step 5: TC-20.2 — Step 3: Preventive Work Order**

Work orders generated from PM Calendar tasks have type 'Preventive'. They inherit the task details, assigned resources, and checklists from the PMA template.


![TC-20.2 — Step 3: Preventive Work Order](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_05_NAV_WO.png)

**Step 6: TC-20.2 — Preventive WO Execution**

The preventive work order tracks the scheduled maintenance execution. Completing the WO updates the PM Calendar and resets the schedule for the next occurrence.


![TC-20.2 — Preventive WO Execution](test-artifacts/screenshots/TC-20-preventive-maintenance-scenario__TC20_PM_06_SCREENSHOT_WO.png)

---

### 8.3. TC 06 Maintenance Request

Navigate to Maintenance Request. Maintenance requests are used to report issues, request corrective maintenance, or schedule preventive maintenance tasks.

**Step 1: TC-06.1 — Maintenance Request List**

Navigate to Maintenance Request. Maintenance requests are used to report issues, request corrective maintenance, or schedule preventive maintenance tasks.


![TC-06.1 — Maintenance Request List](test-artifacts/screenshots/TC-06-maintenance-request__TC06_01_NAV.png)

**Step 2: TC-06.1 — New Maintenance Request**

Click 'Add New' to create a new maintenance request. Fill in the requestor, asset, priority, category, and description fields.


![TC-06.1 — New Maintenance Request](test-artifacts/screenshots/TC-06-maintenance-request__TC06_02_NEW.png)

**Step 3: TC-06.1 — Fill Description**

Enter "E2E Test — Motor vibration excessive, re" into the Description field.


![TC-06.1 — Fill Description](test-artifacts/screenshots/TC-06-maintenance-request__TC06_03_FILL_DESC.png)

**Step 4: TC-06.1 — MR Created (Draft)**

The maintenance request is created with an auto-generated ID (e.g., MTREQ-00001) and workflow state 'Draft'. From here you can submit it for approval.


![TC-06.1 — MR Created (Draft)](test-artifacts/screenshots/TC-06-maintenance-request__TC06_04_SAVE.png)

**Step 5: TC-06.1 — Maintenance Request Detail (Draft)**

The maintenance request is in Draft state. The workflow dropdown shows available transitions. Click 'Submit for Approval' to advance the request.


![TC-06.1 — Maintenance Request Detail (Draft)](test-artifacts/screenshots/TC-06-maintenance-request__TC06_05_VERIFY_DRAFT.png)

---

### 8.4. TC 06 Maintenance Request Lifecycle Full

Navigate to Maintenance Request. MRs progress through: Draft → Pending Approval → Approved → Release → Completed. Emergency MRs can bypass the approval queue.

**Step 1: TC-06.1 — Maintenance Request List**

Navigate to Maintenance Request. MRs progress through: Draft → Pending Approval → Approved → Release → Completed. Emergency MRs can bypass the approval queue.


![TC-06.1 — Maintenance Request List](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_01_NAV.png)

**Step 2: TC-06.1 — MR List Overview**

The maintenance request list shows all MRs with their priority, status, requester, and SLA indicator. Filter by status to see pending, approved, or completed requests.


![TC-06.1 — MR List Overview](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_02_SCREENSHOT_LIST.png)

**Step 3: TC-06.1 — New MR Form**

Click 'Add New' to create a maintenance request. Enter the description, priority (Low/Medium/High/Emergency), site, department, and requested by information.


![TC-06.1 — New MR Form](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_03_NEW.png)

**Step 4: TC-06.1 — Fill Description**

Enter "E2E Full Lifecycle — Pump vibration abov" into the Description field.


![TC-06.1 — Fill Description](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_04_FILL.png)

**Step 5: TC-06.1 — MR Created (Draft)**

The maintenance request is created in 'Draft' state with an auto-generated ID (e.g., MR-00001). Submit for approval to advance the workflow.


![TC-06.1 — MR Created (Draft)](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_05_SAVE.png)

**Step 6: TC-06.1 — MR Detail View**

The MR detail page shows all fields, priority badge, workflow state, and SLA tracking fields. SLA Response Due and SLA Resolution Due are auto-populated based on priority level.


![TC-06.1 — MR Detail View](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_06_VERIFY.png)

**Step 7: TC-06 — Checklist List**

Navigate to Checklist. Checklists are linked to maintenance requests and work orders to ensure all required inspection points are completed.


![TC-06 — Checklist List](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_07_NAV_CHECKLIST.png)

**Step 8: TC-06 — Checklist Overview**

The checklist list shows all inspection checklists with their linked entity, completion status, and number of items checked.


![TC-06 — Checklist Overview](test-artifacts/screenshots/TC-06-maintenance-request-lifecycle-full__TC06_FULL_08_SCREENSHOT_CL.png)

---

### 8.5. Maintenance Request Lifecycle

Navigate to the Maintenance Request list page. Maintenance requests are used to report issues and request corrective or preventive maintenance.

**Step 1: Maintenance Request List**

Navigate to the Maintenance Request list page. Maintenance requests are used to report issues and request corrective or preventive maintenance.


![Maintenance Request List](test-artifacts/screenshots/maintenance-request-lifecycle__MR_01_NAVIGATE.png)

**Step 2: Create New Maintenance Request**

Click 'Add New' to open the maintenance request form.


![Create New Maintenance Request](test-artifacts/screenshots/maintenance-request-lifecycle__MR_02_NEW.png)

**Step 3: Fill Form Field**

Enter "E2E Test — Leaking pipe in Building A" into the Description field.


![Fill Form Field](test-artifacts/screenshots/maintenance-request-lifecycle__MR_03_FILL_DESCRIPTION.png)

**Step 4: Save Maintenance Request**

Click 'Save' to submit the maintenance request. The system creates a draft record that can be moved through the approval workflow.


![Save Maintenance Request](test-artifacts/screenshots/maintenance-request-lifecycle__MR_04_SAVE.png)

**Step 5: Maintenance Request Details**

The maintenance request has been created. Review the details and use the workflow dropdown to advance the request through its lifecycle.


![Maintenance Request Details](test-artifacts/screenshots/maintenance-request-lifecycle__MR_05_VERIFY_SAVED.png)

---

## 9. Master Data

### 9.1. TC 03 Master Data Department

Navigate to Department. Departments are organizational units within a site, used for cost allocation and team-level data scoping.

**Step 1: TC-03.1 — Department List**

Navigate to Department. Departments are organizational units within a site, used for cost allocation and team-level data scoping.


![TC-03.1 — Department List](test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_01_NAV.png)

**Step 2: TC-03.1 — Add New**

Click the Add New button to open the creation form.


![TC-03.1 — Add New](test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_02_NEW.png)

**Step 3: TC-03.1 — Fill Department Name**

Enter "E2E Department X" into the Department Name field.


![TC-03.1 — Fill Department Name](test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_03_FILL_NAME.png)

**Step 4: TC-03.1 — Department Saved**

The department is created and linked to its parent site. Departments are used for team-level data scoping (scope=team) in the RBAC system.


![TC-03.1 — Department Saved](test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_04_SAVE.png)

**Step 5: TC-03.1 — Hierarchy Complete**

With Organization → Site → Department created, the organizational hierarchy is established. This hierarchy is used for data scoping, cost allocation, and reporting.


![TC-03.1 — Hierarchy Complete](test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_05_VERIFY.png)

---

### 9.2. TC 03 Employee Labor

Navigate to Employee. Employees are linked to users, sites, and departments. They serve as requestors, approvers, and technicians across the system.

**Step 1: TC-03.2 — Employee List**

Navigate to Employee. Employees are linked to users, sites, and departments. They serve as requestors, approvers, and technicians across the system.


![TC-03.2 — Employee List](test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_01_NAV.png)

**Step 2: TC-03.2 — New Employee**

Click 'Add New' to create an employee record. Link the employee to a user account, site, and department.


![TC-03.2 — New Employee](test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_02_NEW.png)

**Step 3: TC-03.2 — Fill Employee Name**

Enter "E2E John Smith" into the Employee Name field.


![TC-03.2 — Fill Employee Name](test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_03_FILL.png)

**Step 4: TC-03.2 — Employee Created**

The employee record is created with an auto-generated ID (e.g., EMP-00001). The employee can now be assigned to maintenance requests, work orders, and labor records.


![TC-03.2 — Employee Created](test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_04_SAVE.png)

**Step 5: TC-03.2 — Employee Detail**

The employee record shows name, linked user, site, department, and trade. Employees serve as the bridge between user accounts and operational entities.


![TC-03.2 — Employee Detail](test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_05_VERIFY.png)

---

### 9.3. TC 03 Financial Master Data

Navigate to Account. Accounts are used for financial tracking and cost allocation across maintenance operations.

**Step 1: TC-03.5 — Account List**

Navigate to Account. Accounts are used for financial tracking and cost allocation across maintenance operations.


![TC-03.5 — Account List](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_01_NAV_ACCT.png)

**Step 2: TC-03.5 — New Account**

Click 'Add New' to create an account record. Enter the account name, type, and associated cost center.


![TC-03.5 — New Account](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_02_NEW_ACCT.png)

**Step 3: TC-03.5 — Fill Account Name**

Enter "E2E Maintenance Cost Account" into the Account Name field.


![TC-03.5 — Fill Account Name](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_03_FILL_ACCT.png)

**Step 4: TC-03.5 — Account Created**

The account is saved and can be linked to work orders and purchase requests for cost tracking.


![TC-03.5 — Account Created](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_04_SAVE_ACCT.png)

**Step 5: TC-03.5 — Account Detail**

The account detail page shows the account number, name, type, and associated transactions.


![TC-03.5 — Account Detail](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_05_VERIFY_ACCT.png)

**Step 6: TC-03.5 — Cost Code List**

Navigate to Cost Code. Cost codes categorize expenses for detailed financial reporting on maintenance activities.


![TC-03.5 — Cost Code List](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_06_NAV_CC.png)

**Step 7: TC-03.5 — New Cost Code**

Click 'Add New' to create a cost code. Specify the code identifier, description, and category.


![TC-03.5 — New Cost Code](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_07_NEW_CC.png)

**Step 8: TC-03.5 — Fill Cost Code Name**

Enter "E2E Preventive Maintenance Cost" into the Cost Code Name field.


![TC-03.5 — Fill Cost Code Name](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_08_FILL_CC.png)

**Step 9: TC-03.5 — Cost Code Created**

The cost code is saved and can be used in work orders and maintenance requests for expense categorization.


![TC-03.5 — Cost Code Created](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_09_SAVE_CC.png)

**Step 10: TC-03.5 — Cost Code Detail**

The cost code detail page shows the code, description, and category used for financial reporting.


![TC-03.5 — Cost Code Detail](test-artifacts/screenshots/TC-03-financial-master-data__TC03_FIN_10_VERIFY_CC.png)

---

### 9.4. TC 03 Manufacturer Model

Navigate to Manufacturer. Manufacturers are linked to assets and equipment to track the make and model of each item.

**Step 1: TC-03.3 — Manufacturer List**

Navigate to Manufacturer. Manufacturers are linked to assets and equipment to track the make and model of each item.


![TC-03.3 — Manufacturer List](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_01_NAV.png)

**Step 2: TC-03.3 — Manufacturer List View**

The Manufacturer list shows all registered manufacturers with names, countries, and contact information. Use filters to locate specific manufacturers.


![TC-03.3 — Manufacturer List View](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_02_LIST.png)

**Step 3: TC-03.3 — Open Manufacturer Record**

Click on a manufacturer record to view its details and associated models.


![TC-03.3 — Open Manufacturer Record](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_03_CLICK_FIRST.png)

**Step 4: TC-03.3 — Wait for Page Load**

Wait for all page components to finish loading and rendering.


![TC-03.3 — Wait for Page Load](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_04_WAIT.png)

**Step 5: TC-03.3 — Manufacturer Detail**

The manufacturer detail page shows the company name, country, and associated models. Models link a manufacturer to specific product lines used in asset tracking.


![TC-03.3 — Manufacturer Detail](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MFR_05_DETAIL.png)

**Step 6: TC-03.3 — Model List**

Navigate to Model. Models represent specific product lines from manufacturers and are linked to assets for detailed equipment tracking.


![TC-03.3 — Model List](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_01_NAV.png)

**Step 7: TC-03.3 — Model List View**

The Model list shows all registered product models with names, linked manufacturers, and associated asset counts.


![TC-03.3 — Model List View](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_02_LIST.png)

**Step 8: TC-03.3 — Open Model Record**

Click on a model record to view its details and the linked manufacturer.


![TC-03.3 — Open Model Record](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_03_CLICK_FIRST.png)

**Step 9: TC-03.3 — Wait for Page Load**

Wait for all page components to finish loading and rendering.


![TC-03.3 — Wait for Page Load](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_04_WAIT.png)

**Step 10: TC-03.3 — Model Detail**

The model detail page shows the model name, linked manufacturer, and any associated assets.


![TC-03.3 — Model Detail](test-artifacts/screenshots/TC-03-manufacturer-model__TC03_MODEL_05_DETAIL.png)

---

### 9.5. TC 03 Master Data Organization

Navigate to Organization in the sidebar. This page shows all registered organizations. Organizations are the top level of the hierarchy: Organization → Site → Department.

**Step 1: TC-03.1 — Organization List**

Navigate to Organization in the sidebar. This page shows all registered organizations. Organizations are the top level of the hierarchy: Organization → Site → Department.


![TC-03.1 — Organization List](test-artifacts/screenshots/TC-03-master-data-organization__TC03_01_NAV_ORG.png)

**Step 2: TC-03.1 — Create Organization**

Click 'Add New' to create a new Organization. Fill in the name and other required fields.


![TC-03.1 — Create Organization](test-artifacts/screenshots/TC-03-master-data-organization__TC03_02_NEW_ORG.png)

**Step 3: TC-03.1 — Fill Organization Name**

Enter "E2E Test Corporation" into the Organization Name field.


![TC-03.1 — Fill Organization Name](test-artifacts/screenshots/TC-03-master-data-organization__TC03_03_FILL_ORG_NAME.png)

**Step 4: TC-03.1 — Organization Saved**

Click 'Create' to save the organization. A success notification confirms the record was created with an auto-generated ID.


![TC-03.1 — Organization Saved](test-artifacts/screenshots/TC-03-master-data-organization__TC03_04_SAVE_ORG.png)

**Step 5: TC-03.1 — Organization Detail**

The organization record is now saved. You can see the auto-generated ID and all fields. Navigate to Site to create sites linked to this organization.


![TC-03.1 — Organization Detail](test-artifacts/screenshots/TC-03-master-data-organization__TC03_05_VERIFY_ORG.png)

---

### 9.6. TC 03 Master Data Site

Navigate to Site. Sites represent physical locations within an organization. Each site can have multiple departments.

**Step 1: TC-03.1 — Site List**

Navigate to Site. Sites represent physical locations within an organization. Each site can have multiple departments.


![TC-03.1 — Site List](test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_01_NAV.png)

**Step 2: TC-03.1 — Create Site**

Click 'Add New' to create a new site. Link the site to the organization created in the previous step.


![TC-03.1 — Create Site](test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_02_NEW.png)

**Step 3: TC-03.1 — Fill Site Name**

Enter "E2E Site A" into the Site Name field.


![TC-03.1 — Fill Site Name](test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_03_FILL_NAME.png)

**Step 4: TC-03.1 — Site Saved**

The site is created with an auto-generated ID and linked to the organization. Repeat this process to create additional sites.


![TC-03.1 — Site Saved](test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_04_SAVE.png)

**Step 5: TC-03.1 — Site Detail View**

The site record shows the name, organization link, and any child departments. Each site serves as a scope boundary for role-based access control.


![TC-03.1 — Site Detail View](test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_05_VERIFY.png)

---

### 9.7. TC 03 Vendor Item

Navigate to Vendor. Vendors supply materials, spare parts, and services. Their performance is tracked automatically based on purchase receipts.

**Step 1: TC-03 — Vendor List**

Navigate to Vendor. Vendors supply materials, spare parts, and services. Their performance is tracked automatically based on purchase receipts.


![TC-03 — Vendor List](test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_01_NAV.png)

**Step 2: TC-03 — Add New**

Click the Add New button to open the creation form.


![TC-03 — Add New](test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_02_NEW.png)

**Step 3: TC-03 — Fill Vendor Name**

Enter "E2E Vendor — Industrial Parts Co." into the Vendor Name field.


![TC-03 — Fill Vendor Name](test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_03_FILL.png)

**Step 4: TC-03 — Vendor Created**

The vendor record is created. Performance ratings (delivery, quality, overall) are auto-calculated from purchase receipts. A new vendor starts with default/zero ratings.


![TC-03 — Vendor Created](test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_04_SAVE.png)

**Step 5: TC-03 — Vendor Detail**

The vendor detail shows contact information, performance ratings, and linked purchase orders. Ratings update automatically when purchase receipts are processed.


![TC-03 — Vendor Detail](test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_05_VERIFY.png)

**Step 6: TC-03 — Item (Inventory) List**

Navigate to Item. Items represent materials, spare parts, and consumables tracked in inventory. They are used in purchase requests, purchase orders, and work order parts.


![TC-03 — Item (Inventory) List](test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_06_NAV.png)

**Step 7: TC-03 — Add New**

Click the Add New button to open the creation form.


![TC-03 — Add New](test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_07_NEW.png)

**Step 8: TC-03 — Fill Description**

Enter "E2E Bearing SKF 6206" into the Description field.


![TC-03 — Fill Description](test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_08_FILL.png)

**Step 9: TC-03 — Item Created**

The item is created with its name and default properties. Items track stock levels, reorder points, and are linked to stores for inventory management.


![TC-03 — Item Created](test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_09_SAVE.png)

**Step 10: TC-03 — Item Detail**

The item detail view shows name, unit of measure, stock levels, reorder point, and storage locations. Items are referenced in PR lines, PO lines, and WO parts.


![TC-03 — Item Detail](test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_10_VERIFY.png)

---

### 9.8. TC 03 Work Schedule Holiday

Navigate to Work Schedule. Work schedules define standard working hours, shifts, and availability for maintenance planning.

**Step 1: TC-03.4 — Work Schedule List**

Navigate to Work Schedule. Work schedules define standard working hours, shifts, and availability for maintenance planning.


![TC-03.4 — Work Schedule List](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_01_NAV.png)

**Step 2: TC-03.4 — New Work Schedule**

Click 'Add New' to create a work schedule. Define the schedule name, working days, and shift hours.


![TC-03.4 — New Work Schedule](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_02_NEW.png)

**Step 3: TC-03.4 — Fill Schedule Name**

Enter "E2E Standard 5-Day Schedule" into the Schedule Name field.


![TC-03.4 — Fill Schedule Name](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_03_FILL.png)

**Step 4: TC-03.4 — Work Schedule Created**

The work schedule is saved and can be linked to employees, sites, and maintenance planning calendars.


![TC-03.4 — Work Schedule Created](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_04_SAVE.png)

**Step 5: TC-03.4 — Work Schedule Detail**

The work schedule detail shows the schedule name, working days, shift times, and associated resources.


![TC-03.4 — Work Schedule Detail](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_WS_05_VERIFY.png)

**Step 6: TC-03.4 — Holiday List**

Navigate to Holiday. Holidays define non-working days that affect SLA calculations and maintenance scheduling.


![TC-03.4 — Holiday List](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_01_NAV.png)

**Step 7: TC-03.4 — New Holiday**

Click 'Add New' to create a holiday entry. Specify the holiday name and date.


![TC-03.4 — New Holiday](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_02_NEW.png)

**Step 8: TC-03.4 — Fill Holiday Name**

Enter "E2E Test Holiday" into the Holiday Name field.


![TC-03.4 — Fill Holiday Name](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_03_FILL.png)

**Step 9: TC-03.4 — Holiday Created**

The holiday is saved and will be excluded from SLA calculations and work day computations.


![TC-03.4 — Holiday Created](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_04_SAVE.png)

**Step 10: TC-03.4 — Holiday Detail**

The holiday detail shows the name, date, and associated work schedules affected by this holiday.


![TC-03.4 — Holiday Detail](test-artifacts/screenshots/TC-03-work-schedule-holiday__TC03_HOL_05_VERIFY.png)

---

### 9.9. TC 19 Vendor Performance

Navigate to Vendor. Vendor performance metrics are automatically calculated from purchase receipt delivery data.

**Step 1: TC-19.1 — Vendor List**

Navigate to Vendor. Vendor performance metrics are automatically calculated from purchase receipt delivery data.


![TC-19.1 — Vendor List](test-artifacts/screenshots/TC-19-vendor-performance__TC19_01_NAV.png)

**Step 2: TC-19.1 — Vendor Performance Overview**

The vendor list shows all vendors with their delivery rating, on-time deliveries, late deliveries, quality score, and total orders processed.


![TC-19.1 — Vendor Performance Overview](test-artifacts/screenshots/TC-19-vendor-performance__TC19_02_SCREENSHOT_LIST.png)

**Step 3: TC-19.1 — New Vendor**

Click 'Add New' to create a vendor. Enter vendor name, contact details, and payment terms. Performance metrics will be calculated automatically as purchase receipts are recorded.


![TC-19.1 — New Vendor](test-artifacts/screenshots/TC-19-vendor-performance__TC19_03_NEW.png)

**Step 4: TC-19.1 — Fill Vendor Name**

Enter "E2E Performance Test Vendor" into the Vendor Name field.


![TC-19.1 — Fill Vendor Name](test-artifacts/screenshots/TC-19-vendor-performance__TC19_04_FILL.png)

**Step 5: TC-19.1 — Vendor Created**

The vendor is created with initial performance metrics at zero. As PO receipts are processed, delivery_rating, on_time_deliveries, late_deliveries, and quality_rating are updated automatically.


![TC-19.1 — Vendor Created](test-artifacts/screenshots/TC-19-vendor-performance__TC19_05_SAVE.png)

**Step 6: TC-19.1 — Vendor Detail & Metrics**

The vendor detail page shows contact information, payment terms, and the performance metrics section with delivery rating formula: on_time_deliveries / total_orders × 100.


![TC-19.1 — Vendor Detail & Metrics](test-artifacts/screenshots/TC-19-vendor-performance__TC19_06_VERIFY.png)

---

## 10. Purchasing & Stores

### 10.1. TC 11 Blanket Contract Po

Navigate to Purchase Order. PO types include Standard (one-time), Blanket (spending limit), and Contract (date range).

**Step 1: TC-11.3 — Purchase Order List**

Navigate to Purchase Order. PO types include Standard (one-time), Blanket (spending limit), and Contract (date range).


![TC-11.3 — Purchase Order List](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_01_NAV.png)

**Step 2: TC-11.3 — Purchase Order Overview**

The purchase order list displays all POs with their type, vendor, status, and total amount. Filter by PO type to view specific categories.


![TC-11.3 — Purchase Order Overview](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_02_SCREENSHOT.png)

**Step 3: TC-11.3 — New Blanket PO Form**

Create a new purchase order. Select PO Type = 'Blanket' to create a blanket order with a spending limit. The Blanket Limit and Released Amount fields appear for this type.


![TC-11.3 — New Blanket PO Form](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_03_NEW.png)

**Step 4: TC-11.3 — Blanket PO Form Fields**

The blanket PO form shows type-specific fields: Blanket Limit (maximum spending), Released Amount (amount already released), and vendor selection. These fields control spending authorization.


![TC-11.3 — Blanket PO Form Fields](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_04_SCREENSHOT.png)

**Step 5: TC-11.3 — Blanket PO Created**

The blanket purchase order is created in Draft state. Approve to make it active. Releases against this PO are tracked against the spending limit.


![TC-11.3 — Blanket PO Created](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_05_SAVE.png)

**Step 6: TC-11.3 — Blanket PO Detail**

The blanket PO detail shows the spending limit, released amount, remaining balance, and associated release orders.


![TC-11.3 — Blanket PO Detail](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_BPO_06_VERIFY.png)

**Step 7: TC-11.4 — New Contract PO Form**

Create another purchase order. Select PO Type = 'Contract' to create a contract-based order with start and end dates.


![TC-11.4 — New Contract PO Form](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_CPO_01_NAV.png)

**Step 8: TC-11.4 — Contract PO Form Fields**

The contract PO form shows type-specific fields: Contract Start Date, Contract End Date, and terms. These control the validity period of the procurement agreement.


![TC-11.4 — Contract PO Form Fields](test-artifacts/screenshots/TC-11-blanket-contract-po__TC11_CPO_02_SCREENSHOT.png)

---

### 10.2. TC 11 Purchase Receipt

Navigate to Purchase Receipt. Receipts record the delivery of goods against purchase orders and trigger vendor performance calculations.

**Step 1: TC-11.6 — Purchase Receipt List**

Navigate to Purchase Receipt. Receipts record the delivery of goods against purchase orders and trigger vendor performance calculations.


![TC-11.6 — Purchase Receipt List](test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_01_NAV.png)

**Step 2: TC-11.6 — Receipt List Overview**

The purchase receipt list shows all received deliveries with their PO reference, vendor, received date, and status.


![TC-11.6 — Receipt List Overview](test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_02_SCREENSHOT.png)

**Step 3: TC-11.6 — New Purchase Receipt**

Click 'Add New' to record a receipt. Link it to a purchase order, enter received quantities, and note any discrepancies.


![TC-11.6 — New Purchase Receipt](test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_03_NEW.png)

**Step 4: TC-11.6 — Receipt Form**

The purchase receipt form includes PO reference, vendor, delivery date, received items, quantities, and condition notes. Complete receipts update inventory and vendor performance metrics.


![TC-11.6 — Receipt Form](test-artifacts/screenshots/TC-11-purchase-receipt__TC11_REC_04_SCREENSHOT.png)

---

### 10.3. TC 11 Purchasing Pr Po

Navigate to Purchasing → Purchase Request. Purchase requests initiate procurement for materials, spare parts, and services needed for maintenance.

**Step 1: TC-11.1 — Purchase Request List**

Navigate to Purchasing → Purchase Request. Purchase requests initiate procurement for materials, spare parts, and services needed for maintenance.


![TC-11.1 — Purchase Request List](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_01_NAV_PR.png)

**Step 2: TC-11.1 — New Purchase Request**

Click 'Add New' to create a purchase request. Specify the requestor, due date, site, and department. Add line items with quantities and unit prices.


![TC-11.1 — New Purchase Request](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_02_NEW_PR.png)

**Step 3: TC-11 — Fill Pr Description**

Enter "E2E Test — Spare parts for pump maintena" into the Pr Description field.


![TC-11 — Fill Pr Description](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_03_FILL_PR.png)

**Step 4: TC-11.1 — PR Created (Draft)**

The purchase request is created with an auto-generated ID (e.g., PR-00001) in 'Draft' state. Add line items, then submit for approval.


![TC-11.1 — PR Created (Draft)](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_04_SAVE_PR.png)

**Step 5: TC-11.1 — Purchase Request Detail**

The purchase request detail shows requestor, due date, and line items. The PR Lines child table allows adding items with quantities, unit prices, and calculated line totals.


![TC-11.1 — Purchase Request Detail](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_05_VERIFY_PR.png)

**Step 6: TC-11.2 — Purchase Order List**

Navigate to Purchasing → Purchase Order. Purchase orders are issued to vendors based on approved purchase requests. PO types include Standard, Blanket, and Contract.


![TC-11.2 — Purchase Order List](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_06_NAV_PO.png)

**Step 7: TC-11.2 — New Purchase Order**

Click 'Add New' to create a purchase order. Select the vendor, PO type, site, and department. Add line items matching the approved PR.


![TC-11.2 — New Purchase Order](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_07_NEW_PO.png)

**Step 8: TC-11.2 — PO New Form**

The new purchase order form shows fields for vendor, PO type, site, department, and financial details. Select a vendor to link the PO to approved purchase requests.


![TC-11.2 — PO New Form](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_08_FILL_PO.png)

**Step 9: TC-11.2 — PO Created (Draft)**

The purchase order is created with an auto-generated ID (e.g., PO-00001) in 'Draft' state. The form is editable in Draft. After approval, the form becomes read-only.


![TC-11.2 — PO Created (Draft)](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_09_SAVE_PO.png)

**Step 10: TC-11.2 — Purchase Order Detail**

The purchase order detail shows vendor, PO type, terms, and line items. Supported PO types: Standard (one-time), Blanket (spending limit), and Contract (date range). The workflow moves through Draft → Open → Closed.


![TC-11.2 — Purchase Order Detail](test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_10_VERIFY_PO.png)

---

### 10.4. Purchase Request Lifecycle

Navigate to the Purchase Request list page. Purchase requests initiate the procurement workflow for materials, spare parts, and services.

**Step 1: Purchase Request List**

Navigate to the Purchase Request list page. Purchase requests initiate the procurement workflow for materials, spare parts, and services.


![Purchase Request List](test-artifacts/screenshots/purchase-request-lifecycle__PR_01_NAVIGATE.png)

**Step 2: Create New Purchase Request**

Click 'Add New' to create a new purchase request. Fill in the required fields such as description and requested items.


![Create New Purchase Request](test-artifacts/screenshots/purchase-request-lifecycle__PR_02_NEW.png)

**Step 3: Fill Form Field**

Enter "E2E Test — Spare parts for pump maintena" into the Pr Description field.


![Fill Form Field](test-artifacts/screenshots/purchase-request-lifecycle__PR_03_FILL_DESCRIPTION.png)

**Step 4: Save Purchase Request**

Click 'Save' to create the purchase request. It will start in Draft state and can be submitted for approval.


![Save Purchase Request](test-artifacts/screenshots/purchase-request-lifecycle__PR_04_SAVE.png)

**Step 5: Purchase Request Details**

The purchase request is now saved. Use the workflow dropdown to submit it for approval.


![Purchase Request Details](test-artifacts/screenshots/purchase-request-lifecycle__PR_05_VERIFY_SAVED.png)

---

## 11. Work Management

### 11.1. TC 07 Work Order Child Records

Navigate to Work Order. Work orders contain child records for labor, parts, and equipment tracking.

**Step 1: TC-07.3 — Work Order List**

Navigate to Work Order. Work orders contain child records for labor, parts, and equipment tracking.


![TC-07.3 — Work Order List](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_CHILD_01_NAV.png)

**Step 2: TC-07.3 — Work Order List Overview**

The work order list shows all work orders with their status, priority, type, and assigned resources.


![TC-07.3 — Work Order List Overview](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_CHILD_02_SCREENSHOT.png)

**Step 3: TC-07.3 — Work Order Labor List**

Navigate to Work Order Labor. Labor records track hours spent by technicians on each work order.


![TC-07.3 — Work Order Labor List](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_01_NAV.png)

**Step 4: TC-07.3 — New Labor Entry**

Click 'Add New' to record labor hours. Specify the employee, hours worked, hourly rate, and trade type.


![TC-07.3 — New Labor Entry](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_02_NEW.png)

**Step 5: TC-07.3 — Labor Entry Form**

The labor entry form captures employee, hours, rate, and total cost. The system calculates the line total (hours × rate) automatically.


![TC-07.3 — Labor Entry Form](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_LABOR_03_SCREENSHOT.png)

**Step 6: TC-07.3 — Work Order Parts List**

Navigate to Work Order Parts. Parts records track materials and spare parts consumed during maintenance work.


![TC-07.3 — Work Order Parts List](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_01_NAV.png)

**Step 7: TC-07.3 — New Parts Entry**

Click 'Add New' to record parts consumed. Select the item, quantity, and unit price.


![TC-07.3 — New Parts Entry](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_02_NEW.png)

**Step 8: TC-07.3 — Parts Entry Form**

The parts entry form captures item, quantity, unit price, and calculated total. Parts consumption is deducted from inventory when the work order is completed.


![TC-07.3 — Parts Entry Form](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_PARTS_03_SCREENSHOT.png)

**Step 9: TC-07.3 — Work Order Equipment List**

Navigate to Work Order Equipment. Equipment records track tools and vehicles used during work order execution.


![TC-07.3 — Work Order Equipment List](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_EQUIP_01_NAV.png)

**Step 10: TC-07.3 — Work Order Equipment Overview**

The work order equipment list shows all equipment assigned to work orders with usage hours and associated costs.


![TC-07.3 — Work Order Equipment Overview](test-artifacts/screenshots/TC-07-work-order-child-records__TC07_EQUIP_02_SCREENSHOT.png)

---

### 11.2. TC 07 Wo Failure Reporting

Navigate to Failure Analysis. Failure analysis records document root causes, remedies, and risk priority numbers (RPN) for equipment failures.

**Step 1: TC-07.5 — Failure Analysis List**

Navigate to Failure Analysis. Failure analysis records document root causes, remedies, and risk priority numbers (RPN) for equipment failures.


![TC-07.5 — Failure Analysis List](test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_01_NAV.png)

**Step 2: TC-07.5 — Failure Analysis List View**

The Failure Analysis list shows all failure records with failure modes, cause codes, severity ratings, and RPN scores. Filter by asset or date range.


![TC-07.5 — Failure Analysis List View](test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_02_LIST.png)

**Step 3: TC-07.5 — Open Failure Analysis**

Click on a failure analysis record to view its details including failure mode, cause, severity, occurrence, and detection ratings.


![TC-07.5 — Open Failure Analysis](test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_03_CLICK_FIRST.png)

**Step 4: TC-07.5 — Wait for Page Load**

Wait for all page components to finish loading and rendering.


![TC-07.5 — Wait for Page Load](test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_04_WAIT.png)

**Step 5: TC-07.5 — Failure Analysis Detail**

The failure analysis detail shows failure mode, cause code, remedy code, severity/occurrence/detection ratings, and RPN score. Server actions enable 5-Why and Fishbone templates.


![TC-07.5 — Failure Analysis Detail](test-artifacts/screenshots/TC-07-wo-failure-reporting__TC07_FAIL_05_DETAIL.png)

---

### 11.3. TC 07 Work Order

Navigate to Work Management → Work Order. Work orders track maintenance tasks from request through completion, including labor, parts, and costs.

**Step 1: TC-07.1 — Work Order List**

Navigate to Work Management → Work Order. Work orders track maintenance tasks from request through completion, including labor, parts, and costs.


![TC-07.1 — Work Order List](test-artifacts/screenshots/TC-07-work-order__TC07_01_NAV.png)

**Step 2: TC-07.1 — New Work Order**

Click 'Add New' to create a new work order. Fill in the type, description, priority, site, department, asset, and due date.


![TC-07.1 — New Work Order](test-artifacts/screenshots/TC-07-work-order__TC07_02_NEW.png)

**Step 3: TC-07.1 — Fill Description**

Enter "E2E Test — Repair excessive vibration on" into the Description field.


![TC-07.1 — Fill Description](test-artifacts/screenshots/TC-07-work-order__TC07_03_FILL_DESC.png)

**Step 4: TC-07.1 — WO Created (Requested)**

The work order is created with an auto-generated ID (e.g., WO-00001) in the 'Requested' state. Use the workflow dropdown to approve and start the work order.


![TC-07.1 — WO Created (Requested)](test-artifacts/screenshots/TC-07-work-order__TC07_04_SAVE.png)

**Step 5: TC-07.1 — Work Order Detail**

The work order detail page shows all fields organized in tabs: Details, Labor, Equipment, Parts, Activities, and Attachments. The header shows the workflow state and available transitions.


![TC-07.1 — Work Order Detail](test-artifacts/screenshots/TC-07-work-order__TC07_05_VERIFY.png)

---

### 11.4. TC 08 Work Order Activity

Navigate to Work Order Activity. Activities are individual tasks within a work order that can be assigned to different technicians and tracked independently.

**Step 1: TC-08.1 — Work Order Activity List**

Navigate to Work Order Activity. Activities are individual tasks within a work order that can be assigned to different technicians and tracked independently.


![TC-08.1 — Work Order Activity List](test-artifacts/screenshots/TC-08-work-order-activity__TC08_01_NAV.png)

**Step 2: TC-08.1 — Activity List Overview**

The activity list shows all work order activities with their status, assigned worker, and parent work order. Activities progress through: Awaiting Resources → Ready → In Progress → On Hold → Complete → Closed.


![TC-08.1 — Activity List Overview](test-artifacts/screenshots/TC-08-work-order-activity__TC08_02_SCREENSHOT.png)

**Step 3: TC-08.1 — New Activity**

Click 'Add New' to create a work order activity. Link it to a parent work order, assign a worker, and specify the task description.


![TC-08.1 — New Activity](test-artifacts/screenshots/TC-08-work-order-activity__TC08_03_NEW.png)

**Step 4: TC-08.1 — Fill Description**

Enter "E2E Bearing replacement — Motor Assembly" into the Description field.


![TC-08.1 — Fill Description](test-artifacts/screenshots/TC-08-work-order-activity__TC08_04_FILL.png)

**Step 5: TC-08.1 — Activity Created**

The activity is created in 'Awaiting Resources' state. Allocate resources to move it to 'Ready', then start work to move to 'In Progress'.


![TC-08.1 — Activity Created](test-artifacts/screenshots/TC-08-work-order-activity__TC08_05_SAVE.png)

**Step 6: TC-08.1 — Activity Detail**

The activity detail page shows the task description, assigned worker, parent work order, estimated hours, and workflow state. Use the workflow dropdown to progress the activity through its lifecycle.


![TC-08.1 — Activity Detail](test-artifacts/screenshots/TC-08-work-order-activity__TC08_06_VERIFY.png)

---

### 11.5. Work Order Lifecycle

Navigate to the Work Order list page. This page displays all work orders with their current workflow status, priority, and assigned personnel.

**Step 1: Work Order List**

Navigate to the Work Order list page. This page displays all work orders with their current workflow status, priority, and assigned personnel.


![Work Order List](test-artifacts/screenshots/work-order-lifecycle__WO_01_NAVIGATE.png)

**Step 2: Create New Work Order**

Click 'Add New' to create a new work order. The form opens with default values including the 'Requested' workflow state.


![Create New Work Order](test-artifacts/screenshots/work-order-lifecycle__WO_02_NEW.png)

**Step 3: Fill Form Field**

Enter "E2E Test Work Order — Pump maintenance" into the Description field.


![Fill Form Field](test-artifacts/screenshots/work-order-lifecycle__WO_03_FILL_DESCRIPTION.png)

**Step 4: Save Work Order**

Click 'Save' to create the work order. The system assigns a unique code and sets the initial workflow state.


![Save Work Order](test-artifacts/screenshots/work-order-lifecycle__WO_04_SAVE.png)

**Step 5: Work Order Initial State**

After saving, the work order is in the initial workflow state. The workflow dropdown in the header shows available transitions.


![Work Order Initial State](test-artifacts/screenshots/work-order-lifecycle__WO_05_VERIFY_STATE.png)

---

## 12. Safety Permits

### 12.1. TC 09 Safety Permit Lifecycle

Navigate to Safety Permit. Safety permits ensure proper authorization before hazardous maintenance tasks. Permit types include LOTO, Hot Work, Confined Space, Excavation, Working at Height, and Electrical.

**Step 1: TC-09.1 — Safety Permit List**

Navigate to Safety Permit. Safety permits ensure proper authorization before hazardous maintenance tasks. Permit types include LOTO, Hot Work, Confined Space, Excavation, Working at Height, and Electrical.


![TC-09.1 — Safety Permit List](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_01_NAV.png)

**Step 2: TC-09.1 — Safety Permit Overview**

The safety permit list shows all permits with their type, status, valid dates, and linked work orders. Color-coded status badges indicate the current lifecycle state.


![TC-09.1 — Safety Permit Overview](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_02_SCREENSHOT.png)

**Step 3: TC-09.1 — New Safety Permit Form**

The safety permit form includes fields for permit type, work order link, hazards identified, precautions required, PPE requirements, and emergency contact information.


![TC-09.1 — New Safety Permit Form](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_03_NEW.png)

**Step 4: TC-09.1 — Fill Hazards Identified**

Enter "E2E Lifecycle Test — Electrical hazard, " into the Hazards Identified field.


![TC-09.1 — Fill Hazards Identified](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_04_FILL_TYPE.png)

**Step 5: TC-09.1 — Permit Created (Draft)**

The safety permit is created in 'Draft' state. The workflow progresses: Draft → Submit Request → Requested → Approve → Approved → Activate → Active → Expire → Expired → Renew → Draft.


![TC-09.1 — Permit Created (Draft)](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_05_SAVE.png)

**Step 6: TC-09.1 — Safety Permit Detail**

The safety permit detail page shows all safety-related fields, the workflow state badge, and available transition actions. The permit must be approved by a safety officer before activation.


![TC-09.1 — Safety Permit Detail](test-artifacts/screenshots/TC-09-safety-permit-lifecycle__TC09_LC_06_VERIFY.png)

---

### 12.2. TC 09 Safety Permit

Navigate to Safety Permit. Safety permits control access to hazardous work areas and ensure proper safety procedures are followed before maintenance tasks begin.

**Step 1: TC-09.1 — Safety Permit List**

Navigate to Safety Permit. Safety permits control access to hazardous work areas and ensure proper safety procedures are followed before maintenance tasks begin.


![TC-09.1 — Safety Permit List](test-artifacts/screenshots/TC-09-safety-permit__TC09_01_NAV.png)

**Step 2: TC-09.1 — New Safety Permit**

Click 'Add New' to create a new safety permit. Select the permit type (LOTO, Hot Work, Confined Space, etc.), link it to a work order, and specify hazards and precautions.


![TC-09.1 — New Safety Permit](test-artifacts/screenshots/TC-09-safety-permit__TC09_02_NEW.png)

**Step 3: TC-09.1 — Fill Hazards Identified**

Enter "E2E Test — Identify electrical hazards" into the Hazards Identified field.


![TC-09.1 — Fill Hazards Identified](test-artifacts/screenshots/TC-09-safety-permit__TC09_03_FILL_DESC.png)

**Step 4: TC-09.1 — Safety Permit Created (Draft)**

The safety permit is created with an auto-generated ID (e.g., SP-00001) in 'Draft' state. Submit the request for approval by the safety officer.


![TC-09.1 — Safety Permit Created (Draft)](test-artifacts/screenshots/TC-09-safety-permit__TC09_04_SAVE.png)

**Step 5: TC-09.1 — Safety Permit Detail**

The safety permit detail page shows permit type, valid dates, hazards, precautions, and emergency procedures. The workflow tracks the permit through its approval and activation lifecycle.


![TC-09.1 — Safety Permit Detail](test-artifacts/screenshots/TC-09-safety-permit__TC09_05_VERIFY.png)

---

## 13. Troubleshooting

This section covers common issues observed during testing.

### Empty Credentials Error

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.


![Empty Credentials Error](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_02_EMPTY_SUBMIT.png)

> *Show the validation error that appears when submitting the login form with empty fields.*

### Invalid Credentials Error

If you enter an incorrect username or password, the system displays an error message. Verify your credentials and try again. After multiple failed attempts, your account may be temporarily locked.


![Invalid Credentials Error](test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_05_WRONG_PASSWORD_SUBMIT.png)

> *Capture the error message displayed after failed login. This goes in the Troubleshooting section.*


---
*This manual was auto-generated by the Dual-Purpose Automation Framework.*