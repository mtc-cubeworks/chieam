# EAM 2.1 — System Architecture

A modular, metadata-driven Enterprise Asset Management system built with **FastAPI** (backend) and **Nuxt 4** (frontend).

> **Version:** 2.1.2
> **Last Updated:** 2026-02-09

---

## Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (Nuxt 4 / Vue 3)                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────┐   │
│  │ Sidebar   │ │ UTable    │ │ FormView  │ │ Model Editor   │   │
│  │(metadata) │ │(server pg)│ │(Nuxt UI)  │ │(JSON editor)   │   │
│  └───────────┘ └───────────┘ └───────────┘ └────────────────┘   │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────┐   │
│  │ Socket.IO │ │ Pinia     │ │ Composable│ │ Playwright E2E │   │
│  │(realtime) │ │(stores)   │ │(domain)   │ │ + Vitest       │   │
│  └───────────┘ └───────────┘ └───────────┘ └────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                          │ REST API + Socket.IO
┌──────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ API Layer        api/routes/  +  routers/ (legacy)          │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Application      application/services/  (BaseEntityAPI)     │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Domain           domain/protocols/  (DIP interfaces)        │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Infrastructure   infrastructure/  (DB, events, repos)       │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Services         services/  (business logic)                │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Modules          modules/  (entity JSON + hooks + models)   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                          │ SQLAlchemy (async)
┌──────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (production)                        │
│                    SQLite (development)                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Backend Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI + Socket.IO entry point (97 routes)
│   ├── hooks.py                   # Hooks registry (doc_events)
│   ├── forge.py                   # CLI tool
│   │
│   ├── api/                       # Clean Architecture — API layer
│   │   ├── dependencies.py        # DI factories (get_db, auth, services)
│   │   ├── routes/
│   │   │   ├── entity_crud.py     # POST /api/entity/{e}/action
│   │   │   ├── entity_list.py     # GET  /api/entity/{e}/list
│   │   │   ├── entity_options.py  # GET  /api/entity/{e}/options
│   │   │   ├── entity_workflow.py # POST /api/entity/{e}/workflow
│   │   │   ├── entity_actions.py  # POST /api/entity/{e}/document-action
│   │   │   ├── entity_attachments.py # Attachment CRUD
│   │   │   ├── entity_audit.py    # GET  /api/entity/{e}/{id}/audit
│   │   │   └── entity_print.py    # GET  /api/entity/{e}/{id}/print[/pdf]
│   │   └── schemas/
│   │
│   ├── application/               # Clean Architecture — Application layer
│   │   └── services/
│   │       └── base_entity_api.py # BaseEntityAPI + Context dataclass
│   │
│   ├── domain/                    # Clean Architecture — Domain layer
│   │   └── protocols/
│   │       ├── document_service.py  # DocumentQueryProtocol, DocumentMutationProtocol
│   │       ├── unit_of_work.py      # UnitOfWork protocol
│   │       ├── event_bus.py         # DomainEventBus protocol
│   │       └── cache_protocol.py    # CacheProtocol interface
│   │
│   ├── infrastructure/            # Clean Architecture — Infrastructure layer
│   │   ├── database/
│   │   │   ├── repositories/
│   │   │   │   ├── entity_repository.py
│   │   │   │   └── workflow_repository.py
│   │   │   └── unit_of_work.py
│   │   └── events/
│   │       └── domain_event_bus.py
│   │
│   ├── core/                      # Framework configuration
│   │   ├── config.py              # Settings (env-driven)
│   │   ├── database.py            # SQLAlchemy async engine
│   │   ├── security.py            # JWT + password + RBAC
│   │   ├── base_model.py          # BaseModel (id, created_at, updated_at)
│   │   ├── sanitization.py        # HTML sanitization for XSS prevention
│   │   └── exceptions.py          # Custom exception handlers
│   │
│   ├── meta/
│   │   └── registry.py            # MetaRegistry, EntityMeta, FieldMeta, AttachmentConfig
│   │
│   ├── modules/                   # Modular entity system
│   │   ├── core_eam/              # Core EAM entities
│   │   │   ├── entities/          # {entity}/{entity}.json + {entity}.py
│   │   │   └── models/
│   │   ├── asset_management/
│   │   ├── maintenance/
│   │   ├── purchasing/
│   │   └── stores/
│   │
│   ├── services/                  # Business logic services
│   │   ├── document_query.py      # get_doc, get_list, get_value
│   │   ├── document_mutation.py   # insert_doc, update_doc, delete_doc
│   │   ├── export_service.py      # Excel/CSV export
│   │   ├── import_export.py       # Import validation + execution
│   │   ├── metadata_editor.py     # JSON metadata CRUD
│   │   ├── metadata_validator.py  # Metadata validation rules
│   │   ├── model_generator.py     # SQLAlchemy model code generation
│   │   ├── migration_service.py   # Alembic migration management
│   │   ├── print_service.py       # Jinja2 HTML + Playwright PDF
│   │   ├── naming.py              # Human-readable ID generation
│   │   ├── rbac.py                # Role-based access control
│   │   ├── audit.py               # Audit trail logging
│   │   ├── workflow.py            # Workflow DB service
│   │   ├── socketio_manager.py    # Socket.IO event emission
│   │   └── server_actions.py      # Frappe-style server action loader
│   │
│   ├── routers/                   # Legacy routes (incrementally migrating)
│   │   ├── meta.py                # /api/meta endpoints
│   │   ├── admin/                 # Admin panel + model editor
│   │   │   └── model_editor.py
│   │   ├── auth.py                # Login/logout/refresh
│   │   ├── workflow.py            # Workflow management
│   │   └── import_export.py       # Import/export routes
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── attachment.py          # File attachment model
│   │   ├── audit_log.py           # Audit trail model
│   │   └── workflow.py            # Workflow state/transition models
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   └── base.py                # ActionRequest, ActionResponse
│   │
│   ├── entities/                  # Entity loader + generator
│   │   ├── __init__.py            # load_all_entities(), load_entity_from_json()
│   │   └── generator.py           # FIELD_TYPE_MAP strategy pattern
│   │
│   └── templates/
│       └── print/
│           └── default.html       # Jinja2 print template
│
├── backups/                       # Metadata/model backups (outside app/)
│   ├── metadata/
│   └── models/
│
├── tests/
│   ├── test_architecture.py       # 5 tests — layer boundary enforcement
│   ├── test_services_unit.py      # 20 tests — service unit tests
│   └── test_api_integration.py    # 17 tests — route registration + schemas
│
├── alembic/                       # Database migrations
├── requirements.txt
└── .env
```

---

## Frontend Directory Structure

```
frontend/
├── app/
│   ├── app.vue                    # Root — error boundary + global modals
│   ├── layouts/
│   │   └── default.vue            # Sidebar + breadcrumbs + main content
│   │
│   ├── pages/
│   │   ├── login.vue
│   │   ├── [entity]/
│   │   │   ├── index.vue          # List view (UTable, bulk actions, tree view)
│   │   │   └── [id].vue           # Detail/form view (tabs, workflow, attachments)
│   │   ├── model-editor/
│   │   │   ├── index.vue          # Entity list for editing
│   │   │   └── [entity].vue       # JSON metadata editor
│   │   ├── admin/
│   │   │   └── index.vue          # Users, roles, permissions, ordering
│   │   ├── workflow/
│   │   │   └── index.vue          # Workflow states + transitions manager
│   │   └── import-export.vue      # Import/export page
│   │
│   ├── composables/               # Domain-specific composables
│   │   ├── useApiTypes.ts         # All shared TypeScript interfaces (single source)
│   │   ├── useApi.ts              # Backward-compatible facade (no type re-exports)
│   │   ├── useApiFetch.ts         # Auth-aware fetch wrapper + token refresh
│   │   ├── useEntityApi.ts        # Entity CRUD, list, options
│   │   ├── useAdminApi.ts         # User/role/permission management
│   │   ├── useWorkflowApi.ts      # Workflow CRUD + transitions
│   │   ├── useModelEditorApi.ts   # Model editor + migrations + backups
│   │   ├── useImportExportApi.ts  # Import/export operations
│   │   ├── useAttachmentApi.ts    # Attachment CRUD
│   │   ├── useAuditApi.ts         # Audit trail
│   │   ├── useFormState.ts        # Field visibility, editability, tab rules
│   │   ├── useFormValidation.ts   # Metadata-driven validation
│   │   ├── useTreeView.ts         # Tree view for hierarchical entities
│   │   ├── useBootInfo.ts         # Boot info (sidebar, user, token)
│   │   ├── useAuth.ts             # Authentication composable
│   │   ├── useNotify.ts           # Toast notification wrapper
│   │   ├── useBreadcrumbs.ts      # Dynamic breadcrumb generation
│   │   ├── useAsyncSearch.ts      # Debounced server-side search
│   │   ├── useColumnPreferences.ts # Persisted column visibility (localStorage)
│   │   ├── useSavedFilters.ts     # Persisted filter presets (localStorage)
│   │   ├── useInlineEdit.ts       # Inline cell editing in tables
│   │   ├── useOptimisticUpdate.ts # Optimistic UI updates with rollback
│   │   ├── useOptimisticLock.ts   # Concurrent edit detection (updated_at)
│   │   ├── useEntityLive.ts       # Socket.IO entity change subscriptions
│   │   └── useNotificationCenter.ts # In-app notification center
│   │
│   ├── components/
│   │   ├── ConfirmModal.vue       # Global confirmation modal
│   │   ├── DeleteModal.vue        # Global delete confirmation modal
│   │   ├── AuditTrail.vue         # Audit trail display
│   │   ├── TreeView.vue           # Hierarchical tree view
│   │   ├── entity/
│   │   │   ├── EntityFieldRenderer.vue  # Dynamic field rendering
│   │   │   └── EntityAttachmentsTab.vue # Attachment management
│   │   ├── admin/                 # Admin panel components
│   │   └── workflow/              # Workflow management components
│   │
│   ├── stores/                    # Pinia stores
│   │   ├── auth.ts                # Authentication state
│   │   ├── cache.ts               # API response cache with TTL
│   │   ├── deleteModal.ts         # Delete modal state
│   │   ├── confirmModal.ts        # Confirm modal state
│   │   ├── entityModal.ts         # Entity create/edit modal
│   │   └── importExport.ts        # Import/export state
│   │
│   ├── plugins/
│   │   └── socket.client.ts       # Socket.IO client (entity:change, meta:change, post_save)
│   │
│   └── assets/css/
│       └── main.css               # Tailwind + print styles + responsive mobile
│
├── tests/
│   └── composables/
│       └── useFormValidation.test.ts  # 8 Vitest unit tests
│
├── e2e/
│   └── login.spec.ts             # Playwright E2E tests
│
├── vitest.config.ts
├── playwright.config.ts
├── nuxt.config.ts
└── package.json
```

---

## Key Features

### Entity System

- **Metadata-driven**: UI rendered entirely from JSON entity definitions
- **Human-readable IDs**: `AST-0001`, `WO-0002` (not UUIDs)
- **Hooks system**: Frappe-style lifecycle hooks (validate, before/after CRUD, workflow)
- **Server actions**: Python dotted-path methods (`app.modules.xxx.function_name`)
- **Conditional fields**: `display_depends_on`, `mandatory_depends_on` with eval expressions
- **Form state rules**: `editable_when`, `show_when`, `required_when` per field/tab

### Workflow Engine

- DB-driven states and transitions (not hardcoded)
- JSON-defined workflows per entity (initial_state, states, transitions)
- Frontend workflow action dropdown with state-based filtering

### Attachment System

- Per-entity `attachment_config` (enable, max count, file size, extensions)
- File upload/download/delete with RBAC
- Stored on disk with metadata in `attachment` table

### Print System

- **Jinja2 HTML templates** per entity (with `default.html` fallback)
- **Playwright PDF generation** via `/api/entity/{e}/{id}/print/pdf`
- HTML preview via `/api/entity/{e}/{id}/print`

### Real-time Updates

- **Socket.IO** for entity:change, meta:change, post_save events
- Automatic cache invalidation on changes
- `useEntityLive` composable for per-entity subscriptions

### Security

- JWT authentication with token refresh
- Role-based access control (RBAC) per entity per action
- Rate limiting (slowapi)
- CORS with origin regex
- HTML sanitization for XSS prevention
- Audit trail logging (before/after snapshots)

### Testing

- **Backend**: 42 tests (5 architecture + 20 unit + 17 integration)
- **Frontend**: 8 Vitest unit tests + Playwright E2E setup
- Architecture tests enforce clean layer boundaries

---

## API Endpoints (97 routes)

### Entity CRUD

| Method | Endpoint                                        | Description                      |
| ------ | ----------------------------------------------- | -------------------------------- |
| GET    | `/api/entity/{e}/list`                          | Paginated list with sort/filter  |
| GET    | `/api/entity/{e}/detail/{id}`                   | Single record with link titles   |
| GET    | `/api/entity/{e}/options`                       | Options for link field dropdowns |
| POST   | `/api/entity/{e}/action`                        | Create / Update / Delete         |
| POST   | `/api/entity/{e}/{id}/document-action/{action}` | Server action execution          |
| POST   | `/api/entity/{e}/{id}/workflow/{action}`        | Workflow transition              |

### Attachments

| Method | Endpoint                                          | Description      |
| ------ | ------------------------------------------------- | ---------------- |
| GET    | `/api/entity/{e}/{id}/attachments`                | List attachments |
| POST   | `/api/entity/{e}/{id}/attachments`                | Upload file      |
| GET    | `/api/entity/{e}/{id}/attachments/{aid}/download` | Download file    |
| DELETE | `/api/entity/{e}/{id}/attachments/{aid}`          | Delete file      |

### Print

| Method | Endpoint                         | Description  |
| ------ | -------------------------------- | ------------ |
| GET    | `/api/entity/{e}/{id}/print`     | HTML preview |
| GET    | `/api/entity/{e}/{id}/print/pdf` | PDF download |

### Meta & Admin

| Method  | Endpoint                                                | Description       |
| ------- | ------------------------------------------------------- | ----------------- |
| GET     | `/api/meta`                                             | All entities list |
| GET     | `/api/meta/{entity}`                                    | Entity metadata   |
| GET/PUT | `/api/admin/model-editor/entity/{e}`                    | Model editor      |
| POST    | `/api/admin/model-editor/entity/{e}/update-model`       | Regenerate model  |
| POST    | `/api/admin/model-editor/entity/{e}/generate-migration` | Alembic migration |

### Auth

| Method | Endpoint            | Description         |
| ------ | ------------------- | ------------------- |
| POST   | `/api/auth/login`   | Login (returns JWT) |
| POST   | `/api/auth/refresh` | Refresh token       |
| GET    | `/api/auth/me`      | Current user info   |

---

## Running the Application

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:fastapi_app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Tests
cd backend && python -m pytest tests/ -v
cd frontend && npm test          # Vitest
cd frontend && npm run test:e2e  # Playwright
```

**URLs:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Key Principles

1. **Metadata-driven**: UI and behavior defined by JSON, not code
2. **Clean Architecture**: Domain protocols → Application services → API routes
3. **Hooks for customization**: Business logic via lifecycle hooks
4. **Human-readable IDs**: Entity codes as primary keys
5. **Real-time**: Socket.IO for live updates and cache invalidation
6. **RBAC**: Role-based permissions per entity per action
7. **Modular**: Entities organized in installable modules
8. **PostgreSQL-first**: Production-ready with SQLite fallback
9. **Print-ready**: Jinja2 templates + Playwright PDF generation
10. **Tested**: Architecture enforcement + unit + integration tests
