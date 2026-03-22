"""
Seed script for Asset Management sections that have no/insufficient data:
- Disposed, Property, Property Type, Position, Asset Class,
- System Type, Location Type, Incident, Incident Employee, Breakdown
"""
import psycopg2
import random
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost", port=5432, dbname="eam-spmc",
    user="eam_spmc_user", password="CwSpmcSec2026mR7"
)
cur = conn.cursor()

# ── FK References ──
asset_ids = [f"A-{str(i).zfill(5)}" for i in range(1, 75)] + ["A-00079", "A-00080", "A-00082"]
site_ids = ["SITE-0001", "SITE-0002", "SITE-0003", "SITE-0004"]
location_ids = [f"LOC-{str(i).zfill(4)}" for i in range(1, 60)] + ["LOC-0066", "LOC-0067", "LOC-0068"]
system_ids = [f"SYS-{str(i).zfill(4)}" for i in range(1, 78)]
asset_class_ids = [f"AC-{str(i).zfill(4)}" for i in range(1, 14)]  # existing
equipment_ids = [f"EQP-{str(i).zfill(4)}" for i in range(1, 51)]
employee_ids = ["EMP-0001","EMP-0002","EMP-0003","EMP-0004","EMP-0005",
                "EMP-0021","EMP-0022","EMP-0023","EMP-0024","EMP-0025"]
department_ids = [f"DEPT-{str(i).zfill(4)}" for i in range(1, 19)] + \
                 [f"DEPT-{str(i).zfill(4)}" for i in range(34, 39)]
user_ids = [
    "023c5ac6-a480-4bc7-a77d-078f453d73e0","1e5d153b-6a90-4777-92e5-e5c4154236ab",
    "439d8021-7323-4e20-95bb-504a54db839c","45a73aaa-6184-4003-b447-1ee121968bd5",
    "62fcca4c-95f2-4222-9bea-0469428f69a7","79c9c8c0-9d30-4ef8-9f4b-433c42c6d237",
    "86261ca1-619f-4fd8-beb8-321c71c61e1d","ce00ecca-b47f-45f7-beb4-b6a6171fd536",
    "d7562a34-6bf6-4673-84c2-3432efebf276","e5665d57-07a4-43aa-8c73-094f46ccd68c",
    "e571c973-36d6-4347-a877-3667859f51e2","e5e5dad7-0e62-46ff-9b61-cbe75d874642",
    "e5e8204b-72d3-433b-9aed-0c15860e7aac",
]
uom_ids = [
    "UOM-0001","UOM-00010","UOM-00011","UOM-00012","UOM-00013","UOM-00014",
    "UOM-00015","UOM-00016","UOM-00017","UOM-00018","UOM-00019","UOM-0002",
    "UOM-00020","UOM-00021","UOM-00022","UOM-00023","UOM-00024","UOM-00025",
    "UOM-00026","UOM-00027",
]

def rand_date(start_year=2024, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 3, 1)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")

