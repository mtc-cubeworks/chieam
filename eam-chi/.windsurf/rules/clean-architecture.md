# Clean Architecture & SOLID Principles

**System:** EAM (FastAPI backend + Nuxt frontend)

This project strictly follows **SOLID principles** and **Clean Architecture**. All code contributions must conform to the guidelines below. Do not reference specific file names or code snippets in this document — consult the actual codebase for current implementations.

---

## Architecture Overview

The system uses a four-layer Clean Architecture:

- **Domain** — Pure business rules, protocols (interfaces), and exceptions. Zero external dependencies.
- **Application** — Orchestration, use cases, services, hooks, and DTOs. Depends only on Domain.
- **Infrastructure** — Database repositories, auth providers, file I/O, metadata adapters. Implements Domain protocols.
- **API** — Thin HTTP layer (FastAPI routes, Pydantic schemas). Delegates to Application services.
- **Modules** — Feature-specific business logic (hooks, workflow routers, entity APIs, JSON metadata, ORM models).

---

## Dependency Direction

```
API → Application → Domain ← Infrastructure
```

- Domain **never** imports Application or Infrastructure.
- Application **never** imports Infrastructure directly — use dependency injection.
- API only imports Application layer services via DI factories.
- Modules contain business logic that plugs into Application via hooks/decorators.

---

## SOLID Principles

1. **Single Responsibility (SRP)** — Each file/class has one reason to change. Services handle orchestration, repositories handle persistence, routes handle HTTP.
2. **Open/Closed (OCP)** — Extend behavior via decorators and hook registrations, not by modifying existing code. New workflows are added by registering new handlers.
3. **Liskov Substitution (LSP)** — All implementations honor their protocol contracts. Any repository implementation is interchangeable with another that follows the same protocol.
4. **Interface Segregation (ISP)** — Protocols are focused and role-specific. Separate protocols for reading, writing, workflow, naming, etc.
5. **Dependency Inversion (DIP)** — Services depend on abstract protocols, not concrete classes. DI factories in the API layer wire concrete implementations.

---

## Key Rules

### Backend (FastAPI)

- **Business logic** lives in `modules/*/apis/` or `application/services/`, never in API routes.
- **Workflow state changes** must go through the validated workflow service — never assign state directly.
- **Database operations** use Frappe-style document helpers (`get_doc`, `save_doc`, `get_list`, etc.).
- **Error handling**: All mutating operations must be wrapped in try/except with `await db.rollback()` on failure. Commits happen once at the end, not inside loops.
- **Workflow routing** uses a decorator-based registry pattern per module — one decorator per entity, a single `route_workflow()` dispatch function.
- **Hook registration** delegates to the central workflow router; hooks are the entry point, not the logic container.
- **Entity metadata** (JSON files) drives form state, field visibility, editability, child/link relationships, tab rules, and document actions.
- **Children vs Links**: Inline child tables (e.g., line items) are declared in `children` and rendered inside the parent form. Related entities are declared in `links` and shown as separate tabs.

### Frontend (Nuxt)

- **Composables** encapsulate all API calls, form state management, and reusable logic.
- **Components** are presentational — they receive props and emit events, not call APIs directly (except within composables).
- **Scoped styling** — Page-specific CSS must not leak globally. Use `<style scoped>` or scope third-party CSS imports within wrapper classes.
- **Entity metadata** from the backend drives dynamic form rendering, field visibility, editability rules, and grid column generation.

---

## Checklist (for all code changes)

### Architecture

- No infrastructure imports in the application layer
- All dependencies injected, not instantiated directly
- Repository interfaces defined as domain protocols
- Business logic not in API routes
- ORM models only in infrastructure or module model directories

### SOLID

- Single responsibility per file/class
- New behavior added via extension (decorators, hooks), not modification
- Services depend on protocols, not concrete classes
- Interfaces are focused and not bloated

### Workflow & Data

- Entity JSON includes workflow config and form_state rules where applicable
- Workflow state changes go through the validated service
- All DB mutations wrapped in try/except with rollback
- Commits happen once at the end of a transaction
- Action labels in workflow handlers match transition labels in metadata

### Testing

- Mock dependencies via protocols for unit tests
- Integration tests verify HTTP endpoints end-to-end
- Workflow tests cover state transitions and error paths
