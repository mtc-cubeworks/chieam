Purchase Receipt & Inventory Management

1. Workflow Initiation & Data Mapping
   The inventory receiving process is initiated upon the approval of a specific Purchase Order (PO) Line.
   ● UI Trigger: Once a PO Line reaches the "Approved" state, the system enables the creation of a Purchase Receipt. The "Purchase Receipt" tab becomes is shown.
   ● Data Inheritance: When a user creates a new Purchase Receipt record, the system automatically populates key fields by fetching data directly from the linked Purchase Order Line to ensure data integrity. (post_saving)

   Field Mapping Definition:
   Source (PO Line) | Target (Purchase Receipt)
   purchase_order_line (ID) | purchase_order_line
   line_row_num | pr_row_no
   item_id | item
   site | site
   department | department
   cost_code | cost_code

2. User Execution: The "Confirm Receipt" Action
   The creation of the Purchase Receipt is a two-step process to prevent premature inventory updates:
   1. After saving "/new": The user first saves the Purchase Receipt record. At this stage, no inventory impact occurs.
   2. Action Button: Only after the record is saved does the "Confirm Receipt" action button appear on the interface.
   3. Validation Trigger: Clicking "Confirm Receipt" executes the backend logic (update_inventory). This is the critical gatekeeper that runs the validations detailed below.

3. Backend Validation Rules (The "Confirm" Logic)
   Upon clicking "Confirm Receipt", the system executes a transactional block. If any of the following checks fail, the system performs a Rollback, reverting all changes to ensure database consistency.
   ● Existence Check: The system verifies the existence of the Purchase Receipt, linked PO Line, linked PR Line (via RFQ), and Item Master.
   ● Duplicate Prevention: The system checks the generated_inventory flag. If it is already set to 1, the process halts to prevent double-counting.
   ● Item Type Restriction: Items classified as "Service Item" or "Non-Inventory Item" are blocked from generating stock.
   ● Over-Receiving Logic (Critical):
   ○ The system calculates: (Current Receipt Qty + Previous PO Received Qty).
   ○ Rule: The total must not exceed the original Ordered Quantity on the PO Line.
   ○ Outcome: If the total exceeds the order, the system returns an error: "Cannot receive X items. Only Y remaining."
4. Procurement Document Updates
   If validation passes, the system updates the status of upstream documents:
   ● Purchase Order (PO) Line: Updates quantity_received. Workflow State transitions to "Receive All Items" (if fully satisfied) or "Receive Partial Items".
   ● Purchase Request (PR) Line: Updates qty_received. Workflow State transitions to "Receive All Items" (if fully satisfied) or "Receive Partial Items".
5. Record Generation Specifications

Asset States & Actions
State | Description | Available Actions | Next State
Acquired | Initial state for both manual Asset creation and by "Confirm Receipt" action | Inspect Asset | Inspected
Acquired | Initial state for both manual if Asset is an Equipment creation and by "Confirm Receipt" action | Putaway | Inactive
Inspected | Asset is done inspection and ready to be installed | Install Asset | Active
Inspected | When an Asset is a Fixed Asset and it’s ready to be commissioned | Commission | Active
Inspected | When an Equipment is an Asset and stored in a warehouse or supply room | Putaway | Inactive
Inspected | When an Asset that has been ordered is not in good condition and quality upon inspection | Failed Inspection | Failed Inspection
Active | When an Installed Asset will be undergoing a maintenance | Maintain Asset | Under Maintenance
Active | When an Issued Equipment is an Asset and stored in a warehouse or supply room | Putaway | Inactive
Active | When an Asset is a Commissioned Fixed Asset and will be decommissioned | Decommission | Decommissioned
Inactive | Asset will be installed to a position. | Install Asset | Active
Inactive | When an Equipment is an Asset and being issued or used. | Issue Equipment | Active
Inactive | When an Asset needs to be stored in a warehouse or supply room. | Putaway | Inactive
Inactive | When an Asset needs to retire. | Retire Asset | Decommissioned
Inactive | When an Asset needs to be repaired inside of the organization. | Internal Repair | Under Repair
Inactive | When an Asset needs to be repaired outside of the organization. | Send to Vendor | Decommissioned
Under Maintenance | When an Asset that was installed and completed the maintenance without the need to repair. | Complete | Active
Under Maintenance | When an Asset that was installed will be removed for repair. | Remove Asset | Inactive
Under Repair | When an Asset is done repairing. | Finish Repair | Inactive
Decommissioned | When an Asset was failed repair and to be disposed | Dispose | Disposed
Decommissioned | When an Asset is a Fixed Asset and it’s ready to be recommissioned | Recommission | Active

