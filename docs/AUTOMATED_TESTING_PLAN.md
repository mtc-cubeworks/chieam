# EAM Automated Testing & Documentation Framework

## Implementation Plan

**Date:** April 10, 2026
**Based on:** The Dual-Purpose Automation Framework White Paper
**Target System:** EAM-CHI (Enterprise Asset Management)

---

## 1. Current State Assessment

### What Exists
| Component | Status | Details |
|-----------|--------|---------|
| Playwright | ✅ Installed | v1.58.2, configured in `playwright.config.ts` |
| E2E Tests | ⚠️ Minimal | 1 file (`e2e/login.spec.ts`) with 5 basic tests |
| Unit Tests | ⚠️ Minimal | 3 test files (ChildDataGrid, RelatedDataGrid, useFormValidation) |
| Vitest | ✅ Installed | v4.0.18, `happy-dom` environment |
| TypeScript | ✅ Configured | Strict mode, Nuxt 4 integration |
| CI/CD | ❌ None | No GitHub Actions workflows |

### Application Scale
- **136 entity types** across 5 modules
- **5 modules:** Asset Management (26), Core EAM (31), Maintenance Mgmt (22), Purchasing & Stores (38), Work Mgmt (19)
- **Key pages:** Login, Dashboard, Entity List (dynamic `[entity]`), Entity Detail (`[entity]/[id]`), Admin, Workflow, Calendar, Reports, Settings, Setup
- **Auth:** JWT token-based with refresh flow, bcrypt password hashing

---

## 2. Architecture Design

### Framework Structure

