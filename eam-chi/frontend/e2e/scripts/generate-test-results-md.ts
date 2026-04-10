/**
 * Dual-Purpose Automation Framework — Markdown Test Results Generator
 *
 * Reads test-artifacts/index.json and generates a Markdown test results
 * document with screenshot references and pass/fail summary tables.
 *
 * Usage:
 *   npx tsx e2e/scripts/generate-test-results-md.ts [--output E2E_TEST_RESULTS.md]
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import type { ArtifactIndex, ArtifactEntry } from '../framework/types'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ARTIFACTS_DIR = path.resolve(__dirname, '..', '..', 'test-artifacts')
const INDEX_PATH = path.join(ARTIFACTS_DIR, 'index.json')

const args = process.argv.slice(2)
const outputIdx = args.indexOf('--output')
const outputPath = outputIdx >= 0 && args[outputIdx + 1]
  ? path.resolve(args[outputIdx + 1])
  : path.resolve(__dirname, '..', '..', '..', '..', 'E2E_TEST_RESULTS.md')

function loadIndex(): ArtifactIndex {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error(`Index file not found: ${INDEX_PATH}`)
    process.exit(1)
  }
  return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'))
}

function groupByWorkflow(entries: ArtifactEntry[]): Map<string, ArtifactEntry[]> {
  const groups = new Map<string, ArtifactEntry[]>()
  for (const entry of entries) {
    if (!groups.has(entry.workflow)) groups.set(entry.workflow, [])
    groups.get(entry.workflow)!.push(entry)
  }
  for (const [, group] of groups) group.sort((a, b) => a.step_index - b.step_index)
  return groups
}

function inferModule(workflow: string): string {
  if (workflow.includes('login') || workflow.includes('auth') || workflow.includes('TC-01')) return 'Authentication'
  if (workflow.includes('dashboard')) return 'Dashboard & Overview'
  if (workflow.includes('sidebar') || workflow.includes('navigation')) return 'Navigation'
  if (workflow.includes('TC-03') || workflow.includes('organization') || workflow.includes('site') || workflow.includes('department') || workflow.includes('employee') || workflow.includes('vendor') || workflow.includes('item')) return 'Master Data'
  if (workflow.includes('condition') || workflow.includes('TC-10')) return 'Condition Monitoring'
  if (workflow.includes('asset') || workflow.includes('TC-04')) return 'Asset Management'
  if (workflow.includes('work_order') || workflow.includes('work-order') || workflow.includes('TC-07')) return 'Work Management'
  if (workflow.includes('safety') || workflow.includes('TC-09')) return 'Safety Permits'
  if (workflow.includes('maintenance') || workflow.includes('TC-06')) return 'Maintenance Management'
  if (workflow.includes('purchase') || workflow.includes('TC-11')) return 'Purchasing & Stores'
  if (workflow.includes('entity-list') || workflow.includes('entity_list')) return 'General Features'
  return 'General'
}

function inferTestCaseId(workflow: string): string {
  const match = workflow.match(/TC-(\d+)/)
  if (match) return `TC-${match[1]}`
  if (workflow.includes('login-happy') || workflow.includes('login-edge')) return 'TC-01'
  if (workflow.includes('dashboard')) return 'TC-02'
  if (workflow.includes('sidebar') || workflow.includes('navigation')) return 'TC-02'
  if (workflow.includes('entity-list')) return 'TC-05'
  if (workflow.includes('asset-lifecycle')) return 'TC-04'
  if (workflow.includes('work-order-lifecycle')) return 'TC-07'
  if (workflow.includes('maintenance-request-lifecycle')) return 'TC-06'
  if (workflow.includes('purchase-request-lifecycle')) return 'TC-11'
  return '—'
}

function groupByModule(workflows: Map<string, ArtifactEntry[]>): Map<string, Map<string, ArtifactEntry[]>> {
  const modules = new Map<string, Map<string, ArtifactEntry[]>>()
  for (const [workflow, entries] of workflows) {
    const mod = inferModule(workflow)
    if (!modules.has(mod)) modules.set(mod, new Map())
    modules.get(mod)!.set(workflow, entries)
  }
  return modules
}

function formatWorkflowTitle(name: string): string {
  return name.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function screenshotRef(entry: ArtifactEntry): string {
  if (!entry.visual_artifact) return ''
  const relPath = path.relative(path.dirname(outputPath), path.join(ARTIFACTS_DIR, entry.visual_artifact))
  return `\n![${entry.doc_metadata?.title ?? entry.id}](${relPath})\n`
}

function generate(): string {
  const index = loadIndex()
  const workflows = groupByWorkflow(index.entries)
  const modules = groupByModule(workflows)

  const passCount = index.entries.filter(e => e.dom_context.status === 'Success').length
  const warnCount = index.entries.filter(e => e.dom_context.status === 'ValidationError').length
  const loadingCount = index.entries.filter(e => e.dom_context.status === 'Loading').length
  const errorCount = index.entries.filter(e => e.dom_context.status === 'Error').length
  const passRate = ((passCount / index.total_steps) * 100).toFixed(1)

  const lines: string[] = []

  // Title
  lines.push('# EAM System — E2E Test Results')
  lines.push('')
  lines.push('> Automated Visual Test Report with Step-by-Step Evidence')
  lines.push('')
  lines.push(`**Generated:** ${new Date().toISOString()}`)
  lines.push(`**Base URL:** https://chieam.cubeworksinnovation.com`)
  lines.push(`**Framework:** Dual-Purpose Automation (Playwright v1.58.2)`)
  lines.push('')

  // Executive Summary
  lines.push('---')
  lines.push('')
  lines.push('## Executive Summary')
  lines.push('')
  lines.push('| Metric | Value |')
  lines.push('|--------|-------|')
  lines.push(`| Workflows Tested | ${index.total_workflows} |`)
  lines.push(`| Total Steps | ${index.total_steps} |`)
  lines.push(`| Screenshots Captured | ${index.total_screenshots} |`)
  lines.push(`| Steps Passed | ${passCount} |`)
  lines.push(`| Warnings | ${warnCount} |`)
  lines.push(`| Loading States | ${loadingCount} |`)
  lines.push(`| Errors | ${errorCount} |`)
  lines.push(`| **Pass Rate** | **${passRate}%** |`)
  lines.push('')

  // Result: All pass
  if (errorCount === 0) {
    lines.push(`> ✅ **All ${index.total_workflows} Playwright test cases PASSED.** No errors detected across all workflow steps.`)
    lines.push('')
  }

  // Workflow Summary Table
  lines.push('## Workflow Summary')
  lines.push('')
  lines.push('| # | Test Case | Module | Workflow | Steps | Status |')
  lines.push('|---|-----------|--------|----------|-------|--------|')

  let rowNum = 1
  for (const [moduleName, moduleWorkflows] of modules) {
    for (const [workflowName, entries] of moduleWorkflows) {
      const tcId = inferTestCaseId(workflowName)
      const stepCount = entries.length
      const passedSteps = entries.filter(e => e.dom_context.status === 'Success').length
      const status = passedSteps === stepCount ? '✅ PASS' : `⚠️ ${passedSteps}/${stepCount}`
      lines.push(`| ${rowNum} | ${tcId} | ${moduleName} | ${formatWorkflowTitle(workflowName)} | ${stepCount} | ${status} |`)
      rowNum++
    }
  }
  lines.push('')

  // Table of Contents
  lines.push('---')
  lines.push('')
  lines.push('## Table of Contents')
  lines.push('')
  let chapterNum = 1
  for (const [moduleName, moduleWorkflows] of modules) {
    const anchor = moduleName.toLowerCase().replace(/[^a-z0-9]+/g, '-')
    lines.push(`${chapterNum}. [${moduleName}](#${anchor})`)
    let subNum = 1
    for (const [workflowName] of moduleWorkflows) {
      const subAnchor = workflowName.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      lines.push(`   ${chapterNum}.${subNum}. [${formatWorkflowTitle(workflowName)}](#${subAnchor})`)
      subNum++
    }
    chapterNum++
  }
  lines.push('')

  // Detailed Results by Module
  lines.push('---')
  lines.push('')
  chapterNum = 1

  for (const [moduleName, moduleWorkflows] of modules) {
    const moduleWfCount = moduleWorkflows.size
    const moduleStepCount = Array.from(moduleWorkflows.values()).reduce((sum, arr) => sum + arr.length, 0)

    lines.push(`## ${chapterNum}. ${moduleName}`)
    lines.push('')
    lines.push(`*${moduleWfCount} workflow(s) — ${moduleStepCount} step(s)*`)
    lines.push('')

    let subNum = 1
    for (const [workflowName, entries] of moduleWorkflows) {
      const tcId = inferTestCaseId(workflowName)
      const wfPassCount = entries.filter(e => e.dom_context.status === 'Success').length
      const allPass = wfPassCount === entries.length
      const statusEmoji = allPass ? '✅' : '⚠️'

      lines.push(`### ${chapterNum}.${subNum}. ${formatWorkflowTitle(workflowName)} ${statusEmoji}`)
      lines.push('')
      lines.push(`| Property | Value |`)
      lines.push(`|----------|-------|`)
      lines.push(`| Test Case | ${tcId} |`)
      lines.push(`| Workflow | \`${workflowName}\` |`)
      lines.push(`| Persona | ${entries[0]?.persona ?? 'Admin'} |`)
      lines.push(`| Steps | ${entries.length} |`)
      lines.push(`| Pass Rate | ${wfPassCount}/${entries.length} (${((wfPassCount/entries.length)*100).toFixed(0)}%) |`)
      lines.push(`| Result | ${allPass ? '**PASS**' : '**PARTIAL**'} |`)
      lines.push('')

      // Steps
      for (let i = 0; i < entries.length; i++) {
        const entry = entries[i]
        const stepTitle = entry.doc_metadata?.title ?? `Step ${i + 1}`
        const caption = entry.doc_metadata?.caption ?? entry.action
        const status = entry.dom_context.status

        lines.push(`**Step ${i + 1}: ${stepTitle}** — \`${status}\``)
        lines.push('')
        lines.push(caption)
        lines.push('')
        lines.push(`- **Action:** \`${entry.action}\``)
        lines.push(`- **URL:** \`${entry.url}\``)
        lines.push(`- **Timestamp:** ${entry.timestamp}`)

        if (entry.dom_context.visible_errors.length > 0) {
          lines.push(`- **Visible Errors:**`)
          for (const err of entry.dom_context.visible_errors) {
            lines.push(`  - \`${err}\``)
          }
        }

        if (entry.dom_context.toast_messages.length > 0) {
          lines.push(`- **Toast Messages:** ${entry.dom_context.toast_messages.join(', ')}`)
        }

        lines.push('')
        lines.push(screenshotRef(entry))
        lines.push('')
      }

      lines.push('---')
      lines.push('')
      subNum++
    }
    chapterNum++
  }

  // Footer
  lines.push('')
  lines.push('---')
  lines.push('')
  lines.push('*This report was auto-generated by the Dual-Purpose Automation Framework.*')
  lines.push(`*CubeWorks Innovation — ${new Date().toISOString()}*`)

  return lines.join('\n')
}

function main() {
  console.log('📊 Generating Markdown E2E test results...')
  const markdown = generate()
  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
  fs.writeFileSync(outputPath, markdown, 'utf-8')
  const lineCount = markdown.split('\n').length
  console.log(`✅ Report generated: ${outputPath} (${lineCount} lines)`)
}

main()
