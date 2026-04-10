/**
 * Dual-Purpose Automation Framework — Auth Setup
 *
 * Runs once before all tests to create an authenticated browser
 * storage state. Other projects reuse this via storageState.
 */

import { test as setup, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'
import { S } from './framework/selectors'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const AUTH_FILE = path.join(__dirname, '.auth/admin.json')

setup('authenticate as admin', async ({ page }) => {
  // Ensure auth directory exists
  fs.mkdirSync(path.dirname(AUTH_FILE), { recursive: true })

  await page.goto('/login')
  await page.waitForLoadState('networkidle')

  // Fill credentials
  await page.locator(S.login.usernameInput).first().fill('admin')
  await page.locator(S.login.passwordInput).first().fill('admin123')
  await page.locator(S.login.submitButton).first().click()

  // Wait for redirect away from login
  await page.waitForURL((url) => !url.pathname.includes('/login'), {
    timeout: 15_000,
  })
  expect(page.url()).not.toContain('/login')

  // Wait for app to fully load (sidebar, metadata boot)
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(1000)

  // Save storage state (cookies + localStorage)
  await page.context().storageState({ path: AUTH_FILE })
})