```
frontend/
├── e2e/
│   ├── definitions/                 # YAML workflow definitions
│   │   ├── auth/
│   │   │   ├── login-happy.yaml
│   │   │   └── login-edge-cases.yaml
│   │   ├── asset-management/
│   │   │   ├── asset-lifecycle.yaml
│   │   │   ├── asset-tree-view.yaml
│   │   │   └── meter-reading.yaml
│   │   ├── work-management/
│   │   │   ├── work-order-lifecycle.yaml
│   │   │   └── job-plan-create.yaml
│   │   ├── maintenance/
│   │   │   ├── maintenance-request-lifecycle.yaml
│   │   │   └── pm-calendar.yaml
│   │   ├── purchasing/
│   │   │   ├── purchase-request-lifecycle.yaml
│   │   │   ├── inventory-management.yaml
│   │   │   └── stock-count.yaml
│   │   └── core/
│   │       ├── organization-setup.yaml
│   │       ├── employee-management.yaml
│   │       └── dashboard-overview.yaml
│   │
│   ├── framework/                   # Dual-purpose framework core
│   │   ├── observer.ts              # Screenshot + DOM capture "Observer"
│   │   ├── yaml-runner.ts           # YAML-to-Playwright interpreter
│   │   ├── artifact-index.ts        # Visual Artifact Index builder
│   │   ├── auth-helper.ts           # Reusable login/session helper
│   │   └── selectors.ts             # Centralized stable selectors
│   │
│   ├── page-objects/                # Page Object Models
│   │   ├── login.page.ts
│   │   ├── dashboard.page.ts
│   │   ├── entity-list.page.ts
│   │   ├── entity-detail.page.ts
│   │   ├── admin.page.ts
│   │   └── sidebar.page.ts
│   │
│   ├── fixtures/                    # Playwright custom fixtures
│   │   └── eam-fixtures.ts          # Auth state, test data, observer
│   │
│   ├── workflows/                   # Coded workflow tests (complex flows)
│   │   ├── asset-lifecycle.spec.ts
│   │   ├── work-order-flow.spec.ts
│   │   ├── maintenance-request.spec.ts
│   │   ├── purchase-to-pay.spec.ts
│   │   └── stock-count.spec.ts
│   │
│   ├── visual/                      # Visual regression tests
│   │   ├── screenshots/             # Golden baseline images
│   │   └── visual-regression.spec.ts
│   │
│   ├── login.spec.ts                # (existing - keep)
│   └── runner.spec.ts               # YAML-driven test executor
│
├── scripts/
│   └── generate-manual.ts           # AI post-processor for user manual
│
├── test-artifacts/                  # Generated output (gitignored)
│   ├── screenshots/                 # Captured screenshots
│   ├── index.json                   # Visual Artifact Index
│   └── manual/                      # Generated markdown manual
│
└── playwright.config.ts             # Enhanced config (multi-project)
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Framework scaffolding, auth fixtures, page objects

| # | Task | Files |
|---|------|-------|
| 1.1 | Update `playwright.config.ts` with multi-project setup (test mode + manual-capture mode), storage state for auth, screenshot dirs | `playwright.config.ts` |
| 1.2 | Create auth helper with reusable login + storage state | `e2e/framework/auth-helper.ts` |
| 1.3 | Create Observer module (hooks into Playwright lifecycle, captures screenshots + DOM + metadata into index.json) | `e2e/framework/observer.ts` |
| 1.4 | Create Artifact Index builder (manages `index.json` manifest) | `e2e/framework/artifact-index.ts` |
| 1.5 | Create custom Playwright fixtures (authenticated page, observer injection) | `e2e/fixtures/eam-fixtures.ts` |
| 1.6 | Create Page Object Models for Login, Dashboard, Entity List, Entity Detail, Sidebar | `e2e/page-objects/*.ts` |
| 1.7 | Create centralized selectors map | `e2e/framework/selectors.ts` |

### Phase 2: YAML Definition Engine (Week 1-2)
**Goal:** YAML schema + interpreter for data-driven tests

| # | Task | Files |
|---|------|-------|
| 2.1 | Define YAML workflow schema (TypeScript types + Zod validation) | `e2e/framework/yaml-runner.ts` |
| 2.2 | Implement YAML-to-Playwright interpreter (maps `goto`, `click`, `type`, `select`, `screenshot`, `wait`, `hover` actions) | `e2e/framework/yaml-runner.ts` |
| 2.3 | Implement assertion engine (`visible`, `hidden`, `hasText`, `hasValue`, `urlContains`) | `e2e/framework/yaml-runner.ts` |
| 2.4 | Create `runner.spec.ts` that auto-discovers and runs all `.yaml` definitions | `e2e/runner.spec.ts` |

### Phase 3: Core Workflow Tests (Week 2-3)
**Goal:** Cover the 10 most critical EAM workflows

#### Priority 1 — Authentication & Navigation
| Workflow | Type | Coverage |
|----------|------|----------|
| Login (happy path) | YAML | Valid credentials → dashboard redirect |
| Login (edge cases) | YAML | Wrong password, empty fields, locked account |
| Sidebar navigation | YAML | Navigate to each module → verify page loads |
| Dashboard | YAML | Verify KPI cards, charts render, data displayed |

#### Priority 2 — Asset Management (Core Module)
| Workflow | Type | Coverage |
|----------|------|----------|
| Asset lifecycle | Coded + YAML | Create → Inspect → Install → Active → Decommission (full workflow) |
| Asset tree view | YAML | Parent/child asset hierarchy display |
| Meter reading | YAML | Create meter → record reading → verify history |

#### Priority 3 — Work Management
| Workflow | Type | Coverage |
|----------|------|----------|
| Work order lifecycle | Coded + YAML | Requested → Approved → In Progress → Closed |
| Job plan creation | YAML | Create job plan with tasks → attach to WO |

#### Priority 4 — Maintenance Management
| Workflow | Type | Coverage |
|----------|------|----------|
| Maintenance request | Coded + YAML | Draft → Pending Approval → Approved → Release → Completed |
| PM calendar | YAML | View scheduled maintenance on calendar |
| Failed inspection → WO | Coded | Inspection fail triggers WOA + MR |

#### Priority 5 — Purchasing & Stores
| Workflow | Type | Coverage |
|----------|------|----------|
| Purchase request lifecycle | Coded + YAML | Draft → Submitted → Approved |
| Inventory management | YAML | View stock levels, item search |
| Stock count flow | Coded | Create count → count tasks → reconcile |

#### Priority 6 — Admin & Setup
| Workflow | Type | Coverage |
|----------|------|----------|
| Organization setup | YAML | Create org → site → department |
| Employee management | YAML | CRUD employee records |
| User/role management | YAML | Create user, assign roles |

### Phase 4: Edge Case & Visual Testing (Week 3)
**Goal:** Negative paths, validation, responsive, visual regression

| # | Task | Details |
|---|------|---------|
| 4.1 | Form validation tests | Submit empty required fields → assert error messages appear |
| 4.2 | Duplicate entry tests | Create entity with duplicate unique field → assert error |
| 4.3 | Permission tests | Non-admin user tries restricted action → assert forbidden |
| 4.4 | Empty state tests | Navigate to entity with no records → verify empty state UI |
| 4.5 | Visual regression baselines | Capture golden screenshots for login, dashboard, each entity list |
| 4.6 | Responsive breakpoints | Run key flows at 1280px (desktop), 768px (tablet), 375px (mobile) |

### Phase 5: AI Manual Generation (Week 4)
**Goal:** `index.json` → LLM → User Manual markdown → PDF

| # | Task | Files |
|---|------|-------|
| 5.1 | Build `generate-manual.ts` script that reads `index.json` + screenshots | `scripts/generate-manual.ts` |
| 5.2 | Create LLM prompt templates (intro, step-by-step, troubleshooting sections) | Embedded in script |
| 5.3 | Add Markdown-to-PDF conversion (using Playwright's `page.pdf()`) | `scripts/generate-manual.ts` |
| 5.4 | Create npm scripts: `test:e2e:manual` (capture mode), `generate:manual` | `package.json` |

### Phase 6: CI/CD Pipeline (Week 4)
**Goal:** Automate everything in GitHub Actions

| # | Task | Files |
|---|------|-------|
| 6.1 | PR workflow: Run tests → visual regression → report | `.github/workflows/e2e-tests.yml` |
| 6.2 | Main branch workflow: Capture mode → generate manual → deploy docs | `.github/workflows/generate-docs.yml` |
| 6.3 | Artifact upload (screenshots, index.json, manual PDF) | In workflows |

---

## 4. Technical Design Details

### 4.1 Playwright Config (Multi-Project)

```typescript
// Two modes: fast PR testing + full manual-capture mode
projects: [
  {
    name: 'test',            // PR validation (fast)
    testDir: './e2e',
    testIgnore: ['**/runner.spec.ts'],
    use: { screenshot: 'only-on-failure' }
  },
  {
    name: 'manual-capture',  // Documentation generation (full screenshots)
    testDir: './e2e',
    use: { screenshot: 'on', video: 'on' }
  },
  {
    name: 'visual-regression',
    testDir: './e2e/visual',
    use: { screenshot: 'on' }
  }
]
```

### 4.2 Observer Module

The Observer hooks into every test step and captures:

```typescript
interface ArtifactEntry {
  id: string;                          // e.g., "WO_LIFECYCLE_STEP_03"
  persona: string;                     // e.g., "Admin"
  workflow: string;                    // e.g., "WorkOrderLifecycle"
  action: string;                      // e.g., "Click 'Approve' button"
  visual_artifact: string;             // path to screenshot PNG
  url: string;                         // current page URL
  timestamp: string;                   // ISO timestamp
  dom_context: {
    page_title: string;
    active_element: string;
    visible_errors: string[];
    toast_messages: string[];
    status: 'Success' | 'ValidationError' | 'Loading' | 'Empty';
  };
  doc_metadata: {
    title: string;                     // "Approving a Work Order"
    caption: string;                   // "Click the Approve button..."
    is_edge_case: boolean;
    manual_hint: string;               // AI writing guidance
  };
}
```

### 4.3 YAML Workflow Definition

```yaml
# Example: e2e/definitions/work-management/work-order-lifecycle.yaml
name: work-order-lifecycle
description: Create and process a work order through its complete lifecycle
persona: Admin
base_url: /work_order

