"""
Seed script for SPMC EAM – Maintenance Management module.
Covers: equipment, maintenance_activity, maintenance_trade, maintenance_parts,
maintenance_equipment, service_request, maintenance_request, maintenance_plan,
planned_maintenance_activity, maintenance_calendar, maintenance_interval,
sensor, sensor_data, maintenance_condition, maintenance_order,
maintenance_order_detail, checklist (+more), checklist_details (+more)
"""
import random
from datetime import date, datetime, timedelta
from sqlalchemy import text, create_engine

DB_URL = "postgresql://eam_spmc_user:CwSpmcSec2026mR7@localhost:5432/eam-spmc"
engine = create_engine(DB_URL)

now = datetime.utcnow()

def ts():
    return now

def rand_date(start_days_ago=180, end_days_ago=1):
    d = date.today() - timedelta(days=random.randint(end_days_ago, start_days_ago))
    return d

def rand_dt(start_days_ago=180, end_days_ago=1):
    return datetime.combine(rand_date(start_days_ago, end_days_ago),
                            datetime.min.time()) + timedelta(hours=random.randint(6, 18), minutes=random.randint(0, 59))

# ── Reference data (hardcoded known IDs) ─────────────────────────────────────
SITES = ["SITE-0001", "SITE-0002", "SITE-0003", "SITE-0004"]
DEPTS = [f"DEPT-{i:04d}" for i in range(1, 19)] + [f"DEPT-{i:04d}" for i in range(34, 39)]
EMPLOYEES = [f"EMP-{i:04d}" for i in [1, 2, 3, 4, 5, 21, 22, 23, 24, 25]]
WORK_ORDERS = ["WO-00021", "WO-00022", "WO-00023", "WO-00024", "WO-00025"]
WOA = ["WOA-00021", "WOA-00022", "WOA-00023", "WOA-00024", "WOA-00025"]
MANUFACTURERS = [f"MFR-{i:05d}" for i in range(1, 9)]
MODELS = [f"M-{i:05d}" for i in range(1, 9)]
ASSET_CLASSES = [f"AC-{i:04d}" for i in range(1, 14)]
REQ_ACT_TYPES = [f"RAT-{i:04d}" for i in range(1, 21)]
PROPERTIES = ["PROP-0001", "PROP-0002", "PROP-0003"]
PRIORITIES = ["Low", "Medium", "High", "Emergency"]

# Series state
SERIES = {}

def load_series(conn):
    rows = conn.execute(text("SELECT name, current FROM series")).fetchall()
    for r in rows:
        SERIES[r[0]] = r[1]

def next_id(prefix, width=5):
    cur = SERIES.get(prefix, 0) + 1
    SERIES[prefix] = cur
    return f"{prefix}-{cur:0{width}d}"

def update_series(conn):
    for prefix, cur in SERIES.items():
        conn.execute(text(
            "INSERT INTO series (name, current) VALUES (:n, :c) "
            "ON CONFLICT (name) DO UPDATE SET current = :c"),
            {"n": prefix, "c": cur})

# ── Hospital maintenance activities ──────────────────────────────────────────
ACTIVITY_NAMES = [
    ("Preventive Maintenance Inspection", "Routine inspection of equipment per manufacturer guidelines"),
    ("HVAC Filter Replacement", "Replace air handling unit filters per schedule"),
    ("Generator Load Test", "Monthly load bank test on diesel generators"),
    ("Elevator Safety Inspection", "Annual safety inspection of elevator systems"),
    ("Fire Alarm System Test", "Quarterly fire detection and alarm system testing"),
    ("Medical Gas System Check", "Inspect medical gas outlets and pipeline integrity"),
    ("Boiler Inspection", "Periodic boiler tube and safety valve inspection"),
    ("UPS Battery Test", "Test UPS battery bank capacity and runtime"),
    ("Water Quality Testing", "Test potable and process water quality"),
    ("Sterilizer Validation", "Validate autoclave sterilization cycles"),
    ("Chiller Performance Check", "Check chiller COP and refrigerant levels"),
    ("Electrical Panel Thermography", "Infrared scan of electrical distribution panels"),
    ("Plumbing System Flush", "Flush water lines to prevent legionella"),
    ("Emergency Light Test", "Test emergency lighting battery backup"),
    ("X-Ray Quality Assurance", "QA testing of diagnostic X-ray equipment"),
    ("CT Scanner Calibration", "Calibrate CT scanner for image quality"),
    ("Ventilator Function Test", "Test mechanical ventilator alarm and delivery systems"),
    ("Patient Monitor Calibration", "Calibrate patient monitoring devices"),
    ("Defibrillator Check", "Inspect and test defibrillator units"),
    ("Anesthesia Machine Checkout", "Daily checkout of anesthesia delivery systems"),
    ("Dialysis Machine Disinfection", "Chemical disinfection of dialysis machines"),
    ("Nurse Call System Test", "Test nurse call and code blue systems"),
    ("Roof Inspection", "Inspect roofing for leaks and damage"),
    ("Paint Touch-Up", "Touch up paint in high-traffic clinical areas"),
    ("Parking Lot Maintenance", "Repair and stripe parking lot surfaces"),
    ("Landscaping Maintenance", "Grounds keeping and landscaping"),
    ("Pest Control Treatment", "Scheduled pest control and fumigation"),
    ("Window Cleaning", "External window cleaning schedule"),
    ("CCTV System Check", "Inspect and test security camera systems"),
    ("Access Control Maintenance", "Maintain door access control hardware"),
    ("Pneumatic Tube Check", "Inspect pneumatic tube transport system"),
    ("Mattress Inspection", "Inspect and sanitize patient mattresses"),
    ("Wheelchair Maintenance", "Inspect and repair wheelchairs"),
    ("Stretcher Maintenance", "Inspect and maintain patient stretchers"),
    ("OR Table Maintenance", "Preventive maintenance on operating tables"),
    ("Surgical Light Maintenance", "Clean and adjust OR surgical lights"),
    ("Laundry Equipment Maintenance", "Service industrial laundry machines"),
    ("Kitchen Equipment Service", "Inspect and service dietary equipment"),
    ("Pharmacy Fridge Calibration", "Calibrate pharmacy refrigerator temps"),
    ("Blood Bank Fridge Check", "Inspect blood bank refrigeration units"),
    ("Mortuary Cooler Service", "Service mortuary cooling units"),
    ("Solar Panel Cleaning", "Clean solar panel array for optimal output"),
    ("Waste Compactor Service", "Service medical waste compactor"),
    ("Air Quality Monitoring", "Monitor and test indoor air quality"),
    ("Vibration Analysis", "Vibration analysis on rotating equipment"),
    ("Ultrasonic Testing", "Ultrasonic thickness testing on piping"),
]

