"""
Comprehensive Business Logic Flow Tests
Tests all 4 workflows: PR, Stock Count, Maintenance, Asset
Simulates frontend API calls as a user would make them.
"""
import os
import requests
import json
import time
import sys
from typing import Optional, Dict, Any, List

BASE_URL = "http://localhost:8000"
TOKEN = None
RESULTS = []
_CURRENT_SECTION = ""
# Set VERBOSE=False to suppress per-step prints (runner mode).
# Set VERBOSE=True (or run file directly) for full debug output.
VERBOSE = os.environ.get("FLOW_VERBOSE", "0") == "1"

# ─── Real reference IDs from seeded DB ──────────────────────────────────────
SITE        = "SITE-0001"
DEPT        = "DEPT-0003"
EMP         = "EMP-00001"
ITEM1       = "ITM-000096"
ITEM2       = "ITM-000095"
VENDOR1     = "VND-00001"
VENDOR2     = "VND-00002"
LOCATION    = "LOC-00001"
UOM         = "UOM-00001"
COST_CODE   = "CC-0001"
ASSET_CLASS = "AC-00001"
RAT         = "RAT-0001"

# ─── Helpers ────────────────────────────────────────────────────────────────

def login():
    global TOKEN
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      data={"username": "admin", "password": "admin123"})
    r.raise_for_status()
    TOKEN = r.json()["access_token"]
    print(f"✅ Logged in as admin")

def h():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def api_get(path, params=None):
    return requests.get(f"{BASE_URL}{path}", headers=h(), params=params)

def api_post(path, data):
    return requests.post(f"{BASE_URL}{path}", headers=h(), json=data)

def create_entity(entity, data):
    """POST /api/entity/{entity}/action  action=create"""
    r = api_post(f"/api/entity/{entity}/action", {"action": "create", "data": data})
    if r.status_code not in (200, 201):
        if VERBOSE: print(f"  ❌ CREATE {entity} failed: {r.status_code} {r.text[:300]}")
        return None
    result = r.json()
    if result.get("status") == "error":
        if VERBOSE: print(f"  ❌ CREATE {entity} error: {result.get('message')} {str(result.get('errors',''))[:200]}")
        return None
    record_id = (result.get("data") or {}).get("id") or result.get("id")
    if VERBOSE: print(f"  ✅ Created {entity}: {record_id}")
    return record_id

def get_entity(entity, record_id):
    """GET /api/entity/{entity}/detail/{id}"""
    r = api_get(f"/api/entity/{entity}/detail/{record_id}")
    if r.status_code != 200:
        if VERBOSE: print(f"  ❌ GET {entity}/{record_id}: {r.status_code} {r.text[:200]}")
        return None
    result = r.json()
    return result.get("data", result)

def update_entity(entity, record_id, data):
    """POST /api/entity/{entity}/action  action=update"""
    r = api_post(f"/api/entity/{entity}/action", {"action": "update", "id": record_id, "data": data})
    if r.status_code != 200:
        if VERBOSE: print(f"  ❌ UPDATE {entity}/{record_id}: {r.status_code} {r.text[:200]}")
        return False
    result = r.json()
    if result.get("status") == "error":
        if VERBOSE: print(f"  ❌ UPDATE {entity}/{record_id} error: {result.get('message')}")
        return False
    return True

def do_workflow(entity, record_id, action):
    """POST /api/entity/{entity}/workflow  {action, id}"""
    r = api_post(f"/api/entity/{entity}/workflow", {"action": action, "id": record_id})
    if r.status_code != 200:
        if VERBOSE: print(f"  ❌ WORKFLOW {entity}/{record_id} [{action}]: {r.status_code} {r.text[:300]}")
        return None
    result = r.json()
    if result.get("status") == "error":
        if VERBOSE: print(f"  ❌ WORKFLOW {entity}/{record_id} [{action}] error: {result.get('message')}")
        return None
    if VERBOSE: print(f"  ✅ Workflow [{action}] on {entity}/{record_id}: {result.get('message','OK')}")
    return result

def do_action(entity, record_id, action, payload=None):
    """POST /api/entity/{entity}/{id}/action/{action_name}"""
    r = api_post(f"/api/entity/{entity}/{record_id}/action/{action}", payload or {})
    if r.status_code != 200:
        if VERBOSE: print(f"  ❌ ACTION {entity}/{record_id} [{action}]: {r.status_code} {r.text[:300]}")
        return None
    result = r.json()
    if result.get("status") == "error":
        if VERBOSE: print(f"  ❌ ACTION {entity}/{record_id} [{action}] error: {result.get('message')}")
        return None
    if VERBOSE: print(f"  ✅ Action [{action}] on {entity}/{record_id}: {result.get('message','OK')}")
    return result

def list_entity(entity, limit=200):
    all_records = []
    page = 1
    while True:
        r = api_get(f"/api/entity/{entity}/list", params={"limit": 20, "page": page})
        if r.status_code != 200:
            if VERBOSE: print(f"  ❌ LIST {entity}: {r.status_code}")
            break
        data = r.json()
        records = data.get("data") or data.get("records") or []
        all_records.extend(records)
        total = data.get("total", 0)
        if len(all_records) >= total or len(records) == 0 or len(all_records) >= limit:
            break
        page += 1
    return all_records

def check(condition, description, detail=""):
    global _CURRENT_SECTION
    if VERBOSE:
        status = "✅ PASS" if condition else "❌ FAIL"
        msg = f"  {status}: {description}"
        if detail:
            msg += f" [{detail}]"
        print(msg)
    RESULTS.append({"pass": condition, "desc": description, "detail": str(detail), "section": _CURRENT_SECTION})
    return condition

def section(title):
    global _CURRENT_SECTION
    _CURRENT_SECTION = title
    if VERBOSE:
        print(f"\n{'='*65}")
        print(f"  {title}")
        print(f"{'='*65}")

def sub(title):
    if VERBOSE:
        print(f"\n  --- {title} ---")

def get_linked(entity, field, value, limit=200):
    records = list_entity(entity, limit=limit)
    return [r for r in records if str(r.get(field, "")) == str(value)]

