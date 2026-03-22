import { useAuthStore, type User } from '~/stores/auth'
import { useCacheStore } from '~/stores/cache'
import { resetApiFetch } from '~/composables/useApiFetch'
import { useEntityApi } from '~/composables/useEntityApi'
import { useWorkflowApi } from '~/composables/useWorkflowApi'

export const useAuth = () => {
  const authStore = useAuthStore()
  const cacheStore = useCacheStore()
  const { boot } = useBootInfo()
  const { getMeta, getEntityMeta } = useEntityApi()
  const { getWorkflowStates } = useWorkflowApi()

  const authState = computed(() => ({
    user: authStore.user,
    token: authStore.token,
    refreshToken: authStore.refreshToken,
    isAuthenticated: authStore.isAuthenticated
  }))

  const prefetchMetadata = () => {
    // Fire-and-forget: populate cache so first page load avoids API round-trips
    getMeta().then((meta) => {
      if (meta?.data) {
        const sidebar = meta.data.filter((e: any) => e.in_sidebar).slice(0, 8)
        sidebar.forEach((e: any) => {
          getEntityMeta(e.name).catch(() => {})
        })
      }
    }).catch(() => {})
  }

  const login = async (username: string, password: string) => {
    try {
      const result = await boot(username, password)

      if (result.success) {
        // Prefetch entity metadata in background so first page load hits cache
        prefetchMetadata()
        // Prefetch global workflow states (cached in localStorage)
        getWorkflowStates().catch(() => {})
        return { success: true }
      }
      return { success: false, message: result.message || 'Invalid credentials' }
    } catch (error: any) {
      return {
        success: false,
        message: error.data?.detail || 'Login failed'
      }
    }
  }

  const logout = () => {
    cacheStore.clear()
    resetApiFetch()
    authStore.logout()
    if (import.meta.client) {
      navigateTo('/login')
    }
  }

  return {
    authState,
    authStore,
    login,
    logout
  }
}
