"""
SPMC EAM - Seed Labor & Costing
=================================
Populates 50+ records for:
- Labor: labor_group, labor (additional), labor_availability + details
- Costing: contractor, cost_code (additional)
"""
import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text

DB_URL = "postgresql://eam_spmc_user:CwSpmcSec2026mR7@localhost:5432/eam-spmc"
engine = create_engine(DB_URL)
NOW = datetime.now()

EMPLOYEES = ["EMP-0001","EMP-0002","EMP-0003","EMP-0004","EMP-0005",
             "EMP-0021","EMP-0022","EMP-0023","EMP-0024","EMP-0025"]
LOCATIONS = [f"LOC-{str(i).zfill(4)}" for i in range(1, 60)]
SITES = ["SITE-0001","SITE-0002","SITE-0003","SITE-0004"]

def rc(lst): return random.choice(lst)
def rand_date(start_ago=90, end_ago=0):
    return date.today() - timedelta(days=random.randint(end_ago, start_ago))

# ===================== DOMAIN DATA =====================

LABOR_GROUP_NAMES = [
    "Biomedical Engineering Team", "HVAC Maintenance Crew", "Electrical Team",
    "Plumbing & Piping Group", "Mechanical Maintenance", "Civil Works Team",
    "Carpentry & Woodwork", "Painting & Finishing", "Welding & Fabrication",
    "Fire Safety Team", "Medical Gas Technicians", "Elevator Maintenance",
    "Generator Operations", "Instrumentation & Controls", "Refrigeration Team",
    "Imaging Equipment Specialists", "Laboratory Equipment Team", "IT Infrastructure",
    "Boiler Operations Crew", "Grounds & Landscaping", "Water Treatment Operators",
    "Pneumatic Systems Team", "Kitchen Equipment Maintenance", "Laundry Equipment Crew",
    "Solar Energy Team", "Dental Equipment Specialists", "Ambulance Maintenance",
    "Security Systems Team", "Waste Management Crew", "Sterilization Equipment Team",
    "OR Equipment Specialists", "ICU Equipment Support", "ER Equipment Team",
    "Neonatal Equipment Group", "Dialysis Equipment Team", "Pharmacy Equipment",
    "Radiology QA Team", "Respiratory Equipment", "Pathology Lab Support",
    "Patient Monitoring Team", "Endoscopy Equipment", "Blood Bank Equipment",
    "Physical Therapy Equipment", "Central Supply Team", "Mortuary Systems",
    "Parking & Barriers", "Audio Visual Systems", "Furniture & Fixtures",
    "Building Exterior Team", "Emergency Preparedness Unit",
]

CONTRACTOR_NAMES = [
    "Mindanao Medical Equipment Services Inc.", "Davao HVAC Solutions Corp.",
    "Southern Phil. Electrical Contractors", "Aqua Flow Plumbing Services",
    "Pacific Elevator Maintenance Co.", "GenPower Generator Services",
    "MedTech Calibration Philippines", "FireGuard Safety Systems",
    "ColdChain Refrigeration Davao", "BioMed Solutions International",
    "Siemens Healthineers Philippines", "GE Healthcare Service Center",
    "Philips Medical Systems PH", "Johnson Controls Philippines",
    "Schneider Electric Philippines", "Daikin Philippines Inc.",
    "Otis Elevator Philippines", "KONE Philippines",
    "Carrier Air Conditioning", "Trane Philippines",
    "Honeywell Building Technologies", "ABB Philippines",
    "Emerson Philippines", "Bosch Security Systems PH",
    "Hikvision Philippines", "3M Philippines Healthcare",
    "Steris Corporation Philippines", "Getinge Philippines",
    "Draeger Medical Philippines", "Nihon Kohden Philippines",
    "Mindray Medical Philippines", "Olympus Medical Philippines",
    "Fujifilm Medical Systems PH", "Canon Medical Systems PH",
    "Shimadzu Philippines", "Roche Diagnostics Philippines",
    "Abbott Diagnostics PH", "Sysmex Philippines",
    "Beckman Coulter Philippines", "Bio-Rad Laboratories PH",
    "Davao Industrial Maintenance Corp.", "Southern Welding & Fabrication",
    "Metro Davao Painting Services", "Green Thumb Landscaping Davao",
    "Crystal Clear Water Treatment", "Davao Solar Power Solutions",
    "Safe Waste Management Services", "Davao IT Network Solutions",
    "Philippine Pest Control Services", "Mega Build Construction Davao",
]

