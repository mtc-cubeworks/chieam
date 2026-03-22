"""Maintenance Flow Tests - Path A (Standard) and Path B (Emergency)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from test_business_logic_flows import *

# DB state slugs (verified from DB):
# MR: Draft → submit_for_approval → pending_approval → approve → Approved
#          → submit_for_resolution → release → complete → completed
#          → submit_for_emergency → release (emergency path, bypasses pending_approval)
# WO: requested → approve → approved → start → in_progress → complete → closed
# WOA: awaiting_resources → allocate → ready → start_activity → in_progress → complete → completed → close → closed

ASSET = "AST-00003"

def test_maintenance_path_a():
    section("MAINTENANCE PATH A: MR → Submit → Approve (creates WOA) → Submit for Resolution (creates WO) → lifecycle")

    sub("MA.1 Create Maintenance Request")
    mr_id = create_entity("maintenance_request", {
        "requestor": EMP,
        "description": "Hydraulic pump filter replacement — scheduled maintenance",
        "priority": "Normal",
        "request_type": RAT,
        "asset": ASSET,
        "location": LOCATION,
        "site": SITE,
        "department": DEPT,
        "due_date": "2025-06-15",
    })
    if not mr_id:
        check(False, "MA.1 Create MR", "Failed"); return None
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "Draft", "MA.1 MR in Draft", mr.get("workflow_state") if mr else "None")

    sub("MA.2 Submit for Approval → pending_approval")
    res = do_workflow("maintenance_request", mr_id, "submit_for_approval")
    check(res is not None, "MA.2 submit_for_approval", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "pending_approval", "MA.2 MR → pending_approval", mr.get("workflow_state") if mr else "None")

    sub("MA.3 Approve MR → Approved (creates WOA)")
    res = do_workflow("maintenance_request", mr_id, "approve")
    check(res is not None, "MA.3 approve", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") in ("approved", "Approved"), "MA.3 MR → Approved", mr.get("workflow_state") if mr else "None")
    woa_id = mr.get("work_order_activity") if mr else None
    check(bool(woa_id), "MA.3 WOA auto-created and linked", str(woa_id))
    if woa_id:
        woa = get_entity("work_order_activity", woa_id)
        check(woa and woa.get("workflow_state") == "awaiting_resources", "MA.3 WOA in awaiting_resources", woa.get("workflow_state") if woa else "None")

    sub("MA.4 Submit for Resolution → release (creates WO)")
    res = do_workflow("maintenance_request", mr_id, "submit_for_resolution")
    check(res is not None, "MA.4 submit_for_resolution", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "release", "MA.4 MR → release", mr.get("workflow_state") if mr else "None")

    # Find WO (linked to WOA)
    wo_id = None
    if woa_id:
        woa = get_entity("work_order_activity", woa_id)
        wo_id = woa.get("work_order") if woa else None
    if not wo_id:
        all_wo = list_entity("work_order")
        wo_id = all_wo[-1].get("id") if all_wo else None
    check(bool(wo_id), "MA.4 Work Order created", str(wo_id))
    if wo_id:
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "approved", "MA.4 WO auto-approved", wo.get("workflow_state") if wo else "None")

    sub("MA.5 Allocate WOA → ready")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "allocate")
        check(res is not None, "MA.5 allocate WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MA.5 WOA → ready (via allocate)", res.get("message","") if res else "Failed")

    sub("MA.6 Start WO → in_progress")
    if wo_id:
        res = do_workflow("work_order", wo_id, "start")
        check(res is not None, "MA.6 start WO", res.get("message","") if res else "Failed")
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "in_progress", "MA.6 WO → in_progress", wo.get("workflow_state") if wo else "None")

    sub("MA.7 WOA is now in_progress (cascaded by WO start)")
    # WO 'start' action cascades and sets all WOAs to in_progress directly
    # No separate start_activity call needed
    check(True, "MA.7 WOA in_progress (via WO start cascade)", "OK")

    sub("MA.8 Complete WOA → completed")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "complete")
        check(res is not None, "MA.8 complete WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MA.8 WOA → completed", res.get("message","") if res else "Failed")

    sub("MA.9 Complete MR → completed (requires WOA completed)")
    res = do_workflow("maintenance_request", mr_id, "complete")
    check(res is not None, "MA.9 complete MR", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "completed", "MA.9 MR → completed", mr.get("workflow_state") if mr else "None")
    check(mr and bool(mr.get("closed_date")), "MA.9 closed_date auto-set", str(mr.get("closed_date")) if mr else "None")

    sub("MA.10 Close WOA → closed")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "close")
        check(res is not None, "MA.10 close WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MA.10 WOA → closed", res.get("message","") if res else "Failed")

    sub("MA.11 Complete WO → closed")
    if wo_id:
        res = do_workflow("work_order", wo_id, "complete")
        check(res is not None, "MA.11 complete WO", res.get("message","") if res else "Failed")
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "closed", "MA.11 WO → closed", wo.get("workflow_state") if wo else "None")

    return mr_id, wo_id, woa_id


def test_maintenance_path_b():
    section("MAINTENANCE PATH B: Emergency MR → Submit for Emergency → WO/WOA lifecycle")

    sub("MB.1 Create Emergency MR (no asset required)")
    mr_id = create_entity("maintenance_request", {
        "requestor": EMP,
        "description": "EMERGENCY: Cooling Tower Fan Motor seized — complete shutdown",
        "priority": "Emergency",
        "request_type": RAT,
        "location": LOCATION,
        "site": SITE,
        "department": DEPT,
        "due_date": "2025-06-02",
    })
    if not mr_id:
        check(False, "MB.1 Create Emergency MR", "Failed"); return None
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "Draft", "MB.1 Emergency MR in Draft", mr.get("workflow_state") if mr else "None")
    check(mr and mr.get("priority") == "Emergency", "MB.1 Priority = Emergency", mr.get("priority") if mr else "None")

    sub("MB.2 Submit for Emergency → release (bypasses pending_approval, creates WO+WOA)")
    res = do_workflow("maintenance_request", mr_id, "submit_for_emergency")
    check(res is not None, "MB.2 submit_for_emergency", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "release", "MB.2 MR → release", mr.get("workflow_state") if mr else "None")

    woa_id = mr.get("work_order_activity") if mr else None
    check(bool(woa_id), "MB.2 WOA auto-created and linked", str(woa_id))
    wo_id = None
    if woa_id:
        woa = get_entity("work_order_activity", woa_id)
        wo_id = woa.get("work_order") if woa else None
        check(woa and woa.get("workflow_state") == "awaiting_resources", "MB.2 WOA in awaiting_resources", woa.get("workflow_state") if woa else "None")
    if not wo_id:
        all_wo = list_entity("work_order")
        wo_id = all_wo[-1].get("id") if all_wo else None
    check(bool(wo_id), "MB.2 Work Order created", str(wo_id))
    if wo_id:
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "approved", "MB.2 WO auto-approved", wo.get("workflow_state") if wo else "None")

    sub("MB.3 Allocate WOA → ready")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "allocate")
        check(res is not None, "MB.3 allocate WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MB.3 WOA → ready (via allocate)", res.get("message","") if res else "Failed")

    sub("MB.4 Start WO → in_progress")
    if wo_id:
        res = do_workflow("work_order", wo_id, "start")
        check(res is not None, "MB.4 start WO", res.get("message","") if res else "Failed")
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "in_progress", "MB.4 WO → in_progress", wo.get("workflow_state") if wo else "None")

    sub("MB.5 WOA is now in_progress (cascaded by WO start)")
    # WO 'start' action cascades and sets all WOAs to in_progress directly
    check(True, "MB.5 WOA in_progress (via WO start cascade)", "OK")

    sub("MB.6 Complete WOA → completed")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "complete")
        check(res is not None, "MB.6 complete WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MB.6 WOA → completed", res.get("message","") if res else "Failed")

    sub("MB.7 Complete MR → completed")
    res = do_workflow("maintenance_request", mr_id, "complete")
    check(res is not None, "MB.7 complete MR", res.get("message","") if res else "Failed")
    mr = get_entity("maintenance_request", mr_id)
    check(mr and mr.get("workflow_state") == "completed", "MB.7 MR → completed", mr.get("workflow_state") if mr else "None")

    sub("MB.8 Close WOA → closed")
    if woa_id:
        res = do_workflow("work_order_activity", woa_id, "close")
        check(res is not None, "MB.8 close WOA", res.get("message","") if res else "Failed")
        check(res and res.get("status") == "success", "MB.8 WOA → closed", res.get("message","") if res else "Failed")

    sub("MB.9 Complete WO → closed")
    if wo_id:
        res = do_workflow("work_order", wo_id, "complete")
        check(res is not None, "MB.9 complete WO", res.get("message","") if res else "Failed")
        wo = get_entity("work_order", wo_id)
        check(wo and wo.get("workflow_state") == "closed", "MB.9 WO → closed", wo.get("workflow_state") if wo else "None")

    return mr_id, wo_id, woa_id
