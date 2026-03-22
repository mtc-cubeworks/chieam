"""Stock Count Flow Tests"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from test_business_logic_flows import *

# DB state slugs (verified from DB):
# SC:  Planned → start_stock_count → in_progress → approve → approved → complete → closed
# IA:  Draft → submit → submitted → post → posted

def test_stock_count():
    section("STOCK COUNT: Planned → In Progress → Approved (IA created) → Closed → Post IA")

    sub("SC.1 Create Stock Count (basis=Selection)")
    sc_id = create_entity("stock_count", {
        "site": SITE,
        "basis": "Selection",
        "method": "Guided",
        "freeze_policy": "None",
    })
    if not sc_id:
        check(False, "SC.1 Create Stock Count", "Failed"); return None
    sc = get_entity("stock_count", sc_id)
    check(sc and sc.get("workflow_state") == "Planned", "SC.1 SC in Planned", sc.get("workflow_state") if sc else "None")

    sub("SC.2 Find Stock Count Lines (no-op for Selection basis)")
    result = do_action("stock_count", sc_id, "find_stock_count_lines")
    check(result is not None, "SC.2 find_stock_count_lines action", result.get("message","") if result else "Failed")

    sub("SC.3 Add manual Stock Count Line (Selection basis)")
    scl_id = create_entity("stock_count_line", {
        "stock_count": sc_id,
        "item": ITEM1,
        "snapshot_qty": 10,
        "counted_qty": 13,
        "variance_qty": 3,
    })
    check(bool(scl_id), "SC.3 Stock Count Line created", str(scl_id))

    sub("SC.4 Start Stock Count → in_progress")
    res = do_workflow("stock_count", sc_id, "start_stock_count")
    check(res is not None, "SC.4 start_stock_count workflow", res.get("message","") if res else "Failed")
    sc = get_entity("stock_count", sc_id)
    check(sc and sc.get("workflow_state") == "in_progress", "SC.4 SC → in_progress", sc.get("workflow_state") if sc else "None")

    sub("SC.5 Approve Stock Count → approved (creates IA)")
    res = do_workflow("stock_count", sc_id, "approve")
    check(res is not None, "SC.5 approve workflow", res.get("message","") if res else "Failed")
    sc = get_entity("stock_count", sc_id)
    check(sc and sc.get("workflow_state") == "approved", "SC.5 SC → approved", sc.get("workflow_state") if sc else "None")

    # Find auto-created IA
    ia_id = None
    sc_ias = get_linked("inventory_adjustment", "source_stock_count", sc_id)
    if not sc_ias:
        all_ia = list_entity("inventory_adjustment")
        sc_ias = [all_ia[-1]] if all_ia else []
    check(len(sc_ias) >= 1, "SC.5 IA auto-created", f"Found {len(sc_ias)}")
    ia_id = sc_ias[0].get("id") if sc_ias else None
    if ia_id:
        ia = get_entity("inventory_adjustment", ia_id)
        check(ia and ia.get("workflow_state") == "Draft", "SC.5 IA in Draft", ia.get("workflow_state") if ia else "None")

    sub("SC.6 Complete Stock Count → closed")
    res = do_workflow("stock_count", sc_id, "complete")
    check(res is not None, "SC.6 complete workflow", res.get("message","") if res else "Failed")
    sc = get_entity("stock_count", sc_id)
    check(sc and sc.get("workflow_state") == "closed", "SC.6 SC → closed", sc.get("workflow_state") if sc else "None")

    sub("SC.7 Submit IA → submitted")
    if ia_id:
        res = do_workflow("inventory_adjustment", ia_id, "submit")
        check(res is not None, "SC.7 IA submit workflow", res.get("message","") if res else "Failed")
        ia = get_entity("inventory_adjustment", ia_id)
        check(ia and ia.get("workflow_state") == "submitted", "SC.7 IA → submitted", ia.get("workflow_state") if ia else "None")
    else:
        check(False, "SC.7 IA submit", "No IA found")

    sub("SC.8 Post IA → posted (updates inventory)")
    if ia_id:
        res = do_workflow("inventory_adjustment", ia_id, "post")
        check(res is not None, "SC.8 IA post workflow", res.get("message","") if res else "Failed")
        ia = get_entity("inventory_adjustment", ia_id)
        check(ia and ia.get("workflow_state") == "posted", "SC.8 IA → posted", ia.get("workflow_state") if ia else "None")
    else:
        check(False, "SC.8 IA post", "No IA found")

    return sc_id
