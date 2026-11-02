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
