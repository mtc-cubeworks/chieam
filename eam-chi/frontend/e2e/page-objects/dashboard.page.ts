/**
 * Page Object — Dashboard
 */

import type { Page, Locator } from '@playwright/test'

export class DashboardPage {
  readonly page: Page
  readonly root: Locator
  readonly kpiCards: Locator
  readonly woOpenCount: Locator
  readonly assetActiveCount: Locator

  constructor(page: Page) {
    this.page = page
    this.root = page.locator('[data-testid="dashboard"], main')
    this.kpiCards = page.locator('[data-testid="kpi-card"]')
    this.woOpenCount = page.locator('text=Open Work Orders').locator('..')
    this.assetActiveCount = page.locator('text=Active Assets').locator('..')
  }

  async goto() {
    await this.page.goto('/dashboard')
    await this.page.waitForLoadState('networkidle')
  }

  async isLoaded(): Promise<boolean> {
    try {
      await this.root.waitFor({ state: 'visible', timeout: 10_000 })
      return true
    } catch {
      return false
    }
  }
}
