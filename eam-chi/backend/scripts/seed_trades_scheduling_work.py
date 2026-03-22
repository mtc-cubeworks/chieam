"""
SPMC EAM - Seed Trades, Scheduling, Work Execution & Work Resources
=====================================================================
Populates 50+ records for:
- Trades: trade, trade_labor, trade_availability
- Scheduling: work_schedule, work_schedule_details, holiday, leave_type, leave_application
- Work Execution: work_order_checklist (+details), work_order_activity_logs, work_order_equipment
- Work Resources: work_order_labor, work_order_parts, work_order_parts_reservation
"""
import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text

DB_URL = "postgresql://eam_spmc_user:CwSpmcSec2026mR7@localhost:5432/eam-spmc"
engine = create_engine(DB_URL)
NOW = datetime.now()

# ---------- Reference data ----------
LABORS = ["LBR-0001","LBR-0002","LBR-0003","LBR-0004","LBR-0005",
          "LBR-0021","LBR-0022","LBR-0023","LBR-0024","LBR-0025"]
EMPLOYEES = ["EMP-0001","EMP-0002","EMP-0003","EMP-0004","EMP-0005",
             "EMP-0021","EMP-0022","EMP-0023","EMP-0024","EMP-0025"]
ITEMS = ["ITM-0001","ITM-0002","ITM-0003","ITM-0004","ITM-0005",
         "ITM-0006","ITM-0007","ITM-0008","ITM-0009","ITM-0010",
         "ITM-0026","ITM-0027","ITM-0028","ITM-0029","ITM-0030"]
INVENTORIES = ["INV-0001","INV-0002","INV-0003"]
SITES = ["SITE-0001","SITE-0002","SITE-0003","SITE-0004"]
DEPARTMENTS = [f"DEPT-{str(i).zfill(4)}" for i in list(range(1,19))+[34,35,36,37,38]]
COST_CODES = [f"CC-{str(i).zfill(4)}" for i in list(range(1,6))+list(range(21,26))]
UOM = ["UOM-0001","UOM-0002","UOM-0003"]
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def rc(lst): return random.choice(lst)
def rand_date(start_ago=365, end_ago=0):
    return date.today() - timedelta(days=random.randint(end_ago, start_ago))
def rand_dt(start_ago=365, end_ago=0):
    return datetime.now() - timedelta(days=random.randint(end_ago, start_ago),
                                       hours=random.randint(0,23), minutes=random.randint(0,59))

# ======================= DOMAIN DATA =======================

TRADE_NAMES = [
    ("Biomedical Engineering", "Repair, calibration, and maintenance of medical devices and clinical equipment"),
    ("HVAC Technician", "Heating, ventilation, air conditioning installation and maintenance"),
    ("Electrical", "Electrical systems installation, troubleshooting, and repair"),
    ("Plumbing", "Water supply, drainage, and medical gas piping systems"),
    ("Mechanical", "Mechanical systems including elevators, pumps, and compressors"),
    ("Carpentry", "Woodwork, partitions, ceiling, and furniture repair"),
    ("Painting", "Interior and exterior painting and wall finishing"),
    ("Welding & Fabrication", "Metal work, structural steel, and equipment fabrication"),
    ("Fire Safety Systems", "Fire alarm, sprinkler, and suppression system maintenance"),
    ("Medical Gas Systems", "Oxygen, vacuum, and medical air pipeline maintenance"),
    ("Elevator Technician", "Elevator and dumbwaiter installation and maintenance"),
    ("Generator Technician", "Diesel generator set maintenance and repair"),
    ("Instrumentation & Controls", "BMS, automation, and instrument calibration"),
    ("Refrigeration", "Cold chain, pharmacy refrigeration, and morgue cooling"),
    ("Sterilization Equipment", "Autoclave and sterilizer maintenance and validation"),
    ("Imaging Equipment", "X-ray, CT, MRI, Ultrasound system maintenance"),
    ("Laboratory Equipment", "Lab analyzer, centrifuge, and microscope maintenance"),
    ("IT & Network Infrastructure", "Structured cabling, nurse call, and communication systems"),
    ("Boiler Operations", "Steam boiler operation, water treatment, and maintenance"),
    ("Grounds & Landscaping", "Outdoor maintenance, pest control, and ground keeping"),
    ("Civil Works", "Concrete repair, waterproofing, and structural maintenance"),
    ("Water Treatment", "Water purification, dialysis water, and wastewater treatment"),
    ("Pneumatic Systems", "Pneumatic tube system maintenance and repair"),
    ("Kitchen Equipment", "Commercial kitchen equipment maintenance and gas fitting"),
    ("Laundry Equipment", "Industrial washer, dryer, and ironer maintenance"),
    ("Solar Energy Systems", "PV panel, inverter, and battery maintenance"),
    ("Dental Equipment", "Dental chair, compressor, and suction system maintenance"),
    ("Ambulance Maintenance", "Emergency vehicle mechanical and equipment maintenance"),
    ("Security Systems", "CCTV, access control, and security equipment maintenance"),
    ("Waste Management", "Medical waste treatment equipment and incinerator maintenance"),
    ("Radiology Shielding", "Radiation protection and lead-lined room maintenance"),
    ("Ophthalmology Equipment", "Slit lamp, autorefractor, and OCT maintenance"),
    ("Respiratory Equipment", "Ventilator, CPAP, and oxygen concentrator servicing"),
    ("Dialysis Equipment", "Hemodialysis machine and RO water system maintenance"),
    ("Neonatal Equipment", "Incubator, warmer, and phototherapy unit servicing"),
    ("OR Equipment", "Surgical table, ESU, and tourniquet system maintenance"),
    ("Patient Monitoring", "Bedside monitor, telemetry, and central station maintenance"),
    ("Endoscopy Equipment", "Endoscope, processor, and reprocessor maintenance"),
    ("Pharmacy Automation", "Dispensing machine and compounding hood maintenance"),
    ("Blood Bank Equipment", "Blood warmer, centrifuge, and storage equipment maintenance"),
    ("Physical Therapy Equip", "Ultrasound therapy, TENS, and traction equipment"),
    ("Pathology Equipment", "Microtome, tissue processor, and stainer maintenance"),
    ("Mortuary Systems", "Morgue refrigeration and body handling equipment"),
    ("Central Supply Systems", "CSSD equipment and instrument tracking systems"),
    ("Parking Systems", "Automated barrier gate and ticket machine maintenance"),
    ("Audio Visual Systems", "Conference room AV, PA system, and display maintenance"),
    ("Furniture & Fixtures", "Hospital bed, IV pole, and furniture maintenance"),
    ("Signage & Wayfinding", "Interior and exterior signage maintenance"),
    ("Pest Control Equipment", "UV trap, bait station, and fumigation equipment"),
    ("Emergency Preparedness", "Disaster response equipment and emergency kit maintenance"),
]

