# Purchase Request Workflow Documentation

## Overview

Purchase Request operates with a parent-child relationship where Purchase Request Lines are child records of the Purchase Request. The parent workflow movement directly affects the child workflow states.

## User Interface

### Purchase Request Tabs

- **Lines** - View and manage purchase request line items
- **RFQ** - Request for Quotation management (hidden when PR is in "Rejected" state, hidden when there are no PR Lines)

## Purchase Request States & Actions

| State            | Description                      | Available Actions                          | Next State                  |
| ---------------- | -------------------------------- | ------------------------------------------ | --------------------------- |
| Draft            | Initial state when PR is created | Submit for Review                          | Pending Review              |
| Pending Review   | PR submitted for initial review  | Submit for Approval                        | Pending Approval            |
| Pending Approval | PR awaiting final approval       | Approve, Reject Purchase Request           | Approved, Rejected          |
| Approved         | PR approved for processing       | Generate RFQ, Create Purchase Order, Close | Closed, RFQ Draft, PO Draft |
| Rejected         | PR rejected                      | Revise Purchase Request                    | Draft                       |
| Closed           | PR completed and closed          | -                                          | -                           |

## Purchase Request Line States

| State              | Description                 | Notes                           |
| ------------------ | --------------------------- | ------------------------------- |
| Draft              | Initial state for new lines | Editable                        |
| Pending Approval   | Line awaiting approval      | Editable                        |
| Approved           | Line approved for ordering  | Not editable, can receive items |
| Rejected           | Line rejected               | Not editable                    |
| Partially Received | Some items received         | Updated via Purchase Receipt    |
| Fully Received     | All items received          | Updated via Purchase Receipt    |
| Complete           | Line fully processed        | Final state                     |

## RFQ States & Actions

| State     | Description                                                          | Available Actions          | Next State |
| --------- | -------------------------------------------------------------------- | -------------------------- | ---------- |
| Draft     | Initial state for both manual RFQ creation and "Generate RFQ" action | Submit Source              | Sourcing   |
| Sourcing  | RFQ ready for vendor sourcing                                        | Print RFQ                  | Review     |
| Review    | RFQ under review                                                     | Award (if vendor selected) | Awarded    |
| Awarded   | RFQ awarded to vendor                                                | -                          | Order      |
| Order     | RFQ converted to Purchase Order                                      | -                          | -          |
| Cancelled | RFQ cancelled                                                        | -                          | -          |

## Available Form Actions

### Generate RFQ

- **Available when**: Purchase Request is in "Pending Review", "Pending Approval", or "Approved" state
- **Functionality**: Creates RFQ with Draft state, RFQ Lines will be initially blank

### Create Purchase Order

- **Available when**: Purchase Request is in "Approved" state
- **Functionality**:
  - Check all PR lines, get all vendors, create PO per vendor
  - Vendor field populated according to vendors in PR lines
  - Copy PR lines data to PO lines (grouped by vendor)
  - Source RFQ is null or empty
  - Date ordered is current time
  - Total amount is sum of all lines (qty \* price)

### Create Purchase Order from RFQ

- **Available when**: RFQ is in "Awarded" state
- **Functionality**:
  - Connect source RFQ
  - Get awarded_vendor from RFQ and use it to fill Vendor field
  - Copy RFQ lines data to PO lines
  - Date ordered is current time
  - Total amount is sum of all lines (qty \* price)

## Workflow Transition Logic

### 1. Initial State (Draft)

- **Purchase Request**: Draft state, fully editable
- **PR Lines**: Draft state, fully editable
- **Business Rules**:
  - Can add/edit lines to PR
  - Cannot proceed to next state if PR has no lines

### 2. Submit for Review

- **Purchase Request**: Moves to Pending Review
- **PR Lines**: Remain in Draft state
- **Business Rules**:
  - Both PR and PR Lines remain editable
  - Can still add new PR Lines

### 3. Submit for Approval

- **Purchase Request**: Moves to Pending Approval
- **PR Lines**: Move to Pending Approval
- **Business Rules**:
  - Both PR and PR Lines remain editable
  - Cannot add new lines (disabled)

### 4. Approve Purchase Request

- **Purchase Request**: Moves to Approved
- **PR Lines**: Move to Approved
- **Business Rules**:
  - Both PR and PR Lines become non-editable
  - Cannot add new lines (disabled)

### 5. Reject Purchase Request

- **Purchase Request**: Moves to Rejected
- **PR Lines**: Move to Rejected
- **Business Rules**:
  - Both PR and PR Lines become non-editable
  - Cannot add new lines

### 6. Close Purchase Request

- **Purchase Request**: Moves to Closed
- **Business Rules**:
  - All PR Lines must be in "Complete" state before closing
  - Validation prevents closing if any line is incomplete

### 7. Revise Purchase Request

