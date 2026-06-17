/**
 * Vite 构建配置 / Vite build configuration
 * @Function: 配置开发服务器、代理、构建输出 / Configure dev server, proxy, build output
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 路径别名 / Path aliases
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    // API 代理配置 / API proxy configuration
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8686',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8686',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