WORK_SCHEDULE_NAMES = [
    "Regular Day Shift (7AM-3PM)", "Afternoon Shift (3PM-11PM)", "Night Shift (11PM-7AM)",
    "12-Hour Day Shift (7AM-7PM)", "12-Hour Night Shift (7PM-7AM)",
    "Monday-Friday Office Hours", "Rotating 3-Shift Schedule", "On-Call Weekend Schedule",
    "Biomedical Day Schedule", "HVAC 24/7 Rotation", "Electricians Day Shift",
    "Plumbing Team Schedule", "Generator Operators Rotation", "Elevator Tech Schedule",
    "Fire Safety Team Shift", "Medical Gas Team Schedule", "Imaging Tech On-Call",
    "Lab Equipment Maintenance", "Boiler Room 24/7 Coverage", "Grounds Crew Morning Shift",
    "IT Support Extended Hours", "Kitchen Maintenance Early", "Laundry Equipment AM",
    "Security Systems Support", "Waste Treatment Operators", "Water Treatment 24/7",
    "Weekend Emergency Team", "Holiday Skeleton Crew", "Shutdown Maintenance Schedule",
    "PM Execution Morning", "PM Execution Afternoon", "Emergency Response Team Shift",
    "OR Equipment Readiness", "ICU Equipment Support", "ER Coverage Schedule",
    "Neonatal Equipment Team", "Dialysis Support Schedule", "Pharmacy Equipment Team",
    "Ambulance Bay Coverage", "Radiology PM Schedule", "Dental Clinic Support",
    "Outpatient Services AM", "Outpatient Services PM", "Ward Round Support",
    "Central Supply Coverage", "Blood Bank Equipment Team", "Pathology Lab Schedule",
    "Physical Therapy Support", "Administrative Building", "Night Emergency Standby",
]

