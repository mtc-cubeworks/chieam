/**
 * Dual-Purpose Automation Framework — Manual Generator
 *
 * Reads the Visual Artifact Index (test-artifacts/index.json),
 * groups entries by workflow, and generates a structured Markdown
 * user manual with embedded screenshots and troubleshooting tips.
 *
 * Usage:
 *   npx tsx e2e/scripts/generate-manual.ts [--output USER_MANUAL.md]
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import type { ArtifactIndex, ArtifactEntry } from '../framework/types'

/* ------------------------------------------------------------------ */
/*  Config                                                             */
/* ------------------------------------------------------------------ */

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ARTIFACTS_DIR = path.resolve(__dirname, '..', '..', 'test-artifacts')
const INDEX_PATH = path.join(ARTIFACTS_DIR, 'index.json')
const DEFAULT_OUTPUT = path.resolve(__dirname, '..', '..', 'USER_MANUAL.md')

// Parse CLI args
const args = process.argv.slice(2)
const outputIdx = args.indexOf('--output')
const outputPath = outputIdx >= 0 && args[outputIdx + 1]
  ? path.resolve(args[outputIdx + 1])
  : DEFAULT_OUTPUT

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function loadIndex(): ArtifactIndex {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error(`Index file not found: ${INDEX_PATH}`)
    console.error('Run the e2e tests first: pnpm test:e2e:capture')
    process.exit(1)
  }
  return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'))
}

function groupByWorkflow(entries: ArtifactEntry[]): Map<string, ArtifactEntry[]> {
  const groups = new Map<string, ArtifactEntry[]>()
  for (const entry of entries) {
    const key = entry.workflow
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(entry)
  }
  // Sort entries within each group by step_index
  for (const [, group] of groups) {
    group.sort((a, b) => a.step_index - b.step_index)
  }
  return groups
}

