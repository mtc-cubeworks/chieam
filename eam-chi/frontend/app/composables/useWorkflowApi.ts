/**
 * Workflow API Composable
 * =======================
 * Global workflow states, actions, workflows CRUD, transitions.
 */
import { useCacheStore } from '~/stores/cache'
import { useApiFetch } from './useApiFetch'

const TTL_WORKFLOW = 30 * 60 * 1000 // 30 min — socket invalidates on change
const TTL_WORKFLOW_LOCAL = 24 * 60 * 60 * 1000 // 24h — avoid fetching on every boot

export const useWorkflowApi = () => {
  const { apiFetch, baseURL } = useApiFetch()
  const cache = useCacheStore()

  return {
    // Global States CRUD
    async getWorkflowStates() {
      return cache.fetchCachedWithLocalStorage(
        'workflow:states',
        () => apiFetch<{ status: string; message: string; data: any[] }>(`${baseURL}/workflow/states`),
        TTL_WORKFLOW_LOCAL,
      )
    },
    async createWorkflowState(state: { label: string; color?: string }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/states`, { method: 'POST', body: state })
    },
    async updateWorkflowState(stateId: string, state: { label?: string; color?: string }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/states/${stateId}`, { method: 'PUT', body: state })
    },
    async deleteWorkflowState(stateId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/states/${stateId}`, { method: 'DELETE' })
    },

    // Global Actions CRUD
    async getWorkflowActions() {
      return cache.fetchCached(
        'workflow:actions',
        () => apiFetch<{ status: string; message: string; data: any[] }>(`${baseURL}/workflow/actions`),
        TTL_WORKFLOW
      )
    },
    async createWorkflowAction(action: { label: string }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/actions`, { method: 'POST', body: action })
    },
    async updateWorkflowAction(actionId: string, action: { label?: string }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/actions/${actionId}`, { method: 'PUT', body: action })
    },
    async deleteWorkflowAction(actionId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/actions/${actionId}`, { method: 'DELETE' })
    },

    // Workflows CRUD
    async getWorkflows() {
      return apiFetch<{ status: string; message: string; data: any[] }>(`${baseURL}/workflow`)
    },
    async getWorkflow(workflowId: string) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/${workflowId}`)
    },
    async getWorkflowByEntity(targetEntity: string) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/by-entity/${targetEntity}`)
    },
    async createWorkflow(workflowData: {
      name: string; target_entity: string; is_active?: boolean;
      state_links?: { state_id: string; is_initial?: boolean }[];
      transitions?: { from_state_id: string; action_id: string; to_state_id: string }[];
    }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow`, { method: 'POST', body: workflowData })
    },
    async updateWorkflow(workflowId: string, workflowData: {
      name?: string; is_active?: boolean;
      state_links?: { state_id: string; is_initial?: boolean }[];
      transitions?: { from_state_id: string; action_id: string; to_state_id: string }[];
    }) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}`, { method: 'PUT', body: workflowData })
    },
    async deleteWorkflow(workflowId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}`, { method: 'DELETE' })
    },

    // Workflow State Links
    async addStateToWorkflow(workflowId: string, stateLink: { state_id: string; is_initial?: boolean }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/${workflowId}/states`, { method: 'POST', body: stateLink })
    },
    async removeStateFromWorkflow(workflowId: string, stateLinkId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}/states/${stateLinkId}`, { method: 'DELETE' })
    },
    async updateStateLink(workflowId: string, stateLinkId: string, stateLink: { state_id: string; is_initial?: boolean }) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}/states/${stateLinkId}`, { method: 'PUT', body: stateLink })
    },
    async setInitialState(workflowId: string, stateLinkId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}/states/${stateLinkId}/set-initial`, { method: 'PUT' })
    },

    // Workflow Transitions
    async addTransitionToWorkflow(workflowId: string, transition: { from_state_id: string; action_id: string; to_state_id: string; allowed_roles?: string[] | null }) {
      return apiFetch<{ status: string; message: string; data: any }>(`${baseURL}/workflow/${workflowId}/transitions`, { method: 'POST', body: transition })
    },
    async updateTransition(workflowId: string, transitionId: string, transition: { from_state_id: string; action_id: string; to_state_id: string; allowed_roles?: string[] | null }) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}/transitions/${transitionId}`, { method: 'PUT', body: transition })
    },
    async removeTransitionFromWorkflow(workflowId: string, transitionId: string) {
      return apiFetch<{ status: string; message: string }>(`${baseURL}/workflow/${workflowId}/transitions/${transitionId}`, { method: 'DELETE' })
    },

    // Entity Workflow Transitions (runtime)
    async getWorkflowTransitions(entity: string, currentState?: string | null) {
      const query = new URLSearchParams()
      if (currentState) query.append('current_state', currentState)
      const qs = query.toString()
      return apiFetch<{ status: string; message?: string; data: any[] }>(
        `${baseURL}/workflow/${entity}/transitions${qs ? `?${qs}` : ''}`
      )
    },
  }
}