EQUIPMENT_NAMES = [
    ("Portable Welding Machine", "Welding"),
    ("Hydraulic Lift Jack", "Lifting"),
    ("Digital Multimeter", "Testing"),
    ("Infrared Thermometer", "Testing"),
    ("Thermal Imaging Camera", "Testing"),
    ("Pipe Threading Machine", "Plumbing"),
    ("Conduit Bender", "Electrical"),
    ("Refrigerant Recovery Unit", "HVAC"),
    ("Vacuum Pump", "HVAC"),
    ("Torque Wrench Set", "Mechanical"),
    ("Oscilloscope", "Testing"),
    ("Megger Insulation Tester", "Electrical"),
    ("Laser Alignment Tool", "Mechanical"),
    ("Vibration Analyzer", "Testing"),
    ("Ultrasonic Thickness Gauge", "Testing"),
    ("Portable Generator 5kW", "Power"),
    ("Air Compressor 3HP", "Pneumatic"),
    ("Pressure Test Pump", "Plumbing"),
    ("Cable Puller", "Electrical"),
    ("Concrete Drill", "Construction"),
    ("Scaffold Set", "Construction"),
    ("Safety Harness Kit", "Safety"),
    ("Gas Detector 4-in-1", "Safety"),
    ("Lockout/Tagout Kit", "Safety"),
    ("Refrigerant Leak Detector", "HVAC"),
    ("Clamp Meter", "Electrical"),
    ("Soldering Station", "Electronics"),
    ("Crimping Tool Set", "Electrical"),
    ("Impact Wrench 1/2-inch", "Mechanical"),
    ("Grease Gun", "Mechanical"),
    ("Power Washer", "Cleaning"),
    ("Floor Buffer", "Cleaning"),
    ("Carpet Extractor", "Cleaning"),
    ("Wet/Dry Vacuum", "Cleaning"),
    ("Paint Sprayer", "Painting"),
    ("Belt Tension Meter", "Mechanical"),
    ("Bore Scope Camera", "Testing"),
    ("Drain Snake Machine", "Plumbing"),
    ("Pipe Locator", "Plumbing"),
    ("Stud Finder", "Construction"),
    ("Biomedical Calibrator", "Biomedical"),
    ("Electrical Safety Analyzer", "Biomedical"),
    ("SpO2 Simulator", "Biomedical"),
    ("ECG Simulator", "Biomedical"),
    ("NIBP Simulator", "Biomedical"),
    ("Defibrillator Analyzer", "Biomedical"),
    ("Infusion Pump Analyzer", "Biomedical"),
    ("Ventilator Tester", "Biomedical"),
    ("Radiation Survey Meter", "Radiology"),
    ("Dosimeter Reader", "Radiology"),
]

