"""
SPMC EAM Sample Data Seeder
============================
Generates 50+ records for each major module in the EAM system:
- Service Requests
- Maintenance Activities
- Maintenance Plans (with Planned Maintenance Activities)
- Maintenance Orders (with Order Details)
- Checklists (with Details)
- Work Orders & Work Order Activities
- Maintenance Requests
- Incidents

All data is realistic for Southern Philippines Medical Center (SPMC),
a large government hospital in Davao City.
"""
import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text

DB_URL = "postgresql://eam_spmc_user:CwSpmcSec2026mR7@localhost:5432/eam-spmc"
engine = create_engine(DB_URL)
NOW = datetime.now()

# ---------- Reference data from existing DB ----------
ASSETS = [f"A-{str(i).zfill(5)}" for i in list(range(1, 75)) + [79, 80, 82]]
SITES = ["SITE-0001", "SITE-0002", "SITE-0003", "SITE-0004"]
LOCATIONS = [f"LOC-{str(i).zfill(4)}" for i in list(range(1, 60)) + [66, 67, 68]]
ASSET_CLASSES = [f"AC-{str(i).zfill(4)}" for i in range(1, 14)]
MANUFACTURERS = [f"MFR-{str(i).zfill(5)}" for i in range(1, 9)]
MODELS = [f"M-{str(i).zfill(5)}" for i in range(1, 9)]
DEPARTMENTS = [f"DEPT-{str(i).zfill(4)}" for i in list(range(1, 11)) + list(range(21, 36))]
EMPLOYEES = [f"EMP-{str(i).zfill(4)}" for i in list(range(1, 6)) + list(range(21, 36))]
ITEMS = [f"ITM-{str(i).zfill(4)}" for i in range(1, 11)]
COST_CODES = [f"CC-{str(i).zfill(4)}" for i in list(range(1, 6)) + list(range(21, 26))]
COF = [f"COF-{str(i).zfill(4)}" for i in [1,2,3,4,5,21,22,23,25]]
POSITIONS = [f"POS-{str(i).zfill(4)}" for i in [1,2,12,13,14,15,21,22,24,25]]
RAT = [f"RAT-{str(i).zfill(4)}" for i in range(1, 11)]
UOM = ["UOM-0001", "UOM-0002", "UOM-0003"]
WORK_ORDERS_EXISTING = ["WO-00021", "WO-00022", "WO-00023", "WO-00024", "WO-00025"]

# ---------- Helper functions ----------
def rand_date(start_days_ago=365, end_days_ago=0):
    d = date.today() - timedelta(days=random.randint(end_days_ago, start_days_ago))
    return d

