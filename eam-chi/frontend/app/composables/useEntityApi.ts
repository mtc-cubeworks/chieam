/**
 * Entity API Composable
 * =====================
 * Entity CRUD, list, options, workflow actions, document actions.
 */
import { useCacheStore } from '~/stores/cache'
import { useApiFetch } from './useApiFetch'
import type {
  ActionRequest,
  ActionResponse,
  ListResponse,
  EntityMeta,
  MetaListItem,
} from './useApiTypes'

const TTL = {
  META_LIST: 30 * 60 * 1000,      // 30 min — socket invalidates on change
  ENTITY_META: 30 * 60 * 1000,    // 30 min — socket invalidates on change
  ENTITY_OPTIONS: 15 * 60 * 1000, // 15 min — dropdown data changes infrequently
  LINKED_TITLES: 10 * 60 * 1000,  // 10 min — display names for link fields
}

interface LinkedTitlesCache {
  [key: string]: { title: string; timestamp: number }
}

const isClient = typeof window !== 'undefined'

const getLinkedTitlesCache = (): LinkedTitlesCache => {
  if (!isClient) return {}
  try {
    const cached = localStorage.getItem('linked_titles_cache')
    return cached ? JSON.parse(cached) : {}
  } catch {
    return {}
  }
}

const setLinkedTitlesCache = (c: LinkedTitlesCache) => {
  if (!isClient) return
  try {
    localStorage.setItem('linked_titles_cache', JSON.stringify(c))
  } catch {
    // localStorage full or unavailable — silently skip
  }
}

export const updateLinkedTitlesCache = (linkTitles: Record<string, string>) => {
  if (!isClient || !linkTitles) return
  const c = getLinkedTitlesCache()
  const now = Date.now()
  Object.entries(linkTitles).forEach(([key, title]) => {
    c[key] = { title, timestamp: now }
  })
  Object.keys(c).forEach(key => {
    if (c[key] && now - c[key].timestamp > TTL.LINKED_TITLES) delete c[key]
  })
  setLinkedTitlesCache(c)
}

export const getLinkedTitle = (entity: string, id: string): string | null => {
  if (!isClient) return null
  const c = getLinkedTitlesCache()
  const key = `${entity}::${id}`
  const entry = c[key]
  if (entry && Date.now() - entry.timestamp < TTL.LINKED_TITLES) return entry.title
  return null
}

