export default defineNuxtConfig({
  compatibilityDate: '2026-10-06',

  devtools: {
    enabled: true,
  },

  css: [
    '~/assets/css/main.css',
  ],

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