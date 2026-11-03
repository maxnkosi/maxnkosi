# Avante Brandy — Blender master scene (v005)

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