export const useEntityApi = () => {
  const { apiFetch, baseURL } = useApiFetch()
  const cache = useCacheStore()

  return {
    async getMeta(): Promise<{ status: string; data: MetaListItem[] }> {
      return cache.fetchCached(
        'meta:list',
        () => apiFetch<{ status: string; data: MetaListItem[] }>(`${baseURL}/meta`),
        TTL.META_LIST
      )
    },

    async getEntityMeta(entity: string): Promise<{ status: string; data: EntityMeta }> {
      return cache.fetchCachedWithLocalStorage(
        `meta:entity:v2:${entity}`,
        () => apiFetch<{ status: string; data: EntityMeta }>(`${baseURL}/meta/${entity}`),
        TTL.ENTITY_META
      )
    },

    async getGroupedOptions(
      childEntity: string,
      params: { parent_entity: string; child_parent_fk_field: string; search?: string; limit?: number }
    ): Promise<{ status: 'success' | 'error'; groups?: any[]; message?: string }> {
      const query = new URLSearchParams()
      query.append('parent_entity', params.parent_entity)
      query.append('child_parent_fk_field', params.child_parent_fk_field)
      if (params.search) query.append('search', params.search)
      if (params.limit) query.append('limit', params.limit.toString())
      return apiFetch(`${baseURL}/entity/${childEntity}/grouped-options?${query.toString()}`)
    },

    async postQueryOptions(body: {
      key: string; entity: string; field: string;
      form_state?: Record<string, unknown>; static_params?: Record<string, unknown>
    }): Promise<{ status: 'success' | 'error'; options?: any[]; message?: string }> {
      return apiFetch(`${baseURL}/entity/query-options`, { method: 'POST', body })
    },

    async getEntityList<T = any>(
      entity: string,
      params?: { page?: number; pageSize?: number; sortField?: string; sortOrder?: 'asc' | 'desc'; filterField?: string; filterValue?: string }
    ): Promise<ListResponse<T>> {
      const query = new URLSearchParams()
      if (params?.page) query.append('page', params.page.toString())
      if (params?.pageSize) query.append('page_size', params.pageSize.toString())
      if (params?.sortField) query.append('sort_field', params.sortField)
      if (params?.sortOrder) query.append('sort_order', params.sortOrder)
      if (params?.filterField) query.append('filter_field', params.filterField)
      if (params?.filterValue !== undefined) query.append('filter_value', params.filterValue)
      return apiFetch<ListResponse<T>>(`${baseURL}/entity/${entity}/list?${query.toString()}`)
    },

    async getEntityListView<T = any>(
      entity: string,
      params?: { page?: number; pageSize?: number; sortField?: string; sortOrder?: 'asc' | 'desc'; filterField?: string; filterValue?: string }
    ): Promise<ListResponse<T>> {
      const query = new URLSearchParams()
      if (params?.page) query.append('page', params.page.toString())
      if (params?.pageSize) query.append('page_size', params.pageSize.toString())
      if (params?.sortField) query.append('sort_field', params.sortField)
      if (params?.sortOrder) query.append('sort_order', params.sortOrder)
      if (params?.filterField) query.append('filter_field', params.filterField)
      if (params?.filterValue !== undefined) query.append('filter_value', params.filterValue)

      const response = await apiFetch<ListResponse<T>>(`${baseURL}/entity/${entity}/list-view?${query.toString()}`)
      if (response.status === 'success' && response.data) {
        const allLinkTitles: Record<string, string> = {}
        response.data.forEach((record: any) => {
          if (record._link_titles) Object.assign(allLinkTitles, record._link_titles)
        })
        updateLinkedTitlesCache(allLinkTitles)
      }
      return response
    },

    async getPositionDiagram(filters?: { location?: string; system?: string }): Promise<{
      status: string;
      nodes: any[];
      edges: any[];
      filters?: {
        location: { label: string; value: string }[];
        system: { label: string; value: string }[];
        selected?: {
          location?: string | null;
          system?: string | null;
        };
      };
    }> {
      return apiFetch(`${baseURL}/features/diagram/position`, {
        query: {
          location: filters?.location || undefined,
          system: filters?.system || undefined,
        },
      })
    },

    async getEntityDetail<T = any>(entity: string, id: string): Promise<{ status: string; data: T }> {
      return apiFetch<{ status: string; data: T }>(`${baseURL}/entity/${entity}/detail/${id}`)
    },

    async postEntityAction<T = any>(entity: string, request: ActionRequest): Promise<ActionResponse<T>> {
      return apiFetch<ActionResponse<T>>(`${baseURL}/entity/${entity}/action`, { method: 'POST', body: request })
    },

    async deleteEntity<T = any>(entity: string, id: string): Promise<ActionResponse<T>> {
      return apiFetch<ActionResponse<T>>(`${baseURL}/entity/${entity}/${id}`, { method: 'DELETE' })
    },

    async postWorkflowAction<T = any>(entity: string, id: string, action: string): Promise<ActionResponse<T>> {
      return apiFetch<ActionResponse<T>>(`${baseURL}/entity/${entity}/workflow`, { method: 'POST', body: { id, action } })
    },

    async postDocumentAction<T = any>(entity: string, id: string, action: string, payload?: Record<string, any>): Promise<ActionResponse<T>> {
      return apiFetch<ActionResponse<T>>(`${baseURL}/entity/${entity}/${id}/action/${action}`, {
        method: 'POST',
        body: payload ? { payload } : undefined,
      })
    },

    async getEntityOptions(entity: string, search?: string, limit?: number) {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (limit) params.append('limit', limit.toString())

      if (search) {
        return apiFetch<{ status: string; options: { value: string; label: string }[] }>(
          `${baseURL}/entity/${entity}/options?${params.toString()}`
        )
      }

      const cacheKey = `entity:options:${entity}:${limit || ''}`
      return cache.fetchCached(
        cacheKey,
        () => apiFetch<{ status: string; options: { value: string; label: string }[] }>(
          `${baseURL}/entity/${entity}/options?${params.toString()}`
        ),
        TTL.ENTITY_OPTIONS
      )
    },

    async login(username: string, password: string) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      return apiFetch<{ access_token: string; refresh_token: string }>(`${baseURL}/auth/login`, { method: 'POST', body: formData })
    },

    async refreshToken() {
      return apiFetch<{ access_token: string; refresh_token: string }>(`${baseURL}/auth/refresh`, { method: 'POST' })
    },

    async validateToken(token: string) {
      return apiFetch<{ user: Record<string, unknown> }>(`${baseURL}/auth/validate`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    },

    async getChildRecords(
      parentEntity: string,
      recordId: string,
      childEntity: string,
    ): Promise<{ status: string; data: any[]; total: number; child_entity: string; fk_field: string }> {
      return apiFetch(`${baseURL}/entity/${parentEntity}/${recordId}/children/${childEntity}`)
    },

    async bulkSaveChildren(
      parentEntity: string,
      recordId: string,
      childEntity: string,
      rows: Record<string, any>[],
      deletedIds?: string[],
    ): Promise<ActionResponse> {
      return apiFetch<ActionResponse>(`${baseURL}/entity/${parentEntity}/${recordId}/children/${childEntity}`, {
        method: 'POST',
        body: { rows, deleted_ids: deletedIds || [] },
      })
    },

    async getEntityPrefill(entity: string): Promise<{ status: string; data: Record<string, any> }> {
      return apiFetch<{ status: string; data: Record<string, any> }>(`${baseURL}/entity/${entity}/prefill`)
    },

    async getFetchFromFields(
      entity: string,
      id: string,
      fields: string[],
    ): Promise<{ status: string; data: Record<string, any>; _link_titles: Record<string, string> }> {
      const params = new URLSearchParams({ fields: fields.join(',') })
      return apiFetch(`${baseURL}/entity/${entity}/fetch_from/${id}?${params.toString()}`)
    },

    getLinkedTitle,
    updateLinkedTitlesCache,
  }
}
