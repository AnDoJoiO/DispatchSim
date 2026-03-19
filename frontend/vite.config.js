import { fileURLToPath, URL } from 'node:url'
import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * Copies Silero VAD runtime assets (ONNX model, worklet, WASM) into the build
 * output so they are available at /static/ in production.
 */
function vadAssetsCopyPlugin() {
  const assets = [
    { pkg: '@ricky0123/vad-web', file: 'dist/vad.worklet.bundle.min.js' },
    { pkg: '@ricky0123/vad-web', file: 'dist/silero_vad_legacy.onnx' },
    { pkg: 'onnxruntime-web',    file: 'dist/ort-wasm-simd-threaded.wasm' },
    { pkg: 'onnxruntime-web',    file: 'dist/ort-wasm-simd-threaded.jsep.wasm' },
    { pkg: 'onnxruntime-web',    file: 'dist/ort-wasm-simd-threaded.mjs' },
  ]
  return {
    name: 'vad-assets-copy',
    writeBundle(options) {
      const outDir = options.dir || resolve(__dirname, '../app/static')
      for (const { pkg, file } of assets) {
        const src  = resolve(__dirname, 'node_modules', pkg, file)
        const name = file.split('/').pop()
        const dest = resolve(outDir, name)
        if (existsSync(src)) {
          mkdirSync(dirname(dest), { recursive: true })
          copyFileSync(src, dest)
        }
      }
    },
  }
}

export default defineConfig({
  plugins: [vue(), vadAssetsCopyPlugin()],
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
  // Allow importing .wasm and .onnx files
  assetsInclude: ['**/*.onnx', '**/*.wasm'],
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
