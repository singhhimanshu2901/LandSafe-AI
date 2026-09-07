import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Landsafe AI',
        short_name: 'Landsafe',
        theme_color: '#0b6e4f',
        icons: []
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html}']
      }
    })
  ],
  server: { port: 5173 }
})
