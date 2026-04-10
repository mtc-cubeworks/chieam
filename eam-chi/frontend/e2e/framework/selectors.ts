/**
 * Dual-Purpose Automation Framework — Centralized Selectors
 *
 * Maps logical UI elements to stable CSS / data-testid selectors.
 * Prioritises data-testid; falls back to structural selectors.
 */

export const S = {
  /* ---- Login page ---- */
  login: {
    usernameInput: '[data-testid="login-username"] input, input[placeholder*="username" i]',
    passwordInput: '[data-testid="login-password"] input, input[type="password"]',
    submitButton: '[data-testid="login-submit"], form button[type="submit"]',
    errorMessage: '[data-testid="login-error"], [role="alert"]',
    brandingLogo: '[data-testid="login-logo"], img[alt="Organization logo"]',
    brandingTitle: '[data-testid="login-title"]',
  },

  /* ---- Sidebar / navigation ---- */
  sidebar: {
    root: '[data-testid="sidebar"], aside',
    navMenu: '[data-testid="nav-menu"]',
    collapseButton: '[data-testid="sidebar-toggle"]',
    navLink: (entity: string) => `nav a[href="/${entity}"], a[href="/${entity}"]`,
    userDropdown: '[data-testid="user-menu"]',
    logoutButton: 'text=Logout',
  },

  /* ---- Header / top bar ---- */
  header: {
    root: 'header',
    breadcrumb: '[data-testid="breadcrumb"]',
    notifications: '[data-testid="notifications-btn"], button:has(> .i-lucide-bell)',
  },

  /* ---- Dashboard ---- */
  dashboard: {
    root: '[data-testid="dashboard"]',
    kpiCard: '[data-testid="kpi-card"]',
    chartContainer: '[data-testid="chart"]',
  },

  /* ---- Entity list page ---- */
  entityList: {
    root: '[data-testid="entity-list"]',
    newButton: '[data-testid="btn-new"], button:has-text("New")',
    table: '[data-testid="entity-table"], table',
    tableRow: 'table tbody tr',
    searchInput: '[data-testid="search-input"], input[placeholder*="Search" i]',
    pagination: '[data-testid="pagination"]',
    viewModeTabs: '[data-testid="view-mode"]',
    emptyState: '[data-testid="empty-state"], text=No records found',
    exportButton: '[data-testid="btn-export"]',
  },

  /* ---- Entity detail / form page ---- */
  entityDetail: {
    root: '[data-testid="entity-detail"]',
    form: '[data-testid="entity-form"], form',
    saveButton: '[data-testid="btn-save"], button:has-text("Save")',
    cancelButton: '[data-testid="btn-cancel"], button:has-text("Cancel")',
    editButton: '[data-testid="btn-edit"], button:has(> .i-lucide-pencil)',
    deleteButton: '[data-testid="btn-delete"]',
    backButton: '[data-testid="btn-back"], button:has(> .i-lucide-arrow-left)',
    tabBar: '[role="tablist"]',
    tab: (name: string) => `[role="tab"]:has-text("${name}")`,
    field: (name: string) => `input[name="${name}"], textarea[name="${name}"]`,
    fieldInput: (name: string) => `input[name="${name}"]`,
    fieldSelect: (name: string) => `input[name="${name}"]`,
    fieldError: (name: string) => `.text-destructive, [data-testid="field-error"]`,
    errorAlert: '[data-testid="error-alert"], [role="alert"][data-color="error"]',
    attachmentsTab: '[role="tab"]:has-text("Attachments")',
    uploadButton: 'button:has-text("Upload"), button:has(> .i-lucide-upload)',
  },

  /* ---- Workflow ---- */
  workflow: {
    stateLabel: '[data-testid="workflow-state"]',
    actionDropdown: '[data-testid="workflow-actions"]',
    actionButton: (action: string) => `[data-testid="wf-action-${action}"], [role="menuitem"]:has-text("${action}")`,
  },

  /* ---- Toasts & modals ---- */
  toast: {
    container: '[data-testid="toast"], [role="status"]',
    success: '[data-testid="toast-success"]',
    error: '[data-testid="toast-error"]',
    message: '[data-sonner-toast] [data-title], .toast-message',
  },

  modal: {
    root: '[role="dialog"]',
    confirmButton: '[role="dialog"] button:has-text("Confirm"), [role="dialog"] button:has-text("Yes")',
    cancelButton: '[role="dialog"] button:has-text("Cancel"), [role="dialog"] button:has-text("No")',
    deleteConfirmButton: '[role="dialog"] button:has-text("Delete")',
  },

  /* ---- Generic ---- */
  loading: {
    spinner: '[data-testid="loading"], .animate-spin',
    skeleton: '.animate-pulse, [data-testid="skeleton"]',
  },
} as const