PH_HOLIDAYS_2026 = [
    ("New Year's Day", "2026-01-01"),
    ("Chinese New Year", "2026-02-17"),
    ("EDSA People Power Anniversary", "2026-02-25"),
    ("Araw ng Kagitingan", "2026-04-09"),
    ("Maundy Thursday", "2026-04-02"),
    ("Good Friday", "2026-04-03"),
    ("Black Saturday", "2026-04-04"),
    ("Labor Day", "2026-05-01"),
    ("Independence Day", "2026-06-12"),
    ("Eid'l Fitr", "2026-03-20"),
    ("Eid'l Adha", "2026-05-27"),
    ("Ninoy Aquino Day", "2026-08-21"),
    ("National Heroes Day", "2026-08-31"),
    ("All Saints' Day", "2026-11-01"),
    ("All Souls' Day", "2026-11-02"),
    ("Bonifacio Day", "2026-11-30"),
    ("Feast of Immaculate Conception", "2026-12-08"),
    ("Christmas Eve", "2026-12-24"),
    ("Christmas Day", "2026-12-25"),
    ("Rizal Day", "2026-12-30"),
    ("New Year's Eve", "2026-12-31"),
    ("Davao City Charter Day", "2026-03-16"),
    ("Kadayawan Festival", "2026-08-21"),
    ("SPMC Foundation Day", "2026-07-01"),
    ("Hospital Workers Day", "2026-09-15"),
    ("National Hospital Week Start", "2026-10-05"),
    ("National Hospital Week End", "2026-10-11"),
    ("World Health Day", "2026-04-07"),
    ("Engineers Day", "2026-06-20"),
    ("Maintenance Appreciation Day", "2026-11-15"),
    ("Biomedical Engineering Week", "2026-10-19"),
    ("Energy Conservation Day", "2026-03-14"),
    ("Fire Prevention Month Opening", "2026-03-01"),
    ("Occupational Safety Week", "2026-06-15"),
    ("Quality Week Opening", "2026-10-12"),
    ("Philippine Civil Service Day", "2026-09-01"),
    ("Christmas Party", "2026-12-18"),
    ("Year-End Inventory Day", "2026-12-29"),
    ("Department Outing Day", "2026-05-15"),
    ("General Cleaning Day Q1", "2026-03-28"),
    ("General Cleaning Day Q2", "2026-06-27"),
    ("General Cleaning Day Q3", "2026-09-26"),
    ("General Cleaning Day Q4", "2026-12-19"),
    ("Emergency Drill Day Q1", "2026-02-14"),
    ("Emergency Drill Day Q2", "2026-05-09"),
    ("Emergency Drill Day Q3", "2026-08-08"),
    ("Emergency Drill Day Q4", "2026-11-14"),
    ("PM Shutdown Day - January", "2026-01-17"),
    ("PM Shutdown Day - July", "2026-07-18"),
    ("Annual Physical Exam Day", "2026-04-25"),
]

LEAVE_TYPES = [
    "Vacation Leave", "Sick Leave", "Emergency Leave", "Bereavement Leave",
    "Maternity Leave", "Paternity Leave", "Special Privilege Leave",
    "Mandatory/Forced Leave", "Rehabilitation Leave", "Study Leave",
    "Training Leave", "Official Business", "Compensatory Time Off",
    "Solo Parent Leave", "VAWC Leave", "Special Emergency Leave",
    "Adoption Leave", "Calamity Leave", "Quarantine Leave", "Unpaid Leave",
    "Birthday Leave", "Anniversary Leave", "Union Leave", "Election Leave",
    "Sports Leave", "Women's Special Leave", "Service Incentive Leave",
    "Religious Holiday Leave", "Personal Leave", "Administrative Leave",
    "Dental Appointment Leave", "Eye Care Leave", "Mental Health Day",
    "Community Service Leave", "Blood Donation Leave", "Wellness Leave",
    "Family Day Leave", "Parental Leave", "Rest Day Leave", "Marriage Leave",
    "Graduation Leave", "Medical Procedure Leave", "Jury Duty Leave",
    "Relocation Leave", "Pet Care Leave", "Volunteer Leave",
    "Professional Development Leave", "Conference Attendance Leave",
    "Certification Exam Leave", "Project Transition Leave",
]

LEAVE_REASONS = [
    "Family emergency", "Medical appointment", "Vacation trip to hometown",
    "Personal matters", "House renovation", "Child's school activity",
    "Government transaction", "Wedding attendance", "Dental procedure",
    "Annual physical checkup", "Eye examination", "Mental health rest day",
    "Family reunion", "Religious observance", "Legal matters",
    "Community volunteer work", "Professional development seminar",
    "Continuing education class", "Certification exam preparation",
    "Moving to new residence",
]

CHECKLIST_STATUSES = ["Pending", "Completed", "In Progress", "Failed"]
CHECKLIST_DETAIL_STATUSES = ["Pending", "Checked", "Failed"]

WO_LOG_ENTRIES = [
    "Arrived at site, assessed equipment condition",
    "Parts received from store, preparing for installation",
    "Removed defective component, area cleaned",
    "New component installed, performing initial testing",
    "Calibration completed, within OEM specifications",
    "Waiting for vendor technical support callback",
    "Safety interlock tested and verified functional",
    "Equipment returned to service, user notified",
    "Preventive maintenance checklist completed",
    "Found additional wear on adjacent component, noted for follow-up",
    "Electrical measurements taken - voltage/current normal",
    "Lubrication completed on all moving parts",
    "Filter replaced, differential pressure normalized",
    "Belt tension adjusted to manufacturer specifications",
    "Software updated to latest firmware version",
    "Leak test performed - no leaks detected",
    "Performance test completed - all parameters within limits",
    "Training provided to operator on proper use",
    "Documentation updated in equipment logbook",
    "Final inspection done, work order activity completed",
    "Thermal imaging scan completed, no hotspots found",
    "Vibration readings taken, baseline established",
    "Alignment checked and corrected to specification",
    "Bearing replacement completed successfully",
    "Pressure test passed at 1.5x working pressure",
    "Refrigerant charge verified at correct level",
    "Water quality test passed all parameters",
    "Emergency shutdown test performed successfully",
    "Backup battery capacity test passed",
    "Communication system tested, all zones responsive",
]

