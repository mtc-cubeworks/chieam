# EAM-CHI User Manual

**Enterprise Asset Management — CHI**
**Version 1.0 | March 2026**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Dashboard & Navigation](#3-dashboard--navigation)
4. [Core EAM (Master Data)](#4-core-eam-master-data)
5. [Asset Management](#5-asset-management)
6. [Maintenance Management](#6-maintenance-management)
7. [Work Management](#7-work-management)
8. [Purchasing & Stores](#8-purchasing--stores)
9. [PM Calendar](#9-pm-calendar)
10. [Reports & Analytics](#10-reports--analytics)
11. [Administration](#11-administration)
12. [Workflows & State Machines](#12-workflows--state-machines)
13. [Import & Export](#13-import--export)
14. [Appendix A — Entity Reference](#appendix-a--entity-reference)
15. [Appendix B — Keyboard Shortcuts & Tips](#appendix-b--keyboard-shortcuts--tips)

---

## 1. Introduction

### 1.1 Purpose

EAM-CHI is an Enterprise Asset Management system designed for CHI operations. It provides comprehensive lifecycle management of physical assets, preventive and corrective maintenance planning, work order management, inventory control, and procurement workflows.

### 1.2 System Overview

| Component | Technology |
|-----------|-----------|
| Frontend | Nuxt.js 3 (Vue 3) |
| Backend | FastAPI (Python) with async SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Real-time | Socket.IO |
| Authentication | JWT + Refresh Tokens |

### 1.3 Modules

| Module | Description |
|--------|-------------|
| **Core EAM** | Master data: organizations, sites, departments, employees, labor, trades, schedules, manufacturers |
| **Asset Management** | Assets, equipment, locations, positions, meters, condition monitoring, incidents |
| **Maintenance Management** | Maintenance requests, orders, plans, activities, PM scheduling, failure analysis, inspections |
| **Work Management** | Work orders, activities, labor assignments, parts, checklists, job plans, safety permits |
| **Purchasing & Stores** | Purchase requests, purchase orders, vendors, items, inventory, stock counts, goods receipts |

### 1.4 Conventions Used in This Manual

- **Bold** — UI element names (buttons, fields, menus)
- `Monospace` — System values, codes, or entity names
- *Italic* — Emphasis or notes
- 🔒 — Requires specific role/permission
- ⚙️ — Automated by the system

---

## 2. Getting Started

### 2.1 Logging In

1. Open the application URL in your browser.
2. Enter your **Username** and **Password**.
3. Click **Login**.

The system authenticates via JWT tokens. Your session remains active until the token expires, at which point it is automatically refreshed.

### 2.2 First Login (Setup Wizard)

On first access to a fresh installation, the **Setup Wizard** guides you through:

1. Creating the initial **Organization** record
2. Setting up at least one **Site**
3. Creating the first **Admin User**
4. Configuring basic **Branding** (logo, colors)

### 2.3 User Profile

Access your profile via the user avatar in the top-right corner:

- **Profile** — Update your name, email, contact number
- **Change Password** — Update your password
- **Logout** — End your session

### 2.4 System Requirements

| Requirement | Minimum |
|-------------|---------|
| Browser | Chrome 90+, Firefox 88+, Safari 15+, Edge 90+ |
| Screen | 1280 × 720 minimum (1920 × 1080 recommended) |
| Network | Stable internet connection for real-time features |

---

## 3. Dashboard & Navigation

### 3.1 Sidebar Navigation

The left sidebar displays modules and entities based on your role permissions. Only entities where you have **can_read** permission and **in_sidebar** is enabled appear in the sidebar.

**Module groups:**
- **Core EAM** — Master data entities
- **Asset Management** — Asset-related entities
- **Maintenance Management** — Maintenance planning entities
- **Work Management** — Work order entities
- **Purchasing & Stores** — Procurement and inventory entities

Click any entity name to open its **List View**.

### 3.2 List View

Every entity opens in a tabular list view with:

- **Search** — Free-text search across fields
- **Filters** — Column-specific filtering
- **Sorting** — Click column headers to sort ascending/descending
- **Pagination** — Navigate through records
- **New** — Create a new record (requires `can_create` permission)
- **Export** — Download records to Excel (requires `can_export` permission)
- **Import** — Bulk import from Excel (requires `can_import` permission)

### 3.3 Detail View

Click any record to open its **Detail View**:

- **Form fields** — View and edit record data
- **Workflow bar** — Shows current state and available transitions
- **Child tables** — Related records shown as tabs below the form
- **Attachments** — Upload/download files associated with the record
- **Audit trail** — View change history
- **Actions** — Custom server actions available for the entity

### 3.4 Notifications

Real-time notifications appear via Socket.IO:
- Workflow state changes on records you own or are assigned to
- Maintenance request approvals/rejections
- Work order assignments
- System alerts

---

## 4. Core EAM (Master Data)

The Core EAM module manages all foundational reference data used across the system.

### 4.1 Organization

The top-level entity representing the company.

| Field | Description |
|-------|-------------|
| Organization Name | Legal name of the organization |
| Description | Additional details |

### 4.2 Site

Physical locations or facilities.

| Field | Description |
|-------|-------------|
| Site Name | Name of the site/facility |
| Organization | Parent organization (link) |
| Address | Physical address |

*Naming pattern: auto-generated*

### 4.3 Department

Organizational units within a site.

| Field | Description |
|-------|-------------|
| Department Name | Name of the department |
| Site | Parent site (link) |
| Manager | Department head (employee link) |

### 4.4 Employee

Personnel records linked to user accounts.

| Field | Description |
|-------|-------------|
| Employee Name | Full name |
| User | Linked system user account |
| Position | Job title/position |
| Site | Primary work site |
| Department | Associated department |

*Naming pattern: EMP-{#####}*

### 4.5 Labor

Labor resources available for work orders and maintenance.

| Field | Description |
|-------|-------------|
| Laborer | Display name |
| Labor Type | Classification (e.g., Technician, Helper) |
| Employee | Linked employee record |
| Trade | Trade/skill classification |

*Naming pattern: LAB-{#####}*

### 4.6 Trade

Skill classifications for labor resources (e.g., Electrician, Mechanic, Plumber).

| Field | Description |
|-------|-------------|
| Trade Name | Name of the trade |
| Description | Details about the trade |

**Related entities:**
- **Trade Labor** — Associates labor resources with trades
- **Trade Availability** — Defines time slots a trade is available

### 4.7 Work Schedule

Defines working hours and shift patterns.

| Field | Description |
|-------|-------------|
| Schedule Name | Name identifier |
| Description | Details |

**Children:**
- **Work Schedule Details** — Individual day/time entries defining the schedule

### 4.8 Holidays & Leave

- **Holiday** — Company-wide holidays with date and description
- **Leave Type** — Types of leave (Annual, Sick, etc.)
- **Leave Application** — Individual leave requests

### 4.9 Manufacturer & Model

- **Manufacturer** — Equipment/asset manufacturers
- **Model** — Specific product models linked to manufacturers

### 4.10 Other Master Data

| Entity | Purpose |
|--------|---------|
| **Series** | Document numbering series |
| **Account** | Financial accounts |
| **Cost Code** | Cost categorization codes |
| **Annual Budget** | Budget allocations by department/year |
| **Request Activity Type** | Categories for maintenance activities |
| **Contractor** | External contractor records |
| **Labor Group** | Groups of labor resources |
| **Labor Availability** | Availability schedules for labor |

---

## 5. Asset Management

### 5.1 Assets

The core entity of the system — physical assets being managed.

**Creating an Asset:**

1. Navigate to **Asset Management → Asset**
2. Click **+ New**
3. Fill in required fields:
   - **Asset Tag** — Unique identifier (auto-generated: `A-{#####}`)
   - **Description** — Asset description
   - **Asset Class** — Classification category
   - **Site** — Installation site
4. Save the record

**Key Sections:**

#### Basic Information
| Field | Description |
|-------|-------------|
| Asset Tag | Auto-generated unique ID (A-#####) |
| Description | Detailed description |
| Series | Document series |
| Model | Manufacturer model |
| Serial Number | OEM serial number |
| Date Purchased | Purchase date |
| Cost | Acquisition cost |

#### Location & Assignment
| Field | Description |
|-------|-------------|
| Block Number | Physical block/area |
| Location | Functional location |
| Site | Installation site |
| Department | Owning department |
| Assigned To | Responsible person |

#### Lifecycle Management (AR-1)
| Field | Description |
|-------|-------------|
| Lifecycle State | Current stage: Planning, Procurement, Commissioning, Active, Idle, Decommissioned, Disposed |

#### Asset Hierarchy (AR-2)
| Field | Description |
|-------|-------------|
| Parent Asset | Parent in the asset tree |
| Functional Location | Position in functional hierarchy |

#### Criticality Classification (AR-3)
| Field | Description |
|-------|-------------|
| Criticality | A-Critical, B-Important, C-General |
| Risk Score | Numeric risk assessment (0–100) |

#### Warranty Information (AR-5)
| Field | Description |
|-------|-------------|
| Warranty Start | Start date of warranty |
| Warranty End | End date of warranty |
| Warranty Vendor | Vendor providing warranty |

#### Nameplate / Specifications (AR-6)
| Field | Description |
|-------|-------------|
| Manufacturer | OEM manufacturer |
| Manufacturer Part Number | OEM part number |
| Rated Capacity | Design capacity |
| Rated Power | Power rating |
| Weight | Physical weight |
| Technical Specs | Free-text specifications |

#### Depreciation (AR-7)
| Field | Description |
|-------|-------------|
| Depreciation Method | Straight-Line, Declining Balance, etc. |
| Useful Life Years | Expected lifespan in years |
| Salvage Value | Residual value at end of life |
| Accumulated Depreciation | Total depreciation to date (read-only) |
| Commissioning Date | Date placed in service |

**Asset Workflow:**

```
Acquired → Inspected → Active → Inactive → Under Maintenance → Under Repair → Decommissioned
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Receive | Acquired | Inspected | Asset received and ready for inspection |
| Install Asset | Inspected | Active | Asset installed and operational |
| Retire Asset | Active | Inactive | Temporarily taken out of service |
| Putaway | Active | Under Maintenance | Sent for scheduled maintenance |
| Internal Repair | Active | Under Repair | Sent for repair |
| Send to Vendor | Active | Under Repair | Sent externally for repair |
| Complete | Under Maintenance / Under Repair | Active | Returned to service |
| Remove Asset | Inactive | Decommissioned | Permanently decommissioned |
| Dispose | Decommissioned | *(terminal)* | Asset disposed of |

**Child Records:**
- **Asset Property** — Custom properties and their values
- **Asset Position** — Physical positions within the asset
- **Sub-Asset** — Child assets in the hierarchy
- **Sensor** — Attached sensors for condition monitoring
- **Meter** — Meters for usage tracking
- **Warranty Claim** — Claims against warranty
- **Maintenance History** — Historical maintenance records

**Server Actions:**
- **Clone Asset** (AR-8) — Duplicates the asset record for creating similar equipment. 🔒 *Requires create permission.*

### 5.2 Equipment

Movable equipment that can be assigned to work orders.

| Field | Description |
|-------|-------------|
| Equipment Type | Owned or Rented |
| Equipment Group | Category of equipment |
| Custodian | Responsible employee |
| Location / Site | Current location |
| Equipment Cost | Value/rental cost |

*Naming pattern: EQP-{####}*

**Conditional Fields:**
- *Owned*: **Inventory** link (to the inventory item record)
- *Rented*: **PR Line No** link (to the purchase request line)

### 5.3 Asset Class

Classification categories for grouping assets (e.g., "Rotating Equipment", "Electrical Panel").

**Children:** Asset Class Property, Asset Class Availability

### 5.4 Location Types, System Types, Property Types

Reference data for structuring asset locations, systems, and properties.

### 5.5 Meters & Meter Readings

Track usage-based metrics on assets.

**Meter** — Defines what is being measured (e.g., operating hours, distance, cycles).

**Meter Reading** — Individual readings over time.

| Field | Description |
|-------|-------------|
| Meter | Parent meter |
| Reading Value | Current reading |
| Reading Date | Date/time of reading |
| Delta | Change from previous reading (⚙️ auto-calculated) |

### 5.6 Incidents

Record unplanned events or failures.

| Field | Description |
|-------|-------------|
| Asset | Affected asset |
| Incident Date | When it occurred |
| Description | What happened |
| Severity | 1-Critical, 2-High, 3-Medium, 4-Low |

**Children:** Incident Employee (people involved)

### 5.7 Condition Monitoring

Track real-time asset health through sensor data.

| Field | Description |
|-------|-------------|
| Asset | Monitored asset |
| Sensor | Data source sensor |
| Monitoring Type | Vibration, Temperature, Pressure, Oil Analysis, Ultrasonic, Thermography, Current/Voltage |
| Reading Value | Current sensor reading |
| Reading Unit | Unit of measurement |
| Baseline Value | Normal operating value |
| Warning Threshold | Threshold for warning alert |
| Critical Threshold | Threshold for critical alert |
| Alert Status | Normal, Warning, Critical, Alarm |
| Trend Direction | Stable, Increasing, Decreasing, Erratic |
| Analysis Notes | Free-text notes |

*Naming pattern: CM-{#####}*

**Workflow:**
```
Active → Warning → Critical → Resolved
```

| Transition | Description |
|-----------|-------------|
| Warn | Reading exceeds warning threshold |
| Escalate | Reading exceeds critical threshold |
| Resolve | Issue addressed; return to monitoring |

---

## 6. Maintenance Management

### 6.1 Maintenance Request

The primary entry point for all maintenance work — whether planned or unplanned.

**Creating a Maintenance Request:**

1. Navigate to **Maintenance Management → Maintenance Request**
2. Click **+ New**
3. Fill in:
   - **Requestor** — Employee making the request
   - **Description** — What needs to be done
   - **Asset** — Affected asset
   - **Priority** — Low, Medium, High, or Emergency
   - **Request Category** — Corrective, Emergency, Safety, Modification, Inspection, Condition Based, Preventive
   - **Site / Department** — Location
   - **Due Date** — When action is needed by
4. Save the record

*Naming pattern: MTREQ-{#####}*

**Key Fields:**

| Field | Description |
|-------|-------------|
| Request Category | Corrective, Emergency, Safety, Modification, Inspection, Condition Based, Preventive |
| Priority | Low, Medium, High, Emergency |
| Planned Maintenance Activity | Link to PM activity (if this MR is PM-generated) |
| SLA Response Due | ⚙️ Auto-calculated based on priority |
| SLA Resolution Due | ⚙️ Auto-calculated based on priority |
| SLA Status | On Track, At Risk, Breached (⚙️ auto-tracked) |
| Is Overdue | ⚙️ Auto-flagged when past due date |

**Workflow:**
```
Draft → Pending Approval → Approved → Release → Completed
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Submit for Approval | Draft | Pending Approval | Submit for management review |
| Submit for Emergency | Draft | Approved | Bypass approval for emergencies |
| Approve | Pending Approval | Approved | Manager approves the request |
| Submit for Resolution | Approved | Release | Release work to technicians |
| Complete | Release | Completed | Work finished |
| Reopen | Completed | Draft | Reopen if issue persists |

**SLA Thresholds:**
- Pending Approval: 4 hours
- Approved: 24 hours
- In Progress: 48 hours

⚙️ **Notifications:** When a maintenance request changes state, the system automatically notifies:
- Approvers (on submission)
- Requestor (on approval/rejection)
- Team leads (on escalation)

**Server Actions:**
- **Generate Maintenance Order** — Creates a maintenance order from this request
- **Create Purchase Request** — Auto-creates a PR for parts needed

### 6.2 Maintenance Order

Groups maintenance activities generated from maintenance requests.

| Field | Description |
|-------|-------------|
| Created Date | Date order was created |
| Work Order | Linked work order (read-only) |

*Naming pattern: MTORD-{#####}*

**Children:** Maintenance Order Detail

### 6.3 Maintenance Plan

Defines long-term maintenance strategies for asset classes.

| Field | Description |
|-------|-------------|
| Description | Plan description |
| Asset Class | Target asset classification |
| Manufacturer | Equipment manufacturer |
| Model | Equipment model |

*Naming pattern: MTPLAN-{#####}*

**Children:** Planned Maintenance Activity

### 6.4 Planned Maintenance Activity

Individual maintenance tasks within a plan, defining when and how maintenance occurs.

| Field | Description |
|-------|-------------|
| Maintenance Plan | Parent plan |
| Maintenance Activity | Activity to perform |
| Checklist | Associated checklist |
| Maintenance Schedule | Calendar Based, Interval Based, or Condition Based |
| Maintenance Type | Activity type classification |

*Naming pattern: PMA-{#####}*

**Children:**
- Maintenance Interval — Defines frequency (e.g., every 30 days, every 500 operating hours)
- Maintenance Condition — Defines condition triggers
- Maintenance Calendar — Calendar-specific scheduling
- Maintenance Equipment — Equipment needed
- Maintenance Parts — Parts required
- Maintenance Trade — Trades/skills required

### 6.5 Maintenance Activity

Reusable activity definitions — the actual work to be done.

| Field | Description |
|-------|-------------|
| Activity Name | Name of the activity |
| Description | Detailed description |

*Naming pattern: MTACT-{#####}*

**Children:** Maintenance Parts, Maintenance Trade, Maintenance Equipment

### 6.6 Checklist

Standard checklists for inspection and verification.

| Field | Description |
|-------|-------------|
| Checklist Name | Name |
| Description | Details |

**Children:** Checklist Details (individual check items)

### 6.7 Maintenance Interval

Defines time-based or usage-based intervals for planned maintenance.

| Field | Description |
|-------|-------------|
| Planned Maintenance Activity | Parent PMA |
| Lead Interval | Advance notice period |
| Interval | Frequency value |
| Interval Unit of Measure | Days, weeks, months, hours, etc. |
| Running Interval Property | Meter/property for usage-based |

### 6.8 Failure Analysis

Root cause analysis for asset failures using structured methodologies.

| Field | Description |
|-------|-------------|
| Asset | Failed asset |
| Work Order | Related work order |
| Failure Code | Classification code |
| Failure Mode | How the failure manifested |
| Severity Score | 1–10 severity rating |
| Occurrence Score | 1–10 frequency rating |
| Detection Score | 1–10 detectability rating |
| RPN | Risk Priority Number (⚙️ auto-calculated: Severity × Occurrence × Detection) |
| Risk Level | Low, Medium, High, Critical |

**Server Actions:**
- **Calculate RPN** — Computes Risk Priority Number from severity, occurrence, and detection scores
- **Generate 5-Why Template** — Creates a structured 5-Why analysis template
- **Generate Fishbone Template** — Creates an Ishikawa diagram template

### 6.9 Sensor

IoT/OT sensor definitions for condition monitoring.

| Field | Description |
|-------|-------------|
| Sensor Name | Identifier |
| Asset | Attached asset |
| Sensor Type | Type classification |

### 6.10 Inspection Point

Individual points on an inspection route.

| Field | Description |
|-------|-------------|
| Description | What to inspect |
| Asset | Target asset |
| Inspection Criteria | Pass/fail criteria |

---

## 7. Work Management

### 7.1 Work Order

The central execution entity — all maintenance work is tracked through work orders.

**Creating a Work Order:**

1. Navigate to **Work Management → Work Order**
2. Click **+ New**
3. Fill in:
   - **Work Order Type** — Preventive Maintenance or Corrective Maintenance
   - **Description** — Scope of work
   - **Priority** — Low, Medium, High, Emergency
   - **Due Date** — Required completion date
   - **Site / Department** — Location
   - **Asset** — Target asset (if applicable)
4. Save the record

*Naming pattern: WO-{#####}*

**Key Sections:**

#### Scheduling
| Field | Description |
|-------|-------------|
| Scheduled Start / End | Planned timeframe |
| Actual Start / End | Actual timeframe (filled on execution) |
| Due Date | Deadline |

#### Cost Tracking (WO-5)
| Field | Description |
|-------|-------------|
| Estimated Cost | Budget estimate |
| Total Labor Cost | ⚙️ Rolled up from WO Labor |
| Total Equipment Cost | ⚙️ Rolled up from WO Equipment |
| Total Parts Cost | ⚙️ Rolled up from WO Parts |
| Total Cost | ⚙️ Sum of all cost components |
| Cost Code | Cost center allocation |

#### Downtime Tracking (WO-6)
| Field | Description |
|-------|-------------|
| Downtime Start | When asset went offline |
| Downtime End | When asset returned to service |
| Downtime Hours | ⚙️ Auto-calculated duration |

#### Failure Reporting (WO-7)
| Field | Description |
|-------|-------------|
| Cause Code | Root cause classification |
| Remedy Code | Repair classification |
| Failure Notes | Detailed failure description |

#### Close-out
| Field | Description |
|-------|-------------|
| Technician Findings | What the technician found |
| Work Performed | What was done |
| Recommendations | Follow-up recommendations |
| Follow-up Work Order | Link to follow-up WO if needed |

#### Safety (WO-8)
| Field | Description |
|-------|-------------|
| LOTO Required | Is lockout/tagout needed? |
| Safety Permit | Associated safety permit |

#### Approval
| Field | Description |
|-------|-------------|
| Approval Level | Required approval tier |
| Approved By | Who approved |

**SLA Thresholds:**
- Requested: 8 hours
- Approved: 24 hours
- In Progress: 72 hours

**Workflow:**
```
Requested → Approved → In Progress → Closed
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Approve | Requested | Approved | Work order approved |
| Start | Approved | In Progress | Work begins |
| Complete | In Progress | Closed | Work completed |
| Reopen | Closed | Requested | Reopen if needed |

⚙️ **Notifications:** When a work order state changes, assigned labor is automatically notified.

**Child Records:**
- Work Order Activity (tasks)
- Work Order Labor (labor hours/cost)
- Work Order Equipment (equipment used)
- Work Order Parts (materials consumed)
- Work Order Checklist (checklists completed)
- Safety Permit (associated permits)
- Tool Checkout (tools issued)

### 7.2 Work Order Activity

Individual tasks within a work order.

*Naming pattern: WOACT-{#####}*

**Workflow:**
```
Awaiting Resources → Ready → In Progress → On Hold → Completed → Closed
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Allocate | Awaiting Resources | Ready | Resources confirmed |
| Start Activity | Ready | In Progress | Work begins |
| Put On Hold | In Progress | On Hold | Paused (waiting for parts, etc.) |
| Resume | On Hold | In Progress | Continue work |
| Complete | In Progress | Completed | Task finished |
| Close | Completed | Closed | Formally closed |
| Reopen | Completed | Ready | Reopen if needed |

**Key Fields:**
| Field | Description |
|-------|-------------|
| Work Order | Parent work order |
| Description | Task description |
| Work Item Type | Asset or Non-Asset |
| Work Item | Target asset |
| Activity Type | Type of activity |

**Server Actions:**
- **Generate Templated PMA** — Creates a Planned Maintenance Activity template from a completed activity for future reuse.

### 7.3 Work Order Labor

Tracks labor resources assigned to a work order.

| Field | Description |
|-------|-------------|
| Labor | Labor resource |
| Hours | Hours worked |
| Rate | Hourly rate |
| Total | ⚙️ Hours × Rate |

### 7.4 Work Order Equipment

Tracks equipment used during work execution.

| Field | Description |
|-------|-------------|
| Equipment | Equipment resource |
| Hours | Hours used |

### 7.5 Work Order Parts

Tracks materials/parts consumed.

| Field | Description |
|-------|-------------|
| Item | Inventory item |
| Quantity | Quantity used |
| Unit Price | Price per unit |
| Total | ⚙️ Quantity × Unit Price |

### 7.6 Job Plan

Predefined templates for standard maintenance jobs. Contains pre-configured tasks, labor, parts, and tools so work orders can be created from proven procedures.

| Field | Description |
|-------|-------------|
| Job Plan Name | Name |
| Description | Detailed procedures |

**Children:** Job Plan Task (individual steps with labor, parts, tools)

### 7.7 Safety Permit

Permits required before hazardous work can begin.

*Naming pattern: SP-{#####}*

**Permit Types:**
- **LOTO** — Lockout/Tagout
- **Hot Work** — Welding, cutting, grinding
- **Confined Space** — Tanks, vessels, pits
- **Excavation** — Digging, trenching
- **Working at Height** — Scaffolding, ladders
- **Electrical** — Electrical isolation work

**Key Fields:**
| Field | Description |
|-------|-------------|
| Permit Type | Type of permit (required) |
| Work Order | Associated work order |
| Asset | Target asset |
| Location | Work location |
| Requested By | Employee requesting |
| Approved By | Approving authority |
| Valid From / To | Permit validity window |
| Hazards Identified | List of identified hazards |
| Precautions | Safety precautions to follow |
| Emergency Procedures | Emergency response plan |

**Workflow:**
```
Draft → Requested → Approved → Active → Expired/Cancelled
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Submit Request | Draft | Requested | Permit submitted for review |
| Approve | Requested | Approved | Safety officer approves |
| Activate | Approved | Active | Permit activated for work |
| Expire | Active | Expired | Validity period ended |
| Cancel | Any | Cancelled | Permit cancelled |
| Renew | Expired | Draft | Create renewal |

### 7.8 Work Order Checklist

Links checklist templates to work orders for completion tracking.

**Children:** Work Order Checklist Details (individual check items with completion status)

---

## 8. Purchasing & Stores

### 8.1 Item

Master catalog of all items (parts, materials, assets, services).

*Naming pattern: ITM-{#####}*

**Item Types:**
- **Fixed Asset Item** — Capital equipment
- **Asset Item** — Trackable asset components
- **Inventory Item** — Stocked materials
- **Non Inventory Item** — Non-stocked purchases
- **Service Item** — Services

**Key Fields:**
| Field | Description |
|-------|-------------|
| Item Name | Name (required) |
| Description | Details (required) |
| Item Class | Category classification |
| Item Type | Classification (required) |
| ABC Code | A, B, or C classification |
| UOM | Unit of measure (required) |
| Unit Cost | Standard cost |
| Primary Vendor | Default supplier |
| Is Serialized | Track by serial number |
| Inspection Required | Incoming inspection needed |

### 8.2 Vendor

Supplier/contractor records with performance tracking.

*Naming pattern: VND-{#####}*

**Vendor Types:**
- Supplier
- Contractor
- Service Provider
- OEM

**Performance Metrics (read-only, ⚙️ auto-calculated):**
| Field | Description |
|-------|-------------|
| Delivery Rating | On-time delivery score (0–5) |
| Quality Rating | Quality/rejection score (0–5) |
| Overall Rating | Composite performance (0–5) |
| Total Orders | Lifetime order count |
| On-Time Deliveries | Count of timely deliveries |
| Rejected Deliveries | Count of rejected receipts |

⚙️ Vendor ratings are automatically recalculated when purchase receipts are processed.

### 8.3 Purchase Request

Internal requests for procurement.

*Naming pattern: PR-{#####}*

**Key Fields:**
| Field | Description |
|-------|-------------|
| Requestor | Employee requesting |
| Due Date | When items are needed |
| Site / Department | Location and department |
| Cost Code | Budget allocation |

**Children:** Purchase Request Line (items, quantities, estimated prices)

**Workflow:**
```
Draft → Open → Closed/Rejected/Cancelled
```

### 8.4 Purchase Order

Formal orders placed with vendors.

*Naming pattern: PO-{#####}*

**PO Types:**
- **Standard** — One-time purchase
- **Blanket** — Framework agreement with limit
- **Contract** — Long-term contract with period

**Key Fields:**
| Field | Description |
|-------|-------------|
| Vendor | Supplier (required) |
| Date Ordered | Order date |
| Total Amount | ⚙️ Rolled up from PO lines |
| Site / Department | Location (required) |
| Cost Code | Budget allocation |
| PO Type | Standard, Blanket, Contract |
| Blanket Limit | Maximum for blanket POs |
| Released Amount | Amount used against blanket (read-only) |
| Contract Start / End | Period for contract POs |
| Payment Terms | Agreed payment terms |
| Delivery Terms | Agreed delivery terms |
| Amendment Number | Change order number |
| Amendment Reason | Reason for amendment |
| Original PO | Link to original (for amendments) |

**Workflow:**
```
Draft → Open → Closed/Rejected/Cancelled
```

| Transition | From | To | Description |
|-----------|------|-----|-------------|
| Approve | Draft | Open | PO approved and sent to vendor |
| Reject | Draft | Rejected | PO rejected |
| Complete | Open | Closed | All items received |
| Cancel | Any | Cancelled | PO cancelled |

*Note: The form is only editable in Draft state.*

**Children:** Purchase Order Line (items, quantities, agreed prices)

### 8.5 Purchase Receipt

Records goods received against purchase orders.

| Field | Description |
|-------|-------------|
| Purchase Order | Source PO |
| Received Date | Date of receipt |
| Received Quantity | Qty received |

⚙️ On saving a purchase receipt, vendor performance metrics are automatically recalculated.

### 8.6 Inventory

Tracks stock levels at store locations.

| Field | Description |
|-------|-------------|
| Item | Inventory item |
| Quantity on Hand | Current stock |
| Reorder Point | Minimum before reorder |
| Reorder Quantity | Qty to order |
| Store | Storage location |

### 8.7 Store

Physical storage locations for inventory.

| Field | Description |
|-------|-------------|
| Store Name | Name |
| Location | Physical location |
| Site | Facility |

### 8.8 Stock Count

Periodic physical inventory verification.

| Field | Description |
|-------|-------------|
| Count Date | Scheduled date |
| Store | Target store |
| Status | Planned, In Progress, Completed |

### 8.9 Inventory Adjustment

Records corrections to inventory quantities.

| Field | Description |
|-------|-------------|
| Item | Adjusted item |
| Quantity | Adjustment amount (+/-) |
| Reason | Reason code |

### 8.10 Parts Issue & Parts Return

- **Parts Issue** — Materials issued from stores against work orders
- **Parts Return** — Materials returned to stores with reason tracking

---

## 9. PM Calendar

### 9.1 Overview

The **Preventive Maintenance Calendar** provides a monthly calendar view for scheduling, visualizing, and managing PM tasks. It integrates with maintenance activities, work orders, and maintenance requests.

### 9.2 Accessing the Calendar

Navigate to the **Calendar** page from the main navigation. The calendar displays PM tasks color-coded by workflow state:

| State | Color | Description |
|-------|-------|-------------|
| Draft | Slate gray | Newly created, not yet submitted |
| Pending Approval | Amber | Awaiting management approval |
| Approved | Blue | Approved, ready for execution |
| Release | Violet | Released to technicians |
| Completed | Green | Work finished |

### 9.3 Viewing Tasks

- Select **Year** and **Month** from the dropdowns
- Filter by **Site** and **Department** as needed
- Each day shows scheduled PM tasks with their color indicators
- Click a task to view full details

### 9.4 Creating a PM Task

1. Click on a day or click **+ New Task**
2. Fill in:
   - **Activity Name** — The maintenance activity
   - **Due Date** — Scheduled date
   - **Start Time** — Scheduled time
   - **Assigned To** — Labor resource
   - **Site / Department** — Location
   - **Notes** — Additional instructions
3. Save

⚙️ The system automatically creates:
- A **Maintenance Activity** (if it doesn't already exist)
- A **Planned Maintenance Activity** (Calendar Based schedule)
- A **Work Order** (type: Preventive Maintenance)
- A **Work Order Activity** (30-minute default duration)
- A **Maintenance Request** linking all above

### 9.5 Rescheduling Tasks

Drag and drop a task to a new date. The system updates the due date while preserving the scheduled time.

### 9.6 Updating Task Status

Click a task and update its **Workflow State** to progress it through the approval and execution cycle.

### 9.7 Seed Data

🔒 *Admin only.* Use the **Seed** function to populate the calendar with predefined activities and team members for initial setup. This creates 32 standard activities, 6 team members, 31 holidays, and a full month of PM tasks.

**Standard Activities Include:**
Engine Area Cleaning, Biogrinder Inspection, Hopper Inspections, Hose Pump Inspection, Mixer Inspection, Air Blower, Membrane Checking, Recirculation Pump, Gas Blowers, Chiller, Carbon Filter, Separator, Truck Units Greasing, Boiler, Flare System, Air Compressors, Gas Pipes Draining, General Cleaning, VFD Inspection, Aircon Checking, Faults Checking HMI, Chiller Servicing, Sensor Checking, Genset Inspection, Valves Inspection, Panel Fans Inspection, Analyzer Calibration, Flowmeter Inspection, Greasing All Components, Fire Extinguisher Inspection, Warehouse Inspection.

### 9.8 Auto-Generation

⚙️ **Scheduled Job — PM Calendar Auto-Generation** runs daily at 1:00 AM:

1. Scans all `maintenance_calendar` entries with frequency set
2. Checks the last `maintenance_request` for each planned maintenance activity
3. Calculates the next due date based on frequency (Weekly/7d, Monthly/30d, Quarterly/90d, Annually/365d)
4. If next due ≤ today + 7 days, auto-generates:
   - New maintenance request
   - Linked work order (type: Preventive Maintenance, state: Requested)
5. Logs execution details to `scheduled_job_log`

---

## 10. Reports & Analytics

### 10.1 Accessing Reports

Navigate to **Reports** from the sidebar. Available reports are listed based on your role permissions.

### 10.2 Generating a Report

1. Select a report from the list
2. Configure parameters (date range, site, department, filters)
3. Click **Generate**
4. View the report on-screen
5. Optionally **Export to PDF** for offline use

### 10.3 Exporting Data

Every list view supports **Export to Excel**:
1. Navigate to any entity list view
2. Apply desired filters
3. Click the **Export** button
4. An Excel file downloads with all visible records

---

## 11. Administration

### 11.1 User Management

🔒 *SystemManager role required.*

**Managing Users:**

1. Navigate to **Admin → Users**
2. View all users with pagination
3. **Create User**: Username, email, full name, password, department, site
4. **Edit User**: Update details, activate/deactivate
5. **Assign Roles**: Add/remove roles from a user

### 11.2 Role Management

🔒 *SystemManager role required.*

**Default Roles:**

| Role | Description |
|------|-------------|
| SystemManager | Full access to all entities and admin functions |
| Viewer | Read-only access across all entities |
| Admin | Full CRUD on all entities |
| Editor | Create and update (no delete) |

**Managing Roles:**

1. Navigate to **Admin → Roles**
2. Create custom roles with descriptive names
3. Assign permissions per entity (see below)

### 11.3 Permission Management

🔒 *SystemManager role required.*

The **Permission Matrix** provides a visual grid of Role × Entity with toggleable permissions:

| Permission | Description |
|-----------|-------------|
| **Can Read** | View records and see entity in sidebar |
| **Can Create** | Create new records |
| **Can Update** | Edit existing records |
| **Can Delete** | Delete records |
| **Can Select** | Appear in link field dropdowns |
| **Can Export** | Export records to Excel |
| **Can Import** | Import records from Excel templates |
| **In Sidebar** | Show entity in navigation sidebar |

**Accessing the matrix:**
1. Navigate to **Admin → Permissions**
2. View entities organized by module
3. Toggle permissions per role per entity
4. Save changes

### 11.4 Workflow Management

🔒 *SystemManager role required.*

**Managing Workflows:**

1. Navigate to **Admin → Workflow**
2. View all workflow definitions
3. For each workflow:
   - View/edit states and their colors
   - View/edit transitions (from state → action → to state)
   - Configure allowed roles per transition (restrict who can perform state changes)

**Workflow Transition Role Restrictions:**
Each transition can optionally restrict which roles can execute it. If `allowed_roles` is set on a transition, only users with those roles can trigger that state change.

### 11.5 Model Editor

🔒 *SystemManager role required.*

The **Model Editor** allows dynamic entity management:

1. **View Entities** — List all entity definitions
2. **Edit Entity** — Modify fields, labels, types, and relationships
3. **Sync** — Apply changes to the database (migrations)
4. **Backups** — Create/restore entity configuration backups
5. **Migrations** — Apply, rollback, or check migration status

> ⚠️ **Caution:** Changes in the Model Editor directly affect the database schema. Always create a backup before making structural changes.

### 11.6 Sidebar Ordering

🔒 *SystemManager role required.*

Customize the display order of modules and entities in the sidebar navigation:

1. Navigate to **Admin → Ordering**
2. Drag modules to reorder
3. Drag entities within each module
4. Save the new order

### 11.7 Branding & Settings

Customize application appearance:
- **Logo** — Upload company logo
- **Colors** — Primary, secondary, accent colors
- **Application Name** — Custom title

### 11.8 Scheduled Jobs

The system runs automated background jobs:

| Job | Schedule | Purpose |
|-----|----------|---------|
| PM Calendar Auto-Generation | Daily at 1:00 AM | Generate PM work orders based on maintenance schedules |

All job executions are logged in the **Scheduled Job Log** entity with status, duration, records created/updated, and any error details.

---

## 12. Workflows & State Machines

### 12.1 How Workflows Work

Every workflowed entity has a `workflow_state` field that tracks its current state. State transitions are the only way to move between states — you cannot manually type a state value.

**To transition a record:**
1. Open the record's detail view
2. The workflow bar at the top shows the current state and available actions
3. Click an available action button (e.g., "Approve", "Start", "Complete")
4. The record transitions to the new state
5. An audit log entry is created

### 12.2 State-Based Field Permissions (SM-1)

Certain fields become **read-only** based on the current workflow state. For example:
- Maintenance Request in "Pending Approval": description, asset, and requestor cannot be changed
- Purchase Order in "Open": all form fields are read-only

### 12.3 Required Fields Per State (SM-2)

Some state transitions require specific fields to be filled. The system validates these requirements before allowing the transition.

### 12.4 SLA Tracking (SM-5)

Each entity/state combination has an SLA threshold in hours. The system tracks:
- **SLA Status** — On Track, At Risk, Breached
- **Is Overdue** — Boolean flag automatically set when SLA is exceeded

**SLA thresholds:**

| Entity | State | Hours |
|--------|-------|-------|
| Maintenance Request | Pending Approval | 4h |
| Maintenance Request | Approved | 24h |
| Maintenance Request | In Progress | 48h |
| Work Order | Requested | 8h |
| Work Order | Approved | 24h |
| Work Order | In Progress | 72h |

### 12.5 Audit Logging (SM-6)

Every state transition is logged with:
- Previous state and new state
- User who performed the transition
- Timestamp
- Entity and record ID

---

## 13. Import & Export

### 13.1 Exporting Data

1. Open any entity list view
2. Apply filters (optional)
3. Click **Export**
4. An Excel file downloads containing all matching records

### 13.2 Importing Data

1. Open any entity list view
2. Click **Import**
3. **Download Template** — Get an Excel template with correct column headers
4. Fill in data following the template format
5. **Upload** the completed file
6. **Validate** — System checks for errors (missing required fields, invalid links, data type mismatches)
7. Review validation results
8. **Execute** — Import validated records

> 💡 **Tip:** Always download a fresh template before importing to ensure column headers match the current entity configuration.

---

## Appendix A — Entity Reference

### Auto-Generated ID Patterns

| Entity | Prefix | Pattern |
|--------|--------|---------|
| Asset | A | A-{#####} |
| Equipment | EQP | EQP-{####} |
| Condition Monitoring | CM | CM-{#####} |
| Employee | EMP | EMP-{#####} |
| Labor | LAB | LAB-{#####} |
| Maintenance Request | MTREQ | MTREQ-{#####} |
| Maintenance Order | MTORD | MTORD-{#####} |
| Maintenance Plan | MTPLAN | MTPLAN-{#####} |
| Planned Maintenance Activity | PMA | PMA-{#####} |
| Maintenance Activity | MTACT | MTACT-{#####} |
| Maintenance Interval | MTINT | MTINT-{#####} |
| Work Order | WO | WO-{#####} |
| Work Order Activity | WOACT | WOACT-{#####} |
| Safety Permit | SP | SP-{#####} |
| Item | ITM | ITM-{#####} |
| Vendor | VND | VND-{#####} |
| Purchase Request | PR | PR-{#####} |
| Purchase Order | PO | PO-{#####} |

### Workflow Summary

| Entity | States | Key Transitions |
|--------|--------|-----------------|
| Asset | Acquired → Inspected → Active → Inactive → Under Maintenance → Under Repair → Decommissioned | Receive, Install, Retire, Putaway, Repair, Complete, Remove, Dispose |
| Maintenance Request | Draft → Pending Approval → Approved → Release → Completed | Submit, Emergency, Approve, Release, Complete, Reopen |
| Work Order | Requested → Approved → In Progress → Closed | Approve, Start, Complete, Reopen |
| Work Order Activity | Awaiting Resources → Ready → In Progress → On Hold → Completed → Closed | Allocate, Start, Hold, Resume, Complete, Close, Reopen |
| Safety Permit | Draft → Requested → Approved → Active → Expired/Cancelled | Submit, Approve, Activate, Expire, Cancel, Renew |
| Condition Monitoring | Active → Warning → Critical → Resolved | Warn, Escalate, Resolve |
| Purchase Order | Draft → Open → Closed/Rejected/Cancelled | Approve, Reject, Complete, Cancel |

---

## Appendix B — Keyboard Shortcuts & Tips

### General Tips

- Use **Search** in the list view to quickly find records by any visible field
- **Link fields** (dropdown selectors) can be filtered by typing — start typing to narrow options
- **Child tables** support inline editing — add/edit/delete child records directly from the parent form
- **Attachments** can be uploaded by drag-and-drop onto the attachment area
- **Bulk actions** — Select multiple records in list view for bulk operations
- Use **Ctrl+S** / **Cmd+S** to save the current record
- **Tree views** — Entities like Location and Asset Class support hierarchical tree display when configured

### Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Cannot see an entity in sidebar | Contact admin to verify your role has `can_read` and `in_sidebar` for that entity |
| Cannot create/edit records | Verify your role has `can_create`/`can_update` permission |
| Workflow action not available | The transition may be role-restricted — check with admin |
| SLA showing "Breached" | The record has exceeded its time limit in the current state |
| Import failing | Download a fresh template and verify all required fields are filled |
| Real-time notifications not appearing | Check browser notifications are allowed for the application |

---

*End of User Manual — EAM-CHI v1.0*
