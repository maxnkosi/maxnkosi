- 👋 Hi, I’m Max
- 👀 I’m interested in Art, Design & Tech
- 🌱 I’m currently learning Web Development
- 📫 maxnkosi28@gmail.com

<!---
maxnkosi/maxnkosi is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

## Currency Stream – static 3D logo

A static, glass-material render of the assembled logo (Blender frame 226).

```bash
npm install
npm run dev      # http://127.0.0.1:5173  — drag to orbit, wheel to zoom
```

- `public/models/currency-stream-logo.glb` – 3 meshes (`Central S`, `Left arc`, `Right arc`) under root `Currency Stream Logo`, 0 animations.
- `src/main.js` – Three.js loader, static lighting, orbit controls. `?view=front|oblique` or `?yaw=&pitch=` sets the start pose.
- `src/glassMaterial.js` – rebuilds the Blender material (refractive glass + logo artwork on front-facing surfaces).
- `tools/export_static_logo.py` – Blender (`bpy`) bake: frame-226 transforms, unparent, strip animation, export. `tools/verify_glb.py` checks the GLB.
- `reference/` – supplied JPEG and front/oblique screenshots.

### Use it on a website

`npm run build` writes ready-to-upload files to `site/` (relative paths, works in any folder):

- `site/index.html` – full-page demo.
- `site/embed/` – drop into an existing page: `currency-stream-logo.js` (self-contained, ~168 kB gzip), `models/currency-stream-logo.glb` (5.2 MB) and `example.html`.

```html
<div id="logo" style="width:520px;height:520px"></div>
<script type="module">
  import { mountCurrencyStreamLogo } from './currency-stream-logo.js';
  mountCurrencyStreamLogo(document.getElementById('logo'), {
    modelUrl: './models/currency-stream-logo.glb',
    view: 'front', controls: true, background: '#ffffff' // or null = transparent
  });
</script>
```
Serve over http(s) (not `file://`) and enable gzip/brotli for the `.glb`/`.js` on your host.

### Clear glass version

Same GLB, no tint or artwork: pass `material: 'clear'` to `mountCurrencyStreamLogo` (or open the demo with `?material=clear`).
With the default white background it uses a soft studio backdrop so the glass has something to refract; set `background` to a CSS colour, or `null` for a transparent canvas.

### Settings panel

`panel: true` (the demo shows it unless `?panel=0`) adds a live panel: IOR, depth, transmission, frosting, dispersion, internal back faces, absorption/tint, specular/environment/clearcoat/iridescence, artwork strength (coloured version), static light intensities and ambient occlusion (GTAO: intensity, radius, falloff, thickness, scale).
Pass starting values with `settings: { glass: { ior: 1.7 }, occlusion: { enabled: true } }`; read or change them later via the returned `.settings` and `.update()`. Defaults live in `src/settings.js`.

### Saving settings

Panel edits auto-save in the browser (`localStorage`, separately for the coloured and clear versions) and come back on reload.
**Save / share → Copy settings (JSON)** exports them; paste JSON into the field below it to load. To make a set permanent for everyone, pass it as `settings: {...}` or put the values in `defaultSettings()` in `src/settings.js`.

### Performance

| | before | after |
|---|---|---|
| GLB | 5.2 MB (3.3 MB gzip) | **1.0 MB (0.4 MB gzip)** |
| core JS (gzip) | 190 kB | **161 kB** (panel + occlusion are separate lazy chunks, ~17 kB gzip, fetched only if used) |
| idle cost | rendered every frame | **no frames when nothing changes** |
| single-file artifact | 7.5 MB | 2.0 MB |

What was done:
- `tools/optimize_glb.mjs` runs after the Blender export: exact-duplicate weld, 14-bit position / 10-bit normal quantization, meshopt compression, texture resized to 1536 px. Rounded bevels and UVs are unchanged (the loader needs the meshopt decoder, already wired in `src/logo.js`).
- The logo only loads when it is within 300 px of the viewport (`lazy`), renders only on orbit/resize/setting changes, pauses off-screen, and honours `prefers-reduced-motion`.
- `poster: '/posters/branded.webp'` (12 kB; `clear.webp` is 4 kB) shows instantly and stays as the fallback if WebGL is unavailable.
- `maxPixelRatio` (default 2) can be lowered, e.g. `1.5`, for phones.

Pipeline: `export_static_logo.py` -> `node tools/optimize_glb.mjs in.glb out.glb` -> `npm run build`.

Serving: use gzip/brotli for `.js`, long cache headers for the hashed files in `chunks/`, and `Cache-Control: immutable` for the `.glb` if you version its filename. Preload hint if the logo is above the fold: `<link rel="preload" href="/models/currency-stream-logo.glb" as="fetch" crossorigin>`.
