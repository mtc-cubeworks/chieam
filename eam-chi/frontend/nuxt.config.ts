// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/eslint', '@nuxt/ui', '@vueuse/nuxt', '@pinia/nuxt', '@nu-grid/nuxt'],

  colorMode: {
    preference: 'light',
    fallback: 'light'
  },

  ssr: false,

  devtools: {
    enabled: process.env.NODE_ENV !== 'production'
  },

  css: [
    '~/assets/css/main.css',
    '@quasar/quasar-ui-qcalendar/dist/QCalendarVariables.css',
    '@quasar/quasar-ui-qcalendar/dist/QCalendarMonth.css',
    '@quasar/quasar-ui-qcalendar/dist/QCalendarDay.css',
    '@quasar/quasar-ui-qcalendar/dist/QCalendarResource.css',
    '@quasar/quasar-ui-qcalendar/dist/QCalendarTask.css',
  ],

  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || '/api'
    }
  },

  nitro: {
    preset: 'node-server'
  },

  vite: {
    build: {
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            'pinia': ['pinia'],
            'vue': ['vue', 'vue-router'],
            'utils': ['@vueuse/core', 'scule']
          }
        }
      }
    }
  },

  compatibilityDate: '2025-01-15',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
