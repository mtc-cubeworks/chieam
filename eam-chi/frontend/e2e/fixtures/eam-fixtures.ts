/**
 * Dual-Purpose Automation Framework — Custom Fixtures
 *
 * Extends Playwright's base test with:
 * - authenticatedPage: a page pre-loaded with admin auth state
 * - observer: an Observer instance for artifact capture
 */

import { test as base } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'
import { Observer } from '../framework/observer'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ARTIFACTS_DIR = path.resolve(__dirname, '..', '..', 'test-artifacts')

type EAMFixtures = {
  observer: Observer
}

export const test = base.extend<EAMFixtures>({
  observer: async ({}, use, testInfo) => {
    const obs = new Observer({
      outputDir: ARTIFACTS_DIR,
      project: testInfo.project.name,
      baseURL: testInfo.project.use.baseURL as string ?? '',
    })
    await use(obs)
    obs.flush()
  },
})

export { expect } from '@playwright/test'
