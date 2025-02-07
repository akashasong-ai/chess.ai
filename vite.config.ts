import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_SOCKET_URL': JSON.stringify('https://ai-arena-backend.onrender.com'),
    'import.meta.env.VITE_API_URL': JSON.stringify('https://ai-arena-backend.onrender.com')
  },
  server: {
    proxy: {
      '/socket.io': {
        target: 'https://ai-arena-backend.onrender.com',
        ws: true,
        changeOrigin: true,
        secure: true
      }
    }
  }
})                                