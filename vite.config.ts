import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'https://go-board-app-tunnel-mp5ybwn7.devinapps.com',
      '/socket.io': {
        target: 'https://go-board-app-tunnel-mp5ybwn7.devinapps.com',
        ws: true
      }
    }
  }
})         