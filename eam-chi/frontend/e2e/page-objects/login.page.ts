/**
 * Page Object — Login Page
 */

import type { Page, Locator } from '@playwright/test'
import { S } from '../framework/selectors'

export class LoginPage {
  readonly page: Page
  readonly usernameInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator
  readonly errorMessage: Locator
  readonly brandingLogo: Locator

  constructor(page: Page) {
    this.page = page
    this.usernameInput = page.locator(S.login.usernameInput).first()
    this.passwordInput = page.locator(S.login.passwordInput).first()
    this.submitButton = page.locator(S.login.submitButton).first()
    this.errorMessage = page.locator(S.login.errorMessage).first()
    this.brandingLogo = page.locator(S.login.brandingLogo).first()
  }

  async goto() {
    await this.page.goto('/login')
    await this.page.waitForLoadState('networkidle')
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }

  async loginAsAdmin() {
    await this.login('admin', 'admin123')
    await this.page.waitForURL((url) => !url.pathname.includes('/login'), {
      timeout: 15_000,
    })
  }
}
