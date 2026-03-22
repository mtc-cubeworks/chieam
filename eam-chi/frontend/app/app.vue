<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { useTokenRefresh } from "~/composables/useTokenRefresh";

const authStore = useAuthStore();
const { scheduleRefresh, cancelRefresh } = useTokenRefresh();

useHead({
  meta: [
    { name: "viewport", content: "width=device-width, initial-scale=1" },
    { name: "color-scheme", content: "light" },
  ],
  link: [{ rel: "icon", href: "/favicon.ico" }],
  htmlAttrs: {
    lang: "en",
    class: "light",
  },
});

const colorMode = useColorMode();
const appConfig = useAppConfig();

onMounted(() => {
  // Schedule proactive token refresh if already authenticated
  if (authStore.isAuthenticated && authStore.token) {
    scheduleRefresh(authStore.token);
  }
});

// Re-schedule whenever token is updated (login or refresh)
watch(
  () => authStore.token,
  (newToken) => {
    if (newToken) {
      scheduleRefresh(newToken);
    } else {
      cancelRefresh();
    }
  },
);

onUnmounted(() => {
  cancelRefresh();
});

onMounted(() => {
  // Load persisted theme
  const saved = localStorage.getItem("eam:theme");
  if (saved) {
    try {
      const theme = JSON.parse(saved);
      if (theme.primary) appConfig.ui.colors.primary = theme.primary;
      if (theme.neutral) appConfig.ui.colors.neutral = theme.neutral;
      if (theme.dark !== undefined) {
        colorMode.preference = theme.dark ? "dark" : "light";
        return;
      }
    } catch {}
  }
  // Default to light mode if no theme saved
  colorMode.preference = "light";
  document.documentElement.classList.remove("dark");
  document.documentElement.classList.add("light");
});

const title = "CubeEAM";
const description = "A metadata-driven Enterprise Asset Management application";

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
});

// Global error handler — catches unhandled Vue errors
const appError = ref<{ statusCode?: number; message?: string } | null>(null);

const handleError = () => {
  appError.value = null;
  clearError({ redirect: "/" });
};

useNuxtApp().vueApp.config.errorHandler = (err: any, _instance, info) => {
  console.error(`[Global Error] ${info}:`, err);
};
</script>

<template>
  <UApp>
    <UMain>
      <!-- Global error boundary -->
      <NuxtErrorBoundary
        @error="(err) => console.error('[ErrorBoundary]', err)"
      >
        <NuxtLayout>
          <NuxtPage />
        </NuxtLayout>

        <template
          #error="{ error: boundaryError, clearError: clearBoundaryError }"
        >
          <div
            class="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-4"
          >
            <UIcon
              name="i-lucide-alert-triangle"
              class="h-16 w-16 text-red-500"
            />
            <h2 class="text-xl font-semibold">Something went wrong</h2>
            <p class="text-muted text-center max-w-md">
              {{ boundaryError?.message || "An unexpected error occurred." }}
            </p>
            <div class="flex gap-2">
              <UButton @click="clearBoundaryError" variant="outline">
                Try Again
              </UButton>
              <UButton @click="navigateTo('/')"> Go Home </UButton>
            </div>
          </div>
        </template>
      </NuxtErrorBoundary>

      <!-- Global modals -->
      <DeleteModal />
      <ConfirmModal />
      <EntityModal />
    </UMain>
  </UApp>
</template>