COST_CODE_DATA = [
    ("PM-HVAC", "Preventive maintenance - HVAC systems"),
    ("PM-ELEC", "Preventive maintenance - Electrical systems"),
    ("PM-PLMB", "Preventive maintenance - Plumbing systems"),
    ("PM-MECH", "Preventive maintenance - Mechanical systems"),
    ("PM-BIOM", "Preventive maintenance - Biomedical equipment"),
    ("PM-FIRE", "Preventive maintenance - Fire safety systems"),
    ("PM-ELEV", "Preventive maintenance - Elevators"),
    ("PM-GENR", "Preventive maintenance - Generators"),
    ("PM-BOIL", "Preventive maintenance - Boilers & steam"),
    ("PM-MGAS", "Preventive maintenance - Medical gas systems"),
    ("CM-HVAC", "Corrective maintenance - HVAC systems"),
    ("CM-ELEC", "Corrective maintenance - Electrical systems"),
    ("CM-PLMB", "Corrective maintenance - Plumbing systems"),
    ("CM-MECH", "Corrective maintenance - Mechanical systems"),
    ("CM-BIOM", "Corrective maintenance - Biomedical equipment"),
    ("CM-GENR", "Corrective maintenance - Generators"),
    ("CAL-MED", "Calibration - Medical devices"),
    ("CAL-LAB", "Calibration - Laboratory equipment"),
    ("CAL-IMG", "Calibration - Imaging equipment"),
    ("CAL-MON", "Calibration - Patient monitoring"),
    ("OPS-UTIL", "Operations - Utilities"),
    ("OPS-WTRT", "Operations - Water treatment"),
    ("OPS-WSTE", "Operations - Waste management"),
    ("OPS-LAUN", "Operations - Laundry"),
    ("OPS-KTCH", "Operations - Kitchen equipment"),
    ("PRJ-RENO", "Project - Renovation"),
    ("PRJ-UPGR", "Project - Equipment upgrade"),
    ("PRJ-INST", "Project - New installation"),
    ("PRJ-ENRG", "Project - Energy efficiency"),
    ("PRJ-SAFE", "Project - Safety compliance"),
    ("EXT-CNTR", "External contractor services"),
    ("EXT-VEND", "External vendor service call"),
    ("EXT-WARR", "Warranty claim service"),
    ("SPR-HVAC", "Spare parts - HVAC"),
    ("SPR-ELEC", "Spare parts - Electrical"),
    ("SPR-BIOM", "Spare parts - Biomedical"),
    ("SPR-GENL", "Spare parts - General"),
    ("TRN-TECH", "Training - Technical staff"),
    ("TRN-OPER", "Training - Equipment operators"),
    ("TRN-SAFE", "Training - Safety protocols"),
]

LABORER_NAMES = [
    "Juan dela Cruz", "Maria Santos", "Pedro Reyes", "Ana Garcia",
    "Carlos Mendoza", "Rosa Fernandez", "Miguel Bautista", "Elena Cruz",
    "Roberto Aquino", "Carmen Ramos", "Jose Villanueva", "Linda Castillo",
    "Antonio Flores", "Teresa Morales", "Ricardo Navarro", "Gloria Ortega",
    "Fernando Torres", "Lucia Hernandez", "Eduardo Santiago", "Patricia Luna",
    "Marcos Dizon", "Yolanda Pascual", "Raul Evangelista", "Marites Soriano",
    "Ernesto Cabrera", "Rosemarie Tan", "Danilo Valdez", "Cristina Mercado",
    "Reynaldo Aguilar", "Milagros Santos", "Alfredo Manalo", "Josephine Cruz",
    "Armando Reyes", "Nelia Bautista", "Virgilio Ramos", "Carolina Flores",
    "Leonardo Garcia", "Lourdes Mendoza", "Rolando Aquino", "Felicitas Torres",
]

AVAILABILITY_STATUSES = ["Available", "Reserved", "On Leave", "Non-Working", "Holiday", "End Shift"]
HOURS = [f"{h:02d}:00" for h in range(6, 23)]


def _update_series(conn, prefix, val):
    conn.execute(text(
        "INSERT INTO series (name, current) VALUES (:name, :val) "
        "ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)"
    ), {"name": prefix, "val": val})


