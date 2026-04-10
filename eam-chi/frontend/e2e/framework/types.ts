/**
 * Dual-Purpose Automation Framework — Core Type Definitions
 *
 * Defines the YAML workflow schema, artifact index entries,
 * and observer configuration types.
 */

/* ------------------------------------------------------------------ */
/*  YAML Workflow Schema                                               */
/* ------------------------------------------------------------------ */

export type StepAction =
  | 'goto'
  | 'click'
  | 'type'
  | 'select'
  | 'hover'
  | 'wait'
  | 'screenshot'
  | 'clear'
  | 'press'
  | 'scroll'
  | 'clearSession'
  | 'logout'

export type AssertionType =
  | 'visible'
  | 'hidden'
  | 'hasText'
  | 'hasValue'
  | 'urlContains'
  | 'count'

export interface StepAssertion {
  type: AssertionType
  target?: string
  value?: string
}

export interface DocMetadata {
  title: string
  caption: string
  is_edge_case?: boolean
  manual_hint?: string
}

export interface WorkflowStep {
  id: string
  action: StepAction
  target?: string
  value?: string
  url?: string
  key?: string                 // for 'press' action (e.g. "Enter")
  wait_for?: string            // selector or 'networkidle'
  timeout?: number
  assertions?: StepAssertion[]
  visual_test?: boolean
  doc_metadata?: DocMetadata
}

export interface WorkflowDefinition {
  name: string
  description: string
  persona: string
  base_url?: string
  tags?: string[]
  steps: WorkflowStep[]
}

/* ------------------------------------------------------------------ */
/*  Visual Artifact Index                                              */
/* ------------------------------------------------------------------ */

export interface DomContext {
  page_title: string
  current_url: string
  active_element?: string
  visible_errors: string[]
  toast_messages: string[]
  status: 'Success' | 'ValidationError' | 'Loading' | 'Empty' | 'Error'
}

export interface ArtifactEntry {
  id: string
  persona: string
  workflow: string
  step_index: number
  action: string
  visual_artifact: string
  dom_snapshot?: string
  url: string
  timestamp: string
  dom_context: DomContext
  doc_metadata?: DocMetadata
  assertions_passed?: boolean
}

export interface ArtifactIndex {
  generated_at: string
  base_url: string
  project: string
  total_workflows: number
  total_steps: number
  total_screenshots: number
  entries: ArtifactEntry[]
}

/* ------------------------------------------------------------------ */
/*  Observer Config                                                    */
/* ------------------------------------------------------------------ */

export interface ObserverConfig {
  outputDir: string
  screenshotDir?: string
  captureDOM?: boolean
  captureScreenshots?: boolean
  project?: string
  baseURL?: string
}
