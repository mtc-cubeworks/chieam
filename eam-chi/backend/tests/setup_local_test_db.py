#!/usr/bin/env python3
"""
Seed minimal reference data into eam_test local DB for fast testing.
Run once: python tests/setup_local_test_db.py

Uses direct psycopg2 SQL matching the actual local schema.
"""
import uuid
import psycopg2
from datetime import datetime

LOCAL_DB = "postgresql://eam_user@localhost:5432/eam_test"
NOW = datetime.utcnow().isoformat()


def conn():
    return psycopg2.connect(LOCAL_DB)


def upsert_sql(table, pk, pk_val, cols, vals):
    """Generic upsert: INSERT ... ON CONFLICT DO UPDATE."""
    c = conn()
    cur = c.cursor()
    try:
        col_list = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(vals))
        updates = ", ".join(f"{col}=EXCLUDED.{col}" for col in cols)
        sql = f"""
            INSERT INTO {table} ({pk}, {col_list})
            VALUES (%s, {placeholders})
            ON CONFLICT ({pk}) DO UPDATE SET {updates}
        """
        cur.execute(sql, [pk_val] + list(vals))
        c.commit()
    except Exception as e:
        c.rollback()
        print(f"  WARN {table}/{pk_val}: {e}")
    finally:
        c.close()


