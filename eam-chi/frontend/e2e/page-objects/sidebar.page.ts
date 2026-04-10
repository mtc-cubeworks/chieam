/**
 * Page Object — Sidebar Navigation
 */

import type { Page, Locator } from '@playwright/test'
import { S } from '../framework/selectors'

export class SidebarPage {
  readonly page: Page
  readonly root: Locator
  readonly collapseButton: Locator
  readonly userDropdown: Locator

  constructor(page: Page) {
    this.page = page
    this.root = page.locator(S.sidebar.root).first()
    this.collapseButton = page.locator(S.sidebar.collapseButton).first()
    this.userDropdown = page.locator(S.sidebar.userDropdown).first()
  }

  async navigateTo(entity: string) {
    const link = this.page.locator(S.sidebar.navLink(entity)).first()
    await link.click()
    await this.page.waitForLoadState('networkidle')
  }

  async isVisible(): Promise<boolean> {
    try {
      await this.root.waitFor({ state: 'visible', timeout: 5000 })
      return true
    } catch {
      return false
    }
  }

  async logout() {
    await this.userDropdown.click()
    await this.page.waitForTimeout(200)
    await this.page.locator(S.sidebar.logoutButton).first().click()
  }
}
