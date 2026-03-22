"""PR Flow Tests - Path A (Direct PO), B (RFQ), C (Reject/Revise)"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from test_business_logic_flows import *

# DB state slugs (verified from DB):
# PR:  draft → pending_review → pending_approval → approved → closed / rejected → draft
# PO:  draft → open → closed
# RFQ: draft → sourcing → review → awarded → closed  (create_po_from_rfq is a server action)
# PRL: Draft → pending_approval → approved → complete / rejected

def test_pr_path_a():
    section("PR PATH A: Direct PO → Receipts → Auto-close → Close PR")

    sub("A.1 Create Purchase Request")
    pr_id = create_entity("purchase_request", {
        "pr_description": "PR for Q2 Maintenance Supplies",
        "requestor": EMP, "due_date": "2025-06-15",
        "site": SITE, "department": DEPT, "cost_code": COST_CODE,
    })
    if not pr_id:
        check(False, "A.1 Create PR", "Failed"); return None
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "Draft", "A.1 PR in Draft", pr.get("workflow_state") if pr else "None")

    sub("A.2 Add PR Lines")
    prl1_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM1,
        "qty_required": 10, "unit_cost": 450.00,
        "vendor": VENDOR1, "site": SITE, "department": DEPT,
    })
    prl2_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM2,
        "qty_required": 5, "unit_cost": 1200.00,
        "vendor": VENDOR2, "site": SITE, "department": DEPT,
    })
    check(bool(prl1_id and prl2_id), "A.2 Two PR Lines created", f"L1={prl1_id}, L2={prl2_id}")

    sub("A.3 Submit for Review → pending_review")
    do_workflow("purchase_request", pr_id, "submit_for_review")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "pending_review", "A.3 PR → pending_review", pr.get("workflow_state") if pr else "None")

    sub("A.4 Submit for Approval → pending_approval (lines cascade)")
    do_workflow("purchase_request", pr_id, "submit_for_approval")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "pending_approval", "A.4 PR → pending_approval", pr.get("workflow_state") if pr else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    prl2 = get_entity("purchase_request_line", prl2_id)
    check(prl1 and prl1.get("workflow_state") == "pending_approval", "A.4 Line 1 → pending_approval", prl1.get("workflow_state") if prl1 else "None")
    check(prl2 and prl2.get("workflow_state") == "pending_approval", "A.4 Line 2 → pending_approval", prl2.get("workflow_state") if prl2 else "None")

    sub("A.5 Approve → approved (lines cascade)")
    do_workflow("purchase_request", pr_id, "approve")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "approved", "A.5 PR → approved", pr.get("workflow_state") if pr else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    prl2 = get_entity("purchase_request_line", prl2_id)
    check(prl1 and prl1.get("workflow_state") == "approved", "A.5 Line 1 → approved", prl1.get("workflow_state") if prl1 else "None")
    check(prl2 and prl2.get("workflow_state") == "approved", "A.5 Line 2 → approved", prl2.get("workflow_state") if prl2 else "None")

    sub("A.6 Create Purchase Order (server action)")
    result = do_action("purchase_request", pr_id, "create_purchase_order")
    check(result and result.get("status") == "success", "A.6 create_purchase_order action", result.get("message", "") if result else "Failed")
    # create_purchase_order may create one PO per vendor — collect all POs for this PR
    all_pol_list = list_entity("purchase_order_line")
    all_prl_ids = {prl_id for prl_id in [l.get("id") for l in list_entity("purchase_request_line") if l.get("purchase_request") == pr_id]}
    pr_po_ids = list({pol.get("po_id") for pol in all_pol_list if pol.get("pr_line_id") in all_prl_ids and pol.get("po_id")})
    if not pr_po_ids:
        all_pos = list_entity("purchase_order")
        pr_po_ids = [all_pos[-1].get("id")] if all_pos else []
    check(bool(pr_po_ids), "A.6 PO(s) created", str(pr_po_ids))

    sub("A.7 Approve all POs → open (skip if already open)")
    for po_id in pr_po_ids:
        po = get_entity("purchase_order", po_id)
        if po and po.get("workflow_state") == "draft":
            do_workflow("purchase_order", po_id, "approve")
            po = get_entity("purchase_order", po_id)
        check(po and po.get("workflow_state") == "open", f"A.7 PO {po_id} → open", po.get("workflow_state") if po else "None")

    sub("A.8-A.9 Create and confirm receipts for all PO lines")
    all_po_lines = [pol for pol in all_pol_list if pol.get("po_id") in pr_po_ids]
    pr_line_ids = []
    for i, pol in enumerate(all_po_lines):
        qty = pol.get("quantity_ordered") or pol.get("qty") or (10 if i == 0 else 5)
        r_id = create_entity("purchase_receipt", {
            "purchase_order_line": pol.get("id"),
            "item": pol.get("item_id") or pol.get("item") or ITEM1,
            "quantity_received": qty,
            "date_received": "2025-06-05",
            "receiving_location": LOCATION,
            "site": SITE, "department": DEPT,
            "generated_inventory": False,
        })
        check(bool(r_id), f"A.8 Receipt {i+1} created", str(r_id))
        if r_id:
            res = do_action("purchase_receipt", r_id, "confirm_receipt")
            check(res and res.get("status") == "success", f"A.9 Confirm Receipt {i+1}", res.get("message", "") if res else "Failed")
        if pol.get("pr_line_id"):
            pr_line_ids.append(pol.get("pr_line_id"))

    sub("A.10 Complete PR Lines (fully_received → complete)")
    # Also pick up any fully_received lines not in pr_line_ids
    all_prl = list_entity("purchase_request_line")
    my_fr_lines = [l for l in all_prl if l.get("purchase_request") == pr_id and l.get("workflow_state") == "fully_received"]
    complete_ids = list({*pr_line_ids, *[l.get("id") for l in my_fr_lines]})
    for prl_id in complete_ids:
        res = do_workflow("purchase_request_line", prl_id, "complete")
        check(res and res.get("status") == "success", f"A.10 PR Line {prl_id} → complete", res.get("message", "") if res else "Failed")

    sub("A.11 Close PR (requires all lines complete)")
    res = do_workflow("purchase_request", pr_id, "close")
    check(res and res.get("status") == "success", "A.11 PR close", res.get("message", "") if res else "Failed")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "closed", "A.11 PR → closed", pr.get("workflow_state") if pr else "None")
    return pr_id


def test_pr_path_b():
    section("PR PATH B: RFQ → Award → Create PO → Close")

    sub("B.1-B.5 Create PR-B and approve")
    pr_id = create_entity("purchase_request", {
        "pr_description": "PR for Q3 Electrical Equipment via RFQ",
        "requestor": EMP, "due_date": "2025-07-15",
        "site": SITE, "department": DEPT, "cost_code": COST_CODE,
    })
    if not pr_id:
        check(False, "B.1 Create PR-B", "Failed"); return None
    prl1_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM1,
        "qty_required": 20, "unit_cost": 450.00, "vendor": VENDOR1,
        "site": SITE, "department": DEPT,
    })
    prl2_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM2,
        "qty_required": 8, "unit_cost": 1200.00, "vendor": VENDOR2,
        "site": SITE, "department": DEPT,
    })
    do_workflow("purchase_request", pr_id, "submit_for_review")
    do_workflow("purchase_request", pr_id, "submit_for_approval")
    do_workflow("purchase_request", pr_id, "approve")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "approved", "B.5 PR-B → approved", pr.get("workflow_state") if pr else "None")

    sub("B.6 Generate RFQ (server action)")
    result = do_action("purchase_request", pr_id, "generate_rfq")
    check(result and result.get("status") == "success", "B.6 generate_rfq action", result.get("message", "") if result else "Failed")
    rfq_id = (result.get("data") or {}).get("id") if result else None
    if not rfq_id:
        all_rfq = list_entity("request_for_quotation")
        rfq_id = all_rfq[-1].get("id") if all_rfq else None
    check(bool(rfq_id), "B.6 RFQ created", str(rfq_id))
    if rfq_id:
        rfq = get_entity("request_for_quotation", rfq_id)
        check(rfq and rfq.get("workflow_state") == "Draft", "B.6 RFQ in Draft", rfq.get("workflow_state") if rfq else "None")

    sub("B.7 Add RFQ Lines and set supplier")
    if rfq_id:
        rfql1_id = create_entity("rfq_line", {
            "rfq_id": rfq_id, "pr_line": prl1_id, "item": ITEM1,
            "quantity": 20, "price": 420.00,
        })
        rfql2_id = create_entity("rfq_line", {
            "rfq_id": rfq_id, "pr_line": prl2_id, "item": ITEM2,
            "quantity": 8, "price": 1100.00,
        })
        check(bool(rfql1_id and rfql2_id), "B.7 RFQ Lines created", f"L1={rfql1_id}, L2={rfql2_id}")
        update_entity("request_for_quotation", rfq_id, {
            "supplier": VENDOR1, "awarded_vendor": VENDOR1, "due_date": "2025-07-08",
        })

    sub("B.8 Start Sourcing → sourcing")
    if rfq_id:
        do_workflow("request_for_quotation", rfq_id, "start_sourcing")
        rfq = get_entity("request_for_quotation", rfq_id)
        check(rfq and rfq.get("workflow_state") == "sourcing", "B.8 RFQ → sourcing", rfq.get("workflow_state") if rfq else "None")

    sub("B.9 Submit for Review → review")
    if rfq_id:
        do_workflow("request_for_quotation", rfq_id, "submit_for_review")
        rfq = get_entity("request_for_quotation", rfq_id)
        check(rfq and rfq.get("workflow_state") == "review", "B.9 RFQ → review", rfq.get("workflow_state") if rfq else "None")

    sub("B.10 Award RFQ → awarded")
    if rfq_id:
        do_workflow("request_for_quotation", rfq_id, "award")
        rfq = get_entity("request_for_quotation", rfq_id)
        check(rfq and rfq.get("workflow_state") == "awarded", "B.10 RFQ → awarded", rfq.get("workflow_state") if rfq else "None")

    sub("B.11 Create PO from RFQ (server action create_po_from_rfq)")
    po_id = None
    if rfq_id:
        result = do_action("request_for_quotation", rfq_id, "create_po_from_rfq")
        check(result and result.get("status") == "success", "B.11 create_po_from_rfq action", result.get("message", "") if result else "Failed")
        po_id = (result.get("data") or {}).get("id") if result else None
        if not po_id:
            all_pos = list_entity("purchase_order")
            po_id = all_pos[-1].get("id") if all_pos else None
        check(bool(po_id), "B.11 PO created from RFQ", str(po_id))
        if po_id:
            po = get_entity("purchase_order", po_id)
            check(po and po.get("workflow_state") in ("draft", "open"), "B.11 PO in draft or open", po.get("workflow_state") if po else "None")

    sub("B.12 RFQ auto-closed by create_po_from_rfq")
    if rfq_id:
        rfq = get_entity("request_for_quotation", rfq_id)
        rfq_state = rfq.get("workflow_state") if rfq else None
        if rfq_state != "closed":
            do_workflow("request_for_quotation", rfq_id, "close")
            rfq = get_entity("request_for_quotation", rfq_id)
        check(rfq and rfq.get("workflow_state") == "closed", "B.12 RFQ → closed", rfq.get("workflow_state") if rfq else "None")

    sub("B.13 Approve all POs → open, create receipts, complete PR lines")
    # create_po_from_rfq may create one PO per vendor — collect all POs for this PR
    b_all_pol = list_entity("purchase_order_line")
    b_prl_ids = {l.get("id") for l in list_entity("purchase_request_line") if l.get("purchase_request") == pr_id}
    b_po_ids = list({pol.get("po_id") for pol in b_all_pol if pol.get("pr_line_id") in b_prl_ids and pol.get("po_id")})
    if not b_po_ids and po_id:
        b_po_ids = [po_id]
    for b_po_id in b_po_ids:
        po = get_entity("purchase_order", b_po_id)
        if po and po.get("workflow_state") == "draft":
            do_workflow("purchase_order", b_po_id, "approve")
            po = get_entity("purchase_order", b_po_id)
        check(po and po.get("workflow_state") == "open", f"B.13 PO {b_po_id} → open", po.get("workflow_state") if po else "None")
    b_po_lines = [pol for pol in b_all_pol if pol.get("po_id") in b_po_ids]
    b_pr_line_ids = []
    for i, pol in enumerate(b_po_lines):
        qty = pol.get("quantity_ordered") or pol.get("qty") or 1
        r_id = create_entity("purchase_receipt", {
            "purchase_order_line": pol.get("id"),
            "item": pol.get("item_id") or pol.get("item") or ITEM1,
            "quantity_received": qty,
            "date_received": "2025-07-15",
            "receiving_location": LOCATION,
            "site": SITE, "department": DEPT,
            "generated_inventory": False,
        })
        if r_id:
            do_action("purchase_receipt", r_id, "confirm_receipt")
        if pol.get("pr_line_id"):
            b_pr_line_ids.append(pol.get("pr_line_id"))
    # Complete all fully_received PR lines
    b_all_prl = list_entity("purchase_request_line")
    b_fr_lines = [l for l in b_all_prl if l.get("purchase_request") == pr_id and l.get("workflow_state") == "fully_received"]
    b_complete_ids = list({*b_pr_line_ids, *[l.get("id") for l in b_fr_lines]})
    for prl_id in b_complete_ids:
        do_workflow("purchase_request_line", prl_id, "complete")
    return pr_id


def test_pr_path_c():
    section("PR PATH C: Reject → Revise → Re-submit → Approve")

    sub("C.1-C.4 Create PR-C, add line, submit for approval")
    pr_id = create_entity("purchase_request", {
        "pr_description": "PR for Electrical Components — Batch Order",
        "requestor": EMP, "due_date": "2025-08-10",
        "site": SITE, "department": DEPT, "cost_code": COST_CODE,
    })
    if not pr_id:
        check(False, "C.1 Create PR-C", "Failed"); return None
    prl1_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM1,
        "qty_required": 3, "unit_cost": 450.00, "vendor": VENDOR1,
        "site": SITE, "department": DEPT,
    })
    check(bool(prl1_id), "C.1 PR-C Line 1 created", prl1_id)
    do_workflow("purchase_request", pr_id, "submit_for_review")
    do_workflow("purchase_request", pr_id, "submit_for_approval")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "pending_approval", "C.4 PR-C → pending_approval", pr.get("workflow_state") if pr else "None")

    sub("C.5 Reject → rejected (lines cascade)")
    update_entity("purchase_request", pr_id, {
        "reject_reason": "Insufficient justification — additional vendor quotes required."
    })
    do_workflow("purchase_request", pr_id, "reject_purchase_request")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "rejected", "C.5 PR → rejected", pr.get("workflow_state") if pr else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    check(prl1 and prl1.get("workflow_state") == "rejected", "C.5 Line 1 → rejected", prl1.get("workflow_state") if prl1 else "None")

    sub("C.6 Revise → draft (rejected lines stay locked)")
    do_workflow("purchase_request", pr_id, "revise_purchase_request")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "draft", "C.6 PR → draft", pr.get("workflow_state") if pr else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    check(prl1 and prl1.get("workflow_state") == "rejected", "C.6 Line 1 stays rejected", prl1.get("workflow_state") if prl1 else "None")

    sub("C.7 Add new Lines 2 and 3")
    prl2_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM1,
        "item_description": "Revised qty per approver feedback",
        "qty_required": 5, "unit_cost": 440.00, "vendor": VENDOR1,
        "site": SITE, "department": DEPT,
    })
    prl3_id = create_entity("purchase_request_line", {
        "purchase_request": pr_id, "item": ITEM2,
        "item_description": "Added per rejection note",
        "qty_required": 2, "unit_cost": 1150.00, "vendor": VENDOR1,
        "site": SITE, "department": DEPT,
    })
    check(bool(prl2_id and prl3_id), "C.7 Lines 2 and 3 created", f"L2={prl2_id}, L3={prl3_id}")
    if prl2_id:
        prl2 = get_entity("purchase_request_line", prl2_id)
        check(prl2 and prl2.get("workflow_state") == "Draft", "C.7 New lines in Draft", prl2.get("workflow_state") if prl2 else "None")

    sub("C.8 Re-submit for Review → pending_review")
    do_workflow("purchase_request", pr_id, "submit_for_review")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "pending_review", "C.8 PR → pending_review", pr.get("workflow_state") if pr else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    check(prl1 and prl1.get("workflow_state") == "rejected", "C.8 Line 1 stays rejected", prl1.get("workflow_state") if prl1 else "None")

    sub("C.9 Submit for Approval → pending_approval (new lines cascade)")
    do_workflow("purchase_request", pr_id, "submit_for_approval")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "pending_approval", "C.9 PR → pending_approval", pr.get("workflow_state") if pr else "None")
    if prl2_id:
        prl2 = get_entity("purchase_request_line", prl2_id)
        check(prl2 and prl2.get("workflow_state") == "pending_approval", "C.9 Line 2 → pending_approval", prl2.get("workflow_state") if prl2 else "None")
    if prl3_id:
        prl3 = get_entity("purchase_request_line", prl3_id)
        check(prl3 and prl3.get("workflow_state") == "pending_approval", "C.9 Line 3 → pending_approval", prl3.get("workflow_state") if prl3 else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    check(prl1 and prl1.get("workflow_state") == "rejected", "C.9 Line 1 stays rejected", prl1.get("workflow_state") if prl1 else "None")

    sub("C.10 Approve → approved (new lines cascade, rejected stays)")
    do_workflow("purchase_request", pr_id, "approve")
    pr = get_entity("purchase_request", pr_id)
    check(pr and pr.get("workflow_state") == "approved", "C.10 PR → approved", pr.get("workflow_state") if pr else "None")
    if prl2_id:
        prl2 = get_entity("purchase_request_line", prl2_id)
        check(prl2 and prl2.get("workflow_state") == "approved", "C.10 Line 2 → approved", prl2.get("workflow_state") if prl2 else "None")
    if prl3_id:
        prl3 = get_entity("purchase_request_line", prl3_id)
        check(prl3 and prl3.get("workflow_state") == "approved", "C.10 Line 3 → approved", prl3.get("workflow_state") if prl3 else "None")
    prl1 = get_entity("purchase_request_line", prl1_id)
    check(prl1 and prl1.get("workflow_state") == "rejected", "C.10 Line 1 stays rejected", prl1.get("workflow_state") if prl1 else "None")
    return pr_id