SERVICE_REQUEST_TITLES = [
    "AC unit not cooling in Ward 3B",
    "Leaking faucet in OR 2 scrub area",
    "Flickering lights in ICU hallway",
    "Elevator B making unusual noise",
    "Emergency exit light not working",
    "Hot water not available in ER",
    "Broken window handle in Admin office",
    "Ceiling tile damaged in Lobby",
    "Toilet not flushing in Outpatient",
    "Door lock stuck on Pharmacy entrance",
    "Pest sighting in Kitchen area",
    "Water stain on ceiling in Pedia Ward",
    "Faulty nurse call button Room 412",
    "Power outlet sparking in Lab 2",
    "Generator auto-transfer not working",
    "Medical gas alarm panel showing fault",
    "Fire extinguisher expired in ER",
    "Parking lot light pole out",
    "Wheelchair wheel broken",
    "Autoclave door seal leaking steam",
    "X-ray room temperature too high",
    "CT scanner cooling fan noisy",
    "Patient monitor screen flickering",
    "Defibrillator battery low alarm",
    "Oxygen flowmeter not calibrated",
    "Suction machine weak pressure",
    "IV pump alarm malfunction",
    "Dental chair hydraulic leak",
    "Dialysis water purification alarm",
    "Blood bank fridge temp alarm",
    "Pharmacy fridge above set point",
    "Mortuary cooler not reaching temp",
    "Laundry dryer taking too long",
    "Kitchen dishwasher not draining",
    "CCTV camera 7 offline",
    "Access card reader failure Gate B",
    "Pneumatic tube stuck at Station 5",
    "Intercom system feedback noise",
    "Paint peeling in Delivery Room",
    "Floor tile cracked in Main Lobby",
    "Roof leak above Radiology",
    "Drainage blocked in Utility Room",
    "UPS alarm beeping in Server Room",
    "Air handling unit vibrating loudly",
    "Chiller low refrigerant alarm",
    "Boiler pressure gauge faulty",
    "Fire sprinkler head damaged",
    "EMG machine power issue",
    "Ventilator self-test failure",
    "Stretcher brake not engaging",
]

CHECKLIST_NAMES = [
    ("HVAC Monthly Inspection", "Maintenance"),
    ("Generator Pre-Start Check", "Maintenance"),
    ("Elevator Safety Checklist", "Safety"),
    ("Fire System Monthly Test", "Safety"),
    ("Medical Gas Daily Check", "Maintenance"),
    ("Boiler Daily Inspection", "Maintenance"),
    ("UPS Weekly Test", "Maintenance"),
    ("Water Quality Sampling", "Maintenance"),
    ("Autoclave Cycle Validation", "Maintenance"),
    ("Chiller Daily Log", "Maintenance"),
    ("Electrical Panel Inspection", "Maintenance"),
    ("Emergency Light Monthly", "Safety"),
    ("X-Ray QA Daily", "Inspection"),
    ("CT Daily Warm-Up", "Inspection"),
    ("Ventilator Daily Check", "Maintenance"),
    ("Patient Monitor Check", "Inspection"),
    ("Defibrillator Daily", "Inspection"),
    ("Anesthesia Machine Pre-Use", "Safety"),
    ("Dialysis Pre-Treatment", "Maintenance"),
    ("Nurse Call Weekly Test", "Maintenance"),
    ("Receiving Inspection Form", "Receiving"),
    ("Parts Receiving QC Check", "Receiving"),
    ("Equipment Receiving Check", "Receiving"),
    ("Biomedical PM Checklist", "Maintenance"),
    ("Facility Walkthrough", "Inspection"),
]

CHECKLIST_ITEMS_MAP = {
    "Maintenance": [
        "Check operating temperature", "Inspect belts and hoses", "Verify pressure readings",
        "Test safety switches", "Lubricate moving parts", "Check fluid levels",
        "Inspect electrical connections", "Verify alarm functions", "Check filter condition",
        "Record meter readings",
    ],
    "Safety": [
        "Verify emergency stop function", "Check safety guards in place", "Test alarm system",
        "Inspect fire extinguisher", "Check emergency lighting", "Verify exit signage",
        "Test interlock switches", "Check PPE availability", "Verify lockout/tagout",
        "Review safety logbook",
    ],
    "Inspection": [
        "Visual inspection for damage", "Check calibration status", "Verify display accuracy",
        "Test all operating modes", "Check cable integrity", "Verify patient safety",
        "Record baseline readings", "Compare with specifications",
    ],
    "Receiving": [
        "Verify packing list", "Check for shipping damage", "Verify quantity received",
        "Check expiration dates", "Verify model and serial number",
        "Inspect packaging integrity", "Temperature check if applicable",
    ],
}

SENSOR_NAMES = [
    "HVAC Supply Temp Sensor A1", "HVAC Return Temp Sensor A1", "Chiller Inlet Temp",
    "Chiller Outlet Temp", "Boiler Stack Temp", "Generator Coolant Temp",
    "OR-1 Room Temperature", "OR-2 Room Temperature", "ICU Room Temperature",
    "Pharmacy Fridge Temp", "Blood Bank Fridge Temp", "Mortuary Cooler Temp",
    "Server Room Temperature", "Electrical Room Temp", "OR-1 Humidity",
    "OR-2 Humidity", "Pharmacy Humidity", "Server Room Humidity",
    "Medical Air Pressure", "O2 Pipeline Pressure", "N2O Pipeline Pressure",
    "Vacuum Pipeline Pressure", "Boiler Steam Pressure", "Chiller Refrigerant Pressure",
    "Generator Oil Pressure", "Water Main Pressure", "Fire Pump Discharge Pressure",
    "AHU-1 Vibration", "AHU-2 Vibration", "Chiller Compressor Vibration",
    "Generator Vibration", "Elevator Motor Vibration", "Pump-1 Vibration",
    "Pump-2 Vibration", "Main Transformer Current", "Generator Output Voltage",
    "UPS Load Percentage", "Chiller Power Consumption", "AHU-1 Power Consumption",
    "Boiler Gas Flow Rate", "Medical Air Compressor Hours", "Vacuum Pump Hours",
    "Generator Run Hours", "Elevator Trip Count", "Water Consumption Flow",
    "Diesel Tank Level", "Medical O2 Tank Level", "Chemical Tank Level",
    "Waste Water pH Level", "Potable Water Chlorine Level",
]


