"""
Seed script for SPMC EAM – Procurement, Inventory, and Warehouse modules.
Also seeds employee_site data.
"""
import random
from datetime import date, datetime, timedelta
from sqlalchemy import text, create_engine

DB_URL = "postgresql://eam_spmc_user:CwSpmcSec2026mR7@localhost:5432/eam-spmc"
engine = create_engine(DB_URL)

# ── helpers ──────────────────────────────────────────────────────────────────
now = datetime.utcnow()

def ts():
    return now

def rand_date(start_days_ago=180, end_days_ago=1):
    d = date.today() - timedelta(days=random.randint(end_days_ago, start_days_ago))
    return d

def rand_dt(start_days_ago=180, end_days_ago=1):
    return datetime.combine(rand_date(start_days_ago, end_days_ago), datetime.min.time()) + timedelta(hours=random.randint(6,18), minutes=random.randint(0,59))

# ── Reference data ──────────────────────────────────────────────────────────
SITES = ["SITE-0001", "SITE-0002", "SITE-0003", "SITE-0004"]
DEPTS = [f"DEPT-{i:04d}" for i in range(1, 19)] + [f"DEPT-{i:04d}" for i in range(34, 39)]
EMPLOYEES = [f"EMP-{i:04d}" for i in [1,2,3,4,5,21,22,23,24,25]]
USERS = [
    "439d8021-7323-4e20-95bb-504a54db839c",
    "1e5d153b-6a90-4777-92e5-e5c4154236ab",
    "86261ca1-619f-4fd8-beb8-321c71c61e1d",
    "45a73aaa-6184-4003-b447-1ee121968bd5",
    "79c9c8c0-9d30-4ef8-9f4b-433c42c6d237",
    "62fcca4c-95f2-4222-9bea-0469428f69a7",
    "e5e5dad7-0e62-46ff-9b61-cbe75d874642",
    "e5665d57-07a4-43aa-8c73-094f46ccd68c",
    "e5e8204b-72d3-433b-9aed-0c15860e7aac",
    "d7562a34-6bf6-4673-84c2-3432efebf276",
    "e571c973-36d6-4347-a877-3667859f51e2",
    "ce00ecca-b47f-45f7-beb4-b6a6171fd536",
    "023c5ac6-a480-4bc7-a77d-078f453d73e0",
]
COST_CODES = [f"CC-{i:04d}" for i in range(1, 51)]
LOCATIONS = [f"LOC-{i:04d}" for i in range(1, 60)]
ASSET_CLASSES = [f"AC-{i:04d}" for i in range(1, 14)]
WF_STATES = ["Draft", "Submitted", "Approved", "Completed"]
ISSUE_TYPES = ["Work Order", "Department Request", "Emergency"]
RETURN_TYPES = ["Surplus", "Defective", "Incorrect Item"]
TRANSFER_TYPES = ["Store-to-Store", "Store-to-Location", "Location-to-Location", "Return-to-Vendor"]
VOUCHER_TYPES = ["Purchase Receipt", "Item Issue", "Item Return", "Inventory Adjustment", "Transfer"]

# Series start values (will be set from DB)
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
        conn.execute(text("INSERT INTO series (name, current) VALUES (:n, :c) ON CONFLICT (name) DO UPDATE SET current = :c"),
                     {"n": prefix, "c": cur})

# ── Hospital-relevant items for SPMC ────────────────────────────────────────
HOSPITAL_ITEMS = [
    ("Surgical Gloves (Box/100)", "Disposable sterile surgical gloves", "Consumable"),
    ("N95 Respirator Mask", "Particulate respirator mask", "Consumable"),
    ("IV Cannula 20G", "Intravenous cannula gauge 20", "Consumable"),
    ("Syringe 10ml", "Disposable syringe with needle", "Consumable"),
    ("Gauze Roll 4-inch", "Sterile gauze roll for wound care", "Consumable"),
    ("Foley Catheter 16Fr", "Indwelling urinary catheter", "Consumable"),
    ("Oxygen Regulator", "Medical oxygen flow regulator", "Equipment"),
    ("Pulse Oximeter Probe", "SpO2 finger probe sensor", "Equipment"),
    ("Blood Pressure Cuff (Adult)", "Reusable sphygmomanometer cuff", "Equipment"),
    ("ECG Electrode Pads (50pc)", "Disposable ECG monitoring electrodes", "Consumable"),
    ("Suture Kit Nylon 3-0", "Non-absorbable suture material", "Consumable"),
    ("Endotracheal Tube 7.5mm", "Cuffed endotracheal tube", "Consumable"),
    ("Defibrillator Pads (Adult)", "Replacement defibrillator pads", "Consumable"),
    ("Ventilator Filter HME", "Heat moisture exchanger filter", "Consumable"),
    ("Central Line Kit 7Fr", "Triple-lumen central venous catheter", "Consumable"),
    ("Ambu Bag (Adult)", "Manual resuscitation bag", "Equipment"),
    ("Laryngoscope Blade Mac 3", "Macintosh laryngoscope blade", "Equipment"),
    ("Suction Catheter 14Fr", "Tracheal suction catheter", "Consumable"),
    ("Wound Dressing Foam 10x10", "Foam wound dressing pad", "Consumable"),
    ("Surgical Drape (Sterile)", "Surgical drape sheet", "Consumable"),
    ("HVAC Filter HEPA 24x24", "High-efficiency particulate air filter", "Spare Part"),
    ("Chiller Compressor Belt", "Drive belt for chiller compressor", "Spare Part"),
    ("Fire Sprinkler Head", "Automatic fire sprinkler head", "Spare Part"),
    ("LED Panel Light 600x600", "Recessed LED ceiling panel 40W", "Spare Part"),
    ("UPS Battery 12V 7Ah", "Sealed lead-acid UPS battery", "Spare Part"),
    ("Elevator Door Roller", "Guide roller for elevator door", "Spare Part"),
    ("Water Pump Impeller 4-inch", "Replacement impeller for water pump", "Spare Part"),
    ("Boiler Safety Valve 2-inch", "Pressure relief safety valve", "Spare Part"),
    ("Pipe Fitting Elbow 1-inch SS", "Stainless steel pipe elbow", "Spare Part"),
    ("Generator Oil Filter", "Heavy-duty diesel generator oil filter", "Spare Part"),
    ("Medical Gas Outlet O2", "Oxygen wall outlet assembly", "Spare Part"),
    ("Autoclave Door Gasket", "Silicone seal gasket for autoclave", "Spare Part"),
    ("X-Ray Tube Insert", "Replacement X-ray tube insert assembly", "Spare Part"),
    ("CT Scanner Cooling Fan", "Axial cooling fan for CT scanner", "Spare Part"),
    ("Dialysis Machine Filter Set", "Replacement filter set for dialysis", "Spare Part"),
]

HOSPITAL_VENDORS = [
    "MedEquip Philippines Inc.",
    "Hospital Supplies Davao",
    "PhilMedical Trading Corp.",
    "Mindanao Surgical Supplies",
    "SterilTech Solutions PH",
    "BioMed Engineering Services",
    "Pacific Health Systems",
    "Davao Medical Distributors",
    "Southern Medical Instruments",
    "SPMC Pharmacy Supplies",
    "GreenCare Environmental Services",
    "Powerline Electrical Supply",
    "CoolAir HVAC Philippines",
    "GeneralParts Industrial Corp.",
    "AquaTech Plumbing Systems",
    "ElevaTech Service Philippines",
    "FireSafe Equipment Trading",
    "IT Warehouse Solutions PH",
    "Diagnostic Imaging Parts PH",
    "NephroTech Medical Systems",
    "CardioStream Devices PH",
    "OncoMed Supplies Inc.",
    "PediaCare Equipment Trading",
    "TraumaReady Medical Corp.",
    "CriticalCare Systems PH",
    "OutPatient Medical Supplies",
    "NeuroPsych Equipment PH",
    "PhysioCare Supplies Davao",
    "RadTech Parts and Service",
    "SterilePro Instruments PH",
    "OptiMed Laboratory Supplies",
    "WoundCare Solutions PH",
    "AnesthesiaTech PH Corp.",
    "GastroMed Supplies Davao",
    "ENT Medical Equipment PH",
    "OrthoMed Implants PH",
    "DentalQuip Philippines",
    "PulmoTech Respiratory PH",
    "RehabMed Equipment Trading",
    "LabTech Diagnostics PH",
]

