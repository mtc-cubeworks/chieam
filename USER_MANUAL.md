# EAM System — User Manual

> Auto-generated from 90 screenshots across 21 workflows.
> Generated at: 2026-04-10T01:29:54.919Z

## Table of Contents

1. [Asset Management](#asset-management)
   1.1. [TC 04 Asset Create](#tc-04-asset-create)
   1.2. [Asset Lifecycle](#asset-lifecycle)
2. [Condition Monitoring](#condition-monitoring)
   2.1. [TC 10 Condition Monitoring](#tc-10-condition-monitoring)
3. [Authentication](#authentication)
   3.1. [TC 01 Authentication](#tc-01-authentication)
   3.2. [Login Edge Cases](#login-edge-cases)
   3.3. [Login Happy Path](#login-happy-path)
4. [Dashboard](#dashboard)
   4.1. [Dashboard Overview](#dashboard-overview)
5. [General Features](#general-features)
   5.1. [Entity List Features](#entity-list-features)
6. [Navigation](#navigation)
   6.1. [Sidebar Navigation](#sidebar-navigation)
7. [Maintenance](#maintenance)
   7.1. [TC 06 Maintenance Request](#tc-06-maintenance-request)
   7.2. [Maintenance Request Lifecycle](#maintenance-request-lifecycle)
8. [Master Data](#master-data)
   8.1. [TC 03 Master Data Department](#tc-03-master-data-department)
   8.2. [TC 03 Employee Labor](#tc-03-employee-labor)
   8.3. [TC 03 Master Data Organization](#tc-03-master-data-organization)
   8.4. [TC 03 Master Data Site](#tc-03-master-data-site)
   8.5. [TC 03 Vendor Item](#tc-03-vendor-item)
9. [Purchasing & Stores](#purchasing-&-stores)
   9.1. [TC 11 Purchasing Pr Po](#tc-11-purchasing-pr-po)
   9.2. [Purchase Request Lifecycle](#purchase-request-lifecycle)
10. [Work Management](#work-management)
   10.1. [TC 07 Work Order](#tc-07-work-order)
   10.2. [Work Order Lifecycle](#work-order-lifecycle)
11. [Safety Permits](#safety-permits)
   11.1. [TC 09 Safety Permit](#tc-09-safety-permit)
12. [Troubleshooting](#troubleshooting)

---

## 1. Asset Management

### 1.1. TC 04 Asset Create

Navigate to Asset Management → Asset. The asset list shows all registered assets with their current lifecycle state, site, and criticality.

**Step 1: TC-04.1 — Asset List**

Navigate to Asset Management → Asset. The asset list shows all registered assets with their current lifecycle state, site, and criticality.


![TC-04.1 — Asset List](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_01_NAV.png)

**Step 2: TC-04.1 — New Asset Form**

Click 'Add New' to open the asset creation form. The form includes fields for description, asset class, site, department, manufacturer, and more.


![TC-04.1 — New Asset Form](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_02_NEW.png)

**Step 3: TC-04.1 — Asset Created**

Click 'Create' to save the asset. The system assigns an auto-generated ID (e.g., A-00001) and sets the initial workflow state to 'Acquired'.


![TC-04.1 — Asset Created](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_04_SAVE.png)

**Step 4: TC-04.1 — Asset Detail View**

The asset detail page shows all fields organized in tabs. The workflow state badge in the header indicates the current lifecycle state. Use the workflow dropdown to transition the asset through its lifecycle.


![TC-04.1 — Asset Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-04-asset-create__TC04_05_VERIFY_STATE.png)

---

### 1.2. Asset Lifecycle

Navigate to the Asset list page by clicking 'Asset' in the sidebar or visiting /asset. This page shows all registered assets in a data table with search, filter, and sort capabilities.

**Step 1: Asset List**

Navigate to the Asset list page by clicking 'Asset' in the sidebar or visiting /asset. This page shows all registered assets in a data table with search, filter, and sort capabilities.


![Asset List](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_01_NAVIGATE.png)

**Step 2: Create New Asset**

Click 'Add New' in the top-right corner to open the asset creation form. You will be redirected to a blank form where you can enter the asset details.


![Create New Asset](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_02_NEW.png)

**Step 3: Asset Form Filled**

Fill in the asset details. The 'Description' field is the primary identifier. Additional fields can be filled as needed.


![Asset Form Filled](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_04_FILL_DESCRIPTION.png)

**Step 4: Save New Asset**

After filling in the required fields, click 'Save' to create the asset record. A success notification appears confirming the asset was created.


![Save New Asset](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_05_SAVE.png)

**Step 5: Asset Details View**

After saving, you are taken to the asset detail page where you can view all fields, switch tabs, and manage workflow state.


![Asset Details View](eam-chi/frontend/test-artifacts/screenshots/asset-lifecycle__ASSET_06_VERIFY_SAVED.png)

---

## 2. Condition Monitoring

### 2.1. TC 10 Condition Monitoring

Navigate to Condition Monitoring. This module tracks real-time sensor data and condition indicators for assets, with configurable warning and critical thresholds.

**Step 1: TC-10.1 — Condition Monitoring List**

Navigate to Condition Monitoring. This module tracks real-time sensor data and condition indicators for assets, with configurable warning and critical thresholds.


![TC-10.1 — Condition Monitoring List](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_01_NAV.png)

**Step 2: TC-10.1 — New Condition Monitor**

Click 'Add New' to set up condition monitoring for an asset. Define the monitoring type (Vibration, Temperature, Pressure, etc.), baseline value, and warning/critical thresholds.


![TC-10.1 — New Condition Monitor](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_02_NEW.png)

**Step 3: TC-10.1 — Condition Monitor Created**

The condition monitoring record is created in 'Active' state. As readings are taken, the system automatically transitions to Warning or Critical states based on threshold values.


![TC-10.1 — Condition Monitor Created](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_04_SAVE.png)

**Step 4: TC-10.1 — Condition Monitoring Detail**

The detail view shows the asset, monitoring type, baseline value, thresholds, current reading, alert status, and trend direction. The workflow state reflects the current alert level.


![TC-10.1 — Condition Monitoring Detail](eam-chi/frontend/test-artifacts/screenshots/TC-10-condition-monitoring__TC10_05_VERIFY.png)

---

## 3. Authentication

### 3.1. TC 01 Authentication

Navigate to the login page. The login form displays with Username and Password fields, along with the organization branding (logo and name).

**Step 1: TC-01.1 — Login Page**

Navigate to the login page. The login form displays with Username and Password fields, along with the organization branding (logo and name).


![TC-01.1 — Login Page](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_01_LOGIN_PAGE.png)

**Step 2: TC-01.1 — Successful Login**

After entering valid credentials and clicking 'Sign In', you are redirected to the Home page. The sidebar displays navigation items based on your role permissions.


![TC-01.1 — Successful Login](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_04_SUBMIT.png)

**Step 3: TC-01.1 — Sidebar & Navigation**

The sidebar shows all available modules based on your role. Admin users can see all entities including Settings, Admin, Workflow, and Model Editor sections.


![TC-01.1 — Sidebar & Navigation](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_05_VERIFY_SIDEBAR.png)

**Step 4: TC-01.5 — User Menu**

Click your name/avatar at the bottom of the sidebar to open the user menu. From here you can access your Profile or Logout.


![TC-01.5 — User Menu](eam-chi/frontend/test-artifacts/screenshots/TC-01-authentication__TC01_06_PROFILE.png)

---

### 3.2. Login Edge Cases

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.

**Step 1: Empty Credentials Error**

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.


![Empty Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_02_EMPTY_SUBMIT.png)

**Step 2: Invalid Credentials Error**

If you enter an incorrect username or password, the system displays an error message. Verify your credentials and try again. After multiple failed attempts, your account may be temporarily locked.


![Invalid Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_05_WRONG_PASSWORD_SUBMIT.png)

---

### 3.3. Login Happy Path

Open the EAM application in your web browser. You will be presented with the login screen showing the organization branding and credential fields.

**Step 1: Login Page**

Open the EAM application in your web browser. You will be presented with the login screen showing the organization branding and credential fields.


![Login Page](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_01_NAVIGATE.png)

**Step 2: Enter Username**

Enter your username in the Username field. This is the account name provided by your system administrator.


![Enter Username](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_02_ENTER_USERNAME.png)

**Step 3: Enter Password**

Enter your password in the Password field. Passwords are case-sensitive.


![Enter Password](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_03_ENTER_PASSWORD.png)

**Step 4: Submit Login**

Click the 'Sign in' button. Upon successful authentication, you will be redirected to the home page.


![Submit Login](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_04_SUBMIT.png)

**Step 5: Home Page After Login**

After successful login, the main application loads with the sidebar navigation showing all available modules.


![Home Page After Login](eam-chi/frontend/test-artifacts/screenshots/login-happy-path__LOGIN_05_HOME_LOADED.png)

---

## 4. Dashboard

### 4.1. Dashboard Overview

The Dashboard provides a real-time overview of your asset management system. Navigate to the Dashboard by clicking 'Dashboard' in the left sidebar or by visiting /dashboard.

**Step 1: Dashboard Overview**

The Dashboard provides a real-time overview of your asset management system. Navigate to the Dashboard by clicking 'Dashboard' in the left sidebar or by visiting /dashboard.


![Dashboard Overview](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_01_NAVIGATE.png)

**Step 2: Key Performance Indicators**

Six KPI cards are displayed at the top: Total Assets, Work Orders, Overdue WOs, Inventory, Purchase Requests, and Incidents. Each card shows the current total and a secondary metric such as the count from the last 30 days.


![Key Performance Indicators](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_02_KPI_CARDS.png)

**Step 3: Refreshing Dashboard Data**

Click the 'Refresh' button in the top-right corner to reload all dashboard data from the server.


![Refreshing Dashboard Data](eam-chi/frontend/test-artifacts/screenshots/dashboard-overview__DASH_03_REFRESH.png)

---

## 5. General Features

### 5.1. Entity List Features

Entity list pages display records in a data table. They support search, column filtering, sorting, pagination, and multiple view modes (list, tree, diagram, hierarchy).

**Step 1: Entity List Page**

Entity list pages display records in a data table. They support search, column filtering, sorting, pagination, and multiple view modes (list, tree, diagram, hierarchy).


![Entity List Page](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_01_NAVIGATE.png)

**Step 2: Search Records**

Type in the search box to filter records. The table updates in real-time as you type. You can search across the selected filter field.


![Search Records](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_02_SEARCH.png)

**Step 3: Search Results**

The table displays only records matching your search term. The total count badge updates to reflect the filtered result count.


![Search Results](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_04_SEARCH_RESULTS.png)

**Step 4: Open Record Detail**

Click any row in the table to open the detail view for that record. You can view and edit all fields, manage attachments, and control the workflow state.


![Open Record Detail](eam-chi/frontend/test-artifacts/screenshots/entity-list-features__LIST_06_CLICK_ROW.png)

---

## 6. Navigation

### 6.1. Sidebar Navigation

The sidebar is always visible on the left side of the screen. It contains the organization logo, navigation links grouped by module, and user account controls at the bottom.

**Step 1: Application Sidebar**

The sidebar is always visible on the left side of the screen. It contains the organization logo, navigation links grouped by module, and user account controls at the bottom.


![Application Sidebar](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_01_HOME.png)

**Step 2: Navigate to Dashboard**

Click 'Dashboard' in the sidebar to view the system-wide KPI overview.


![Navigate to Dashboard](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_02_DASHBOARD.png)

**Step 3: Navigate to Assets**

Click 'Asset' under the Asset Management module to view the full list of registered assets.


![Navigate to Assets](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_03_ASSET.png)

**Step 4: Navigate to Work Orders**

Click 'Work Order' under the Work Management module to view and manage work orders. Expand the module group if it is collapsed.


![Navigate to Work Orders](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_04_WORK_ORDER.png)

**Step 5: Collapse Sidebar**

Click the hamburger menu icon in the header to collapse the sidebar. This gives you more horizontal space for data tables and forms. Click again to expand.


![Collapse Sidebar](eam-chi/frontend/test-artifacts/screenshots/sidebar-navigation__NAV_05_COLLAPSE.png)

---

## 7. Maintenance

### 7.1. TC 06 Maintenance Request

Navigate to Maintenance Request. Maintenance requests are used to report issues, request corrective maintenance, or schedule preventive maintenance tasks.

**Step 1: TC-06.1 — Maintenance Request List**

Navigate to Maintenance Request. Maintenance requests are used to report issues, request corrective maintenance, or schedule preventive maintenance tasks.


![TC-06.1 — Maintenance Request List](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_01_NAV.png)

**Step 2: TC-06.1 — New Maintenance Request**

Click 'Add New' to create a new maintenance request. Fill in the requestor, asset, priority, category, and description fields.


![TC-06.1 — New Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_02_NEW.png)

**Step 3: TC-06.1 — MR Created (Draft)**

The maintenance request is created with an auto-generated ID (e.g., MTREQ-00001) and workflow state 'Draft'. From here you can submit it for approval.


![TC-06.1 — MR Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_04_SAVE.png)

**Step 4: TC-06.1 — Maintenance Request Detail (Draft)**

The maintenance request is in Draft state. The workflow dropdown shows available transitions. Click 'Submit for Approval' to advance the request.


![TC-06.1 — Maintenance Request Detail (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-06-maintenance-request__TC06_05_VERIFY_DRAFT.png)

---

### 7.2. Maintenance Request Lifecycle

Navigate to the Maintenance Request list page. Maintenance requests are used to report issues and request corrective or preventive maintenance.

**Step 1: Maintenance Request List**

Navigate to the Maintenance Request list page. Maintenance requests are used to report issues and request corrective or preventive maintenance.


![Maintenance Request List](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_01_NAVIGATE.png)

**Step 2: Create New Maintenance Request**

Click 'Add New' to open the maintenance request form.


![Create New Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_02_NEW.png)

**Step 3: Save Maintenance Request**

Click 'Save' to submit the maintenance request. The system creates a draft record that can be moved through the approval workflow.


![Save Maintenance Request](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_04_SAVE.png)

**Step 4: Maintenance Request Details**

The maintenance request has been created. Review the details and use the workflow dropdown to advance the request through its lifecycle.


![Maintenance Request Details](eam-chi/frontend/test-artifacts/screenshots/maintenance-request-lifecycle__MR_05_VERIFY_SAVED.png)

---

## 8. Master Data

### 8.1. TC 03 Master Data Department

Navigate to Department. Departments are organizational units within a site, used for cost allocation and team-level data scoping.

**Step 1: TC-03.1 — Department List**

Navigate to Department. Departments are organizational units within a site, used for cost allocation and team-level data scoping.


![TC-03.1 — Department List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_01_NAV.png)

**Step 2: TC-03.1 — Department Saved**

The department is created and linked to its parent site. Departments are used for team-level data scoping (scope=team) in the RBAC system.


![TC-03.1 — Department Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_04_SAVE.png)

**Step 3: TC-03.1 — Hierarchy Complete**

With Organization → Site → Department created, the organizational hierarchy is established. This hierarchy is used for data scoping, cost allocation, and reporting.


![TC-03.1 — Hierarchy Complete](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-department__TC03_DEPT_05_VERIFY.png)

---

### 8.2. TC 03 Employee Labor

Navigate to Employee. Employees are linked to users, sites, and departments. They serve as requestors, approvers, and technicians across the system.

**Step 1: TC-03.2 — Employee List**

Navigate to Employee. Employees are linked to users, sites, and departments. They serve as requestors, approvers, and technicians across the system.


![TC-03.2 — Employee List](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_01_NAV.png)

**Step 2: TC-03.2 — New Employee**

Click 'Add New' to create an employee record. Link the employee to a user account, site, and department.


![TC-03.2 — New Employee](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_02_NEW.png)

**Step 3: TC-03.2 — Employee Created**

The employee record is created with an auto-generated ID (e.g., EMP-00001). The employee can now be assigned to maintenance requests, work orders, and labor records.


![TC-03.2 — Employee Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_04_SAVE.png)

**Step 4: TC-03.2 — Employee Detail**

The employee record shows name, linked user, site, department, and trade. Employees serve as the bridge between user accounts and operational entities.


![TC-03.2 — Employee Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-employee-labor__TC03_EMP_05_VERIFY.png)

---

### 8.3. TC 03 Master Data Organization

Navigate to Organization in the sidebar. This page shows all registered organizations. Organizations are the top level of the hierarchy: Organization → Site → Department.

**Step 1: TC-03.1 — Organization List**

Navigate to Organization in the sidebar. This page shows all registered organizations. Organizations are the top level of the hierarchy: Organization → Site → Department.


![TC-03.1 — Organization List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_01_NAV_ORG.png)

**Step 2: TC-03.1 — Create Organization**

Click 'Add New' to create a new Organization. Fill in the name and other required fields.


![TC-03.1 — Create Organization](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_02_NEW_ORG.png)

**Step 3: TC-03.1 — Organization Saved**

Click 'Create' to save the organization. A success notification confirms the record was created with an auto-generated ID.


![TC-03.1 — Organization Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_04_SAVE_ORG.png)

**Step 4: TC-03.1 — Organization Detail**

The organization record is now saved. You can see the auto-generated ID and all fields. Navigate to Site to create sites linked to this organization.


![TC-03.1 — Organization Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-organization__TC03_05_VERIFY_ORG.png)

---

### 8.4. TC 03 Master Data Site

Navigate to Site. Sites represent physical locations within an organization. Each site can have multiple departments.

**Step 1: TC-03.1 — Site List**

Navigate to Site. Sites represent physical locations within an organization. Each site can have multiple departments.


![TC-03.1 — Site List](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_01_NAV.png)

**Step 2: TC-03.1 — Create Site**

Click 'Add New' to create a new site. Link the site to the organization created in the previous step.


![TC-03.1 — Create Site](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_02_NEW.png)

**Step 3: TC-03.1 — Site Saved**

The site is created with an auto-generated ID and linked to the organization. Repeat this process to create additional sites.


![TC-03.1 — Site Saved](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_04_SAVE.png)

**Step 4: TC-03.1 — Site Detail View**

The site record shows the name, organization link, and any child departments. Each site serves as a scope boundary for role-based access control.


![TC-03.1 — Site Detail View](eam-chi/frontend/test-artifacts/screenshots/TC-03-master-data-site__TC03_SITE_05_VERIFY.png)

---

### 8.5. TC 03 Vendor Item

Navigate to Vendor. Vendors supply materials, spare parts, and services. Their performance is tracked automatically based on purchase receipts.

**Step 1: TC-03 — Vendor List**

Navigate to Vendor. Vendors supply materials, spare parts, and services. Their performance is tracked automatically based on purchase receipts.


![TC-03 — Vendor List](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_01_NAV.png)

**Step 2: TC-03 — Vendor Created**

The vendor record is created. Performance ratings (delivery, quality, overall) are auto-calculated from purchase receipts. A new vendor starts with default/zero ratings.


![TC-03 — Vendor Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_04_SAVE.png)

**Step 3: TC-03 — Vendor Detail**

The vendor detail shows contact information, performance ratings, and linked purchase orders. Ratings update automatically when purchase receipts are processed.


![TC-03 — Vendor Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_VENDOR_05_VERIFY.png)

**Step 4: TC-03 — Item (Inventory) List**

Navigate to Item. Items represent materials, spare parts, and consumables tracked in inventory. They are used in purchase requests, purchase orders, and work order parts.


![TC-03 — Item (Inventory) List](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_06_NAV.png)

**Step 5: TC-03 — Item Created**

The item is created with its name and default properties. Items track stock levels, reorder points, and are linked to stores for inventory management.


![TC-03 — Item Created](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_09_SAVE.png)

**Step 6: TC-03 — Item Detail**

The item detail view shows name, unit of measure, stock levels, reorder point, and storage locations. Items are referenced in PR lines, PO lines, and WO parts.


![TC-03 — Item Detail](eam-chi/frontend/test-artifacts/screenshots/TC-03-vendor-item__TC03_ITEM_10_VERIFY.png)

---

## 9. Purchasing & Stores

### 9.1. TC 11 Purchasing Pr Po

Navigate to Purchasing → Purchase Request. Purchase requests initiate procurement for materials, spare parts, and services needed for maintenance.

**Step 1: TC-11.1 — Purchase Request List**

Navigate to Purchasing → Purchase Request. Purchase requests initiate procurement for materials, spare parts, and services needed for maintenance.


![TC-11.1 — Purchase Request List](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_01_NAV_PR.png)

**Step 2: TC-11.1 — New Purchase Request**

Click 'Add New' to create a purchase request. Specify the requestor, due date, site, and department. Add line items with quantities and unit prices.


![TC-11.1 — New Purchase Request](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_02_NEW_PR.png)

**Step 3: TC-11.1 — PR Created (Draft)**

The purchase request is created with an auto-generated ID (e.g., PR-00001) in 'Draft' state. Add line items, then submit for approval.


![TC-11.1 — PR Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_04_SAVE_PR.png)

**Step 4: TC-11.1 — Purchase Request Detail**

The purchase request detail shows requestor, due date, and line items. The PR Lines child table allows adding items with quantities, unit prices, and calculated line totals.


![TC-11.1 — Purchase Request Detail](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_05_VERIFY_PR.png)

**Step 5: TC-11.2 — Purchase Order List**

Navigate to Purchasing → Purchase Order. Purchase orders are issued to vendors based on approved purchase requests. PO types include Standard, Blanket, and Contract.


![TC-11.2 — Purchase Order List](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_06_NAV_PO.png)

**Step 6: TC-11.2 — New Purchase Order**

Click 'Add New' to create a purchase order. Select the vendor, PO type, site, and department. Add line items matching the approved PR.


![TC-11.2 — New Purchase Order](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_07_NEW_PO.png)

**Step 7: TC-11.2 — PO New Form**

The new purchase order form shows fields for vendor, PO type, site, department, and financial details. Select a vendor to link the PO to approved purchase requests.


![TC-11.2 — PO New Form](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_08_FILL_PO.png)

**Step 8: TC-11.2 — PO Created (Draft)**

The purchase order is created with an auto-generated ID (e.g., PO-00001) in 'Draft' state. The form is editable in Draft. After approval, the form becomes read-only.


![TC-11.2 — PO Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_09_SAVE_PO.png)

**Step 9: TC-11.2 — Purchase Order Detail**

The purchase order detail shows vendor, PO type, terms, and line items. Supported PO types: Standard (one-time), Blanket (spending limit), and Contract (date range). The workflow moves through Draft → Open → Closed.


![TC-11.2 — Purchase Order Detail](eam-chi/frontend/test-artifacts/screenshots/TC-11-purchasing-pr-po__TC11_10_VERIFY_PO.png)

---

### 9.2. Purchase Request Lifecycle

Navigate to the Purchase Request list page. Purchase requests initiate the procurement workflow for materials, spare parts, and services.

**Step 1: Purchase Request List**

Navigate to the Purchase Request list page. Purchase requests initiate the procurement workflow for materials, spare parts, and services.


![Purchase Request List](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_01_NAVIGATE.png)

**Step 2: Create New Purchase Request**

Click 'Add New' to create a new purchase request. Fill in the required fields such as description and requested items.


![Create New Purchase Request](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_02_NEW.png)

**Step 3: Save Purchase Request**

Click 'Save' to create the purchase request. It will start in Draft state and can be submitted for approval.


![Save Purchase Request](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_04_SAVE.png)

**Step 4: Purchase Request Details**

The purchase request is now saved. Use the workflow dropdown to submit it for approval.


![Purchase Request Details](eam-chi/frontend/test-artifacts/screenshots/purchase-request-lifecycle__PR_05_VERIFY_SAVED.png)

---

## 10. Work Management

### 10.1. TC 07 Work Order

Navigate to Work Management → Work Order. Work orders track maintenance tasks from request through completion, including labor, parts, and costs.

**Step 1: TC-07.1 — Work Order List**

Navigate to Work Management → Work Order. Work orders track maintenance tasks from request through completion, including labor, parts, and costs.


![TC-07.1 — Work Order List](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_01_NAV.png)

**Step 2: TC-07.1 — New Work Order**

Click 'Add New' to create a new work order. Fill in the type, description, priority, site, department, asset, and due date.


![TC-07.1 — New Work Order](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_02_NEW.png)

**Step 3: TC-07.1 — WO Created (Requested)**

The work order is created with an auto-generated ID (e.g., WO-00001) in the 'Requested' state. Use the workflow dropdown to approve and start the work order.


![TC-07.1 — WO Created (Requested)](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_04_SAVE.png)

**Step 4: TC-07.1 — Work Order Detail**

The work order detail page shows all fields organized in tabs: Details, Labor, Equipment, Parts, Activities, and Attachments. The header shows the workflow state and available transitions.


![TC-07.1 — Work Order Detail](eam-chi/frontend/test-artifacts/screenshots/TC-07-work-order__TC07_05_VERIFY.png)

---

### 10.2. Work Order Lifecycle

Navigate to the Work Order list page. This page displays all work orders with their current workflow status, priority, and assigned personnel.

**Step 1: Work Order List**

Navigate to the Work Order list page. This page displays all work orders with their current workflow status, priority, and assigned personnel.


![Work Order List](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_01_NAVIGATE.png)

**Step 2: Create New Work Order**

Click 'Add New' to create a new work order. The form opens with default values including the 'Requested' workflow state.


![Create New Work Order](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_02_NEW.png)

**Step 3: Save Work Order**

Click 'Save' to create the work order. The system assigns a unique code and sets the initial workflow state.


![Save Work Order](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_04_SAVE.png)

**Step 4: Work Order Initial State**

After saving, the work order is in the initial workflow state. The workflow dropdown in the header shows available transitions.


![Work Order Initial State](eam-chi/frontend/test-artifacts/screenshots/work-order-lifecycle__WO_05_VERIFY_STATE.png)

---

## 11. Safety Permits

### 11.1. TC 09 Safety Permit

Navigate to Safety Permit. Safety permits control access to hazardous work areas and ensure proper safety procedures are followed before maintenance tasks begin.

**Step 1: TC-09.1 — Safety Permit List**

Navigate to Safety Permit. Safety permits control access to hazardous work areas and ensure proper safety procedures are followed before maintenance tasks begin.


![TC-09.1 — Safety Permit List](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_01_NAV.png)

**Step 2: TC-09.1 — New Safety Permit**

Click 'Add New' to create a new safety permit. Select the permit type (LOTO, Hot Work, Confined Space, etc.), link it to a work order, and specify hazards and precautions.


![TC-09.1 — New Safety Permit](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_02_NEW.png)

**Step 3: TC-09.1 — Safety Permit Created (Draft)**

The safety permit is created with an auto-generated ID (e.g., SP-00001) in 'Draft' state. Submit the request for approval by the safety officer.


![TC-09.1 — Safety Permit Created (Draft)](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_04_SAVE.png)

**Step 4: TC-09.1 — Safety Permit Detail**

The safety permit detail page shows permit type, valid dates, hazards, precautions, and emergency procedures. The workflow tracks the permit through its approval and activation lifecycle.


![TC-09.1 — Safety Permit Detail](eam-chi/frontend/test-artifacts/screenshots/TC-09-safety-permit__TC09_05_VERIFY.png)

---

## 12. Troubleshooting

This section covers common issues observed during testing.

### Empty Credentials Error

If you attempt to sign in without entering credentials, the system displays a validation message prompting you to fill in the required fields.


![Empty Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_02_EMPTY_SUBMIT.png)

> *Show the validation error that appears when submitting the login form with empty fields.*

### Invalid Credentials Error

If you enter an incorrect username or password, the system displays an error message. Verify your credentials and try again. After multiple failed attempts, your account may be temporarily locked.


![Invalid Credentials Error](eam-chi/frontend/test-artifacts/screenshots/login-edge-cases__LOGIN_ERR_05_WRONG_PASSWORD_SUBMIT.png)

> *Capture the error message displayed after failed login. This goes in the Troubleshooting section.*


---
*This manual was auto-generated by the Dual-Purpose Automation Framework.*