Maintenance Request States & Actions
State | Description | Available Actions | Next State
Draft | Initial state for both manual Maintenance Request creation and by "Confirm Receipt" action | Submit for Approval | Pending Approval
Draft | Initial state for both manual Maintenance Request creation and by "Confirm Receipt" action | Submit for Emergency | Release
Pending Approval | Approve | Approved
Approved | Submit for Resolution | Release
Release | Complete | Completed
Completed | Reopen | Release

Work Order Activity States & Actions
State | Description | Available Actions | Next State
Awaiting Resources | Initial state for both manual Work Order Activity creation and by "Confirm Receipt" action | Allocate | Ready
Ready | Start Activity | In Progress
In Progress | Put On Hold | On Hold
In Progress | Complete | Completed
On Hold | Resume | In Progress
Completed | Reopen | In Progress
Completed | Close | Closed

The system dynamically generates records based on the item's classification.
A. Inventory Record Creation
● Identification: A temporary Asset Tag is generated automatically using the format Temp-Tag-[RandomHash].
● Location Strategy: The system attempts to map the receiving location to a specific parent Store.
● Costing: The unit_cost and financial_asset_number are locked in based on the Purchase Order data.
● Transaction Type: Hardcoded as "Add".
B. Asset Record Creation
For items classified as Asset or Fixed Asset, the system creates a parallel Asset record.
● Bi-Directional Linking:
○ The Inventory record is updated with the asset ID.
○ The Asset record is updated with the inventory ID.
● Property Inheritance: If the item belongs to an asset_class, the system iterates through the Asset Class Property table and copies all defined property templates to the new Asset record.
● State: Defaults to "Acquired".
C. Equipment Registration
If the item is flagged as Equipment (is_equipment == 1):
● An Equipment record is created immediately.
● Type: Defaults to "Owned".
● Location: Linked to the Site and Receiving Location.
D. Automated Inspection Workflow
If the item requires inspection (inspection_required == 1), the system triggers an accelerated maintenance workflow:
● Work Order Activity: Created with the status "Awaiting Resources".
● Maintenance Request: Created with a Due Date set to 7 days from the current date.
● Auto-Approval: The system automatically executes workflow transitions on the Maintenance Request, moving it from Draft -> Submit for Approval -> Approve. This ensures the inspection request is active immediately without manual administrative approval. 6. Inventory & Asset Generation Logic (Matrix)
The system generates records based on the specific Item Type and Serialization settings defined in the Item Master.
Item Type Serialization System Behavior
Asset Item Serialized 1-to-1 Creation: Creates individual Inventory and Asset records per unit.

Workflow:

• If Inspection Required: Creates Maintenance Request.

• If Is Equipment: Creates Equipment record + "Putaway".

• Default: Triggers "Inspect Asset".
Asset Item Non-Serialized Batch Update: Updates existing Inventory quantity (or creates new).

Workflow: Creates a single Asset record for the batch. Triggers "Putaway" (if Equipment) or "Inspect Asset".
Fixed Asset Serialized 1-to-1 Creation: Creates individual records.

Workflow: Triggers "Putaway" and "Install Asset".
Fixed Asset Non-Serialized Batch Update: Updates inventory quantity.

Workflow: Creates Asset record, triggers "Inspect Asset" and "Install Asset".
Regular Serialized 1-to-1 Creation: Creates individual Inventory records per unit. Returns specific action need_update_serial_num.
Regular Non-Serialized Batch Update: Increases actual_inv on existing Inventory record at that location. If no record exists, creates a new one. 7. Post-Processing: Batch Serial Number Assignment
For serialized items, the system utilizes a secondary endpoint (update_inventory_serialno) to handle the assignment of serial numbers after the initial records are created.
● Input: Accepts a JSON list of Inventory IDs and their corresponding Serial Numbers.
● Logic: Iterates through the list and updates the serial_number field on the Inventory records.
● Safety: This is also transactional; if one update in the list fails, the entire batch update is rolled back. 8. Completion
● Flagging: The Purchase Receipt is marked as processed (generated_inventory = 1).
● Return: The system returns a success status, the specific action performed, and a navigation path to the newly created records (Inventory, Asset, or Maintenance Request).
