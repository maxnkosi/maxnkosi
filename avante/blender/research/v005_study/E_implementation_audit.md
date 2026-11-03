# E. Implementation audit: build_avante_master.py (v004)

Scope: read-only audit of `build_avante_master.py` (834 lines), `qc_render.py`, `README.md`, `research/agent1..6_*.md`, the v004 macro and QC renders, and `research/references/ref01..13.png`. Nothing was run in Blender. All line numbers refer to `build_avante_master.py` unless prefixed `qc:` (qc_render.py).

Conventions used in the code: 1 BU = 1 m; `MM = 0.001` (L22); constants are in mm and multiplied by `MM` when written to geometry or to the Displacement Scale. Noise textures use **Object** coordinates (L297/L299). The objects have no transform (origin at world 0, scale 1), so Object coordinates are world metres. A Noise `Scale` of S therefore gives a feature size of about 1/S m (S = 833 gives about 1.2 mm).

Unset Principled inputs keep the Blender 4.x/5.x defaults. Socket names are applied only if they exist (`if k in p.inputs`, L254), so a misspelled or renamed socket is dropped silently.

Texture facts (decoded from the PNGs, not from code):

| File | px | Physical span (code) | px/mm | Effective ppi |
|---|---|---|---|---|
| COLOR / MASK-FOIL / MASK-EMB / MASK-UV `__LBL-FRONT-01` | 4870 x 2026 | 243.469 x 101.258 mm (`WRAP_ART`, L62) | 20.0 | 508 |
| COLOR / MASK-FOIL `__LBL-NECK-01` | 3174 x 360 | 158.667 x 17.975 mm (L79) | 20.0 | 508 |
| COLOR / MASK-FOIL `__LBL-ROUNDEL-01` | 1200 x 1200 | 47.706 mm (`ROUNDEL_TEX`, L57) | 25.15 | 639 |

- All PNGs are 8-bit RGBA with alpha 255 everywhere. The PNG dpi tag is 25 (metadata only).
- The masks are binary black/white with 1 to 3 px anti-aliased edges: median 1 px, p90 2 to 3 px. A few runs are up to 28 to 29 px on the neck and roundel masks (thin or soft strokes).
- MASK-FOIL and MASK-EMB for the front are the same image within 86 px. The foil bounding box is about 61 x 30.5 mm (AVANTE plus bird). Foil stroke widths: p10 about 7 px (0.35 mm), median about 35 px (1.75 mm).
- Image nodes: Cubic interpolation, CLIP extension (L261). Masks are Non-Color; colour maps keep the default sRGB. The `alpha` argument of `mat_label` and the `ALPHA__*.png` files are unused. Die shapes come from geometry.

Render-pixel footprint at the label (pinhole, sensor 36 mm by Blender default, fit AUTO, so 36 mm spans 2000 px on landscape renders):

| Camera | Distance to surface | Footprint | Render px/mm | Texture px/mm | Texel : px |
|---|---|---|---|---|---|
| CAM_Macro_Avante (2000x1600) | about 0.236 m | 0.0425 mm/px | 23.5 | 20.0 | 1 texel = 1.18 px (texture under-resolved) |
| CAM_Macro_CollarFlag (2000x1600) | about 0.20 m | 0.036 mm/px | 27.8 | 20.0 | 1 texel = 1.39 px (texture under-resolved) |
| CAM_Macro_Roundel (2000x1600) | about 0.242 m | 0.0436 mm/px | 23.0 | 25.15 | 0.91 (OK) |
| qc `paper` (1200x960) | about 0.169 m | 0.0507 mm/px | 19.7 | 20.0 | about 1:1 |

---

## 1. Foil materials

There are four foil or metal materials. Foil on paper and foil on film are separate node trees, not a shared group.

### 1a. FOIL-01 on paper: inside `mat_label()` (L310 to L368), used by `M_LBL-FRONT-01_SUB-01_Paper` (L596) and `M_LBL-NECK-01_SUB-01_Paper` (L639)

