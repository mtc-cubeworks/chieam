# Database Credentials - EAM FastAPI Project

## Local PostgreSQL Database
**Purpose**: Development database for local work

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: eam_local_db
- Username: eam_local
- Password: eam_local_password

**Connection URLs:**
- Async: `postgresql+asyncpg://eam_local:eam_local_password@localhost:5432/eam_local_db`
- Sync: `postgresql://eam_local:eam_local_password@localhost:5432/eam_local_db`

---

## Remote PostgreSQL Database (Contabo VPS)
**Purpose**: Remote production/staging database

**Connection Details:**
- Host: 194.233.77.65
- Port: 5432
- Database: eam_db
- Username: eam_user
- Password: eam_password

**Connection URLs:**
- Async: `postgresql+asyncpg://eam_user:eam_password@194.233.77.65:5432/eam_db`
- Sync: `postgresql://eam_user:eam_password@194.233.77.65:5432/eam_db`

---

## Switching Between Databases

### To switch to Local PostgreSQL:
```bash
# Edit .env file and replace with:
DATABASE_URL=postgresql+asyncpg://eam_local:eam_local_password@localhost:5432/eam_local_db
DATABASE_URL_SYNC=postgresql://eam_local:eam_local_password@localhost:5432/eam_local_db
```

### To switch to Remote PostgreSQL:
```bash
# Edit .env file and replace with:
DATABASE_URL=postgresql+asyncpg://eam_user:eam_password@194.233.77.65:5432/eam_db
DATABASE_URL_SYNC=postgresql://eam_user:eam_password@194.233.77.65:5432/eam_db
```

### To switch to SQLite:
```bash
# Edit .env file and replace with:
DATABASE_URL=sqlite+aiosqlite:///./eam_local.db
DATABASE_URL_SYNC=sqlite:///./eam_local.db
```

---

## Database Management Commands

### PostgreSQL Commands:
```bash
# Start PostgreSQL service
brew services start postgresql@14

# Stop PostgreSQL service
brew services stop postgresql@14

# Connect to local database
psql -d eam_local_db -U eam_local

# List all databases
psql -l

# Create new database
createdb -O eam_local new_database_name

# Drop database
dropdb -U eam_local database_name
```

### Application Commands:
```bash
# Initialize database with migrations and seeds
cd backend && python -m app.forge init-db

# Run migrations only
cd backend && python -m app.forge migrate

# Seed data only
cd backend && python -m app.forge seed

# Check database status
cd backend && python -m app.forge status
```

---

## Notes
- Local PostgreSQL database created: 2026-02-27
- User `eam_local` has superuser privileges for development
- Remote database is hosted on Contabo VPS (194.233.77.65)
- SQLite database file: `eam_local.db` (in project root when using SQLite)
