/**
 * Page Object — Entity Detail / Form (/[entity]/[id])
 */

import type { Page, Locator } from '@playwright/test'
import { S } from '../framework/selectors'

export class EntityDetailPage {
  readonly page: Page
  readonly form: Locator
  readonly saveButton: Locator
  readonly cancelButton: Locator
  readonly editButton: Locator
  readonly backButton: Locator
  readonly tabBar: Locator
  readonly workflowState: Locator
  readonly workflowActions: Locator
  readonly errorAlert: Locator

  constructor(page: Page) {
    this.page = page
    this.form = page.locator(S.entityDetail.form).first()
    this.saveButton = page.locator(S.entityDetail.saveButton).first()
    this.cancelButton = page.locator(S.entityDetail.cancelButton).first()
    this.editButton = page.locator(S.entityDetail.editButton).first()
    this.backButton = page.locator(S.entityDetail.backButton).first()
    this.tabBar = page.locator(S.entityDetail.tabBar).first()
    this.workflowState = page.locator(S.workflow.stateLabel).first()
    this.workflowActions = page.locator(S.workflow.actionDropdown).first()
    this.errorAlert = page.locator(S.entityDetail.errorAlert).first()
  }

  async goto(entity: string, id: string) {
    await this.page.goto(`/${entity}/${id}`)
    await this.page.waitForLoadState('networkidle')
  }

  async gotoNew(entity: string) {
    await this.page.goto(`/${entity}/new`)
    await this.page.waitForLoadState('networkidle')
  }

  async fillField(fieldName: string, value: string) {
    const input = this.page.locator(S.entityDetail.fieldInput(fieldName)).first()
    await input.fill(value)
  }

  async selectField(fieldName: string, value: string) {
    const field = this.page.locator(S.entityDetail.field(fieldName)).first()
    // Try native select
    try {
      await field.locator('select').selectOption(value, { timeout: 3000 })
    } catch {
      // Click combobox to open dropdown, then pick option
      await field.locator('[role="combobox"], input').first().click()
      await this.page.waitForTimeout(200)
      await this.page
        .locator(`[role="option"]:has-text("${value}")`)
        .first()
        .click()
    }
  }

  async save() {
    await this.saveButton.click()
    await this.page.waitForTimeout(500)
  }

  async getFieldError(fieldName: string): Promise<string | null> {
    const error = this.page.locator(S.entityDetail.fieldError(fieldName)).first()
    try {
      await error.waitFor({ state: 'visible', timeout: 3000 })
      return error.textContent()
    } catch {
      return null
    }
  }

  async triggerWorkflowAction(actionName: string) {
    await this.workflowActions.click()
    await this.page.waitForTimeout(200)
    await this.page
      .locator(S.workflow.actionButton(actionName))
      .first()
      .click()
    await this.page.waitForTimeout(500)
  }

  async getWorkflowState(): Promise<string> {
    return (await this.workflowState.textContent()) ?? ''
  }

  async switchTab(name: string) {
    await this.page.locator(S.entityDetail.tab(name)).first().click()
    await this.page.waitForTimeout(300)
  }

  async waitForToast(text?: string) {
    const toast = this.page.locator(S.toast.message).first()
    await toast.waitFor({ state: 'visible', timeout: 5000 })
    if (text) {
      await this.page.locator(`${S.toast.message}:has-text("${text}")`).first().waitFor({
        state: 'visible',
        timeout: 5000,
      })
    }
  }
}
