import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Vercel serves the app at the domain root.
// GitHub Pages serves it from /kmeans-customer-segmentation/.
const base = process.env.VERCEL
  ? '/'
  : '/kmeans-customer-segmentation/'

export default defineConfig({
  plugins: [react()],
  base,
})
