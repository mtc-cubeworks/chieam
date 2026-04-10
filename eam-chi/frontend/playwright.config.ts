import { defineConfig, devices } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000'
const ARTIFACTS_DIR = path.resolve(__dirname, 'test-artifacts')

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  retries: 1,
  workers: 1,
  fullyParallel: false,
  outputDir: path.join(ARTIFACTS_DIR, 'test-results'),

  use: {
    baseURL: BASE_URL,
    headless: true,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    trace: 'on-first-retry',
    video: 'off',
  },

  webServer: {
    command: 'npm run dev',
    url: BASE_URL,
    reuseExistingServer: true,
    timeout: 120_000,
  },

  projects: [
    /* ----------- Auth setup (runs first) ----------- */
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.ts$/,
      use: { ...devices['Desktop Chrome'] },
    },

    /* ----------- PR test mode (fast) ----------- */
    {
      name: 'test',
      dependencies: ['auth-setup'],
      testIgnore: ['**/runners/**', '**/visual/**'],
      use: {
        ...devices['Desktop Chrome'],
        storageState: path.join(__dirname, 'e2e/.auth/admin.json'),
        screenshot: 'only-on-failure',
      },
    },

    /* ----------- YAML-driven runner ----------- */
    {
      name: 'yaml-runner',
      dependencies: ['auth-setup'],
      testMatch: /workflow-runner\.spec\.ts$/,
      use: {
        ...devices['Desktop Chrome'],
        storageState: path.join(__dirname, 'e2e/.auth/admin.json'),
        screenshot: 'on',
      },
    },

    /* ----------- Manual-capture mode (full screenshots) ----------- */
    {
      name: 'manual-capture',
      dependencies: ['auth-setup'],
      use: {
        ...devices['Desktop Chrome'],
        storageState: path.join(__dirname, 'e2e/.auth/admin.json'),
        screenshot: 'on',
        video: 'on',
      },
    },

    /* ----------- Visual regression ----------- */
    {
      name: 'visual-regression',
      dependencies: ['auth-setup'],
      testDir: './e2e/visual',
      use: {
        ...devices['Desktop Chrome'],
        storageState: path.join(__dirname, 'e2e/.auth/admin.json'),
      },
    },
  ],
})