| Node | Setting | Line |
|---|---|---|
| Principled `foilb` | Base Color = `FOIL_F0` = (0.95, 0.69, 0.33) linear; Metallic 1.0 | L269, L339 |
| | Specular Tint (acts as the F82 edge tint for metals in Principled v2): default white, so no edge tint. Specular IOR Level 0.5 and IOR 1.5 are defaults with no effect at Metallic 1. Anisotropic 0. Coat 0. | not set |
| Roughness | 0.14 + 0.08 x Noise(Scale 800, Detail 2, Object coords), about 0.18 ± 0.02 typical (0.14 to 0.22 bounds). Feature size about 1.25 mm. | L340 to L341 |
| Normal | Bump(Strength 1.0, Distance 1.0), Height = `relief` x 0.5 | L342 to L343 |
| `relief` (shared with paper) | felt Noise(Scale 833, Detail 2) x 4.5e-5 + fibre Noise(Scale 1.0, Detail 2, Mapping Scale (4000, 800, 4000)) x 1.2e-5, in metres | L317 to L318 |
| | With Distance 1.0 the height is taken as metres. Foil therefore follows the felt at half amplitude: about 0 to 22 µm full range, typically about ±3 to 4 µm. Octaves are at about 1.2, 0.6 and 0.3 mm. No ColorRamp, no Distortion. | |
| Mask | Mix Shader Fac = MASK-FOIL-01 image `Color` (Non-Color, Cubic). Paper is shader 1, foil is shader 2. No blur, erode or dropout. | L315, L344 to L346 |
| Mask resolution | 20 px/mm (0.05 mm texel). The edge is the image's 1 to 3 px AA, so 0.05 to 0.15 mm. | — |
| UV coat | Coat Weight from MASK-UV goes to the **paper** BSDF only, not the foil. Coat Roughness 0.08. | L347 to L350 |

### 1b. FOIL-01 on film: inside `mat_roundel()` (L373 to L399)

| Node | Setting | Line |
|---|---|---|
| Principled `foilb` | Base Color FOIL_F0, Metallic 1.0 (same as 1a) | L380 |
| Roughness | 0.14 + 0.08 x Noise(800, Detail 2) | L381 to L382 |
| Normal | **None.** No bump on the roundel foil, so it is smooth. | — |
| Mask | MASK-FOIL-01__LBL-ROUNDEL-01 `Color` into the Mix Fac (ink is shader 1, foil is shader 2) | L377, L383 to L384 |
| Mask resolution | 25.15 px/mm (0.04 mm texel) | — |

### 1c. MET-01 gold pinline on the capsule: `M_MET-01_GoldInk` (L486)

- Base Color = `GOLD` = sRGB #E7C187 converted to linear (L268). Metallic **0.85**, Roughness 0.28. No noise and no bump.
- Faces with a centre below `PINLINE_TOP` get this material (L488 to L490). The gold band runs from z 171.83 to 173.25 mm, which is 1.42 mm tall.

### 1d. Glass "waviness" bump (for completeness)

- `M_GLS-01_Flint`: Bump Strength 1.0, Distance 0.00012 m, Height from Noise(Scale 28, about 36 mm features, Detail 1) (L277 to L279).

---

## 2. Emboss and relief

### 2a. Front-label EMB-01 (`mat_label`, emboss branch, L351 to L358, wired from L597)

- **Height source:** the MASK-EMB-01 image `Color` (Non-Color, Cubic) goes straight into Displacement Height (L353, L356). There is no blur, distance field, Map Range, smoothstep or step. The mask is binary with a 1 to 3 px AA edge.
- **Displacement node:** space `OBJECT` (L354), Midlevel **0.0**, Scale `EMB_H * MM` = **0.0002 m (0.20 mm)** (L355, with `EMB_H` at L45). Height 1 lifts the surface 0.2 mm along the normal; height 0 means no displacement.
- **Method:** `m.displacement_method = 'BOTH'` (L358). This is true displacement plus bump from the displacement shader.
- **Dicing:** Subdivision modifier `emboss_dice` is added after Solidify (L603 to L605). Settings: `SIMPLE`, `levels = 0` (viewport), `render_levels = 1`, `use_adaptive_subdivision = True`, `adaptive_space = 'PIXEL'`, `adaptive_pixel_size = 1.0`.
- **Not set:** the script does not set `cycles.feature_set`, `cycles.dicing_rate`, `cycles.offscreen_dicing_scale`, `cycles.max_subdivisions` or a dicing camera, so defaults apply.
- **Base mesh:** a 0.5 x 0.5 mm grid in developed (s, v) space (L588 to L589), clipped to the die by marching squares.

**Inferred profile:**
- The plateau is flat at +0.2 mm and meets the flat paper through a wall only as wide as the mask AA plus cubic-filter spread: about 1 to 3 texels plus about 1 texel, so roughly 0.05 to 0.2 mm.
- That makes the wall slope about 45° to 75°. The profile is a **hard step (mesa)** with no rounded shoulder or bevelled die wall.
- The macro render agrees: AVANTE letters show a crisp dark wall line on their lower and left edges (`renders/v004_foil_macro.png`).