def seed():
    print("=== Setting up local eam_test DB ===\n")

    # ── Admin user ──────────────────────────────────────────────────────────
    try:
        import bcrypt
        pwd_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    except Exception:
        import hashlib
        # fallback: sha256 prefixed to look like bcrypt (won't verify via passlib but works for direct DB insert)
        pwd_hash = "$2b$12$fakehashfortest" + hashlib.sha256(b"admin123").hexdigest()[:38]

    admin_id = str(uuid.uuid4())
    c = conn()
    cur = c.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username='admin'")
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO users (id, username, email, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
                VALUES (%s, 'admin', 'admin@test.local', 'Admin User', %s, true, true, %s, %s)
            """, (admin_id, pwd_hash, NOW, NOW))
            c.commit()
            print("  ✅ Admin user created")
        else:
            admin_id = row[0]
            print("  ✅ Admin user exists")
    except Exception as e:
        c.rollback()
        print(f"  ❌ Admin user: {e}")
    finally:
        c.close()

    # ── Organization ────────────────────────────────────────────────────────
    upsert_sql("organization", "id", "ORG-0001",
        ["organization_name", "is_active", "created_at", "updated_at"],
        ["Test Organization", True, NOW, NOW])
    print("  ✅ Organization")

    # ── Site ────────────────────────────────────────────────────────────────
    upsert_sql("site", "id", "SITE-0001",
        ["site_name", "organization", "created_at", "updated_at"],
        ["Test Site", "ORG-0001", NOW, NOW])
    print("  ✅ Site")

    # ── Cost Code ───────────────────────────────────────────────────────────
    upsert_sql("cost_code", "id", "CC-0001",
        ["code", "description", "site", "created_at", "updated_at"],
        ["CC-0001", "General Cost Code", "SITE-0001", NOW, NOW])
    print("  ✅ Cost Code")

    # ── Department ──────────────────────────────────────────────────────────
    upsert_sql("department", "id", "DEPT-0003",
        ["department_name", "site", "created_at", "updated_at"],
        ["Maintenance", "SITE-0001", NOW, NOW])
    print("  ✅ Department")

    # ── Employee (linked to admin user) ─────────────────────────────────────
    # 'user' is a reserved word — must quote it
    c2 = conn()
    cur2 = c2.cursor()
    try:
        cur2.execute("""
            INSERT INTO employee (id, employee_name, "user", created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET employee_name=EXCLUDED.employee_name
        """, ("EMP-00001", "Test Employee", admin_id, NOW, NOW))
        c2.commit()
    except Exception as e:
        c2.rollback()
        print(f"  WARN employee: {e}")
    finally:
        c2.close()
    print("  ✅ Employee")

    # ── Location type (needed for location FK) ───────────────────────────────
    upsert_sql("location_type", "id", "LT-00001",
        ["name", "created_at", "updated_at"],
        ["Building", NOW, NOW])
    print("  ✅ Location Type")

    # ── Location ────────────────────────────────────────────────────────────
    upsert_sql("location", "id", "LOC-00001",
        ["name", "site", "created_at", "updated_at"],
        ["Main Warehouse", "SITE-0001", NOW, NOW])
    print("  ✅ Location")

    # ── Asset Class ─────────────────────────────────────────────────────────
    upsert_sql("asset_class", "id", "AC-00001",
        ["name", "created_at", "updated_at"],
        ["General Equipment", NOW, NOW])
    print("  ✅ Asset Class")

    # ── Unit of Measure ─────────────────────────────────────────────────────
    upsert_sql("unit_of_measure", "id", "UOM-00001",
        ["name", "short_name", "created_at", "updated_at"],
        ["Each", "EA", NOW, NOW])
    print("  ✅ Unit of Measure")

    # ── Items ───────────────────────────────────────────────────────────────
    upsert_sql("item", "id", "ITM-000096",
        ["item_name", "item_type", "is_serialized", "is_equipment", "created_at", "updated_at"],
        ["Test Item 1", "Inventory Item", False, False, NOW, NOW])
    upsert_sql("item", "id", "ITM-000095",
        ["item_name", "item_type", "is_serialized", "is_equipment", "created_at", "updated_at"],
        ["Test Item 2", "Inventory Item", False, False, NOW, NOW])
    print("  ✅ Items (ITM-000096, ITM-000095)")

    # ── Vendors ─────────────────────────────────────────────────────────────
    upsert_sql("vendor", "id", "VND-00001",
        ["vendor_name", "created_at", "updated_at"],
        ["Vendor One", NOW, NOW])
    upsert_sql("vendor", "id", "VND-00002",
        ["vendor_name", "created_at", "updated_at"],
        ["Vendor Two", NOW, NOW])
    print("  ✅ Vendors (VND-00001, VND-00002)")

    # ── Inventory (for stock count tests) ───────────────────────────────────
    c = conn()
    cur = c.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='inventory' AND column_name='quantity_on_hand'")
        has_qty = cur.fetchone()[0] > 0
        c.close()
    except Exception:
        has_qty = False
        c.close()

    if has_qty:
        upsert_sql("inventory", "id", "INV-TEST-01",
            ["item", "location", "site", "quantity_on_hand", "unit_cost", "created_at", "updated_at"],
            ["ITM-000096", "LOC-00001", "SITE-0001", 100, 10.0, NOW, NOW])
        print("  ✅ Inventory record")
    else:
        print("  ⚠️  Inventory table has no quantity_on_hand — skipping")

    # ── Position (for asset install) ─────────────────────────────────────────
    c = conn()
    cur = c.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='position'")
        has_pos = cur.fetchone()[0] > 0
        c.close()
    except Exception:
        has_pos = False
        c.close()

    if has_pos:
        upsert_sql('"position"', "id", "POS-00001",
            ["position_tag", "site", "created_at", "updated_at"],
            ["Test Position", "SITE-0001", NOW, NOW])
        print("  ✅ Position")

    print("\n=== Seeding workflows ===")
    import subprocess, os, sys
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql+asyncpg://eam_user@localhost:5432/eam_test"
    env["DATABASE_URL_SYNC"] = "postgresql://eam_user@localhost:5432/eam_test"
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "seed_workflows_from_excel.py"],
        cwd=backend_dir, env=env, capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  ✅ Workflows seeded")
    else:
        print(f"  ⚠️  Workflow seed: {result.stderr[-300:]}")

    print("\n=== Local test DB ready ===")
    print("  SITE=SITE-0001  DEPT=DEPT-0003  EMP=EMP-00001")
    print("  ITEM1=ITM-000096  ITEM2=ITM-000095")
    print("  VENDOR1=VND-00001  VENDOR2=VND-00002")
    print("  LOCATION=LOC-00001  COST_CODE=CC-0001")
    print("  ASSET_CLASS=AC-00001")


if __name__ == "__main__":
    seed()
