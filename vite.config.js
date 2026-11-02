import { defineConfig } from 'vite';
// base './' = the build works from any folder or sub-path on your host.
// Also builds an embeddable ES library: site/currency-stream-logo.js
export default defineConfig({ base: './', build: { outDir: 'site', emptyOutDir: true } });
