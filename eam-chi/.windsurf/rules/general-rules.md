# Stack

- Backend: FastAPI (Python)
- Frontend: Nuxt 3, NuxtUI v4, TypeScript, Pinia, TailwindCSS

# Core Philosophy

- Fix root causes, not symptoms.
- Present 2-3 solution approaches with trade-offs, then recommend one.

# Code Style

- One function = one responsibility. If you need "and" to describe it, split it.
- Avoid deep nesting — use early returns and extract utilities.
- RO-RO pattern for functions with multiple params or return values.
- Arrow functions for simple cases (<3 lines), named functions otherwise.

# Frontend Rules

- Server state → `useFetch` / `useAsyncData`. UI state → Pinia. Local state → `ref`.
- Logic in composables, presentation in components.
- Use NuxtUI v4 primitives before writing custom UI.

# Backend Rules

- Pydantic models for all request/response shapes — no raw dicts in routes.
- Use dependency injection for auth, DB sessions, and shared services.
- Raise `HTTPException` with consistent shape: `{ detail, code }`.

# Type Safety

- Frontend types generated from FastAPI's OpenAPI schema — never written manually.
- Backend is source of truth for all shared types and enums.
