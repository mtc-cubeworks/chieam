import asyncio
from datetime import date

from sqlalchemy import select

from app.core.database import async_session_maker
from app.core.seed import get_or_create_series
from app.models.auth import Role, User
from app.core.security import get_password_hash
from app.modules.core_eam.models.site import Site
from app.modules.core_eam.models.department import Department
from app.modules.core_eam.models.manufacturer import Manufacturer
from app.modules.core_eam.models.model import Model
from app.modules.asset_management.models.location import Location
from app.modules.asset_management.models.location_type import LocationType
from app.modules.asset_management.models.system import System
from app.modules.asset_management.models.system_type import SystemType
from app.modules.asset_management.models.asset_class import AssetClass
from app.modules.asset_management.models.asset import Asset
from app.modules.asset_management.models.property_type import PropertyType
from app.modules.asset_management.models.property import Property
from app.modules.asset_management.models.asset_property import AssetProperty
from app.modules.purchasing_stores.models.unit_of_measure import UnitOfMeasure


async def ensure_named_series(db, name: str):
    return await get_or_create_series(db, name)


async def next_id(db, series_name: str, prefix: str, width: int = 4) -> str:
    series = await ensure_named_series(db, series_name)
    series.current += 1
    await db.flush()
    return f"{prefix}-{str(series.current).zfill(width)}"


async def get_by_name(db, model, field_name: str, value: str):
    result = await db.execute(select(model).where(getattr(model, field_name) == value))
    return result.scalar_one_or_none()


async def ensure_role(db, name: str, description: str):
    role = await get_by_name(db, Role, "name", name)
    if role:
        return role
    role = Role(name=name, description=description, is_active=True)
    db.add(role)
    await db.flush()
    return role


async def ensure_admin(db):
    admin = await get_by_name(db, User, "username", "admin")
    if admin:
        if not admin.is_superuser:
            admin.is_superuser = True
        if not admin.is_active:
            admin.is_active = True
        await db.flush()
        return admin

    system_manager = await ensure_role(db, "SystemManager", "Full system access")
    admin = User(
        username="admin",
        email="admin@spmceam.local",
        full_name="SPMC System Administrator",
        first_name="SPMC",
        last_name="Administrator",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        department="Facilities Engineering"
    )
    admin.roles.append(system_manager)
    db.add(admin)
    await db.flush()
    return admin


async def ensure_site(db, site_name: str, site_code: str):
    result = await db.execute(select(Site).where(Site.site_code == site_code))
    site = result.scalar_one_or_none()
    if site:
        return site
    site = Site(
        id=await next_id(db, "SITE", "SITE"),
        site_name=site_name,
        site_code=site_code,
    )
    db.add(site)
    await db.flush()
    return site


async def ensure_department(db, site_id: str, site_name: str, department_name: str, department_code: str):
    result = await db.execute(select(Department).where(Department.department_code == department_code))
    dept = result.scalar_one_or_none()
    if dept:
        return dept
    dept = Department(
        id=await next_id(db, "DEPT", "DEPT"),
        department_name=department_name,
        department_code=department_code,
        site=site_id,
        site_name=site_name,
    )
    db.add(dept)
    await db.flush()
    return dept


