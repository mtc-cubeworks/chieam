Stock Count and Inventory Adjustment Workflow Documentation

Overview

Stock Count operates with a parent-child relationship where Stock Count Lines are child records of the Stock Count. This document defines the comprehensive business rules, automated workflows, and safety validations governing the Stock Count lifecycle, from initialization and physical counting to final ledger reconciliation.

- The parent workflow movement does not directly affect the child, since child lines do not have individual workflow states.

- Inventory Adjustment operates under the same parent-child relationship logic.

---

User Interface

Stock Count Tabs

- **Lines:** View and manage stock count line items.

Stock Count States & Actions

| State       | Description                                | Available Actions | Next State |
| ----------- | ------------------------------------------ | ----------------- | ---------- |
| **Planned** | Initial state when Stock Count is created. |

| Start Stock Count, Find Stock Count Lines.

| In Progress

|
| **In Progress** | Progressing for exporting lines and importing counted quantities.

| Approve, Import/Export.

| Approved

|
| **Approved** | Stock Count approved for Inventory Adjustment.

| Complete.

| Closed

|
| **Closed** | Final state; process is done and closed.

| None.

| None

|

---

Field Definitions

- **Store:** Location where the inventory items are generally stored.

- **Site:** The branch or place of an organization or company.

- **Method:** Controls how the "Snapshot Quantity" is displayed.

- **0 Blind:** "Snapshot Quantity" field is hidden to ensure unbiased counting.

- **Guided:** "Snapshot Quantity" field shows the actual system quantity.

- **Basis:** Criteria for fetching inventory data:

- **Full:** The whole inventory item data from the selected "Store" and "Site".

- **ABC:** By quality or class; once selected the "ABC's Code" field will show.

- **A:** Inventory items that are class or quality "A".

- **B:** Inventory items that are class or quality "B".

- **C:** Inventory items that are class or quality "C".

- **Selection:** Selected inventory item data from the selected "Store" and "Site".

- **Freeze Policy:** Handles items currently in adjustment that are selected for other processes.

- **None:** No restrictions.

- **Freeze:** Items cannot be selected for other transaction processes.

- **Warn:** System warns the user if items are selected for other processes.

- **Snapshot At:** Current datetime when the Stock Count state moves to "In Progress".

---

Available Form Actions

Find Stock Count Lines

- **Available when:** Stock Count is in "Planned" state.

- **Functionality:** Get inventory item records based on set data from the following fields: Store, Site, and Basis.

- **Logic:** Create Stock Count Line records (1 Inventory record to 1 Stock Count Line record) and fill the following fields based on the Inventory record:

- stock_count: Stock Count parent id.

- inventory: Inventory id.

- item: Item from Inventory.

- asset_tag: asset_tag from Inventory.

- serial_nos: serial_number from Inventory.

- bin: bin_location from Inventory.

- zone: zone from Inventory.

- uom: unit_of_measure from Inventory.

- snapshot_qty: actual_inv from Inventory (depends on data of "Method").

---

Workflow Transition Logic

1. Initial State (Planned)

- **Logic:** The system captures a "Snapshot Qty" representing the current system balance for selected items.

- **Scope:** Items are fetched based on Full (entire store), ABC (classification), or Selection.

- **Constraint:** Items already associated with an "In Progress" Stock Count are excluded to prevent double-counting.

- **Business Rules:** Users can add or edit lines. The system creates one Stock Count Line per Inventory record.

2. In Progress (Counting & Control)

- **Logic:** Once saved and started, the system applies the Freeze Policy to the underlying Inventory records.

- **Rule:** Depending on the policy (Freeze or Warn), items are restricted to ensure the snapshot remains valid during the physical count.

- **Mutual Exclusivity:** An inventory record cannot be simultaneously "Frozen" and "Warned." Setting one policy automatically clears the other.

3. Approved (Reconciliation)

- **Logic:** The system validates variances and triggers a formal Inventory Adjustment.

- **Negative Inventory Guardrail:** No adjustment is permitted if the final result would be negative stock.

- **Validation Formula:**

- **Checkpoints:** This safety check is performed during manual updates, bulk imports, and at the final approval stage.

---

Calculation and Financial Logic

The system maintains real-time tracking of discrepancies using standardized calculations:

- **Variance Quantity:**

- **Variance Value:**

- **Discovery Logic:** If an item is counted but has no existing system record, the system automatically includes it in the adjustment to initialize the inventory.

---

Automated Reconciliation (Post-Approval)

