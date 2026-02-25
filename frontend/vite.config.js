import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  // base ensures built assets are referenced as /static/assets/... which
  // FastAPI serves correctly from the app/static mount point.
  base: '/static/',
  build: {
    outDir: '../app/static',
    emptyOutDir: false, // preserve landing.html, css/, js/
  },
})
