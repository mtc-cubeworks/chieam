"""
Seed Data Module
================
Consolidated seed data for initial setup and testing.

Sections:
- Core: Roles, Users, Permissions
- Workflow: States, Actions, Workflows
- EAM: Sites, Departments, Trades, etc.
- Asset Management: Asset Classes, Locations, Systems
- Purchasing: Items, Stores, Inventory
- Maintenance: Activities
- Work Management: Work Orders (future)

Last Updated: 2026-01-29
"""
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from app.core.config import settings
from app.models.auth import User, Role, EntityPermission
from app.models.workflow import (
    WorkflowState, WorkflowAction, Workflow, WorkflowStateLink, WorkflowTransition, generate_slug
)


# =============================================================================
# HELPERS
# =============================================================================

async def get_or_create_series(db: AsyncSession, name: str, current: int = 0):
    """Get or create a naming series."""
    from app.modules.core_eam.models.series import Series
    result = await db.execute(select(Series).where(Series.name == name))
    series = result.scalar_one_or_none()
    if not series:
        series = Series(name=name, current=current)
        db.add(series)
        await db.flush()
    return series


# =============================================================================
# CORE: ROLES & USERS
# =============================================================================


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def seed_roles(db: AsyncSession):
    """Create default roles with RBAC permissions and data scopes."""
    roles_data = [
        # General roles
        {"name": "SystemManager", "description": "Full system access - can do everything", "data_scope": "all"},
        {"name": "Executive", "description": "Read access to all data across all sites", "data_scope": "all"},
        {"name": "SiteManager", "description": "Full access within assigned site(s)", "data_scope": "site"},
        {"name": "Supervisor", "description": "Access to own department/team data", "data_scope": "team"},
        {"name": "Technician", "description": "CRUD access to own records within modules", "data_scope": "own"},
        {"name": "Viewer", "description": "Read-only access to own site data", "data_scope": "site"},
        # Asset management roles
        {"name": "AssetManager", "description": "Manage assets, locations, systems within assigned site(s)", "data_scope": "site"},
        # Procurement & stores roles
        {"name": "PurchaseManager", "description": "Approve and manage all procurement within site(s)", "data_scope": "site"},
        {"name": "Buyer", "description": "Create and manage purchase orders, RFQs, vendor invoices", "data_scope": "site"},
        {"name": "Requisitioner", "description": "Create purchase requests and view order status", "data_scope": "own"},
        {"name": "StoresManager", "description": "Manage inventory, stores, stock counts within site(s)", "data_scope": "site"},
        {"name": "Storekeeper", "description": "Issue, receive, transfer and count stock", "data_scope": "site"},
        # Maintenance management roles
        {"name": "MaintenanceManager", "description": "Manage all maintenance activities within assigned site(s)", "data_scope": "site"},
        {"name": "Planner", "description": "Plan and schedule maintenance activities within assigned site(s)", "data_scope": "site"},
        {"name": "MaintenanceSupervisor", "description": "Supervise maintenance team and approve work orders", "data_scope": "team"},
    ]
    
    for role_data in roles_data:
        result = await db.execute(select(Role).where(Role.name == role_data["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            role = Role(**role_data)
            db.add(role)
        else:
            # Update data_scope on existing roles if not already set
            if not existing.data_scope or existing.data_scope == "all":
                existing.data_scope = role_data["data_scope"]
    
    await db.commit()


async def seed_users(db: AsyncSession):
    """Create default users with different roles."""
    # Get roles
    result = await db.execute(select(Role).where(Role.name == "SystemManager"))
    system_manager_role = result.scalar_one_or_none()
    
    result = await db.execute(select(Role).where(Role.name == "Technician"))
    technician_role = result.scalar_one_or_none()
    
    result = await db.execute(select(Role).where(Role.name == "Viewer"))
    viewer_role = result.scalar_one_or_none()
    
    users_data = [
        {
            "username": getattr(settings, "INITIAL_ADMIN_USERNAME", "admin"),
            "email": getattr(settings, "INITIAL_ADMIN_EMAIL", "admin@example.com"),
            "full_name": getattr(settings, "INITIAL_ADMIN_FULL_NAME", "System Administrator"),
            "password": getattr(settings, "INITIAL_ADMIN_PASSWORD", "admin123"),
            "is_superuser": True,
            "role": system_manager_role,
        },
        {
            "username": getattr(settings, "INITIAL_TECHNICIAN_USERNAME", "technician"),
            "email": getattr(settings, "INITIAL_TECHNICIAN_EMAIL", "technician@example.com"),
            "full_name": getattr(settings, "INITIAL_TECHNICIAN_FULL_NAME", "Default Technician"),
            "password": getattr(settings, "INITIAL_TECHNICIAN_PASSWORD", "technician123"),
            "is_superuser": False,
            "role": technician_role,
        },
        {
            "username": getattr(settings, "INITIAL_VIEWER_USERNAME", "viewer"),
            "email": getattr(settings, "INITIAL_VIEWER_EMAIL", "viewer@example.com"),
            "full_name": getattr(settings, "INITIAL_VIEWER_FULL_NAME", "Default Viewer"),
            "password": getattr(settings, "INITIAL_VIEWER_PASSWORD", "viewer123"),
            "is_superuser": False,
            "role": viewer_role,
        },
    ]
    
    for user_data in users_data:
        result = await db.execute(select(User).where(User.username == user_data["username"]))
        if result.scalar_one_or_none():
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=hash_password(user_data["password"]),
            is_active=True,
            is_superuser=user_data["is_superuser"],
        )
        if user_data["role"]:
            user.roles.append(user_data["role"])
        
        db.add(user)
    
    await db.commit()


async def seed_global_workflow_states(db: AsyncSession) -> dict:
    """Create global workflow states. Returns dict of slug -> state for reference."""
    states_data = [
        ("Draft", "gray"),
        ("Open", "blue"),
        ("Acquired", "blue"),
        ("Inspected", "yellow"),
        ("Active", "green"),
        ("Inactive", "gray"),
        ("In Progress", "yellow"),
        ("Pending Approval", "orange"),
        ("Approved", "green"),
        ("Rejected", "red"),
        ("Closed", "gray"),
        ("Cancelled", "red"),
        ("Disposed", "red"),
    ]
    
    states_map = {}
    for label, color in states_data:
        slug = generate_slug(label)
        result = await db.execute(select(WorkflowState).where(WorkflowState.slug == slug))
        state = result.scalar_one_or_none()
        if not state:
            state = WorkflowState(label=label, slug=slug, color=color)
            db.add(state)
            await db.flush()
        states_map[slug] = state
    
    await db.commit()
    return states_map


async def seed_global_workflow_actions(db: AsyncSession) -> dict:
    """Create global workflow actions. Returns dict of slug -> action for reference."""
    actions_data = [
        "Submit",
        "Approve",
        "Reject",
        "Cancel",
        "Reopen",
        "Close",
        "Inspect",
        "Install",
        "Activate",
        "Deactivate",
        "Dispose",
        "Start",
        "Complete",
        "Putaway",
    ]
    
    actions_map = {}
    for label in actions_data:
        slug = generate_slug(label)
        result = await db.execute(select(WorkflowAction).where(WorkflowAction.slug == slug))
        action = result.scalar_one_or_none()
        if not action:
            action = WorkflowAction(label=label, slug=slug)
            db.add(action)
            await db.flush()
        actions_map[slug] = action
    
    await db.commit()
    return actions_map


async def seed_asset_workflow(db: AsyncSession):
    """Create sample workflow for Asset entity using global states/actions."""
    # Check if workflow already exists
    result = await db.execute(select(Workflow).where(Workflow.target_entity == "asset"))
    if result.scalar_one_or_none():
        return
    
    # Ensure global states and actions exist
    states_map = await seed_global_workflow_states(db)
    actions_map = await seed_global_workflow_actions(db)
    
    # Create workflow for asset
    workflow = Workflow(
        name="Asset Lifecycle",
        target_entity="asset",
        is_active=True,
    )
    db.add(workflow)
    await db.flush()
    
    # Link states to workflow
    state_slugs = ["acquired", "inspected", "active", "inactive", "disposed"]
    for i, slug in enumerate(state_slugs):
        if slug in states_map:
            link = WorkflowStateLink(
                workflow_id=workflow.id,
                state_id=states_map[slug].id,
                is_initial=(slug == "acquired"),
                sort_order=i,
            )
            db.add(link)
    
    await db.flush()
    
    # Add transitions
    transitions_data = [
        ("acquired", "inspect", "inspected"),
        ("inspected", "install", "active"),
        ("inspected", "putaway", "inactive"),
        ("active", "deactivate", "inactive"),
        ("inactive", "activate", "active"),
        ("inactive", "dispose", "disposed"),
    ]
    for from_slug, action_slug, to_slug in transitions_data:
        if from_slug in states_map and action_slug in actions_map and to_slug in states_map:
            transition = WorkflowTransition(
                workflow_id=workflow.id,
                from_state_id=states_map[from_slug].id,
                action_id=actions_map[action_slug].id,
                to_state_id=states_map[to_slug].id,
            )
            db.add(transition)
    
    await db.commit()


async def seed_entity_permissions(db: AsyncSession):
    """Create default entity permissions for all roles."""
    # Get all roles
    result = await db.execute(select(Role))
    roles = {r.name: r for r in result.scalars().all()}
    
    # Define permissions per role
    # SystemManager: full access to everything
    # Technician: CRUD on modules, no admin
    # Viewer: read only
    
    entities = ["users", "role", "asset", "location", "work_order"]
    
    permissions_config = {
        "SystemManager": {"can_read": True, "can_create": True, "can_update": True, "can_delete": True},
        "Technician": {"can_read": True, "can_create": True, "can_update": True, "can_delete": False},
        "Viewer": {"can_read": True, "can_create": False, "can_update": False, "can_delete": False},
    }
    
    for role_name, perms in permissions_config.items():
        role = roles.get(role_name)
        if not role:
            continue
        
        for entity_name in entities:
            # Skip admin entities for non-SystemManager
            if entity_name in ["users", "role"] and role_name != "SystemManager":
                continue
            
            # Check if permission already exists
            result = await db.execute(
                select(EntityPermission)
                .where(EntityPermission.role_id == role.id)
                .where(EntityPermission.entity_name == entity_name)
            )
            if result.scalar_one_or_none():
                continue
            
            perm = EntityPermission(
                role_id=role.id,
                entity_name=entity_name,
                **perms
            )
            db.add(perm)
    
    await db.commit()


async def seed_sample_todos(db: AsyncSession):
    """Create sample todo records with proper naming codes."""
    from app.modules.todo.models.todo import Todo
    from app.modules.todo.models.todo_comment import TodoComment
    from app.modules.core_eam.models.series import Series
    from sqlalchemy import select
    
    from sqlalchemy import delete
    # Remove existing comments first (foreign key constraint), then todos
    await db.execute(delete(TodoComment))
    await db.execute(delete(Todo))
    await db.commit()
    
    # Check again if table is empty
    result = await db.execute(select(Todo.id))
    existing = result.scalars().all()
    
    if len(existing) >= 5:
        return [t.id for t in existing[:5]]
    
    # Get or create series for TODO
    result = await db.execute(select(Series).where(Series.name == "TODO"))
    series = result.scalar_one_or_none()
    if not series:
        series = Series(name="TODO", current=0)
        db.add(series)
        await db.flush()
    
    from datetime import date

    sample_todos = [
        {"title": "Complete project documentation", "description": "Write comprehensive docs for the API", "status": "open", "priority": "high", "due_date": date.today(), "completed": False},
        {"title": "Review pull requests", "description": "Check and merge pending PRs", "status": "in_progress", "priority": "medium", "due_date": date.today(), "completed": False},
        {"title": "Update dependencies", "description": "Upgrade to latest package versions", "status": "open", "priority": "low", "due_date": date.today(), "completed": False},
        {"title": "Fix bug in authentication", "description": "Users can't login with special characters", "status": "open", "priority": "high", "due_date": date.today(), "completed": False},
        {"title": "Implement caching layer", "description": "Add Redis for performance", "status": "open", "priority": "medium", "due_date": date.today(), "completed": False},
    ]
    
    created_todos = []
    for todo_data in sample_todos:
        series.current += 1
        todo_id = f"TODO-{str(series.current).zfill(4)}"
        todo = Todo(id=todo_id, **todo_data)
        db.add(todo)
        created_todos.append(todo)
    
    await db.flush()
    await db.commit()
    
    # Store created todo IDs for comment seeding
    return [t.id for t in created_todos]


async def seed_sample_comments(db: AsyncSession, todo_ids: list):
    """Create sample comments linked to todos."""
    from app.modules.todo.models.todo_comment import TodoComment
    from app.modules.core_eam.models.series import Series
    from sqlalchemy import select
    
    if not todo_ids:
        return
    
    result = await db.execute(select(TodoComment))
    existing = result.scalars().all()
    
    if len(existing) >= 5:
        return
    
    # Get or create series for TC (Todo Comment)
    result = await db.execute(select(Series).where(Series.name == "TC"))
    series = result.scalar_one_or_none()
    if not series:
        series = Series(name="TC", current=0)
        db.add(series)
        await db.flush()
    
    sample_comments = [
        {"todo_id": todo_ids[0], "content": "Started working on this task.", "author": "admin"},
        {"todo_id": todo_ids[0], "content": "Need more details from the team.", "author": "admin"},
        {"todo_id": todo_ids[1], "content": "PR #42 looks good, will merge soon.", "author": "admin"},
        {"todo_id": todo_ids[2], "content": "Waiting for security review.", "author": "admin"},
        {"todo_id": todo_ids[3], "content": "This is a critical bug, prioritizing.", "author": "admin"},
    ]
    
    for comment_data in sample_comments:
        series.current += 1
        comment_id = f"TC-{str(series.current).zfill(4)}"
        comment = TodoComment(id=comment_id, **comment_data)
        db.add(comment)
    
    await db.commit()


async def seed_asset_management_data(db: AsyncSession):
    """Seed asset management data with parent-child relationships."""
    from app.modules.core_eam.models.series import Series
    from app.modules.asset_management.models.asset_class import AssetClass
    from app.modules.asset_management.models.location import Location
    from app.modules.asset_management.models.location_type import LocationType
    from app.modules.asset_management.models.system import System
    from app.modules.asset_management.models.system_type import SystemType
    
    # Check if data already exists
    result = await db.execute(select(AssetClass))
    if result.scalars().first():
        return
    
    # Helper to get/create series
    async def get_series(name: str, current: int = 0) -> Series:
        result = await db.execute(select(Series).where(Series.name == name))
        series = result.scalar_one_or_none()
        if not series:
            series = Series(name=name, current=current)
            db.add(series)
            await db.flush()
        return series
    
    # Seed Location Types
    lt_series = await get_series("LT")
    location_types = []
    for lt_name in ["Building", "Floor", "Room", "Area", "Warehouse"]:
        lt_series.current += 1
        lt = LocationType(id=f"LT-{str(lt_series.current).zfill(4)}", name=lt_name)
        db.add(lt)
        location_types.append(lt)
    await db.flush()
    
    # Seed System Types
    st_series = await get_series("ST")
    system_types = []
    for st_name in ["HVAC", "Electrical", "Plumbing", "Fire Safety", "Production"]:
        st_series.current += 1
        st = SystemType(id=f"ST-{str(st_series.current).zfill(4)}", name=st_name)
        db.add(st)
        system_types.append(st)
    await db.flush()
    
    # Seed Asset Classes with hierarchy (parent-child)
    ac_series = await get_series("AC")
    
    # Parent classes
    ac_series.current += 1
    pump_class = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="Pump", description="All pump types")
    db.add(pump_class)
    
    ac_series.current += 1
    motor_class = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="Motor", description="All motor types")
    db.add(motor_class)
    
    ac_series.current += 1
    valve_class = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="Valve", description="All valve types")
    db.add(valve_class)
    await db.flush()
    
    # Child classes (with parent references)
    ac_series.current += 1
    centrifugal_pump = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="Centrifugal Pump", description="Centrifugal type pumps", parent_asset_class=pump_class.id)
    db.add(centrifugal_pump)
    
    ac_series.current += 1
    submersible_pump = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="Submersible Pump", description="Submersible type pumps", parent_asset_class=pump_class.id)
    db.add(submersible_pump)
    
    ac_series.current += 1
    ac_motor = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="AC Motor", description="AC electric motors", parent_asset_class=motor_class.id)
    db.add(ac_motor)
    
    ac_series.current += 1
    dc_motor = AssetClass(id=f"AC-{str(ac_series.current).zfill(4)}", name="DC Motor", description="DC electric motors", parent_asset_class=motor_class.id)
    db.add(dc_motor)
    await db.flush()
    
    # Seed Locations with hierarchy (parent-child)
    loc_series = await get_series("LOC")
    
    # Parent location (Main Building)
    loc_series.current += 1
    main_building = Location(
        id=f"LOC-{str(loc_series.current).zfill(4)}",
        name="Main Building",
        description="Main production facility",
        location_type=location_types[0].id,  # Building
        site="SITE-0001",
        address="123 Industrial Ave"
    )
    db.add(main_building)
    await db.flush()
    
    # Child locations (Floors)
    loc_series.current += 1
    floor_1 = Location(
        id=f"LOC-{str(loc_series.current).zfill(4)}",
        name="Floor 1",
        description="Ground floor",
        location_type=location_types[1].id,  # Floor
        parent_location=main_building.id,
        site="SITE-0001",
        address="123 Industrial Ave, Floor 1"
    )
    db.add(floor_1)
    
    loc_series.current += 1
    floor_2 = Location(
        id=f"LOC-{str(loc_series.current).zfill(4)}",
        name="Floor 2",
        description="Second floor",
        location_type=location_types[1].id,  # Floor
        parent_location=main_building.id,
        site="SITE-0001",
        address="123 Industrial Ave, Floor 2"
    )
    db.add(floor_2)
    await db.flush()
    
    # Grandchild locations (Rooms)
    loc_series.current += 1
    pump_room = Location(
        id=f"LOC-{str(loc_series.current).zfill(4)}",
        name="Pump Room",
        description="Main pump room",
        location_type=location_types[2].id,  # Room
        parent_location=floor_1.id,
        site="SITE-0001",
        address="123 Industrial Ave, Floor 1, Pump Room"
    )
    db.add(pump_room)
    
    loc_series.current += 1
    electrical_room = Location(
        id=f"LOC-{str(loc_series.current).zfill(4)}",
        name="Electrical Room",
        description="Main electrical room",
        location_type=location_types[2].id,  # Room
        parent_location=floor_1.id,
        site="SITE-0001",
        address="123 Industrial Ave, Floor 1, Electrical Room"
    )
    db.add(electrical_room)
    await db.flush()
    
    # Seed Systems with hierarchy (parent-child)
    sys_series = await get_series("SYS")
    
    # Parent system
    sys_series.current += 1
    hvac_system = System(
        id=f"SYS-{str(sys_series.current).zfill(4)}",
        name="HVAC System",
        description="Main HVAC system",
        system_type=system_types[0].id,  # HVAC
        location=main_building.id,
        site="SITE-0001"
    )
    db.add(hvac_system)
    await db.flush()
    
    # Child systems
    sys_series.current += 1
    cooling_system = System(
        id=f"SYS-{str(sys_series.current).zfill(4)}",
        name="Cooling System",
        description="Cooling subsystem",
        system_type=system_types[0].id,
        parent_system=hvac_system.id,
        location=floor_1.id,
        site="SITE-0001"
    )
    db.add(cooling_system)
    
    sys_series.current += 1
    heating_system = System(
        id=f"SYS-{str(sys_series.current).zfill(4)}",
        name="Heating System",
        description="Heating subsystem",
        system_type=system_types[0].id,
        parent_system=hvac_system.id,
        location=floor_2.id,
        site="SITE-0001"
    )
    db.add(heating_system)
    
    await db.commit()
    print("  ✅ Seeded asset management data with parent-child relationships")


