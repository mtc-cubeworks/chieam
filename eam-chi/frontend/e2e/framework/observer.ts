/**
 * Dual-Purpose Automation Framework — Observer Module
 *
 * Hooks into the Playwright lifecycle to capture screenshots,
 * DOM snapshots, and contextual metadata for every documented step.
 * Populates the Visual Artifact Index as a Structured Narrative Map.
 */

import fs from 'fs'
import path from 'path'
import type { Page } from '@playwright/test'
import type {
  ArtifactEntry,
  DomContext,
  DocMetadata,
  ObserverConfig,
} from './types'
import { ArtifactIndexBuilder } from './artifact-index'

export class Observer {
  private config: Required<ObserverConfig>
  private index: ArtifactIndexBuilder

  constructor(config: ObserverConfig) {
    this.config = {
      outputDir: config.outputDir,
      screenshotDir: config.screenshotDir ?? path.join(config.outputDir, 'screenshots'),
      captureDOM: config.captureDOM ?? true,
      captureScreenshots: config.captureScreenshots ?? true,
      project: config.project ?? 'eam',
      baseURL: config.baseURL ?? '',
    }

    fs.mkdirSync(this.config.screenshotDir, { recursive: true })
    this.index = new ArtifactIndexBuilder(this.config.outputDir)
  }

  /**
   * Capture a documented step: screenshot + DOM context + index entry.
   */
  async capture(
    page: Page,
    opts: {
      id: string
      workflow: string
      persona: string
      stepIndex: number
      action: string
      docMetadata?: DocMetadata
    },
  ): Promise<ArtifactEntry> {
    // 1. Screenshot
    let screenshotPath = ''
    if (this.config.captureScreenshots) {
      const filename = `${opts.workflow}__${opts.id}.png`
      screenshotPath = path.join(this.config.screenshotDir, filename)
      await page.screenshot({ path: screenshotPath, fullPage: false })
    }

    // 2. DOM context
    const domContext = await this.captureDomContext(page)

    // 3. DOM snapshot (cleaned ARIA tree)
    let domSnapshotPath: string | undefined
    if (this.config.captureDOM) {
      domSnapshotPath = await this.captureDomSnapshot(page, opts.workflow, opts.id)
    }

    // 4. Build entry
    const entry: ArtifactEntry = {
      id: opts.id,
      persona: opts.persona,
      workflow: opts.workflow,
      step_index: opts.stepIndex,
      action: opts.action,
      visual_artifact: screenshotPath
        ? path.relative(this.config.outputDir, screenshotPath)
        : '',
      dom_snapshot: domSnapshotPath
        ? path.relative(this.config.outputDir, domSnapshotPath)
        : undefined,
      url: page.url(),
      timestamp: new Date().toISOString(),
      dom_context: domContext,
      doc_metadata: opts.docMetadata,
    }

    this.index.addEntry(entry)
    return entry
  }

  /**
   * Extract DOM context: page title, active element, visible errors, toasts.
   */
  private async captureDomContext(page: Page): Promise<DomContext> {
    const context = await page.evaluate(() => {
      const title = document.title
      const url = window.location.href
      const el = document.activeElement
      const active = el
        ? `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.getAttribute('name') ? '[name=' + el.getAttribute('name') + ']' : ''}`
        : ''

      // Collect visible error messages
      const errorEls = document.querySelectorAll(
        '.text-destructive, [data-testid="field-error"], [role="alert"][data-color="error"], [data-testid="error-alert"]',
      )
      const errors = Array.from(errorEls)
        .map((el) => el.textContent?.trim() ?? '')
        .filter(Boolean)

      // Collect toast messages
      const toastEls = document.querySelectorAll(
        '[data-sonner-toast] [data-title], [data-testid="toast"], [role="status"]',
      )
      const toasts = Array.from(toastEls)
        .map((el) => el.textContent?.trim() ?? '')
        .filter(Boolean)

      // Determine status
      let status: string = 'Success'
      if (errors.length > 0) status = 'ValidationError'
      else if (document.querySelector('.animate-spin, [data-testid="loading"]'))
        status = 'Loading'
      else if (
        document.querySelector(
          '[data-testid="empty-state"], [data-testid="no-data"]',
        )
      )
        status = 'Empty'

      return {
        page_title: title,
        current_url: url,
        active_element: active,
        visible_errors: errors,
        toast_messages: toasts,
        status,
      }
    })

    return context as DomContext
  }

  /**
   * Capture a cleaned-up ARIA/accessibility tree snapshot.
   */
  private async captureDomSnapshot(
    page: Page,
    workflow: string,
    stepId: string,
  ): Promise<string> {
    const snapshotDir = path.join(this.config.outputDir, 'dom-snapshots')
    fs.mkdirSync(snapshotDir, { recursive: true })

    const snapshot = await page.evaluate(() => {
      // Walk the DOM and extract a simplified accessibility tree
      function walk(el: Element, depth: number): string {
        if (depth > 8) return ''
        const tag = el.tagName.toLowerCase()
        const role = el.getAttribute('role') || ''
        const label =
          el.getAttribute('aria-label') ||
          el.getAttribute('placeholder') ||
          el.getAttribute('title') ||
          ''
        const text =
          el.childNodes.length === 1 && el.childNodes[0].nodeType === 3
            ? (el.childNodes[0].textContent?.trim().slice(0, 80) ?? '')
            : ''

        const indent = '  '.repeat(depth)
        let line = `${indent}<${tag}`
        if (role) line += ` role="${role}"`
        if (label) line += ` label="${label}"`
        if (el.id) line += ` id="${el.id}"`
        if (el.getAttribute('data-testid'))
          line += ` data-testid="${el.getAttribute('data-testid')}"`
        if (el.getAttribute('data-field'))
          line += ` data-field="${el.getAttribute('data-field')}"`
        line += '>'
        if (text) line += text

        const children = Array.from(el.children)
          .filter(
            (c) =>
              !['SCRIPT', 'STYLE', 'SVG', 'PATH', 'LINK', 'META'].includes(
                c.tagName,
              ),
          )
          .map((c) => walk(c, depth + 1))
          .filter(Boolean)
          .join('\n')

        if (children) return `${line}\n${children}\n${indent}</${tag}>`
        return text ? `${line}</${tag}>` : ''
      }

      const body = document.querySelector('main') || document.body
      return walk(body, 0)
    })

    const filename = `${workflow}__${stepId}.aria.txt`
    const snapshotPath = path.join(snapshotDir, filename)
    fs.writeFileSync(snapshotPath, snapshot, 'utf-8')
    return snapshotPath
  }

  /**
   * Flush the index to disk. Call at the end of a test suite.
   */
  flush(): void {
    this.index.flush(this.config.baseURL, this.config.project)
  }

  /**
   * Clear all artifacts (for fresh runs).
   */
  clear(): void {
    this.index.clear()
  }

  get entries() {
    return this.index.getEntries()
  }
}
