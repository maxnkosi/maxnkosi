# Avante Brandy — Blender master scene (v009)

Concept 1 rev D packaging on the 750 ml Imperial bottle, built procedurally from the
Figma/Notion handoff (Figma file `JcxeRDhCrtgZUXhTWQn2hV`, pages 01–03).

## Open it

1. Open `avante_master_v004.blend` (v001, v002 and the v003 checkpoint kept for reference) in Blender 4.2+ (built and tested with Blender 5.2.3 LTS).
2. Or rebuild from source: **Scripting** tab → **Open** `build_avante_master.py` → **Run Script**.
   The `textures/` folder must stay next to the script.
3. Cameras: `CAM_Hero`, `CAM_ThreeQuarter`, `CAM_Macro_Avante`. Render engine: Cycles.

Headless:

```bash
blender -b -P build_avante_master.py -- --render out.png --camera CAM_Hero --samples 256 --res 2000x3200
```

## What is in the scene

| Object | ID | Notes |
| --- | --- | --- |
| `GLS-01_Glass` | GLS-01 | 750 ml Imperial (flint, 226.9 mm). Chamfered-square body lofted to a Ø34.1 neck; 4.5 mm walls; base solved to **14.4 mm** so the inner volume to the fill line = **750.0 ml** |
| `LIQ-01_Brandy` | LIQ-01 | Fill 66 mm below glass top (supplier). IOR 1.36, amber volume absorption (proposal; calibrate) |
| `SLV-CAP-01_Capsule` | SLV-CAP-01 | Closed-top navy shrink capsule to 66.3 mm from cap top; gold pinline (MET-01) 64.9–66.3 mm |
| `LBL-NECK-01_Collar` | LBL-NECK-01 | Collar 23.7–37.6 mm from cap top; radial flag at 3 o'clock, roundel on both plies |
| `LBL-FRONT-01_Wrap` | LBL-FRONT-01 | Wrap over front + bevels + sides (back clear); UVs = developed dieline (page 01 § L) |
| `LBL-ROUNDEL-01_Roundel` | LBL-ROUNDEL-01 | Clear-film die Ø46.7, printed disc Ø43.7, centre 195.9 mm from cap top |

Materials are named by ID (`M_LBL-FRONT-01_SUB-01_Paper`, `M_FOIL…`, etc.). Foil, emboss and
spot-UV are driven by the black/white masks in `textures/` (exported from Figma page 03).

## Acceptance checks

`python check_avante_master.py` (with the `bpy` module) or run it inside Blender — v001 and v002 result: **ALL PASS (11/11)**
(glass 226.9 mm, overall 238.1 mm, max width 89.0 mm, capsule 66.27 mm, wrap crown 79.6 mm,
collar 23.66–37.64 mm, roundel centre 195.9 mm, inner volume 750.0 ml).

## v002 changes

- Wrap and collar flags are now cut to the exact die shape (marching-squares clip of the developed
  dieline) with real 0.10 mm paper thickness (Solidify with rim) — no alpha-cut edges.
- Glass vertical edges softened (≈R1–2 mm), so the wrap rolls smoothly over the bevels.
- FOIL-01: warm pale-gold reflectance, roughness 0.18, plus a specular card light so the foil reads metallic.
- Brandy absorption deepened; meniscus (≈1.3 mm climb at the glass wall).

## Known limitations / proposals (P)

- Bottle shape is photo-derived at the supplier height (±0.7 mm). Shoulder angle, bevel width,
  neck Ø, cap Ø and wall thickness are proposals until measured on a real bottle.
- Emboss is a bump map (≈0.2 mm), not true displacement — needs adaptive subdivision for extreme macro.
- A small residual step remains where the wrap crown crosses from the shoulder onto the bevel corners.
- Brandy colour, light levels and foil roughness are first-pass values for look development.
- No glass mould seams; brandy colour still to be calibrated against product photography.

## v003 / v004 changes

`avante_master_v003.blend` is a checkpoint (brandy calibration only). `avante_master_v004.blend` is current.

- Wrap development fixed: 1.02 mm jump at the fold and v=0 removed; front art now on the rev D datum (wrap bottom 165.87 mm, spec 165.9).
- Glass: monotone-cubic profile, finer rings, 12 mm inner heel fillet, 3.5 mm punt, base 20.6 mm, wall 3.6 mm, still 750 ml.
- Liquid overlaps glass by 0.05 mm (no air film), IOR 1.355, 1.8 mm meniscus.
- Paper: felt and fibre relief, separate ink and bare-paper response, cut-edge material, paper reverse visible through the back.
- Capsule: film bridges steps, geometric pleats, 2 mm back seam, lower gloss.
- Foil: true 0.2 mm emboss via adaptive subdivision, foil micro-roughness. Roundel: conforming mesh, 0.05 mm film, 0.04 mm stamped-foil relief.
- Studio: off-axis key, strip rims, flags, camera-invisible back and foil cards, AgX with no look, CAM_Turntable (120 frames), roundel and flag macro cameras.