# =============================================================================
# EAM: CORE REFERENCE DATA
# =============================================================================

async def seed_core_eam_data(db: AsyncSession):
    """Seed core EAM entities: Site, Department, Trade, Labor, etc."""
    try:
        from app.modules.core_eam.models.site import Site
        from app.modules.core_eam.models.department import Department
        from app.modules.core_eam.models.trade import Trade
        from app.modules.core_eam.models.labor import Labor
        from app.modules.core_eam.models.cost_code import CostCode
        
        result = await db.execute(select(Site))
        if result.scalars().first():
            print("  ⏭️  Core EAM data already exists, skipping")
            return
        
        # Sites
        site_series = await get_or_create_series(db, "SITE")
        sites = []
        for site_name in ["Main Plant", "Warehouse A", "Office Building"]:
            site_series.current += 1
            site = Site(
                id=f"SITE-{str(site_series.current).zfill(4)}",
                site_name=site_name,
                site_code=f"SITE-{str(site_series.current).zfill(4)}",
            )
            db.add(site)
            sites.append(site)
        await db.flush()
        
        # Departments
        dept_series = await get_or_create_series(db, "DEPT")
        for dept_name in ["Maintenance", "Operations", "Engineering", "Warehouse"]:
            dept_series.current += 1
            dept = Department(
                id=f"DEPT-{str(dept_series.current).zfill(4)}",
                department_name=dept_name,
                department_code=f"DEPT-{str(dept_series.current).zfill(4)}",
                site=sites[0].id,
                site_name=sites[0].site_name,
            )
            db.add(dept)
        await db.flush()
        
        # Trades
        trade_series = await get_or_create_series(db, "TRD")
        for trade_name in ["Electrician", "Mechanic", "Plumber", "HVAC Technician"]:
            trade_series.current += 1
            trade = Trade(id=f"TRD-{str(trade_series.current).zfill(4)}", trade_name=trade_name)
            db.add(trade)
        await db.flush()
        
        # Labor
        labor_series = await get_or_create_series(db, "LBR")
        for name in ["John Smith", "Jane Doe", "Bob Wilson", "Alice Brown"]:
            labor_series.current += 1
            labor = Labor(id=f"LBR-{str(labor_series.current).zfill(4)}", laborer=name, labor_type="Employee")
            db.add(labor)
        await db.flush()
        
        # Cost Codes
        cc_series = await get_or_create_series(db, "CC")
        for cc_name in ["Labor", "Materials", "Equipment", "Overhead"]:
            cc_series.current += 1
            cc = CostCode(id=f"CC-{str(cc_series.current).zfill(4)}", code=cc_name)
            db.add(cc)
        
        await db.commit()
        print("  ✅ Seeded core EAM data")
        
    except ImportError as e:
        print(f"  ⚠️  Could not seed core EAM data: {e}")