async def ensure_location_type(db, name: str):
    result = await db.execute(select(LocationType).where(LocationType.name == name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = LocationType(id=await next_id(db, "LT", "LT"), name=name)
    db.add(row)
    await db.flush()
    return row


async def ensure_system_type(db, name: str):
    result = await db.execute(select(SystemType).where(SystemType.name == name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = SystemType(id=await next_id(db, "ST", "ST"), name=name)
    db.add(row)
    await db.flush()
    return row


async def ensure_asset_class(db, name: str, description: str, parent_asset_class: str | None = None):
    result = await db.execute(select(AssetClass).where(AssetClass.name == name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = AssetClass(
        id=await next_id(db, "AC", "AC"),
        name=name,
        description=description,
        parent_asset_class=parent_asset_class,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_manufacturer(db, company_name: str):
    result = await db.execute(select(Manufacturer).where(Manufacturer.company_name == company_name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = Manufacturer(id=await next_id(db, "MFR", "MFR", 5), company_name=company_name)
    db.add(row)
    await db.flush()
    return row


async def ensure_model(db, manufacturer, model_name: str):
    result = await db.execute(
        select(Model).where(Model.model_name == model_name, Model.manufacturer == manufacturer.id)
    )
    row = result.scalar_one_or_none()
    if row:
        return row
    row = Model(
        id=await next_id(db, "M", "M", 5),
        model_name=model_name,
        manufacturer=manufacturer.id,
        manufacturer_name=manufacturer.company_name,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_uom(db, name: str, short_name: str):
    result = await db.execute(select(UnitOfMeasure).where(UnitOfMeasure.short_name == short_name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = UnitOfMeasure(id=await next_id(db, "UOM", "UOM"), name=name, short_name=short_name)
    db.add(row)
    await db.flush()
    return row


async def ensure_property_type(db, name: str):
    result = await db.execute(select(PropertyType).where(PropertyType.name == name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = PropertyType(id=await next_id(db, "PT", "PT"), name=name)
    db.add(row)
    await db.flush()
    return row


async def ensure_property(db, name: str, description: str, property_type, unit_of_measure=None):
    result = await db.execute(select(Property).where(Property.name == name))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = Property(
        id=await next_id(db, "PROP", "PROP"),
        name=name,
        description=description,
        property_type=property_type.id,
        unit_of_measure=unit_of_measure.id if unit_of_measure else None,
        system=False,
        inactive=False,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_location(db, name: str, description: str, location_type, site, parent_location=None, address: str | None = None):
    result = await db.execute(
        select(Location).where(
            Location.name == name,
            Location.site == site.id,
            Location.parent_location == (parent_location.id if parent_location else None),
        )
    )
    row = result.scalar_one_or_none()
    if row:
        return row
    row = Location(
        id=await next_id(db, "LOC", "LOC"),
        name=name,
        description=description,
        location_type=location_type.id,
        location_type_name=location_type.name,
        parent_location=parent_location.id if parent_location else None,
        site=site.id,
        address=address,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_system(db, name: str, description: str, system_type, site, location, parent_system=None):
    result = await db.execute(
        select(System).where(
            System.name == name,
            System.location == location.id,
            System.site == site.id,
            System.parent_system == (parent_system.id if parent_system else None),
        )
    )
    row = result.scalar_one_or_none()
    if row:
        return row
    row = System(
        id=await next_id(db, "SYS", "SYS"),
        name=name,
        description=description,
        system_type=system_type.id,
        system_type_name=system_type.name,
        parent_system=parent_system.id if parent_system else None,
        location=location.id,
        site=site.id,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_asset(db, payload: dict):
    result = await db.execute(select(Asset).where(Asset.asset_tag == payload["asset_tag"]))
    row = result.scalar_one_or_none()
    if row:
        return row
    row = Asset(
        id=await next_id(db, "A", "A", 5),
        workflow_state="active",
        asset_tag=payload["asset_tag"],
        asset_class=payload["asset_class"].id,
        description=payload["description"],
        series=payload["asset_tag"].split("-")[2],
        model=payload["model"].id,
        serial_number=payload["serial_number"],
        date_purchased=payload["date_purchased"],
        cost=payload["cost"],
        block_number=payload["block_number"],
        number_of_repairs=0,
        location=payload["location"].id,
        site=payload["site"].id,
        department=payload["department"].id,
        system=payload["system"].id,
        defective=False,
        is_equipment=True,
        need_repair=False,
        bypass_process=True,
    )
    db.add(row)
    await db.flush()
    return row


async def ensure_asset_property(db, asset, prop, value: str, property_type, unit_of_measure=None):
    result = await db.execute(
        select(AssetProperty).where(AssetProperty.asset == asset.id, AssetProperty.property == prop.id)
    )
    row = result.scalar_one_or_none()
    if row:
        row.property_value = value
        row.property_type = property_type.name
        row.unit_of_measure = unit_of_measure.id if unit_of_measure else None
        await db.flush()
        return row
    row = AssetProperty(
        id=await next_id(db, "APR", "APR"),
        asset=asset.id,
        property=prop.id,
        property_value=value,
        unit_of_measure=unit_of_measure.id if unit_of_measure else None,
        property_type=property_type.name,
    )
    db.add(row)
    await db.flush()
    return row


async def main():
    async with async_session_maker() as db:
        await ensure_role(db, "SystemManager", "Full system access")
        await ensure_role(db, "Technician", "CRUD access to modules")
        await ensure_role(db, "Viewer", "Read-only access")
        await ensure_admin(db)

        site = await ensure_site(db, "Southern Philippines Medical Center", "SPMC")

        departments = {}
        for code, name in [
            ("DEPT-FE", "Facilities Engineering"),
            ("DEPT-BIOMED", "Biomedical Engineering"),
            ("DEPT-IT", "Information Technology"),
            ("DEPT-RAD", "Radiology"),
            ("DEPT-CARD", "Cardiology"),
            ("DEPT-NEPH", "Nephrology and Transplant"),
            ("DEPT-ONC", "Oncology"),
            ("DEPT-WOM", "Women and Newborn Care"),
            ("DEPT-PED", "Pediatrics"),
            ("DEPT-TRAUMA", "Trauma and Emergency"),
            ("DEPT-ICU", "Critical Care"),
            ("DEPT-OPD", "Outpatient Services"),
            ("DEPT-IPBM", "Psychiatry and Behavioral Medicine"),
        ]:
            departments[code] = await ensure_department(db, site.id, site.site_name, name, code)

        location_types = {}
        for name in ["Building", "Floor", "Room", "Area"]:
            location_types[name] = await ensure_location_type(db, name)

        system_types = {}
        for name in ["HVAC", "Electrical", "Plumbing", "Medical Gas", "IT Network", "Vertical Transport", "Imaging", "Dialysis", "Fire Safety", "Power Generation"]:
            system_types[name] = await ensure_system_type(db, name)

        category_parent = {}
        for name in ["Mechanical", "Electrical", "Plumbing", "Medical", "IT"]:
            category_parent[name] = await ensure_asset_class(db, name, f"{name} hospital assets")

        asset_classes = {
            "AHU": await ensure_asset_class(db, "Air Handling Unit", "Hospital air handling unit", category_parent["Mechanical"].id),
            "GEN": await ensure_asset_class(db, "Backup Generator", "Emergency power generator", category_parent["Electrical"].id),
            "UPS": await ensure_asset_class(db, "UPS", "Uninterruptible power supply", category_parent["Electrical"].id),
            "ELV": await ensure_asset_class(db, "Elevator", "Patient/service elevator", category_parent["Mechanical"].id),
            "MGS": await ensure_asset_class(db, "Medical Gas Manifold", "Medical gas manifold system", category_parent["Plumbing"].id),
            "MRI": await ensure_asset_class(db, "MRI Machine", "Magnetic resonance imaging machine", category_parent["Medical"].id),
            "DIA": await ensure_asset_class(db, "Dialysis Machine", "Hemodialysis machine", category_parent["Medical"].id),
            "SW": await ensure_asset_class(db, "Core Network Switch", "Managed network switch", category_parent["IT"].id),
        }

        manufacturers = {}
        for name in ["Carrier", "Cummins", "Otis", "GE Healthcare", "Fresenius", "Cisco", "Drager", "Schneider Electric"]:
            manufacturers[name] = await ensure_manufacturer(db, name)

        models = {
            "AHU-39HQM": await ensure_model(db, manufacturers["Carrier"], "39HQM"),
            "GEN-C2750D5": await ensure_model(db, manufacturers["Cummins"], "C2750D5"),
            "UPS-GVL500": await ensure_model(db, manufacturers["Schneider Electric"], "Galaxy VL 500"),
            "ELV-GEN2": await ensure_model(db, manufacturers["Otis"], "Gen2 Premier"),
            "MGS-AVSU": await ensure_model(db, manufacturers["Drager"], "AVSU-ICU"),
            "MRI-SIGNA": await ensure_model(db, manufacturers["GE Healthcare"], "SIGNA Explorer 1.5T"),
            "DIA-5008S": await ensure_model(db, manufacturers["Fresenius"], "5008S CorDiax"),
            "SW-C9300": await ensure_model(db, manufacturers["Cisco"], "Catalyst 9300-48P"),
        }

        text_property_type = await ensure_property_type(db, "Text")
        numeric_property_type = await ensure_property_type(db, "Number")
        score_uom = await ensure_uom(db, "Score", "pts")
        year_uom = await ensure_uom(db, "Years", "yr")
        criticality_prop = await ensure_property(db, "Criticality Score", "1-5 hospital safety criticality score", numeric_property_type, score_uom)
        pm_prop = await ensure_property(db, "PM Frequency", "Preventive maintenance frequency", text_property_type)
        eul_prop = await ensure_property(db, "Expected Useful Life", "Expected useful life in years", numeric_property_type, year_uom)

        building_specs = [
            {"code": "MB", "name": "Main Building", "floors": ["Ground Floor", "2nd Floor", "3rd Floor"], "dept": "DEPT-FE"},
            {"code": "MAB", "name": "Medical Arts Building", "floors": ["Ground Floor", "3rd Floor", "7th Floor"], "dept": "DEPT-OPD"},
            {"code": "MHC", "name": "Mindanao Heart Center", "floors": ["Ground Floor", "2nd Floor", "3rd Floor"], "dept": "DEPT-CARD"},
            {"code": "KTI", "name": "Kidney and Transplant Institute", "floors": ["Ground Floor", "2nd Floor", "4th Floor", "5th Floor"], "dept": "DEPT-NEPH"},
            {"code": "CAN", "name": "Cancer Institute", "floors": ["Ground Floor", "2nd Floor", "3rd Floor"], "dept": "DEPT-ONC"},
            {"code": "IWNH", "name": "Institute for Women's Health and Newborn", "floors": ["Ground Floor", "NICU Floor", "LDR Floor", "5th Floor"], "dept": "DEPT-WOM"},
            {"code": "CHI", "name": "Children's Institute", "floors": ["Ground Floor", "2nd Floor", "4th Floor", "5th Floor"], "dept": "DEPT-PED"},
            {"code": "ORI", "name": "Orthopedic and Rehab Institute", "floors": ["Ground Floor", "2nd Floor", "4th Floor"], "dept": "DEPT-FE"},
            {"code": "TRA", "name": "Trauma Complex", "floors": ["Ground Floor", "2nd Floor", "4th Floor"], "dept": "DEPT-TRAUMA"},
            {"code": "OPD", "name": "JICA OPD Building", "floors": ["Ground Floor", "2nd Floor"], "dept": "DEPT-OPD"},
            {"code": "ICU", "name": "Central ICU Building", "floors": ["Ground Floor", "2nd Floor", "5th Floor"], "dept": "DEPT-ICU"},
            {"code": "ISO", "name": "Isolation Facility Building", "floors": ["Ground Floor", "2nd Floor"], "dept": "DEPT-ICU"},
            {"code": "IPBM", "name": "Institute for Psychiatry and Behavioral Medicine", "floors": ["Ground Floor", "2nd Floor"], "dept": "DEPT-IPBM"},
            {"code": "ACB", "name": "Acute Care Building", "floors": ["Ground Floor", "2nd Floor", "3rd Floor"], "dept": "DEPT-TRAUMA"},
        ]

        systems_by_building = {}
        floor_locations = {}
        for spec in building_specs:
            building = await ensure_location(
                db,
                spec["name"],
                f"SPMC facility building: {spec['name']}",
                location_types["Building"],
                site,
                None,
                f"Southern Philippines Medical Center, Davao City - {spec['name']}",
            )
            floor_locations[spec["code"]] = []
            for floor_name in spec["floors"]:
                floor = await ensure_location(
                    db,
                    f"{spec['code']} {floor_name}",
                    f"{floor_name} of {spec['name']}",
                    location_types["Floor"],
                    site,
                    building,
                    f"{spec['name']}, {floor_name}",
                )
                floor_locations[spec["code"]].append(floor)

            systems_by_building[spec["code"]] = {
                "hvac": await ensure_system(db, f"{spec['code']} HVAC System", f"Primary HVAC system for {spec['name']}", system_types["HVAC"], site, building),
                "power": await ensure_system(db, f"{spec['code']} Electrical Power System", f"Primary electrical distribution for {spec['name']}", system_types["Electrical"], site, building),
                "medgas": await ensure_system(db, f"{spec['code']} Medical Gas System", f"Medical gas reticulation for {spec['name']}", system_types["Medical Gas"], site, building),
                "it": await ensure_system(db, f"{spec['code']} IT Network System", f"Core IT network for {spec['name']}", system_types["IT Network"], site, building),
            }
            if spec["code"] not in {"ISO", "IPBM"}:
                systems_by_building[spec["code"]]["elevator"] = await ensure_system(db, f"{spec['code']} Vertical Transport System", f"Elevator transport system for {spec['name']}", system_types["Vertical Transport"], site, building)

        def build_asset_records():
            records = []
            for spec in building_specs:
                code = spec["code"]
                dept = departments[spec["dept"]]
                ground = floor_locations[code][0]
                top = floor_locations[code][-1]
                systems = systems_by_building[code]
                base_year = 2020 if code in {"MB", "MAB", "MHC"} else 2022

                records.append({
                    "asset_tag": f"SPMC-{code}-HVAC-001",
                    "description": f"AHU serving {spec['name']} main air distribution",
                    "asset_class": asset_classes["AHU"],
                    "model": models["AHU-39HQM"],
                    "serial_number": f"{code}-AHU-001",
                    "date_purchased": date(base_year, 1, 15),
                    "cost": 1450000.0,
                    "block_number": 1,
                    "location": top,
                    "site": site,
                    "department": dept,
                    "system": systems["hvac"],
                    "criticality": "5",
                    "pm_frequency": "Monthly",
                    "eul": "15",
                })
                records.append({
                    "asset_tag": f"SPMC-{code}-ELEC-001",
                    "description": f"Emergency backup generator for {spec['name']}",
                    "asset_class": asset_classes["GEN"],
                    "model": models["GEN-C2750D5"],
                    "serial_number": f"{code}-GEN-001",
                    "date_purchased": date(base_year, 2, 10),
                    "cost": 5200000.0,
                    "block_number": 1,
                    "location": ground,
                    "site": site,
                    "department": dept,
                    "system": systems["power"],
                    "criticality": "5",
                    "pm_frequency": "Monthly",
                    "eul": "20",
                })
                records.append({
                    "asset_tag": f"SPMC-{code}-MGS-001",
                    "description": f"Medical gas manifold and alarm panel for {spec['name']}",
                    "asset_class": asset_classes["MGS"],
                    "model": models["MGS-AVSU"],
                    "serial_number": f"{code}-MGS-001",
                    "date_purchased": date(base_year, 3, 5),
                    "cost": 780000.0,
                    "block_number": 1,
                    "location": ground,
                    "site": site,
                    "department": dept,
                    "system": systems["medgas"],
                    "criticality": "5",
                    "pm_frequency": "Quarterly",
                    "eul": "12",
                })
                records.append({
                    "asset_tag": f"SPMC-{code}-IT-001",
                    "description": f"Core network switch stack for {spec['name']}",
                    "asset_class": asset_classes["SW"],
                    "model": models["SW-C9300"],
                    "serial_number": f"{code}-SW-001",
                    "date_purchased": date(base_year, 4, 20),
                    "cost": 420000.0,
                    "block_number": 1,
                    "location": ground,
                    "site": site,
                    "department": departments["DEPT-IT"],
                    "system": systems["it"],
                    "criticality": "4",
                    "pm_frequency": "Quarterly",
                    "eul": "8",
                })
                if "elevator" in systems:
                    records.append({
                        "asset_tag": f"SPMC-{code}-ELV-001",
                        "description": f"Patient/service elevator for {spec['name']}",
                        "asset_class": asset_classes["ELV"],
                        "model": models["ELV-GEN2"],
                        "serial_number": f"{code}-ELV-001",
                        "date_purchased": date(base_year, 5, 12),
                        "cost": 3100000.0,
                        "block_number": 1,
                        "location": ground,
                        "site": site,
                        "department": dept,
                        "system": systems["elevator"],
                        "criticality": "4",
                        "pm_frequency": "Monthly",
                        "eul": "20",
                    })

            kti_floor = floor_locations["KTI"][1]
            can_floor = floor_locations["CAN"][1]
            mhc_floor = floor_locations["MHC"][1]
            records.extend([
                {
                    "asset_tag": "SPMC-KTI-DIA-001",
                    "description": "Dialysis machine station 01 for Kidney and Transplant Institute",
                    "asset_class": asset_classes["DIA"],
                    "model": models["DIA-5008S"],
                    "serial_number": "KTI-DIA-001",
                    "date_purchased": date(2023, 1, 15),
                    "cost": 1450000.0,
                    "block_number": 2,
                    "location": kti_floor,
                    "site": site,
                    "department": departments["DEPT-NEPH"],
                    "system": systems_by_building["KTI"]["medgas"],
                    "criticality": "5",
                    "pm_frequency": "Monthly",
                    "eul": "10",
                },
                {
                    "asset_tag": "SPMC-KTI-DIA-002",
                    "description": "Dialysis machine station 02 for Kidney and Transplant Institute",
                    "asset_class": asset_classes["DIA"],
                    "model": models["DIA-5008S"],
                    "serial_number": "KTI-DIA-002",
                    "date_purchased": date(2023, 1, 15),
                    "cost": 1450000.0,
                    "block_number": 2,
                    "location": kti_floor,
                    "site": site,
                    "department": departments["DEPT-NEPH"],
                    "system": systems_by_building["KTI"]["medgas"],
                    "criticality": "5",
                    "pm_frequency": "Monthly",
                    "eul": "10",
                },
                {
                    "asset_tag": "SPMC-CAN-MRI-001",
                    "description": "MRI machine for Cancer Institute imaging suite",
                    "asset_class": asset_classes["MRI"],
                    "model": models["MRI-SIGNA"],
                    "serial_number": "CAN-MRI-001",
                    "date_purchased": date(2024, 6, 1),
                    "cost": 68500000.0,
                    "block_number": 3,
                    "location": can_floor,
                    "site": site,
                    "department": departments["DEPT-RAD"],
                    "system": systems_by_building["CAN"]["power"],
                    "criticality": "5",
                    "pm_frequency": "Quarterly",
                    "eul": "12",
                },
                {
                    "asset_tag": "SPMC-MHC-UPS-001",
                    "description": "Cardiac cath lab UPS for Mindanao Heart Center",
                    "asset_class": asset_classes["UPS"],
                    "model": models["UPS-GVL500"],
                    "serial_number": "MHC-UPS-001",
                    "date_purchased": date(2022, 9, 12),
                    "cost": 2250000.0,
                    "block_number": 2,
                    "location": mhc_floor,
                    "site": site,
                    "department": departments["DEPT-CARD"],
                    "system": systems_by_building["MHC"]["power"],
                    "criticality": "5",
                    "pm_frequency": "Monthly",
                    "eul": "10",
                },
            ])
            return records

        for record in build_asset_records():
            asset = await ensure_asset(db, record)
            await ensure_asset_property(db, asset, criticality_prop, record["criticality"], numeric_property_type, score_uom)
            await ensure_asset_property(db, asset, pm_prop, record["pm_frequency"], text_property_type)
            await ensure_asset_property(db, asset, eul_prop, record["eul"], numeric_property_type, year_uom)

        await db.commit()
        print("✅ SPMC hospital seed complete")


if __name__ == "__main__":
    asyncio.run(main())