**Micro-noise on the foil top:**
- Yes. The foil BSDF normal (L342 to L343) is the felt-plus-fibre fBM bump at 0.5x paper amplitude, applied on top of the displaced plateau.
- The roughness is also modulated at a 1.25 mm scale (L340 to L341).
- Both patterns are smooth, low-frequency (1.2 mm, 0.6 mm and 0.3 mm octaves) and isotropic in the front plane. A metal at roughness about 0.18 shows slope variation of this kind as lumpy, hammered or crumpled highlights.
- The render matches. The AVANTE letterforms show blotchy light and dark patches at about 1 to 2 mm across every glyph. The roundel foil, which has no bump, shows clean smooth gradients (`renders/v004_roundel_macro.png`).
- Estimate (not measured): a ±3 to 4 µm height over a 0.3 to 0.6 mm half-wavelength gives normal tilts of about 1° per octave. With three octaves summed, reflected-ray deviations are about 2° to 4°.

### 2b. Roundel stamped relief (`mat_roundel`, L395 to L398)

- Height = the same MASK-FOIL-01 `Color` used for the foil mix (no separate emboss mask and no blur).
- Displacement space OBJECT, Midlevel 0.0, Scale `ROUNDEL_RELIEF * MM` = **0.00004 m (0.04 mm)** (L46, L396). Method `BOTH` (L398).
- Dicing: `relief_dice` Subdivision with the same settings as the wrap: SIMPLE, levels 0, render_levels 1, adaptive, PIXEL, 1.0 (L675 to L676).
- Base mesh: a 128-segment by 24-ring disc. Ring spacing is about 0.97 mm; the outer circumferential edge is about 1.15 mm (L654).
- Profile: the same hard step, 0.04 mm high.

### 2c. Paper and collar relief

- Collar (`mat_label` with no `emb`): no displacement, no subdivision modifier. All relief there is the felt and fibre bump only.

---

## 3. Paper and label

### 3a. Paper BSDF (`mat_label`, L316 to L337)

| Element | Value | Line |
|---|---|---|
| Felt | Noise Scale 833 (about 1.2 mm), Detail 2, Roughness 0.5 (default), Distortion 0, Object coords; height x 4.5e-5 m | L317, L318 |
| Fibre | Noise Scale 1.0 behind Mapping Scale (4000, 800, 4000): features 0.25 mm in X and Z, 1.25 mm in **Y**; height x 1.2e-5 m | L317, L318 |
| Ink vs bare relief | Height x (0.7 + 0.3 x bare), so ink areas get 0.7x relief | L329, L331 |
| Bump | Strength 1.0, Distance 1.0 (heights are true metres) | L330 to L331 |
| Ink/bare split | RGBToBW(colour map) then Map Range From 0.30 to 0.60 (linear luminance, clamped) gives `bare` (1 = cream knock-out) | L320 to L323 |
| Roughness | Mix Float: Factor `bare`; A = ink 0.52 + 0.12 x Noise(Scale 300, about 3.3 mm, Detail 3), about 0.58 ± 0.06; B = bare 0.78 | L325 to L328 |
| Ink density | Bright/Contrast with Bright = (Noise(1500, about 0.67 mm) − 0.5) x 0.06, an **additive** offset of up to ±0.03 on linear colour | L333 to L335 |
| Principled | Base = density-modulated colour map; Sheen Weight 0.08 (Sheen Roughness default 0.5); Specular IOR Level 0.5 and IOR 1.5 defaults; Coat from the UV mask (front only), Coat Roughness 0.08 | L336 to L337, L349 to L350 |
| Reverse side | `back_white=True` for the wrap only. When Geometry Position · Normal < 0, the BSDF switches to Principled (0.86, 0.83, 0.76), Roughness 0.85. | L360 to L366, L597 |
| Cut edge | `M_SUB-01_CutEdge`: Principled (0.90, 0.88, 0.82), Roughness 0.9, no bump, assigned to the Solidify rim | L370 to L371, L584, L645 |

### 3b. Geometry

