/**
 * Dual-Purpose Automation Framework — E2E Test Results Report Generator
 *
 * Reads the Visual Artifact Index (test-artifacts/index.json),
 * and generates a comprehensive HTML test report with embedded
 * screenshots as visual evidence for each test step.
 *
 * Usage:
 *   npx tsx e2e/scripts/generate-test-report.ts [--output E2E_TEST_RESULTS.html]
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
  : path.resolve(__dirname, '..', '..', '..', '..', 'E2E_TEST_RESULTS.html')

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function loadIndex(): ArtifactIndex {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error(`Index file not found: ${INDEX_PATH}`)
    process.exit(1)
  }
  return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'))
}

function imageToBase64(imgPath: string): string {
  const fullPath = path.join(ARTIFACTS_DIR, imgPath)
  if (!fs.existsSync(fullPath)) return ''
  const data = fs.readFileSync(fullPath)
  return `data:image/png;base64,${data.toString('base64')}`
}

function groupByWorkflow(entries: ArtifactEntry[]): Map<string, ArtifactEntry[]> {
  const groups = new Map<string, ArtifactEntry[]>()
  for (const entry of entries) {
    const key = entry.workflow
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(entry)
  }
  for (const [, group] of groups) {
    group.sort((a, b) => a.step_index - b.step_index)
  }
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

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function getStatusBadge(entry: ArtifactEntry): string {
  const s = entry.dom_context.status
  if (s === 'Success') return '<span class="badge pass">PASS</span>'
  if (s === 'ValidationError') return '<span class="badge warn">WARN</span>'
  if (s === 'Error') return '<span class="badge fail">FAIL</span>'
  if (s === 'Loading') return '<span class="badge info">LOADING</span>'
  return '<span class="badge info">INFO</span>'
}

/* ------------------------------------------------------------------ */
/*  HTML Generator                                                     */
/* ------------------------------------------------------------------ */