Upon Approval, the system automates the transition from "Stock Count" to "Inventory Adjustment":

| Feature               | Business Rule                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| **Selective Posting** | Only lines with a non-zero variance (or missing records) are pushed to the Inventory Adjustment. |

|
| **Valuation** | Adjustments use the current unit_cost from the Item Master to ensure financial accuracy.

|
| **Audit Traceability** | Every generated Inventory Adjustment is stamped with the source Stock Count ID for a permanent audit trail.

|

---

Inventory Adjustment

Inventory Adjustment Tabs

- **Lines:** View and manage inventory adjustment line items.

Inventory Adjustment States & Actions

| State     | Description                                             | Available Actions | Next State |
| --------- | ------------------------------------------------------- | ----------------- | ---------- |
| **Draft** | Initial state when the Inventory Adjustment is created. |

| Submit.

| Submitted

|
| **Submitted** | The Inventory Adjustment is submitted for initial review.

| Post, Cancel.

| Posted, Cancelled

|
| **Posted** | Final State: The Inventory Adjustment is posted to Inventory.

| None.

| None

|
| **Cancelled** | Final State: The Inventory Adjustment is cancelled.

| None.

| None

|

Field Definitions

Inventory Adjustment

- **Reference Doctype:** By default, the value is "Inventory".

- **Posting Datetime:** The current datetime recorded when the state moves to "Posted".

- **Location/Store/Site/Cost Center:** Common data derived from the selected Inventory records in the Stock Count Lines.

Inventory Adjustment Line

- **Rule:** 1 Stock Count Line = 1 Inventory Adjustment Line.

- **Mapping:**

- Inventory Adjustment: Parent ID.

- Inventory: Data from Inventory ID in Stock Count Line.

- Item: Data from Item ID in Stock Count Line.

- Asset Tag / Serial Number: From Stock Count Line.

- Bin / Zone: From Stock Count Line.

- Unit of Measure: From Stock Count Line.

- Current Quantity: From Snapshot Quantity in Stock Count Line.

- Adjustment Quantity: From Variance Quantity in Stock Count Line.

- Current Rate: Data from the Unit Cost of the selected Item.

- Adjustment Value: From Variance Value in Stock Count Line.

- Inventory Adjustment Account: Specified account for adjustment entries.

- Inventory Account: Specified account for inventory.

---

Posting Synchronization

When an Inventory Adjustment is posted, the system synchronizes adjustment quantities with master Inventory records. The system updates existing stock (Actual and Available) or initializes new records, maintaining accurate stock positioning (Location, Store, Zone, Bin).

Logic Breakdown (The "Post" Action)

1.  **Validation:** Verifies the adjustment contains at least one line item; otherwise, it terminates with an error.

2.  **State Detection:**

- **Case A (Existing Record):** If linked to an Inventory ID, an additive update is performed. It adds adjusted_qty to both actual_inv and available_inv and resets freeze/warn flags.

- **Case B (New Record):** If no Inventory ID is linked, a new master record is created using attributes from the adjustment line.

3.  **Audit & Persistence:** The adjustment line is updated with the new reference and committed to the database.

---

Inventory Adjustment Logic Matrix

| Scenario            | Condition                    | System Behavior |
| ------------------- | ---------------------------- | --------------- |
| **Existing Record** | Inventory ID exists on Line. |

| **Additive Update:** Updates actual_inv and available_inv by adding adjusted_qty. Resets freeze and warn flags to 0.

|
| **New Record** | Inventory ID is null/empty.

| **Create New:** Initializes a new Inventory record with adjusted_qty. Maps all location and item attributes.

|
| **Negative Guardrail** | Final result would be < 0.

| <br>**Block:** Adjustment is blocked/permitted only if the result is .

|
| **Zero Variance** | Variance Qty is 0.

| <br>**Skip:** Line is generally excluded from adjustment generation (Selective Posting).

|

---

Business Validation Rules

1.  **Import/Export Permissions:** Only available in "In Progress" state with existing line data.

2.  **Duplicate Prevention:** Prevents duplicate lines for the same Item/Bin/Zone combination in a single Stock Count.

3.  **State Synchronization:** Parent state changes do not affect child line states.

4.  **Data Integrity:** "Find Stock Count Lines" is only available in the "Planned" state.

5.  **Posting Validation:** An Inventory Adjustment cannot be posted if it contains no lines.

6.  **Freeze Policy Reset:** Successful posting MUST reset freeze and warn flags on the associated Inventory record to 0.