ITEM_CLASSES = [
    ("Medical Consumables", "Disposable medical supplies", "Consumable", True),
    ("Surgical Instruments", "Reusable surgical instruments", "Equipment", True),
    ("HVAC Components", "Heating ventilation and air conditioning parts", "Spare Part", True),
    ("Electrical Components", "Electrical maintenance parts", "Spare Part", True),
    ("Plumbing Components", "Plumbing maintenance parts", "Spare Part", True),
    ("Biomedical Equipment Parts", "Biomedical device spare parts", "Equipment", True),
    ("IT Equipment", "Information technology equipment", "Equipment", True),
    ("Safety Equipment", "Fire safety and emergency equipment", "Equipment", True),
    ("Laboratory Supplies", "Laboratory consumables and reagents", "Consumable", True),
    ("Linen and Textiles", "Hospital linen and textile supplies", "Consumable", False),
    ("Cleaning Supplies", "Housekeeping and sanitation supplies", "Consumable", False),
    ("Office Supplies", "General office and admin supplies", "Consumable", False),
    ("Pharmaceutical Items", "Pharmacy and drug supplies", "Consumable", True),
    ("Diagnostic Imaging Parts", "Radiology equipment parts", "Spare Part", True),
    ("Patient Monitoring Parts", "Patient monitor accessories", "Equipment", True),
    ("Elevator Components", "Elevator maintenance parts", "Spare Part", True),
    ("Generator Components", "Diesel generator parts", "Spare Part", True),
    ("Medical Gas Parts", "Medical gas system components", "Spare Part", True),
    ("Sterilization Supplies", "Autoclave and sterilization items", "Consumable", True),
    ("Furniture and Fixtures", "Hospital furniture items", "Equipment", False),
    ("PPE Supplies", "Personal protective equipment", "Consumable", True),
    ("Respiratory Supplies", "Respiratory therapy consumables", "Consumable", True),
    ("IV Therapy Supplies", "Intravenous therapy items", "Consumable", True),
    ("Wound Care Products", "Wound dressing and care products", "Consumable", True),
    ("Catheter Supplies", "Catheter and drainage items", "Consumable", True),
    ("Anesthesia Supplies", "Anesthesia equipment and consumables", "Consumable", True),
    ("Dialysis Supplies", "Hemodialysis consumables", "Consumable", True),
    ("Orthopedic Supplies", "Orthopedic implants and supplies", "Consumable", True),
    ("Dental Supplies", "Dental equipment and consumables", "Consumable", True),
    ("Rehabilitation Equipment", "Physical therapy equipment parts", "Equipment", True),
    ("Waste Management Supplies", "Medical waste disposal items", "Consumable", False),
    ("Kitchen Equipment Parts", "Dietary department equipment parts", "Spare Part", False),
    ("Laundry Equipment Parts", "Laundry machinery spare parts", "Spare Part", False),
    ("Mortuary Supplies", "Mortuary and pathology items", "Consumable", False),
    ("Communication Equipment", "Phone and communication parts", "Equipment", False),
    ("CCTV and Security Parts", "Security system components", "Equipment", False),
    ("Water Treatment Parts", "Water treatment system components", "Spare Part", True),
    ("Solar Panel Components", "Solar energy system parts", "Spare Part", False),
    ("Building Materials", "General construction materials", "Spare Part", False),
    ("Transport Equipment Parts", "Ambulance and vehicle parts", "Spare Part", False),
    ("Surgical Lighting Parts", "Operating room light components", "Spare Part", True),
    ("Mattress and Bedding", "Hospital mattresses and bedding", "Equipment", False),
    ("Signage and Labels", "Hospital signage and label supplies", "Consumable", False),
    ("Paint and Coating", "Maintenance paint supplies", "Consumable", False),
    ("Hardware and Fasteners", "Nuts bolts and general hardware", "Spare Part", False),
    ("Lubrication Products", "Machine oils and lubricants", "Consumable", False),
    ("Welding Supplies", "Welding rods and consumables", "Consumable", False),
    ("Measurement Instruments", "Calibration and measurement tools", "Equipment", True),
    ("Disinfection Equipment", "UV and chemical disinfection devices", "Equipment", True),
    ("Pneumatic Components", "Compressed air system parts", "Spare Part", False),
]

UOM_LIST = [
    ("Piece", "PC"),
    ("Box", "BX"),
    ("Pack", "PK"),
    ("Liter", "LTR"),
    ("Kilogram", "KG"),
    ("Meter", "M"),
    ("Roll", "RL"),
    ("Set", "SET"),
    ("Bottle", "BTL"),
    ("Pair", "PR"),
    ("Dozen", "DZ"),
    ("Carton", "CTN"),
    ("Can", "CAN"),
    ("Gallon", "GAL"),
    ("Tube", "TB"),
    ("Sheet", "SHT"),
    ("Bag", "BAG"),
    ("Ream", "RM"),
    ("Drum", "DRM"),
    ("Ampule", "AMP"),
    ("Vial", "VL"),
    ("Spool", "SPL"),
    ("Foot", "FT"),
    ("Inch", "IN"),
    ("Unit", "UN"),
    ("Case", "CS"),
    ("Bundle", "BDL"),
    ("Gram", "G"),
    ("Milliliter", "ML"),
    ("Strip", "STRP"),
    ("Tablet", "TAB"),
    ("Capsule", "CAP"),
    ("Cartridge", "CART"),
    ("Syringe", "SYR"),
    ("Length", "LEN"),
    ("Pad", "PAD"),
    ("Kit", "KIT"),
    ("Tray", "TRY"),
    ("Cup", "CUP"),
    ("Jar", "JAR"),
    ("Sachet", "SACH"),
    ("Belt", "BLT"),
    ("Filter", "FLT"),
    ("Valve", "VLV"),
    ("Gasket", "GSK"),
    ("Bearing", "BRG"),
    ("Plate", "PLT"),
]

CURRENCIES = [
    ("US Dollar", "USD", 56.50),
    ("Euro", "EUR", 62.80),
    ("British Pound", "GBP", 72.90),
    ("Japanese Yen", "JPY", 0.38),
    ("Australian Dollar", "AUD", 37.20),
    ("Canadian Dollar", "CAD", 42.10),
    ("Singapore Dollar", "SGD", 42.80),
    ("Chinese Yuan", "CNY", 7.80),
    ("Korean Won", "KRW", 0.042),
    ("Thai Baht", "THB", 1.60),
    ("Malaysian Ringgit", "MYR", 12.90),
    ("Indonesian Rupiah", "IDR", 0.0036),
    ("Indian Rupee", "INR", 0.68),
    ("UAE Dirham", "AED", 15.40),
    ("Saudi Riyal", "SAR", 15.10),
    ("Swiss Franc", "CHF", 65.20),
    ("New Taiwan Dollar", "TWD", 1.80),
    ("Hong Kong Dollar", "HKD", 7.25),
    ("Vietnamese Dong", "VND", 0.0023),
    ("Brazilian Real", "BRL", 11.50),
    ("Mexican Peso", "MXN", 3.30),
    ("South Korean Won", "KRW2", 0.043),
    ("New Zealand Dollar", "NZD", 34.10),
    ("Swedish Krona", "SEK", 5.50),
    ("Norwegian Krone", "NOK", 5.40),
    ("Danish Krone", "DKK", 8.40),
    ("Polish Zloty", "PLN", 14.50),
    ("Czech Koruna", "CZK", 2.50),
    ("Turkish Lira", "TRY2", 1.70),
    ("South African Rand", "ZAR", 3.10),
    ("Egyptian Pound", "EGP", 1.16),
    ("Bangladeshi Taka", "BDT", 0.47),
    ("Pakistani Rupee", "PKR", 0.20),
    ("Sri Lankan Rupee", "LKR", 0.19),
    ("Myanmar Kyat", "MMK", 0.027),
    ("Cambodian Riel", "KHR", 0.014),
    ("Lao Kip", "LAK", 0.0026),
    ("Brunei Dollar", "BND", 42.90),
    ("Qatari Riyal", "QAR", 15.50),
    ("Kuwaiti Dinar", "KWD", 184.30),
    ("Bahraini Dinar", "BHD", 150.20),
    ("Omani Rial", "OMR", 147.00),
    ("Israeli Shekel", "ILS", 15.60),
    ("Jordanian Dinar", "JOD", 79.70),
    ("Lebanese Pound", "LBP", 0.00063),
    ("Kenyan Shilling", "KES", 0.44),
    ("Nigerian Naira", "NGN2", 0.036),
    ("Ghanaian Cedi", "GHS", 4.50),
]

STORE_NAMES = [
    ("Central Medical Store", "SITE-0001"),
    ("ICU Emergency Supplies", "SITE-0002"),
    ("Surgical Instruments Store", "SITE-0002"),
    ("Biomedical Engineering Store", "SITE-0002"),
    ("Pharmacy Warehouse", "SITE-0001"),
    ("Radiology Parts Store", "SITE-0004"),
    ("Facilities Maintenance Store", "SITE-0003"),
    ("HVAC Spare Parts Store", "SITE-0003"),
    ("Electrical Maintenance Store", "SITE-0003"),
    ("General Hospital Supplies", "SITE-0001"),
    ("Operating Room Supplies", "SITE-0002"),
    ("Laboratory Supplies Store", "SITE-0004"),
    ("IT Equipment Store", "SITE-0001"),
    ("Linen and Laundry Store", "SITE-0001"),
    ("Kitchen Supplies Store", "SITE-0001"),
    ("Waste Management Store", "SITE-0003"),
    ("Outpatient Supplies Store", "SITE-0001"),
    ("Pediatric Supplies Store", "SITE-0002"),
    ("Cardiology Supplies Store", "SITE-0002"),
    ("Oncology Supplies Store", "SITE-0002"),
    ("Nephrology Supplies Store", "SITE-0002"),
    ("Emergency Department Store", "SITE-0002"),
    ("Trauma Supplies Store", "SITE-0002"),
    ("Dental Equipment Store", "SITE-0001"),
    ("Rehabilitation Supplies Store", "SITE-0001"),
    ("Safety Equipment Store", "SITE-0003"),
    ("Generator Parts Store", "SITE-0003"),
    ("Plumbing Parts Store", "SITE-0003"),
    ("Elevator Parts Store", "SITE-0003"),
    ("Fire Safety Store", "SITE-0003"),
    ("Medical Gas Store", "SITE-0003"),
    ("Paint and Coating Store", "SITE-0003"),
    ("Welding Supplies Store", "SITE-0003"),
    ("Tool Crib", "SITE-0003"),
    ("Receiving Dock Store", "SITE-0001"),
    ("Quarantine Store", "SITE-0001"),
    ("Sterile Processing Store", "SITE-0002"),
    ("Anesthesia Supplies Store", "SITE-0002"),
    ("Respiratory Therapy Store", "SITE-0002"),
    ("Wound Care Store", "SITE-0002"),
    ("IV Therapy Store", "SITE-0002"),
    ("Mortuary Supplies Store", "SITE-0001"),
    ("Blood Bank Supplies Store", "SITE-0002"),
    ("Endoscopy Supplies Store", "SITE-0002"),
    ("Dialysis Supplies Store", "SITE-0002"),
    ("Nutrition Supplements Store", "SITE-0001"),
    ("PPE Storage Area", "SITE-0001"),
]