function generateHTML(index: ArtifactIndex): string {
  const workflows = groupByWorkflow(index.entries)
  const modules = groupByModule(workflows)

  const totalWorkflows = index.total_workflows
  const totalSteps = index.total_steps
  const totalScreenshots = index.total_screenshots
  const passCount = index.entries.filter(e => e.dom_context.status === 'Success').length
  const warnCount = index.entries.filter(e => e.dom_context.status === 'ValidationError').length
  const errorCount = index.entries.filter(e => e.dom_context.status === 'Error').length
  const passRate = ((passCount / totalSteps) * 100).toFixed(1)

  // Build TOC and content
  let tocHtml = ''
  let contentHtml = ''
  let moduleIdx = 0

  for (const [moduleName, moduleWorkflows] of modules) {
    const moduleId = moduleName.toLowerCase().replace(/[^a-z0-9]+/g, '-')
    const moduleWfCount = moduleWorkflows.size
    const moduleStepCount = Array.from(moduleWorkflows.values()).reduce((sum, arr) => sum + arr.length, 0)

    tocHtml += `<li><a href="#${moduleId}">${escapeHtml(moduleName)}</a> <span class="toc-count">${moduleWfCount} tests, ${moduleStepCount} steps</span><ul>`

    contentHtml += `<section class="module" id="${moduleId}">
      <h2>${escapeHtml(moduleName)}</h2>
      <p class="module-summary">${moduleWfCount} workflow test(s) &mdash; ${moduleStepCount} step(s) captured</p>`

    for (const [workflowName, entries] of moduleWorkflows) {
      const wfId = workflowName.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      const tcId = inferTestCaseId(workflowName)
      const wfTitle = formatWorkflowTitle(workflowName)
      const wfPassCount = entries.filter(e => e.dom_context.status === 'Success').length
      const wfTotalSteps = entries.length
      const allPass = wfPassCount === wfTotalSteps

      tocHtml += `<li><a href="#${wfId}">${escapeHtml(wfTitle)}</a></li>`

      contentHtml += `
        <div class="workflow" id="${wfId}">
          <h3>
            ${allPass ? '<span class="badge pass">PASS</span>' : '<span class="badge warn">PARTIAL</span>'}
            ${escapeHtml(wfTitle)}
            <span class="tc-badge">${tcId}</span>
          </h3>
          <table class="meta-table">
            <tr><th>Workflow</th><td>${escapeHtml(workflowName)}</td></tr>
            <tr><th>Persona</th><td>${escapeHtml(entries[0]?.persona ?? 'Admin')}</td></tr>
            <tr><th>Steps</th><td>${wfTotalSteps}</td></tr>
            <tr><th>Pass Rate</th><td>${wfPassCount}/${wfTotalSteps} (${((wfPassCount/wfTotalSteps)*100).toFixed(0)}%)</td></tr>
            <tr><th>Start URL</th><td><code>${escapeHtml(entries[0]?.url ?? '')}</code></td></tr>
          </table>

          <div class="steps">`

      for (let i = 0; i < entries.length; i++) {
        const entry = entries[i]
        const imgData = imageToBase64(entry.visual_artifact)
        const stepTitle = entry.doc_metadata?.title ?? `Step ${i + 1}`
        const caption = entry.doc_metadata?.caption ?? entry.action

        contentHtml += `
            <div class="step">
              <div class="step-header">
                <span class="step-num">${i + 1}</span>
                ${getStatusBadge(entry)}
                <strong>${escapeHtml(stepTitle)}</strong>
              </div>
              <div class="step-body">
                <div class="step-info">
                  <p class="step-caption">${escapeHtml(caption)}</p>
                  <table class="detail-table">
                    <tr><th>Action</th><td><code>${escapeHtml(entry.action)}</code></td></tr>
                    <tr><th>URL</th><td><code>${escapeHtml(entry.url)}</code></td></tr>
                    <tr><th>Status</th><td>${escapeHtml(entry.dom_context.status)}</td></tr>
                    <tr><th>Timestamp</th><td>${escapeHtml(entry.timestamp)}</td></tr>
                    ${entry.dom_context.visible_errors.length > 0 ? `<tr><th>Errors</th><td class="errors">${entry.dom_context.visible_errors.map(e => escapeHtml(e)).join('<br>')}</td></tr>` : ''}
                    ${entry.dom_context.toast_messages.length > 0 ? `<tr><th>Toasts</th><td>${entry.dom_context.toast_messages.map(t => escapeHtml(t)).join('<br>')}</td></tr>` : ''}
                  </table>
                </div>
                ${imgData ? `<div class="screenshot-container">
                  <a href="${imgData}" target="_blank" title="Click to view full size">
                    <img src="${imgData}" alt="${escapeHtml(stepTitle)}" loading="lazy" />
                  </a>
                </div>` : '<div class="screenshot-container no-img">No screenshot captured</div>'}
              </div>
            </div>`
      }

      contentHtml += `
          </div>
        </div>`
    }

    contentHtml += `</section>`
    tocHtml += `</ul></li>`
    moduleIdx++
  }

  const generatedAt = new Date().toISOString()

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EAM E2E Test Results — Visual Report</title>
  <style>
    :root {
      --bg: #f5f7fa; --card: #fff; --border: #e2e8f0;
      --text: #1a202c; --muted: #718096;
      --pass: #38a169; --pass-bg: #f0fff4;
      --fail: #e53e3e; --fail-bg: #fff5f5;
      --warn: #d69e2e; --warn-bg: #fffff0;
      --info: #3182ce; --info-bg: #ebf8ff;
      --accent: #2b6cb0; --header-bg: #1a365d;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }

    /* Header */
    .report-header { background: var(--header-bg); color: white; padding: 2rem 3rem; }
    .report-header h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; }
    .report-header .subtitle { opacity: 0.85; font-size: 0.95rem; }
    .report-header .meta { margin-top: 1rem; display: flex; gap: 2rem; flex-wrap: wrap; font-size: 0.85rem; opacity: 0.9; }

    /* Summary Cards */
    .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; padding: 1.5rem 3rem; margin-top: -1rem; }
    .summary-card { background: var(--card); border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
    .summary-card .num { font-size: 2rem; font-weight: 800; }
    .summary-card .label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .summary-card.pass .num { color: var(--pass); }
    .summary-card.warn .num { color: var(--warn); }
    .summary-card.fail .num { color: var(--fail); }
    .summary-card.info .num { color: var(--accent); }

    /* Layout */
    .container { display: flex; max-width: 1600px; margin: 0 auto; }
    .toc-sidebar { width: 280px; min-width: 280px; padding: 1.5rem; position: sticky; top: 0; height: 100vh; overflow-y: auto; border-right: 1px solid var(--border); background: var(--card); font-size: 0.85rem; }
    .toc-sidebar h3 { margin-bottom: 1rem; font-size: 0.95rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .toc-sidebar ul { list-style: none; }
    .toc-sidebar > ul > li { margin-bottom: 0.75rem; }
    .toc-sidebar > ul > li > a { font-weight: 600; color: var(--accent); text-decoration: none; }
    .toc-sidebar > ul > li > a:hover { text-decoration: underline; }
    .toc-sidebar ul ul { padding-left: 1rem; margin-top: 0.25rem; }
    .toc-sidebar ul ul li { margin-bottom: 0.2rem; }
    .toc-sidebar ul ul a { color: var(--text); text-decoration: none; font-weight: 400; }
    .toc-sidebar ul ul a:hover { color: var(--accent); }
    .toc-count { font-size: 0.75rem; color: var(--muted); }
    .main-content { flex: 1; padding: 2rem 3rem; min-width: 0; }

    /* Module sections */
    .module { margin-bottom: 3rem; }
    .module h2 { font-size: 1.5rem; color: var(--header-bg); border-bottom: 3px solid var(--accent); padding-bottom: 0.5rem; margin-bottom: 0.5rem; }
    .module-summary { color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }

    /* Workflow card */
    .workflow { background: var(--card); border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 2rem; overflow: hidden; }
    .workflow h3 { padding: 1rem 1.5rem; background: #f7fafc; border-bottom: 1px solid var(--border); font-size: 1.1rem; display: flex; align-items: center; gap: 0.75rem; }
    .tc-badge { font-size: 0.75rem; background: var(--accent); color: white; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; margin-left: auto; }

    /* Meta table */
    .meta-table { width: 100%; font-size: 0.85rem; border-collapse: collapse; }
    .meta-table th { text-align: left; padding: 0.4rem 1.5rem; width: 120px; color: var(--muted); font-weight: 600; }
    .meta-table td { padding: 0.4rem 0.5rem; }
    .meta-table tr { border-bottom: 1px solid var(--border); }

    /* Steps */
    .steps { padding: 1rem 1.5rem; }
    .step { border: 1px solid var(--border); border-radius: 8px; margin-bottom: 1rem; overflow: hidden; }
    .step-header { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: #f7fafc; border-bottom: 1px solid var(--border); cursor: pointer; }
    .step-header:hover { background: #edf2f7; }
    .step-num { width: 28px; height: 28px; border-radius: 50%; background: var(--accent); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; flex-shrink: 0; }
    .step-body { display: flex; gap: 1.5rem; padding: 1rem; flex-wrap: wrap; }
    .step-info { flex: 1; min-width: 300px; }
    .step-caption { margin-bottom: 0.75rem; color: var(--text); font-size: 0.9rem; }

    .detail-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; }
    .detail-table th { text-align: left; padding: 0.3rem 0.5rem; width: 80px; color: var(--muted); vertical-align: top; }
    .detail-table td { padding: 0.3rem 0.5rem; word-break: break-all; }
    .detail-table code { background: #edf2f7; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.78rem; }
    .detail-table .errors { color: var(--fail); }

    .screenshot-container { flex: 0 0 480px; max-width: 480px; }
    .screenshot-container img { width: 100%; border: 1px solid var(--border); border-radius: 6px; cursor: zoom-in; transition: transform 0.2s; }
    .screenshot-container img:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .screenshot-container.no-img { display: flex; align-items: center; justify-content: center; color: var(--muted); font-style: italic; background: #f7fafc; border-radius: 6px; min-height: 100px; }

    /* Badges */
    .badge { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
    .badge.pass { background: var(--pass-bg); color: var(--pass); border: 1px solid var(--pass); }
    .badge.fail { background: var(--fail-bg); color: var(--fail); border: 1px solid var(--fail); }
    .badge.warn { background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn); }
    .badge.info { background: var(--info-bg); color: var(--info); border: 1px solid var(--info); }

    /* Footer */
    .report-footer { text-align: center; padding: 2rem; color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); margin-top: 2rem; }

    /* Responsive */
    @media (max-width: 1024px) {
      .container { flex-direction: column; }
      .toc-sidebar { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid var(--border); }
      .step-body { flex-direction: column; }
      .screenshot-container { flex: none; max-width: 100%; }
      .summary { padding: 1rem; }
      .main-content { padding: 1rem; }
    }

    /* Print */
    @media print {
      .toc-sidebar { display: none; }
      .report-header { padding: 1rem; }
      .step-body { page-break-inside: avoid; }
      .workflow { page-break-inside: avoid; }
      .screenshot-container img { max-height: 300px; object-fit: contain; }
    }

    /* Expand/collapse */
    .step-body.collapsed { display: none; }
  </style>
</head>
<body>

  <div class="report-header">
    <h1>EAM System — E2E Test Results</h1>
    <div class="subtitle">Automated Visual Test Report with Step-by-Step Evidence</div>
    <div class="meta">
      <span>Generated: ${generatedAt}</span>
      <span>Base URL: ${escapeHtml(index.entries[0]?.url?.replace(/\/[^/]*$/, '') ?? '')}</span>
      <span>Framework: Dual-Purpose Automation (Playwright ${process.env.npm_package_devDependencies__playwright_test ?? 'v1.58.2'})</span>
    </div>
  </div>

  <div class="summary">
    <div class="summary-card info">
      <div class="num">${totalWorkflows}</div>
      <div class="label">Workflows Tested</div>
    </div>
    <div class="summary-card info">
      <div class="num">${totalSteps}</div>
      <div class="label">Total Steps</div>
    </div>
    <div class="summary-card info">
      <div class="num">${totalScreenshots}</div>
      <div class="label">Screenshots Captured</div>
    </div>
    <div class="summary-card pass">
      <div class="num">${passRate}%</div>
      <div class="label">Pass Rate</div>
    </div>
    <div class="summary-card pass">
      <div class="num">${passCount}</div>
      <div class="label">Steps Passed</div>
    </div>
    ${warnCount > 0 ? `<div class="summary-card warn"><div class="num">${warnCount}</div><div class="label">Warnings</div></div>` : ''}
    ${errorCount > 0 ? `<div class="summary-card fail"><div class="num">${errorCount}</div><div class="label">Errors</div></div>` : ''}
  </div>

  <div class="container">
    <nav class="toc-sidebar">
      <h3>Test Modules</h3>
      <ul>${tocHtml}</ul>
    </nav>
    <main class="main-content">
      ${contentHtml}
    </main>
  </div>

  <div class="report-footer">
    <p>EAM E2E Test Results &mdash; Auto-generated by the Dual-Purpose Automation Framework</p>
    <p>CubeWorks Innovation &bull; ${generatedAt}</p>
  </div>

  <script>
    // Toggle step expand/collapse
    document.querySelectorAll('.step-header').forEach(header => {
      header.addEventListener('click', () => {
        const body = header.nextElementSibling;
        if (body) body.classList.toggle('collapsed');
      });
    });
  </script>
</body>
</html>`
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */

function main() {
  console.log('📊 Generating E2E test results report...')
  console.log(`   Index: ${INDEX_PATH}`)
  console.log(`   Output: ${outputPath}`)

  const index = loadIndex()
  const html = generateHTML(index)

  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
  fs.writeFileSync(outputPath, html, 'utf-8')

  const sizeMB = (Buffer.byteLength(html, 'utf-8') / (1024 * 1024)).toFixed(1)
  console.log(`✅ Report generated: ${outputPath} (${sizeMB} MB)`)
  console.log(`   ${index.total_workflows} workflows, ${index.total_steps} steps, ${index.total_screenshots} screenshots`)
}

main()
