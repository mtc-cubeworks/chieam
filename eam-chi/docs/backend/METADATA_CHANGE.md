# Metadata Sync Architecture

> **Version**: 2.0 — Implemented 2026-02-16
> **Inspired by**: Frappe's DocType editor (atomic save pattern)

## Overview

The EAM model editor uses a **single atomic save** that synchronizes metadata across all layers in one request. No manual steps, no desync possible.

## The Workflow

```
User clicks "Save & Sync" in UI
    ↓
PUT /api/admin/model-editor/entity/{name}
    ↓
1. Validate metadata (MetadataValidator)
    ↓
2. Analyze changes — safe vs dangerous (MetadataChangeAnalyzer)
    ↓
3. Backup current JSON (JsonMetadataWriter)
    ↓
4. Save new JSON to disk (JsonMetadataWriter)
    ↓
5. Reload entity in MetaRegistry (RegistryManagerAdapter)
    → /meta/{entity} now serves fresh data
    ↓
6. Update SQLAlchemy model file (ModelGeneratorAdapter)
    ↓
7. Generate Alembic migration if schema changed (MigrationManagerAdapter)
    ↓
8. Apply migration to database (MigrationManagerAdapter)
    ↓
9. Emit WebSocket event (socket_manager)
    ↓
Response with SyncResult → UI shows step-by-step status
```

## Clean Architecture

```
app/
├── domain/protocols/metadata_sync.py    # Pure Python protocols (no framework imports)
│   ├── MetadataReaderProtocol
│   ├── MetadataWriterProtocol
│   ├── MetadataValidatorProtocol
│   ├── ChangeAnalyzerProtocol
│   ├── ModelGeneratorProtocol
│   ├── MigrationManagerProtocol
│   └── RegistryManagerProtocol
│
├── application/services/
│   └── metadata_sync_service.py         # Orchestrator (depends ONLY on protocols)
│       └── MetadataSyncService
│           ├── save_and_sync()          # Atomic save — the core operation
│           ├── preview_changes()        # Read-only analysis
│           ├── list_entities()
│           ├── get_entity()
│           ├── get_migration_status()
│           ├── apply_migrations()
│           ├── rollback_migrations()
│           ├── list_backups()
│           ├── restore_backup()         # Restore + re-sync
│           └── reload_all_metadata()
│
├── infrastructure/metadata/
│   └── adapters.py                      # Concrete implementations
│       ├── JsonMetadataReader           # Reads entity JSON files
│       ├── JsonMetadataWriter           # Writes JSON + manages backups
│       ├── MetadataValidator            # Wraps metadata_validator.py
│       ├── MetadataChangeAnalyzer       # Diff analysis (safe/dangerous)
│       ├── ModelGeneratorAdapter        # Wraps ModelGeneratorService
│       ├── MigrationManagerAdapter      # Wraps MigrationService (Alembic)
│       └── RegistryManagerAdapter       # Manages MetaRegistry
│
├── api/dependencies.py
│   └── get_metadata_sync_service()      # DI factory wiring adapters → service
│
└── routers/admin/model_editor.py        # Thin API layer (no business logic)
```

## SOLID Compliance

| Principle | How                                                               |
| --------- | ----------------------------------------------------------------- |
| **SRP**   | Each adapter has one responsibility (read, write, validate, etc.) |
| **OCP**   | New adapters can be added without modifying MetadataSyncService   |
| **LSP**   | All adapters satisfy their protocol contracts                     |
| **ISP**   | 7 focused protocols instead of one monolithic interface           |
| **DIP**   | MetadataSyncService depends on protocols, not concrete classes    |

## Key Differences from Old System

| Old (multi-step)                                                                 | New (atomic)                         |
| -------------------------------------------------------------------------------- | ------------------------------------ |
| Save JSON → manually Update Model → manually Generate Migration → manually Apply | Single "Save & Sync" does everything |
| 4 separate API calls                                                             | 1 API call                           |
| Desync possible between steps                                                    | No desync possible                   |
| Router contained business logic                                                  | Router is thin, delegates to service |
| Direct service instantiation                                                     | Dependency injection via protocols   |
| No architecture tests                                                            | 16 tests covering all layers         |

## Frontend Changes

- **Single "Save & Sync" button** replaces Save + Update Model + Generate + Apply
- **SyncResult status badges** show JSON → Registry → Model → DB pipeline
- **Warnings displayed** if any non-fatal step had issues
- Removed `updateAllModels` (no longer needed)
- Removed `updateEntityModel`, `generateEntityMigration` API methods

## Test Coverage

```
tests/test_metadata_sync.py — 16 tests:
  - 5 architecture tests (clean architecture compliance)
  - 7 MetadataSyncService unit tests (mocked dependencies)
  - 3 infrastructure adapter tests
  - 1 DI factory test
```
