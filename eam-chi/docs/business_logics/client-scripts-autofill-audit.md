# Client Scripts Auto-Fill Audit

This document audits all client scripts in the Frappe EAM system to identify instances where selecting a value in one field auto-fills other fields.

## Summary of Auto-Fill Patterns

### 1. **Work Order Activity** (`work-order-activity.client.ts`)

Status: Not fulfilled

#### On Load (New Documents):

- **work_order** → fills: `site`, `department`
- **work_item** → fills: `location`, `site`, `department`, updates `activity_type` query

#### On Field Change:

- **location** → updates `work_item` query filter
- **work_item** (new documents only) → fills: `location`, clears `activity_type`
- **work_item** → updates `activity_type` query filter based on asset workflow state

### 2. **Asset** (`asset.client.ts`)

Status: Accomplished

#### On Load:

- Sets initial queries: `system` (filtered by location), `model` (filtered by manufacturer), `department` (filtered by site)

#### On Field Change (New Documents Only):

- **location** → fills: `site`
- **manufacturer** → clears: `model`
- **site** → clears: `department`

#### On Field Change (All Documents):

- **manufacturer** → updates `model` query filter
- **location** → updates `system` query filter
- **site** → updates `department` query filter

### 3. **Maintenance Request** (`maintenance-request.client.ts`)

Status: Accomplished

#### On Load:

- **asset** (new documents) → fills: `location`, `site`, `department`
- **asset** (all documents) → fills: `location`, `site`, `department`, stores `asset_workflow_state`
- Sets `requested_date` to today if empty
- Sets `department` query filter based on `site`

#### On Field Change:

- **planned_maintenance_activity** → updates `asset` query filter
- **asset** (new documents) → fills: `location`, `site`, `department`, clears `request_type` if changed
- **asset** → updates `request_type` query filter based on asset workflow state
- **site** → updates `department` query filter

### 4. **Purchase Request** (`purchase-request.client.ts`)

Status: Not fulfilled

#### On Field Change (New Documents Only):

- **store** → fills: `site`

### 5. **Item Issue** (`item-issue.client.ts`)

Status: Accomplished

#### On Load:

- Sets `work_order_activity` query filter (workflow_state != 'Closed')
- **work_order_activity** → updates `cost_code` query filter based on WOA site
- **site** → updates `cost_code` query filter

#### On Field Change:

- **work_order_activity** → updates `cost_code` query filter based on WOA site
- **site** → updates `cost_code` query filter

### 6. **Stock Count** (`stock-count.client.ts`)

Status: Accomplished

#### On Field Change (New Documents Only):

- **store** → fills: `site`

### 7. **Purchase Receipt** (`purchase-receipt.client.ts`)

Status: Accomplished

#### On Load (New Documents):

- Sets `date_received` to today if empty
- Sets `receiving_location` from current user's location
- **purchase_request_line** → fills: `pr_row_no`, `item`, `site`, `department`, `account_code`

#### On Field Change (New Documents Only):

- **purchase_request_line** → fills: `pr_row_no`, `item`, `site`, `department`, `account_code`

### 8. **Transfer** (`transfer.client.ts`)

Status: Not fulfilled

#### On Field Change (New Documents Only):

- **transfer_type** → clears: `item_to_transfer`, `from_location`
- **inventory** → fills: `item_to_transfer`, `from_location`
- **labor** → fills: `item_to_transfer`, `from_location`
- **equipment** → fills: `item_to_transfer`, `from_location`

### 9. **Position** (`position.client.ts`)

Status: Accomplished

#### On Load (New Documents):

- **location** → fills: `site`

#### On Field Change (New Documents Only):

- **location** → fills: `site`

### 10. **Item Return** (`item-return.client.ts`)

Status: Accomplished

#### On Load (New Documents):

- **work_order_activity** → fills: `site`, `department`
- Sets `date_returned` to today if empty
- **work_order_activity** → updates `cost_code` query filter
- **site** → updates `cost_code` query filter

#### On Field Change:

- **work_order_activity** (new documents) → fills: `site`, `department`
- **work_order_activity** → updates `cost_code` query filter
- **site** → updates `cost_code` query filter

### 11. **Employee** (`employee.client.ts`)

Status: Not fulfilled

#### On Load:

- Sets `department` query filter based on `site`

#### On Field Change:

- **site** → updates `department` query filter

### 12. **Asset Class** (`asset-class.client.ts`)

#### On Load:

- Sets `parent_asset_class_id` query filter based on `equipment`

#### On Field Change:

- **equipment** → updates `parent_asset_class_id` query filter
- **manufacturer** (new documents) → clears: `model`

### 13. **Maintenance Plan** (`maintenance-plan.client.ts`)

#### On Load:

- Sets `model` query filter based on `manufacturer`

#### On Field Change:

- **manufacturer** → updates `model` query filter
- **manufacturer** (new documents) → clears: `model`

## Common Patterns

### Location → Site Cascade

Multiple forms use the pattern where selecting a `location` auto-fills the `site` field:

- Asset
- Maintenance Request
- Position
- Work Order Activity (indirectly through work_item)

### Site → Department Query Filter

Many forms filter the `department` field based on the selected `site`:

- Asset
- Maintenance Request
- Employee
- Item Issue
- Item Return

### Parent → Child Field Queries

Several forms filter child fields based on parent selections:

- Manufacturer → Model (Asset, Maintenance Plan, Asset Class)
- Location → System (Asset)
- Equipment → Parent Asset Class (Asset Class)

### Work Order Activity as Source

WOA is commonly used as a source for site and department information:

- Item Issue
- Item Return

### Store → Site Pattern

Forms dealing with inventory/stores commonly auto-fill site from store:

- Purchase Request
- Stock Count

## Key Observations

1. **New Document Check**: Most auto-fill operations only occur on new documents (checked via `!(form as any).name || (form as any).name === 'new'`)

2. **Query Updates**: Field changes often update query filters for related fields, not just direct field values

3. **Clear Dependent Fields**: When a parent field changes, dependent child fields are often cleared to maintain data integrity

4. **API Calls**: Auto-fill data is typically fetched via `get_description` or custom API endpoints

5. **Workflow State Awareness**: Some forms use workflow state to determine field availability and filtering

## Files Without Auto-Fill Logic

The following client scripts don't contain auto-fill logic:

- `bin.client.ts`
- `department.client.ts`
- `equipment.client.ts`
- `incident-report.client.ts`
- `inspection.client.ts`
- `inventory-adjustment.client.ts`
- `inventory-adjustment-line.client.ts`
- `inventory.client.ts`
- `item-issue-line.client.ts`
- `item-return-line.client.ts`
- `item.client.ts`
- `labor.client.ts`
- `maintenance-calendar.client.ts`
- `maintenance-condition.client.ts`
- `maintenance-equipment.client.ts`
- `maintenance-interval.client.ts`
- `maintenance-order-detail.client.ts`
- `maintenance-order.client.ts`
- `maintenance-parts.client.ts`
- `putaway.client.ts`
- `stock-count-line.client.ts`
- `stock-count-task.client.ts`
- `store.client.ts`
- `system.client.ts`
- `transfer-receipt.client.ts`
- `work-order-activity-logs.client.ts`
- `work-order.client.ts`