steps:
  - id: WO_01_NAVIGATE
    action: goto
    url: /work_order
    assertions:
      - type: visible
        target: '[data-testid="entity-table"]'
    doc_metadata:
      title: "Accessing Work Orders"
      caption: "Navigate to the Work Order list from the sidebar menu."

  - id: WO_02_CREATE
    action: click
    target: 'button:has-text("New")'
    doc_metadata:
      title: "Creating a New Work Order"
      caption: "Click the 'New' button to open the work order form."

  - id: WO_03_FILL_TYPE
    action: select
    target: '[data-field="work_order_type"]'
    value: "Corrective Maintenance"
    doc_metadata:
      title: "Selecting Work Order Type"
      caption: "Choose the appropriate work order type from the dropdown."

  - id: WO_04_FILL_DESC
    action: type
    target: '[data-field="description"]'
    value: "Replace conveyor belt bearing - Unit A3"

  - id: WO_05_FILL_PRIORITY
    action: select
    target: '[data-field="priority"]'
    value: "High"

  - id: WO_06_SAVE
    action: click
    target: 'button:has-text("Save")'
    assertions:
      - type: hasText
        target: '.toast-message'
        value: "created successfully"
    doc_metadata:
      title: "Saving the Work Order"
      caption: "Click Save. The system assigns an auto-generated WO number."

  - id: WO_07_APPROVE
    action: click
    target: 'button:has-text("Approve")'
    assertions:
      - type: hasText
        target: '[data-testid="workflow-state"]'
        value: "Approved"
    doc_metadata:
      title: "Approving the Work Order"
      caption: "Use the workflow action button to approve the work order."