`qc_render.py` renders the fixed comparison cameras into `renders/qc/`. Specialist reports are in `research/`; most numeric values there are artistic, as each report states.

## v005 changes (3 Nov 2026)

`avante_master_v005.blend` is current; v001–v004 are untouched. Based on the reference study in
`research/v005_study/` (`00_SYNTHESIS.md`). Rebuild order: `prep_v005_textures.py`, then `build_avante_master.py`.
Finals: `render_finals.py -- v005 512` (aims the camera-dependent cards for each camera).

Client decisions applied: dyed-through navy stock (navy cut edge and reverse), 0.15 mm label,
bird/spear graphic toned down to dL* 7 above the navy (#286789 to #0E4765, render-side texture
`COLOR__LBL-FRONT-01_v005.png`; Figma artwork untouched), angled macro cameras added, roundel keeps raised 0.04 mm foil.

- Foil: paper felt bump removed from the foil (the v004 "crumple"); rare 3 um pits plus 2 um grain at 0.13 mm;
  roughness 0.07 ± 0.015; glossy blur 0.
- Foil lighting: the 1.1 × 0.42 m flat card is replaced by narrow gradient strips placed in the mirror direction of
  the active camera (allowing for the 4° face taper), light-linked to the labels; a second small strip for the
  roundel stands on the table when its mirror points into the floor. World near-black (0.003).
- Emboss: rounded 16-bit height map (`HEIGHT-EMB-01__LBL-FRONT-01.exr`, 40 px/mm, 0.15 mm Gaussian shoulder,
  foil edge at the foot, thin strokes lower) instead of a hard-stepped 8-bit mask.
- Paper: sheen 0, specular 0.32, felt pecks 0.6 mm at 30 um, body 10 um, fibres along the sheet in label-UV mm
  (v004 fibres ran into the front panel); multiplicative 6 mm mottle ±3 % (v004 additive, about ±30 % on navy).
- Label: 0.15 mm, 0.005 mm from the glass, 0.025 mm bevelled cut edge, wetted navy reverse on the glass side with
  no displacement (v004 displaced the reverse too). Collar plies glued back to back with a 0.6 mm tip curl.
- Fixes: roundel film base colour white (v004 grey ring); collar radius now clears the pleated capsule
  (17.25 → 17.64 mm); LGT_Top and LGT_Fill_Low square as intended. Black flags keep shadows off (with shadows on
  they threw a hard edge across the backdrop) — they act only in reflection.
- Liquid: back card enlarged to 0.17 × 0.24 m, strength 1.25, less orange.
- Cameras: `CAM_Angle_Avante` (135 mm, 25° roll), `CAM_Angle_Roundel` (135 mm, −20°), `CAM_Angle_CollarFlag`
  (100 mm, 15°). Each camera carries `foil_aim_z`.
- Not done: macro artwork re-export at about 50 px/mm (still 20 px/mm), AgX contrast look (kept "None").

## v006 changes (3 Nov 2026) — arched shoulder

`avante_master_v006.blend` is current; v001–v005 are untouched. From the client bottle references
(Figma `56:35`, kept local only): the real bottle's shoulder is a revolved dome cutting the square
body, so each flat face ends in an **arch** (high at the panel centre, carved down at the corners).
v001–v005 shrank the square section with height, giving a pyramid with a straight horizontal crease.

- Section = soft-min of the body square (held at 88.9 mm above 152.5 mm) and a dome radius `shoulder_R(z)`
  (`dome_cut`, 1.2 mm fillet). The dome follows the measured front silhouette above 157.5 mm and eases out
  (monotone Hermite) to clear the corners: corners start carving at about 140 mm, panel centre at about
  151 mm, a ~12 mm arch, close to the rev D wrap crown's ~16 mm drop. Arch heights are read from the photos
  and the crown (A), not measured.
- Applied to the outer glass, inner wall (inset 3.6 mm), liquid, wrap surface and capsule. Neck finish
  rounding now only above 182 mm.
- Base re-solved 20.6 → 17.8 mm to hold 750.0 ml. 11/11 checks pass.
- Renders: `v006_hero`, `v006_threequarter`, `v006_foil_macro`, `v006_angle_avante`,
  `v006_glass_only_threequarter`; other v005 shots unaffected by the shoulder and not re-rendered.

## v007 changes (3 Nov 2026) — reference-true Imperial glass

`avante_master_v007.blend` is current; v001–v006 are untouched. v006's shoulder was rejected by the client
(uneven surface, low shoulders, label placement, over-bevelled edges). Multi-agent study, critics and judge's
ruling: `research/v006_study/` (`G_judge_ruling.md`). Glass now lives in `glass_v007.py`, installed by the
builder (`GLASS_MODEL = 'v007'`; `'legacy'` keeps the v006 dome for comparison).