- **Thickness:** `LABEL_T` = 0.10 mm (L44). Wrap: Solidify thickness 0.1 mm, offset +1, rim on, even offset (L582 to L583). Collar: the same thickness without even offset (L644).
- **Glass gap:** the wrap is built at a radial offset of **+0.03 mm** from the analytic glass section (L593, through `surf_xyz` L514 to L527). The offset is radial (horizontal), so the normal gap is smaller on the 49° shoulder segment.
- **Outer face:** 0.13 mm off the glass.
- **Edges:** die line from the marching-squares clip of the 0.5 mm grid with linear edge interpolation (L548 to L573). The cut edge is a square 90° wall 0.1 mm high. Auto-smooth is 30° (L585). There is no edge rounding, lift or adhesive modelling.
- **Back face:** the inner Solidify face uses the same material, UVs and displacement as the front. It shows `back_white` paper when seen through the bottle.
- **Artwork resolution:** 20 px/mm (508 ppi) for the front and neck, 25.15 px/mm (639 ppi) for the roundel. See the tables at the top for texel-to-pixel ratios.

---

## 4. Roundel and collar flag

### 4a. Roundel `M_LBL-ROUNDEL-01_ClearFilm` (L373 to L399) and geometry (L650 to L677)

| Element | Value | Line |
|---|---|---|
| Ink | Principled, Base = COLOR map, Roughness 0.5, no bump | L378 to L379 |
| Foil | See 1b | L380 to L384 |
| Print/film split | UV radius < `ROUNDEL_PRINT_R / ROUNDEL_TEX` = 21.855 / 47.706 = 0.4581: inside is ink/foil (opaque), outside is film | L386 to L392 |
| Film | Principled Roughness 0.04, IOR 1.49, Transmission Weight 1.0, **Base Color left at the default 0.8 grey** | L385 |
| Relief | See 2b | L395 to L398 |
| Mesh | Disc Ø46.706 mm, centre z 42.2 mm, x −0.43 mm; follows the tapered face at `−(width_at(z)/2) − 0.12 mm`; planar UVs (0.5 + x/47.706, 0.5 + z/47.706) | L652 to L659 |
| Film thickness | Solidify 0.05 mm, offset +1, rim on, no rim material (rim uses the film part of the material) | L673 |
| Glass gap | 0.12 mm; the outer face sits about 0.17 mm off the glass | L652 |
| Print model | Clear film is not layered over the ink. The print disc is an opaque BSDF with no film or gloss on top, and there is no white underprint layer. | — |

### 4b. Collar flag `LBL-NECK-01_Collar` (L609 to L647), material `M_LBL-NECK-01_SUB-01_Paper` (L639)

- **Material:** `mat_label` with the neck colour and foil masks only. No emboss, no UV coat, no `back_white`. The foil is as in 1a, with the felt bump at 0.5x.
- **Cylinder:** radius `rc` = 17.05 + 0.06 + 0.14 = 17.25 mm (L610). 160 segments (about 0.68 mm each) and 9 z rows (about 1.75 mm each) (L615 to L621). UVs come from the developed collar artwork (L612 to L613).
- **Flag plies:** two plies at y = ∓0.12 mm, radial at +X, clipped to a stadium die with a 48 x 28 grid (about 0.5 mm) (L627 to L637). Each ply is solidified 0.1 mm with offset +1 (L644).
- **Ply normals:** `recalc_normals` is not called on the collar. From the winding, the clipped grid normal is −Y; the back ply keeps it and the front ply is reversed.
- **Inferred ply build-up:** each ply grows toward the mid-plane, giving a flag about 0.24 mm thick with an inner air gap of about 0.04 mm. Verify this in the .blend.
- **Rim:** the cut-edge material (L645).

### 4c. Capsule (context)

