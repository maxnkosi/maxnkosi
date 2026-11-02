import { defineConfig } from 'vite';
// npm run build:lib -> site/embed/currency-stream-logo.js (single self-contained ES module)
export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: 'site/embed', emptyOutDir: true,
    lib: { entry: 'src/logo.js', formats: ['es'], fileName: () => 'currency-stream-logo.js' },
  },
});
