import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
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
      port: parseInt(env.VITE_FRONTEND_PORT || '5173'),
      host: '0.0.0.0', // Allow access from any host including ngrok
      strictPort: false, // Allow fallback to next available port
      // Allow all hosts including ngrok domains
      allowedHosts: true,
      hmr: {
        port: parseInt(env.VITE_FRONTEND_PORT || '5173'),
        host: 'localhost', // HMR should always use localhost
      },
      proxy: {
        '/api': {
          target: env.VITE_API_GATEWAY_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true, // Enable WebSocket proxying
        }
      },
      // Allow all origins for development (needed for ngrok)
      cors: {
        origin: true,
        credentials: true
      }
    },
    preview: {
      port: parseInt(env.VITE_FRONTEND_PORT || '5173'),
      host: '0.0.0.0',
      strictPort: false
    },
    build: {
      // Ensure build works for various environments
      target: 'esnext',
      minify: 'esbuild'
    }
  }
});
