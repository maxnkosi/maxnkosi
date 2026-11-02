import { defineConfig } from 'vite';
export default defineConfig({
  base: './', publicDir: false, assetsInclude: ['**/*.glb'],
  build: { outDir: process.env.OUT, emptyOutDir: true, assetsInlineLimit: 1e8, rollupOptions: { output: { inlineDynamicImports: true } },
    lib: { entry: 'src/artifact.js', formats: ['iife'], name: 'CSLogo', fileName: () => 'bundle.js' } },
});