def seed():
    with engine.begin() as conn:
        # ============================================================
        # 1) LABOR GROUPS (50)
        # ============================================================
        print("Seeding Labor Groups...")
        lg_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM labor_group")).scalar()
        lg_start = max(lg_max + 1, 1)
        lg_ids = []
        for i in range(50):
            lg_id = f"LBRGRP-{str(lg_start+i).zfill(5)}"
            lg_ids.append(lg_id)
            conn.execute(text(
                "INSERT INTO labor_group (id, labor_group_name, created_at, updated_at) "
                "VALUES (:id,:name,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": lg_id, "name": LABOR_GROUP_NAMES[i], "now": NOW})
        _update_series(conn, "LBRGRP", lg_start + 50)
        print(f"  Created {len(lg_ids)} labor groups")

        # ============================================================
        # 2) CONTRACTORS (50)
        # ============================================================
        print("Seeding Contractors...")
        cn_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM contractor")).scalar()
        cn_start = max(cn_max + 1, 1)
        contractor_ids = []
        for i in range(50):
            cn_id = f"CNTR-{str(cn_start+i).zfill(5)}"
            contractor_ids.append(cn_id)
            conn.execute(text(
                "INSERT INTO contractor (id, contractor_name, created_at, updated_at) "
                "VALUES (:id,:name,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": cn_id, "name": CONTRACTOR_NAMES[i], "now": NOW})
        _update_series(conn, "CNTR", cn_start + 50)
        print(f"  Created {len(contractor_ids)} contractors")

        # ============================================================
        # 3) ADDITIONAL LABOR (40 more to reach 50 total)
        # ============================================================
        print("Seeding Additional Labor...")
        lbr_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM labor")).scalar()
        lbr_start = max(lbr_max + 1, 26)
        new_labor_ids = []
        for i in range(40):
            lbr_id = f"LBR-{str(lbr_start+i).zfill(4)}"
            new_labor_ids.append(lbr_id)
            is_employee = random.random() > 0.3
            name = LABORER_NAMES[i]
            conn.execute(text(
                "INSERT INTO labor (id, labor_type, labor_group, employee, contractor, "
                "laborer, location, labor_cost, created_at, updated_at) "
                "VALUES (:id,:ltype,:lg,:emp,:cntr,:laborer,:loc,:cost,:now,:now) "
                "ON CONFLICT (id) DO NOTHING"
            ), {
                "id": lbr_id,
                "ltype": "Employee" if is_employee else "Contractor",
                "lg": rc(lg_ids),
                "emp": rc(EMPLOYEES) if is_employee else None,
                "cntr": rc(contractor_ids) if not is_employee else None,
                "laborer": name,
                "loc": rc(LOCATIONS[:30]),
                "cost": round(random.uniform(300, 2500), 2),
                "now": NOW,
            })
        _update_series(conn, "LBR", lbr_start + 40)
        all_labor_ids = [r[0] for r in conn.execute(text("SELECT id FROM labor ORDER BY id")).fetchall()]
        print(f"  Created {len(new_labor_ids)} additional labor records (total: {len(all_labor_ids)})")

        # ============================================================
        # 4) LABOR AVAILABILITY (50) + Details
        # ============================================================
        print("Seeding Labor Availability...")
        la_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM labor_availability")).scalar()
        la_start = max(la_max + 1, 1)
        lad_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM labor_availability_details")).scalar()
        lad_counter = max(lad_max + 1, 1)
        la_ids = []

        for i in range(50):
            la_id = f"LBRAV-{str(la_start+i).zfill(5)}"
            la_ids.append(la_id)
            labor = rc(all_labor_ids)
            # Get laborer name
            laborer_name = conn.execute(text("SELECT laborer FROM labor WHERE id=:id"), {"id": labor}).scalar() or labor
            d = rand_date(60, 0)
            conn.execute(text(
                "INSERT INTO labor_availability (id, labor, laborer, date, created_at, updated_at) "
                "VALUES (:id,:labor,:laborer,:d,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": la_id, "labor": labor, "laborer": laborer_name, "d": d, "now": NOW})

            # Create hourly detail slots (8-12 hours per day)
            start_hour = random.choice([6, 7, 8])
            num_hours = random.randint(8, 12)
            for h in range(num_hours):
                lad_id = f"LBRAVD-{str(lad_counter).zfill(5)}"
                lad_counter += 1
                hour = f"{(start_hour + h) % 24:02d}:00"
                if h < num_hours - 1:
                    status = rc(["Available", "Available", "Available", "Reserved"])
                else:
                    status = "End Shift"
                reason = ""
                if status == "Reserved":
                    reason = rc(["Assigned to WO", "PM scheduled", "Emergency standby", "Training session"])
                conn.execute(text(
                    "INSERT INTO labor_availability_details (id, labor_availability, hour, status, reason, created_at, updated_at) "
                    "VALUES (:id,:la,:hour,:status,:reason,:now,:now) ON CONFLICT (id) DO NOTHING"
                ), {"id": lad_id, "la": la_id, "hour": hour, "status": status, "reason": reason, "now": NOW})

        _update_series(conn, "LBRAV", la_start + 50)
        _update_series(conn, "LBRAVD", lad_counter)
        print(f"  Created {len(la_ids)} labor availability records with hourly details")

        # ============================================================
        # 5) ADDITIONAL COST CODES (40 more to reach 50 total)
        # ============================================================
        print("Seeding Additional Cost Codes...")
        cc_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM cost_code")).scalar()
        cc_start = max(cc_max + 1, 26)
        cc_count = 0
        for i in range(40):
            cc_id = f"CC-{str(cc_start+i).zfill(4)}"
            cc_count += 1
            code, desc = COST_CODE_DATA[i]
            scope = rc(["Global", "Per Site"])
            site = rc(SITES) if scope == "Per Site" else None
            conn.execute(text(
                "INSERT INTO cost_code (id, code, description, scope, site, created_at, updated_at) "
                "VALUES (:id,:code,:desc,:scope,:site,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": cc_id, "code": code, "desc": desc, "scope": scope, "site": site, "now": NOW})
        _update_series(conn, "CC", cc_start + 40)
        print(f"  Created {cc_count} additional cost codes")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n=== SEEDING COMPLETE ===")
        for tbl in ["labor_group", "contractor", "labor", "labor_availability",
                     "labor_availability_details", "cost_code"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl:45s} {count:5d} records")


if __name__ == "__main__":
    seed()
