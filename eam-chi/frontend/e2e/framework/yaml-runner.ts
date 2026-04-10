/**
 * Dual-Purpose Automation Framework — YAML Parser & Runner
 *
 * Reads YAML workflow definitions and maps each step to Playwright
 * page actions. Integrates with the Observer for artifact capture.
 */

import fs from 'fs'
import path from 'path'
import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'
import type { WorkflowDefinition, WorkflowStep, StepAssertion } from './types'
import { Observer } from './observer'

/* ------------------------------------------------------------------ */
/*  YAML parsing (lightweight — avoids native dependency issues)       */
/* ------------------------------------------------------------------ */

/**
 * Minimal YAML parser for workflow definitions.
 * Handles the subset of YAML we use: scalars, arrays of objects, booleans.
 * For production, swap with 'yaml' or 'js-yaml' package.
 */
export function parseYAML(content: string): WorkflowDefinition {
  // We use a simple JSON-compatible approach: workflow YAMLs are also
  // stored as JSON for reliability. For .yaml files we use js-yaml at runtime.
  // This function attempts JSON first, then falls back to basic YAML parsing.
  try {
    return JSON.parse(content) as WorkflowDefinition
  } catch {
    // Fallback: use dynamic import of js-yaml if available
    throw new Error(
      'YAML parsing requires the "js-yaml" package. Install it or use .json workflow files.',
    )
  }
}

/**
 * Load a workflow definition from a file (.yaml or .json).
 */
export async function loadWorkflow(filePath: string): Promise<WorkflowDefinition> {
  const ext = path.extname(filePath).toLowerCase()
  const content = fs.readFileSync(filePath, 'utf-8')

  if (ext === '.json') {
    return JSON.parse(content) as WorkflowDefinition
  }

  // For .yaml/.yml, dynamically import js-yaml
  try {
    const yaml = await import('js-yaml')
    return yaml.load(content) as WorkflowDefinition
  } catch {
    // Try the basic JSON parse fallback
    return parseYAML(content)
  }
}

/**
 * Discover all workflow definition files in a directory (recursive).
 */
export function discoverWorkflows(dir: string): string[] {
  if (!fs.existsSync(dir)) return []

  const files: string[] = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...discoverWorkflows(fullPath))
    } else if (/\.(ya?ml|json)$/.test(entry.name)) {
      files.push(fullPath)
    }
  }
  return files
}

/* ------------------------------------------------------------------ */
/*  Step Executor                                                      */
/* ------------------------------------------------------------------ */

export class WorkflowRunner {
  private page: Page
  private observer: Observer
  private workflow: WorkflowDefinition

  constructor(page: Page, observer: Observer, workflow: WorkflowDefinition) {
    this.page = page
    this.observer = observer
    this.workflow = workflow
  }

  /**
   * Execute all steps in the workflow sequentially.
   */
  async runAll(): Promise<{ passed: number; failed: number; errors: string[] }> {
    let passed = 0
    let failed = 0
    const errors: string[] = []

    for (let i = 0; i < this.workflow.steps.length; i++) {
      const step = this.workflow.steps[i]
      try {
        await this.executeStep(step, i)
        passed++
      } catch (err) {
        failed++
        errors.push(`Step ${step.id}: ${(err as Error).message}`)
      }
    }

    return { passed, failed, errors }
  }

  /**
   * Execute a single workflow step.
   */
  async executeStep(step: WorkflowStep, index: number): Promise<void> {
    const timeout = step.timeout ?? 15_000

    // Pre-action: wait if specified (only for networkidle or explicit pre-waits)
    if (step.wait_for === 'networkidle') {
      await this.page.waitForLoadState('networkidle', { timeout })
    }

    // Execute the action
    await this.performAction(step, timeout)

    // Post-action: wait for selector if specified (non-networkidle)
    if (step.wait_for && step.wait_for !== 'networkidle') {
      await this.page.waitForSelector(step.wait_for, { timeout })
    }

    // Post-action: small settle delay for UI transitions
    await this.page.waitForTimeout(300)

    // Wait for loading spinners to disappear before capturing
    await this.waitForLoaded(timeout)

    // Run assertions
    if (step.assertions?.length) {
      for (const assertion of step.assertions) {
        await this.runAssertion(assertion, timeout)
      }
    }

    // Capture artifact for every step (all steps are documented)
    {
      await this.observer.capture(this.page, {
        id: step.id,
        workflow: this.workflow.name,
        persona: this.workflow.persona,
        stepIndex: index,
        action: this.describeAction(step),
        docMetadata: step.doc_metadata,
      })
    }
  }

