import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import tsconfigPaths from "vite-tsconfig-paths";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      '/api/sessions': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/api/sign-in': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/api/get-started': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/api/me': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/api/sign-out': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
    },
    fs: {
      allow: [
        // Only allow main project folders
        './',
      ],
      strict: true,
    },
  },
  optimizeDeps: {
    exclude: [
      "adapt_learn",
      "res",
      "backend",
    ],
  },
  plugins: [
    react(),
    tsconfigPaths(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