- Navy: Principled NAVY (#003653 converted to linear), Roughness 0.34, Coat Weight 0.2, Coat Roughness 0.18 (L485). Solidify 0.05 mm (L491).
- Pleats: geometric, amplitude 0.075 mm x up to 1.5, with 34 and 57 cycles around 256 ring vertices (L464 to L465).
- Back seam: raised 0.06 mm (L467 to L468).

---

## 5. Lighting and camera

All positions are in metres, world space. The bottle axis is (0, 0, z) with the base at z = 0; the label front faces −Y. The lights aim at `tgt` = (0, 0, 0.12) (L740). Light colours are default white.

| Object | Type and size | Power or strength | Position | Visibility | Line |
|---|---|---|---|---|---|
| LGT_Key_Softbox | Area RECT 0.9 x 1.2 m | 10.5 W | (−0.72, −0.42, 0.42), about 0.89 m, camera-left, front, high | default | L742 |
| LGT_Rim_L_Strip | Area RECT 0.05 x 0.8 | 3.2 W | (−0.30, 0.08, 0.13), about 0.31 m | default | L743 |
| LGT_Rim_R_Strip | Area RECT 0.05 x 0.8 | 3.2 W | (0.30, 0.08, 0.13) | default | L744 |
| LGT_Top | Area RECT, size 0.6, **size_y not set** | 0.45 W | (0.05, −0.05, 0.65) | default | L745 |
| LGT_Fill_Low | Area RECT, size 0.5, **size_y not set** | 0.5 W | (0.55, −0.55, 0.08) | default | L746 |
| FLG_Black_L / R | Planes 0.38 x 0.6, re-rotated to YZ planes at x = ±0.16, spanning y 0.08 to 0.46 and z −0.05 to 0.55 | Principled 0.003 black, Roughness 0.9 | (±0.16, 0.27, 0.25) | camera off, diffuse off, **shadow off** | L748 to L750, L695 to L696 |
| CRD_Brandy_Back | Emissive plane 0.15 x 0.14; spherical gradient ^0.55 | Strength 1.7, colour (1.0, 0.93, 0.82) | (0, 0.085, 0.092), parented to RIG_BackCard (LOCKED_TRACK to the active camera) | camera, diffuse and shadow off | L752 to L755, L690 to L712 |
| CRD_Foil_Specular | Emissive plane 1.1 x 0.42; spherical gradient ^0.55 | Strength 0.95, colour (1.0, 0.97, 0.92) | (0, −0.55, 0.075), facing (0, 0, 0.13); between CAM_Hero and the bottle | camera, diffuse and shadow off | L756 |
| World | Background (0.02, 0.02, 0.022), strength 1.0 | | | | L738 to L739 |
| ENV_Sweep | Floor y −0.6 to 0.25 at z 0, 0.25 m cove, wall at y 0.5 to z 1.2, width 1.6 m | Principled (0.016, 0.0155, 0.015), Roughness 0.62, Specular IOR Level 0.3 | | | L724 to L736 |

| Camera | Location | Lens | Target | Focus | f-stop | Line |
|---|---|---|---|---|---|---|
| CAM_Hero | (0, −0.74, 0.13) | 85 | (0, 0, 0.119) | DoF off | — | L759 |
| CAM_ThreeQuarter | (0.42, −0.6, 0.16) | 85 | (0, 0, 0.119) | off | — | L760 |
| CAM_Macro_Avante | (0, −0.28, 0.137) | 100 | (0, 0, 0.137) | 0.235 m | 16 | L761 |
| CAM_Macro_Roundel | (0, −0.28, 0.0422) | 100 | (0, 0, 0.0422) | 0.242 m | 8 | L762 |
| CAM_Macro_CollarFlag | (0.06, −0.2, 0.216) | 100 | (0.027, 0, 0.2075) | 0.205 m | 11 | L763 |
| CAM_Turntable | (0, −0.8, 0.03) relative to the rig at z 0.119; 120 frames, linear | 85 | rig | off | — | L769 to L779 |
| qc: hero, threequarter | same as build | 85 | | off | | qc:L11 to L12 |
| qc: base / paper / neck / roundel / liquid | see qc:L13 to L17 | 100 | | 0.285 / 0.168 / 0.262 / 0.242 / 0.185 | all f/11 (the roundel is f/8 in the build) | qc:L13 to L17 |

- **Sensor:** not set, so 36 mm with fit AUTO. Clip start is not set (default 0.1 m), which is below every camera distance.
- **Computed DoF** (CoC 0.03 mm): Macro_Avante f/16 about 3.0 mm; Macro_Roundel f/8 about 1.5 mm; Macro_CollarFlag f/11 about 1.4 mm. The flag spans about 3.9 mm in depth because it is about 9° off-normal.
- **Render (L782 to L795):**
  - Cycles, 128 samples by default (CLI `--samples` at L829); OIDN denoise on (input passes and prefilter at defaults).
  - Bounces: max 32, transmission 24, glossy 12, transparent 24, volume 4; diffuse at the default 4.
  - Caustics: reflective off and refractive off.
  - `blur_glossy` 0.2, adaptive threshold 0.005, indirect clamp 10; direct clamp and light threshold at defaults (0 and 0.01).
  - Resolution 1000x1600 by default; macros use `--res`.
- **Colour management:** AgX, Look None; exposure, gamma and display at defaults.
- **Device:** the build uses CPU unless `--gpu` (METAL, L825 to L828). The QC script always forces GPU METAL (qc:L21 to L23).

---

## 6. Parameter table

| Parameter | Current value | file:line |
|---|---|---|
| FOIL_F0 (foil base colour) | (0.95, 0.69, 0.33, 1) linear | build:269 |
| Foil Metallic (paper / film) | 1.0 / 1.0 | build:339 / 380 |
| Foil roughness base + noise amp | 0.14 + 0.08·N | build:341, 382 |
| Foil roughness noise scale, detail | 800 (1.25 mm), 2 | build:340, 381 |
| Foil Specular Tint (F82) | default white (unset) | build:339, 380 |
| Foil bump height multiplier | relief x 0.5 | build:343 |
| Foil bump Strength / Distance | 1.0 / 1.0 | build:342 |
| Foil mask source and interpolation | MASK-FOIL-01 Color, Cubic, CLIP | build:315, 261, 345 |
| Felt noise scale / detail / height | 833 / 2 / 4.5e-5 m | build:317, 318 |
| Fibre noise scale / stretch / height | 1.0 / (4000, 800, 4000) / 1.2e-5 m | build:317, 318 |
| Paper bump Strength / Distance | 1.0 / 1.0 | build:330 |
| Ink relief factor | 0.7 + 0.3·bare | build:329 |
| Ink/bare luminance window | 0.30 to 0.60 | build:321 |
| Ink roughness | 0.52 + 0.12·N(300, d3) | build:325, 326 |
| Bare paper roughness | 0.78 | build:328 |
| Ink density noise | N(1500) additive ±0.03 | build:333, 335 |
| Paper Sheen Weight | 0.08 | build:336 |
| UV coat roughness | 0.08 | build:350 |
| Paper reverse colour / roughness | (0.86, 0.83, 0.76) / 0.85 | build:364 |
| Cut-edge colour / roughness | (0.90, 0.88, 0.82) / 0.9 | build:371 |
| EMB_H (emboss height) | 0.20 mm | build:45, 355 |
| Emboss Midlevel / space | 0.0 / OBJECT | build:354, 355 |
| Emboss height source | raw MASK-EMB-01, no blur | build:353, 356 |
| Displacement method (wrap / roundel) | BOTH / BOTH | build:358 / 398 |
| Wrap subdiv: type, levels, render levels | SIMPLE, 0, 1 | build:603, 604 |
| Adaptive subdiv, space, pixel size | True, PIXEL, 1.0 | build:605 |
| Wrap base grid | 0.5 mm (s) x 0.5 mm (v) | build:588, 589 |
| LABEL_T | 0.10 mm | build:44, 582, 644 |
| Wrap glass offset | 0.03 mm radial | build:593 |
| Solidify offset / rim / even (wrap) | 1.0 / True / True | build:582, 583 |
| Label auto-smooth | 30° | build:585, 646, 674 |
| ROUNDEL_RELIEF | 0.04 mm | build:46, 396 |
| Roundel ink roughness | 0.5 | build:378 |
| Roundel film rough / IOR / transmission / base colour | 0.04 / 1.49 / 1.0 / default 0.8 | build:385 |
| Roundel print radius threshold | 0.4581 (UV) | build:389 |
| Roundel glass offset / film thickness | 0.12 mm / 0.05 mm | build:652 / 673 |
| Roundel mesh density | 128 seg x 24 rings | build:654 |
| Roundel subdiv | SIMPLE, 0, 1, adaptive PIXEL 1.0 | build:675, 676 |
| Collar radius rc | 17.25 mm | build:610 |
| Collar ply offset | ±0.12 mm | build:633 |
| Collar cylinder segments / rows | 160 / 9 | build:617 / 615 |
| Capsule navy rough / coat / coat rough | 0.34 / 0.2 / 0.18 | build:485 |
| Pinline gold Metallic / rough | 0.85 / 0.28 | build:486 |
| Capsule pleat amplitude | 0.075 mm (x up to 1.5) | build:465 |
| Glass IOR / absorption density / colour | 1.52 / 10 / (0.90, 0.97, 0.93) | build:273, 275 |
| Glass waviness noise / bump distance | 28 / 0.00012 | build:277, 278 |
| Brandy IOR / density / colour | 1.355 / 95 / (0.9, 0.7, 0.2) | build:285, 287, 288 |
| Key softbox size / W / position | 0.9 x 1.2 / 10.5 / (−0.72, −0.42, 0.42) | build:742 |
| Rim strips size / W / position | 0.05 x 0.8 / 3.2 / (±0.30, 0.08, 0.13) | build:743, 744 |
| Top light | 0.6 x default / 0.45 W / (0.05, −0.05, 0.65) | build:745 |
| Fill low | 0.5 x default / 0.5 W / (0.55, −0.55, 0.08) | build:746 |
| Black flags position / size / shadow | (±0.16, 0.27, 0.25) / 0.38 x 0.6 / off | build:749, 750 |
| Back card size / strength / colour / position | 0.15 x 0.14 / 1.7 / (1, 0.93, 0.82) / (0, 0.085, 0.092) | build:753 |
| Foil card size / strength / colour / position | 1.1 x 0.42 / 0.95 / (1, 0.97, 0.92) / (0, −0.55, 0.075) | build:756 |
| Card falloff exponent | 0.55 (spherical gradient) | build:705 |
| World colour / strength | (0.02, 0.02, 0.022) / 1.0 | build:739 |
| Sweep colour / rough / spec | (0.016, 0.0155, 0.015) / 0.62 / 0.3 | build:734 |
| Macro cameras lens / focus / f-stop | 100 / see §5 / 16, 8, 11 | build:761 to 763 |
| QC macro f-stop | 11 (all) | qc:13 to 17 |
| Samples / denoiser | 128 / OIDN | build:782, 785 |
| Bounces max / trans / gloss / transp / vol | 32 / 24 / 12 / 24 / 4 | build:786, 787 |
| Caustics reflective / refractive | off / off | build:788 |
| Blur glossy / adaptive threshold / indirect clamp | 0.2 / 0.005 / 10 | build:789 |
| View transform / look | AgX / None | build:793, 794 |
| Texture resolution, front / neck / roundel | 4870x2026 / 3174x360 / 1200x1200 (20 / 20 / 25.15 px/mm) | textures/ |

---

## 7. Bugs and suspicious items

Severity is my estimate. "Verify" means the item was derived from code or defaults and not confirmed in the .blend.

1. **Felt/fibre bump on the foil is the likely source of the "crumpled" foil (high).** L342 to L343 apply 0.5x the paper's 1.2 mm fBM height (three octaves) to the metal normal, and L340 to L341 add 1.25 mm roughness blotches. Real hot-foil on a flat-die plateau is near-mirror. The v004 AVANTE macro shows lumpy highlights; the bump-free roundel foil does not.
2. **The emboss is a hard mesa (medium to high).** The raw binary mask goes into the 0.2 mm displacement (L353 to L356), with no blur or bevel profile. The wall width is set only by the 1 to 3 px AA plus the cubic filter, about 0.05 to 0.2 mm. The roundel's 0.04 mm relief has the same issue (L397).
3. **Displacement applies to the inner Solidify face too (high, verify).** The wrap's inner face (toward the glass) has the same material and UVs. With method BOTH it is displaced 0.2 mm along its own normal, which points into the glass. The glass gap is only 0.03 mm (L593), so embossed areas push about 0.17 mm into the glass, and the paper becomes 0.3 mm thick there instead of debossing on the back. The roundel does the same with 0.04 mm into a 0.12 mm gap: no intersection, but the film doubles in thickness.
4. **The texture is under-resolved for the macros (medium).** At 20 px/mm the front and neck artwork are magnified 1.18x (Macro_Avante) and 1.39x (Macro_CollarFlag). Foil and emboss edges are therefore defined at about 1.2 to 1.4 render px per texel, and Cubic interpolation adds more softening. The roundel (25.15 px/mm) is adequate.
5. **The roundel film has a grey tint (high).** Base Color is left at the default 0.8 with Transmission 1.0 (L385). Transmitted light is multiplied by 0.8 at each surface, about 0.64 through both film faces. The clear ring outside the print disc reads darker than the surrounding liquid in `v004_roundel_macro.png`. The glass and brandy set Base Color to 1.0 (L273, L285); the film does not.
6. **The fibre stretch axis is wrong for the front panel (medium).** The Mapping Scale (4000, 800, 4000) at L317 stretches along object **Y**, the depth axis for the front face (normal −Y). Fibres are therefore isotropic 0.25 mm specks on the front and back, and appear as streaks only on the side panels (YZ plane).
7. **The felt is a smooth fBM, not a pecked felt (low to medium).** There is no Distortion and no contrast ramp (Agent 3 proposed both). Its 1.2 mm scale also equals the foil roughness noise scale (800), so the two blotch patterns reinforce each other.
8. **Ink density offset is additive (medium).** Bright/Contrast Bright of ±0.03 on linear colour (L335) is large next to navy (linear about 0.00, 0.037, 0.087): up to about ±35% on the blue channel, and it lifts red from 0. The comment says ±3%.
9. **The capsule cuts through the collar (medium).** The comment "clears the capsule pleats" (L610) is false. Evaluated from the script maths:
   - Capsule outer surface, including the 0.05 mm film: up to **17.32 mm** across the collar height, against collar rc 17.25 mm.
   - At the collar top (z 214.4 mm) the capsule reaches **17.56 mm**, because `capsule_profile` smoothing picks up the bar-top head step. That is about 0.3 mm of interpenetration.
   - Pleat troughs go down to 17.00 mm, below the glass neck surface at 17.05 mm, so the capsule dips into the glass.
10. **The black flags cannot block light (medium).** `visible_shadow = False` (L750, and L700 for cards) means FLG_Black_L/R do not stop rim spill on the backdrop, contrary to the comment at L747. With diffuse also off (L696), they only act as black in glossy and transmission rays.
11. **LGT_Top and LGT_Fill_Low have an unset size_y (low, verify).** Shape RECTANGLE with only `size` set (L745 to L746), so `size_y` stays at the datablock default, probably 0.25 m. They are 0.6 x 0.25 and 0.5 x 0.25, not square.
12. **Adaptive subdivision gating (verify).** The script never sets `cycles.feature_set`. If the running build still needs Experimental for adaptive dicing, or if `render_levels = 1` caps it, the wrap displaces only to about a 0.25 mm grid. The roundel would displace only to about 0.5 to 1 mm, which turns the step into jagged ramps. Check the evaluated mesh, or a wireframe render, in the .blend.
13. **Possible double shading at the emboss walls with BOTH (low, verify).** With 1 px dicing, method BOTH adds displacement bump on top of the already-displaced geometry, and the felt bump is layered on top of that. Compare with `DISPLACEMENT` only to rule out over-darkened walls.
14. **Collar ply gap and thickness (low, verify).** No `recalc_normals` on the collar. From the winding, the plies grow toward each other, leaving a 0.04 mm gap and a flag about 0.24 mm thick, about 2.4x the paper thickness. The collar Solidify also lacks `use_even_offset` (L644).
15. **Die corners are chamfered (low).** The marching-squares clip on a 0.5 mm grid (L588 to L589) bevels sharp convex trim corners by up to about 0.5 mm, for example the TRIM vertices at (±119.4, 14.429) and (±106.749, 86.63).
16. **Pinline Metallic 0.85 (low).** L486 mixes about 15% dielectric diffuse into the "gold ink" metal.
17. **Capsule pleat sampling (low).** The 57-cycle pleat term (L464) on 256 ring vertices is about 4.5 vertices per wavelength, close to Nyquist, so it can look faceted.
18. **Denoiser and micro-detail (low).** OIDN at the default 128 samples can smooth the ±µm felt bump and foil micro-variation in macros. Agent 6 V1 notes the albedo/normal risk.
19. **Documentation drift (info).**
    - README "Known limitations" still says "Emboss is a bump map", and its table cites 4.5 mm walls and a 14.4 mm base. The code has `WALL = 3.6` and a solved base of 20.6 mm.
    - Agent 6's "Current" values (key 7.5 W, rims 5 W at ±0.38, back card 0.11 x 0.2 at strength 2.6, foil card 1.25, Blur Glossy 0.5, Macro f/8) no longer match the code: 10.5 W, 3.2 W at ±0.30, 0.15 x 0.14 at 1.7, 0.95, 0.2, f/16.
    - The README says the build was tested on Blender 5.2.3; the brief says Cycles 5.1.
20. **Silent socket drop (info).** `principled()` ignores unknown keys (L254), so any renamed Principled input in a future build is skipped without an error.

### Reference context (what v004 is being compared against)

- **Foil:** ref01, ref02, ref09, ref11, ref12 and ref13 show embossed or debossed foil with bevelled, rounded die walls. ref12 shows a deliberate fine linear micro-texture on the foil. Plateaus are mostly smooth mirror with sweeping gradient highlights.
- **Paper:** ref02, ref03, ref05 and ref13 show a fine, high-frequency felt or fibre tooth, finer than 1 mm and contrasty under raking light. ref08 shows a woven/linen emboss.
- **Roundels and medallions:** ref06, ref10 and ref11 show raised medallions with multi-level relief.
- **Collar flag:** ref05 shows a die-cut collar flag with visible paper tooth.