ZONES_PER_STORE = [
    "Receiving Zone", "Storage Zone A", "Storage Zone B", "High-Value Zone",
    "Bulk Storage Zone", "Refrigerated Zone", "Hazardous Materials Zone",
    "Quarantine Zone", "Outbound Zone", "Returns Zone",
]

BIN_NAMES = [
    ("Rack A", "Shelf 1", "Bin A1-01"), ("Rack A", "Shelf 2", "Bin A1-02"),
    ("Rack A", "Shelf 3", "Bin A1-03"), ("Rack B", "Shelf 1", "Bin B1-01"),
    ("Rack B", "Shelf 2", "Bin B1-02"), ("Rack B", "Shelf 3", "Bin B1-03"),
    ("Rack C", "Shelf 1", "Bin C1-01"), ("Rack C", "Shelf 2", "Bin C1-02"),
    ("Rack D", "Shelf 1", "Bin D1-01"), ("Rack D", "Shelf 2", "Bin D1-02"),
]

REASON_CODES = [
    ("DAMAGED", "Item damaged during handling", "Adjustment"),
    ("EXPIRED", "Item past expiration date", "Adjustment"),
    ("MISSING", "Item missing from inventory", "Adjustment"),
    ("RETURNED", "Item returned by department", "Return"),
    ("SURPLUS", "Excess stock from work order", "Return"),
    ("INCORRECT", "Incorrect item issued", "Return"),
    ("DEFECTIVE", "Item found defective on inspection", "Adjustment"),
    ("RECOUNT", "Variance found during stock count", "Adjustment"),
    ("TRANSFER_IN", "Received from inter-store transfer", "Transfer"),
    ("TRANSFER_OUT", "Sent via inter-store transfer", "Transfer"),
    ("RECEIVED", "New stock received from vendor", "Receipt"),
    ("ISSUED", "Issued to work order or department", "Issue"),
    ("DONATED", "Donated items received", "Receipt"),
    ("DISPOSED", "Items sent for proper disposal", "Adjustment"),
    ("CALIBRATED", "Equipment calibrated and returned", "Return"),
    ("CONSUMED", "Consumed during procedure", "Issue"),
    ("LOST", "Item lost or unaccounted for", "Adjustment"),
    ("STOLEN", "Item reported stolen", "Adjustment"),
    ("RECALLED", "Manufacturer recall", "Adjustment"),
    ("SAMPLE", "Sample item for evaluation", "Receipt"),
    ("WARRANTY", "Warranty replacement received", "Receipt"),
    ("REFURBISHED", "Refurbished item returned to stock", "Return"),
    ("QC_REJECT", "Quality control rejection", "Adjustment"),
    ("EMERGENCY", "Emergency issue without PR", "Issue"),
    ("RECLASSIFIED", "Item reclassified to different class", "Adjustment"),
    ("OBSOLETE", "Item declared obsolete", "Adjustment"),
    ("SEASONAL", "Seasonal stock adjustment", "Adjustment"),
    ("VENDOR_CREDIT", "Credit received from vendor", "Return"),
    ("BREAKAGE", "Item broken during storage", "Adjustment"),
    ("CONTAMINATED", "Item contaminated and discarded", "Adjustment"),
    ("WRITE_OFF", "Officially written off records", "Adjustment"),
    ("REDISTRIBUTION", "Redistributed to another facility", "Transfer"),
    ("BATCH_VARIANCE", "Batch quantity variance", "Adjustment"),
    ("UNIT_CONVERSION", "Unit of measure conversion adjustment", "Adjustment"),
    ("CYCLE_COUNT", "Cycle count adjustment", "Adjustment"),
    ("OPENING_BALANCE", "Opening balance entry", "Adjustment"),
    ("REPAIR_RETURN", "Item returned from repair", "Return"),
    ("EXCHANGE", "Item exchanged with vendor", "Return"),
    ("TESTING", "Item used for testing", "Issue"),
    ("DONATION_OUT", "Item donated to other facility", "Transfer"),
    ("DECAY", "Natural decay or evaporation", "Adjustment"),
    ("SYSTEM_ADJUSTMENT", "System generated adjustment", "Adjustment"),
    ("PHYSICAL_COUNT", "Physical count adjustment", "Adjustment"),
    ("PRODUCTION", "Produced by internal workshop", "Receipt"),
    ("CONSOLIDATION", "Stock consolidation adjustment", "Adjustment"),
    ("SPLITTING", "Stock splitting adjustment", "Adjustment"),
    ("RELABEL", "Item relabeled/retagged", "Adjustment"),
    ("INSURANCE_CLAIM", "Insurance claim replacement", "Receipt"),
    ("GRANT_FUNDED", "Items from grant/funded project", "Receipt"),
    ("GOVERNMENT_SUPPLY", "Government supplied items", "Receipt"),
]


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main():
    with engine.begin() as conn:
        load_series(conn)

        # ── Load actual reference IDs from DB ───────────────────────────
        COST_CODES = [r[0] for r in conn.execute(text("SELECT id FROM cost_code ORDER BY id")).fetchall()]
        EMPLOYEES = [r[0] for r in conn.execute(text("SELECT id FROM employee ORDER BY id")).fetchall()]
        LOCATIONS = [r[0] for r in conn.execute(text("SELECT id FROM location ORDER BY id")).fetchall()]
        ACCOUNTS = [r[0] for r in conn.execute(text("SELECT id FROM account ORDER BY id")).fetchall()]
        print(f"Loaded references: {len(COST_CODES)} cost_codes, {len(EMPLOYEES)} employees, {len(LOCATIONS)} locations, {len(ACCOUNTS)} accounts")

        # ── 1. Employee Site ────────────────────────────────────────────
        print("Seeding employee_site ...")
        emp_site_data = []
        for emp in EMPLOYEES:
            # Each employee gets 1-3 site assignments
            assigned_sites = random.sample(SITES, k=random.randint(1, 3))
            for i, site in enumerate(assigned_sites):
                eid = next_id("EMPS")
                emp_site_data.append({
                    "id": eid,
                    "employee": emp,
                    "site": site,
                    "department": random.choice(DEPTS),
                    "default": (i == 0),
                    "created_at": ts(), "updated_at": ts(),
                })
        if emp_site_data:
            conn.execute(text("""INSERT INTO employee_site (id, employee, site, department, "default", created_at, updated_at)
                VALUES (:id, :employee, :site, :department, :default, :created_at, :updated_at)"""), emp_site_data)
        print(f"  → {len(emp_site_data)} employee_site records")

        # ── 2. Vendors (add 40 to existing 10) ─────────────────────────
        print("Seeding vendors ...")
        vendor_data = []
        for vname in HOSPITAL_VENDORS:
            vid = next_id("VND")
            vendor_data.append({
                "id": vid, "vendor_name": vname,
                "site": random.choice(SITES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("INSERT INTO vendor (id, vendor_name, site, created_at, updated_at) VALUES (:id, :vendor_name, :site, :created_at, :updated_at)"), vendor_data)
        ALL_VENDORS = [r[0] for r in conn.execute(text("SELECT id FROM vendor ORDER BY id")).fetchall()]
        print(f"  → {len(vendor_data)} new vendors (total {len(ALL_VENDORS)})")

        # ── 3. Item Classes ─────────────────────────────────────────────
        print("Seeding item_class ...")
        ic_data = []
        for (name, desc, itype, serialized) in ITEM_CLASSES:
            icid = next_id("ITMCL")
            ic_data.append({
                "id": icid, "item_class_name": name, "description": desc,
                "item_class_type": itype, "asset_class": random.choice(ASSET_CLASSES) if serialized else None,
                "parent_item_class": None, "default_uom": None,
                "valuation_method": random.choice(["FIFO", "Average", "Standard"]),
                "account": None, "inventory_tracking": True,
                "is_serialized": serialized, "is_active": True,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO item_class (id, item_class_name, description, item_class_type, asset_class,
            parent_item_class, default_uom, valuation_method, account, inventory_tracking, is_serialized, is_active,
            created_at, updated_at) VALUES (:id, :item_class_name, :description, :item_class_type, :asset_class,
            :parent_item_class, :default_uom, :valuation_method, :account, :inventory_tracking, :is_serialized, :is_active,
            :created_at, :updated_at)"""), ic_data)
        ALL_ITEM_CLASSES = [d["id"] for d in ic_data]
        print(f"  → {len(ic_data)} item classes")

        # ── 4. Unit of Measure (add 47 to existing 3) ──────────────────
        print("Seeding unit_of_measure ...")
        uom_data = []
        for (name, short) in UOM_LIST:
            uid = next_id("UOM")
            uom_data.append({
                "id": uid, "name": name, "short_name": short,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("INSERT INTO unit_of_measure (id, name, short_name, created_at, updated_at) VALUES (:id, :name, :short_name, :created_at, :updated_at)"), uom_data)
        ALL_UOMS = [r[0] for r in conn.execute(text("SELECT id FROM unit_of_measure ORDER BY id")).fetchall()]
        print(f"  → {len(uom_data)} new UOMs (total {len(ALL_UOMS)})")

        # ── 5. Currency (add 48 to existing 2) ─────────────────────────
        print("Seeding currency ...")
        cur_data = []
        for (name, sym, rate) in CURRENCIES:
            cid = next_id("CUR")
            cur_data.append({
                "id": cid, "currency_name": name, "symbol": sym,
                "conversion_factor": rate, "active": True,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("INSERT INTO currency (id, currency_name, symbol, conversion_factor, active, created_at, updated_at) VALUES (:id, :currency_name, :symbol, :conversion_factor, :active, :created_at, :updated_at)"), cur_data)
        ALL_CURRENCIES = [r[0] for r in conn.execute(text("SELECT id FROM currency ORDER BY id")).fetchall()]
        print(f"  → {len(cur_data)} new currencies (total {len(ALL_CURRENCIES)})")

        # ── 6. Reason Codes ─────────────────────────────────────────────
        print("Seeding reason_code ...")
        rc_data = []
        for (code, desc, mvtype) in REASON_CODES:
            rcid = next_id("RCD")
            rc_data.append({
                "id": rcid, "code": code, "description": desc,
                "movement_type": mvtype,
                "default_debit_account": None, "default_credit_account": None,
                "approval_threshold": random.choice([None, 10000, 50000, 100000]),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO reason_code (id, code, description, movement_type,
            default_debit_account, default_credit_account, approval_threshold, created_at, updated_at)
            VALUES (:id, :code, :description, :movement_type, :default_debit_account, :default_credit_account,
            :approval_threshold, :created_at, :updated_at)"""), rc_data)
        ALL_REASON_CODES = [d["id"] for d in rc_data]
        print(f"  → {len(rc_data)} reason codes")

        # ── 7. Stores (add 47 to existing 3) ───────────────────────────
        print("Seeding stores ...")
        store_data = []
        for (sname, ssite) in STORE_NAMES:
            sid = next_id("STR")
            store_data.append({
                "id": sid, "store_name": sname,
                "location": random.choice(LOCATIONS),
                "location_name": sname,
                "site": ssite,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("INSERT INTO store (id, store_name, location, location_name, site, created_at, updated_at) VALUES (:id, :store_name, :location, :location_name, :site, :created_at, :updated_at)"), store_data)
        ALL_STORES = [r[0] for r in conn.execute(text("SELECT id FROM store ORDER BY id")).fetchall()]
        print(f"  → {len(store_data)} new stores (total {len(ALL_STORES)})")

        # ── 8. Zones ───────────────────────────────────────────────────
        print("Seeding zones ...")
        zone_data = []
        zone_map = {}  # store_id -> [zone_ids]
        for store_row in store_data[:10]:  # Zones for first 10 new stores
            for zname in random.sample(ZONES_PER_STORE, k=random.randint(3, 6)):
                zid = next_id("ZN")
                zone_data.append({
                    "id": zid, "zone_name": zname,
                    "store": store_row["id"],
                    "store_name": store_row["store_name"],
                    "site": store_row["site"],
                    "created_at": ts(), "updated_at": ts(),
                })
                zone_map.setdefault(store_row["id"], []).append(zid)
        if zone_data:
            conn.execute(text("INSERT INTO zone (id, zone_name, store, store_name, site, created_at, updated_at) VALUES (:id, :zone_name, :store, :store_name, :site, :created_at, :updated_at)"), zone_data)
        ALL_ZONES = [d["id"] for d in zone_data]
        print(f"  → {len(zone_data)} zones")

        # ── 9. Bins ────────────────────────────────────────────────────
        print("Seeding bins ...")
        bin_data = []
        for store_row in store_data[:10]:
            for (rack, shelf, bname) in random.sample(BIN_NAMES, k=min(5, len(BIN_NAMES))):
                bid = next_id("BIN")
                bin_data.append({
                    "id": bid, "rack_name": rack, "shelf_name": shelf,
                    "bin_name": bname,
                    "store": store_row["id"],
                    "store_name": store_row["store_name"],
                    "site": store_row["site"],
                    "created_at": ts(), "updated_at": ts(),
                })
        if bin_data:
            conn.execute(text("INSERT INTO bin (id, rack_name, shelf_name, bin_name, store, store_name, site, created_at, updated_at) VALUES (:id, :rack_name, :shelf_name, :bin_name, :store, :store_name, :site, :created_at, :updated_at)"), bin_data)
        ALL_BINS = [d["id"] for d in bin_data]
        print(f"  → {len(bin_data)} bins")

        # ── 10. Items (add 35 to existing 15) ──────────────────────────
        print("Seeding items ...")
        item_data = []
        for (iname, idesc, itype) in HOSPITAL_ITEMS:
            iid = next_id("ITM")
            item_data.append({
                "id": iid, "item_name": iname, "description": idesc,
                "item_class": random.choice(ALL_ITEM_CLASSES),
                "item_type": itype,
                "abc_code": random.choice(["A", "B", "C"]),
                "expense_account": None, "inventory_adjustment_account": None,
                "primary_vendor": random.choice(ALL_VENDORS),
                "asset_class": random.choice(ASSET_CLASSES) if itype == "Equipment" else None,
                "uom": random.choice(ALL_UOMS),
                "actual_qty_on_hand": random.randint(10, 500),
                "available_capacity": random.randint(5, 400),
                "unit_cost": round(random.uniform(50, 25000), 2),
                "reserved_capacity": random.randint(0, 50),
                "is_serialized": (itype == "Equipment"),
                "inspection_required": random.choice([True, False]),
                "is_equipment": (itype == "Equipment"),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO item (id, item_name, description, item_class, item_type, abc_code,
            expense_account, inventory_adjustment_account, primary_vendor, asset_class, uom,
            actual_qty_on_hand, available_capacity, unit_cost, reserved_capacity,
            is_serialized, inspection_required, is_equipment, created_at, updated_at)
            VALUES (:id, :item_name, :description, :item_class, :item_type, :abc_code,
            :expense_account, :inventory_adjustment_account, :primary_vendor, :asset_class, :uom,
            :actual_qty_on_hand, :available_capacity, :unit_cost, :reserved_capacity,
            :is_serialized, :inspection_required, :is_equipment, :created_at, :updated_at)"""), item_data)
        ALL_ITEMS = [r[0] for r in conn.execute(text("SELECT id FROM item ORDER BY id")).fetchall()]
        ITEM_NAMES = {d["id"]: d["item_name"] for d in item_data}
        # Add existing items to name map
        existing_items_map = {
            "ITM-0001": "Bearing 6205", "ITM-0002": "Motor Oil 5W-30",
            "ITM-0003": "Pump Seal Kit", "ITM-0004": "Electric Motor 5HP",
            "ITM-0005": "Centrifugal Pump",
        }
        ITEM_NAMES.update(existing_items_map)
        print(f"  → {len(item_data)} new items (total {len(ALL_ITEMS)})")

        # ── 11. Inventory (add 47 to existing 3) with actual_inv & available_inv ──
        print("Seeding inventory ...")
        inv_data = []
        for irow in item_data:
            invid = next_id("INV")
            actual = random.randint(10, 500)
            reserved = random.randint(0, min(20, actual))
            available = actual - reserved
            store = random.choice(ALL_STORES)
            zones_for_store = zone_map.get(store, [])
            inv_data.append({
                "id": invid,
                "workflow_state": None,
                "transaction_type": None,
                "date": rand_date(30, 1),
                "assigned_to": None,
                "serial_number": f"SN-{random.randint(100000, 999999)}" if irow["is_serialized"] else None,
                "financial_asset_number": None,
                "site": random.choice(SITES),
                "location": random.choice(LOCATIONS),
                "location_name": irow["item_name"][:50],
                "store_location": store,
                "zone": random.choice(zones_for_store) if zones_for_store else None,
                "bin_location": random.choice(ALL_BINS) if ALL_BINS else None,
                "item": irow["id"],
                "item_type": irow["item_type"],
                "item_name": irow["item_name"],
                "asset_tag": None,
                "unit_of_measure": irow["uom"],
                "asset": None,
                "base_unit_cost": irow["unit_cost"],
                "actual_inv": actual,
                "available_inv": available,
                "reserved_inv": reserved,
                "freeze": False,
                "warn": (actual < 20),
                "created_at": ts(), "updated_at": ts(),
            })
        # Also add 15 more for existing items to reach 50+
        existing_item_ids = [itm for itm in ALL_ITEMS if itm not in ITEM_NAMES]
        for itm in existing_item_ids[:15]:
            invid = next_id("INV")
            actual = random.randint(20, 300)
            reserved = random.randint(0, min(15, actual))
            available = actual - reserved
            store = random.choice(ALL_STORES)
            zones_for_store = zone_map.get(store, [])
            inv_data.append({
                "id": invid,
                "workflow_state": None,
                "transaction_type": None,
                "date": rand_date(60, 1),
                "assigned_to": None,
                "serial_number": None,
                "financial_asset_number": None,
                "site": random.choice(SITES),
                "location": random.choice(LOCATIONS),
                "location_name": None,
                "store_location": store,
                "zone": random.choice(zones_for_store) if zones_for_store else None,
                "bin_location": random.choice(ALL_BINS) if ALL_BINS else None,
                "item": itm,
                "item_type": None,
                "item_name": ITEM_NAMES.get(itm, f"Item {itm}"),
                "asset_tag": None,
                "unit_of_measure": random.choice(ALL_UOMS),
                "asset": None,
                "base_unit_cost": round(random.uniform(100, 15000), 2),
                "actual_inv": actual,
                "available_inv": available,
                "reserved_inv": reserved,
                "freeze": False,
                "warn": (actual < 25),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO inventory (id, workflow_state, transaction_type, date, assigned_to,
            serial_number, financial_asset_number, site, location, location_name, store_location,
            zone, bin_location, item, item_type, item_name, asset_tag, unit_of_measure, asset,
            base_unit_cost, actual_inv, available_inv, reserved_inv, "freeze", warn,
            created_at, updated_at)
            VALUES (:id, :workflow_state, :transaction_type, :date, :assigned_to,
            :serial_number, :financial_asset_number, :site, :location, :location_name, :store_location,
            :zone, :bin_location, :item, :item_type, :item_name, :asset_tag, :unit_of_measure, :asset,
            :base_unit_cost, :actual_inv, :available_inv, :reserved_inv, :freeze, :warn,
            :created_at, :updated_at)"""), inv_data)
        ALL_INVENTORY = [d["id"] for d in inv_data] + ["INV-0001", "INV-0002", "INV-0003"]
        print(f"  → {len(inv_data)} new inventory records (total {len(ALL_INVENTORY)})")

        # Also update existing 3 inventory records to have actual/available values
        conn.execute(text("""UPDATE inventory SET actual_inv = 150, available_inv = 130, reserved_inv = 20,
            date = :d, warn = false WHERE id = 'INV-0001'"""), {"d": rand_date(30, 1)})
        conn.execute(text("""UPDATE inventory SET actual_inv = 85, available_inv = 75, reserved_inv = 10,
            date = :d, warn = false WHERE id = 'INV-0002'"""), {"d": rand_date(30, 1)})
        conn.execute(text("""UPDATE inventory SET actual_inv = 200, available_inv = 180, reserved_inv = 20,
            date = :d, warn = false WHERE id = 'INV-0003'"""), {"d": rand_date(30, 1)})
        print("  → Updated existing 3 inventory records with actual/available values")

        # ── 12. Purchase Requests (add 45 to existing 5) ───────────────
        print("Seeding purchase_requests ...")
        pr_data = []
        pr_line_data = []
        pr_descriptions = [
            "PR - Surgical gloves and N95 masks for ER",
            "PR - IV cannulas and syringes for ICU",
            "PR - ECG electrodes and pulse ox probes",
            "PR - HVAC filters for Main Building",
            "PR - UPS batteries for server room",
            "PR - Elevator maintenance parts",
            "PR - Generator oil filters replacement",
            "PR - Medical gas outlet assemblies",
            "PR - Autoclave gaskets for CSSD",
            "PR - X-ray tube replacement parts",
            "PR - Dialysis machine filter sets",
            "PR - CT scanner cooling components",
            "PR - Foley catheters and suction sets",
            "PR - Ventilator HME filters",
            "PR - Central line kits for ICU",
            "PR - Defibrillator pads restock",
            "PR - Wound dressings and gauze",
            "PR - Surgical drapes for OR",
            "PR - Fire sprinkler heads replacement",
            "PR - LED panel lights for wards",
            "PR - Boiler safety valves inspection set",
            "PR - Water pump impellers maintenance",
            "PR - Pipe fittings for plumbing repair",
            "PR - Ambu bags for emergency carts",
            "PR - Laryngoscope blades restock",
            "PR - Suture kits nylon 3-0 bulk order",
            "PR - Endotracheal tubes various sizes",
            "PR - Blood pressure cuffs replacement",
            "PR - Oxygen regulators for ward stations",
            "PR - Chiller compressor belts",
            "PR - Laboratory reagent supplies quarterly",
            "PR - Dental equipment consumables",
            "PR - Rehabilitation therapy supplies",
            "PR - PPE supplies monthly restock",
            "PR - Pharmacy warehouse supplies",
            "PR - Kitchen equipment parts",
            "PR - Laundry equipment belts",
            "PR - Waste management disposal supplies",
            "PR - Radiology consumables quarterly",
            "PR - IT equipment replacement parts",
            "PR - Biomedical calibration supplies",
            "PR - Orthopedic supplies quarterly",
            "PR - Anesthesia consumables restock",
            "PR - Respiratory therapy filters",
            "PR - Cardiac monitoring supplies",
        ]
        for i, desc in enumerate(pr_descriptions):
            prid = next_id("PR")
            site = random.choice(SITES)
            dept = random.choice(DEPTS)
            date_req = rand_date(120, 5)
            pr_data.append({
                "id": prid,
                "workflow_state": random.choice(["Approved", "Submitted", "Draft"]),
                "date_requested": date_req,
                "pr_description": desc,
                "requestor": random.choice(EMPLOYEES),
                "requestor_name": None,
                "due_date": date_req + timedelta(days=random.randint(7, 30)),
                "work_activity_id": None,
                "maintenance_request": None,
                "reject_reason": None,
                "site": site,
                "department": dept,
                "cost_code": random.choice(COST_CODES),
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-3 lines per PR
            for ln in range(random.randint(1, 3)):
                prlid = next_id("PRL")
                itm = random.choice(ALL_ITEMS)
                qty = random.randint(5, 200)
                ucost = round(random.uniform(50, 15000), 2)
                pr_line_data.append({
                    "id": prlid,
                    "workflow_state": "Approved",
                    "purchase_request": prid,
                    "financial_asset_number": None,
                    "row_no": ln + 1,
                    "item": itm,
                    "item_description": ITEM_NAMES.get(itm, f"Item {itm}"),
                    "unit_of_measure": random.choice(ALL_UOMS),
                    "unit_cost": ucost,
                    "base_currency": "CUR-0005",
                    "qty_required": qty,
                    "total_line_amount": round(ucost * qty, 2),
                    "account_code": None,
                    "cost_code": random.choice(COST_CODES),
                    "site": site,
                    "department": dept,
                    "vendor": random.choice(ALL_VENDORS),
                    "po_num": None,
                    "date_required": date_req + timedelta(days=random.randint(7, 21)),
                    "qty_received": 0,
                    "base_currency_unit": None,
                    "base_currency_line_amount": None,
                    "conversion_factor": None,
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO purchase_request (id, workflow_state, date_requested, pr_description,
            requestor, requestor_name, due_date, work_activity_id, maintenance_request, reject_reason,
            site, department, cost_code, created_at, updated_at)
            VALUES (:id, :workflow_state, :date_requested, :pr_description, :requestor, :requestor_name,
            :due_date, :work_activity_id, :maintenance_request, :reject_reason, :site, :department, :cost_code,
            :created_at, :updated_at)"""), pr_data)
        conn.execute(text("""INSERT INTO purchase_request_line (id, workflow_state, purchase_request, financial_asset_number,
            row_no, item, item_description, unit_of_measure, unit_cost, base_currency, qty_required,
            total_line_amount, account_code, cost_code, site, department, vendor, po_num, date_required,
            qty_received, base_currency_unit, base_currency_line_amount, conversion_factor,
            created_at, updated_at)
            VALUES (:id, :workflow_state, :purchase_request, :financial_asset_number, :row_no, :item,
            :item_description, :unit_of_measure, :unit_cost, :base_currency, :qty_required,
            :total_line_amount, :account_code, :cost_code, :site, :department, :vendor, :po_num,
            :date_required, :qty_received, :base_currency_unit, :base_currency_line_amount, :conversion_factor,
            :created_at, :updated_at)"""), pr_line_data)
        ALL_PR = [d["id"] for d in pr_data]
        ALL_PRL = [d["id"] for d in pr_line_data]
        print(f"  → {len(pr_data)} purchase requests, {len(pr_line_data)} PR lines")

        # ── 13. Request for Quotations ──────────────────────────────────
        print("Seeding RFQs ...")
        rfq_data = []
        rfq_line_data = []
        for i in range(50):
            rfqid = next_id("RFQ")
            pr = random.choice(ALL_PR)
            vendor = random.choice(ALL_VENDORS)
            date_issue = rand_date(90, 5)
            rfq_data.append({
                "id": rfqid,
                "workflow_state": random.choice(["Issued", "Received", "Awarded", "Closed"]),
                "purchase_request": pr,
                "generated_by": random.choice(EMPLOYEES),
                "supplier": vendor,
                "date_issue": date_issue,
                "due_date": date_issue + timedelta(days=random.randint(5, 15)),
                "requestor": random.choice(EMPLOYEES),
                "awarded_vendor": vendor if random.random() > 0.3 else None,
                "terms_and_conditions": "Standard SPMC procurement terms apply. Delivery within 15 business days." if random.random() > 0.5 else None,
                "remarks": None,
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-4 RFQ lines
            for ln in range(random.randint(1, 4)):
                rfqlid = next_id("RFQL")
                itm = random.choice(ALL_ITEMS)
                rfq_line_data.append({
                    "id": rfqlid,
                    "rfq_id": rfqid,
                    "pr_line": random.choice(ALL_PRL) if ALL_PRL else None,
                    "item": itm,
                    "item_description": ITEM_NAMES.get(itm, f"Item {itm}"),
                    "quantity": random.randint(5, 100),
                    "price": round(random.uniform(100, 20000), 2),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO request_for_quotation (id, workflow_state, purchase_request, generated_by,
            supplier, date_issue, due_date, requestor, awarded_vendor, terms_and_conditions, remarks,
            created_at, updated_at)
            VALUES (:id, :workflow_state, :purchase_request, :generated_by, :supplier, :date_issue, :due_date,
            :requestor, :awarded_vendor, :terms_and_conditions, :remarks, :created_at, :updated_at)"""), rfq_data)
        conn.execute(text("""INSERT INTO rfq_line (id, rfq_id, pr_line, item, item_description, quantity, price,
            created_at, updated_at)
            VALUES (:id, :rfq_id, :pr_line, :item, :item_description, :quantity, :price,
            :created_at, :updated_at)"""), rfq_line_data)
        ALL_RFQS = [d["id"] for d in rfq_data]
        print(f"  → {len(rfq_data)} RFQs, {len(rfq_line_data)} RFQ lines")

        # ── 14. Purchase Orders (add 45 to existing 5) ─────────────────
        print("Seeding purchase_orders ...")
        po_data = []
        po_line_data = []
        for i in range(45):
            poid = next_id("PO")
            vendor = random.choice(ALL_VENDORS)
            site = random.choice(SITES)
            dept = random.choice(DEPTS)
            date_ord = rand_date(90, 3)
            total = round(random.uniform(5000, 500000), 2)
            po_data.append({
                "id": poid,
                "workflow_state": random.choice(["Approved", "Submitted", "Completed"]),
                "source_rfq": random.choice(ALL_RFQS) if random.random() > 0.3 else random.choice(ALL_PR),
                "vendor": vendor,
                "vendor_name": None,
                "date_ordered": date_ord,
                "total_amount": total,
                "site": site,
                "department": dept,
                "cost_code": random.choice(COST_CODES),
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-3 PO lines
            for ln in range(random.randint(1, 3)):
                polid = next_id("POL")
                itm = random.choice(ALL_ITEMS)
                qty = random.randint(5, 200)
                price = round(random.uniform(100, 25000), 2)
                po_line_data.append({
                    "id": polid,
                    "workflow_state": "Approved",
                    "po_id": poid,
                    "pr_line_id": random.choice(ALL_PRL) if random.random() > 0.4 else None,
                    "line_row_num": ln + 1,
                    "financial_asset_number": None,
                    "item_id": itm,
                    "item_description": ITEM_NAMES.get(itm, f"Item {itm}"),
                    "quantity_ordered": qty,
                    "price": price,
                    "quantity_received": 0,
                    "site": site,
                    "department": dept,
                    "cost_code": random.choice(COST_CODES),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO purchase_order (id, workflow_state, source_rfq, vendor, vendor_name,
            date_ordered, total_amount, site, department, cost_code, created_at, updated_at)
            VALUES (:id, :workflow_state, :source_rfq, :vendor, :vendor_name, :date_ordered, :total_amount,
            :site, :department, :cost_code, :created_at, :updated_at)"""), po_data)
        conn.execute(text("""INSERT INTO purchase_order_line (id, workflow_state, po_id, pr_line_id, line_row_num,
            financial_asset_number, item_id, item_description, quantity_ordered, price, quantity_received,
            site, department, cost_code, created_at, updated_at)
            VALUES (:id, :workflow_state, :po_id, :pr_line_id, :line_row_num, :financial_asset_number,
            :item_id, :item_description, :quantity_ordered, :price, :quantity_received,
            :site, :department, :cost_code, :created_at, :updated_at)"""), po_line_data)
        ALL_PO = [d["id"] for d in po_data]
        ALL_POL = [d["id"] for d in po_line_data]
        print(f"  → {len(po_data)} purchase orders, {len(po_line_data)} PO lines")

        # ── 15. Purchase Receipts (add 45 to existing 5) ───────────────
        print("Seeding purchase_receipts ...")
        prc_data = []
        for i in range(45):
            prcid = next_id("PRC")
            pol = random.choice(ALL_POL) if ALL_POL else None
            prl = random.choice(ALL_PRL) if ALL_PRL else None
            itm = random.choice(ALL_ITEMS)
            qty_recv = random.randint(5, 100)
            prc_data.append({
                "id": prcid,
                "purchase_order_line": pol,
                "purchase_request_line": prl,
                "pr_row_no": random.randint(1, 3),
                "is_received": True,
                "item": itm,
                "quantity_received": qty_recv,
                "date_received": rand_date(60, 1),
                "receiving_location": random.choice(LOCATIONS),
                "site": random.choice(SITES),
                "department": random.choice(DEPTS),
                "cost_code": random.choice(COST_CODES),
                "generated_inventory": None,
                "account_code": None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO purchase_receipt (id, purchase_order_line, purchase_request_line, pr_row_no,
            is_received, item, quantity_received, date_received, receiving_location, site, department,
            cost_code, generated_inventory, account_code, created_at, updated_at)
            VALUES (:id, :purchase_order_line, :purchase_request_line, :pr_row_no, :is_received, :item,
            :quantity_received, :date_received, :receiving_location, :site, :department, :cost_code,
            :generated_inventory, :account_code, :created_at, :updated_at)"""), prc_data)
        print(f"  → {len(prc_data)} purchase receipts")

        # ── 16. Purchase Returns ────────────────────────────────────────
        print("Seeding purchase_returns ...")
        purtn_data = []
        for i in range(50):
            prid = next_id("PURTN")
            itm = random.choice(ALL_ITEMS)
            purtn_data.append({
                "id": prid,
                "inventory": random.choice(ALL_INVENTORY),
                "serial_number": f"SN-{random.randint(100000, 999999)}" if random.random() > 0.7 else None,
                "item": itm,
                "unit_of_measure": random.choice(ALL_UOMS),
                "date_returned": rand_date(60, 1),
                "quantity_returned": random.randint(1, 20),
                "site": random.choice(SITES),
                "department": random.choice(DEPTS),
                "cost_code": random.choice(COST_CODES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO purchase_return (id, inventory, serial_number, item, unit_of_measure,
            date_returned, quantity_returned, site, department, cost_code, created_at, updated_at)
            VALUES (:id, :inventory, :serial_number, :item, :unit_of_measure, :date_returned,
            :quantity_returned, :site, :department, :cost_code, :created_at, :updated_at)"""), purtn_data)
        print(f"  → {len(purtn_data)} purchase returns")

        # ── 17. Sales Orders ───────────────────────────────────────────
        print("Seeding sales_orders ...")
        so_data = []
        soi_data = []
        customer_names = [
            "Davao Regional Medical Center", "Brokenshire Memorial Hospital",
            "San Pedro Hospital of Davao", "Metro Davao Medical Center",
            "Adventist Hospital Davao", "Davao Doctors Hospital",
            "Philippine Red Cross Davao", "DOH Region XI",
            "Bangsamoro Ministry of Health", "Cotabato Regional Hospital",
            "General Santos Medical Center", "Western Mindanao Medical Center",
            "Zamboanga Medical Center", "Northern Mindanao Medical Center",
            "Caraga Regional Hospital", "SPMC Outreach Program",
            "SPMC Community Health Center", "SPMC Children's Village",
            "SPMC Dental Outreach", "Davao City Health Office",
            "Davao del Sur Provincial Hospital", "Compostela Valley Medical Center",
            "Island Garden City Hospital", "Samal District Hospital",
            "Panabo City Hospital", "Tagum Doctors Hospital",
            "Mati Doctors Hospital", "Digos Doctors Hospital",
            "Nabunturan Municipal Hospital", "Kidapawan Doctors Hospital",
            "Bukidnon Provincial Hospital", "Lanao del Norte Medical Center",
            "Misamis University Hospital", "Iligan Medical Center",
            "Marawi City Hospital", "Sultan Kudarat General Hospital",
            "South Cotabato Provincial Hospital", "Sarangani Provincial Hospital",
            "Davao Oriental Provincial Hospital", "Surigao City Hospital",
            "Butuan Medical Center", "Bislig District Hospital",
            "Tandag City Hospital", "Bayugan District Hospital",
            "Prosperidad Municipal Hospital", "Lianga District Hospital",
            "San Francisco District Hospital", "Dinagat District Hospital",
            "Siargao District Hospital", "Hinatuan Municipal Hospital",
        ]
        for i, cname in enumerate(customer_names):
            soid = next_id("SO")
            site = random.choice(SITES)
            odate = rand_dt(120, 3)
            so_data.append({
                "id": soid,
                "workflow_state": random.choice(["Draft", "Confirmed", "Completed", "Cancelled"]),
                "description": f"Sales order for {cname}",
                "customer_name": cname,
                "order_date": odate,
                "currency": random.choice(ALL_CURRENCIES),
                "site": site,
                "notes": f"Delivery to {cname} facility" if random.random() > 0.5 else None,
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-3 items per SO
            for ln in range(random.randint(1, 3)):
                soiid = next_id("SOI")
                itm = random.choice(ALL_ITEMS)
                qty = random.randint(1, 50)
                uprice = round(random.uniform(500, 30000), 2)
                soi_data.append({
                    "id": soiid,
                    "sales_order": soid,
                    "row_no": ln + 1,
                    "item": itm,
                    "item_description": ITEM_NAMES.get(itm, f"Item {itm}"),
                    "unit_of_measure": random.choice(ALL_UOMS),
                    "qty": qty,
                    "unit_price": uprice,
                    "total_amount": round(uprice * qty, 2),
                    "site": site,
                    "department": random.choice(DEPTS),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO sales_order (id, workflow_state, description, customer_name, order_date,
            currency, site, notes, created_at, updated_at)
            VALUES (:id, :workflow_state, :description, :customer_name, :order_date,
            :currency, :site, :notes, :created_at, :updated_at)"""), so_data)
        conn.execute(text("""INSERT INTO sales_order_item (id, sales_order, row_no, item, item_description,
            unit_of_measure, qty, unit_price, total_amount, site, department, created_at, updated_at)
            VALUES (:id, :sales_order, :row_no, :item, :item_description, :unit_of_measure, :qty,
            :unit_price, :total_amount, :site, :department, :created_at, :updated_at)"""), soi_data)
        print(f"  → {len(so_data)} sales orders, {len(soi_data)} SO items")

        # ── 18. Item Issues ────────────────────────────────────────────
        print("Seeding item_issues ...")
        ii_data = []
        iil_data = []
        for i in range(50):
            iiid = next_id("PI")
            site = random.choice(SITES)
            dept = random.choice(DEPTS)
            ii_data.append({
                "id": iiid,
                "workflow_state": random.choice(["Submitted", "Issued", "Completed"]),
                "issue_type": random.choice(ISSUE_TYPES),
                "issue_to": random.choice(EMPLOYEES),
                "date_issued": rand_dt(90, 1),
                "work_order_activity": None,
                "site": site,
                "department": dept,
                "cost_code": random.choice(COST_CODES),
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-3 lines per issue
            for ln in range(random.randint(1, 3)):
                iilid = next_id("IIL")
                inv = random.choice(ALL_INVENTORY)
                itm_name = ITEM_NAMES.get(random.choice(ALL_ITEMS), "Misc Item")
                iil_data.append({
                    "id": iilid,
                    "item_issue": iiid,
                    "work_order_parts": None,
                    "work_order_equipment": None,
                    "inventory": inv,
                    "item_name": itm_name,
                    "store": random.choice(ALL_STORES),
                    "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                    "zone": random.choice(ALL_ZONES) if ALL_ZONES else None,
                    "quantity_issued": random.randint(1, 50),
                    "unit_cost": round(random.uniform(50, 10000), 2),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO item_issue (id, workflow_state, issue_type, issue_to, date_issued,
            work_order_activity, site, department, cost_code, created_at, updated_at)
            VALUES (:id, :workflow_state, :issue_type, :issue_to, :date_issued,
            :work_order_activity, :site, :department, :cost_code, :created_at, :updated_at)"""), ii_data)
        conn.execute(text("""INSERT INTO item_issue_line (id, item_issue, work_order_parts, work_order_equipment,
            inventory, item_name, store, bin, zone, quantity_issued, unit_cost, created_at, updated_at)
            VALUES (:id, :item_issue, :work_order_parts, :work_order_equipment, :inventory, :item_name,
            :store, :bin, :zone, :quantity_issued, :unit_cost, :created_at, :updated_at)"""), iil_data)
        print(f"  → {len(ii_data)} item issues, {len(iil_data)} issue lines")

        # ── 19. Item Returns ───────────────────────────────────────────
        print("Seeding item_returns ...")
        ir_data = []
        irl_data = []
        for i in range(50):
            irid = next_id("PARTN")
            site = random.choice(SITES)
            dept = random.choice(DEPTS)
            ir_data.append({
                "id": irid,
                "workflow_state": random.choice(["Submitted", "Returned", "Completed"]),
                "return_type": random.choice(RETURN_TYPES),
                "returned_by": random.choice(EMPLOYEES),
                "date_returned": rand_dt(90, 1),
                "work_order_activity": None,
                "site": site,
                "department": dept,
                "cost_code": random.choice(COST_CODES),
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-2 lines per return
            for ln in range(random.randint(1, 2)):
                irlid = next_id("IRL")
                itm = random.choice(ALL_ITEMS)
                irl_data.append({
                    "id": irlid,
                    "item_return": irid,
                    "work_order_parts": None,
                    "work_order_equipment": None,
                    "item": itm,
                    "quantity_returned": random.randint(1, 20),
                    "unit_cost": round(random.uniform(50, 10000), 2),
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO item_return (id, workflow_state, return_type, returned_by, date_returned,
            work_order_activity, site, department, cost_code, created_at, updated_at)
            VALUES (:id, :workflow_state, :return_type, :returned_by, :date_returned,
            :work_order_activity, :site, :department, :cost_code, :created_at, :updated_at)"""), ir_data)
        conn.execute(text("""INSERT INTO item_return_line (id, item_return, work_order_parts, work_order_equipment,
            item, quantity_returned, unit_cost, created_at, updated_at)
            VALUES (:id, :item_return, :work_order_parts, :work_order_equipment, :item,
            :quantity_returned, :unit_cost, :created_at, :updated_at)"""), irl_data)
        print(f"  → {len(ir_data)} item returns, {len(irl_data)} return lines")

        # ── 20. Inventory Adjustments ──────────────────────────────────
        print("Seeding inventory_adjustments ...")
        ia_data = []
        ial_data = []
        for i in range(50):
            iaid = next_id("INVADJ")
            store = random.choice(ALL_STORES)
            site = random.choice(SITES)
            ia_data.append({
                "id": iaid,
                "workflow_state": random.choice(["Draft", "Submitted", "Approved", "Completed"]),
                "source_stock_count": None,
                "reference_doctype": random.choice(["Stock Count", "Physical Audit", "System Correction", None]),
                "posting_datetime": rand_dt(90, 1),
                "location": random.choice(LOCATIONS),
                "store": store,
                "site": site,
                "cost_center": random.choice(ACCOUNTS) if ACCOUNTS else None,
                "remarks": random.choice([
                    "Physical count variance adjustment",
                    "Damaged goods write-off",
                    "System correction entry",
                    "Expired items disposal",
                    "Cycle count adjustment",
                    None,
                ]),
                "created_at": ts(), "updated_at": ts(),
            })
            # 1-3 adjustment lines
            for ln in range(random.randint(1, 3)):
                ialid = next_id("INVADJL")
                inv = random.choice(ALL_INVENTORY)
                itm = random.choice(ALL_ITEMS)
                cur_qty = random.randint(10, 200)
                adj_qty = random.randint(-20, 50)
                ial_data.append({
                    "id": ialid,
                    "inventory_adjustment": iaid,
                    "inventory": inv,
                    "item": itm,
                    "asset_tag": None,
                    "serial_nos": None,
                    "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                    "zone": random.choice(ALL_ZONES) if ALL_ZONES else None,
                    "uom": random.choice(ALL_UOMS),
                    "current_qty": cur_qty,
                    "adjusted_qty": adj_qty,
                    "current_rate": round(random.uniform(100, 10000), 2),
                    "delta_value": round(adj_qty * random.uniform(100, 5000), 2),
                    "inventory_adjustment_account": None,
                    "inventory_account": None,
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO inventory_adjustment (id, workflow_state, source_stock_count, reference_doctype,
            posting_datetime, location, store, site, cost_center, remarks, created_at, updated_at)
            VALUES (:id, :workflow_state, :source_stock_count, :reference_doctype, :posting_datetime,
            :location, :store, :site, :cost_center, :remarks, :created_at, :updated_at)"""), ia_data)
        conn.execute(text("""INSERT INTO inventory_adjustment_line (id, inventory_adjustment, inventory, item, asset_tag,
            serial_nos, bin, zone, uom, current_qty, adjusted_qty, current_rate, delta_value,
            inventory_adjustment_account, inventory_account, created_at, updated_at)
            VALUES (:id, :inventory_adjustment, :inventory, :item, :asset_tag, :serial_nos, :bin, :zone,
            :uom, :current_qty, :adjusted_qty, :current_rate, :delta_value,
            :inventory_adjustment_account, :inventory_account, :created_at, :updated_at)"""), ial_data)
        print(f"  → {len(ia_data)} inventory adjustments, {len(ial_data)} adjustment lines")

        # ── 21. Transfers ──────────────────────────────────────────────
        print("Seeding transfers ...")
        tr_data = []
        for i in range(50):
            trid = next_id("TR")
            from_store = random.choice(ALL_STORES)
            to_store = random.choice([s for s in ALL_STORES if s != from_store])
            itm = random.choice(ALL_ITEMS)
            tr_data.append({
                "id": trid,
                "transfer_type": random.choice(TRANSFER_TYPES),
                "moved_by": random.choice(EMPLOYEES),
                "date_moved": rand_date(90, 1),
                "work_order_activity": None,
                "inventory": random.choice(ALL_INVENTORY),
                "labor": None,
                "equipment": None,
                "item_to_transfer": itm,
                "purchase_request_line": random.choice(ALL_PRL) if random.random() > 0.7 else None,
                "site": random.choice(SITES),
                "from_location": random.choice(LOCATIONS),
                "from_store": from_store,
                "from_bin": random.choice(ALL_BINS) if ALL_BINS else None,
                "from_zone": random.choice(ALL_ZONES) if ALL_ZONES else None,
                "to_location": random.choice(LOCATIONS),
                "to_vendor": random.choice(ALL_VENDORS) if random.random() > 0.8 else None,
                "to_store": to_store,
                "to_bin": random.choice(ALL_BINS) if ALL_BINS else None,
                "to_zone": random.choice(ALL_ZONES) if ALL_ZONES else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO transfer (id, transfer_type, moved_by, date_moved, work_order_activity,
            inventory, labor, equipment, item_to_transfer, purchase_request_line, site,
            from_location, from_store, from_bin, from_zone,
            to_location, to_vendor, to_store, to_bin, to_zone, created_at, updated_at)
            VALUES (:id, :transfer_type, :moved_by, :date_moved, :work_order_activity,
            :inventory, :labor, :equipment, :item_to_transfer, :purchase_request_line, :site,
            :from_location, :from_store, :from_bin, :from_zone,
            :to_location, :to_vendor, :to_store, :to_bin, :to_zone, :created_at, :updated_at)"""), tr_data)
        ALL_TRANSFERS = [d["id"] for d in tr_data]
        print(f"  → {len(tr_data)} transfers")

        # ── 22. Transfer Receipts ──────────────────────────────────────
        print("Seeding transfer_receipts ...")
        trr_data = []
        for i in range(50):
            trrid = next_id("TRR", width=6)
            trr_data.append({
                "id": trrid,
                "transfer_request": random.choice(ALL_TRANSFERS),
                "inventory": random.choice(ALL_INVENTORY),
                "unit_of_measure": random.choice(ALL_UOMS),
                "date_received": rand_date(60, 1),
                "receiving_location": random.choice(LOCATIONS),
                "site": random.choice(SITES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO transfer_receipt (id, transfer_request, inventory, unit_of_measure,
            date_received, receiving_location, site, created_at, updated_at)
            VALUES (:id, :transfer_request, :inventory, :unit_of_measure, :date_received,
            :receiving_location, :site, :created_at, :updated_at)"""), trr_data)
        print(f"  → {len(trr_data)} transfer receipts")

        # ── 23. Putaway ────────────────────────────────────────────────
        print("Seeding putaway ...")
        pa_data = []
        for i in range(50):
            paid = next_id("PA")
            itm = random.choice(ALL_ITEMS)
            store = random.choice(ALL_STORES)
            zones_for_store = zone_map.get(store, [])
            pa_data.append({
                "id": paid,
                "putaway_type": random.choice(["New Receipt", "Return to Stock", "Repair Return", "Transfer In"]),
                "source_data_repair": None,
                "source_data_parts_return": None,
                "source_data_asset": None,
                "item": itm,
                "serial_number": f"SN-{random.randint(100000, 999999)}" if random.random() > 0.7 else None,
                "qty": random.randint(1, 100),
                "site": random.choice(SITES),
                "store": store,
                "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                "zone": random.choice(zones_for_store) if zones_for_store else None,
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO putaway (id, putaway_type, source_data_repair, source_data_parts_return,
            source_data_asset, item, serial_number, qty, site, store, bin, zone, created_at, updated_at)
            VALUES (:id, :putaway_type, :source_data_repair, :source_data_parts_return,
            :source_data_asset, :item, :serial_number, :qty, :site, :store, :bin, :zone,
            :created_at, :updated_at)"""), pa_data)
        print(f"  → {len(pa_data)} putaway records")

        # ── 24. Stock Counts ───────────────────────────────────────────
        print("Seeding stock_counts ...")
        sc_data = []
        scl_data = []
        sct_data = []
        for i in range(50):
            scid = next_id("SC")
            store = random.choice(ALL_STORES)
            site = random.choice(SITES)
            sc_data.append({
                "id": scid,
                "workflow_state": random.choice(["Draft", "In Progress", "Completed", "Reconciled"]),
                "store": store,
                "site": site,
                "method": random.choice(["Full Count", "Cycle Count", "Spot Check", "ABC Count"]),
                "basis": random.choice(["Annual", "Quarterly", "Monthly", "Ad Hoc"]),
                "abc_code": random.choice(["A", "B", "C", None]),
                "freeze_policy": random.choice(["Hard Freeze", "Soft Freeze", "No Freeze"]),
                "snapshot_at": rand_dt(60, 1),
                "created_at": ts(), "updated_at": ts(),
            })
            # 2-5 count lines per stock count
            for ln in range(random.randint(2, 5)):
                sclid = next_id("SCL")
                inv = random.choice(ALL_INVENTORY)
                itm = random.choice(ALL_ITEMS)
                snap_qty = random.randint(10, 300)
                counted = snap_qty + random.randint(-15, 15)
                variance = counted - snap_qty
                scl_data.append({
                    "id": sclid,
                    "stock_count": scid,
                    "inventory": inv,
                    "item": itm,
                    "asset_tag": None,
                    "serial_nos": None,
                    "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                    "zone": random.choice(ALL_ZONES) if ALL_ZONES else None,
                    "uom": random.choice(ALL_UOMS),
                    "snapshot_qty": snap_qty,
                    "counted_qty": counted,
                    "variance_qty": variance,
                    "variance_value": round(variance * random.uniform(100, 5000), 2),
                    "variance_reason": random.choice(ALL_REASON_CODES) if variance != 0 and ALL_REASON_CODES else None,
                    "is_reconciled": random.choice([True, False]),
                    "created_at": ts(), "updated_at": ts(),
                })
            # 1-2 tasks per stock count
            for tn in range(random.randint(1, 2)):
                sctid = next_id("SCT")
                sct_data.append({
                    "id": sctid,
                    "stock_count": scid,
                    "assigned_to": random.choice(USERS),
                    "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                    "submitted_at": rand_dt(60, 1) if random.random() > 0.3 else None,
                    "site": site,
                    "created_at": ts(), "updated_at": ts(),
                })
        conn.execute(text("""INSERT INTO stock_count (id, workflow_state, store, site, method, basis, abc_code,
            freeze_policy, snapshot_at, created_at, updated_at)
            VALUES (:id, :workflow_state, :store, :site, :method, :basis, :abc_code,
            :freeze_policy, :snapshot_at, :created_at, :updated_at)"""), sc_data)
        conn.execute(text("""INSERT INTO stock_count_line (id, stock_count, inventory, item, asset_tag, serial_nos,
            bin, zone, uom, snapshot_qty, counted_qty, variance_qty, variance_value, variance_reason,
            is_reconciled, created_at, updated_at)
            VALUES (:id, :stock_count, :inventory, :item, :asset_tag, :serial_nos, :bin, :zone, :uom,
            :snapshot_qty, :counted_qty, :variance_qty, :variance_value, :variance_reason,
            :is_reconciled, :created_at, :updated_at)"""), scl_data)
        conn.execute(text("""INSERT INTO stock_count_task (id, stock_count, assigned_to, bin, submitted_at, site,
            created_at, updated_at)
            VALUES (:id, :stock_count, :assigned_to, :bin, :submitted_at, :site,
            :created_at, :updated_at)"""), sct_data)
        print(f"  → {len(sc_data)} stock counts, {len(scl_data)} count lines, {len(sct_data)} count tasks")

        # ── 25. Inspections ────────────────────────────────────────────
        print("Seeding inspections ...")
        insp_data = []
        inspection_results = [
            "Item passed quality inspection - acceptable condition",
            "Minor cosmetic damage noted - item accepted with discount",
            "Item rejected - does not meet SPMC specifications",
            "Item passed sterility test - approved for patient use",
            "Calibration verified within acceptable tolerance",
            "Quantity shortage noted - vendor notified for replacement",
            "Expiration date verified - within acceptable shelf life",
            "Packaging intact - item approved for storage",
            "Temperature sensitive item - cold chain verified",
            "Documentation complete - item approved for receiving",
        ]
        for i in range(50):
            inspid = next_id("INSP")
            insp_data.append({
                "id": inspid,
                "inspection_date": rand_date(90, 1),
                "inspector": random.choice(EMPLOYEES),
                "site": random.choice(SITES),
                "inventory": random.choice(ALL_INVENTORY),
                "inspection_result": random.choice(inspection_results),
                "action_required": random.choice([
                    "None - item cleared for use",
                    "Return to vendor for replacement",
                    "Hold in quarantine pending further review",
                    "Accept with noted exception",
                    "Schedule re-inspection in 30 days",
                    None,
                ]),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO inspection (id, inspection_date, inspector, site, inventory,
            inspection_result, action_required, created_at, updated_at)
            VALUES (:id, :inspection_date, :inspector, :site, :inventory,
            :inspection_result, :action_required, :created_at, :updated_at)"""), insp_data)
        print(f"  → {len(insp_data)} inspections")

        # ── 26. Stock Ledger Entries ───────────────────────────────────
        print("Seeding stock_ledger_entries ...")
        sle_data = []
        for i in range(50):
            sleid = next_id("SLE")
            itm = random.choice(ALL_ITEMS)
            qty_in = random.randint(0, 100)
            qty_out = random.randint(0, 50) if qty_in == 0 else 0
            rate = round(random.uniform(100, 15000), 2)
            sle_data.append({
                "id": sleid,
                "item": itm,
                "serial_no": None,
                "store": random.choice(ALL_STORES),
                "bin": random.choice(ALL_BINS) if ALL_BINS else None,
                "posting_datetime": rand_dt(90, 1),
                "qty_in": qty_in,
                "qty_out": qty_out,
                "value_in": round(qty_in * rate, 2),
                "value_out": round(qty_out * rate, 2),
                "balance_qty": random.randint(10, 500),
                "balance_value": round(random.uniform(10000, 500000), 2),
                "voucher_type": random.choice(VOUCHER_TYPES),
                "voucher_no": f"VCH-{random.randint(10000, 99999)}",
                "site": random.choice(SITES),
                "created_at": ts(), "updated_at": ts(),
            })
        conn.execute(text("""INSERT INTO stock_ledger_entry (id, item, serial_no, store, bin, posting_datetime,
            qty_in, qty_out, value_in, value_out, balance_qty, balance_value, voucher_type, voucher_no,
            site, created_at, updated_at)
            VALUES (:id, :item, :serial_no, :store, :bin, :posting_datetime,
            :qty_in, :qty_out, :value_in, :value_out, :balance_qty, :balance_value,
            :voucher_type, :voucher_no, :site, :created_at, :updated_at)"""), sle_data)
        print(f"  → {len(sle_data)} stock ledger entries")

        # ── Update all series counters ─────────────────────────────────
        update_series(conn)
        print("\n✓ All series counters updated")

    print("\n════════════════════════════════════════════════════════════")
    print("SEED COMPLETE - Procurement, Inventory & Warehouse modules")
    print("════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    main()
