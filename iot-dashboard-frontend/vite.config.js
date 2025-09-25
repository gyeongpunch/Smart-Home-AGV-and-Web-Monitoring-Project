// iot-dashboard-frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [ vue() ],
  server: {
    port: 5173,
    proxy: {
      // /api 로 시작하는 요청은 http://localhost:3000 으로 보냅니다
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