# =============================================================================
# PURCHASING: ITEMS, STORES, INVENTORY
# =============================================================================

async def seed_purchasing_data(db: AsyncSession):
    """Seed purchasing entities: Item, Store, Inventory."""
    try:
        from app.modules.purchasing_stores.models.item import Item
        from app.modules.purchasing_stores.models.store import Store
        from app.modules.purchasing_stores.models.inventory import Inventory
        
        result = await db.execute(select(Item))
        if result.scalars().first():
            print("  ⏭️  Purchasing data already exists, skipping")
            return
        
        # Items
        item_series = await get_or_create_series(db, "ITM")
        items = []
        item_data = [
            ("Bearing 6205", "Standard bearing for pumps"),
            ("Motor Oil 5W-30", "Synthetic motor oil"),
            ("Pump Seal Kit", "Complete seal kit for pumps"),
            ("Electric Motor 5HP", "5HP AC electric motor"),
            ("Centrifugal Pump", "Industrial centrifugal pump"),
        ]
        for name, desc in item_data:
            item_series.current += 1
            item = Item(id=f"ITM-{str(item_series.current).zfill(4)}", item_name=name, description=desc)
            db.add(item)
            items.append(item)
        await db.flush()
        
        # Stores
        store_series = await get_or_create_series(db, "STR")
        stores = []
        for store_name in ["Main Warehouse", "Maintenance Store", "Spare Parts Store"]:
            store_series.current += 1
            store = Store(id=f"STR-{str(store_series.current).zfill(4)}", store_name=store_name)
            db.add(store)
            stores.append(store)
        await db.flush()
        
        # Inventory
        inv_series = await get_or_create_series(db, "INV")
        for item in items[:3]:
            inv_series.current += 1
            inv = Inventory(
                id=f"INV-{str(inv_series.current).zfill(4)}",
                item=item.id,
                item_name=item.item_name,
                actual_inv=0,
                available_inv=0,
                reserved_inv=0,
                store_location=stores[0].id if stores else None,
                site=stores[0].site if stores else None,
                location=stores[0].location if stores else None,
                location_name=stores[0].location_name if stores else None,
            )
            db.add(inv)
        
        await db.commit()
        print("  ✅ Seeded purchasing data")
        
    except ImportError as e:
        print(f"  ⚠️  Could not seed purchasing data: {e}")