- **Purchase Request**: Reverts to Draft
- **PR Lines**: Remain in Rejected state
- **Business Rules**:
  - PR Form becomes editable again
  - Can add new lines and edit them
  - Previously rejected lines remain disabled and non-editable

## Purchase Request Line State Logic

### Receipt Processing

- When PR Line is in "Approved" state, subsequent state changes are controlled by:
  - Purchase Order Line creation and updates
  - Purchase Receipt processing
- State progression: Approved → Partially Received → Fully Received → Complete

## RFQ Processing Logic

### RFQ Generation

- **Trigger**: "Generate RFQ" action on approved PR states
- **Process**:
  - Creates RFQ Lines (RFQ Log model will be removed)
  - RFQ Lines will be initially blank (no automatic copy from PR Lines)
  - RFQ enters "Sourcing" state
- **Printing**: RFQ can be printed in "Sourcing" state once RFQ Lines exist

### RFQ Line Structure

- **Parent Entity**: RFQ Line will be a child table linked to the main RFQ entity
- **Data Source**: Manually populated by users during RFQ sourcing process
- **Fields**: Will include item details, quantities, pricing, and vendor information
- **Naming**: Auto-format: RFQL-{#####}

## Purchase Order States & Actions

| State     | Description                      | Available Actions | Next State        |
| --------- | -------------------------------- | ----------------- | ----------------- |
| Draft     | Initial state when PO is created | Approve, Reject   | Open, Rejected    |
| Open      | PO approved and active           | Complete, Cancel  | Closed, Cancelled |
| Closed    | PO completed and closed          | -                 | -                 |
| Rejected  | PO rejected                      | -                 | -                 |
| Cancelled | PO cancelled                     | -                 | -                 |

### Purchase Order Business Logic

- **Upon Creation**: PO starts in Draft state
- **Draft → Open**: When "Approve" action is clicked, all PO Lines change to Approved state (not editable, cannot add lines)
- **Open State**: Shows Purchase Receipt tab in PO form
- **Draft → Rejected**: When "Reject" action is clicked, reject PO lines as well (not editable, cannot add lines)
- **Open → Closed**: Can only close when all PO Lines are in Closed state
- **Open → Cancelled**: Can only cancel if no lines are receiving OR all PO lines are still in "Approved" state. Once cancelled, all PO lines are cancelled (not editable)
- **Cancelled State**: Hide Purchase Receipt tab in PO form
- **NOTE FOR REVIEW**: What happens if one PO line is not in "Approved" state when trying to cancel?

## Purchase Order Line States

| State              | Description                    | Notes                           |
| ------------------ | ------------------------------ | ------------------------------- |
| Draft              | Initial state for new PO lines | Editable                        |
| Approved           | Line approved and active       | Not editable, can receive items |
| Rejected           | Line rejected                  | Not editable                    |
| Partially Received | Some items received            | Updated via Purchase Receipt    |
| Fully Received     | All items received             | Updated via Purchase Receipt    |
| Complete           | Line fully processed           | Final state                     |
| Cancelled          | Line cancelled                 | Not editable                    |

### Purchase Order Line Business Logic

- **Synchronized Movement**: PO Line and PR Line will move at the same time (or almost)
- **Receipt Control**: Only Purchase Receipt can change both workflow states
- **Receipt-based States**: Line statuses "Fully Received" and "Partially Received" based on Purchase Receipt qty_received compared to line request qty
- **Manual Cancellation**: If a PO line was manually cancelled, hide Purchase Receipt tab in PO form
- **Auto-close Logic**: For every "Fully Received" → "Complete" transition:
  - Check number of PO lines in PO vs number of "completed" PO lines
  - If all PO lines in the PO are complete, the PO header will automatically close
  - Implement automated return (via websocket or return)
  - Copy the same logic to PR Lines

## Business Validation Rules

1. **Line Requirement**: PR cannot advance from Draft without at least one line
2. **Edit Permissions**: Edit rights decrease as workflow progresses
3. **State Synchronization**: Parent state changes trigger child state updates
4. **Completion Validation**: All lines must be complete before PR can be closed
5. **Revision Handling**: Rejected lines remain locked during revision process
6. **RFQ Submit Source Validation**: Cannot submit RFQ from Draft to Sourcing if there are no RFQ lines
7. **RFQ Print Permission**: RFQ can only be printed when in Sourcing state
8. **RFQ Award Validation**: Cannot proceed to Awarded state if Awarded Vendor field is null or empty
9. **RFQ Awarded State Lock**: When RFQ is in "Awarded" state, cannot add lines, cannot edit both RFQ and Lines, but shows "Create Purchase Order" action button
10. **RFQ Review Award Validation**: In "Review" state, cannot award if Awarded Vendor is null or empty
11. **RFQ Cancelled State Lock**: When RFQ is cancelled, form and lines become disabled/uneditable, cannot print or attach documents
