# Windsurf Rules — Quick Reference

**Purpose:** Guide for AI assistants and developers on which rule file to use for different tasks.

---

## Rule Files Overview

| Rule File | Purpose | When to Use |
|-----------|---------|-------------|
| **forge-cli.md** | Entity & migration toolkit | Changing JSON, models, fields, or DB schema |
| **clean-architecture.md** | Architecture & business logic | Writing business logic, workflows, or refactoring |
| **backend-dev-tools.md** | Querying, testing, CLI tools | Writing queries, tests, or using CLI commands |
| **nuxt-ui-tools.md** | Frontend UI components | Building frontend UI with Nuxt UI |

---

## Decision Tree

### I need to...

#### **Change the database schema**
→ Use **`forge-cli.md`**
- Added/removed field in entity JSON
- Changed field type
- Created new entity
- Need to sync models to DB

**Quick answer:** Run `forge sync -m "description"`

---

#### **Write business logic or workflow**
→ Use **`clean-architecture.md`**
- Implementing workflow handlers
- Creating server actions
- Writing validation logic
- Refactoring to SOLID principles

**Key patterns:**
- Use `@register_workflow` decorator
- Always rollback on errors
- Use `apply_workflow_state()` for state changes
- Follow dependency injection patterns

---

#### **Query the database or write tests**
→ Use **`backend-dev-tools.md`**
- Fetching records with `get_doc()` / `get_list()`
- Writing unit/integration tests
- Using pytest or Alembic CLI
- Performance optimization

**Quick reference:**
```python
# Query
doc = await get_doc("asset", asset_id, db)
lines = await get_list("pr_line", {"pr": pr_id}, db)

# Test
pytest tests/test_purchase_request.py -v
```

---

#### **Build frontend UI**
→ Use **`nuxt-ui-tools.md`**
- Using Nuxt UI components
- Checking component props/slots
- Theming and styling

**Quick reference:**
- Use Nuxt UI MCP server for component docs
- Reference `@docs https://ui.nuxt.com/llms.txt`

---

## Common Scenarios

### Scenario: "I added a field to an entity JSON"

**Files to trigger:**
1. **`forge-cli.md`** — Understand the sync workflow
2. Run: `forge sync -m "add field_name to entity"`

**What happens:**
- Forge regenerates model from JSON
- Generates Alembic migration
- Applies migration to DB

---

### Scenario: "I need to implement a workflow action"

**Files to trigger:**
1. **`clean-architecture.md`** — Follow workflow implementation pattern
2. **`backend-dev-tools.md`** — Use document helpers for queries

**Pattern:**
```python
# In workflow_router.py
@register_workflow("entity_name")
async def entity_workflow(doc, action, db, user):
    try:
        if action == "Approve":
            # Business logic
            result = await apply_workflow_state("entity", doc, "approve", db)
            return result
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}
```

---

### Scenario: "I need to write tests for a workflow"

**Files to trigger:**
1. **`backend-dev-tools.md`** — Testing patterns section
2. **`clean-architecture.md`** — Workflow compliance checklist

**Pattern:**
```python
@pytest.mark.asyncio
async def test_approve_workflow(db):
    pr = await new_doc("purchase_request", db, workflow_state="draft")
    result = await apply_workflow_state("purchase_request", pr, "approve", db)
    assert result["status"] == "success"
    assert pr.workflow_state == "approved"
```

---

### Scenario: "I'm getting 'Table already defined' error"

**Files to trigger:**
1. **`forge-cli.md`** — Safety Guards section

**Cause:** Duplicate entity JSON creating model that conflicts with `app/models/*`

**Fix:** Delete the conflicting entity JSON. Reserved tables are protected by Forge.

---

### Scenario: "I need to optimize slow queries"

**Files to trigger:**
1. **`backend-dev-tools.md`** — Performance Tips section

**Patterns:**
- Fetch only needed fields: `fields=["id", "name"]`
- Avoid N+1: Batch fetch related records
- Use batch commits: `commit=False` in loops

---

## File Structure Quick Reference

```
.windsurf/rules/
├── README.md                 ← You are here
├── forge-cli.md              ← Entity/migration toolkit
├── clean-architecture.md     ← SOLID + business logic + workflows
├── backend-dev-tools.md      ← Queries + tests + CLI
└── nuxt-ui-tools.md          ← Frontend UI components
```

---

## Integration Points

### Forge CLI ↔ Clean Architecture
- **Forge** generates models from JSON
- **Clean Architecture** defines how to use those models in business logic
- **Connection:** Entity JSON → Model → Service layer → Workflow handlers

### Clean Architecture ↔ Backend Dev Tools
- **Clean Architecture** defines patterns (SOLID, DIP, workflows)
- **Backend Dev Tools** provides concrete helpers (`get_doc`, `save_doc`, etc.)
- **Connection:** Services use document helpers to implement business logic

### All Rules → Testing
- **Forge CLI:** Test migrations with `forge migrate --status`
- **Clean Architecture:** Test workflows with `apply_workflow_state()`
- **Backend Dev Tools:** Test patterns with pytest

---

## Maintenance

### When to Update These Rules

| Update Trigger | Files to Update |
|----------------|-----------------|
| New Forge command added | `forge-cli.md` |
| New SOLID pattern adopted | `clean-architecture.md` |
| New document helper added | `backend-dev-tools.md` |
| New Nuxt UI version | `nuxt-ui-tools.md` |
| Architecture refactor | `clean-architecture.md` + `README.md` |

### Rule Versioning

Rules are versioned implicitly via git commits. Major changes should be documented in:
- Commit messages
- Memory system (for AI assistants)
- This README's changelog section (below)

---

## Changelog

### 2026-02-28 — Major Refactor
- **Consolidated:** `solid-clean-architecture.md` + `business-logic-patterns.md` → `clean-architecture.md`
- **Renamed:** `frappe-document-patterns.md` → `backend-dev-tools.md`
- **Rewrote:** `forge-cli.md` with v2 features (fast path, progress bar, safety guards)
- **Added:** This README for quick navigation

**Rationale:**
- Reduce duplication between SOLID and business logic rules
- Create clear decision tree for which rule to use
- Align with Forge CLI v2 optimizations
- Consolidate query/test/CLI patterns in one place

---

## Quick Start for AI Assistants

When a user asks to:
1. **Change schema** → Read `forge-cli.md` → Run `forge sync`
2. **Write business logic** → Read `clean-architecture.md` → Follow patterns
3. **Query/test** → Read `backend-dev-tools.md` → Use helpers
4. **Build UI** → Read `nuxt-ui-tools.md` → Use Nuxt UI MCP

**Always:**
- Check file triggers table in `forge-cli.md`
- Follow SOLID principles in `clean-architecture.md`
- Use document helpers from `backend-dev-tools.md`
- Rollback on errors (mandatory pattern)
