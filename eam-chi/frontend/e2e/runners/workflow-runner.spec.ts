/**
 * Dual-Purpose Automation Framework — YAML-Driven Test Runner
 *
 * Auto-discovers all workflow definitions in e2e/definitions/
 * and creates a Playwright test for each one.
 */

import path from 'path'
import { fileURLToPath } from 'url'
import { test, expect } from '../fixtures/eam-fixtures'
import { discoverWorkflows, loadWorkflow, WorkflowRunner } from '../framework/yaml-runner'
import { ArtifactIndexBuilder } from '../framework/artifact-index'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const DEFINITIONS_DIR = path.resolve(__dirname, '..', 'definitions')
const ARTIFACTS_DIR = path.resolve(__dirname, '..', '..', 'test-artifacts')

// Discover all workflow definition files
const workflowFiles = discoverWorkflows(DEFINITIONS_DIR)

if (workflowFiles.length === 0) {
  test('no workflow definitions found', () => {
    console.warn(`No workflow definitions found in ${DEFINITIONS_DIR}`)
  })
} else {
  for (const filePath of workflowFiles) {
    const relativePath = path.relative(DEFINITIONS_DIR, filePath)
    const testName = relativePath.replace(/\.(json|ya?ml)$/, '').replace(/\//g, ' > ')

    test(`workflow: ${testName}`, async ({ page, observer }) => {
      // Load the workflow definition
      const workflow = await loadWorkflow(filePath)

      // Create the runner
      const runner = new WorkflowRunner(page, observer, workflow)

      // Execute all steps
      const result = await runner.runAll()

      // Report results
      if (result.errors.length > 0) {
        console.error(`Workflow "${workflow.name}" had ${result.failed} failures:`)
        for (const err of result.errors) {
          console.error(`  - ${err}`)
        }
      }

      // Assert all steps passed
      expect(result.failed, `${result.failed} step(s) failed:\n${result.errors.join('\n')}`).toBe(0)
    })
  }
}

// After all tests: flush the artifact index
test.afterAll(async () => {
  const builder = new ArtifactIndexBuilder(ARTIFACTS_DIR)
  builder.flush('', 'yaml-runner')
})