def main():
    with engine.begin() as conn:
        load_series(conn)

        # ── Load actual reference IDs from DB ───────────────────────────
        ASSETS = [r[0] for r in conn.execute(text("SELECT id FROM asset ORDER BY id")).fetchall()]
        LOCATIONS = [r[0] for r in conn.execute(text("SELECT id FROM location ORDER BY id")).fetchall()]
        TRADES = [r[0] for r in conn.execute(text("SELECT id FROM trade ORDER BY id")).fetchall()]
        ITEMS = [r[0] for r in conn.execute(text("SELECT id FROM item ORDER BY id")).fetchall()]
        CHECKLISTS = [r[0] for r in conn.execute(text("SELECT id FROM checklist ORDER BY id")).fetchall()]
        ASSET_PROPS = [r[0] for r in conn.execute(text("SELECT id FROM asset_property ORDER BY id")).fetchall()]
        UOMS = [r[0] for r in conn.execute(text("SELECT id FROM unit_of_measure ORDER BY id")).fetchall()]
        EXISTING_MA = [r[0] for r in conn.execute(text("SELECT id FROM maintenance_activity ORDER BY id")).fetchall()]
        EXISTING_MTREQ = [r[0] for r in conn.execute(text("SELECT id FROM maintenance_request ORDER BY id")).fetchall()]
        print(f"Loaded: {len(ASSETS)} assets, {len(LOCATIONS)} locations, {len(TRADES)} trades, "
              f"{len(ITEMS)} items, {len(CHECKLISTS)} checklists, {len(ASSET_PROPS)} asset_props, "
              f"{len(UOMS)} uoms, {len(EXISTING_MA)} maint_activities, {len(EXISTING_MTREQ)} maint_requests")

        # ── 1. Equipment (50 records) ───────────────────────────────────
        print("Seeding equipment ...")
        eq_data = []
        for (ename, etype) in EQUIPMENT_NAMES:
            eqid = next_id("EQP", width=4)
            eq_data.append({
                "id": eqid,
                "equipment_type": etype,
                "equipment_group": None,
                "equipment_group_name": None,
                "custodian": random.choice(EMPLOYEES),
                "location": random.choice(LOCATIONS),
                "location_name": None,
                "site": random.choice(SITES),
                "inventory": None,
                "pr_line_no": None,
                "description": ename,
                "equipment_cost": round(random.uniform(5000, 250000), 2),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO equipment (id, equipment_type, equipment_group, equipment_group_name,
            custodian, location, location_name, site, inventory, pr_line_no, description, equipment_cost,
            created_at, updated_at)
            VALUES (:id, :equipment_type, :equipment_group, :equipment_group_name,
            :custodian, :location, :location_name, :site, :inventory, :pr_line_no, :description, :equipment_cost,
            :created_at, :updated_at)"""), eq_data)
        ALL_EQUIPMENT = [d["id"] for d in eq_data]
        print(f"  → {len(eq_data)} equipment records")

        # ── 2. Maintenance Activities (+46 → 50 total) ─────────────────
        print("Seeding maintenance_activity ...")
        ma_data = []
        for (aname, adesc) in ACTIVITY_NAMES:
            # Use prefix "MA" matching existing series
            maid = next_id("MA", width=4)
            ma_data.append({
                "id": maid,
                "activity_name": aname,
                "description": adesc,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_activity (id, activity_name, description, created_at, updated_at)
            VALUES (:id, :activity_name, :description, :created_at, :updated_at)"""), ma_data)
        ALL_MA = EXISTING_MA + [d["id"] for d in ma_data]
        print(f"  → {len(ma_data)} new activities (total {len(ALL_MA)})")

        # ── 3. Checklists (+25 → 50 total) ─────────────────────────────
        print("Seeding checklists ...")
        chk_data = []
        chkd_data = []
        for (cname, ctype) in CHECKLIST_NAMES:
            chkid = next_id("CHL")
            chk_data.append({
                "id": chkid,
                "checklist_name": cname,
                "checklist_type": ctype,
                "created_at": ts(), "updated_at": ts(),
            })
            # Add checklist detail items
            items_for_type = CHECKLIST_ITEMS_MAP.get(ctype, CHECKLIST_ITEMS_MAP["Maintenance"])
            for idx, item_name in enumerate(random.sample(items_for_type, min(len(items_for_type), random.randint(4, 8)))):
                chkdid = next_id("CHLD")
                chkd_data.append({
                    "id": chkdid,
                    "checklist": chkid,
                    "item_name": item_name,
                    "is_mandatory": random.choice([True, True, False]),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO checklist (id, checklist_name, checklist_type, created_at, updated_at)
            VALUES (:id, :checklist_name, :checklist_type, :created_at, :updated_at)"""), chk_data)
        if chkd_data:
            conn.execute(text("""INSERT INTO checklist_details (id, checklist, item_name, is_mandatory, created_at, updated_at)
                VALUES (:id, :checklist, :item_name, :is_mandatory, :created_at, :updated_at)"""), chkd_data)
        ALL_CHECKLISTS = CHECKLISTS + [d["id"] for d in chk_data]
        print(f"  → {len(chk_data)} new checklists, {len(chkd_data)} detail items (total {len(ALL_CHECKLISTS)} checklists)")

        # ── 4. Maintenance Trade (50) ───────────────────────────────────
        print("Seeding maintenance_trade ...")
        mt_data = []
        for i in range(50):
            mtid = next_id("MTTRD")
            mt_data.append({
                "id": mtid,
                "maintenance_activity": random.choice(ALL_MA),
                "trade": random.choice(TRADES) if TRADES else None,
                "required_qty": random.randint(1, 5),
                "required_hours": round(random.uniform(0.5, 8.0), 1),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_trade (id, maintenance_activity, trade, required_qty, required_hours,
            created_at, updated_at)
            VALUES (:id, :maintenance_activity, :trade, :required_qty, :required_hours,
            :created_at, :updated_at)"""), mt_data)
        print(f"  → {len(mt_data)} maintenance trades")

        # ── 5. Maintenance Parts (50) ───────────────────────────────────
        print("Seeding maintenance_parts ...")
        mp_data = []
        for i in range(50):
            mpid = next_id("MTPART")
            mp_data.append({
                "id": mpid,
                "maintenance_activity": random.choice(ALL_MA),
                "item": random.choice(ITEMS) if ITEMS else None,
                "quantity": random.randint(1, 20),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_parts (id, maintenance_activity, item, quantity, created_at, updated_at)
            VALUES (:id, :maintenance_activity, :item, :quantity, :created_at, :updated_at)"""), mp_data)
        print(f"  → {len(mp_data)} maintenance parts")

        # ── 6. Maintenance Equipment (50) ───────────────────────────────
        print("Seeding maintenance_equipment ...")
        me_data = []
        for i in range(50):
            meid = next_id("MTEQP")
            me_data.append({
                "id": meid,
                "maintenance_activity": random.choice(ALL_MA),
                "equipment": random.choice(ALL_EQUIPMENT),
                "required_qty": random.randint(1, 3),
                "required_hours": round(random.uniform(0.5, 8.0), 1),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_equipment (id, maintenance_activity, equipment, required_qty,
            required_hours, created_at, updated_at)
            VALUES (:id, :maintenance_activity, :equipment, :required_qty,
            :required_hours, :created_at, :updated_at)"""), me_data)
        print(f"  → {len(me_data)} maintenance equipment")

        # ── 7. Service Requests (50) ────────────────────────────────────
        print("Seeding service_request ...")
        sr_data = []
        statuses = ["Draft", "Submitted", "In Progress", "Closed", "Cancelled"]
        for i, title in enumerate(SERVICE_REQUEST_TITLES):
            srid = next_id("SRQ")
            status = random.choice(statuses)
            sr_data.append({
                "id": srid,
                "title": title,
                "description": f"Reported issue: {title}. Please dispatch appropriate team for resolution.",
                "status": status,
                "priority": random.choice(PRIORITIES),
                "date_reported": rand_date(120, 1),
                "closed_date": rand_date(60, 1) if status in ("Closed", "Cancelled") else None,
                "asset": random.choice(ASSETS) if random.random() > 0.3 else None,
                "site": random.choice(SITES),
                "location": random.choice(LOCATIONS),
                "work_order": random.choice(WORK_ORDERS) if status in ("In Progress", "Closed") and random.random() > 0.5 else None,
                "incident": None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO service_request (id, title, description, status, priority, date_reported,
            closed_date, asset, site, location, work_order, incident, created_at, updated_at)
            VALUES (:id, :title, :description, :status, :priority, :date_reported,
            :closed_date, :asset, :site, :location, :work_order, :incident, :created_at, :updated_at)"""), sr_data)
        print(f"  → {len(sr_data)} service requests")

        # ── 8. Maintenance Requests (+45 → 50 total) ───────────────────
        print("Seeding maintenance_request ...")
        mr_data = []
        mr_descriptions = [
            "Preventive maintenance due for HVAC system",
            "Scheduled filter replacement for AHU",
            "Generator monthly load test required",
            "Annual elevator safety inspection due",
            "Fire alarm quarterly test scheduled",
            "Medical gas system routine check",
            "Boiler annual inspection due",
            "UPS battery replacement scheduled",
            "Water quality testing cycle",
            "Sterilizer validation due",
            "Chiller performance degradation observed",
            "Electrical panel hot spot detected",
            "Plumbing flush schedule due",
            "Emergency lighting test cycle",
            "X-ray tube replacement assessment",
            "CT scanner image quality degraded",
            "Ventilator malfunction reported",
            "Patient monitor drift calibration",
            "Defibrillator annual test due",
            "Anesthesia vaporizer calibration",
            "Dialysis machine RO membrane check",
            "Nurse call system fault reported",
            "Roof inspection after heavy rain",
            "Paint deterioration in patient areas",
            "Parking lot restriping needed",
            "Landscaping storm damage repair",
            "Pest control quarterly treatment",
            "Window cleaning schedule",
            "CCTV storage drive replacement",
            "Access control battery replacement",
            "Pneumatic tube stuck capsules",
            "Mattress replacement assessment",
            "Wheelchair fleet inspection",
            "Stretcher hydraulics failing",
            "OR table positioning motor issue",
            "Surgical light arm loose",
            "Laundry extractor bearing noise",
            "Kitchen oven thermostat drift",
            "Pharmacy fridge alarm threshold",
            "Blood bank backup generator test",
            "Mortuary system PM scheduled",
            "Solar inverter fault alarm",
            "Waste compactor hydraulic leak",
            "Air quality reading out of spec",
            "Pump vibration above threshold",
        ]
        wf_states = ["Draft", "Pending Approval", "Approved", "Release", "Completed"]
        for i, desc in enumerate(mr_descriptions):
            mrid = next_id("MTREQ")
            wf = random.choice(wf_states)
            asset = random.choice(ASSETS)
            mr_data.append({
                "id": mrid,
                "workflow_state": wf,
                "requestor": random.choice(EMPLOYEES),
                "requested_date": rand_date(120, 1),
                "description": desc,
                "priority": random.choice(PRIORITIES),
                "asset": asset,
                "request_type": random.choice(REQ_ACT_TYPES),
                "location": random.choice(LOCATIONS),
                "site": random.choice(SITES),
                "department": random.choice(DEPTS),
                "position": None,
                "incident": None,
                "planned_maintenance_activity": None,
                "due_date": rand_date(30, 1) if random.random() > 0.3 else None,
                "next_maintenance_request": None,
                "closed_date": rand_date(30, 1) if wf == "Completed" else None,
                "work_order_activity": random.choice(WOA) if wf in ("Release", "Completed") else None,
                "property": None,
                "maintenance_interval_property": None,
                "running_interval_value": None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_request (id, workflow_state, requestor, requested_date, description,
            priority, asset, request_type, location, site, department, position, incident,
            planned_maintenance_activity, due_date, next_maintenance_request, closed_date,
            work_order_activity, property, maintenance_interval_property, running_interval_value,
            created_at, updated_at)
            VALUES (:id, :workflow_state, :requestor, :requested_date, :description,
            :priority, :asset, :request_type, :location, :site, :department, :position, :incident,
            :planned_maintenance_activity, :due_date, :next_maintenance_request, :closed_date,
            :work_order_activity, :property, :maintenance_interval_property, :running_interval_value,
            :created_at, :updated_at)"""), mr_data)
        ALL_MTREQ = EXISTING_MTREQ + [d["id"] for d in mr_data]
        print(f"  → {len(mr_data)} new requests (total {len(ALL_MTREQ)})")

        # ── 9. Maintenance Plans (50) ───────────────────────────────────
        print("Seeding maintenance_plan ...")
        plan_data = []
        plan_descs = [
            "HVAC System Preventive Maintenance Plan",
            "Generator Monthly Maintenance Schedule",
            "Elevator Annual Maintenance Program",
            "Fire Safety Systems Quarterly Plan",
            "Medical Gas System Maintenance Plan",
            "Boiler Maintenance Schedule",
            "UPS and Power Systems Plan",
            "Water Treatment Maintenance Plan",
            "Sterilization Equipment PM Plan",
            "Chiller System Maintenance Plan",
            "Electrical Distribution PM Plan",
            "Emergency Systems Test Plan",
            "Diagnostic Imaging QA Plan",
            "CT Scanner Maintenance Program",
            "Ventilator Maintenance Schedule",
            "Patient Monitoring PM Plan",
            "Defibrillator Test Schedule",
            "Anesthesia Equipment PM Plan",
            "Dialysis Equipment Maintenance",
            "Communication Systems PM Plan",
            "Roof and Exterior Maintenance",
            "Interior Maintenance Plan",
            "Parking and Grounds Maintenance",
            "Pest Control Schedule",
            "Security Systems PM Plan",
            "Pneumatic Tube System PM",
            "Patient Furniture Maintenance",
            "OR Equipment PM Program",
            "Laundry Equipment PM Plan",
            "Kitchen Equipment PM Plan",
            "Pharmacy Equipment PM Plan",
            "Blood Bank Equipment PM Plan",
            "Mortuary Equipment PM Plan",
            "Solar Systems PM Plan",
            "Waste Management Equipment PM",
            "Air Quality Monitoring Plan",
            "Vibration Monitoring Program",
            "Plumbing System Maintenance",
            "Paint and Finish Maintenance",
            "Window and Glass Maintenance",
            "CCTV Maintenance Schedule",
            "Access Control PM Plan",
            "Biomedical Equipment Annual PM",
            "Facility Walkthrough Schedule",
            "Energy Management PM Plan",
            "Water Conservation Plan",
            "Infection Control Equipment PM",
            "Laboratory Equipment PM Plan",
            "Rehabilitation Equipment PM",
            "Dental Equipment PM Plan",
        ]
        for desc in plan_descs:
            pid = next_id("MTPLAN")
            plan_data.append({
                "id": pid,
                "description": desc,
                "asset_class": random.choice(ASSET_CLASSES),
                "asset_class_name": None,
                "manufacturer": random.choice(MANUFACTURERS) if random.random() > 0.4 else None,
                "manufacturer_name": None,
                "model": random.choice(MODELS) if random.random() > 0.5 else None,
                "model_name": None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_plan (id, description, asset_class, asset_class_name,
            manufacturer, manufacturer_name, model, model_name, created_at, updated_at)
            VALUES (:id, :description, :asset_class, :asset_class_name,
            :manufacturer, :manufacturer_name, :model, :model_name, :created_at, :updated_at)"""), plan_data)
        ALL_PLANS = [d["id"] for d in plan_data]
        print(f"  → {len(plan_data)} maintenance plans")

        # ── 10. Planned Maintenance Activities (50) ─────────────────────
        print("Seeding planned_maintenance_activity ...")
        pma_data = []
        schedules = ["Calendar Based", "Interval Based", "Condition Based"]
        for i in range(50):
            pmaid = next_id("PMA")
            plan = random.choice(ALL_PLANS)
            ma = random.choice(ALL_MA)
            chk = random.choice(ALL_CHECKLISTS) if random.random() > 0.3 else None
            pma_data.append({
                "id": pmaid,
                "maintenance_plan": plan,
                "maintenance_plan_name": None,
                "maintenance_activity": ma,
                "maintenance_activity_name": None,
                "checklist": chk,
                "checklist_name": None,
                "maintenance_schedule": random.choice(schedules),
                "maintenance_type": random.choice(REQ_ACT_TYPES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO planned_maintenance_activity (id, maintenance_plan, maintenance_plan_name,
            maintenance_activity, maintenance_activity_name, checklist, checklist_name,
            maintenance_schedule, maintenance_type, created_at, updated_at)
            VALUES (:id, :maintenance_plan, :maintenance_plan_name,
            :maintenance_activity, :maintenance_activity_name, :checklist, :checklist_name,
            :maintenance_schedule, :maintenance_type, :created_at, :updated_at)"""), pma_data)
        ALL_PMA = [d["id"] for d in pma_data]
        print(f"  → {len(pma_data)} planned maintenance activities")

        # ── 11. Maintenance Calendar (50) ───────────────────────────────
        print("Seeding maintenance_calendar ...")
        cal_data = []
        frequencies = ["Weekly", "Monthly", "Quarterly", "Annually", "Day of Week", "Day of Month"]
        for i in range(50):
            calid = next_id("MTCAL")
            pma = random.choice(ALL_PMA)
            cal_data.append({
                "id": calid,
                "planned_maintenance_activity": pma,
                "maintenance_plan": None,
                "maintenance_activity": None,
                "frequency": random.choice(frequencies),
                "lead_calendar_days": random.choice([1, 3, 5, 7, 14, 30]),
                "last_maintenance_date_property": random.choice(PROPERTIES) if random.random() > 0.5 else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_calendar (id, planned_maintenance_activity, maintenance_plan,
            maintenance_activity, frequency, lead_calendar_days, last_maintenance_date_property,
            created_at, updated_at)
            VALUES (:id, :planned_maintenance_activity, :maintenance_plan,
            :maintenance_activity, :frequency, :lead_calendar_days, :last_maintenance_date_property,
            :created_at, :updated_at)"""), cal_data)
        print(f"  → {len(cal_data)} maintenance calendars")

        # ── 12. Maintenance Interval (50) ───────────────────────────────
        print("Seeding maintenance_interval ...")
        mi_data = []
        for i in range(50):
            miid = next_id("MTINT")
            pma = random.choice(ALL_PMA)
            mi_data.append({
                "id": miid,
                "planned_maintenance_activity": pma,
                "maintenance_plan": None,
                "maintenance_activity": None,
                "lead_interval": round(random.uniform(1, 50), 1),
                "interval": round(random.uniform(10, 5000), 1),
                "interval_unit_of_measure": random.choice(UOMS) if UOMS else None,
                "running_interval_property": random.choice(PROPERTIES) if random.random() > 0.5 else None,
                "last_interval_property": random.choice(PROPERTIES) if random.random() > 0.5 else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_interval (id, planned_maintenance_activity, maintenance_plan,
            maintenance_activity, lead_interval, interval, interval_unit_of_measure,
            running_interval_property, last_interval_property, created_at, updated_at)
            VALUES (:id, :planned_maintenance_activity, :maintenance_plan,
            :maintenance_activity, :lead_interval, :interval, :interval_unit_of_measure,
            :running_interval_property, :last_interval_property, :created_at, :updated_at)"""), mi_data)
        print(f"  → {len(mi_data)} maintenance intervals")

        # ── 13. Sensors (50) ───────────────────────────────────────────
        print("Seeding sensor ...")
        sensor_data_list = []
        for sname in SENSOR_NAMES:
            snrid = next_id("SNR")
            asset = random.choice(ASSETS)
            sensor_data_list.append({
                "id": snrid,
                "sensor_name": sname,
                "asset": asset,
                "asset_name": None,
                "asset_property": random.choice(ASSET_PROPS) if ASSET_PROPS else None,
                "uom_short_name": None,
                "property_type": None,
                "root_topic_name": f"spmc/sensors/{snrid.lower()}",
                "collection_frequency": random.choice(["hourly", "daily", "weekly", "monthly"]),
                "site": random.choice(SITES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO sensor (id, sensor_name, asset, asset_name, asset_property,
            uom_short_name, property_type, root_topic_name, collection_frequency, site,
            created_at, updated_at)
            VALUES (:id, :sensor_name, :asset, :asset_name, :asset_property,
            :uom_short_name, :property_type, :root_topic_name, :collection_frequency, :site,
            :created_at, :updated_at)"""), sensor_data_list)
        ALL_SENSORS = [d["id"] for d in sensor_data_list]
        print(f"  → {len(sensor_data_list)} sensors")

        # ── 14. Sensor Data (50) ──────────────────────────────────────
        print("Seeding sensor_data ...")
        sd_data = []
        for i in range(50):
            sdid = next_id("SNRD")
            sd_data.append({
                "id": sdid,
                "sensor": random.choice(ALL_SENSORS),
                "value": str(round(random.uniform(0, 500), 2)),
                "timestamp": rand_dt(30, 1).isoformat(),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO sensor_data (id, sensor, value, timestamp, created_at, updated_at)
            VALUES (:id, :sensor, :value, :timestamp, :created_at, :updated_at)"""), sd_data)
        print(f"  → {len(sd_data)} sensor data records")

        # ── 15. Maintenance Condition (50) ─────────────────────────────
        print("Seeding maintenance_condition ...")
        mc_data = []
        operators = ["==", "!=", ">", "<", ">=", "<="]
        for i in range(50):
            mcid = next_id("MTCOND")
            mc_data.append({
                "id": mcid,
                "planned_maintenance_activity": random.choice(ALL_PMA),
                "maintenance_plan": None,
                "maintenance_activity": None,
                "sensor": random.choice(ALL_SENSORS),
                "uom_short_name": None,
                "property_type": None,
                "comparison_operator": random.choice(operators),
                "threshold_property": random.choice(PROPERTIES) if random.random() > 0.3 else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_condition (id, planned_maintenance_activity, maintenance_plan,
            maintenance_activity, sensor, uom_short_name, property_type, comparison_operator,
            threshold_property, created_at, updated_at)
            VALUES (:id, :planned_maintenance_activity, :maintenance_plan,
            :maintenance_activity, :sensor, :uom_short_name, :property_type, :comparison_operator,
            :threshold_property, :created_at, :updated_at)"""), mc_data)
        print(f"  → {len(mc_data)} maintenance conditions")

        # ── 16. Maintenance Orders (50) ────────────────────────────────
        print("Seeding maintenance_order ...")
        mo_data = []
        for i in range(50):
            moid = next_id("MTORD")
            mo_data.append({
                "id": moid,
                "created_date": rand_date(90, 1),
                "work_order": random.choice(WORK_ORDERS) if random.random() > 0.4 else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO maintenance_order (id, created_date, work_order, created_at, updated_at)
            VALUES (:id, :created_date, :work_order, :created_at, :updated_at)"""), mo_data)
        ALL_MO = [d["id"] for d in mo_data]
        print(f"  → {len(mo_data)} maintenance orders")

        # ── 17. Maintenance Order Details ──────────────────────────────
        print("Seeding maintenance_order_detail ...")
        mod_data = []
        avail_statuses = ["Available", "Partially Available", "Not Available", "Pending Check"]
        for mo in ALL_MO:
            # 1-3 details per order
            for seq in range(1, random.randint(2, 4)):
                modid = next_id("MTORDD")
                mod_data.append({
                    "id": modid,
                    "maintenance_order": mo,
                    "seq_num": seq,
                    "maint_req": random.choice(ALL_MTREQ),
                    "asset": random.choice(ASSETS),
                    "due_date": str(rand_date(60, 1)),
                    "resource_availability_status": random.choice(avail_statuses),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO maintenance_order_detail (id, maintenance_order, seq_num, maint_req,
            asset, due_date, resource_availability_status, created_at, updated_at)
            VALUES (:id, :maintenance_order, :seq_num, :maint_req,
            :asset, :due_date, :resource_availability_status, :created_at, :updated_at)"""), mod_data)
        print(f"  → {len(mod_data)} maintenance order details")

        # ── Update all series counters ─────────────────────────────────
        update_series(conn)
        print("\n✓ All series counters updated")

    print("\n════════════════════════════════════════════════════════════")
    print("SEED COMPLETE - Maintenance Management module")
    print("════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
