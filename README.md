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
