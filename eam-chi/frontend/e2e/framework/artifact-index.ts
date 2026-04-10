/**
 * Dual-Purpose Automation Framework — Artifact Index Builder
 *
 * Manages the Visual Artifact Index (index.json) that serves as the
 * Structured Narrative Map for AI-driven manual generation.
 */

import fs from 'fs'
import path from 'path'
import type { ArtifactEntry, ArtifactIndex } from './types'

export class ArtifactIndexBuilder {
  private entries: ArtifactEntry[] = []
  private outputDir: string
  private indexPath: string

  constructor(outputDir: string) {
    this.outputDir = outputDir
    this.indexPath = path.join(outputDir, 'index.json')
    fs.mkdirSync(outputDir, { recursive: true })

    // Load existing index if resuming
    if (fs.existsSync(this.indexPath)) {
      try {
        const existing: ArtifactIndex = JSON.parse(fs.readFileSync(this.indexPath, 'utf-8'))
        this.entries = existing.entries || []
      } catch {
        this.entries = []
      }
    }
  }

  addEntry(entry: ArtifactEntry): void {
    this.entries.push(entry)
  }

  getEntries(): ArtifactEntry[] {
    return [...this.entries]
  }

  getEntriesByWorkflow(workflow: string): ArtifactEntry[] {
    return this.entries.filter((e) => e.workflow === workflow)
  }

  flush(baseURL: string, project: string): void {
    const workflows = new Set(this.entries.map((e) => e.workflow))
    const screenshots = this.entries.filter((e) => e.visual_artifact).length

    const index: ArtifactIndex = {
      generated_at: new Date().toISOString(),
      base_url: baseURL,
      project,
      total_workflows: workflows.size,
      total_steps: this.entries.length,
      total_screenshots: screenshots,
      entries: this.entries,
    }

    fs.writeFileSync(this.indexPath, JSON.stringify(index, null, 2), 'utf-8')
  }

  clear(): void {
    this.entries = []
    if (fs.existsSync(this.indexPath)) {
      fs.unlinkSync(this.indexPath)
    }
  }
}
