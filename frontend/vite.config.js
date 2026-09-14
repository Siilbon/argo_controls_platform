import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: {
    // Plotly (~4.6 MB) is its own chunk, only downloaded when a trend is opened
    chunkSizeWarningLimit: 5000,
  },
  server: {
    proxy: {
      // Any request starting with /api gets forwarded to Flask
      '/api': 'http://localhost:5001',
    },
  },
})
