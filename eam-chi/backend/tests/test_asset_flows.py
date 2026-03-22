"""Asset Flow Tests - Path A (Asset Item bypass=True) and Path B (Equipment)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from test_business_logic_flows import *

def test_asset_path_a():
    section("ASSET PATH A: Asset Item — Acquire → Inspect → Install → Maintain → Remove → Retire → Dispose")

    sub("AA.1 Create Asset (bypass_process=True for direct install)")
    asset_id = create_entity("asset", {
        "asset_tag": "TEST-PUMP-A001",
        "asset_class": ASSET_CLASS,
        "site": SITE,
        "department": DEPT,
        "location": LOCATION,
        "bypass_process": True,
        "is_equipment": False,
        "item": ITEM1,
    })
    if not asset_id:
        check(False, "AA.1 Create Asset", "Failed"); return None
    asset = get_entity("asset", asset_id)
    check(asset is not None, "AA.1 Asset created", asset_id)
    # Initial state is 'acquired' (shown as None before first transition)
    state = asset.get("workflow_state") if asset else None
    check(state in (None, "acquired", "Acquired"), "AA.1 Asset in Acquired state", str(state))

    sub("AA.2 Inspect Asset → Inspected")
    res = do_workflow("asset", asset_id, "inspect_asset")
    check(res is not None, "AA.2 inspect_asset workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "inspected", "AA.2 Asset → Inspected", asset.get("workflow_state") if asset else "None")

    sub("AA.3 Install Asset → Active (bypass=True: direct AssetPosition)")
    res = do_workflow("asset", asset_id, "install_asset")
    check(res is not None, "AA.3 install_asset workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "active", "AA.3 Asset → Active", asset.get("workflow_state") if asset else "None")
    positions = get_linked("asset_position", "asset", asset_id)
    check(len(positions) >= 1, "AA.3 Asset Position created", f"Found {len(positions)}")

    sub("AA.4 Maintain Asset → Under Maintenance")
    res = do_workflow("asset", asset_id, "maintain_asset")
    check(res is not None, "AA.4 maintain_asset workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "under_maintenance", "AA.4 Asset → Under Maintenance", asset.get("workflow_state") if asset else "None")

    sub("AA.5 Remove Asset → Inactive (closes AssetPosition)")
    res = do_workflow("asset", asset_id, "remove_asset")
    check(res is not None, "AA.5 remove_asset workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "inactive", "AA.5 Asset → Inactive", asset.get("workflow_state") if asset else "None")
    positions = get_linked("asset_position", "asset", asset_id)
    closed_pos = [p for p in positions if p.get("date_removed")]
    check(len(closed_pos) >= 1, "AA.5 Asset Position date_removed set", f"{len(closed_pos)} closed positions")

    sub("AA.6 Retire Asset → Decommissioned")
    res = do_workflow("asset", asset_id, "retire_asset")
    check(res is not None, "AA.6 retire_asset workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "decommissioned", "AA.6 Asset → Decommissioned", asset.get("workflow_state") if asset else "None")

    sub("AA.7 Dispose Asset → Disposed")
    res = do_workflow("asset", asset_id, "dispose")
    check(res is not None, "AA.7 dispose workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "disposed", "AA.7 Asset → Disposed", asset.get("workflow_state") if asset else "None")

    return asset_id


def test_asset_path_b():
    section("ASSET PATH B: Equipment — Acquired → Putaway → Issue → Putaway")

    sub("AB.1 Create Equipment Asset (bypass_process=True, is_equipment=True)")
    asset_id = create_entity("asset", {
        "asset_tag": "TEST-COMP-B001",
        "asset_class": ASSET_CLASS,
        "site": SITE,
        "department": DEPT,
        "location": LOCATION,
        "bypass_process": True,
        "is_equipment": True,
        "item": ITEM1,
    })
    if not asset_id:
        check(False, "AB.1 Create Equipment Asset", "Failed"); return None
    asset = get_entity("asset", asset_id)
    check(asset is not None, "AB.1 Equipment created", asset_id)
    state = asset.get("workflow_state") if asset else None
    check(state in (None, "acquired", "Acquired"), "AB.1 Equipment in Acquired state", str(state))
    inv_id = asset.get("inventory") if asset else None
    check(bool(inv_id), "AB.1 Inventory auto-created (bypass=True)", str(inv_id))

    sub("AB.2 Putaway → Inactive (creates Putaway record)")
    res = do_workflow("asset", asset_id, "putaway")
    check(res is not None, "AB.2 putaway workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "inactive", "AB.2 Asset → Inactive", asset.get("workflow_state") if asset else "None")

    sub("AB.3 Issue Equipment → Active (creates Item Issue)")
    res = do_workflow("asset", asset_id, "issue_equipment")
    check(res is not None, "AB.3 issue_equipment workflow", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "active", "AB.3 Asset → Active", asset.get("workflow_state") if asset else "None")

    sub("AB.4 Putaway again → Inactive (return to storage)")
    res = do_workflow("asset", asset_id, "putaway")
    check(res is not None, "AB.4 putaway workflow (return)", res.get("message","") if res else "Failed")
    asset = get_entity("asset", asset_id)
    check(asset and asset.get("workflow_state") == "inactive", "AB.4 Asset → Inactive (returned)", asset.get("workflow_state") if asset else "None")

    return asset_id
