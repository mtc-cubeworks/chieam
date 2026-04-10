/**
 * Page Object — Entity List (dynamic /[entity] page)
 */

import type { Page, Locator } from '@playwright/test'
import { S } from '../framework/selectors'

export class EntityListPage {
  readonly page: Page
  readonly newButton: Locator
  readonly table: Locator
  readonly tableRows: Locator
  readonly searchInput: Locator
  readonly pagination: Locator
  readonly emptyState: Locator

  constructor(page: Page) {
    this.page = page
    this.newButton = page.locator(S.entityList.newButton).first()
    this.table = page.locator(S.entityList.table).first()
    this.tableRows = page.locator(S.entityList.tableRow)
    this.searchInput = page.locator(S.entityList.searchInput).first()
    this.pagination = page.locator(S.entityList.pagination).first()
    this.emptyState = page.locator(S.entityList.emptyState).first()
  }

  async goto(entity: string) {
    await this.page.goto(`/${entity}`)
    await this.page.waitForLoadState('networkidle')
  }

  async clickNew() {
    await this.newButton.click()
    await this.page.waitForLoadState('networkidle')
  }

  async search(term: string) {
    await this.searchInput.fill(term)
    await this.page.waitForTimeout(500)
  }

  async getRowCount(): Promise<number> {
    return this.tableRows.count()
  }

  async clickFirstRow() {
    await this.tableRows.first().click()
    await this.page.waitForLoadState('networkidle')
  }

  async hasData(): Promise<boolean> {
    const rows = await this.getRowCount()
    return rows > 0
  }
}
