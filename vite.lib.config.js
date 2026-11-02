import { defineConfig } from 'vite';
// npm run build:lib -> site/embed/currency-stream-logo.js (ES module; panel + occlusion are lazy chunks next to it).
// Built in app mode (not `lib`) so it is fully minified and tree-shaken.
export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: 'site/embed', emptyOutDir: true, chunkSizeWarningLimit: 900,
    rollupOptions: {
      input: 'src/logo.js',
      preserveEntrySignatures: 'exports-only',
      output: { format: 'es', entryFileNames: 'currency-stream-logo.js', chunkFileNames: 'chunks/[name]-[hash].js' },
    },
  },
});
