export default defineNuxtConfig({
  compatibilityDate: '2026-10-06',

  devtools: {
    enabled: true,
  },

  css: [
    '~/assets/css/main.css',
  ],

  imports: {
    // Register directly: glob scanning can miss paths containing braces on Windows.
    imports: [
      {
        name: 'useCoverageApi',
        from: '~/composables/useCoverageApi',
      },
    ],
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://127.0.0.1:8000/api/coverage',
    },
  },

  nitro: {
    externals: {
      inline: [
        /[\\/]node_modules[\\/]nuxt[\\/]dist[\\/]/,
      ],
    },
  },
})
