import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to, _from) => {
  const authStore = useAuthStore()

  // Skip auth check for setup page
  if (to.path === '/setup') {
    return
  }

  // On login page (or unauthenticated navigation), check if setup is needed
  if (to.path === '/login' || !authStore.isAuthenticated) {
    // Only check setup status on the client side
    if (import.meta.client) {
      try {
        const config = useRuntimeConfig()
        const baseURL = config.public.apiUrl as string
        const status = await $fetch<{ needs_setup: boolean }>(`${baseURL}/setup/status`)
        if (status.needs_setup) {
          return navigateTo('/setup')
        }
      } catch {
        // If the check fails, proceed normally
      }
    }
  }

  // Skip auth check for login page
  if (to.path === '/login') {
    if (authStore.isAuthenticated) {
      return navigateTo('/')
    }
    return
  }

  // If not authenticated, redirect to login
  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
})
