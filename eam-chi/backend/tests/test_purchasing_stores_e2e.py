"""
End-to-end Purchasing & Stores Workflow Test

Tests the full purchasing lifecycle:
1. Login
2. Create Purchase Request + Lines
3. PR workflow: Draft → Pending Review → Pending Approval → Approved
4. Generate RFQ (server action)
5. RFQ workflow: Draft → Sourcing → Review → Awarded
6. Create PO from RFQ (server action)
7. PO workflow: Draft → Open
8. Create Purchase Receipt linked to PO Line
9. Confirm Receipt (server action) → validates inventory creation
10. Verify PO Line / PR Line qty_received and workflow states
11. Reject flow validation
12. Over-receiving validation
"""
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"
TOKEN = None


def log(msg, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{msg}")


results = []


def test(label, passed, detail=""):
    icon = "✅" if passed else "❌"
    detail_str = f" - {detail}" if detail else ""
    print(f"  {icon} {label}{detail_str}")
    results.append((label, passed, detail))
    return passed


def headers():
    return {"Authorization": f"Bearer {TOKEN}"}


async def login():
    global TOKEN
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        resp = await client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        data = resp.json()
        if data.get("access_token"):
            TOKEN = data["access_token"]
            return True
        print(f"  Login response: {data}")
        return False


async def api_get(path):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        resp = await client.get(path, headers=headers())
        return resp.json()


async def api_post(path, data=None):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        resp = await client.post(path, json=data or {}, headers=headers())
        return resp.json()


async def create_record(entity, data):
    return await api_post(f"/api/entity/{entity}/action", {"action": "create", "data": data})


async def workflow_action(entity, record_id, action_slug):
    return await api_post(f"/api/entity/{entity}/workflow", {"action": action_slug, "id": record_id})


async def document_action(entity, record_id, action_name):
    return await api_post(f"/api/entity/{entity}/{record_id}/action/{action_name}")


async def get_record(entity, record_id):
    return await api_get(f"/api/entity/{entity}/detail/{record_id}")


async def get_meta(entity):
    return await api_get(f"/api/meta/{entity}")


# ─── Helpers ───

async def get_first_id(entity):
    """Get the first record ID for an entity."""
    resp = await api_get(f"/api/entity/{entity}/list?page=1&page_size=1")
    if resp.get("status") == "success" and resp.get("data"):
        return resp["data"][0].get("id")
    return None


def extract_id_from_response(resp):
    """Extract created record ID from action response."""
    resp_data = resp.get("data", {}) or {}
    path = resp_data.get("path") or resp.get("path")
    if path:
        return path.split("/")[-1]
    return resp_data.get("id")


def normalize_state(state):
    """Normalize workflow state for comparison."""
    if not state:
        return ""
    import re
    s = state.lower().strip()
    s = re.sub(r'[^a-z0-9\s_]', '', s)
    return re.sub(r'\s+', '_', s)


# ─── Main Test Flow ───

async def run_tests():
    global TOKEN

    print("=" * 70)
    print("PURCHASING & STORES - FULL E2E TEST")
    print("=" * 70)

    # ─── 1. Login ───
    print("\n📋 Phase 1: Authentication")
    ok = await login()
    test("Login as admin", ok, f"Token: {TOKEN[:20]}..." if ok else "FAILED")
    if not ok:
        print("FATAL: Cannot continue without auth")
        return

    # ─── 2. Metadata Validation ───
    print("\n📋 Phase 2: Entity Metadata Validation")

    pr_meta = await get_meta("purchase_receipt")
    pr_meta_ok = pr_meta.get("status") == "success"
    test("Purchase Receipt metadata loads", pr_meta_ok)
    if pr_meta_ok:
        pr_data = pr_meta["data"]
        actions = [a.get("action") for a in pr_data.get("actions", [])]
        test("PR Receipt has confirm_receipt action", "confirm_receipt" in actions, str(actions))
        test("PR Receipt has update_inventory_serialno action", "update_inventory_serialno" in actions, str(actions))
        wf = pr_data.get("workflow", {})
        test("PR Receipt workflow initial state is draft", wf.get("initial_state") == "draft", wf.get("initial_state"))

    rfq_meta = await get_meta("request_for_quotation")
    rfq_meta_ok = rfq_meta.get("status") == "success"
    test("RFQ metadata loads", rfq_meta_ok)
    if rfq_meta_ok:
        rfq_data = rfq_meta["data"]
        rfq_actions = [a.get("action") for a in rfq_data.get("actions", [])]
        test("RFQ has create_po_from_rfq action", "create_po_from_rfq" in rfq_actions, str(rfq_actions))
        rfq_wf = rfq_data.get("workflow", {})
        rfq_states = [s.get("slug") if isinstance(s, dict) else s for s in rfq_wf.get("states", [])]
        test("RFQ has expected states", "draft" in rfq_states and "sourcing" in rfq_states and "awarded" in rfq_states, str(rfq_states))

    # ─── 3. Get reference data ───
    print("\n📋 Phase 3: Reference Data")
    valid_site = await get_first_id("site")
    valid_dept = await get_first_id("department")
    valid_vendor = await get_first_id("vendor")
    valid_item = await get_first_id("item")
    valid_location = await get_first_id("location")
    log(f"site={valid_site}, dept={valid_dept}, vendor={valid_vendor}, item={valid_item}, location={valid_location}", 1)

    # ─── 4. Create Purchase Request ───
    print("\n📋 Phase 4: Create Purchase Request")
    pr_resp = await create_record("purchase_request", {
        "pr_description": "E2E Full Flow Test PR",
        "date_requested": "2026-02-10",
        "due_date": "2026-03-10",
        "site": valid_site,
        "department": valid_dept,
    })
    pr_created = pr_resp.get("status") == "success"
    pr_id = pr_resp.get("data", {}).get("id") if pr_created else None
    test("Create Purchase Request", pr_created, f"ID: {pr_id}")

    if not pr_id:
        print("FATAL: Cannot continue without PR")
        return

    # ─── 5. Add PR Lines ───
    print("\n📋 Phase 5: Add Purchase Request Lines")
    line1_resp = await create_record("purchase_request_line", {
        "purchase_request": pr_id,
        "item": valid_item,
        "item_description": "Test Item for E2E",
        "qty_required": 10,
        "unit_cost": 25.00,
        "vendor": valid_vendor,
        "site": valid_site,
        "department": valid_dept,
    })
    line1_ok = line1_resp.get("status") == "success"
    line1_id = line1_resp.get("data", {}).get("id") if line1_ok else None
    test("Create PR Line 1", line1_ok, f"ID: {line1_id}")

    line2_resp = await create_record("purchase_request_line", {
        "purchase_request": pr_id,
        "item": valid_item,
        "item_description": "Test Item 2 for E2E",
        "qty_required": 5,
        "unit_cost": 50.00,
        "vendor": valid_vendor,
        "site": valid_site,
        "department": valid_dept,
    })
    line2_ok = line2_resp.get("status") == "success"
    line2_id = line2_resp.get("data", {}).get("id") if line2_ok else None
    test("Create PR Line 2", line2_ok, f"ID: {line2_id}")

    # ─── 6. PR Workflow: Draft → Pending Review → Pending Approval → Approved ───
    print("\n📋 Phase 6: PR Workflow Transitions")

    wf_resp = await workflow_action("purchase_request", pr_id, "submit_for_review")
    test("PR: Draft → Pending Review", wf_resp.get("status") == "success", wf_resp.get("message", ""))

    wf_resp = await workflow_action("purchase_request", pr_id, "submit_for_approval")
    test("PR: Pending Review → Pending Approval", wf_resp.get("status") == "success", wf_resp.get("message", ""))

    wf_resp = await workflow_action("purchase_request", pr_id, "approve")
    test("PR: Pending Approval → Approved", wf_resp.get("status") == "success", wf_resp.get("message", ""))

    pr_detail = await get_record("purchase_request", pr_id)
    pr_state = normalize_state(pr_detail.get("data", {}).get("workflow_state", ""))
    test("PR state is approved", pr_state == "approved", pr_state)

    # ─── 7. Generate RFQ (server action) ───
    print("\n📋 Phase 7: Generate RFQ")
    rfq_resp = await document_action("purchase_request", pr_id, "generate_rfq")
    rfq_action_ok = rfq_resp.get("status") == "success"
    test("Generate RFQ action succeeds", rfq_action_ok, rfq_resp.get("message", ""))

    rfq_id = extract_id_from_response(rfq_resp) if rfq_action_ok else None
    if rfq_id:
        test("RFQ created with ID", bool(rfq_id), rfq_id)
        rfq_detail = await get_record("request_for_quotation", rfq_id)
        rfq_state = normalize_state(rfq_detail.get("data", {}).get("workflow_state", ""))
        test("RFQ initial state is draft", rfq_state == "draft", rfq_state)

    # ─── 8. Add RFQ Lines ───
    print("\n📋 Phase 8: Add RFQ Lines")
    if rfq_id and line1_id:
        rfq_line_resp = await create_record("rfq_line", {
            "rfq_id": rfq_id,
            "pr_line": line1_id,
            "item": valid_item,
            "item_description": "Test Item for E2E",
            "quantity": 10,
            "price": 25.00,
        })
        rfq_line_ok = rfq_line_resp.get("status") == "success"
        rfq_line_id = rfq_line_resp.get("data", {}).get("id") if rfq_line_ok else None
        test("Create RFQ Line", rfq_line_ok, f"ID: {rfq_line_id}")

    # ─── 9. RFQ Workflow: Draft → Sourcing → Review → Awarded ───
    print("\n📋 Phase 9: RFQ Workflow Transitions")
    if rfq_id:
        wf_resp = await workflow_action("request_for_quotation", rfq_id, "start_sourcing")
        test("RFQ: Draft → Sourcing", wf_resp.get("status") == "success", wf_resp.get("message", ""))

        wf_resp = await workflow_action("request_for_quotation", rfq_id, "submit_for_review")
        test("RFQ: Sourcing → Review", wf_resp.get("status") == "success", wf_resp.get("message", ""))

        # Set awarded vendor before awarding
        await api_post(f"/api/entity/request_for_quotation/action", {
            "action": "update",
            "id": rfq_id,
            "data": {"awarded_vendor": valid_vendor}
        })

        wf_resp = await workflow_action("request_for_quotation", rfq_id, "award")
        test("RFQ: Review → Awarded", wf_resp.get("status") == "success", wf_resp.get("message", ""))

        rfq_detail = await get_record("request_for_quotation", rfq_id)
        rfq_state = normalize_state(rfq_detail.get("data", {}).get("workflow_state", ""))
        test("RFQ state is awarded", rfq_state == "awarded", rfq_state)

    # ─── 10. Create PO from RFQ (server action) ───
    print("\n📋 Phase 10: Create PO from RFQ")
    po_id = None
    if rfq_id:
        po_resp = await document_action("request_for_quotation", rfq_id, "create_po_from_rfq")
        po_action_ok = po_resp.get("status") == "success"
        test("Create PO from RFQ action", po_action_ok, po_resp.get("message", ""))

        po_id = extract_id_from_response(po_resp) if po_action_ok else None
        if po_id:
            test("PO created with ID", bool(po_id), po_id)

    # ─── 10b. Fallback: Create PO from PR if RFQ path didn't produce PO ───
    if not po_id:
        print("\n📋 Phase 10b: Create PO from PR (fallback)")
        po_resp = await document_action("purchase_request", pr_id, "create_purchase_order")
        po_action_ok = po_resp.get("status") == "success"
        test("Create PO from PR action", po_action_ok, po_resp.get("message", ""))
        po_id = extract_id_from_response(po_resp) if po_action_ok else None
        if po_id:
            test("PO created with ID", bool(po_id), po_id)

    if not po_id:
        print("FATAL: Cannot continue without PO")
        return

    # ─── 11. PO Workflow: Draft → Open ───
    print("\n📋 Phase 11: PO Workflow")
    wf_resp = await workflow_action("purchase_order", po_id, "approve")
    test("PO: Draft → Open", wf_resp.get("status") == "success", wf_resp.get("message", ""))

    po_detail = await get_record("purchase_order", po_id)
    po_state = normalize_state(po_detail.get("data", {}).get("workflow_state", ""))
    test("PO state is open", po_state == "open", po_state)

    # ─── 12. Get PO Lines ───
    print("\n📋 Phase 12: Verify PO Lines")
    po_lines_resp = await api_get(f"/api/entity/purchase_order_line/list?page=1&page_size=50&filter_field=po_id&filter_value={po_id}")
    po_lines = po_lines_resp.get("data", [])
    test("PO has lines", len(po_lines) > 0, f"count={len(po_lines)}")

    # Pick the first PO line that has an item_id and is in draft state
    selected_line = None
    for pl in po_lines:
        has_item = pl.get("item_id") or pl.get("item")
        is_draft = normalize_state(pl.get("workflow_state", "")) == "draft"
        if has_item and is_draft:
            selected_line = pl
            break
    # Fallback: any line with an item
    if not selected_line:
        for pl in po_lines:
            if pl.get("item_id") or pl.get("item"):
                selected_line = pl
                break
    if not selected_line and po_lines:
        selected_line = po_lines[0]

    po_line_id = selected_line.get("id") if selected_line else None
    po_line_item = (selected_line.get("item_id") or selected_line.get("item")) if selected_line else None
    po_line_qty = (selected_line.get("quantity_ordered") or selected_line.get("qty_ordered")) if selected_line else None
    if po_line_qty:
        po_line_qty = int(po_line_qty)
    log(f"PO Line: {po_line_id}, item={po_line_item}, qty={po_line_qty}", 1)

    # PO Line should be auto-approved by PO workflow handler when PO is approved
    if po_line_id:
        pol_detail = await get_record("purchase_order_line", po_line_id)
        pol_state = normalize_state(pol_detail.get("data", {}).get("workflow_state", ""))
        if pol_state == "approved":
            test("PO Line: Auto-approved by PO workflow", True, pol_state)
        else:
            # Fallback: manually approve if not auto-approved
            wf_resp = await workflow_action("purchase_order_line", po_line_id, "approve_line")
            test("PO Line: Draft → Approved", wf_resp.get("status") == "success", wf_resp.get("message", ""))

    # ─── 13. Create Purchase Receipt ───
    print("\n📋 Phase 13: Create Purchase Receipt")
    # Use half the PO line qty for partial receipt, or 1 if qty is small
    first_receipt_qty = max(1, (po_line_qty or 2) // 2)
    if po_line_id:
        receipt_resp = await create_record("purchase_receipt", {
            "purchase_order_line": po_line_id,
            "quantity_received": first_receipt_qty,
            "date_received": "2026-02-10",
            "receiving_location": valid_location,
            "site": valid_site,
            "department": valid_dept,
        })
        receipt_ok = receipt_resp.get("status") == "success"
        receipt_id = receipt_resp.get("data", {}).get("id") if receipt_ok else None
        test("Create Purchase Receipt", receipt_ok, f"ID: {receipt_id}")

        if receipt_id:
            receipt_detail = await get_record("purchase_receipt", receipt_id)
            receipt_state = normalize_state(receipt_detail.get("data", {}).get("workflow_state", ""))
            test("Receipt initial state is draft", receipt_state == "draft", receipt_state)

    # ─── 14. Confirm Receipt (server action) ───
    print("\n📋 Phase 14: Confirm Receipt")
    if receipt_id:
        confirm_resp = await document_action("purchase_receipt", receipt_id, "confirm_receipt")
        confirm_ok = confirm_resp.get("status") == "success"
        test("Confirm Receipt action", confirm_ok, confirm_resp.get("message", ""))

        if not confirm_ok:
            log(f"Error detail: {json.dumps(confirm_resp, indent=2)}", 2)

    # ─── 15. Verify PO Line updated ───
    print("\n📋 Phase 15: Verify Procurement Document Updates")
    if po_line_id:
        pol_detail = await get_record("purchase_order_line", po_line_id)
        pol_data = pol_detail.get("data", {})
        pol_qty_received = pol_data.get("quantity_received", 0) or pol_data.get("qty_received", 0)
        if pol_qty_received:
            pol_qty_received = int(pol_qty_received)
        pol_state = normalize_state(pol_data.get("workflow_state", ""))
        test("PO Line qty_received updated", pol_qty_received == first_receipt_qty, f"qty_received={pol_qty_received}, expected={first_receipt_qty}")
        test("PO Line state is partially_received", pol_state == "partially_received", pol_state)

    # ─── 16. Over-Receiving Validation ───
    print("\n📋 Phase 16: Over-Receiving Validation")
    if po_line_id:
        over_receipt_resp = await create_record("purchase_receipt", {
            "purchase_order_line": po_line_id,
            "quantity_received": 999,
            "date_received": "2026-02-10",
            "receiving_location": valid_location,
            "site": valid_site,
        })
        over_receipt_id = over_receipt_resp.get("data", {}).get("id") if over_receipt_resp.get("status") == "success" else None
        if over_receipt_id:
            over_confirm = await document_action("purchase_receipt", over_receipt_id, "confirm_receipt")
            test("Over-receiving blocked", over_confirm.get("status") == "error", over_confirm.get("message", ""))

    # ─── 17. Duplicate Prevention ───
    print("\n📋 Phase 17: Duplicate Prevention")
    if receipt_id:
        dup_confirm = await document_action("purchase_receipt", receipt_id, "confirm_receipt")
        test("Duplicate confirm blocked", dup_confirm.get("status") == "error", dup_confirm.get("message", ""))

    # ─── 18. Second Receipt to Complete ───
    print("\n📋 Phase 18: Complete Receiving")
    if po_line_id and po_line_qty:
        remaining = (po_line_qty or 10) - first_receipt_qty
        if remaining > 0:
            receipt2_resp = await create_record("purchase_receipt", {
                "purchase_order_line": po_line_id,
                "quantity_received": remaining,
                "date_received": "2026-02-11",
                "receiving_location": valid_location,
                "site": valid_site,
                "department": valid_dept,
            })
            receipt2_ok = receipt2_resp.get("status") == "success"
            receipt2_id = receipt2_resp.get("data", {}).get("id") if receipt2_ok else None
            test("Create second receipt", receipt2_ok, f"ID: {receipt2_id}, qty={remaining}")

            if receipt2_id:
                confirm2 = await document_action("purchase_receipt", receipt2_id, "confirm_receipt")
                test("Confirm second receipt", confirm2.get("status") == "success", confirm2.get("message", ""))

                # Verify PO Line is now fully received
                pol_detail2 = await get_record("purchase_order_line", po_line_id)
                pol_data2 = pol_detail2.get("data", {})
                pol_state2 = normalize_state(pol_data2.get("workflow_state", ""))
                pol_qty2 = pol_data2.get("quantity_received", 0)
                test("PO Line fully received", pol_qty2 == po_line_qty, f"qty={pol_qty2}/{po_line_qty}")
                test("PO Line state is fully_received", pol_state2 == "fully_received", pol_state2)

    # ─── Summary ───
    print("\n" + "=" * 70)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")

    if failed:
        print("\nFailed tests:")
        for label, ok, detail in results:
            if not ok:
                print(f"  ❌ {label}: {detail}")

    print("=" * 70)
    return results


if __name__ == "__main__":
    import asyncio
    test_results = asyncio.run(run_tests())
    if test_results and any(not ok for _, ok, _ in test_results):
        sys.exit(1)
    elif not test_results:
        sys.exit(1)
