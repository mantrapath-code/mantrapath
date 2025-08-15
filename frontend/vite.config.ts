import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, loadEnv } from "vite";
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: parseInt(process.env.VITE_FRONTEND_PORT || '5173'),
    host: '0.0.0.0', // Allow access from any host
    hmr: {
      port: parseInt(process.env.VITE_FRONTEND_PORT || '5173'),
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_GATEWAY_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