```

### 4.4 Auth Fixture (Storage State Pattern)

```typescript
// Playwright "storageState" pattern — login once, reuse across all tests
// e2e/fixtures/eam-fixtures.ts

import { test as base, Page } from '@playwright/test';
import { Observer } from '../framework/observer';

type EAMFixtures = {
  authenticatedPage: Page;
  observer: Observer;
};

export const test = base.extend<EAMFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: './e2e/.auth/admin.json'
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
  observer: async ({}, use) => {
    const obs = new Observer({ outputDir: './test-artifacts' });
    await use(obs);
    await obs.flush();   // writes index.json on teardown
  }
});
```

### 4.5 Page Object: Entity List

```typescript
// e2e/page-objects/entity-list.page.ts
import { Page, Locator } from '@playwright/test';

export class EntityListPage {
  readonly page: Page;
  readonly newButton: Locator;
  readonly table: Locator;
  readonly searchInput: Locator;
  readonly pagination: Locator;
  readonly viewModeButtons: Locator;

  constructor(page: Page) {
    this.page = page;
    this.newButton = page.locator('button:has-text("New")');
    this.table = page.locator('[data-testid="entity-table"], table');
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.pagination = page.locator('[data-testid="pagination"]');
    this.viewModeButtons = page.locator('[data-testid="view-mode"]');
  }

  async goto(entity: string) {
    await this.page.goto(`/${entity}`);
    await this.page.waitForLoadState('networkidle');
  }

  async create() {
    await this.newButton.click();
  }

  async search(term: string) {
    await this.searchInput.fill(term);
    await this.page.waitForTimeout(500);
  }

  async getRowCount(): Promise<number> {
    return this.table.locator('tbody tr').count();
  }
}
```

---

## 5. Artifact Index → Manual Generation Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Playwright Tests (manual-capture project)                       │
│                                                                  │
│  Step 1: Login ──► Step 2: Navigate ──► Step 3: Create ──► ...   │
│       │                  │                    │                   │
│   screenshot          screenshot          screenshot             │
│   + DOM snap          + DOM snap          + DOM snap             │
│       │                  │                    │                   │
│       └──────────────────┴────────────────────┘                  │
│                          │                                       │
│                    Observer Module                                │
│                          │                                       │
│                    index.json                                    │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  generate-manual.ts                                              │
│                                                                  │
│  1. Read index.json (grouped by workflow)                        │
│  2. For each workflow:                                           │
│     - Send artifact entries + manual_hints to LLM                │
│     - LLM generates markdown section with image references       │
│  3. Assemble full manual:                                        │
│     - Table of Contents                                          │
│     - Module chapters (Asset, WO, Maintenance, Purchasing)       │
│     - Troubleshooting appendix (edge case artifacts)             │
│  4. Convert to PDF via Playwright page.pdf()                     │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                   USER_MANUAL.pdf
                   USER_MANUAL.md
```

---

## 6. Test Coverage Matrix

### Entities to Test (Priority Tiers)