function inferModule(workflow: string): string {
  if (workflow.includes('login') || workflow.includes('auth') || workflow.includes('TC-01')) return 'Authentication'
  if (workflow.includes('dashboard')) return 'Dashboard'
  if (workflow.includes('sidebar') || workflow.includes('navigation')) return 'Navigation'
  if (workflow.includes('TC-03') || workflow.includes('organization') || workflow.includes('site') || workflow.includes('department') || workflow.includes('employee') || workflow.includes('vendor') || workflow.includes('item')) return 'Master Data'
  if (workflow.includes('condition') || workflow.includes('TC-10')) return 'Condition Monitoring'
  if (workflow.includes('asset') || workflow.includes('TC-04')) return 'Asset Management'
  if (workflow.includes('work_order') || workflow.includes('work-order') || workflow.includes('TC-07')) return 'Work Management'
  if (workflow.includes('safety') || workflow.includes('TC-09')) return 'Safety Permits'
  if (workflow.includes('maintenance') || workflow.includes('TC-06')) return 'Maintenance'
  if (workflow.includes('purchase') || workflow.includes('TC-11')) return 'Purchasing & Stores'
  if (workflow.includes('entity-list') || workflow.includes('entity_list')) return 'General Features'
  return 'General'
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
  return name
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function screenshotMarkdown(entry: ArtifactEntry, basePath: string): string {
  if (!entry.visual_artifact) return ''
  const relPath = path.relative(path.dirname(basePath), path.join(ARTIFACTS_DIR, entry.visual_artifact))
  return `\n![${entry.doc_metadata?.title ?? entry.id}](${relPath})\n`
}

/* ------------------------------------------------------------------ */
/*  Generator                                                          */
/* ------------------------------------------------------------------ */

function generate(): string {
  const index = loadIndex()
  const workflows = groupByWorkflow(index.entries)
  const modules = groupByModule(workflows)
  const edgeCases: ArtifactEntry[] = []

  const lines: string[] = []

  // Title page
  lines.push('# EAM System — User Manual')
  lines.push('')
  lines.push(`> Auto-generated from ${index.total_screenshots} screenshots across ${index.total_workflows} workflows.`)
  lines.push(`> Generated at: ${index.generated_at}`)
  lines.push('')

  // Table of contents
  lines.push('## Table of Contents')
  lines.push('')
  let chapterNum = 1
  const tocEntries: { module: string; workflows: string[] }[] = []
  for (const [moduleName, moduleWorkflows] of modules) {
    const wfNames = Array.from(moduleWorkflows.keys())
    tocEntries.push({ module: moduleName, workflows: wfNames })
    lines.push(`${chapterNum}. [${moduleName}](#${moduleName.toLowerCase().replace(/\s+/g, '-')})`)
    let subNum = 1
    for (const wfName of wfNames) {
      lines.push(`   ${chapterNum}.${subNum}. [${formatWorkflowTitle(wfName)}](#${wfName.toLowerCase().replace(/\s+/g, '-')})`)
      subNum++
    }
    chapterNum++
  }
  lines.push(`${chapterNum}. [Troubleshooting](#troubleshooting)`)
  lines.push('')
  lines.push('---')
  lines.push('')

  // Chapters
  chapterNum = 1
  for (const [moduleName, moduleWorkflows] of modules) {
    lines.push(`## ${chapterNum}. ${moduleName}`)
    lines.push('')

    let subNum = 1
    for (const [workflowName, entries] of moduleWorkflows) {
      lines.push(`### ${chapterNum}.${subNum}. ${formatWorkflowTitle(workflowName)}`)
      lines.push('')

      // Workflow description from first entry context
      const firstWithMeta = entries.find((e) => e.doc_metadata?.caption)
      if (firstWithMeta?.doc_metadata?.caption) {
        lines.push(firstWithMeta.doc_metadata.caption)
        lines.push('')
      }

      // Steps
      let stepNum = 1
      for (const entry of entries) {
        if (!entry.doc_metadata) continue

        // Collect edge cases for the troubleshooting section
        if (entry.doc_metadata.is_edge_case) {
          edgeCases.push(entry)
        }

        lines.push(`**Step ${stepNum}: ${entry.doc_metadata.title}**`)
        lines.push('')
        lines.push(entry.doc_metadata.caption)
        lines.push('')

        // Screenshot
        lines.push(screenshotMarkdown(entry, outputPath))

        // DOM context notes
        if (entry.dom_context.visible_errors.length > 0) {
          lines.push('> **Note:** The following validation messages were visible:')
          for (const err of entry.dom_context.visible_errors) {
            lines.push(`> - ${err}`)
          }
          lines.push('')
        }

        if (entry.dom_context.toast_messages.length > 0) {
          lines.push(`> **System message:** ${entry.dom_context.toast_messages.join(', ')}`)
          lines.push('')
        }

        stepNum++
      }

      lines.push('---')
      lines.push('')
      subNum++
    }
    chapterNum++
  }

  // Troubleshooting appendix
  lines.push(`## ${chapterNum}. Troubleshooting`)
  lines.push('')
  lines.push('This section covers common issues observed during testing.')
  lines.push('')

  if (edgeCases.length === 0) {
    lines.push('No edge cases were captured during this test run.')
  } else {
    for (const entry of edgeCases) {
      if (!entry.doc_metadata) continue
      lines.push(`### ${entry.doc_metadata.title}`)
      lines.push('')
      lines.push(entry.doc_metadata.caption)
      lines.push('')
      lines.push(screenshotMarkdown(entry, outputPath))

      if (entry.dom_context.visible_errors.length > 0) {
        lines.push('**Error messages displayed:**')
        for (const err of entry.dom_context.visible_errors) {
          lines.push(`- \`${err}\``)
        }
        lines.push('')
      }

      if (entry.doc_metadata.manual_hint) {
        lines.push(`> *${entry.doc_metadata.manual_hint}*`)
        lines.push('')
      }
    }
  }

  lines.push('')
  lines.push('---')
  lines.push(`*This manual was auto-generated by the Dual-Purpose Automation Framework.*`)

  return lines.join('\n')
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

function main() {
  console.log('📖 Generating user manual from test artifacts...')
  console.log(`   Index: ${INDEX_PATH}`)
  console.log(`   Output: ${outputPath}`)

  const markdown = generate()
  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
  fs.writeFileSync(outputPath, markdown, 'utf-8')

  console.log(`✅ Manual generated: ${outputPath}`)
  console.log(`   ${markdown.split('\n').length} lines`)
}

main()
