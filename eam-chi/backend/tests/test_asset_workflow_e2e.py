"""
Asset Workflow — End-to-End Test
Tests the full asset lifecycle per asset_workflow.md.
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None
results = []


def H():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


async def POST(path, data=None, form=False):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as c:
        if form:
            return (await c.post(path, data=data or {}, headers=H())).json()
        return (await c.post(path, json=data or {}, headers=H())).json()


async def GET(path):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as c:
        return (await c.get(path, headers=H())).json()


async def create(entity, data):
    return await POST(f"/api/entity/{entity}/action", {"action": "create", "data": data})


async def update(entity, rid, data):
    return await POST(f"/api/entity/{entity}/action", {"action": "update", "id": rid, "data": data})


async def wf(entity, rid, action_slug):
    return await POST(f"/api/entity/{entity}/workflow", {"action": action_slug, "id": rid})


async def detail(entity, rid):
    return await GET(f"/api/entity/{entity}/detail/{rid}")


async def lst(entity, qs=""):
    return await GET(f"/api/entity/{entity}/list?page=1&page_size=50{qs}")


def state_eq(val, slug):
    if not val:
        return False
    return val.lower().replace(" ", "_") == slug.lower().replace(" ", "_")


def test(name, passed, detail_str=""):
    results.append((name, passed, detail_str))
    icon = "✅" if passed else "❌"
    suffix = f" — {detail_str}" if detail_str else ""
    print(f"  {icon} {name}{suffix}")


def log(msg, indent=1):
    print("  " * indent + msg)


def _summary():
    print("\n" + "=" * 70)
    passed = sum(1 for _, p, _ in results if p)
    failed = len(results) - passed
    print(f"RESULTS: {passed}/{len(results)} passed, {failed} failed")
    print("=" * 70)
    if failed:
        print("\nFailed tests:")
        for name, p, d in results:
            if not p:
                print(f"  ❌ {name} — {d}")


def _redirect(r):
    """Extract redirect path from workflow response (lives in data dict)."""
    resp_data = r.get("data") or {}
    return resp_data.get("redirect_path")


async def main():
    global TOKEN

    print("=" * 70)
    print("ASSET WORKFLOW — END-TO-END TEST")
    print("=" * 70)

    # ── Phase 1: Auth ─────────────────────────────────────────────────────────
    print("\n📋 Phase 1: Authentication")
    login = await POST("/api/auth/login", {"username": "admin", "password": "admin123"}, form=True)
    TOKEN = login.get("access_token")
    test("Login as admin", TOKEN is not None)
    if not TOKEN:
        _summary(); return

    # ── Phase 2: Metadata ─────────────────────────────────────────────────────
    print("\n📋 Phase 2: Entity Metadata Validation")
    meta_r = await GET("/api/meta/asset")
    meta = meta_r.get("data", {}) if meta_r.get("status") == "success" else meta_r
    test("asset metadata loads", bool(meta.get("fields")))

    wf_meta = meta.get("workflow") or {}
    states = [s.get("slug") or s.get("name", "").lower() for s in wf_meta.get("states", [])]
    test("asset workflow enabled", bool(states), str(states))
    for s in ["acquired", "inspected", "active", "inactive", "under_maintenance",
              "under_repair", "decommissioned", "disposed", "failed_inspection"]:
        test(f"state '{s}' exists", s in states)

    fields_by_name = {f["name"]: f for f in meta.get("fields", [])}
    test("bypass_process field exists", "bypass_process" in fields_by_name)
    link_entities = [lk.get("entity") for lk in meta.get("links", [])]
    for lk in ["asset_property", "asset_position", "sub_asset", "maintenance_request", "incident"]:
        test(f"link '{lk}' exists", lk in link_entities)

    # ── Phase 3: Reference data ───────────────────────────────────────────────
    print("\n📋 Phase 3: Reference Data")
    site_id = None
    site_r = await lst("site")
    if site_r.get("data"):
        site_id = site_r["data"][0]["id"]
    test("site exists", site_id is not None, str(site_id))

    rat_r = await lst("request_activity_type")
    rat_types = {r.get("type", "").lower() for r in (rat_r.get("data") or [])}
    test("activity type 'Inspect Asset' exists", any("inspect" in t for t in rat_types), str(rat_types))
    test("activity type 'Maintain Asset' exists", any("maintain" in t for t in rat_types), str(rat_types))

    # ── Phase 4: Create Asset (bypass ON) ────────────────────────────────────
    print("\n📋 Phase 4: Create Asset (bypass_process=True)")
    ts = f"{asyncio.get_event_loop().time():.0f}"
    asset_r = await create("asset", {
        "asset_tag": f"TEST-BP-{ts}",
        "description": "E2E Test Asset (bypass)",
        "site": site_id,
        "item_type": "Asset Item",
        "is_equipment": False,
        "bypass_process": True,
        "workflow_state": "acquired",
    })
    asset_id = asset_r.get("data", {}).get("id") if asset_r.get("status") == "success" else None
    test("Create Asset (bypass ON)", asset_id is not None, asset_r.get("message", ""))
    if not asset_id:
        _summary(); return

    asset_rec = (await detail("asset", asset_id)).get("data", {})
    ws = asset_rec.get("workflow_state") or asset_r.get("data", {}).get("workflow_state")
    test("Initial state is acquired", state_eq(ws, "acquired"), str(ws))

    # ── Phase 5: Inventory auto-provisioning ─────────────────────────────────
    print("\n📋 Phase 5: Inventory Auto-Provisioning")
    inv_id = asset_rec.get("inventory")
    test("Inventory auto-provisioned (bypass=True)", inv_id is not None, str(inv_id))

    # ── Phase 6: inspect_asset → WOA + MR ────────────────────────────────────
    print("\n📋 Phase 6: Inspect Asset → WOA + MR")
    inspect_r = await wf("asset", asset_id, "inspect_asset")
    inspect_ok = inspect_r.get("status") == "success"
    test("inspect_asset succeeds", inspect_ok, inspect_r.get("message", ""))

    mr_id = None
    if inspect_ok:
        asset_after = (await detail("asset", asset_id)).get("data", {})
        test("State is inspected", state_eq(asset_after.get("workflow_state"), "inspected"),
             asset_after.get("workflow_state"))

        redirect = _redirect(inspect_r)
        test("inspect_asset redirects to MR", redirect is not None, str(redirect))
        if redirect:
            mr_id = redirect.split("/")[-1]
            mr_rec = (await detail("maintenance_request", mr_id)).get("data", {})
            test("MR linked to asset", mr_rec.get("asset") == asset_id, mr_rec.get("asset"))
            test("MR auto-advanced to approved",
                 state_eq(mr_rec.get("workflow_state"), "approved"),
                 mr_rec.get("workflow_state"))
            woa_id = mr_rec.get("work_order_activity")
            test("MR linked to WOA", woa_id is not None, str(woa_id))
            if woa_id:
                woa_rec = (await detail("work_order_activity", woa_id)).get("data", {})
                test("WOA status is awaiting_resources",
                     state_eq(woa_rec.get("workflow_state"), "awaiting_resources"),
                     woa_rec.get("workflow_state"))

    # ── Phase 7: failed_inspection ────────────────────────────────────────────
    print("\n📋 Phase 7: Failed Inspection (simple transition)")
    fail_r = await create("asset", {
        "asset_tag": f"TEST-FAIL-{ts}",
        "description": "E2E Fail Asset",
        "site": site_id,
        "item_type": "Asset Item",
    })
    fail_id = fail_r.get("data", {}).get("id") if fail_r.get("status") == "success" else None
    if fail_id:
        await wf("asset", fail_id, "inspect_asset")
        fi_r = await wf("asset", fail_id, "failed_inspection")
        test("failed_inspection succeeds", fi_r.get("status") == "success", fi_r.get("message", ""))
        fi_rec = (await detail("asset", fail_id)).get("data", {})
        test("State is failed_inspection",
             state_eq(fi_rec.get("workflow_state"), "failed_inspection"),
             fi_rec.get("workflow_state"))

    # ── Phase 8: install_asset (bypass ON → AssetPosition) ───────────────────
    print("\n📋 Phase 8: Install Asset (bypass ON → direct AssetPosition)")
    install_r = await wf("asset", asset_id, "install_asset")
    install_ok = install_r.get("status") == "success"
    test("install_asset succeeds (bypass ON)", install_ok, install_r.get("message", ""))

    apos_id = None
    if install_ok:
        asset_active = (await detail("asset", asset_id)).get("data", {})
        test("State is active after install",
             state_eq(asset_active.get("workflow_state"), "active"),
             asset_active.get("workflow_state"))
        redirect = _redirect(install_r)
        test("install_asset redirects to AssetPosition", redirect is not None, str(redirect))
        if redirect:
            apos_id = redirect.split("/")[-1]
            apos_rec = (await detail("asset_position", apos_id)).get("data", {})
            test("AssetPosition linked to asset", apos_rec.get("asset") == asset_id,
                 apos_rec.get("asset"))
            test("AssetPosition has date_installed", apos_rec.get("date_installed") is not None,
                 str(apos_rec.get("date_installed")))
            test("AssetPosition date_removed is None", apos_rec.get("date_removed") is None,
                 str(apos_rec.get("date_removed")))

    # ── Phase 9: install_asset blocked (open position) ────────────────────────
    print("\n📋 Phase 9: Install Asset Blocked (open position exists)")
    await wf("asset", asset_id, "putaway")
    install_blocked = await wf("asset", asset_id, "install_asset")
    test("install_asset blocked when open position exists",
         install_blocked.get("status") == "error",
         install_blocked.get("message", ""))

    # ── Phase 10: maintain_asset → WOA + MR ──────────────────────────────────
    print("\n📋 Phase 10: Maintain Asset → WOA + MR")
    # Close open position, re-install, then maintain
    if apos_id:
        await update("asset_position", apos_id, {"date_removed": "2026-01-01"})
    install2_r = await wf("asset", asset_id, "install_asset")
    test("install_asset succeeds after closing position",
         install2_r.get("status") == "success", install2_r.get("message", ""))

    maintain_r = await wf("asset", asset_id, "maintain_asset")
    maintain_ok = maintain_r.get("status") == "success"
    test("maintain_asset succeeds", maintain_ok, maintain_r.get("message", ""))

    apos2_id = None
    if install2_r.get("status") == "success":
        redirect2 = _redirect(install2_r)
        if redirect2:
            apos2_id = redirect2.split("/")[-1]

    if maintain_ok:
        asset_maint = (await detail("asset", asset_id)).get("data", {})
        test("State is under_maintenance",
             state_eq(asset_maint.get("workflow_state"), "under_maintenance"),
             asset_maint.get("workflow_state"))
        redirect = _redirect(maintain_r)
        if redirect:
            mr2_id = redirect.split("/")[-1]
            mr2_rec = (await detail("maintenance_request", mr2_id)).get("data", {})
            test("Maintain MR auto-approved",
                 state_eq(mr2_rec.get("workflow_state"), "approved"),
                 mr2_rec.get("workflow_state"))

    # ── Phase 11: remove_asset → closes open position ────────────────────────
    print("\n📋 Phase 11: Remove Asset → closes AssetPosition")
    remove_r = await wf("asset", asset_id, "remove_asset")
    remove_ok = remove_r.get("status") == "success"
    test("remove_asset succeeds", remove_ok, remove_r.get("message", ""))

    if remove_ok:
        asset_removed = (await detail("asset", asset_id)).get("data", {})
        test("State is inactive after remove_asset",
             state_eq(asset_removed.get("workflow_state"), "inactive"),
             asset_removed.get("workflow_state"))
        redirect = _redirect(remove_r)
        if redirect:
            closed_pos = (await detail("asset_position", redirect.split("/")[-1])).get("data", {})
            test("AssetPosition date_removed set",
                 closed_pos.get("date_removed") is not None,
                 str(closed_pos.get("date_removed")))

    # ── Phase 12: complete (under_maintenance → active) ───────────────────────
    print("\n📋 Phase 12: Complete (simple transition)")
    if apos2_id:
        await update("asset_position", apos2_id, {"date_removed": "2026-01-01"})
    install3_r = await wf("asset", asset_id, "install_asset")
    if install3_r.get("status") == "success":
        maintain3_r = await wf("asset", asset_id, "maintain_asset")
        if maintain3_r.get("status") == "success":
            complete_r = await wf("asset", asset_id, "complete")
            test("complete succeeds", complete_r.get("status") == "success",
                 complete_r.get("message", ""))
            asset_comp = (await detail("asset", asset_id)).get("data", {})
            test("State is active after complete",
                 state_eq(asset_comp.get("workflow_state"), "active"),
                 asset_comp.get("workflow_state"))

    # ── Phase 13: internal_repair → WOA + MR ─────────────────────────────────
    print("\n📋 Phase 13: Internal Repair → WOA + MR")
    await wf("asset", asset_id, "putaway")
    repair_r = await wf("asset", asset_id, "internal_repair")
    repair_ok = repair_r.get("status") == "success"
    test("internal_repair succeeds", repair_ok, repair_r.get("message", ""))

    if repair_ok:
        asset_repair = (await detail("asset", asset_id)).get("data", {})
        test("State is under_repair",
             state_eq(asset_repair.get("workflow_state"), "under_repair"),
             asset_repair.get("workflow_state"))
        redirect = _redirect(repair_r)
        if redirect:
            mr_rep = (await detail("maintenance_request", redirect.split("/")[-1])).get("data", {})
            test("Repair MR auto-approved",
                 state_eq(mr_rep.get("workflow_state"), "approved"),
                 mr_rep.get("workflow_state"))

    await wf("asset", asset_id, "finish_repair")
    asset_fin = (await detail("asset", asset_id)).get("data", {})
    test("finish_repair → inactive",
         state_eq(asset_fin.get("workflow_state"), "inactive"),
         asset_fin.get("workflow_state"))

    # ── Phase 14: send_to_vendor → WOA + MR ──────────────────────────────────
    print("\n📋 Phase 14: Send to Vendor → WOA + MR")
    vendor_r = await wf("asset", asset_id, "send_to_vendor")
    vendor_ok = vendor_r.get("status") == "success"
    test("send_to_vendor succeeds", vendor_ok, vendor_r.get("message", ""))
    if vendor_ok:
        asset_vendor = (await detail("asset", asset_id)).get("data", {})
        test("State is under_repair after send_to_vendor",
             state_eq(asset_vendor.get("workflow_state"), "under_repair"),
             asset_vendor.get("workflow_state"))
        redirect = _redirect(vendor_r)
        test("send_to_vendor creates MR", redirect is not None, str(redirect))

    # Back to inactive via finish_repair
    await wf("asset", asset_id, "finish_repair")
    # Ensure asset is inactive before issue_equipment
    asset_pre_issue = (await detail("asset", asset_id)).get("data", {})
    if not state_eq(asset_pre_issue.get("workflow_state"), "inactive"):
        await wf("asset", asset_id, "putaway")

    # ── Phase 15: issue_equipment → ItemIssue ────────────────────────────────
    print("\n📋 Phase 15: Issue Equipment → ItemIssue")
    issue_r = await wf("asset", asset_id, "issue_equipment")
    issue_ok = issue_r.get("status") == "success"
    test("issue_equipment succeeds", issue_ok, issue_r.get("message", ""))
    if issue_ok:
        asset_issued = (await detail("asset", asset_id)).get("data", {})
        test("State is active after issue_equipment",
             state_eq(asset_issued.get("workflow_state"), "active"),
             asset_issued.get("workflow_state"))
        redirect = _redirect(issue_r)
        test("issue_equipment creates ItemIssue", redirect is not None, str(redirect))
        if redirect:
            ii_rec = (await detail("item_issue", redirect.split("/")[-1])).get("data", {})
            test("ItemIssue has site", ii_rec.get("site") == site_id, str(ii_rec.get("site")))

    # ── Phase 16: retire → decommissioned ────────────────────────────────────
    print("\n📋 Phase 16: Retire Asset → Decommissioned")
    await wf("asset", asset_id, "putaway")
    retire_r = await wf("asset", asset_id, "retire_asset")
    test("retire_asset succeeds", retire_r.get("status") == "success", retire_r.get("message", ""))
    asset_ret = (await detail("asset", asset_id)).get("data", {})
    test("State is decommissioned after retire",
         state_eq(asset_ret.get("workflow_state"), "decommissioned"),
         asset_ret.get("workflow_state"))

    # ── Phase 17: recommission → active ──────────────────────────────────────
    print("\n📋 Phase 17: Recommission → Active")
    recommission_r = await wf("asset", asset_id, "recommission")
    test("recommission succeeds", recommission_r.get("status") == "success",
         recommission_r.get("message", ""))
    asset_recom = (await detail("asset", asset_id)).get("data", {})
    test("State is active after recommission",
         state_eq(asset_recom.get("workflow_state"), "active"),
         asset_recom.get("workflow_state"))

    # ── Phase 18: decommission → dispose ─────────────────────────────────────
    print("\n📋 Phase 18: Decommission → Dispose")
    decom_r = await wf("asset", asset_id, "decommission")
    test("decommission succeeds", decom_r.get("status") == "success", decom_r.get("message", ""))
    dispose_r = await wf("asset", asset_id, "dispose")
    dispose_ok = dispose_r.get("status") == "success"
    test("dispose succeeds (regular Asset Item)", dispose_ok, dispose_r.get("message", ""))
    if dispose_ok:
        asset_disp = (await detail("asset", asset_id)).get("data", {})
        test("State is disposed",
             state_eq(asset_disp.get("workflow_state"), "disposed"),
             asset_disp.get("workflow_state"))
        redirect = _redirect(dispose_r)
        test("dispose redirects to Disposed record", redirect is not None, str(redirect))
        if redirect:
            dsp_rec = (await detail("disposed", redirect.split("/")[-1])).get("data", {})
            test("Disposed record linked to asset", dsp_rec.get("asset") == asset_id,
                 dsp_rec.get("asset"))

    # ── Phase 19: Fixed Asset — dispose blocked with open position ────────────
    print("\n📋 Phase 19: Fixed Asset — Dispose Blocked (open position)")
    fixed_r = await create("asset", {
        "asset_tag": f"TEST-FX-{ts}",
        "description": "E2E Fixed Asset",
        "site": site_id,
        "item_type": "Fixed Asset Item",
        "bypass_process": True,
    })
    fixed_id = fixed_r.get("data", {}).get("id") if fixed_r.get("status") == "success" else None
    test("Create Fixed Asset Item", fixed_id is not None, fixed_r.get("message", ""))

    if fixed_id:
        await wf("asset", fixed_id, "inspect_asset")
        comm_r = await wf("asset", fixed_id, "commission")
        test("commission succeeds (Fixed Asset)", comm_r.get("status") == "success",
             comm_r.get("message", ""))
        fixed_active = (await detail("asset", fixed_id)).get("data", {})
        test("Fixed Asset active after commission",
             state_eq(fixed_active.get("workflow_state"), "active"),
             fixed_active.get("workflow_state"))

        await wf("asset", fixed_id, "decommission")

        # Dispose with open position → blocked
        dispose_blocked = await wf("asset", fixed_id, "dispose")
        test("dispose blocked (Fixed Asset with open position)",
             dispose_blocked.get("status") == "error",
             dispose_blocked.get("message", ""))

        # Close position then dispose
        pos_list = await lst("asset_position", f"&asset={fixed_id}")
        for pos in (pos_list.get("data") or []):
            if not pos.get("date_removed"):
                await update("asset_position", pos["id"], {"date_removed": "2026-01-01"})

        dispose2_r = await wf("asset", fixed_id, "dispose")
        test("dispose succeeds after closing position",
             dispose2_r.get("status") == "success", dispose2_r.get("message", ""))
        if dispose2_r.get("status") == "success":
            fixed_disp = (await detail("asset", fixed_id)).get("data", {})
            test("Fixed Asset state is disposed",
                 state_eq(fixed_disp.get("workflow_state"), "disposed"),
                 fixed_disp.get("workflow_state"))

    # ── Phase 20: install_asset bypass OFF → WOA + MR ────────────────────────
    print("\n📋 Phase 20: Install Asset — bypass OFF → WOA + MR")
    nobp_r = await create("asset", {
        "asset_tag": f"TEST-NB-{ts}",
        "description": "E2E No-Bypass Asset",
        "site": site_id,
        "item_type": "Asset Item",
        "bypass_process": False,
    })
    nobp_id = nobp_r.get("data", {}).get("id") if nobp_r.get("status") == "success" else None
    if nobp_id:
        await wf("asset", nobp_id, "inspect_asset")
        install_nobp = await wf("asset", nobp_id, "install_asset")
        install_nobp_ok = install_nobp.get("status") == "success"
        test("install_asset (bypass OFF) succeeds", install_nobp_ok, install_nobp.get("message", ""))
        if install_nobp_ok:
            redirect = _redirect(install_nobp)
            test("install_asset (bypass OFF) creates MR",
                 redirect is not None and "maintenance_request" in (redirect or ""),
                 str(redirect))

    _summary()


if __name__ == "__main__":
    asyncio.run(main())