- Shoulder: straight cone R = 40.16 − 1.287 (z − 160) (52° from vertical, fitted to PROFILE 160–172.5) cut by the
  chamfered square, exact rolling-ball fillet ρ 7 (inner 8); neck fillet 20.5. Arch crease 156.6 centre / 145.9
  corner (rise 10.7), visible onset 154.05 / 143.15. Square held above 147.5 (no break). PROFILE 140 → 88.1 (raw2).
- ρ: the ruling chose 4 on a reported 0.58 mm silhouette deviation; re-measured, ρ 4 deviates 1.25 mm at the
  knuckle and only ρ 7 meets the 0.7 mm tolerance (0.58), matching raw2's soft centre knuckle.
- Vertical edges R ≈ 1.0 (soft-min k 0.125, stable form), ramping to k 0.7 over 10 mm under the crease so each
  chamfer cap blends without a dimple. Chamfer width unchanged (0.0754).
- Heel: flat 32° bevel from z 8.5, footprint half-width 30.6, R 1 breaks. Flat inner floor (PUNT_H 0), inner heel R 5,
  wall offset along the normal (true 3.6 mm on the cone), bore blended over 181–189. Base re-solves to 20.0 mm for
  750.0 ml (raw2 suggests ≈17.4 — unresolved, no supplier drawing).
- Mesh: 776 angles per ring clustered at the edge vertices, rows following the arch (0.15 mm in the band), plain
  smooth shading. Glass ≈ 680k vertices (≈ 4× v006).
- Label kept exactly as approved (rev D die, datums 79.63 / 165.87, artwork). Perimeter by arc length on the filleted
  section; the label sits on the glass and its top crosses the arch onset by 4.4 mm (front centre) to 5.6 mm (fold).
  Reported as WARN W1 — **client decision pending**: rev D.2 die following the arch (crown ≈ 84.7 from cap) /
  keep and trial on real bottles / custom mould with a higher shoulder.
- Checks: 26 (11 original + 15 v007 shoulder checks) — ALL PASS; W1 warnings as above.
- New cameras: `CAM_Shoulder`, `CAM_Shoulder_34` (135 mm, level with the shoulder at z 155).

## v008 changes (3 Nov 2026) — client: close up the corner chamfer, label 3 mm down

`avante_master_v008.blend` is current; v001–v007 untouched.
- Corner chamfer leg 0.0754 → **0.050** of body width (6.7 → 4.5 mm; facet ≈ 6.3 mm), within the 0.045–0.055 W that
  studies A/D read on the references. The cone now meets the corners lower: crease 144.75 corner / 156.6 centre,
  rise 11.9 mm (raw2: 11.7 measured). Base re-solves to 21.0 mm for 750.0 ml.
- Wrap label moved **3 mm down** (`LABEL_DROP`): crown 82.63, bottom 168.87 from cap top (client instruction, supersedes
  79.64 / 165.9). Overlap past the arch onset falls to 1.4 mm (centre) / 2.9 mm (fold), still reported as W1.
- Wrap is now a true-length (isometric) wrap round the filleted section, so the art is not stretched to fit the
  narrower facets; the approved dieline's panel boundaries no longer coincide exactly with the glass corners.
- Checks: arch corner targets moved to the reference values for a 4–5 mm leg; datum checks follow `LABEL_DROP`.
  All 26 pass. New camera `CAM_Corner` (front-right chamfer close-up).

## v009 changes (3 Nov 2026) — rounded corners, rev D.2 die, label 6 mm lower

`avante_master_v009.blend` is current; v001–v008 untouched. Client instructions and decision:
- **Chamfer closed totally; vertical corners rounded** (`CHAMFER = 0`, `CORNER_R = 4.5` mm true radius; inner wall
  radius 0.9 = 4.5 − 3.6). The corner sits further out, so the cone meets it lower: crease 143.75 corner / 156.6
  centre, arch rise 12.9 mm (raw2, which has a chamfer, 11.7). Base re-solves to 21.7 mm for 750.0 ml.
- **Rev D.2 die (Route 1): the top edge follows the arch.** `revD2_trim(clearance=2.0)` replaces the dieline's top chain
  by min(approved edge, arch onset − 2 mm), so the label lies entirely on flat glass. Crown 86.05 mm from cap top;
  clearance 2.0 mm (centre) / 1.98 (corner). Artwork untouched; the spear tip clears the die edge by ~8 mm.
  `LABEL_MODE = 'approved'` restores the rev D die.
- **Label moved a further 3 mm down** (`LABEL_DROP = 6.0`): bottom 171.87 mm from cap top. The label bottom is now
  **0.67 mm** above the roundel film — reported as W2 (under 2 mm is tight for labelling tolerance).
- Checks: 29 (11 + 18), all pass; W2 warning. Arch-corner targets are now the geometry of the rounded corner (the
  references have a chamfer, so there is no reference value for them).