# =============================================================================
# MAINTENANCE: ACTIVITIES
# =============================================================================

async def seed_maintenance_data(db: AsyncSession):
    """Seed maintenance entities: Maintenance Activity."""
    try:
        from app.modules.maintenance_mgmt.models.maintenance_activity import MaintenanceActivity
        
        result = await db.execute(select(MaintenanceActivity))
        if result.scalars().first():
            print("  ⏭️  Maintenance data already exists, skipping")
            return
        
        ma_series = await get_or_create_series(db, "MA")
        for name in ["Oil Change", "Filter Replacement", "Bearing Inspection", "Alignment Check"]:
            ma_series.current += 1
            ma = MaintenanceActivity(id=f"MA-{str(ma_series.current).zfill(4)}", activity_name=name)
            db.add(ma)
        
        await db.commit()
        print("  ✅ Seeded maintenance activities")
        
    except ImportError as e:
        print(f"  ⚠️  Could not seed maintenance data: {e}")


# =============================================================================
# REQUEST ACTIVITY TYPES
# =============================================================================

async def seed_request_activity_types(db: AsyncSession):
    """Seed Request Activity Types for workflow actions."""
    try:
        from app.modules.core_eam.models.request_activity_type import RequestActivityType
        
        result = await db.execute(select(RequestActivityType))
        if result.scalars().first():
            print("  ⏭️  Request Activity Types already exist, skipping")
            return
        
        rat_series = await get_or_create_series(db, "RAT")
        types = [
            # Asset workflow actions with states
            ("Retire Asset", "Asset", "Inactive", "SystemManager"),
            ("Putaway", "Asset", "Inactive", "Technician"),
            ("Dispose", "Asset", "Decommissioned", "SystemManager"),
            ("Receive", "Asset", "Under Repair", "Technician"),
            ("Send to Vendor", "Asset", "Inactive", "Technician"),
            ("Internal Repair", "Asset", "Inactive", "Technician"),
            ("Remove Asset", "Asset", "Under Maintenance", "Technician"),
            ("Complete", "Asset", "Under Maintenance", "Technician"),
            ("Install Asset", "Asset", "Inactive", "Technician"),
            ("Putaway", "Asset", "Inspected", "Technician"),
            ("Failed Inspection", "Asset", "Inspected", "Technician"),
            ("Install Asset", "Asset", "Inspected", "Technician"),
            ("Maintain Asset", "Asset", "Active", "Technician"),
            ("Inspect Asset", "Asset", "Acquired", "Technician"),
            # Generic types for other entities
            ("Install Asset", "Install Asset", "General", "Technician"),
            ("Remove Asset", "Remove Asset", "General", "Technician"),
            ("Maintain Asset", "Maintain Asset", "General", "Technician"),
            ("Inspect Asset", "Inspection", "General", "Technician"),
            ("Replace Asset", "Replace Asset", "General", "SystemManager"),
            ("Decommission", "Decommission", "General", "SystemManager"),
        ]
        for menu_val, type_val, state_val, role_val in types:
            rat_series.current += 1
            rat = RequestActivityType(
                id=f"RAT-{str(rat_series.current).zfill(4)}", 
                menu=menu_val, 
                type=type_val,
                state=state_val,
                role=role_val
            )
            db.add(rat)
        
        await db.commit()
        print("  ✅ Seeded request activity types")
        
    except ImportError as e:
        print(f"  ⚠️  Could not seed request activity types: {e}")


