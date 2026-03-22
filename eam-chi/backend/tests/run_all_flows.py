"""
Main runner for all business logic flow tests.
Run: python tests/run_all_flows.py

Output is clean — server logs are suppressed. Only test results shown.
"""
import sys, os, time

# ── Suppress server log noise from stderr ──────────────────────────────────
# The backend server runs separately; its uvicorn logs bleed into this terminal.
# Redirect stderr to /dev/null for clean output.
class _SuppressServerLogs:
    """Context manager: suppress lines that look like server access logs."""
    def __init__(self):
        self._orig = sys.stderr
    def write(self, s):
        # Pass through lines that are clearly from our test code
        if any(x in s for x in ["INFO:", "WARNING:", "DEBUG:", "Emitting", "Registered", "Loaded module"]):
            return
        self._orig.write(s)
    def flush(self):
        self._orig.flush()
    def __enter__(self):
        sys.stderr = self
        return self
    def __exit__(self, *a):
        sys.stderr = self._orig

sys.path.insert(0, os.path.dirname(__file__))

from test_business_logic_flows import login, RESULTS, section, check
from test_pr_flows import test_pr_path_a, test_pr_path_b, test_pr_path_c
from test_sc_flows import test_stock_count
from test_maint_flows import test_maintenance_path_a, test_maintenance_path_b
from test_asset_flows import test_asset_path_a, test_asset_path_b


def print_summary(elapsed: float):
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["pass"])
    failed = total - passed

    print(f"\n{'='*65}")
    print(f"  FINAL TEST SUMMARY  ({elapsed:.1f}s)")
    print(f"{'='*65}")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")
    print(f"{'='*65}")

    if failed > 0:
        print(f"\n  FAILED CHECKS:")
        for r in RESULTS:
            if not r["pass"]:
                print(f"  ❌  {r['desc']}  [{r['detail']}]")

    print(f"\n  FULL CHECKLIST:")
    current_section = ""
    for r in RESULTS:
        if r.get("section") and r["section"] != current_section:
            current_section = r["section"]
            print(f"\n  {current_section}")
        status = "✅" if r["pass"] else "❌"
        print(f"    {status} {r['desc']}")


if __name__ == "__main__":
    t0 = time.time()
    login()

    # ── 1. Purchase Request Flows ──────────────────────────────────────────
    section("=== MODULE 1: PURCHASE REQUEST ===")
    print("  Running PR Path A (Direct PO)...")
    test_pr_path_a()
    print("  Running PR Path B (RFQ)...")
    test_pr_path_b()
    print("  Running PR Path C (Reject/Revise)...")
    test_pr_path_c()

    # ── 2. Stock Count Flow ────────────────────────────────────────────────
    section("=== MODULE 2: STOCK COUNT ===")
    print("  Running Stock Count...")
    test_stock_count()

    # ── 3. Maintenance Flows ───────────────────────────────────────────────
    section("=== MODULE 3: MAINTENANCE ===")
    print("  Running Maintenance Path A (Standard)...")
    test_maintenance_path_a()
    print("  Running Maintenance Path B (Emergency)...")
    test_maintenance_path_b()

    # ── 4. Asset Flows ─────────────────────────────────────────────────────
    section("=== MODULE 4: ASSET ===")
    print("  Running Asset Path A (Lifecycle)...")
    test_asset_path_a()
    print("  Running Asset Path B (Equipment)...")
    test_asset_path_b()

    print_summary(time.time() - t0)