def rand_datetime(start_year=2024, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 3, 1)
    delta = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta))).strftime("%Y-%m-%d %H:%M:%S")

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ═══════════════════════════════════════════════════════
# 1. PROPERTY TYPE (currently 2 → add 8 more = 10 total)
# ═══════════════════════════════════════════════════════
print("Seeding property_type...")
property_type_new = [
    "Boolean", "Date", "Integer", "Decimal", "Percentage",
    "Currency", "Duration", "Rating",
]
for i, name in enumerate(property_type_new, start=3):
    pid = f"PT-{str(i).zfill(4)}"
    cur.execute("INSERT INTO property_type (id, name, created_at, updated_at) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (pid, name, NOW, NOW))
conn.commit()
print(f"  property_type: inserted {len(property_type_new)} new rows")

# All property type IDs
all_property_type_ids = [f"PT-{str(i).zfill(4)}" for i in range(1, 11)]

# ═══════════════════════════════════════════════════════
# 2. LOCATION TYPE (currently 4 → add 46 more = 50 total)
# ═══════════════════════════════════════════════════════
print("Seeding location_type...")
location_type_new = [
    "Wing", "Ward", "Department", "Corridor", "Lobby", "Basement",
    "Rooftop", "Utility Room", "Plant Room", "Server Room",
    "Operating Theater", "ICU Bay", "Emergency Bay", "Pharmacy",
    "Laboratory", "Radiology Suite", "CT Room", "MRI Room",
    "X-Ray Room", "Ultrasound Room", "Recovery Room", "Nurse Station",
    "Reception", "Waiting Area", "Cafeteria", "Kitchen",
    "Laundry Room", "Storage Room", "Supply Closet", "Parking Area",
    "Loading Dock", "Workshop", "Office", "Conference Room",
    "Chapel", "Mortuary", "NICU", "PICU", "Dialysis Unit",
    "Blood Bank", "Outpatient Clinic", "Rehabilitation Room",
    "Sterilization Room", "Waste Management Area", "Helipad",
    "Garden/Courtyard",
]
for i, name in enumerate(location_type_new, start=5):
    lid = f"LT-{str(i).zfill(4)}"
    cur.execute("INSERT INTO location_type (id, name, created_at, updated_at) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (lid, name, NOW, NOW))
conn.commit()
print(f"  location_type: inserted {len(location_type_new)} new rows")

# ═══════════════════════════════════════════════════════
# 3. SYSTEM TYPE (currently 10 → add 40 more = 50 total)
# ═══════════════════════════════════════════════════════
print("Seeding system_type...")
system_type_new = [
    "Water Supply", "Waste Water", "Steam Distribution", "Compressed Air",
    "Vacuum System", "Nurse Call", "Building Automation", "Security/CCTV",
    "Access Control", "Public Address", "Pneumatic Tube", "Lighting",
    "Solar Power", "Emergency Power", "UPS Systems", "Fuel System",
    "Refrigeration", "Cold Storage", "Sterilization", "Medical Waste",
    "Oxygen Distribution", "Nitrous Oxide", "Nitrogen Supply", "Carbon Dioxide",
    "Surgical Lighting", "Patient Monitoring", "Telemetry", "Data Network",
    "Telephone/VOIP", "Intercom", "Fire Alarm", "Fire Suppression",
    "Smoke Extraction", "Stormwater", "Rainwater Harvesting", "Irrigation",
    "Kitchen Equipment", "Laundry Equipment", "Elevator Controls", "Escalator",
]
for i, name in enumerate(system_type_new, start=11):
    sid = f"ST-{str(i).zfill(4)}"
    cur.execute("INSERT INTO system_type (id, name, created_at, updated_at) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (sid, name, NOW, NOW))
conn.commit()
print(f"  system_type: inserted {len(system_type_new)} new rows")

# ═══════════════════════════════════════════════════════
# 4. ASSET CLASS (currently 13 → add 37 more = 50 total)
# ═══════════════════════════════════════════════════════
print("Seeding asset_class...")
asset_class_new = [
    ("CT Scanner", "Diagnostic imaging computed tomography scanner"),
    ("X-Ray Machine", "Radiography equipment for X-ray imaging"),
    ("Ultrasound Machine", "Diagnostic ultrasound imaging equipment"),
    ("Ventilator", "Mechanical ventilation for respiratory support"),
    ("Patient Monitor", "Bedside vital signs monitoring system"),
    ("Infusion Pump", "Intravenous fluid delivery pump"),
    ("Defibrillator", "Cardiac defibrillation device"),
    ("Anesthesia Machine", "Anesthesia delivery and monitoring system"),
    ("Surgical Table", "Motorized operating room table"),
    ("Autoclave", "High-pressure steam sterilization equipment"),
    ("Centrifuge", "Laboratory centrifuge for sample preparation"),
    ("Blood Bank Refrigerator", "Temperature-controlled blood storage unit"),
    ("Incubator", "Neonatal care temperature-controlled incubator"),
    ("ECG Machine", "Electrocardiogram recording device"),
    ("Suction Machine", "Medical suction/aspiration device"),
    ("Oxygen Concentrator", "Portable oxygen generation device"),
    ("Chiller", "HVAC central cooling chiller plant"),
    ("Cooling Tower", "Heat rejection cooling tower"),
    ("Air Handling Unit", "HVAC air handling and conditioning unit"),
    ("Boiler", "Steam/hot water generation boiler"),
    ("Fire Pump", "Fire protection water pump system"),
    ("Transfer Switch", "Automatic transfer switch for backup power"),
    ("Transformer", "Electrical power transformer"),
    ("Switchgear", "Electrical power distribution switchgear"),
    ("Water Pump", "Domestic/process water pump"),
    ("Sewage Pump", "Wastewater/sewage pump system"),
    ("Generator Set", "Diesel/gas engine generator set"),
    ("Solar Panel Array", "Photovoltaic solar panel installation"),
    ("Battery Bank", "Energy storage battery bank system"),
    ("CCTV Camera", "Surveillance closed-circuit TV camera"),
    ("Access Control Panel", "Door access control electronic panel"),
    ("Fire Alarm Panel", "Addressable fire alarm control panel"),
    ("BMS Controller", "Building management system controller"),
    ("Pneumatic Tube Station", "Hospital pneumatic tube transport station"),
    ("Nurse Call Station", "Patient bedside nurse call terminal"),
    ("Medical Gas Outlet", "Wall-mounted medical gas outlet point"),
    ("Roof Exhaust Fan", "Rooftop exhaust ventilation fan"),
]

# Use existing IDs as parent references for hierarchy
parent_map = {
    "CT Scanner": "AC-0004", "X-Ray Machine": "AC-0004", "Ultrasound Machine": "AC-0004",
    "Ventilator": "AC-0004", "Patient Monitor": "AC-0004", "Infusion Pump": "AC-0004",
    "Defibrillator": "AC-0004", "Anesthesia Machine": "AC-0004", "Surgical Table": "AC-0004",
    "Autoclave": "AC-0004", "Centrifuge": "AC-0004", "Blood Bank Refrigerator": "AC-0004",
    "Incubator": "AC-0004", "ECG Machine": "AC-0004", "Suction Machine": "AC-0004",
    "Oxygen Concentrator": "AC-0004",
    "Chiller": "AC-0001", "Cooling Tower": "AC-0001", "Air Handling Unit": "AC-0001",
    "Boiler": "AC-0001", "Water Pump": "AC-0001", "Sewage Pump": "AC-0001",
    "Roof Exhaust Fan": "AC-0001",
    "Fire Pump": "AC-0002", "Transfer Switch": "AC-0002", "Transformer": "AC-0002",
    "Switchgear": "AC-0002", "Generator Set": "AC-0002", "Solar Panel Array": "AC-0002",
    "Battery Bank": "AC-0002", "Fire Alarm Panel": "AC-0002",
    "CCTV Camera": "AC-0005", "Access Control Panel": "AC-0005",
    "BMS Controller": "AC-0005", "Pneumatic Tube Station": "AC-0005",
    "Nurse Call Station": "AC-0005", "Medical Gas Outlet": "AC-0004",
}

new_ac_ids = []
for i, (name, desc) in enumerate(asset_class_new, start=14):
    acid = f"AC-{str(i).zfill(4)}"
    new_ac_ids.append(acid)
    parent = parent_map.get(name)
    cur.execute("""INSERT INTO asset_class (id, name, description, parent_asset_class, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (acid, name, desc, parent, NOW, NOW))
conn.commit()
all_asset_class_ids = asset_class_ids + new_ac_ids
print(f"  asset_class: inserted {len(asset_class_new)} new rows")

# ═══════════════════════════════════════════════════════
# 5. PROPERTY (currently 3 → add 47 more = 50 total)
# ═══════════════════════════════════════════════════════
print("Seeding property...")
property_new = [
    ("Voltage Rating", "Rated voltage of electrical equipment", "UOM-0001", "PT-0002"),
    ("Power Rating (kW)", "Rated power output in kilowatts", "UOM-0001", "PT-0002"),
    ("Amperage Rating", "Rated current draw in amperes", "UOM-0001", "PT-0002"),
    ("Operating Pressure (PSI)", "Normal operating pressure", "UOM-0001", "PT-0002"),
    ("Flow Rate (L/min)", "Fluid flow rate in liters per minute", "UOM-0001", "PT-0006"),
    ("Temperature Range (°C)", "Operating temperature range", "UOM-0001", "PT-0002"),
    ("Weight (kg)", "Equipment weight in kilograms", "UOM-0001", "PT-0006"),
    ("Dimensions (LxWxH)", "Physical dimensions", "UOM-0001", "PT-0001"),
    ("Manufacturer", "Equipment manufacturer name", "UOM-0001", "PT-0001"),
    ("Model Number", "Manufacturer model number", "UOM-0001", "PT-0001"),
    ("Serial Number", "Equipment serial number", "UOM-0001", "PT-0001"),
    ("Year of Manufacture", "Year the equipment was manufactured", "UOM-0001", "PT-0005"),
    ("Installation Date", "Date equipment was installed", "UOM-0001", "PT-0004"),
    ("Warranty Expiry", "Warranty expiration date", "UOM-0001", "PT-0004"),
    ("Capacity (BTU)", "Cooling/heating capacity", "UOM-0001", "PT-0002"),
    ("Refrigerant Type", "Type of refrigerant used", "UOM-0001", "PT-0001"),
    ("Fuel Type", "Type of fuel consumed", "UOM-0001", "PT-0001"),
    ("Fuel Tank Capacity (L)", "Fuel tank volume in liters", "UOM-0001", "PT-0006"),
    ("RPM Rating", "Rated rotational speed", "UOM-0001", "PT-0002"),
    ("Noise Level (dB)", "Sound output in decibels", "UOM-0001", "PT-0006"),
    ("Efficiency Rating (%)", "Energy efficiency percentage", "UOM-0001", "PT-0007"),
    ("IP Rating", "Ingress protection rating", "UOM-0001", "PT-0001"),
    ("Insulation Class", "Electrical insulation class", "UOM-0001", "PT-0001"),
    ("Phase", "Electrical phase (single/three)", "UOM-0001", "PT-0001"),
    ("Frequency (Hz)", "Electrical frequency", "UOM-0001", "PT-0002"),
    ("Head Pressure (m)", "Pump head pressure in meters", "UOM-0001", "PT-0006"),
    ("Tank Volume (L)", "Storage tank volume", "UOM-0001", "PT-0006"),
    ("Filter Size", "Air/fluid filter dimensions", "UOM-0001", "PT-0001"),
    ("Belt Size", "Drive belt specification", "UOM-0001", "PT-0001"),
    ("Bearing Type", "Type of bearing used", "UOM-0001", "PT-0001"),
    ("Lubrication Type", "Required lubrication specification", "UOM-0001", "PT-0001"),
    ("Calibration Due Date", "Next calibration due date", "UOM-0001", "PT-0004"),
    ("Accuracy Class", "Measurement accuracy classification", "UOM-0001", "PT-0001"),
    ("Resolution", "Display/imaging resolution", "UOM-0001", "PT-0001"),
    ("Battery Backup (hrs)", "Built-in battery duration", "UOM-0001", "PT-0006"),
    ("Alarm Setpoint High", "High alarm threshold value", "UOM-0001", "PT-0006"),
    ("Alarm Setpoint Low", "Low alarm threshold value", "UOM-0001", "PT-0006"),
    ("Max Operating Temp (°C)", "Maximum operating temperature", "UOM-0001", "PT-0006"),
    ("Min Operating Temp (°C)", "Minimum operating temperature", "UOM-0001", "PT-0006"),
    ("Certification Standard", "Compliance certification standard", "UOM-0001", "PT-0001"),
    ("Safety Class", "Equipment safety classification", "UOM-0001", "PT-0001"),
    ("Risk Category", "Risk assessment category", "UOM-0001", "PT-0001"),
    ("MTBF (hours)", "Mean time between failures", "UOM-0001", "PT-0005"),
    ("MTTR (hours)", "Mean time to repair", "UOM-0001", "PT-0005"),
    ("Replacement Cost", "Estimated replacement cost", "UOM-0001", "PT-0008"),
    ("Depreciation Rate (%)", "Annual depreciation percentage", "UOM-0001", "PT-0007"),
    ("Condition Score", "Current condition assessment score", "UOM-0001", "PT-0010"),
]

for i, (name, desc, uom, ptype) in enumerate(property_new, start=4):
    pid = f"PROP-{str(i).zfill(4)}"
    cur.execute("""INSERT INTO property (id, name, description, unit_of_measure, property_type, system, inactive, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (pid, name, desc, uom, ptype, False, False, NOW, NOW))
conn.commit()
print(f"  property: inserted {len(property_new)} new rows")

# ═══════════════════════════════════════════════════════
# 6. POSITION (currently 11 → add 39 more = 50 total)
# ═══════════════════════════════════════════════════════
print("Seeding position...")
position_new = [
    ("POS-ICU-BED-001", "ICU Bed Position 1", "AC-0004", "SYS-0001", "LOC-0005"),
    ("POS-ICU-BED-002", "ICU Bed Position 2", "AC-0004", "SYS-0002", "LOC-0005"),
    ("POS-ICU-BED-003", "ICU Bed Position 3", "AC-0004", "SYS-0003", "LOC-0005"),
    ("POS-ICU-VENT-001", "ICU Ventilator Station 1", "AC-0004", "SYS-0004", "LOC-0005"),
    ("POS-ICU-VENT-002", "ICU Ventilator Station 2", "AC-0004", "SYS-0005", "LOC-0005"),
    ("POS-ER-BAY-001", "Emergency Bay Position 1", "AC-0004", "SYS-0006", "LOC-0003"),
    ("POS-ER-BAY-002", "Emergency Bay Position 2", "AC-0004", "SYS-0007", "LOC-0003"),
    ("POS-ER-BAY-003", "Emergency Bay Position 3", "AC-0004", "SYS-0008", "LOC-0003"),
    ("POS-OR-TABLE-001", "OR Table Position 1", "AC-0004", "SYS-0009", "LOC-0007"),
    ("POS-OR-TABLE-002", "OR Table Position 2", "AC-0004", "SYS-0010", "LOC-0007"),
    ("POS-OR-ANES-001", "OR Anesthesia Station 1", "AC-0004", "SYS-0011", "LOC-0007"),
    ("POS-RAD-CT-001", "CT Scanner Position", "AC-0004", "SYS-0012", "LOC-0010"),
    ("POS-RAD-XRAY-001", "X-Ray Machine Position 1", "AC-0004", "SYS-0013", "LOC-0010"),
    ("POS-RAD-XRAY-002", "X-Ray Machine Position 2", "AC-0004", "SYS-0014", "LOC-0010"),
    ("POS-RAD-MRI-001", "MRI Scanner Position", "AC-0011", "SYS-0015", "LOC-0010"),
    ("POS-RAD-US-001", "Ultrasound Room Position 1", "AC-0004", "SYS-0016", "LOC-0010"),
    ("POS-LAB-CENT-001", "Lab Centrifuge Position 1", "AC-0004", "SYS-0017", "LOC-0012"),
    ("POS-LAB-CENT-002", "Lab Centrifuge Position 2", "AC-0004", "SYS-0018", "LOC-0012"),
    ("POS-LAB-FRIDGE-001", "Lab Refrigerator Position", "AC-0004", "SYS-0019", "LOC-0012"),
    ("POS-NICU-INC-001", "NICU Incubator Position 1", "AC-0004", "SYS-0020", "LOC-0008"),
    ("POS-NICU-INC-002", "NICU Incubator Position 2", "AC-0004", "SYS-0021", "LOC-0008"),
    ("POS-DIAL-STA-001", "Dialysis Station 1", "AC-0012", "SYS-0022", "LOC-0015"),
    ("POS-DIAL-STA-002", "Dialysis Station 2", "AC-0012", "SYS-0023", "LOC-0015"),
    ("POS-DIAL-STA-003", "Dialysis Station 3", "AC-0012", "SYS-0024", "LOC-0015"),
    ("POS-HVAC-AHU-001", "HVAC AHU Position Main Bldg", "AC-0001", "SYS-0025", "LOC-0001"),
    ("POS-HVAC-AHU-002", "HVAC AHU Position Wing A", "AC-0001", "SYS-0026", "LOC-0002"),
    ("POS-HVAC-CHI-001", "Chiller Plant Position 1", "AC-0001", "SYS-0027", "LOC-0001"),
    ("POS-HVAC-CT-001", "Cooling Tower Position", "AC-0001", "SYS-0028", "LOC-0001"),
    ("POS-ELEC-GEN-001", "Generator Position 1", "AC-0007", "SYS-0029", "LOC-0001"),
    ("POS-ELEC-GEN-002", "Generator Position 2", "AC-0007", "SYS-0030", "LOC-0001"),
    ("POS-ELEC-TX-001", "Transformer Position Main", "AC-0002", "SYS-0031", "LOC-0001"),
    ("POS-ELEC-UPS-001", "UPS Room Position 1", "AC-0008", "SYS-0032", "LOC-0001"),
    ("POS-ELEC-UPS-002", "UPS Room Position 2", "AC-0008", "SYS-0033", "LOC-0001"),
    ("POS-PLMB-PUMP-001", "Water Pump Position Main", "AC-0003", "SYS-0034", "LOC-0001"),
    ("POS-PLMB-PUMP-002", "Sewage Pump Position", "AC-0003", "SYS-0035", "LOC-0001"),
    ("POS-FIRE-PUMP-001", "Fire Pump House Position", "AC-0002", "SYS-0036", "LOC-0001"),
    ("POS-ELEV-A-001", "Elevator A Motor Room", "AC-0009", "SYS-0037", "LOC-0001"),
    ("POS-ELEV-B-001", "Elevator B Motor Room", "AC-0009", "SYS-0038", "LOC-0001"),
    ("POS-GAS-MAN-001", "Medical Gas Manifold Room", "AC-0010", "SYS-0039", "LOC-0001"),
]

for i, (tag, desc, ac, sys, loc) in enumerate(position_new, start=26):
    pid = f"POS-{str(i).zfill(4)}"
    site = random.choice(site_ids)
    cur.execute("""INSERT INTO position (id, position_tag, description, asset_class, system, location, site, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (pid, tag, desc, ac, sys, loc, site, NOW, NOW))
conn.commit()
print(f"  position: inserted {len(position_new)} new rows")

# ═══════════════════════════════════════════════════════
# 7. DISPOSED (currently 0 → add 50)
# ═══════════════════════════════════════════════════════
print("Seeding disposed...")
conditions = ["Damage", "Non Operational", "Missing Parts"]
methods = ["Scrap", "Sale", "Donation"]
statuses = ["Draft", "Submitted", "Approved", "Reverse"]
disposal_reasons = [
    "Beyond economic repair - replacement cost lower than repair",
    "Equipment obsolete - no spare parts available from manufacturer",
    "Failed safety inspection - cannot meet regulatory standards",
    "Exceeded useful life - performance degradation below acceptable levels",
    "Catastrophic motor failure - internal components seized",
    "Compressor failure - refrigerant leak detected, unrepairable",
    "Circuit board damage from power surge - no replacement PCB available",
    "Corrosion damage from chemical exposure - structural integrity compromised",
    "Software no longer supported by vendor - security vulnerability",
    "Repeated breakdowns - maintenance cost exceeds 60% replacement value",
    "Water damage from pipe burst - electrical components destroyed",
    "Physical damage from equipment collision during transport",
    "Calibration no longer achievable - out of specification permanently",
    "Radiation source depleted - requires specialized disposal",
    "Battery cells degraded - hazardous material containment required",
    "Screen/display failure - replacement screens discontinued",
    "Pump impeller worn beyond tolerance - cavitation damage",
    "Heat exchanger fouling - tubes collapsed and unrepairable",
    "Motor bearing failure - shaft misalignment caused catastrophic wear",
    "Control panel fire damage - complete rewiring uneconomical",
]

for i in range(1, 51):
    did = f"DSP-{str(i).zfill(4)}"
    asset = random.choice(asset_ids)
    cond = random.choice(conditions)
    ddate = rand_date(2024, 2026)
    reason = random.choice(disposal_reasons)
    method = random.choice(methods)
    status = random.choice(statuses)
    site = random.choice(site_ids)
    cur.execute("""INSERT INTO disposed (id, asset, condition, disposal_date, disposal_reason,
                   disposal_method, disposal_status, site, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (did, asset, cond, ddate, reason, method, status, site, NOW, NOW))
conn.commit()
print(f"  disposed: inserted 50 rows")

# ═══════════════════════════════════════════════════════
# 8. INCIDENT (currently 0 → add 50)
# ═══════════════════════════════════════════════════════
print("Seeding incident...")
incident_types = ["Equipment Damage", "Property Damage", "Fire/Explosion",
                  "Electrical Incident", "Safety Incident", "Theft/Vandalism", "Spill/Leak/Release"]
severities = ["Low", "Medium", "High", "Critical"]
incident_titles = [
    "CT scanner cooling system failure during patient scan",
    "Water leak from ceiling pipe in ICU Ward 3B",
    "Electrical short circuit in OR lighting panel",
    "Elevator B emergency stop triggered between floors",
    "Chemical spill in pathology laboratory",
    "Generator failed to start during power outage test",
    "MRI room quench event - helium venting activated",
    "Fire alarm false trigger in main kitchen exhaust",
    "Autoclave pressure safety valve malfunction",
    "Slip hazard from condensation under AHU-03",
    "CCTV camera fell from ceiling mount in parking",
    "Medical gas outlet leak detected in Ward 5A",
    "UPS battery overheating alarm in server room",
    "Broken glass in patient waiting area window",
    "Boiler room steam pipe leak near junction valve",
    "X-ray machine arm lock failure during positioning",
    "Fire extinguisher expired and discharged accidentally",
    "Sewage backup in basement utility corridor",
    "Roof leak during typhoon damaged ceiling tiles in ER",
    "Pneumatic tube station jammed causing sample delay",
    "Dialysis machine water treatment alarm triggered",
    "Operating room temperature exceeded 28°C during surgery",
    "Emergency exit door lock malfunction in Wing B",
    "Blood bank refrigerator temperature alarm - 8°C reading",
    "Nurse call system failure in pediatric ward",
    "Transformer oil leak detected at main substation",
    "Solar panel mounting bracket loose on rooftop",
    "Access control door failed to lock after hours",
    "Cafeteria grease trap overflow incident",
    "Patient bed rail mechanism jammed during adjustment",
    "Oxygen manifold pressure drop below safe threshold",
    "Chiller condenser tube leak requiring emergency shutdown",
    "Ventilator alarm malfunction - false low-pressure alert",
    "Radiology room lead shielding door hinge failure",
    "Pharmacy refrigerator power cord damage discovered",
    "Laundry dryer exhaust vent blockage caused high temp",
    "Water pump vibration alarm triggered in plant room",
    "BMS controller communication loss with 12 field devices",
    "Corridor lighting circuit breaker tripped during night shift",
    "NICU incubator humidity sensor drift detected",
    "Defibrillator battery failed routine charge test",
    "Kitchen hood fire suppression system inspection failure",
    "Rooftop exhaust fan belt snapped during operation",
    "Emergency lighting inverter failure during blackout test",
    "Switchgear arc flash near-miss during breaker racking",
    "Medical air compressor oil carry-over detected",
    "Parking lot bollard struck by delivery vehicle",
    "Waste management area biohazard container breach",
    "Cooling tower drift eliminator damaged by debris",
    "Rehabilitation pool chlorine dosing system malfunction",
]
immediate_actions = [
    "Area cordoned off and signage placed",
    "Equipment powered down and locked out",
    "Maintenance team dispatched immediately",
    "Patients relocated to alternate area",
    "Backup system activated",
    "Fire brigade notified as precaution",
    "Spill containment kit deployed",
    "Affected area evacuated per protocol",
    "Temporary repair applied to contain situation",
    "Security notified and area secured",
]
preventive_actions_list = [
    "Schedule comprehensive inspection of similar equipment",
    "Update preventive maintenance frequency for this asset class",
    "Install additional monitoring sensors",
    "Conduct staff retraining on equipment operation",
    "Review and update the standard operating procedure",
    "Install backup/redundant system components",
    "Upgrade equipment to current safety standards",
    "Implement additional safety barriers and guards",
    "Add this failure mode to the FMEA register",
    "Schedule a root cause analysis meeting",
]

for i in range(1, 51):
    iid = f"IR-{str(i).zfill(4)}"
    title = incident_titles[i - 1]
    desc = f"Detailed incident report: {title}. Investigation underway. " \
           f"Area has been inspected and documented with photographs."
    itype = random.choice(incident_types)
    idt = rand_datetime(2024, 2026)
    drep = idt[:10]
    loc = random.choice(location_ids)
    asset = random.choice(asset_ids)
    reported_by = random.choice(user_ids)
    site = random.choice(site_ids)
    dept = random.choice(department_ids)
    sev = random.choice(severities)
    imm_action = random.choice(immediate_actions)
    prev_action = random.choice(preventive_actions_list)
    assigned = random.choice(employee_ids)
    closed_date = None
    if random.random() < 0.4:
        closed_date = (datetime.strptime(drep, "%Y-%m-%d") + timedelta(days=random.randint(3, 30))).strftime("%Y-%m-%d")

    cur.execute("""INSERT INTO incident (id, title, description, incident_type, incident_datetime,
                   date_reported, location, asset, reported_by, site, department, severity,
                   immediate_action_taken, preventive_actions, assigned_to, closed_date, created_at, updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (iid, title, desc, itype, idt, drep, loc, asset, reported_by, site, dept, sev,
                 imm_action, prev_action, assigned, closed_date, NOW, NOW))
conn.commit()
print(f"  incident: inserted 50 rows")

# ═══════════════════════════════════════════════════════
# 9. INCIDENT EMPLOYEE (child records, ~2 per incident)
# ═══════════════════════════════════════════════════════
print("Seeding incident_employee...")
roles = ["Injured", "Witness", "Reporter", "Supervisor", "Investigator"]
injury_sevs = ["None", "Minor", "Moderate", "Severe"]
ie_count = 0
for i in range(1, 51):
    incident_id = f"IR-{str(i).zfill(4)}"
    num_employees = random.randint(1, 3)
    chosen_emps = random.sample(employee_ids, min(num_employees, len(employee_ids)))
    for j, emp in enumerate(chosen_emps):
        ie_count += 1
        ieid = f"IE-{str(ie_count).zfill(4)}"
        role = random.choice(roles)
        injured = role == "Injured"
        inj_sev = random.choice(["Minor", "Moderate"]) if injured else "None"
        inj_desc = "Minor injury sustained during incident" if injured else None
        ppe = random.choice([True, False])
        treatment = "First aid administered on site" if injured else None
        cur.execute("""INSERT INTO incident_employee (id, incident, employee, role_in_incident,
                       injured, injury_severity, injury_description, ppe_used, treatment, created_at, updated_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                    (ieid, incident_id, emp, role, injured, inj_sev, inj_desc, ppe, treatment, NOW, NOW))
conn.commit()
print(f"  incident_employee: inserted {ie_count} rows")

# ═══════════════════════════════════════════════════════
# 10. BREAKDOWN (currently 0 → add 50)
# ═══════════════════════════════════════════════════════
print("Seeding breakdown...")
breakdown_causes = [
    "Bearing failure due to insufficient lubrication",
    "Motor overheating from blocked ventilation ports",
    "Belt snapped due to excessive wear and misalignment",
    "Electrical contactor welded shut from arc damage",
    "Capacitor failure in variable frequency drive",
    "Compressor seized due to liquid slugging",
    "Sensor drift caused false readings and safety shutdown",
    "Control board failure from power surge",
    "Pump cavitation from low suction pressure",
    "Valve stuck in closed position due to corrosion buildup",
    "Fan blade fatigue crack caused imbalance",
    "Filter clogged causing high differential pressure alarm",
    "Thermostat malfunction caused temperature overshoot",
    "Relay failure in starter panel",
    "Gasket leak at flange connection",
    "Software glitch caused PLC lockup",
    "Wiring insulation breakdown from heat exposure",
    "Mechanical seal failure caused fluid leak",
    "Coupling misalignment after foundation settlement",
    "Battery cell failure in backup power system",
    "Coolant leak from corroded pipe fitting",
    "Pressure safety valve stuck open",
    "Motor winding insulation failure",
    "Hydraulic cylinder seal leak",
    "Gearbox oil contamination from moisture ingress",
]

for i in range(1, 51):
    bid = f"BD-{str(i).zfill(4)}"
    equip = random.choice(equipment_ids)
    bdate = rand_date(2024, 2026)
    hour_start = random.randint(0, 20)
    min_start = random.choice([0, 15, 30, 45])
    duration_hours = random.randint(1, 8)
    duration_mins = random.choice([0, 15, 30, 45])
    start_time = f"{hour_start:02d}:{min_start:02d}"
    end_h = hour_start + duration_hours
    end_m = min_start + duration_mins
    if end_m >= 60:
        end_h += 1
        end_m -= 60
    if end_h >= 24:
        end_h = 23
        end_m = 59
    end_time = f"{end_h:02d}:{end_m:02d}"
    cause = random.choice(breakdown_causes)
    cur.execute("""INSERT INTO breakdown (id, equipment, breakdown_date, start_time, end_time, cause, created_at, updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (bid, equip, bdate, start_time, end_time, cause, NOW, NOW))
conn.commit()
print(f"  breakdown: inserted 50 rows")

# ═══════════════════════════════════════════════════════
print("\n✅ All Asset Management seed data inserted successfully!")
cur.close()
conn.close()