WO_PARTS_STATES = ["Draft", "Submitted", "Approved", "Release", "In Progress", "Completed"]
RESERVATION_STATUSES = ["Reserved", "Issued", "Returned", "Cancelled"]


def _update_series(conn, prefix, val):
    conn.execute(text(
        "INSERT INTO series (name, current) VALUES (:name, :val) "
        "ON CONFLICT (name) DO UPDATE SET current = GREATEST(series.current, :val)"
    ), {"name": prefix, "val": val})


def seed():
    with engine.begin() as conn:
        # ============================================================
        # 1) TRADES (50)
        # ============================================================
        print("Seeding Trades...")
        trd_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM trade")).scalar()
        trd_start = max(trd_max + 1, 1)
        trade_ids = []
        for i in range(50):
            trd_id = f"TRD-{str(trd_start+i).zfill(5)}"
            trade_ids.append(trd_id)
            name, desc = TRADE_NAMES[i]
            conn.execute(text(
                "INSERT INTO trade (id, trade_name, description, on_staff, licensed, available_capacity, created_at, updated_at) "
                "VALUES (:id,:name,:desc,:staff,:lic,:cap,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": trd_id, "name": name, "desc": desc,
                "staff": random.random() > 0.2, "lic": random.random() > 0.5,
                "cap": random.randint(2, 15), "now": NOW})
        _update_series(conn, "TRD", trd_start + 50)
        print(f"  Created {len(trade_ids)} trades")

        # ============================================================
        # 2) TRADE LABOR (50) - link labors to trades
        # ============================================================
        print("Seeding Trade Labor...")
        tl_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM trade_labor")).scalar()
        tl_counter = max(tl_max + 1, 1)
        tl_count = 0
        for i in range(50):
            tl_id = f"TRDEMP-{str(tl_counter).zfill(5)}"
            tl_counter += 1
            tl_count += 1
            conn.execute(text(
                "INSERT INTO trade_labor (id, trade, labor, laborer, \"primary\", created_at, updated_at) "
                "VALUES (:id,:trade,:labor,:laborer,:prim,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": tl_id, "trade": rc(trade_ids), "labor": rc(LABORS),
                "laborer": f"Laborer-{i+1}", "prim": i % 5 == 0, "now": NOW})
        _update_series(conn, "TRDEMP", tl_counter)
        print(f"  Created {tl_count} trade labor entries")

        # ============================================================
        # 3) TRADE AVAILABILITY (50)
        # ============================================================
        print("Seeding Trade Availability...")
        ta_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM trade_availability")).scalar()
        ta_counter = max(ta_max + 1, 1)
        ta_count = 0
        for i in range(50):
            ta_id = f"TRDAV-{str(ta_counter).zfill(5)}"
            ta_counter += 1
            ta_count += 1
            avail = random.randint(2, 10)
            reserved = random.randint(0, avail)
            conn.execute(text(
                "INSERT INTO trade_availability (id, trade, specific_datetime, remaining_capacity, "
                "reserved_capacity, available_capacity, created_at, updated_at) "
                "VALUES (:id,:trade,:dt,:rem,:res,:avail,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": ta_id, "trade": rc(trade_ids),
                "dt": rand_dt(90, 0), "rem": avail - reserved,
                "res": reserved, "avail": avail, "now": NOW})
        _update_series(conn, "TRDAV", ta_counter)
        print(f"  Created {ta_count} trade availability entries")

        # ============================================================
        # 4) WORK SCHEDULES (50) + Work Schedule Details
        # ============================================================
        print("Seeding Work Schedules...")
        ws_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_schedule")).scalar()
        ws_start = max(ws_max + 1, 1)
        wsd_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_schedule_details")).scalar()
        wsd_counter = max(wsd_max + 1, 1)
        ws_ids = []

        shift_patterns = [
            [("07:00","15:00")], [("15:00","23:00")], [("23:00","07:00")],
            [("07:00","19:00")], [("19:00","07:00")], [("08:00","17:00")],
            [("06:00","14:00")], [("14:00","22:00")], [("08:00","12:00"),("13:00","17:00")],
            [("07:30","16:30")],
        ]

        for i in range(50):
            ws_id = f"WSCHED-{str(ws_start+i).zfill(5)}"
            ws_ids.append(ws_id)
            sd = rand_date(180, 0)
            conn.execute(text(
                "INSERT INTO work_schedule (id, schedule_name, specific_labor, start_date, end_date, created_at, updated_at) "
                "VALUES (:id,:name,:labor,:sd,:ed,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": ws_id, "name": WORK_SCHEDULE_NAMES[i % len(WORK_SCHEDULE_NAMES)],
                "labor": rc(LABORS) if random.random() > 0.4 else None,
                "sd": sd, "ed": sd + timedelta(days=random.choice([30,60,90,180,365])), "now": NOW})

            # Create schedule details for 5-7 days
            pattern = rc(shift_patterns)
            working_days = random.sample(DAYS, random.randint(5, 7))
            for day in DAYS:
                wsd_id = f"WSCHEDD-{str(wsd_counter).zfill(5)}"
                wsd_counter += 1
                is_working = day in working_days
                times = pattern[0] if is_working else ("00:00", "00:00")
                conn.execute(text(
                    "INSERT INTO work_schedule_details (id, work_schedule, day, start_time, end_time, is_working, created_at, updated_at) "
                    "VALUES (:id,:ws,:day,:st,:et,:iw,:now,:now) ON CONFLICT (id) DO NOTHING"
                ), {"id": wsd_id, "ws": ws_id, "day": day,
                    "st": times[0], "et": times[1], "iw": is_working, "now": NOW})

        _update_series(conn, "WSCHED", ws_start + 50)
        _update_series(conn, "WSCHEDD", wsd_counter)
        print(f"  Created {len(ws_ids)} work schedules with details")

        # ============================================================
        # 5) HOLIDAYS (50)
        # ============================================================
        print("Seeding Holidays...")
        hol_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM holiday")).scalar()
        hol_start = max(hol_max + 1, 1)
        hol_count = 0
        for i in range(50):
            hol_id = f"HOL-{str(hol_start+i).zfill(5)}"
            hol_count += 1
            name, dt_str = PH_HOLIDAYS_2026[i]
            conn.execute(text(
                "INSERT INTO holiday (id, holiday_name, holiday_date, specific_labor, created_at, updated_at) "
                "VALUES (:id,:name,:hd,:labor,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": hol_id, "name": name, "hd": dt_str,
                "labor": rc(LABORS) if random.random() > 0.7 else None, "now": NOW})
        _update_series(conn, "HOL", hol_start + 50)
        print(f"  Created {hol_count} holidays")

        # ============================================================
        # 6) LEAVE TYPES (50)
        # ============================================================
        print("Seeding Leave Types...")
        lt_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM leave_type")).scalar()
        lt_start = max(lt_max + 1, 1)
        lt_ids = []
        for i in range(50):
            lt_id = f"LVT-{str(lt_start+i).zfill(5)}"
            lt_ids.append(lt_id)
            conn.execute(text(
                "INSERT INTO leave_type (id, leave_type_name, created_at, updated_at) "
                "VALUES (:id,:name,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": lt_id, "name": LEAVE_TYPES[i], "now": NOW})
        _update_series(conn, "LVT", lt_start + 50)
        print(f"  Created {len(lt_ids)} leave types")

        # ============================================================
        # 7) LEAVE APPLICATIONS (50)
        # ============================================================
        print("Seeding Leave Applications...")
        la_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM leave_application")).scalar()
        la_start = max(la_max + 1, 1)
        la_count = 0
        for i in range(50):
            la_id = f"LVAPP-{str(la_start+i).zfill(5)}"
            la_count += 1
            fd = rand_dt(180, 5)
            dur = random.choice([1, 2, 3, 5, 7, 10, 14])
            conn.execute(text(
                "INSERT INTO leave_application (id, labor, leave_type, from_date, to_date, reason, created_at, updated_at) "
                "VALUES (:id,:labor,:lt,:fd,:td,:reason,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": la_id, "labor": rc(LABORS), "lt": rc(lt_ids),
                "fd": fd, "td": fd + timedelta(days=dur),
                "reason": rc(LEAVE_REASONS), "now": NOW})
        _update_series(conn, "LVAPP", la_start + 50)
        print(f"  Created {la_count} leave applications")

        # ============================================================
        # GET EXISTING + NEWLY CREATED WORK ORDER ACTIVITIES
        # (We need WOA IDs for work execution/resources)
        # ============================================================
        woa_ids = [r[0] for r in conn.execute(text("SELECT id FROM work_order_activity ORDER BY id")).fetchall()]
        if not woa_ids:
            print("  WARNING: No work_order_activity records found. Creating some first...")
            # Create WOAs referencing existing work orders
            wo_ids = [r[0] for r in conn.execute(text("SELECT id FROM work_order ORDER BY id")).fetchall()]
            if not wo_ids:
                print("  ERROR: No work_orders exist either. Skipping work execution/resources.")
                _print_summary(conn)
                return
            woa_max = 0
            woa_start = max(woa_max + 1, 36)
            for j in range(50):
                woa_id = f"WOA-{str(woa_start+j).zfill(5)}"
                woa_ids.append(woa_id)
                sd = rand_dt(180, 30)
                conn.execute(text(
                    "INSERT INTO work_order_activity (id, workflow_state, work_order, description, "
                    "assigned_to, location, site, department, start_date, end_date, created_at, updated_at) "
                    "VALUES (:id,:ws,:wo,:desc,:at,:loc,:site,:dept,:sd,:ed,:now,:now) ON CONFLICT (id) DO NOTHING"
                ), {"id": woa_id, "ws": rc(["Draft","Submitted","Approved","Release","in_progress","completed"]),
                    "wo": rc(wo_ids), "desc": f"Activity for {rc(wo_ids)}",
                    "at": rc(LABORS), "loc": rc([f"LOC-{str(k).zfill(4)}" for k in range(1,60)]),
                    "site": rc(SITES), "dept": rc(DEPARTMENTS),
                    "sd": sd, "ed": sd + timedelta(hours=random.randint(1,48)), "now": NOW})
            _update_series(conn, "WOA", woa_start + 50)
            print(f"  Created {len(woa_ids)} work order activities")
        else:
            print(f"  Found {len(woa_ids)} existing work order activities")

        # Get checklist IDs
        cl_ids = [r[0] for r in conn.execute(text("SELECT id FROM checklist ORDER BY id")).fetchall()]
        if not cl_ids:
            # Create some checklists
            print("  No checklists found, creating some...")
            cl_start = 1
            cl_items_base = [
                "Visual inspection completed", "Equipment cleaned", "Safety guards in place",
                "Emergency stop functional", "Parameters within spec", "Connections secure",
                "No unusual noise", "Lubrication adequate", "Documentation updated", "Operator notified",
            ]
            cl_names = [
                "HVAC Pre-Start Checklist", "Generator Monthly Inspection", "Elevator Safety Check",
                "Fire Extinguisher Monthly", "Medical Gas Daily Check", "Autoclave Validation",
                "Patient Monitor Test", "Ventilator Pre-Use", "Defibrillator Daily Check",
                "Surgical Light Pre-Op", "CT Scanner Daily QA", "MRI Safety Checklist",
                "X-Ray Room Safety", "Infusion Pump Pre-Use", "Lab Equipment Daily QA",
                "Blood Bank Fridge Log", "Pharmacy Cold Storage", "UPS System Daily Check",
                "Boiler Daily Inspection", "Chiller Operator Log", "Cooling Tower Weekly",
                "Electrical Panel Scan", "BMS Alarm Check", "CCTV System Test",
                "Nurse Call System Test",
            ]
            cld_counter = 1
            for ci in range(25):
                cl_id = f"CHL-{str(cl_start+ci).zfill(5)}"
                cl_ids.append(cl_id)
                conn.execute(text(
                    "INSERT INTO checklist (id, checklist_name, checklist_type, created_at, updated_at) "
                    "VALUES (:id,:name,:ctype,:now,:now) ON CONFLICT (id) DO NOTHING"
                ), {"id": cl_id, "name": cl_names[ci], "ctype": rc(["Pre-Use","Inspection","Maintenance","Safety","Calibration"]), "now": NOW})
                for item_name in random.sample(cl_items_base, random.randint(5, 8)):
                    conn.execute(text(
                        "INSERT INTO checklist_details (id, checklist, item_name, is_mandatory, created_at, updated_at) "
                        "VALUES (:id,:cl,:name,:m,:now,:now) ON CONFLICT (id) DO NOTHING"
                    ), {"id": f"CHLD-{str(cld_counter).zfill(5)}", "cl": cl_id,
                        "name": item_name, "m": random.random() > 0.3, "now": NOW})
                    cld_counter += 1
            _update_series(conn, "CHL", cl_start + 25)
            _update_series(conn, "CHLD", cld_counter)
            print(f"  Created {len(cl_ids)} checklists")

        # ============================================================
        # 8) WORK ORDER CHECKLISTS (50) + Checklist Details
        # ============================================================
        print("Seeding Work Order Checklists...")
        wochk_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_checklist")).scalar()
        wochk_start = max(wochk_max + 1, 1)
        wochkd_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_checklist_detail")).scalar()
        wochkd_counter = max(wochkd_max + 1, 1)
        wochk_ids = []

        checklist_items = [
            "Visual inspection of equipment exterior",
            "Check all electrical connections and wiring",
            "Verify safety interlocks are functional",
            "Test emergency stop mechanism",
            "Measure operating temperature within range",
            "Check fluid/gas levels and top up if needed",
            "Inspect belts, hoses, and seals for wear",
            "Verify calibration is current and accurate",
            "Clean equipment surfaces and filters",
            "Test alarm systems and indicators",
            "Document serial numbers and readings",
            "Verify proper labeling and tagging",
            "Check grounding and bonding connections",
            "Inspect for leaks (water, gas, oil)",
            "Run functional test cycle",
        ]

        for i in range(50):
            wochk_id = f"WOCHK-{str(wochk_start+i).zfill(5)}"
            wochk_ids.append(wochk_id)
            conn.execute(text(
                "INSERT INTO work_order_checklist (id, work_order_activity, checklist, inspector_id, "
                "inspection_date, remarks, status, created_at, updated_at) "
                "VALUES (:id,:woa,:cl,:insp,:idate,:rem,:status,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": wochk_id, "woa": rc(woa_ids), "cl": rc(cl_ids),
                "insp": rc(EMPLOYEES), "idate": rand_date(120, 0),
                "rem": rc(["All items passed","Minor issues noted - see details","Follow-up required","Equipment performing well",""]),
                "status": rc(CHECKLIST_STATUSES), "now": NOW})

            # 5-10 checklist detail items per checklist
            for j in range(random.randint(5, 10)):
                wochkd_id = f"WOCHKD-{str(wochkd_counter).zfill(5)}"
                wochkd_counter += 1
                conn.execute(text(
                    "INSERT INTO work_order_checklist_detail (id, work_order_checklist, item_name, "
                    "is_mandatory, remarks, status, created_at, updated_at) "
                    "VALUES (:id,:wochk,:item,:mand,:rem,:status,:now,:now) ON CONFLICT (id) DO NOTHING"
                ), {"id": wochkd_id, "wochk": wochk_id,
                    "item": checklist_items[j % len(checklist_items)],
                    "mand": random.random() > 0.3,
                    "rem": rc(["OK","Satisfactory","Needs attention","Within spec","N/A",""]),
                    "status": rc(CHECKLIST_DETAIL_STATUSES), "now": NOW})

        _update_series(conn, "WOCHK", wochk_start + 50)
        _update_series(conn, "WOCHKD", wochkd_counter)
        print(f"  Created {len(wochk_ids)} work order checklists with details")

        # ============================================================
        # 9) WORK ORDER ACTIVITY LOGS (50)
        # ============================================================
        print("Seeding Work Order Activity Logs...")
        wolog_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_activity_logs")).scalar()
        wolog_start = max(wolog_max + 1, 1)
        wolog_count = 0
        for i in range(50):
            wolog_id = f"WOLOG-{str(wolog_start+i).zfill(5)}"
            wolog_count += 1
            conn.execute(text(
                "INSERT INTO work_order_activity_logs (id, work_order_activity, date, log, created_at, updated_at) "
                "VALUES (:id,:woa,:d,:log,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": wolog_id, "woa": rc(woa_ids),
                "d": rand_date(120, 0),
                "log": rc(WO_LOG_ENTRIES), "now": NOW})
        _update_series(conn, "WOLOG", wolog_start + 50)
        print(f"  Created {wolog_count} work order activity logs")

        # ============================================================
        # 10) WORK ORDER EQUIPMENT (50)
        # ============================================================
        print("Seeding Work Order Equipment...")
        woeqp_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_equipment")).scalar()
        woeqp_start = max(woeqp_max + 1, 1)
        woeqp_ids = []
        for i in range(50):
            woeqp_id = f"WOEQP-{str(woeqp_start+i).zfill(5)}"
            woeqp_ids.append(woeqp_id)
            sd = rand_dt(120, 5)
            hrs = round(random.uniform(0.5, 16), 1)
            conn.execute(text(
                "INSERT INTO work_order_equipment (id, workflow_state, work_order_activity, item, "
                "start_datetime, end_datetime, total_hours_used, estimated_hours, created_at, updated_at) "
                "VALUES (:id,:ws,:woa,:item,:sd,:ed,:hrs,:est,:now,:now) ON CONFLICT (id) DO NOTHING"
            ), {"id": woeqp_id, "ws": rc(["Draft","In Progress","Completed"]),
                "woa": rc(woa_ids), "item": rc(ITEMS),
                "sd": sd, "ed": sd + timedelta(hours=int(hrs)),
                "hrs": hrs, "est": round(hrs * random.uniform(0.8, 1.5), 1), "now": NOW})
        _update_series(conn, "WOEQP", woeqp_start + 50)
        print(f"  Created {len(woeqp_ids)} work order equipment entries")

        # ============================================================
        # 11) WORK ORDER LABOR (50)
        # ============================================================
        print("Seeding Work Order Labor...")
        wolbr_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_labor")).scalar()
        wolbr_start = max(wolbr_max + 1, 1)
        wolbr_ids = []
        for i in range(50):
            wolbr_id = f"WOLBR-{str(wolbr_start+i).zfill(5)}"
            wolbr_ids.append(wolbr_id)
            sd = rand_dt(120, 5)
            hrs = round(random.uniform(1, 12), 1)
            trd = rc(trade_ids)
            lbr = rc(LABORS)
            conn.execute(text(
                "INSERT INTO work_order_labor (id, workflow_state, work_order_activity, trade, labor, "
                "laborer, lead, start_datetime, end_datetime, total_hours_used, estimated_hours, created_at, updated_at) "
                "VALUES (:id,:ws,:woa,:trd,:lbr,:laborer,:lead,:sd,:ed,:hrs,:est,:now,:now) "
                "ON CONFLICT (id) DO NOTHING"
            ), {"id": wolbr_id, "ws": rc(WO_PARTS_STATES),
                "woa": rc(woa_ids), "trd": trd, "lbr": lbr,
                "laborer": f"Laborer {lbr}", "lead": random.random() > 0.7,
                "sd": sd, "ed": sd + timedelta(hours=int(hrs)),
                "hrs": hrs, "est": round(hrs * random.uniform(0.8, 1.5), 1), "now": NOW})
        _update_series(conn, "WOLBR", wolbr_start + 50)
        print(f"  Created {len(wolbr_ids)} work order labor entries")

        # ============================================================
        # 12) WORK ORDER LABOR ACTUAL HOURS (50)
        # ============================================================
        print("Seeding Work Order Labor Actual Hours...")
        wlahr_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_labor_actual_hours")).scalar()
        wlahr_start = max(wlahr_max + 1, 1)
        wlahr_count = 0
        for i in range(50):
            wlahr_id = f"WLAHR-{str(wlahr_start+i).zfill(5)}"
            wlahr_count += 1
            conn.execute(text(
                "INSERT INTO work_order_labor_actual_hours (id, wo_labor_id, date, time, reason, "
                "comment, site, department, cost_code, created_at, updated_at) "
                "VALUES (:id,:wl,:d,:t,:reason,:comment,:site,:dept,:cc,:now,:now) "
                "ON CONFLICT (id) DO NOTHING"
            ), {"id": wlahr_id, "wl": rc(wolbr_ids),
                "d": rand_date(90, 0), "t": f"{random.randint(1,8)}.{random.randint(0,5)} hrs",
                "reason": rc(["Regular work","Overtime","Emergency call-out","Standby","Training"]),
                "comment": rc(WO_LOG_ENTRIES[:10]),
                "site": rc(SITES), "dept": rc(DEPARTMENTS), "cc": rc(COST_CODES), "now": NOW})
        _update_series(conn, "WLAHR", wlahr_start + 50)
        print(f"  Created {wlahr_count} work order labor actual hours")

        # ============================================================
        # 13) WORK ORDER PARTS (50)
        # ============================================================
        print("Seeding Work Order Parts...")
        wopart_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_parts")).scalar()
        wopart_start = max(wopart_max + 1, 1)
        wopart_ids = []
        for i in range(50):
            wopart_id = f"WOPART-{str(wopart_start+i).zfill(5)}"
            wopart_ids.append(wopart_id)
            qty_req = random.randint(1, 20)
            qty_iss = random.randint(0, qty_req)
            qty_ret = random.randint(0, max(qty_iss - 1, 0))
            conn.execute(text(
                "INSERT INTO work_order_parts (id, workflow_state, work_order_activity, item, "
                "unit_of_measure, total_actual_qty, total_avail_qty, date_required, "
                "quantity_required, quantity_issued, quantity_returned, created_at, updated_at) "
                "VALUES (:id,:ws,:woa,:item,:uom,:taq,:tavq,:dr,:qr,:qi,:qret,:now,:now) "
                "ON CONFLICT (id) DO NOTHING"
            ), {"id": wopart_id, "ws": rc(WO_PARTS_STATES),
                "woa": rc(woa_ids), "item": rc(ITEMS),
                "uom": rc(UOM), "taq": qty_iss - qty_ret,
                "tavq": random.randint(10, 100),
                "dr": rand_date(60, 0), "qr": qty_req, "qi": qty_iss, "qret": qty_ret,
                "now": NOW})
        _update_series(conn, "WOPART", wopart_start + 50)
        print(f"  Created {len(wopart_ids)} work order parts")

        # ============================================================
        # 14) WORK ORDER PARTS RESERVATION (50)
        # ============================================================
        print("Seeding Work Order Parts Reservations...")
        wprs_max = conn.execute(text("SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM '[0-9]+$') AS INTEGER)),0) FROM work_order_parts_reservation")).scalar()
        wprs_start = max(wprs_max + 1, 1)
        wprs_count = 0
        for i in range(50):
            wprs_id = f"WPRS-{str(wprs_start+i).zfill(5)}"
            wprs_count += 1
            item = rc(ITEMS)
            conn.execute(text(
                "INSERT INTO work_order_parts_reservation (id, work_order_parts, item_id, item, "
                "unit_of_measure, inventory, date_reserved, quantity_reserved, status, created_at, updated_at) "
                "VALUES (:id,:wop,:iid,:item,:uom,:inv,:dr,:qr,:status,:now,:now) "
                "ON CONFLICT (id) DO NOTHING"
            ), {"id": wprs_id, "wop": rc(wopart_ids), "iid": item, "item": item,
                "uom": rc(UOM), "inv": rc(INVENTORIES),
                "dr": rand_dt(60, 0), "qr": round(random.uniform(1, 15), 0),
                "status": rc(RESERVATION_STATUSES), "now": NOW})
        _update_series(conn, "WPRS", wprs_start + 50)
        print(f"  Created {wprs_count} work order parts reservations")

        _print_summary(conn)


def _print_summary(conn):
    print("\n=== SEEDING COMPLETE ===")
    tables = [
        "trade", "trade_labor", "trade_availability",
        "work_schedule", "work_schedule_details", "holiday",
        "leave_type", "leave_application",
        "work_order_checklist", "work_order_checklist_detail",
        "work_order_activity_logs", "work_order_equipment",
        "work_order_labor", "work_order_labor_actual_hours",
        "work_order_parts", "work_order_parts_reservation",
    ]
    for tbl in tables:
        try:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl:45s} {count:5d} records")
        except:
            print(f"  {tbl:45s} ERROR")


if __name__ == "__main__":
    seed()