def rand_datetime(start_days_ago=365, end_days_ago=0):
    d = datetime.now() - timedelta(
        days=random.randint(end_days_ago, start_days_ago),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    return d

def rc(lst):
    return random.choice(lst)

# ---------- SPMC-specific realistic data ----------

# Hospital-specific service request titles
SR_TITLES = [
    "CT Scanner malfunction - no image output",
    "MRI cooling system alert",
    "X-Ray generator flickering",
    "Ventilator alarm not triggering",
    "Infusion pump flow rate error",
    "Elevator stuck on 3rd floor",
    "HVAC unit not cooling OR-3",
    "Autoclave sterilization cycle incomplete",
    "Emergency generator failed load test",
    "UPS battery replacement needed - ICU",
    "Dialysis machine water leak",
    "Oxygen concentrator low output",
    "Patient monitor screen blank",
    "Defibrillator battery degraded",
    "Suction machine motor overheating",
    "Laboratory centrifuge vibration",
    "Blood bank refrigerator temperature alarm",
    "Pharmacy cold storage compressor noise",
    "Laundry dryer not heating",
    "Kitchen exhaust fan malfunction",
    "Fire alarm panel zone fault",
    "Nurse call system intermittent",
    "CCTV camera offline - ER entrance",
    "Water heater leaking - Ward 5",
    "Roof leak above Radiology",
    "Fluorescent light flickering - OPD",
    "Surgical light intensity dropping",
    "Anesthesia machine vaporizer leak",
    "ECG machine paper jam",
    "Nebulizer not producing mist",
    "Wheelchair brake failure",
    "Stretcher wheel bearing worn",
    "Ambulance AC not working",
    "Dental chair hydraulic failure",
    "Ophthalmoscope bulb replacement",
    "Ultrasound probe cable fraying",
    "Endoscope light source dim",
    "Pathology microscope focus drift",
    "Pharmacy dispensing machine error",
    "Pneumatic tube system jammed",
    "Intercom system static noise - Ward 7",
    "Backup power automatic transfer switch fault",
    "Boiler pressure gauge reading high",
    "Chiller plant vibration alarm",
    "Cooling tower fan belt slipping",
    "Medical gas manifold pressure drop",
    "Vacuum system pump overheating",
    "Waste treatment plant pH imbalance",
    "Solar panel inverter fault",
    "Parking barrier gate stuck",
    "Loading dock door motor failure",
    "Morgue refrigeration unit alarm",
    "Neonatal incubator temperature fluctuation",
    "Operating room air handling unit filter clogged",
    "Sterilization department steam trap leaking",
]

SR_DESCRIPTIONS = [
    "Equipment reported not functioning properly during morning rounds. Requesting immediate inspection.",
    "Intermittent fault detected during routine use. Staff reported unusual noise/behavior.",
    "Scheduled preventive maintenance overdue. Equipment showing early signs of degradation.",
    "Patient safety concern raised by nursing staff. Requires urgent assessment.",
    "Equipment failed self-diagnostic test. Vendor support may be required.",
    "Multiple complaints from department staff about performance issues.",
    "Environmental control out of specification. Affecting patient comfort and safety.",
    "Regulatory compliance inspection upcoming. Equipment must be certified operational.",
    "Critical infrastructure component showing wear. Preventive replacement recommended.",
    "Emergency backup system test failure. Must be restored before next scheduled test.",
]

MA_ACTIVITIES = [
    ("Preventive Maintenance - HVAC Filter Change", "Replace air handling unit filters, clean coils, check refrigerant levels"),
    ("Corrective Maintenance - Motor Replacement", "Replace faulty motor, align coupling, test amperage draw"),
    ("Predictive Maintenance - Vibration Analysis", "Perform vibration analysis on rotating equipment, document findings"),
    ("Preventive Maintenance - Electrical Panel Inspection", "Inspect breakers, tighten connections, thermal scan for hotspots"),
    ("Calibration - Patient Monitor", "Calibrate ECG, SpO2, NIBP, and temperature channels per manufacturer specs"),
    ("Preventive Maintenance - Generator Load Test", "Perform monthly load bank test, check fuel system, inspect coolant"),
    ("Corrective Maintenance - Plumbing Repair", "Repair/replace damaged piping, check for leaks, restore water supply"),
    ("Preventive Maintenance - Fire Safety Check", "Test fire alarm panel, inspect sprinklers, check extinguisher charges"),
    ("Preventive Maintenance - Elevator Inspection", "Inspect cables, brakes, door mechanisms, and safety interlocks"),
    ("Calibration - Laboratory Equipment", "Calibrate analytical balances, pipettes, and centrifuge RPM"),
    ("Preventive Maintenance - UPS Battery Check", "Test battery capacity, check connections, clean terminals"),
    ("Corrective Maintenance - Autoclave Repair", "Replace door gasket, calibrate pressure/temperature sensors"),
    ("Preventive Maintenance - Medical Gas System", "Inspect manifolds, check pressures, test alarm systems"),
    ("Preventive Maintenance - Boiler Inspection", "Check water treatment, inspect tubes, test safety valves"),
    ("Corrective Maintenance - Refrigeration Repair", "Diagnose and repair refrigeration system, recharge as needed"),
    ("Preventive Maintenance - Dental Equipment", "Clean and lubricate handpieces, check compressor, test suction"),
    ("Predictive Maintenance - Thermal Imaging", "Perform IR scan of electrical panels and mechanical equipment"),
    ("Preventive Maintenance - Water Treatment", "Test water quality, replace filters, check dosing pumps"),
    ("Corrective Maintenance - Door/Lock Repair", "Repair automatic doors, replace locks, adjust closers"),
    ("Preventive Maintenance - Surgical Light Check", "Clean reflectors, test intensity, check articulation joints"),
    ("Preventive Maintenance - Chiller Maintenance", "Clean condenser, check oil, inspect compressor valves"),
    ("Calibration - Infusion Pump", "Verify flow rate accuracy across all channels per IEC 60601"),
    ("Preventive Maintenance - Roof Maintenance", "Inspect membrane integrity, clean drains, seal penetrations"),
    ("Corrective Maintenance - Electrical Wiring", "Repair damaged wiring, replace outlets, test circuits"),
    ("Preventive Maintenance - Ventilator Check", "Test all modes, calibrate O2 sensor, replace circuits"),
    ("Preventive Maintenance - Imaging Equipment", "Clean detectors, calibrate, perform quality assurance tests"),
    ("Corrective Maintenance - Pneumatic System", "Clear blockages, replace diaphragms, test station delivery"),
    ("Preventive Maintenance - Kitchen Equipment", "Clean grease traps, inspect gas lines, test hood suppression"),
    ("Preventive Maintenance - Laundry Equipment", "Inspect bearings, clean lint systems, check water valves"),
    ("Calibration - Sterilizer Validation", "Perform biological indicator testing, Bowie-Dick test, leak test"),
    ("Preventive Maintenance - CCTV System", "Clean cameras, check recording, test motion detection"),
    ("Corrective Maintenance - Nurse Call System", "Replace faulty call stations, test all zones, update firmware"),
    ("Preventive Maintenance - Waste Management", "Inspect autoclaves, check shredder blades, test treatment cycle"),
    ("Preventive Maintenance - Solar Panel Cleaning", "Clean panels, inspect wiring, check inverter performance"),
    ("Corrective Maintenance - Stretcher Repair", "Replace wheels, fix brakes, check side rails and mattress"),
    ("Preventive Maintenance - Oxygen Plant", "Check compressor, replace desiccant, test purity output"),
    ("Predictive Maintenance - Oil Analysis", "Sample and analyze lubricant from critical rotating equipment"),
    ("Preventive Maintenance - Emergency Lighting", "Test battery backup, replace bulbs, verify exit signage"),
    ("Corrective Maintenance - CT Scanner Tube", "Replace X-ray tube, calibrate, perform phantom scan QA"),
    ("Preventive Maintenance - Access Control System", "Test card readers, check door locks, update access lists"),
    ("Preventive Maintenance - BMS System Check", "Verify sensor readings, test alarms, update setpoints"),
    ("Calibration - Blood Gas Analyzer", "Run calibration gases, verify QC materials, clean electrodes"),
    ("Preventive Maintenance - Wheelchair Fleet", "Inspect frames, test brakes, check upholstery, clean"),
    ("Corrective Maintenance - Parking System", "Repair barrier gates, fix ticket dispensers, test payment"),
    ("Preventive Maintenance - Communication System", "Test intercom, check PA system, verify paging coverage"),
    ("Corrective Maintenance - Window/Glass Repair", "Replace broken panes, reseal frames, check safety glazing"),
    ("Preventive Maintenance - Pest Control Equipment", "Inspect bait stations, service UV traps, check records"),
    ("Preventive Maintenance - Paint and Wall Repair", "Touch up walls, repair damaged surfaces in patient areas"),
    ("Calibration - Radiation Monitoring", "Calibrate dosimeters, test area monitors, verify shielding"),
    ("Preventive Maintenance - Ambulance Check", "Inspect medical equipment, test communications, check AC"),
]

MAINT_PLAN_DESCRIPTIONS = [
    "HVAC System Preventive Maintenance Plan",
    "Critical Medical Equipment Maintenance Program",
    "Electrical Infrastructure Maintenance Plan",
    "Plumbing and Water System Maintenance",
    "Fire Safety and Life Safety Maintenance",
    "Elevator and Vertical Transport Maintenance",
    "Laboratory Equipment Calibration Program",
    "Emergency Power System Maintenance",
    "Medical Gas Distribution Maintenance",
    "Boiler and Steam System Maintenance",
    "Refrigeration and Cold Chain Maintenance",
    "Building Envelope Maintenance Plan",
    "Surgical Suite Equipment Maintenance",
    "Imaging Equipment PM Program",
    "ICU/CCU Critical Equipment Maintenance",
    "Sterilization Equipment Maintenance",
    "Kitchen and Food Service Equipment",
    "Laundry Equipment Maintenance Plan",
    "Communication Systems Maintenance",
    "Security and Access Control Maintenance",
    "Dental Clinic Equipment Maintenance",
    "Ophthalmology Equipment Maintenance",
    "Physical Therapy Equipment Maintenance",
    "Neonatal Equipment Maintenance Program",
    "OR Equipment Preventive Maintenance",
    "ER Equipment Ready-State Maintenance",
    "Dialysis Equipment Maintenance Program",
    "Pathology Lab Equipment Maintenance",
    "Pharmacy Equipment Maintenance Plan",
    "Radiology QA and PM Program",
    "Respiratory Therapy Equipment PM",
    "Outpatient Clinic Equipment Maintenance",
    "Ward Equipment Maintenance Schedule",
    "Transport Equipment Maintenance",
    "Waste Management Equipment Maintenance",
    "Water Treatment System Maintenance",
    "Solar Energy System Maintenance",
    "BMS and Automation Maintenance",
    "Parking and Grounds Equipment PM",
    "Utility Metering and Monitoring PM",
    "Paint and Interior Maintenance Schedule",
    "Pest Control Equipment Maintenance",
    "Nurse Call and Patient Safety Systems PM",
    "Pneumatic Tube System Maintenance",
    "Patient Bed and Furniture Maintenance",
    "Autoclave and Decontamination PM",
    "Oxygen Generation Plant Maintenance",
    "Chiller Plant Maintenance Program",
    "Cooling Tower Maintenance Schedule",
    "Emergency Vehicle Maintenance Program",
]

CHECKLIST_NAMES = [
    "HVAC Pre-Start Checklist",
    "Generator Monthly Inspection",
    "Elevator Safety Inspection",
    "Fire Extinguisher Monthly Check",
    "Medical Gas System Daily Check",
    "Autoclave Daily Validation",
    "Patient Monitor Function Test",
    "Ventilator Pre-Use Checklist",
    "Defibrillator Daily Check",
    "Surgical Light Pre-Op Check",
    "CT Scanner Daily QA",
    "MRI Safety Checklist",
    "X-Ray Room Safety Check",
    "Ultrasound Probe Inspection",
    "Infusion Pump Pre-Use Check",
    "Laboratory Equipment Daily QA",
    "Blood Bank Refrigerator Log",
    "Pharmacy Cold Storage Check",
    "Oxygen Concentrator Check",
    "Suction Machine Pre-Use Test",
    "Ambulance Equipment Readiness",
    "Crash Cart Daily Inspection",
    "Anesthesia Machine Pre-Use",
    "Endoscope Reprocessing Check",
    "Dialysis Machine Pre-Treatment",
    "Dental Unit Daily Flush",
    "Sterilizer Load Release Checklist",
    "Boiler Daily Inspection",
    "Chiller Plant Operator Log",
    "UPS System Daily Check",
    "Water Treatment Daily Log",
    "Cooling Tower Weekly Check",
    "Electrical Panel Monthly Scan",
    "BMS Alarm Verification",
    "CCTV System Weekly Test",
    "Nurse Call System Test",
    "Emergency Lighting Monthly Test",
    "Waste Treatment Daily Operations",
    "Kitchen Equipment Pre-Service",
    "Laundry Equipment Start-Up",
    "Solar Inverter Daily Check",
    "Parking System Daily Check",
    "Fire Alarm Panel Weekly Test",
    "Medical Air Compressor Check",
    "Vacuum System Daily Check",
    "Pneumatic Tube Daily Test",
    "Access Control Weekly Audit",
    "Pest Control Station Check",
    "Wheelchair Safety Inspection",
    "Stretcher Pre-Use Inspection",
]

CHECKLIST_ITEMS_MAP = {
    "default": [
        "Visual inspection completed",
        "Equipment cleaned and free of debris",
        "All safety guards in place",
        "Emergency stop functional",
        "Operating parameters within spec",
        "Electrical connections secure",
        "No unusual noise or vibration",
        "Lubrication levels adequate",
        "Documentation updated",
        "Operator notified of status",
    ]
}

WO_DESCRIPTIONS = [
    "Scheduled preventive maintenance per hospital PM program",
    "Corrective work order for reported equipment failure",
    "Emergency repair - patient safety impact",
    "Seasonal HVAC maintenance for comfort compliance",
    "Annual calibration and certification work",
    "Infrastructure upgrade per capital improvement plan",
    "Regulatory compliance corrective action",
    "Energy efficiency improvement project",
    "Breakdown repair - critical infrastructure",
    "Planned replacement of end-of-life equipment",
]

WO_TYPES = ["Preventive", "Corrective", "Emergency", "Project"]
PRIORITIES = ["Low", "Medium", "High", "Emergency"]
SEVERITIES = ["Minor", "Moderate", "Major", "Critical"]
SR_STATUSES = ["Draft", "Submitted", "In Progress", "Closed"]
MR_STATES = ["Draft", "Submitted", "Approved", "Release", "In Progress", "Completed"]
WO_STATES = ["Draft", "Submitted", "Approved", "Release", "In Progress", "Completed"]
WOA_STATES = ["Draft", "Submitted", "Approved", "Release", "in_progress", "completed"]
SCHEDULE_TYPES = ["Calendar Based", "Interval Based", "Condition Based"]
FREQUENCIES = ["Daily", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Semi-Annually", "Annually"]
CHECKLIST_TYPES = ["Pre-Use", "Inspection", "Maintenance", "Safety", "Calibration"]


def seed():
    with engine.begin() as conn:
        # ==============================
        # 1) MAINTENANCE ACTIVITIES (50)
        # ==============================
        print("Seeding Maintenance Activities...")
        existing_ma = conn.execute(text("SELECT COUNT(*) FROM maintenance_activity")).scalar()
        ma_start = existing_ma + 1
        ma_ids = []
        for i in range(50):
            idx = i
            ma_id = f"MTACT-{str(ma_start + i).zfill(5)}"
            ma_ids.append(ma_id)
            name, desc = MA_ACTIVITIES[idx % len(MA_ACTIVITIES)]
            conn.execute(text("""
                INSERT INTO maintenance_activity (id, activity_name, description, created_at, updated_at)
                VALUES (:id, :name, :desc, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {"id": ma_id, "name": name, "desc": desc, "now": NOW})

        # Update series
        new_ma_val = ma_start + 50
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTACT', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": new_ma_val})
        print(f"  Created {len(ma_ids)} maintenance activities")

        # ==============================
        # 2) CHECKLISTS with Details (50)
        # ==============================
        print("Seeding Checklists...")
        existing_cl = conn.execute(text("SELECT COUNT(*) FROM checklist")).scalar()
        cl_start = existing_cl + 1
        cl_ids = []
        cld_counter = conn.execute(text("SELECT COUNT(*) FROM checklist_details")).scalar() + 1

        for i in range(50):
            cl_id = f"CHL-{str(cl_start + i).zfill(5)}"
            cl_ids.append(cl_id)
            conn.execute(text("""
                INSERT INTO checklist (id, checklist_name, checklist_type, created_at, updated_at)
                VALUES (:id, :name, :ctype, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": cl_id,
                "name": CHECKLIST_NAMES[i % len(CHECKLIST_NAMES)],
                "ctype": rc(CHECKLIST_TYPES),
                "now": NOW,
            })

            # Add 5-8 checklist detail items
            items = random.sample(CHECKLIST_ITEMS_MAP["default"], min(random.randint(5, 8), len(CHECKLIST_ITEMS_MAP["default"])))
            for item_name in items:
                cld_id = f"CHLD-{str(cld_counter).zfill(5)}"
                cld_counter += 1
                conn.execute(text("""
                    INSERT INTO checklist_details (id, checklist, item_name, is_mandatory, created_at, updated_at)
                    VALUES (:id, :cl, :name, :mand, :now, :now)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": cld_id, "cl": cl_id, "name": item_name,
                    "mand": random.random() > 0.3, "now": NOW,
                })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('CHL', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": cl_start + 50})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('CHLD', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": cld_counter})
        print(f"  Created {len(cl_ids)} checklists with details")

        # ==============================
        # 3) INCIDENTS (50)
        # ==============================
        print("Seeding Incidents...")
        existing_inc = conn.execute(text("SELECT COUNT(*) FROM incident")).scalar()
        inc_start = existing_inc + 1
        inc_ids = []
        incident_titles = [
            "Electrical short circuit in Ward 3",
            "Water pipe burst in basement",
            "Elevator entrapment - Building A",
            "Chemical spill in laboratory",
            "Medical gas alarm triggered",
            "Power outage affecting OR wing",
            "HVAC smoke detected in duct",
            "Patient slip and fall - wet floor near ER",
            "Fire alarm activated - kitchen area",
            "Generator fuel leak detected",
            "Steam line rupture in laundry",
            "Refrigerant leak in pharmacy cold room",
            "CT scanner overheating shutdown",
            "UPS failure during brownout",
            "Flooding in lower ground floor",
            "Broken window - pediatric ward",
            "Autoclave door seal failure",
            "Oxygen manifold pressure drop",
            "Emergency exit door jammed",
            "Lightning strike damage to solar array",
            "Sewage backup in restroom",
            "Pest infestation reported - kitchen store",
            "Ceiling tile collapse - OPD hallway",
            "Electrical panel arc flash event",
            "Medical waste treatment system failure",
            "Boiler safety valve discharge",
            "Parking lot sinkhole formation",
            "Security camera tampering detected",
            "Nurse call system complete failure",
            "MRI quench event",
            "Surgical light dropped during procedure",
            "Ambulance breakdown during transport",
            "Water treatment chlorine overdose alarm",
            "Building structural crack observed",
            "Elevator cable wear detected during inspection",
            "Gas pipeline corrosion found",
            "Rooftop equipment blown off during typhoon",
            "Dialysis water contamination alert",
            "Pharmacy compounding hood failure",
            "Neonatal incubator alarm malfunction",
            "OR air pressure differential loss",
            "Blood bank power interruption",
            "Patient monitor false arrest alarm",
            "Ventilator software crash during use",
            "Endoscope reprocessor chemical leak",
            "Radiology shielding integrity concern",
            "Dental x-ray exposure control fault",
            "Lab analyzer reagent spill",
            "Pneumatic tube carrier stuck in line",
            "Emergency shower and eyewash failure",
        ]
        incident_types = ["Safety", "Equipment Failure", "Environmental", "Infrastructure", "Utility"]

        for i in range(50):
            inc_id = f"INC-{str(inc_start + i).zfill(5)}"
            inc_ids.append(inc_id)
            dt = rand_datetime(365, 0)
            conn.execute(text("""
                INSERT INTO incident (id, title, description, incident_type, incident_datetime,
                    date_reported, location, asset, reported_by, site, department, severity,
                    immediate_action_taken, preventive_actions, created_at, updated_at)
                VALUES (:id, :title, :desc, :itype, :idt, :dr, :loc, :asset, :rb, :site,
                    :dept, :sev, :iat, :pa, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": inc_id,
                "title": incident_titles[i],
                "desc": f"Incident reported at SPMC. {incident_titles[i]}. Immediate response initiated by on-duty staff.",
                "itype": rc(incident_types),
                "idt": dt,
                "dr": dt.date(),
                "loc": rc(LOCATIONS),
                "asset": rc(ASSETS),
                "rb": rc(EMPLOYEES),
                "site": rc(SITES),
                "dept": rc(DEPARTMENTS),
                "sev": rc(SEVERITIES),
                "iat": "Area secured and affected personnel evacuated. Incident reported to safety officer.",
                "pa": "Root cause analysis to be conducted. Corrective measures to be identified.",
                "now": NOW,
            })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('INC', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": inc_start + 50})
        print(f"  Created {len(inc_ids)} incidents")

        # ==============================
        # 4) SERVICE REQUESTS (55)
        # ==============================
        print("Seeding Service Requests...")
        existing_sr = conn.execute(text("SELECT COUNT(*) FROM service_request")).scalar()
        sr_start = existing_sr + 1
        sr_ids = []

        for i in range(55):
            sr_id = f"SRQ-{str(sr_start + i).zfill(5)}"
            sr_ids.append(sr_id)
            status = rc(SR_STATUSES)
            dr = rand_date(300, 5)
            cd = dr + timedelta(days=random.randint(1, 30)) if status == "Closed" else None
            conn.execute(text("""
                INSERT INTO service_request (id, title, description, status, priority,
                    date_reported, closed_date, asset, site, location, incident, created_at, updated_at)
                VALUES (:id, :title, :desc, :status, :priority, :dr, :cd, :asset, :site,
                    :loc, :inc, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": sr_id,
                "title": SR_TITLES[i % len(SR_TITLES)],
                "desc": rc(SR_DESCRIPTIONS),
                "status": status,
                "priority": rc(PRIORITIES),
                "dr": dr,
                "cd": cd,
                "asset": rc(ASSETS),
                "site": rc(SITES),
                "loc": rc(LOCATIONS),
                "inc": rc(inc_ids) if random.random() > 0.7 else None,
                "now": NOW,
            })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('SRQ', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": sr_start + 55})
        print(f"  Created {len(sr_ids)} service requests")

        # ==============================
        # 5) MAINTENANCE PLANS (50) with Planned Maintenance Activities
        # ==============================
        print("Seeding Maintenance Plans...")
        existing_mp = conn.execute(text("SELECT COUNT(*) FROM maintenance_plan")).scalar()
        mp_start = existing_mp + 1
        mp_ids = []
        pma_counter = conn.execute(text("SELECT COUNT(*) FROM planned_maintenance_activity")).scalar() + 1
        mc_counter = conn.execute(text("SELECT COUNT(*) FROM maintenance_calendar")).scalar() + 1
        mi_counter = conn.execute(text("SELECT COUNT(*) FROM maintenance_interval")).scalar() + 1

        for i in range(50):
            mp_id = f"MTPLAN-{str(mp_start + i).zfill(5)}"
            mp_ids.append(mp_id)
            ac = rc(ASSET_CLASSES)
            mfr = rc(MANUFACTURERS)
            mdl = rc(MODELS)
            conn.execute(text("""
                INSERT INTO maintenance_plan (id, description, asset_class, manufacturer,
                    model, created_at, updated_at)
                VALUES (:id, :desc, :ac, :mfr, :mdl, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": mp_id,
                "desc": MAINT_PLAN_DESCRIPTIONS[i % len(MAINT_PLAN_DESCRIPTIONS)],
                "ac": ac, "mfr": mfr, "mdl": mdl, "now": NOW,
            })

            # 2-4 Planned Maintenance Activities per plan
            num_pma = random.randint(2, 4)
            selected_ma = random.sample(ma_ids, min(num_pma, len(ma_ids)))
            for ma_id in selected_ma:
                pma_id = f"PMA-{str(pma_counter).zfill(5)}"
                pma_counter += 1
                sched = rc(SCHEDULE_TYPES)
                cl_id = rc(cl_ids) if random.random() > 0.3 else None
                conn.execute(text("""
                    INSERT INTO planned_maintenance_activity (id, maintenance_plan,
                        maintenance_activity, checklist, maintenance_schedule,
                        maintenance_type, created_at, updated_at)
                    VALUES (:id, :mp, :ma, :cl, :sched, :mtype, :now, :now)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": pma_id, "mp": mp_id, "ma": ma_id,
                    "cl": cl_id, "sched": sched, "mtype": rc(RAT), "now": NOW,
                })

                # Add schedule detail based on type
                if sched == "Calendar Based":
                    mcal_id = f"MCAL-{str(mc_counter).zfill(5)}"
                    mc_counter += 1
                    conn.execute(text("""
                        INSERT INTO maintenance_calendar (id, planned_maintenance_activity,
                            maintenance_plan, maintenance_activity, frequency,
                            lead_calendar_days, created_at, updated_at)
                        VALUES (:id, :pma, :mp, :ma, :freq, :lead, :now, :now)
                        ON CONFLICT (id) DO NOTHING
                    """), {
                        "id": mcal_id, "pma": pma_id, "mp": mp_id, "ma": ma_id,
                        "freq": rc(FREQUENCIES), "lead": random.randint(1, 14), "now": NOW,
                    })
                elif sched == "Interval Based":
                    mint_id = f"MINT-{str(mi_counter).zfill(5)}"
                    mi_counter += 1
                    conn.execute(text("""
                        INSERT INTO maintenance_interval (id, planned_maintenance_activity,
                            maintenance_plan, maintenance_activity, lead_interval,
                            interval, interval_unit_of_measure, created_at, updated_at)
                        VALUES (:id, :pma, :mp, :ma, :lead, :intv, :uom, :now, :now)
                        ON CONFLICT (id) DO NOTHING
                    """), {
                        "id": mint_id, "pma": pma_id, "mp": mp_id, "ma": ma_id,
                        "lead": round(random.uniform(10, 100), 1),
                        "intv": round(random.uniform(500, 5000), 0),
                        "uom": rc(UOM), "now": NOW,
                    })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTPLAN', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mp_start + 50})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('PMA', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": pma_counter})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MCAL', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mc_counter})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MINT', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mi_counter})
        print(f"  Created {len(mp_ids)} maintenance plans with planned activities")

        # ==============================
        # 6) WORK ORDERS (55) with Work Order Activities
        # ==============================
        print("Seeding Work Orders and Activities...")
        existing_wo = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)), 0) FROM work_order")).scalar()
        wo_start = max(existing_wo + 1, 36)
        wo_ids = []
        woa_counter_result = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)), 0) FROM work_order_activity")).scalar()
        woa_counter = max(woa_counter_result + 1, 36)

        for i in range(55):
            wo_id = f"WO-{str(wo_start + i).zfill(5)}"
            wo_ids.append(wo_id)
            wo_state = rc(WO_STATES)
            dd = rand_date(180, 0)
            conn.execute(text("""
                INSERT INTO work_order (id, workflow_state, work_order_type, description,
                    category_of_failure, due_date, priority, severity, site, department,
                    cost_code, created_at, updated_at)
                VALUES (:id, :ws, :wot, :desc, :cof, :dd, :pri, :sev, :site, :dept,
                    :cc, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": wo_id, "ws": wo_state, "wot": rc(WO_TYPES),
                "desc": rc(WO_DESCRIPTIONS), "cof": rc(COF),
                "dd": dd, "pri": rc(PRIORITIES), "sev": rc(SEVERITIES),
                "site": rc(SITES), "dept": rc(DEPARTMENTS), "cc": rc(COST_CODES),
                "now": NOW,
            })

            # 1-3 work order activities per WO
            num_woa = random.randint(1, 3)
            for j in range(num_woa):
                woa_id = f"WOA-{str(woa_counter).zfill(5)}"
                woa_counter += 1
                asset = rc(ASSETS)
                sd = rand_datetime(180, 30)
                ed = sd + timedelta(hours=random.randint(1, 48))
                conn.execute(text("""
                    INSERT INTO work_order_activity (id, workflow_state, work_order,
                        description, work_item_type, work_item, activity_type,
                        position, assigned_to, location, site, department,
                        start_date, end_date, created_at, updated_at)
                    VALUES (:id, :ws, :wo, :desc, :wit, :wi, :at, :pos, :assigned,
                        :loc, :site, :dept, :sd, :ed, :now, :now)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": woa_id, "ws": rc(WOA_STATES), "wo": wo_id,
                    "desc": rc(MA_ACTIVITIES)[0][:255],
                    "wit": "Asset", "wi": asset,
                    "at": rc(RAT), "pos": rc(POSITIONS),
                    "assigned": rc(EMPLOYEES),
                    "loc": rc(LOCATIONS), "site": rc(SITES), "dept": rc(DEPARTMENTS),
                    "sd": sd, "ed": ed, "now": NOW,
                })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('WO', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": wo_start + 55})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('WOA', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": woa_counter})
        print(f"  Created {len(wo_ids)} work orders with activities")

        # ==============================
        # 7) MAINTENANCE ORDERS (50) with Details
        # ==============================
        print("Seeding Maintenance Orders...")
        existing_mo = conn.execute(text("SELECT COUNT(*) FROM maintenance_order")).scalar()
        mo_start = existing_mo + 1
        mo_ids = []
        mod_counter = conn.execute(text("SELECT COUNT(*) FROM maintenance_order_detail")).scalar() + 1

        # Get maintenance request IDs for linking
        mr_ids_result = conn.execute(text("SELECT id FROM maintenance_request")).fetchall()
        mr_ids = [r[0] for r in mr_ids_result]

        for i in range(50):
            mo_id = f"MTORD-{str(mo_start + i).zfill(5)}"
            mo_ids.append(mo_id)
            cd = rand_date(180, 0)
            wo_link = rc(wo_ids) if random.random() > 0.3 else None
            conn.execute(text("""
                INSERT INTO maintenance_order (id, created_date, work_order, created_at, updated_at)
                VALUES (:id, :cd, :wo, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {"id": mo_id, "cd": cd, "wo": wo_link, "now": NOW})

            # 1-4 order details per maintenance order
            num_details = random.randint(1, 4)
            for j in range(num_details):
                mod_id = f"MTORDD-{str(mod_counter).zfill(5)}"
                mod_counter += 1
                conn.execute(text("""
                    INSERT INTO maintenance_order_detail (id, maintenance_order, seq_num,
                        maint_req, asset, due_date, resource_availability_status,
                        created_at, updated_at)
                    VALUES (:id, :mo, :seq, :mr, :asset, :dd, :ras, :now, :now)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": mod_id, "mo": mo_id, "seq": j + 1,
                    "mr": rc(mr_ids) if mr_ids and random.random() > 0.5 else None,
                    "asset": rc(ASSETS),
                    "dd": str(rand_date(90, 0)),
                    "ras": rc(["Available", "Partially Available", "Not Available", "Pending Check"]),
                    "now": NOW,
                })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTORD', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mo_start + 50})
        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTORDD', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mod_counter})
        print(f"  Created {len(mo_ids)} maintenance orders with details")

        # ==============================
        # 8) MAINTENANCE REQUESTS (50)
        # ==============================
        print("Seeding Maintenance Requests...")
        existing_mr = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)), 0) FROM maintenance_request")).scalar()
        mr_start = max(existing_mr + 1, 36)
        new_mr_ids = []

        mr_descriptions = [
            "Scheduled PM due per maintenance calendar for this asset",
            "Condition-based trigger: sensor reading exceeded threshold",
            "Interval-based maintenance due per running hours counter",
            "Breakdown reported - corrective maintenance required",
            "Inspection findings require follow-up maintenance",
            "Annual compliance maintenance per regulatory requirement",
            "Operator reported abnormal performance during routine use",
            "Post-incident maintenance and safety verification",
            "Manufacturer recommended service interval reached",
            "Warranty claim maintenance - vendor coordination required",
        ]

        for i in range(50):
            mr_id = f"MTREQ-{str(mr_start + i).zfill(5)}"
            new_mr_ids.append(mr_id)
            rd = rand_date(300, 5)
            state = rc(MR_STATES)
            cd = rd + timedelta(days=random.randint(5, 60)) if state == "Completed" else None
            conn.execute(text("""
                INSERT INTO maintenance_request (id, workflow_state, requestor,
                    requested_date, description, priority, asset, request_type,
                    location, site, department, due_date, closed_date,
                    created_at, updated_at)
                VALUES (:id, :ws, :req, :rd, :desc, :pri, :asset, :rt, :loc,
                    :site, :dept, :dd, :cd, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": mr_id, "ws": state, "req": rc(EMPLOYEES),
                "rd": rd, "desc": rc(mr_descriptions),
                "pri": rc(PRIORITIES), "asset": rc(ASSETS),
                "rt": rc(RAT), "loc": rc(LOCATIONS), "site": rc(SITES),
                "dept": rc(DEPARTMENTS),
                "dd": rd + timedelta(days=random.randint(7, 30)),
                "cd": cd, "now": NOW,
            })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTREQ', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mr_start + 50})
        print(f"  Created {len(new_mr_ids)} maintenance requests")

        # ==============================
        # 9) MAINTENANCE PARTS for activities (link items to activities)
        # ==============================
        print("Seeding Maintenance Parts...")
        mp_counter = conn.execute(text("SELECT COUNT(*) FROM maintenance_parts")).scalar() + 1
        parts_count = 0
        for ma_id in ma_ids[:30]:  # First 30 activities get parts
            num_parts = random.randint(1, 3)
            for _ in range(num_parts):
                mp_id = f"MTPRT-{str(mp_counter).zfill(5)}"
                mp_counter += 1
                parts_count += 1
                conn.execute(text("""
                    INSERT INTO maintenance_parts (id, maintenance_activity, item, quantity, created_at, updated_at)
                    VALUES (:id, :ma, :item, :qty, :now, :now)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": mp_id, "ma": ma_id, "item": rc(ITEMS),
                    "qty": random.randint(1, 10), "now": NOW,
                })

        conn.execute(text("""
            INSERT INTO series (name, current) VALUES ('MTPRT', :val)
            ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)
        """), {"val": mp_counter})
        print(f"  Created {parts_count} maintenance parts")

        # ==============================
        # Summary
        # ==============================
        print("\n=== SEEDING COMPLETE ===")
        for tbl in ["service_request", "maintenance_activity", "maintenance_plan",
                     "planned_maintenance_activity", "maintenance_order",
                     "maintenance_order_detail", "maintenance_request",
                     "checklist", "checklist_details", "incident",
                     "work_order", "work_order_activity", "maintenance_parts",
                     "maintenance_calendar", "maintenance_interval"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl:45s} {count:5d} records")


if __name__ == "__main__":
    seed()
