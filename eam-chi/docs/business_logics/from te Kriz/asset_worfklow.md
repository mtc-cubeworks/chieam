# Asset Workflow Documentation

## Overview

The Asset workflow as it moves it creates a maintenance request record and work order activity record. The system automates the lifecycle of physical assets from creation and initialization to maintenance, deployment, and eventual disposal. The logic acts as a central controller that intercepts user actions and system events to generate necessary transactional records, synchronize inventory data, and enforce workflow approvals automatically.

---

## User Interface

### Asset Tabs

- **Asset Property:** View and manage asset property records (inherited from Asset Class).

- **Asset Position:** View and manage asset position records (installation history).

- **Sub Asset:** View and manage sub-asset records.

- **Maintenance Request:** View and manage maintenance request records linked to this asset.

- **Sensor:** View and manage sensor records.

- **Incident:** View and manage incident records.

---

## Asset Classification

### 1. Asset Item

Moveable assets classified into two distinct roles:

- **Installable Components:** Items that are installed, removed, and maintained within a larger system.

- **Standalone Equipment:** Individual units that operate independently.

- **Lifecycle:** Both types are eventually disposed of at the end of their lifecycle.

### 2. Fixed Asset Item

Stationary assets that remain in one place. They are not installed or removed in the traditional sense.

- **Lifecycle:** Managed by being Decommissioned (taken offline) and Recommissioned (brought back online).

---

## Asset States & Actions

| State        | Description                          | Available Actions | Next State |
| ------------ | ------------------------------------ | ----------------- | ---------- |
| **Acquired** | Initial state when Asset is created. |

| • Inspect Asset

<br>

<br>• Putaway (for asset item that is an equipment).

| Inspected, Inactive

|
| **Inspected** | The asset is inspected and ready for installment.

| • Install Asset (for asset item that is not an equipment)

<br>

<br>• Commission (for fixed asset item)<br>

<br>• Putaway<br>

<br>• Failed Inspection.

| Active, Inactive, Failed Inspection

|
| **Failed Inspection** | Final State: During inspection an asset is found not in good quality.

| None.

| None

|
| **Active** | Asset is already installed, is unused, or stored in a store room.

| • Maintain Asset (for asset item that is not an equipment)

<br>

<br>• Putaway (for asset item that is an equipment)<br>

<br>• Decommission (for fixed asset item).

| Under Maintenance, Inactive, Decommissioned

|
| **Inactive** | Asset is inactive.

| • Install Asset (for asset item that is not an equipment)

<br>

<br>• Issue Equipment (for asset item that is an equipment)<br>

<br>• Putaway (for asset item that is not an equipment)<br>

<br>• Retire Asset (for asset item that is not an equipment)<br>

<br>• Internal Repair (for asset item that is not an equipment)<br>

<br>• Send to Vendor (for asset item that is not an equipment).

| Active, Inactive, Decommissioned, Under Repair

|
| **Under Maintenance** | Asset is currently under maintenance.

| • Complete

<br>

<br>• Remove Asset.

| Active, Inactive

|
| **Under Repair** | Asset is done repairing.

| • Finish Repair.

| Inactive

|
| **Decommissioned** | Asset is under decommissioning.

| • Dispose

<br>

<br>• Recommission (for fixed asset item).

| Disposed, Active

|
| **Disposed** | Final State: Asset is disposed.

| None.

| None

|

---

## Asset Initialization & Property Synchronization

**Trigger:** Occurs immediately after an asset record is saved in the system.

### Business Logic

- **Inheritance of Properties:** When an asset is created, the system identifies its assigned Asset Class and retrieves the master list of standard properties associated with that class. The system applies any missing ones to the specific asset instance.

- **Automated Inventory Provisioning:** The system checks a global Configuration setting to determine if process bypass is enabled. If enabled, and the asset lacks a linked inventory record, the system automatically generates a new Inventory ledger entry initialized with a positive quantity and linked to the asset's site and location.

- **Data Synchronization:** To maintain data integrity, the system compares the Asset Tag on the main record with the linked Inventory record and updates the Inventory record if a discrepancy is found.

### Technical Specification

- **Transaction Management:** The entire initialization process is wrapped in a database savepoint. If any step fails, the system performs a full rollback to prevent partial data corruption.

- **System Privileges:** Inventory records are created using system-level overrides to ensure background automation is not hindered by specific user permissions.

---

## Workflow Transition Logic

| Action Category                       | Specific Actions | Logic & Validation | Generated Records |
| ------------------------------------- | ---------------- | ------------------ | ----------------- |
| **Maintenance, Inspection, & Repair** | • Inspect Asset  |

<br>

<br>• Maintain Asset<br>

<br>• Internal Repair<br>

<br>• Send to Vendor.

| <br>**Activity Lookup:** System retrieves the specific Activity Type definition .

<br>

<br>**Workflow Automation:** System automatically transitions the Maintenance Request (Draft -> Submit -> Approve) to expedite the process.

| <br>**Work Order Activity:** Created with status "Awaiting Resources" .

<br>

<br>**Maintenance Request:** Created and linked to the Work Order Activity.

|
| **Inventory Movement** | • Issue Equipment.

| <br>**Storage Lookup:** Looks up current Inventory record for storage details (Store, Bin, Zone).

| <br>**Item Issue:** Formally tracks checkout from warehouse.

|
| **Installation & Commissioning** | • Install Asset

<br>

<br>• Remove Asset<br>

<br>• Commission<br>

<br>• Putaway.

| <br>**Return Logic:** Links asset's serial number and quantity to return item to storage.

<br>

<br>**Bypass Logic Check:** If Bypass OFF, enforces formal process via Maintenance Request. If Bypass ON, skips request phase and directly logs installation.

<br>

<br>**Removal Validation:** Checks Asset Position history. Enforces that previous position must have "Date Removed" before new position is established.

| • **Putaway:** Transaction linking item to storage .

<br>

<br>• **(Bypass OFF)** Maintenance Request .

<br>

<br>• **(Bypass ON)** Asset Position (with "Date Installed" logged) .

<br>

<br>• **Removal** Asset Position.

|
| **End of Life** | • Dispose.

| **Validation:** If "Fixed Asset", checks if asset is formally removed from last known Asset Position. If position is still open, returns error.

| <br>**Disposed Record:** Marks asset as no longer in service.

|
| **Simple State Transitions** | • Failed Inspection

<br>

<br>• Complete<br>

<br>• Retire<br>

<br>• Decommission<br>

<br>• Recommission.

| **Direct Transition:** No secondary documents required. System triggers standard Workflow Engine to update document state.

| <br>**Asset Status Update**.

|

---

## Technical Architecture Specifications

### Transactional Integrity & Error Handling

- **Atomic Operations:** Both the initialization and lifecycle management functions utilize database savepoints to ensure complex operations are treated as a single atomic unit.

- **Rollback Strategy:** In the event of an exception, the system initiates a rollback to the savepoint, reverting all changes, and presents the user with a structured error message.

Would you like me to help you define an Asset Class and its standard properties for a specific type of equipment?
