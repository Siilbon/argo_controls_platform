import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// The site is served under /acp on the shared IIS server, so every URL the
// browser asks for starts with /acp. IIS strips that prefix before Flask sees
// the request, so the backend routes stay /api/... and /.
const BASE = '/acp/'

export default defineConfig({
  base: BASE,
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
      // Anything under /acp/api goes to Flask, without the /acp that IIS would strip
      [`${BASE}api`]: {
        target: 'http://localhost:5001',
        rewrite: path => path.slice(BASE.length - 1),
      },
    },
  },
})
