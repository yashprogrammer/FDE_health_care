import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',   // served under /copilot/ behind the gateway: all URLs relative
  server: { port: 5172, proxy: { '/api': 'http://localhost:8002' } },
})
