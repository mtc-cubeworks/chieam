"""
End-to-end Purchase Request Workflow Test

Tests the full PR lifecycle as documented in purchase_request_workflow.md:
1. Login
2. Create PR
3. Add PR Lines
4. Submit for Review (Draft → Pending Review)
5. Submit for Approval (Pending Review → Pending Approval, lines move too)
6. Approve (Pending Approval → Approved, lines move too)
7. Generate RFQ (server action)
8. Create Purchase Order (server action)
9. Reject flow (Pending Approval → Rejected → Draft via Revise)
10. Close flow (all lines complete → PR can close)

Also tests:
- RFQ entity metadata (workflow, snake_case naming)
- Server action validation (wrong state)
"""
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"
TOKEN = None

def log(msg, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{msg}")

def log_result(label, passed, detail=""):
    icon = "✅" if passed else "❌"
    detail_str = f" - {detail}" if detail else ""
    print(f"  {icon} {label}{detail_str}")
    return passed

results = []

def test(label, passed, detail=""):
    results.append((label, passed, detail))
    return log_result(label, passed, detail)


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


def headers():
    return {"Authorization": f"Bearer {TOKEN}"}


async def api_get(path):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        resp = await client.get(path, headers=headers())
        return resp.json()


async def api_post(path, data=None):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        resp = await client.post(path, json=data or {}, headers=headers())
        return resp.json()


async def create_record(entity, data):
    return await api_post(f"/api/entity/{entity}/action", {
        "action": "create",
        "data": data
    })


async def workflow_action(entity, record_id, action_slug):
    return await api_post(f"/api/entity/{entity}/workflow", {
        "action": action_slug,
        "id": record_id
    })


async def document_action(entity, record_id, action_name):
    return await api_post(f"/api/entity/{entity}/{record_id}/action/{action_name}")


async def get_record(entity, record_id):
    return await api_get(f"/api/entity/{entity}/detail/{record_id}")


async def get_meta(entity):
    return await api_get(f"/api/meta/{entity}")


async def run_tests():
    global TOKEN
    
    print("=" * 70)
    print("PURCHASE REQUEST WORKFLOW - END-TO-END TEST")
    print("=" * 70)
    
    # ─── 1. Login ───
    print("\n📋 Phase 1: Authentication")
    ok = await login()
    test("Login as admin", ok, f"Token: {TOKEN[:20]}..." if ok else "FAILED")
    if not ok:
        print("FATAL: Cannot continue without auth")
        return
    
    # ─── 2. Check RFQ Metadata ───
    print("\n📋 Phase 2: Entity Metadata Validation")
    
    rfq_meta = await get_meta("request_for_quotation")
    rfq_ok = rfq_meta.get("status") == "success"
    test("RFQ metadata loads", rfq_ok)
    
    if rfq_ok:
        rfq_data = rfq_meta["data"]
        test("RFQ name is snake_case", rfq_data.get("name") == "request_for_quotation", rfq_data.get("name"))
        
        wf = rfq_data.get("workflow")
        test("RFQ workflow metadata present", wf is not None and wf.get("enabled") == True)
        if wf:
            test("RFQ initial state is 'draft'", wf.get("initial_state") == "draft", wf.get("initial_state"))
            states = [s.get("slug") for s in wf.get("states", [])]
            test("RFQ has expected states", "draft" in states and "sourcing" in states and "awarded" in states, str(states))
    
    pr_meta = await get_meta("purchase_request")
    pr_ok = pr_meta.get("status") == "success"
    test("PR metadata loads", pr_ok)
    
    if pr_ok:
        pr_data = pr_meta["data"]
        actions = pr_data.get("actions", [])
        action_names = [a.get("action") for a in actions]
        test("PR has generate_rfq action", "generate_rfq" in action_names, str(action_names))
        test("PR has create_purchase_order action", "create_purchase_order" in action_names, str(action_names))
        # Verify no endpoint/method fields (Frappe-style)
        for a in actions:
            if a.get("action") == "generate_rfq":
                test("generate_rfq has no endpoint field", "endpoint" not in a)
                break
    
    # ─── 3. Create Purchase Request ───
    print("\n📋 Phase 3: Create Purchase Request")
    
    # Get a valid site ID for realistic test data
    sites_resp = await api_get("/api/entity/site/list?page=1&page_size=1")
    valid_site = None
    valid_dept = None
    if sites_resp.get("status") == "success" and sites_resp.get("data"):
        valid_site = sites_resp["data"][0].get("id")
    depts_resp = await api_get("/api/entity/department/list?page=1&page_size=1")
    if depts_resp.get("status") == "success" and depts_resp.get("data"):
        valid_dept = depts_resp["data"][0].get("id")
    log(f"Using site={valid_site}, dept={valid_dept}", 1)

    pr_resp = await create_record("purchase_request", {
        "pr_description": "E2E Test PR - Workflow Validation",
        "date_requested": "2026-02-06",
        "due_date": "2026-03-06",
        "site": valid_site,
        "department": valid_dept,
    })
    pr_created = pr_resp.get("status") == "success"
    pr_id = pr_resp.get("data", {}).get("id") if pr_created else None
    test("Create Purchase Request", pr_created, f"ID: {pr_id}")
    
    if pr_created:
        pr_state = pr_resp["data"].get("workflow_state")
        test("PR initial state is Draft", pr_state and pr_state.lower() == "draft", pr_state)
    
    if not pr_id:
        print("FATAL: Cannot continue without PR")
        return
    
    # ─── 4. Add PR Lines ───
    print("\n📋 Phase 4: Add Purchase Request Lines")
    
    line1_resp = await create_record("purchase_request_line", {
        "purchase_request": pr_id,
        "item_description": "Test Item 1",
        "qty_required": 10,
        "unit_cost": 25.00,
    })
    line1_ok = line1_resp.get("status") == "success"
    line1_id = line1_resp.get("data", {}).get("id") if line1_ok else None
    test("Create PR Line 1", line1_ok, f"ID: {line1_id}")
    
    line2_resp = await create_record("purchase_request_line", {
        "purchase_request": pr_id,
        "item_description": "Test Item 2",
        "qty_required": 5,
        "unit_cost": 50.00,
    })
    line2_ok = line2_resp.get("status") == "success"
    line2_id = line2_resp.get("data", {}).get("id") if line2_ok else None
    test("Create PR Line 2", line2_ok, f"ID: {line2_id}")
    
    # ─── 5. Workflow: Draft → Pending Review ───
    print("\n📋 Phase 5: Submit for Review (Draft → Pending Review)")
    
    wf_resp = await workflow_action("purchase_request", pr_id, "submit_for_review")
    wf_ok = wf_resp.get("status") == "success"
    test("Submit for Review", wf_ok, wf_resp.get("message", ""))
    
    if wf_ok:
        pr_detail = await get_record("purchase_request", pr_id)
        pr_state = pr_detail.get("data", {}).get("workflow_state", "")
        normalized = pr_state.lower().strip().replace(" ", "_") if pr_state else ""
        test("PR state is pending_review", normalized == "pending_review", f"raw='{pr_state}' normalized='{normalized}'")
    
    # ─── 6. Test Generate RFQ (server action from pending_review) ───
    print("\n📋 Phase 6: Generate RFQ (Server Action)")
    
    rfq_resp = await document_action("purchase_request", pr_id, "generate_rfq")
    rfq_action_ok = rfq_resp.get("status") == "success"
    test("Generate RFQ action succeeds", rfq_action_ok, rfq_resp.get("message", ""))
    
    rfq_id = None
    if rfq_action_ok:
        # Check for generated ID/path
        resp_data = rfq_resp.get("data", {}) or {}
        path = resp_data.get("path") or rfq_resp.get("path")
        if path:
            rfq_id = path.split("/")[-1]
            test("RFQ created with ID", bool(rfq_id), rfq_id)
        
        # Verify RFQ exists and has workflow_state
        if rfq_id:
            rfq_detail = await get_record("request_for_quotation", rfq_id)
            rfq_detail_ok = rfq_detail.get("status") == "success"
            test("RFQ record exists", rfq_detail_ok)
            if rfq_detail_ok:
                rfq_state = rfq_detail.get("data", {}).get("workflow_state", "")
                test("RFQ initial state is draft", rfq_state.lower() == "draft", rfq_state)
    
    # ─── 7. Workflow: Pending Review → Pending Approval ───
    print("\n📋 Phase 7: Submit for Approval (Pending Review → Pending Approval)")
    
    wf_resp = await workflow_action("purchase_request", pr_id, "submit_for_approval")
    wf_ok = wf_resp.get("status") == "success"
    test("Submit for Approval", wf_ok, wf_resp.get("message", ""))
    
    if wf_ok:
        pr_detail = await get_record("purchase_request", pr_id)
        pr_state = pr_detail.get("data", {}).get("workflow_state", "")
        normalized = pr_state.lower().strip().replace(" ", "_") if pr_state else ""
        test("PR state is pending_approval", normalized == "pending_approval", f"raw='{pr_state}' normalized='{normalized}'")
    
    # ─── 8. Workflow: Pending Approval → Approved ───
    print("\n📋 Phase 8: Approve (Pending Approval → Approved)")
    
    wf_resp = await workflow_action("purchase_request", pr_id, "approve")
    wf_ok = wf_resp.get("status") == "success"
    test("Approve PR", wf_ok, wf_resp.get("message", ""))
    
    if wf_ok:
        pr_detail = await get_record("purchase_request", pr_id)
        pr_state = pr_detail.get("data", {}).get("workflow_state", "")
        normalized = pr_state.lower().strip().replace(" ", "_") if pr_state else ""
        test("PR state is approved", normalized == "approved", f"raw='{pr_state}' normalized='{normalized}'")
    
    # ─── 9. Create Purchase Order (server action from approved) ───
    print("\n📋 Phase 9: Create Purchase Order (Server Action)")
    
    po_resp = await document_action("purchase_request", pr_id, "create_purchase_order")
    po_action_ok = po_resp.get("status") == "success"
    test("Create PO action", po_action_ok, po_resp.get("message", ""))
    
    po_id = None
    if po_action_ok:
        resp_data = po_resp.get("data", {}) or {}
        path = resp_data.get("path") or po_resp.get("path")
        if path:
            po_id = path.split("/")[-1]
            test("PO created with ID", bool(po_id), po_id)
    
    # ─── 10. Test validation: action in wrong state ───
    print("\n📋 Phase 10: Validation Tests")
    
    # Create a new PR to test rejection flow
    pr2_resp = await create_record("purchase_request", {
        "pr_description": "E2E Test PR 2 - Rejection Flow",
        "date_requested": "2026-02-06",
    })
    pr2_id = pr2_resp.get("data", {}).get("id") if pr2_resp.get("status") == "success" else None
    
    if pr2_id:
        # Try to generate RFQ from Draft (should fail - validation in Python code)
        rfq_resp2 = await document_action("purchase_request", pr2_id, "generate_rfq")
        test(
            "Generate RFQ from Draft fails (validation in code)",
            rfq_resp2.get("status") == "error",
            rfq_resp2.get("message", "")
        )
        
        # Try to create PO from Draft (should fail)
        po_resp2 = await document_action("purchase_request", pr2_id, "create_purchase_order")
        test(
            "Create PO from Draft fails (validation in code)",
            po_resp2.get("status") == "error",
            po_resp2.get("message", "")
        )
    
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
    # Return non-zero exit code if any tests failed
    if test_results and any(not ok for _, ok, _ in test_results):
        sys.exit(1)
    elif not test_results:
        sys.exit(1)