**Tier 1 — Critical (full workflow tests with screenshots):**
| Entity | Module | Workflow States | Test Type |
|--------|--------|----------------|-----------|
| Asset | Asset Mgmt | acquired → inspected → active → decommissioned | Coded + YAML |
| Work Order | Work Mgmt | Requested → Approved → In Progress → Closed | Coded + YAML |
| Maintenance Request | Maintenance | Draft → Pending → Approved → Release → Completed | Coded + YAML |
| Purchase Request | Purchasing | Draft → Submitted → Approved | Coded + YAML |
| Inspection | Purchasing | Draft → Start → Completed/Failed | Coded |

**Tier 2 — Important (CRUD + basic workflow):**
| Entity | Module |
|--------|--------|
| Organization, Site, Department | Core EAM |
| Employee | Core EAM |
| Item, Inventory | Purchasing |
| Vendor | Purchasing |
| Job Plan | Work Mgmt |
| Maintenance Plan | Maintenance |
| Meter / Meter Reading | Asset Mgmt |

**Tier 3 — Standard (CRUD smoke tests, YAML-driven):**
All remaining entities — auto-generated YAML tests for:
- Navigate to list page → verify table loads
- Click "New" → verify form opens
- Save empty form → verify validation errors

---

## 7. npm Scripts

```jsonc
{
  "test:e2e": "playwright test --project=test",
  "test:e2e:ui": "playwright test --project=test --ui",
  "test:e2e:capture": "playwright test --project=manual-capture",
  "test:e2e:visual": "playwright test --project=visual-regression",
  "test:e2e:update-snapshots": "playwright test --project=visual-regression --update-snapshots",
  "generate:manual": "npx tsx scripts/generate-manual.ts",
  "docs:generate": "npm run test:e2e:capture && npm run generate:manual"
}
```

---

## 8. Stable Selectors Strategy

Since the EAM app uses `@nuxt/ui` v4 components, selectors need to target:

| Component | Selector Strategy |
|-----------|-------------------|
| Buttons | `button:has-text("Save")`, `[data-testid="btn-save"]` |
| Inputs | `[data-field="field_name"] input` |
| Select dropdowns | `[data-field="field_name"]` |
| Table rows | `table tbody tr`, `[data-testid="entity-table"] tr` |
| Workflow state badge | `[data-testid="workflow-state"]` |
| Sidebar nav items | `nav a[href="/${entity}"]` |
| Toast messages | `.toast-message`, `[role="alert"]` |
| Modal dialogs | `[role="dialog"]` |
| Form error messages | `[data-testid="field-error"]`, `.text-destructive` |

**Action Required:** Add `data-testid` attributes to ~20 key components during Phase 1. These are targeted additions, not a full refactor.

---

## 9. Environment Requirements

- **Local dev:** `http://localhost:3000` (frontend) + `http://localhost:8000` (backend)
- **CHI staging:** `https://chieam.cubeworksinnovation.com` (for capture mode against real data)
- **Credentials:** `admin` / `admin123` (superuser)
- **Browser:** Chromium (primary), Firefox (secondary validation)

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dynamic entity pages have no `data-testid` attributes | Brittle selectors | Phase 1 adds ~20 stable selectors to key components |
| 136 entities = huge YAML maintenance | Test bloat | Tier 3 entities use auto-generated smoke YAML from entity JSON schema |
| Screenshots vary by data state | Flaky visual tests | Use `maxDiffPixelRatio: 0.01` tolerance + consistent test data seeding |
| LLM manual quality inconsistent | Bad docs | Use structured prompts with `manual_hint` fields + human review step |
| CI runner speed | Slow PRs | Test mode runs only Tier 1+2 coded tests; full capture is main-branch only |

---

## 11. Deliverables Summary

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| Phase 1 | Framework core + page objects + auth fixtures | Week 1 |
| Phase 2 | YAML engine + runner | Week 1-2 |
| Phase 3 | 15+ workflow test suites covering all 5 modules | Week 2-3 |
| Phase 4 | Edge case tests + visual regression baselines | Week 3 |
| Phase 5 | `generate-manual.ts` + AI-generated USER_MANUAL.md | Week 4 |
| Phase 6 | GitHub Actions CI/CD pipelines | Week 4 |

**Total:** ~30 test files, ~200+ test cases, ~50 YAML definitions, 1 AI manual generator, 2 CI workflows
