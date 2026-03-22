# Installing an Asset — Step-by-Step Manual

> This document explains, in plain language, how to install an asset in the system using the **formal path** (no bypass). The formal path creates a proper paper trail through a Maintenance Request and Work Order before the asset is physically installed to a Position.

---

## Overview

Installing an asset means recording that a piece of equipment or asset has been physically placed at a specific Position (e.g., a room, rack, or mounting point). The system tracks this through a chain of records:

```
Asset → Maintenance Request → Work Order → Work Order Activity → Asset Position
```

Once the Asset Position is created, the system automatically marks the asset as **installed** and links it to the correct location.

---

## Prerequisites

Before you start, make sure:

- The asset exists and is in either the **Acquired** or **Inspected** workflow state.
- The asset has `bypass_process` set to **No** (formal path).
- There is no open (unremoved) Asset Position for this asset. If one exists, you must close it first by setting a `Date Removed`.
- A **Position** record exists for the physical location where the asset will be installed.

---

## Step 1 — Trigger "Install Asset" on the Asset

1. Open the Asset record.
2. Click the workflow action button **"Install Asset"**.
3. The system will:
   - Create a **Work Order Activity (WOA)** in `Awaiting Resources` state.
   - Create a **Maintenance Request (MR)** linked to that WOA, auto-advanced to `Approved` state.
   - Transition the Asset from its current state to `Active`.
   - Redirect you to the newly created Maintenance Request.

> **What was created:** MR record + WOA record. No Asset Position yet.

---

## Step 2 — Set the Position on the Work Order Activity

The WOA needs to know **where** the asset will be installed. This must be set manually.

1. Open the **Work Order Activity** record (linked from the Maintenance Request or accessible from the sidebar).
2. Find the **Position** field.
3. Select the target Position (e.g., `POS-0007 — Projector Stuff`).
4. Save the record.

> **Why:** The WOA is what eventually creates the Asset Position record. Without a Position set here, completion will be blocked.

---

## Step 3 — Release the Maintenance Request to Create a Work Order

1. Open the **Maintenance Request** record.
2. Click the workflow action **"Submit for Resolution"**.
3. The system will:
   - Transition the MR from `Approved` → `Release`.
   - Automatically create a **Work Order (WO)** and link it to the WOA.
   - Redirect you to the newly created Work Order.

> **What was created:** WO record, now linked to the WOA.

---

## Step 4 — Progress the Work Order Activity to "In Progress"

The WOA must pass through its workflow states before it can be completed.

1. Open the **Work Order Activity** record.
2. Click **"Allocate"** — moves state from `Awaiting Resources` → `Ready`.
   - Note: If a Planned Maintenance Activity is linked, the system will check that labor, equipment, and parts are assigned before allowing this step.
3. Click **"Start Activity"** — moves state from `Ready` → `In Progress`.

---

## Step 5 — Complete the Work Order Activity

This is the key step that creates the Asset Position.

1. While the WOA is in `In Progress` state, click **"Complete"**.
2. The system will:
   - Look up the activity type (must be "Install Asset").
   - Validate that a **Position** is set on the WOA.
   - Create an **Asset Position** record linking the Asset to the Position, with today's `date_installed`.
   - Update the **Position** record: set `current_asset` to this asset.
   - Update the **Asset** record: copy `location`, `system`, and `position` from the Position.
   - Close the linked Maintenance Request by setting `closed_date` to today.
   - Redirect to the Asset record.

> **What was created:** Asset Position record (e.g., `APOS-0031`).

---

## Step 6 — Verify the Installation

After completion, confirm the following:

| Record | What to Check |
|---|---|
| **Asset** | `workflow_state` = `active` (or `installed` depending on config), `position` = the selected Position ID, `location` updated |
| **Asset Position** | Record exists with `asset`, `position`, and `date_installed` filled; `date_removed` is blank |
| **Position** | `current_asset` = the installed asset ID |
| **Maintenance Request** | `workflow_state` = `release`, `closed_date` filled |
| **Work Order Activity** | `workflow_state` = `completed` |
| **Work Order** | Linked to WOA |

---

## Full Record Chain (Summary)

```
[Asset A-00059]
    ↓ Install Asset (workflow action)
[Maintenance Request MTREQ-00106]   ← auto-approved
[Work Order Activity WOACT-00098]   ← position set manually

    ↓ Submit for Resolution (on MR)
[Work Order WO-00032]               ← auto-created, linked to WOA

    ↓ Allocate → Start Activity → Complete (on WOA)
[Asset Position APOS-0031]          ← position=POS-0007, asset=A-00059

    ↓ After-save / hook
[Asset A-00059]                     ← location, position, system updated
[Position POS-0007]                 ← current_asset = A-00059
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Asset still has an open position record" | A previous Asset Position exists without `date_removed` | Open the old Asset Position and set a `Date Removed` |
| "Cannot complete: no Position specified" | The WOA has no Position set | Edit the WOA and select a Position before completing |
| "Work Item (Asset) not found" | The WOA's `work_item` field is blank | Ensure the WOA was created with the correct asset linked |
| Asset Position not created after completing WOA | Activity type `menu` is not "Install Asset" | Verify the Request Activity Type record has `menu` = "Install Asset" |
| MR stuck at "Approved" | Need to progress it manually | Click "Submit for Resolution" on the MR |

---

## Bypass Path (Alternative)

If the asset has `bypass_process = Yes`, clicking "Install Asset" will **skip** the MR/WO/WOA chain entirely and create the Asset Position directly. This is a shortcut for assets that don't require formal approval.

The formal path described in this document is required when `bypass_process = No`.