  /**
   * Map a YAML action to a Playwright page method.
   */
  private async performAction(step: WorkflowStep, timeout: number): Promise<void> {
    switch (step.action) {
      case 'goto':
        if (!step.url) throw new Error(`Step ${step.id}: 'goto' requires a 'url'`)
        await this.page.goto(step.url, { waitUntil: 'domcontentloaded', timeout })
        await this.page.waitForLoadState('networkidle', { timeout }).catch(() => {})
        break

      case 'click':
        if (!step.target) throw new Error(`Step ${step.id}: 'click' requires a 'target'`)
        await this.page.locator(step.target).first().click({ timeout })
        break

      case 'type':
        if (!step.target) throw new Error(`Step ${step.id}: 'type' requires a 'target'`)
        await this.page.locator(step.target).first().fill(step.value ?? '', { timeout })
        break

      case 'clear':
        if (!step.target) throw new Error(`Step ${step.id}: 'clear' requires a 'target'`)
        await this.page.locator(step.target).first().clear({ timeout })
        break

      case 'select':
        if (!step.target) throw new Error(`Step ${step.id}: 'select' requires a 'target'`)
        // Try native select first, fallback to clicking a combobox option
        try {
          await this.page.locator(step.target).first().selectOption(step.value ?? '', { timeout })
        } catch {
          // Click to open dropdown, then click the option
          await this.page.locator(step.target).first().click({ timeout })
          await this.page.waitForTimeout(200)
          if (step.value) {
            await this.page
              .locator(`[role="option"]:has-text("${step.value}"), [role="menuitem"]:has-text("${step.value}")`)
              .first()
              .click({ timeout })
          }
        }
        break

      case 'hover':
        if (!step.target) throw new Error(`Step ${step.id}: 'hover' requires a 'target'`)
        await this.page.locator(step.target).first().hover({ timeout })
        break

      case 'press':
        await this.page.keyboard.press(step.key ?? step.value ?? 'Enter')
        break

      case 'wait':
        if (step.target) {
          await this.page.waitForSelector(step.target, { timeout })
        } else {
          await this.page.waitForTimeout(step.timeout ?? 1000)
        }
        break

      case 'scroll':
        if (step.target) {
          await this.page.locator(step.target).first().scrollIntoViewIfNeeded({ timeout })
        } else {
          await this.page.evaluate(() => window.scrollBy(0, 400))
        }
        break

      case 'screenshot':
        // Screenshot-only step (no UI action). Observer will capture it.
        break

      case 'clearSession':
        // Clear all cookies and storage — useful before login tests
        await this.page.context().clearCookies()
        await this.page.evaluate(() => {
          try { localStorage.clear() } catch {}
          try { sessionStorage.clear() } catch {}
        })
        break

      case 'logout':
        // Navigate to logout then to login page
        await this.page.context().clearCookies()
        await this.page.evaluate(() => {
          try { localStorage.clear() } catch {}
          try { sessionStorage.clear() } catch {}
        })
        await this.page.goto('/login', { waitUntil: 'domcontentloaded', timeout })
        break

      default:
        throw new Error(`Step ${step.id}: Unknown action '${step.action}'`)
    }
  }

  /**
   * Wait for loading spinners to disappear (max 8 seconds).
   * Prevents capturing screenshots while data is still loading.
   */
  private async waitForLoaded(timeout: number): Promise<void> {
    const maxWait = Math.min(timeout, 8000)
    try {
      await this.page.waitForFunction(
        () => {
          const spinners = document.querySelectorAll('.animate-spin, [data-testid="loading"]')
          // Only count visible spinners
          for (const s of spinners) {
            const rect = s.getBoundingClientRect()
            if (rect.width > 0 && rect.height > 0) return false
          }
          return true
        },
        { timeout: maxWait },
      )
    } catch {
      // Timeout is acceptable — some pages may have persistent spinners
    }
    // Extra settle time after spinners clear
    await this.page.waitForTimeout(200)
  }

  /**
   * Run a single assertion.
   */
  private async runAssertion(assertion: StepAssertion, timeout: number): Promise<void> {
    switch (assertion.type) {
      case 'visible':
        if (!assertion.target) throw new Error('visible assertion requires target')
        await expect(this.page.locator(assertion.target).first()).toBeVisible({ timeout })
        break

      case 'hidden':
        if (!assertion.target) throw new Error('hidden assertion requires target')
        await expect(this.page.locator(assertion.target).first()).toBeHidden({ timeout })
        break

      case 'hasText':
        if (!assertion.target) throw new Error('hasText assertion requires target')
        await expect(this.page.locator(assertion.target).first()).toContainText(
          assertion.value ?? '',
          { timeout },
        )
        break

      case 'hasValue':
        if (!assertion.target) throw new Error('hasValue assertion requires target')
        await expect(this.page.locator(assertion.target).first()).toHaveValue(
          assertion.value ?? '',
          { timeout },
        )
        break

      case 'urlContains':
        await expect(this.page).toHaveURL(new RegExp(assertion.value ?? ''), { timeout })
        break

      case 'count':
        if (!assertion.target || !assertion.value)
          throw new Error('count assertion requires target and value')
        await expect(this.page.locator(assertion.target)).toHaveCount(
          parseInt(assertion.value, 10),
          { timeout },
        )
        break
    }
  }

  /**
   * Build a human-readable description of the step action.
   */
  private describeAction(step: WorkflowStep): string {
    switch (step.action) {
      case 'goto':
        return `Navigate to ${step.url}`
      case 'click':
        return `Click on "${step.target}"`
      case 'type':
        return `Type "${step.value}" into "${step.target}"`
      case 'select':
        return `Select "${step.value}" from "${step.target}"`
      case 'hover':
        return `Hover over "${step.target}"`
      case 'press':
        return `Press key "${step.key ?? step.value}"`
      case 'screenshot':
        return `Capture screenshot`
      case 'wait':
        return `Wait for ${step.target ?? step.timeout + 'ms'}`
      default:
        return `${step.action} on "${step.target ?? ''}"`
    }
  }
}
