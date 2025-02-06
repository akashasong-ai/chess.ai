import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'https://ai-arena-backend.onrender.com',
      '/socket.io': {
        target: 'https://ai-arena-backend.onrender.com',
        ws: true
      }
    }
  }
})      