async def seed_operational_scenario_data(db: AsyncSession):
    """Seed a coherent end-to-end operational dataset from organization to work orders."""
    try:
        from app.models.auth import Role, User, user_roles
        from app.modules.core_eam.models.organization import Organization
        from app.modules.core_eam.models.site import Site
        from app.modules.core_eam.models.department import Department
        from app.modules.core_eam.models.employee import Employee
        from app.modules.core_eam.models.cost_code import CostCode
        from app.modules.core_eam.models.account import Account
        from app.modules.core_eam.models.labor import Labor
        from app.modules.core_eam.models.request_activity_type import RequestActivityType
        from app.modules.asset_management.models.asset_class import AssetClass
        from app.modules.asset_management.models.asset import Asset
        from app.modules.asset_management.models.location import Location
        from app.modules.asset_management.models.system import System
        from app.modules.asset_management.models.position import Position
        from app.modules.purchasing_stores.models.vendor import Vendor
        from app.modules.purchasing_stores.models.item import Item
        from app.modules.purchasing_stores.models.unit_of_measure import UnitOfMeasure
        from app.modules.purchasing_stores.models.currency import Currency
        from app.modules.purchasing_stores.models.purchase_request import PurchaseRequest
        from app.modules.purchasing_stores.models.purchase_request_line import PurchaseRequestLine
        from app.modules.purchasing_stores.models.purchase_order import PurchaseOrder
        from app.modules.purchasing_stores.models.purchase_order_line import PurchaseOrderLine
        from app.modules.purchasing_stores.models.purchase_receipt import PurchaseReceipt
        from app.modules.maintenance_mgmt.models.maintenance_request import MaintenanceRequest
        from app.modules.work_mgmt.models.category_of_failure import CategoryOfFailure
        from app.modules.work_mgmt.models.work_order import WorkOrder
        from app.modules.work_mgmt.models.work_order_activity import WorkOrderActivity

        today = date.today()

        async def ensure_one(model, filters: dict, create_data: dict):
            result = await db.execute(select(model).filter_by(**filters))
            instance = result.scalar_one_or_none()
            if instance:
                return instance
            instance = model(**create_data)
            db.add(instance)
            await db.flush()
            return instance

        async def next_id(series_name: str, prefix: str, digits: int = 4):
            series = await get_or_create_series(db, series_name)
            series.current += 1
            return f"{prefix}{str(series.current).zfill(digits)}"

        def make_username(full_name: str) -> str:
            return full_name.lower().replace(" ", ".")

        result = await db.execute(select(Role).where(Role.name == "Technician"))
        technician_role = result.scalar_one_or_none()

        result = await db.execute(select(RequestActivityType))
        request_types = result.scalars().all()
        request_type_value = request_types[0].id if request_types else None

        result = await db.execute(select(AssetClass).order_by(AssetClass.name))
        asset_classes = result.scalars().all()
        if not asset_classes:
            await seed_asset_management_data(db)
            result = await db.execute(select(AssetClass).order_by(AssetClass.name))
            asset_classes = result.scalars().all()

        result = await db.execute(select(Location).where(Location.site == "SITE-0001").order_by(Location.name))
        locations = result.scalars().all()
        result = await db.execute(select(System).where(System.site == "SITE-0001").order_by(System.name))
        systems = result.scalars().all()

        if not locations:
            await seed_asset_management_data(db)
            result = await db.execute(select(Location).order_by(Location.name))
            locations = result.scalars().all()
        if not systems:
            result = await db.execute(select(System).order_by(System.name))
            systems = result.scalars().all()

        result = await db.execute(
            select(Organization).where(
                Organization.organizational_code.in_(["CWI-OPS", "SPMC-OPS"])
            )
        )
        organization = result.scalar_one_or_none()
        if organization is None:
            organization = Organization(id=await next_id("ORG-U", "ORG-U-", 5))
            db.add(organization)
            await db.flush()
        organization.organization_name = "Southern Philippines Medical Center"
        organization.legal_name = "Southern Philippines Medical Center"
        organization.organizational_code = "SPMC-OPS"
        organization.is_active = True

        maintenance_account = await ensure_one(
            Account,
            {"account_code": "6000-MNT"},
            {
                "id": await next_id("ACC", "ACC-", 4),
                "account_code": "6000-MNT",
                "account_name": "Facilities Maintenance Expense",
                "account_type": "Expense",
            },
        )
        spares_account = await ensure_one(
            Account,
            {"account_code": "1200-SPR"},
            {
                "id": await next_id("ACC", "ACC-", 4),
                "account_code": "1200-SPR",
                "account_name": "Medical Spare Parts Inventory",
                "account_type": "Asset",
            },
        )

        legacy_site_codes = {
            "MAIN-PLT": "SPMC-MAIN",
            "UTIL-YD": "SPMC-FAC",
            "PKG-HALL": "SPMC-DIAG",
        }
        result = await db.execute(
            select(Site).where(Site.site_code.in_(list(legacy_site_codes.keys())))
        )
        for legacy_site in result.scalars().all():
            legacy_site.site_code = legacy_site_codes[legacy_site.site_code]
            legacy_site.organization = organization.id
            legacy_site.organization_name = organization.organization_name

        site_specs = [
            ("Main Hospital Building", "SPMC-MAIN"),
            ("Facilities and Utilities Complex", "SPMC-FAC"),
            ("Diagnostic and Imaging Center", "SPMC-DIAG"),
        ]
        sites = []
        for site_name, site_code in site_specs:
            site = await ensure_one(
                Site,
                {"site_code": site_code},
                {
                    "id": await next_id("SITE", "SITE-", 4),
                    "site_name": site_name,
                    "site_code": site_code,
                    "organization": organization.id,
                    "organization_name": organization.organization_name,
                    "default_cost_code": None,
                },
            )
            site.site_name = site_name
            site.site_code = site_code
            site.organization = organization.id
            site.organization_name = organization.organization_name
            sites.append(site)

        department_specs = [
            ("Biomedical Engineering", "BME"),
            ("Hospital Operations", "OPS"),
            ("Facilities Management", "FAC"),
            ("Central Supply", "CSR"),
            ("Diagnostic Services", "DIA"),
        ]
        departments = []
        for idx, (name, code) in enumerate(department_specs):
            site = sites[min(idx, len(sites) - 1 if idx >= len(sites) else idx % len(sites))]
            department = await ensure_one(
                Department,
                {"department_code": f"{site.site_code}-{code}"},
                {
                    "id": await next_id("DEPT", "DEPT-", 4),
                    "department_name": name,
                    "department_code": f"{site.site_code}-{code}",
                    "site": site.id,
                    "site_name": site.site_name,
                    "default_cost_code": None,
                    "overhead_method": "percentage",
                    "overhead_percent": 10.0,
                    "overhead_expense_account": maintenance_account.id,
                    "labor_expense_account_overwrite": maintenance_account.id,
                },
            )
            department.department_name = name
            department.department_code = f"{site.site_code}-{code}"
            department.site = site.id
            department.site_name = site.site_name
            department.overhead_expense_account = maintenance_account.id
            department.labor_expense_account_overwrite = maintenance_account.id
            departments.append(department)

        cost_code_specs = [
            ("BME-EQPM", "Biomedical equipment preventive and corrective maintenance", sites[0], departments[0]),
            ("BME-LS", "Life support equipment service", sites[0], departments[0]),
            ("FAC-UTL", "Hospital facilities and utilities support", sites[1], departments[2]),
            ("CSR-STO", "Central supply spare parts and consumables", sites[0], departments[3]),
            ("DIA-EQP", "Diagnostic equipment support", sites[2], departments[4]),
        ]
        cost_codes = []
        for code, description, site, department in cost_code_specs:
            cost_code = await ensure_one(
                CostCode,
                {"code": code},
                {
                    "id": await next_id("CC", "CC-", 4),
                    "code": code,
                    "description": description,
                    "scope": department.department_name,
                    "site": site.id,
                    "site_name": site.site_name,
                },
            )
            cost_code.description = description
            cost_code.scope = department.department_name
            cost_code.site = site.id
            cost_code.site_name = site.site_name
            cost_codes.append(cost_code)
            if not site.default_cost_code:
                site.default_cost_code = cost_code.id
            if not department.default_cost_code:
                department.default_cost_code = cost_code.id

        employee_specs = [
            ("Maria Santos", "Biomedical Engineering Head", sites[0], departments[0]),
            ("Paolo Reyes", "Biomedical Equipment Technician", sites[0], departments[0]),
            ("Liza Fernandez", "Facilities Engineer", sites[1], departments[2]),
            ("Ramon Dela Cruz", "Central Supply Officer", sites[0], departments[3]),
            ("Angela Navarro", "Diagnostic Services Planner", sites[2], departments[4]),
        ]
        employees = []
        for name, position_name, site, department in employee_specs:
            username = make_username(name)
            user = await ensure_one(
                User,
                {"username": username},
                {
                    "username": username,
                    "email": f"{username}@spmc.local",
                    "full_name": name,
                    "hashed_password": hash_password("password123"),
                    "is_active": True,
                    "is_superuser": False,
                    "department": department.id,
                    "site": site.id,
                },
            )
            user.full_name = name
            user.email = f"{username}@spmc.local"
            user.department = department.id
            user.site = site.id
            user.is_active = True
            if technician_role:
                role_result = await db.execute(
                    select(Role)
                    .join(Role.users)
                    .where(Role.id == technician_role.id)
                    .where(User.id == user.id)
                )
                if role_result.scalar_one_or_none() is None:
                    await db.execute(
                        user_roles.insert().values(user_id=user.id, role_id=technician_role.id)
                    )

            employee = await ensure_one(
                Employee,
                {"employee_name": name},
                {
                    "id": await next_id("EMP", "EMP-", 4),
                    "user": user.id,
                    "employee_name": name,
                    "position": position_name,
                },
            )
            employee.user = user.id
            employee.position = position_name
            user.employee_id = employee.id
            employees.append(employee)

        sites[0].site_manager = employees[0].id
        sites[1].site_manager = employees[2].id
        sites[2].site_manager = employees[4].id
        departments[0].department_manager = employees[0].id
        departments[1].department_manager = employees[2].id
        departments[2].department_manager = employees[2].id
        departments[3].department_manager = employees[3].id
        departments[4].department_manager = employees[4].id

        labor_specs = [
            (employees[1], "Mechanical Technician", locations[0] if locations else None),
            (employees[0], "Maintenance Supervisor", locations[0] if locations else None),
            (employees[2], "Operations Engineer", locations[1] if len(locations) > 1 else (locations[0] if locations else None)),
            (employees[3], "Store Officer", locations[0] if locations else None),
            (employees[4], "Planner", locations[0] if locations else None),
        ]
        labors = []
        for employee, laborer_name, location in labor_specs:
            labor = await ensure_one(
                Labor,
                {"employee": employee.id},
                {
                    "id": await next_id("LBR", "LBR-", 4),
                    "labor_type": "Employee",
                    "employee": employee.id,
                    "laborer": laborer_name,
                    "location": location.id if location else None,
                    "location_name": location.name if location else None,
                    "labor_cost": 125.0,
                },
            )
            labors.append(labor)

        uom_each = await ensure_one(
            UnitOfMeasure,
            {"short_name": "EA"},
            {"id": await next_id("UOM", "UOM-", 4), "name": "Each", "short_name": "EA"},
        )
        local_currency = await ensure_one(
            Currency,
            {"currency_name": "Philippine Peso"},
            {
                "id": await next_id("CUR", "CUR-", 4),
                "currency_name": "Philippine Peso",
                "symbol": "₱",
                "conversion_factor": 1.0,
                "active": True,
            },
        )

        vendor_specs = [
            ("MedTech Davao Supplies", sites[0]),
            ("PhilCare Biomedical Systems", sites[0]),
            ("Mindanao Utility Controls", sites[1]),
            ("Sterile Stores and Parts Center", sites[0]),
            ("Diagnostic Imaging Solutions PH", sites[2]),
        ]
        vendors = []
        for vendor_name, site in vendor_specs:
            vendor = await ensure_one(
                Vendor,
                {"vendor_name": vendor_name},
                {"id": await next_id("VND", "VND-", 4), "vendor_name": vendor_name, "site": site.id},
            )
            vendors.append(vendor)

        site_location_specs = [
            (sites[0], "SPMC Main Hospital Biomedical Workshop"),
            (sites[1], "SPMC Facilities Plant Room"),
            (sites[2], "SPMC Diagnostic Imaging Equipment Room"),
        ]
        scenario_site_locations = {}
        for site, location_name in site_location_specs:
            location = await ensure_one(
                Location,
                {"name": location_name},
                {
                    "id": await next_id("LOC", "LOC-", 4),
                    "name": location_name,
                    "description": f"{site.site_name} service area",
                    "location_type": locations[0].location_type if locations else None,
                    "location_type_name": getattr(locations[0], "location_type_name", None) if locations else None,
                    "site": site.id,
                    "address": f"{site.site_name} campus area",
                },
            )
            location.site = site.id
            scenario_site_locations[site.id] = location
            site.location = location.id
            site.location_name = location.name

        scenario_site_systems = {}
        for site in sites:
            parent_location = scenario_site_locations.get(site.id)
            system = await ensure_one(
                System,
                {"name": f"SPMC {site.site_name} System"},
                {
                    "id": await next_id("SYS", "SYS-", 4),
                    "name": f"SPMC {site.site_name} System",
                    "description": f"Clinical support system for {site.site_name}",
                    "system_type": systems[0].system_type if systems else None,
                    "system_type_name": getattr(systems[0], "system_type_name", None) if systems else None,
                    "location": parent_location.id if parent_location else None,
                    "site": site.id,
                },
            )
            system.site = site.id
            system.location = parent_location.id if parent_location else None
            scenario_site_systems[site.id] = system

        asset_class_by_name = {ac.name.lower(): ac for ac in asset_classes if ac.name}
        relevant_class_names = [
            "centrifugal pump",
            "submersible pump",
            "ac motor",
            "dc motor",
            "pump",
        ]
        relevant_classes = [asset_class_by_name[name] for name in relevant_class_names if name in asset_class_by_name]
        if not relevant_classes:
            relevant_classes = asset_classes[:5]

        item_specs = [
            ("Ventilator PM Kit", "Preventive maintenance kit for ICU ventilators", relevant_classes[0] if len(relevant_classes) > 0 else None, vendors[0], 85000.0, False),
            ("Patient Monitor Power Module", "Replacement power module for bedside patient monitors", relevant_classes[2] if len(relevant_classes) > 2 else relevant_classes[0], vendors[1], 420000.0, True),
            ("Autoclave Door Seal Set", "Door seal set for CSSD autoclaves", relevant_classes[0] if len(relevant_classes) > 0 else None, vendors[3], 12000.0, False),
            ("Medical Vacuum Pump Cable Kit", "Cable kit for medical vacuum pump assembly", relevant_classes[1] if len(relevant_classes) > 1 else relevant_classes[0], vendors[2], 54000.0, False),
            ("CT Scanner Cooling Fan Assembly", "Cooling fan assembly for CT scanner gantry support", relevant_classes[2] if len(relevant_classes) > 2 else relevant_classes[0], vendors[4], 67000.0, False),
        ]
        items = []
        for item_name, description, asset_class, vendor, unit_cost, is_equipment in item_specs:
            item = await ensure_one(
                Item,
                {"item_name": item_name},
                {
                    "id": await next_id("ITM", "ITM-", 4),
                    "item_name": item_name,
                    "description": description,
                    "item_type": "Spare Part" if not is_equipment else "Equipment",
                    "expense_account": maintenance_account.id,
                    "primary_vendor": vendor.id,
                    "asset_class": asset_class.id if asset_class else None,
                    "uom": uom_each.id,
                    "actual_qty_on_hand": 10,
                    "available_capacity": 10,
                    "reserved_capacity": 0,
                    "unit_cost": unit_cost,
                    "is_serialized": is_equipment,
                    "inspection_required": is_equipment,
                    "is_equipment": is_equipment,
                },
            )
            items.append(item)

        failure_specs = [
            "Pressure Leakage",
            "Sensor Failure",
            "Power Module Overheating",
            "Cable Insulation Breakdown",
            "Calibration Drift",
        ]
        failures = []
        for idx, failure_name in enumerate(failure_specs):
            failure = await ensure_one(
                CategoryOfFailure,
                {"failure_name": failure_name},
                {
                    "id": await next_id("COF", "COF-", 4),
                    "failure_name": failure_name,
                    "description": f"{failure_name} detected during hospital operations",
                    "site": sites[min(idx // 2, len(sites) - 1)].id,
                    "active": True,
                },
            )
            failures.append(failure)

        legacy_asset_tag_map = {
            "OPS-MAIN-PLT-001": "SPMC-MAIN-001",
            "OPS-MAIN-PLT-002": "SPMC-MAIN-002",
            "OPS-UTIL-YD-001": "SPMC-FAC-001",
            "OPS-UTIL-YD-002": "SPMC-FAC-002",
            "OPS-PKG-HALL-001": "SPMC-DIAG-001",
        }
        result = await db.execute(
            select(Asset).where(Asset.asset_tag.in_(list(legacy_asset_tag_map.keys())))
        )
        for legacy_asset in result.scalars().all():
            legacy_asset.asset_tag = legacy_asset_tag_map[legacy_asset.asset_tag]

        asset_specs = [
            ("SPMC-MAIN-001", sites[0], departments[0], relevant_classes[0] if len(relevant_classes) > 0 else None, items[0], employees[0], 1),
            ("SPMC-MAIN-002", sites[0], departments[0], relevant_classes[0] if len(relevant_classes) > 0 else None, items[2], employees[1], 2),
            ("SPMC-FAC-001", sites[1], departments[2], relevant_classes[2] if len(relevant_classes) > 2 else (relevant_classes[0] if relevant_classes else None), items[1], employees[2], 3),
            ("SPMC-FAC-002", sites[1], departments[2], relevant_classes[1] if len(relevant_classes) > 1 else (relevant_classes[0] if relevant_classes else None), items[3], employees[2], 4),
            ("SPMC-DIAG-001", sites[2], departments[4], relevant_classes[2] if len(relevant_classes) > 2 else (relevant_classes[0] if relevant_classes else None), items[4], employees[4], 5),
        ]
        expected_asset_tags = {asset_tag for asset_tag, *_ in asset_specs}

        legacy_title_map = {
            "Seal replacement on raw water transfer pump": "Ventilator preventive maintenance kit replacement in ICU",
            "Bearing change for condensate pump": "Autoclave door seal replacement in CSSD",
            "Motor replacement for cooling tower circulation unit": "Patient monitor power module replacement in ER",
            "Cable kit replacement for borehole submersible pump": "Medical vacuum pump cable kit replacement",
            "Drive coupling renewal on packaging conveyor motor": "CT scanner cooling fan assembly replacement",
        }
        legacy_pr_titles = [f"PR - {old}" for old in legacy_title_map]
        legacy_wo_titles = [f"WO - {old}" for old in legacy_title_map]
        legacy_activity_titles = [f"Activity - {old}" for old in legacy_title_map]

        result = await db.execute(
            select(PurchaseRequest).where(PurchaseRequest.pr_description.in_(legacy_pr_titles))
        )
        legacy_purchase_requests = result.scalars().all()
        for legacy_pr in legacy_purchase_requests:
            result = await db.execute(
                select(PurchaseRequestLine).where(PurchaseRequestLine.purchase_request == legacy_pr.id)
            )
            legacy_pr_lines = result.scalars().all()
            for legacy_pr_line in legacy_pr_lines:
                result = await db.execute(
                    select(PurchaseReceipt).where(PurchaseReceipt.purchase_request_line == legacy_pr_line.id)
                )
                for receipt in result.scalars().all():
                    await db.delete(receipt)
                result = await db.execute(
                    select(PurchaseOrderLine).where(PurchaseOrderLine.pr_line_id == legacy_pr_line.id)
                )
                for po_line in result.scalars().all():
                    result = await db.execute(
                        select(PurchaseReceipt).where(PurchaseReceipt.purchase_order_line == po_line.id)
                    )
                    for receipt in result.scalars().all():
                        await db.delete(receipt)
                    await db.delete(po_line)
                await db.delete(legacy_pr_line)
            result = await db.execute(
                select(PurchaseOrder).where(PurchaseOrder.source_rfq == legacy_pr.id)
            )
            for po in result.scalars().all():
                await db.delete(po)
            await db.delete(legacy_pr)

        result = await db.execute(
            select(MaintenanceRequest).where(MaintenanceRequest.description.in_(list(legacy_title_map.keys())))
        )
        for record in result.scalars().all():
            await db.delete(record)

        result = await db.execute(
            select(WorkOrderActivity).where(WorkOrderActivity.description.in_(legacy_activity_titles))
        )
        for record in result.scalars().all():
            await db.delete(record)

        result = await db.execute(
            select(WorkOrder).where(WorkOrder.description.in_(legacy_wo_titles))
        )
        for record in result.scalars().all():
            await db.delete(record)
        await db.flush()

        scenario_assets = []
        for asset_tag, site, department, asset_class, item, employee, block_number in asset_specs:
            location = scenario_site_locations.get(site.id)
            system = scenario_site_systems.get(site.id)
            asset = await ensure_one(
                Asset,
                {"asset_tag": asset_tag},
                {
                    "id": await next_id("A", "A-", 5),
                    "workflow_state": "active",
                    "asset_tag": asset_tag,
                    "asset_class": asset_class.id if asset_class else None,
                    "description": f"{asset_class.name if asset_class else 'Operational Asset'} deployed at {site.site_name}",
                    "serial_number": f"SN-{asset_tag}",
                    "date_purchased": today - timedelta(days=300 + (block_number * 45)),
                    "cost": float(item.unit_cost or 50000.0),
                    "block_number": block_number,
                    "number_of_repairs": max(0, block_number - 1),
                    "location": location.id if location else None,
                    "site": site.id,
                    "department": department.id,
                    "assigned_to": employee.id,
                    "system": system.id if system else None,
                    "item": item.id,
                    "defective": False,
                    "item_type": item.item_type,
                    "is_equipment": bool(item.is_equipment),
                    "need_repair": False,
                    "bypass_process": False,
                },
            )
            asset.workflow_state = "active"
            asset.asset_class = asset_class.id if asset_class else None
            asset.description = f"{asset_class.name if asset_class else 'Operational Asset'} deployed at {site.site_name}"
            asset.serial_number = f"SN-{asset_tag}"
            asset.location = location.id if location else None
            asset.site = site.id
            asset.department = department.id
            asset.assigned_to = employee.id
            asset.system = system.id if system else None
            asset.item = item.id
            asset.item_type = item.item_type
            asset.is_equipment = bool(item.is_equipment)
            asset.block_number = block_number
            scenario_assets.append(asset)

        positions = []
        for idx, asset in enumerate(scenario_assets):
            site = next((s for s in sites if s.id == asset.site), sites[idx % len(sites)])
            location = scenario_site_locations.get(site.id)
            system = scenario_site_systems.get(site.id)
            asset_class = next((ac for ac in asset_classes if ac.id == asset.asset_class), None)
            position = await ensure_one(
                Position,
                {"position_tag": f"POS-{site.site_code}-{idx + 1:03d}"},
                {
                    "id": await next_id("POS", "POS-", 4),
                    "position_tag": f"POS-{site.site_code}-{idx + 1:03d}",
                    "description": f"{asset.description} installed position",
                    "asset_class": asset.asset_class,
                    "asset_class_name": asset_class.name if asset_class else None,
                    "system": system.id if system else None,
                    "system_name": system.name if system else None,
                    "location": location.id if location else None,
                    "location_name": location.name if location else None,
                    "site": site.id,
                    "current_asset": asset.id,
                },
            )
            position.site = site.id
            position.location = location.id if location else None
            position.location_name = location.name if location else None
            position.system = system.id if system else None
            position.system_name = system.name if system else None
            asset.position = position.id
            asset.site = site.id
            asset.location = location.id if location else None
            asset.system = system.id if system else None
            positions.append(position)

        purchase_requests = []
        maintenance_requests = []
        work_orders = []

        scenario_specs = [
            {
                "title": "Ventilator preventive maintenance kit replacement in ICU",
                "priority": "High",
                "severity": "High",
                "asset": scenario_assets[0],
                "site": sites[0],
                "department": departments[0],
                "cost_code": cost_codes[0],
                "item": items[0],
                "vendor": vendors[0],
                "failure": failures[0],
                "requestor": employees[0],
                "labor": labors[0],
            },
            {
                "title": "Autoclave door seal replacement in CSSD",
                "priority": "Medium",
                "severity": "Medium",
                "asset": scenario_assets[1],
                "site": sites[0],
                "department": departments[0],
                "cost_code": cost_codes[0],
                "item": items[2],
                "vendor": vendors[3],
                "failure": failures[1],
                "requestor": employees[1],
                "labor": labors[0],
            },
            {
                "title": "Patient monitor power module replacement in ER",
                "priority": "Emergency",
                "severity": "Critical",
                "asset": scenario_assets[2],
                "site": sites[1],
                "department": departments[2],
                "cost_code": cost_codes[2],
                "item": items[1],
                "vendor": vendors[1],
                "failure": failures[2],
                "requestor": employees[2],
                "labor": labors[2],
            },
            {
                "title": "Medical vacuum pump cable kit replacement",
                "priority": "High",
                "severity": "High",
                "asset": scenario_assets[3],
                "site": sites[1],
                "department": departments[2],
                "cost_code": cost_codes[2],
                "item": items[3],
                "vendor": vendors[2],
                "failure": failures[3],
                "requestor": employees[2],
                "labor": labors[2],
            },
            {
                "title": "CT scanner cooling fan assembly replacement",
                "priority": "Medium",
                "severity": "Medium",
                "asset": scenario_assets[4],
                "site": sites[2],
                "department": departments[4],
                "cost_code": cost_codes[4],
                "item": items[4],
                "vendor": vendors[4],
                "failure": failures[4],
                "requestor": employees[4],
                "labor": labors[4],
            },
        ]

        for idx, spec in enumerate(scenario_specs, start=1):
            asset = spec["asset"]
            position = positions[idx - 1] if idx - 1 < len(positions) else None
            location = scenario_site_locations.get(spec["site"].id)
            system = scenario_site_systems.get(spec["site"].id)
            asset.site = spec["site"].id
            asset.department = spec["department"].id
            asset.location = location.id if location else None
            asset.system = system.id if system else None
            asset.assigned_to = spec["requestor"].id
            if position:
                position.site = spec["site"].id
                position.location = location.id if location else None
                position.location_name = location.name if location else None
                position.system = system.id if system else None
                position.system_name = system.name if system else None
                position.current_asset = asset.id

            maintenance_request = await ensure_one(
                MaintenanceRequest,
                {"description": spec["title"]},
                {
                    "id": await next_id("MTREQ", "MTREQ-", 5),
                    "workflow_state": "Approved" if idx < 5 else "Release",
                    "requestor": spec["requestor"].id,
                    "requested_date": today - timedelta(days=12 - idx),
                    "description": spec["title"],
                    "priority": spec["priority"],
                    "asset": asset.id,
                    "request_type": request_type_value,
                    "location": location.id if location else None,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "position": position.id if position else None,
                    "due_date": today + timedelta(days=idx * 3),
                },
            )
            maintenance_request.requestor = spec["requestor"].id
            maintenance_request.asset = asset.id
            maintenance_request.site = spec["site"].id
            maintenance_request.department = spec["department"].id
            maintenance_request.location = location.id if location else None
            maintenance_request.position = position.id if position else None
            maintenance_requests.append(maintenance_request)

            work_order = await ensure_one(
                WorkOrder,
                {"description": f"WO - {spec['title']}"},
                {
                    "id": await next_id("WO", "WO-", 5),
                    "workflow_state": "Released",
                    "work_order_type": "Corrective",
                    "description": f"WO - {spec['title']}",
                    "category_of_failure": spec["failure"].id,
                    "due_date": today + timedelta(days=idx * 4),
                    "priority": spec["priority"],
                    "severity": spec["severity"],
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "cost_code": spec["cost_code"].id,
                },
            )
            work_order.site = spec["site"].id
            work_order.department = spec["department"].id
            work_order.cost_code = spec["cost_code"].id
            work_orders.append(work_order)

            work_order_activity = await ensure_one(
                WorkOrderActivity,
                {"description": f"Activity - {spec['title']}"},
                {
                    "id": await next_id("WOA", "WOA-", 5),
                    "workflow_state": "In Progress",
                    "work_order": work_order.id,
                    "work_order_name": work_order.description,
                    "description": f"Activity - {spec['title']}",
                    "work_item_type": "Asset",
                    "work_item": asset.id,
                    "asset_name": asset.asset_tag,
                    "activity_type": "Corrective Maintenance",
                    "activity_type_name": "Corrective Maintenance",
                    "position": position.id if position else None,
                    "assigned_to": spec["labor"].id,
                    "does_it_need_repair": True,
                    "location": location.id if location else None,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "start_date": datetime.utcnow() - timedelta(days=idx),
                    "end_date": datetime.utcnow() + timedelta(days=max(1, idx - 3)),
                },
            )
            work_order_activity.work_order = work_order.id
            work_order_activity.work_order_name = work_order.description
            work_order_activity.work_item = asset.id
            work_order_activity.asset_name = asset.asset_tag
            work_order_activity.position = position.id if position else None
            work_order_activity.assigned_to = spec["labor"].id
            work_order_activity.location = location.id if location else None
            work_order_activity.site = spec["site"].id
            work_order_activity.department = spec["department"].id
            maintenance_request.work_order_activity = work_order_activity.id

            purchase_request = await ensure_one(
                PurchaseRequest,
                {"pr_description": f"PR - {spec['title']}"},
                {
                    "id": await next_id("PR", "PR-", 5),
                    "workflow_state": "Approved",
                    "date_requested": today - timedelta(days=10 - idx),
                    "requestor": spec["requestor"].id,
                    "pr_description": f"PR - {spec['title']}",
                    "due_date": today + timedelta(days=idx * 2),
                    "work_activity_id": work_order_activity.id,
                    "maintenance_request": maintenance_request.id,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "cost_code": spec["cost_code"].id,
                },
            )
            purchase_request.requestor = spec["requestor"].id
            purchase_request.work_activity_id = work_order_activity.id
            purchase_request.maintenance_request = maintenance_request.id
            purchase_request.site = spec["site"].id
            purchase_request.department = spec["department"].id
            purchase_request.cost_code = spec["cost_code"].id
            purchase_requests.append(purchase_request)

            qty = 1 if spec["item"].is_equipment else (2 + idx)
            total_amount = float((spec["item"].unit_cost or 0.0) * qty)

            pr_line = await ensure_one(
                PurchaseRequestLine,
                {"purchase_request": purchase_request.id, "row_no": 1},
                {
                    "id": await next_id("PRL", "PRL-", 5),
                    "workflow_state": "Approved",
                    "purchase_request": purchase_request.id,
                    "financial_asset_number": asset.asset_tag,
                    "row_no": 1,
                    "item": spec["item"].id,
                    "item_description": spec["item"].description,
                    "unit_of_measure": uom_each.id,
                    "unit_cost": spec["item"].unit_cost,
                    "base_currency": local_currency.id,
                    "qty_required": qty,
                    "total_line_amount": total_amount,
                    "account_code": spares_account.id,
                    "cost_code": spec["cost_code"].id,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "vendor": spec["vendor"].id,
                    "date_required": datetime.utcnow() + timedelta(days=idx * 2),
                    "qty_received": qty,
                    "base_currency_unit": spec["item"].unit_cost,
                    "base_currency_line_amount": total_amount,
                    "conversion_factor": 1.0,
                },
            )
            pr_line.item = spec["item"].id
            pr_line.unit_of_measure = uom_each.id
            pr_line.base_currency = local_currency.id
            pr_line.account_code = spares_account.id
            pr_line.cost_code = spec["cost_code"].id
            pr_line.site = spec["site"].id
            pr_line.department = spec["department"].id
            pr_line.vendor = spec["vendor"].id
            pr_line.po_num = purchase_request.id

            purchase_order = await ensure_one(
                PurchaseOrder,
                {"source_rfq": purchase_request.id},
                {
                    "id": await next_id("PO", "PO-", 5),
                    "workflow_state": "Approved",
                    "source_rfq": purchase_request.id,
                    "vendor": spec["vendor"].id,
                    "vendor_name": spec["vendor"].vendor_name,
                    "date_ordered": today - timedelta(days=7 - idx),
                    "total_amount": total_amount,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "cost_code": spec["cost_code"].id,
                },
            )
            purchase_order.vendor = spec["vendor"].id
            purchase_order.vendor_name = spec["vendor"].vendor_name
            purchase_order.site = spec["site"].id
            purchase_order.department = spec["department"].id
            purchase_order.cost_code = spec["cost_code"].id

            po_line = await ensure_one(
                PurchaseOrderLine,
                {"po_id": purchase_order.id, "line_row_num": 1},
                {
                    "id": await next_id("POL", "POL-", 5),
                    "workflow_state": "Approved",
                    "po_id": purchase_order.id,
                    "pr_line_id": pr_line.id,
                    "line_row_num": 1,
                    "financial_asset_number": asset.asset_tag,
                    "item_id": spec["item"].id,
                    "item_description": spec["item"].description,
                    "quantity_ordered": qty,
                    "price": spec["item"].unit_cost,
                    "quantity_received": qty,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "cost_code": spec["cost_code"].id,
                },
            )
            po_line.po_id = purchase_order.id
            po_line.pr_line_id = pr_line.id
            po_line.item_id = spec["item"].id
            po_line.site = spec["site"].id
            po_line.department = spec["department"].id
            po_line.cost_code = spec["cost_code"].id

            receipt = await ensure_one(
                PurchaseReceipt,
                {"purchase_order_line": po_line.id},
                {
                    "id": await next_id("PRC", "PRC-", 5),
                    "purchase_order_line": po_line.id,
                    "purchase_request_line": pr_line.id,
                    "pr_row_no": 1,
                    "is_received": True,
                    "item": spec["item"].id,
                    "quantity_received": qty,
                    "date_received": today - timedelta(days=max(0, 5 - idx)),
                    "receiving_location": location.id if location else None,
                    "site": spec["site"].id,
                    "department": spec["department"].id,
                    "cost_code": spec["cost_code"].id,
                    "generated_inventory": False,
                    "account_code": spares_account.id,
                },
            )
            receipt.purchase_request_line = pr_line.id
            receipt.item = spec["item"].id
            receipt.receiving_location = location.id if location else None
            receipt.site = spec["site"].id
            receipt.department = spec["department"].id
            receipt.cost_code = spec["cost_code"].id
            receipt.account_code = spares_account.id

            asset.number_of_repairs = (asset.number_of_repairs or 0) + 1
            asset.need_repair = False
            asset.defective = False

        await db.commit()
        print("  ✅ Seeded operational scenario data")

    except ImportError as e:
        print(f"  ⚠️  Could not seed operational scenario data: {e}")


# =============================================================================
# MAIN ENTRY POINTS
# =============================================================================

async def run_seeds(db: AsyncSession):
    """Run all seed functions."""
    print("🌱 Seeding database...")
    
    # Core
    await seed_roles(db)
    await seed_users(db)
    await seed_entity_permissions(db)
    
    # Workflow
    await seed_asset_workflow(db)
    
    # EAM Data
    await seed_core_eam_data(db)
    await seed_asset_management_data(db)
    await seed_purchasing_data(db)
    await seed_maintenance_data(db)
    await seed_request_activity_types(db)
    await seed_operational_scenario_data(db)
    
    print("✅ Seeding complete!")


async def seed_data():
    """Entry point for CLI seed command."""
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        await run_seeds(db)
