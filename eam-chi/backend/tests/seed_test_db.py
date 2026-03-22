"""
Seed minimal reference data into eam_test local DB for fast testing.
Run once before tests: python tests/seed_test_db.py
"""
import psycopg2
import hashlib
import uuid
from datetime import datetime

DB = "postgresql://eam_user@localhost:5432/eam_test"

def get_conn():
    return psycopg2.connect(DB)

def run(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"  WARN: {e}")
    finally:
        conn.close()

def upsert(table, id_col, id_val, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cols = list(data.keys())
        vals = list(data.values())
        set_clause = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols)
        placeholders = ", ".join(["%s"] * len(vals))
        sql = f"""
            INSERT INTO {table} ({id_col}, {', '.join(cols)})
            VALUES (%s, {placeholders})
            ON CONFLICT ({id_col}) DO UPDATE SET {set_clause}
        """
        cur.execute(sql, [id_val] + vals)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"  WARN upsert {table}/{id_val}: {e}")
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """bcrypt-compatible hash — use passlib if available, else sha256 fallback"""
    try:
        from passlib.context import CryptContext
        ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return ctx.hash(password)
    except ImportError:
        return hashlib.sha256(password.encode()).hexdigest()

def seed():
    print("Seeding test DB...")

    # ── Admin user ──────────────────────────────────────────────────────────
    admin_id = str(uuid.uuid4())
    hashed = hash_password("admin123")
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username='admin'")
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO users (id, username, email, hashed_password, is_active, is_superuser, full_name)
                VALUES (%s, 'admin', 'admin@test.com', %s, true, true, 'Admin User')
            """, (admin_id, hashed))
            conn.commit()
            print("  ✅ Admin user created")
        else:
            admin_id = row[0]
            print("  ✅ Admin user exists")
    except Exception as e:
        conn.rollback()
        print(f"  WARN admin user: {e}")
    finally:
        conn.close()

    now = datetime.utcnow().isoformat()

    # ── Core reference data ─────────────────────────────────────────────────
    upsert("organization", "id", "ORG-0001", {"name": "Test Org", "created_at": now, "updated_at": now})
    upsert("site", "id", "SITE-0001", {"site_name": "Test Site", "organization": "ORG-0001", "created_at": now, "updated_at": now})
    upsert("department", "id", "DEPT-0003", {"department_name": "Maintenance", "site": "SITE-0001", "created_at": now, "updated_at": now})
    upsert("cost_code", "id", "CC-0001", {"cost_code_name": "General", "created_at": now, "updated_at": now})

    # Employee
    upsert("employee", "id", "EMP-00001", {
        "first_name": "Test", "last_name": "Employee",
        "site": "SITE-0001", "department": "DEPT-0003",
        "created_at": now, "updated_at": now
    })

    # Unit of measure
    upsert("unit_of_measure", "id", "UOM-00001", {"uom_name": "Each", "uom_abbreviation": "EA", "created_at": now, "updated_at": now})

    # Items
    upsert("item", "id", "ITM-000096", {
        "item_name": "Test Item 1", "item_type": "Inventory Item",
        "unit_of_measure": "UOM-00001", "is_serialized": False, "is_equipment": False,
        "created_at": now, "updated_at": now
    })
    upsert("item", "id", "ITM-000095", {
        "item_name": "Test Item 2", "item_type": "Inventory Item",
        "unit_of_measure": "UOM-00001", "is_serialized": False, "is_equipment": False,
        "created_at": now, "updated_at": now
    })

    # Vendors
    upsert("vendor", "id", "VND-00001", {"vendor_name": "Vendor One", "created_at": now, "updated_at": now})
    upsert("vendor", "id", "VND-00002", {"vendor_name": "Vendor Two", "created_at": now, "updated_at": now})

    # Location
    upsert("location", "id", "LOC-00001", {
        "location_name": "Main Warehouse", "site": "SITE-0001",
        "created_at": now, "updated_at": now
    })

    # Asset class
    upsert("asset_class", "id", "AC-00001", {
        "asset_class_name": "General Equipment",
        "created_at": now, "updated_at": now
    })

    # Position (for asset install tests)
    upsert("position", "id", "POS-00001", {
        "position_name": "Test Position", "site": "SITE-0001",
        "created_at": now, "updated_at": now
    })

    # Resource type (for maintenance)
    try:
        upsert("resource_type", "id", "RAT-0001", {
            "resource_type_name": "Technician",
            "created_at": now, "updated_at": now
        })
    except Exception:
        pass  # table may not exist

    # Inventory for stock count tests
    upsert("inventory", "id", "INV-TEST-01", {
        "item": "ITM-000096", "location": "LOC-00001",
        "site": "SITE-0001", "department": "DEPT-0003",
        "quantity_on_hand": 100, "unit_cost": 10.0,
        "created_at": now, "updated_at": now
    })

    print("  ✅ Reference data seeded")
    print("\nTest DB ready. IDs:")
    print("  SITE=SITE-0001  DEPT=DEPT-0003  EMP=EMP-00001")
    print("  ITEM1=ITM-000096  ITEM2=ITM-000095")
    print("  VENDOR1=VND-00001  VENDOR2=VND-00002")
    print("  LOCATION=LOC-00001  COST_CODE=CC-0001")
    print("  ASSET_CLASS=AC-00001  POSITION=POS-00001")

if __name__ == "__main__":
    seed()
