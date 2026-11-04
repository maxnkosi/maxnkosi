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

## Variants master v001 (3 Nov 2026) — Concepts 1, 5, 6, 7 and 10 in one studio

`avante_variants_master_v001.blend` holds all five bottles in **one scene and one shared studio**. It is built from
the approved v009 master, which is never re-saved (`build_variants_master.py` refuses to write over it).

    blender -b avante_master_v009.blend --python build_variants_master.py -- --save avante_variants_master_v001.blend
    blender -b avante_variants_master_v001.blend --python check_variants_master.py
    blender -b avante_variants_master_v001.blend --python render_variants.py -- variants_v001 [shot,names] [sample_scale]

**Hierarchy:**
- `AVANTE_VARIANTS_MASTER` contains `STUDIO_SHARED` (Floor, Background, Softboxes, Reflectors, Flags), `CAMERAS`
  (Lineup_Hero, Lineup_ThreeQuarter, Individual_Hero, Individual_ThreeQuarter, Material_Macros) and
  `CONCEPT_01/05/06/07/10`.
- Each concept has `Cxx_Bottle_Glass`, `Liquid`, `Closure`, `Labels`, `Emblems` and `Materials` collections, all
  parented to a `Cxx_ROOT` empty.

**What is shared and what isn't:**
- Glass, liquid and capsule are linked duplicates of the v009 meshes, so all five bottles are physically
  identical.
- Every label, print, emblem and label material is a per-concept copy. A check confirms that no label material or
  mesh is shared between concepts.

**Staging:** `variants_stage.py`, also stored in the .blend as a text block.
- `stage('single', 'C06', cam)` stands that concept on the v009 hero mark and hides the other four from render, so
  they cast no stray shadows or reflections. Lights, cards and cameras are the v009 rig, unchanged.
- `stage('lineup', None, cam)` stands all five on their lineup marks, 135 mm apart.
- Lineup-only extras: a floor apron, a 3x-wide copy of the sweep, a wide foil strip and a back card behind each
  bottle.

**Concept 1 is v009 unchanged:**
- Its mesh, transform, material and modifier signatures are identical to v009.
- Its hero render matches v009 to within noise (mean |Δ| 7e-6).

**Concepts 5, 6, 7 and 10** are built by `variants_concepts.py` and `variants_kit.py` from the Figma layer exports
in `textures/variants_src/` (nodes 4:3, 4:305, 4:187 and 4:227).
- **Artwork:** composited 1:1 into `textures/variants/`, never redrawn. The exports arrive flattened on white, so
  alpha is recovered from each layer's single ink colour. The medallion ring strokes, lost in the flattened
  export, are redrawn to the measured radii.
- **Placement:** one uniform scale per concept. Label bottom at 15 mm, clear of the heel. The top element sits at
  most at 153 mm, 1 mm under the arch onset at the panel centre. Scale is the smaller of rev D (0.019356 mm/u) and
  what fits:
  - **C06: 100 %** (rev D)
  - **C05: 95.2 %**
  - **C07 and C10: 91.4 %**

  Their artwork is taller than the Imperial's flat face. At rev D, Concept 7's coin would sit on the shoulder
  curve.
- **Labels:** wrap labels on the v008 true-length wrap, level top and bottom edges, front and sides with the back
  clear, as Concept 1.
- **Physical interpretation:**

| Figma element | Physical treatment |
| --- | --- |
| Navy labels (C05, C06, C07) | SUB-01 dyed-through navy felt, 0.15 mm; cream ink; FOIL-01 hot foil; EMB-01 0.2 mm emboss on wordmarks and monograms (as Concept 1) |
| Cream label (C10) | SUB-04 natural cream felt; navy ink; navy wordmark blind-embossed; gold spearman in foil |
| Gold art on bare glass | PRT-01 bright-gold precious-metal screen print, fired on (near-mirror, roughness 0.10–0.16) |
| Navy medallions (C06, C10) | Navy felt roundel Ø43.7 / Ø40.0 mm; foil ring and embossed foil monogram. C06's overlaps the label top edge |
| Bronze coin (C07) | MED-01 die-struck metal seal, 0.3 mm. Satin turned field, polished relief, rolled edge |
| Neck | v009 capsule. All navy on the variants: the four Figma concepts show no gold pinline. Collar flag LBL-NECK-01 (same artwork as Concept 1) on C06, C07 and C10; none on C05 |

**Foil lighting:** single shots aim the v009 foil strip at each concept's own foil copy. A third strip,
`CRD_Foil_Strip_Print`, is light-linked to the active concept's glass prints. The roundel strip lights its
emblem.

**Renders:** `renders/variants_v001_*`.
- Lineup hero and lineup three-quarter, at 2400×1350.
- Hero and three-quarter for all five concepts, at 1000×1600, 512 samples.
- Label, angle, emblem and print macros, plus the collar flag, at 2000×1600, 384 samples.

**Open:**
- The shared v009 key grazes the front faces, so the cream stock (C10 label, cream bands) reads as warm grey
  (about 50 % exposure). Lifting it would change the approved Concept 1 baseline, so this needs your decision.
- Typography on C05, C07 and C10 is 5–9 % smaller than Concept 1's, from the fit rule above.

## Figma design review (review system v001, 3 Nov 2026)

Figma file `JcxeRDhCrtgZUXhTWQn2hV` (AVANTE). Six pages were added after page 03; Page 1 and pages 01–03 are untouched
(checked layer by layer: the five editable copies match their Page 1 sources exactly, apart from 0.002-unit float noise on one rotated rectangle).

| Page | Node | Contents |
| ---- | ---- | -------- |
| 04 — Concept 01 \| Design Review | 61:2 (frame 62:2) | artwork component 62:31 · renders v001 · 7 callouts · register |
| 05 — Concept 05 \| Design Review | 61:3 (frame 64:2) | artwork component 64:31 · 8 callouts |
| 06 — Concept 06 \| Design Review | 61:4 (frame 64:413) | artwork component 64:442 · 9 callouts |
| 07 — Concept 07 \| Design Review | 61:5 (frame 64:868) | artwork component 64:897 · 9 callouts |
| 08 — Concept 10 \| Design Review | 61:6 (frame 64:1359) | artwork component 64:1388 · 9 callouts |
| 09 — All Concepts \| Comparison | 61:7 (frame 65:2) | lineup renders · one row per concept, artwork as INSTANCES · open decisions |

**Concept page layout.** A = editable vector, a local component holding a verbatim copy of the Page 1 group (the
source of truth for that concept's artwork from now on). B = front hero, C = three-quarter, both v001 renders.
Renders are registered to the vector: 9.624 Figma units per render pixel (front face of CAM_Hero at 1000 × 1600,
= rev D 0.019356 mm/u), shoulder line Z_EDGE 150.6 mm on artwork y 3851, dashed magenta guides across all three
panels. Differences between drawing and render are therefore real: the C01 label is 6 mm lower (v009), C05/C07/C10
are fitted at 95.2 / 91.4 %, C06 sits ≈10 mm higher (label bottom fixed 15 mm above base).
Numbered callouts with leader lines point at the components; the **material & finish register** below lists per
component: ID, Figma nodes, substrate, thickness, surface/roughness, ink, foil type/colour, foil finish, relief +
height, coating, Blender material, status. A render archive box receives superseded renders.

**Status convention** (component `Review / Status chip`, 61:16): APPROVED user-approved treatment · PROPOSED
recommendation awaiting review · REVIEW needs a design decision · SUPERSEDED historical. Only Concept 1 carries
APPROVED (the owner-approved direction of page 02); every variant treatment is PROPOSED or REVIEW. Gold processes
are kept distinct: FOIL-01 hot foil (flat or raised with EMB-01), PRT-01 fired bright-gold print on glass, MET-01
metallic ink (capsule pinline), MED-01 solid struck metal (C07 coin). Thickness, depth and grade values marked (P)
are proposals for visual authenticity, not manufacturing specifications.

**Figma → Blender update procedure** (`figma_review/`). Change detection is implemented and tested; applying a
change is a Claude-run procedure, not automatic synchronisation.
1. The user edits the artwork component on a concept page (page 09 follows automatically, it shows instances).
2. Claude runs `figma_signature.js` read-only through `use_figma` and saves the result as JSON.
3. `python3 figma_review/diff_review.py figma_review/baseline_v001.json CURRENT.json` lists changed, added and
   removed layers per concept, maps each review-copy node to its Page 1 source id (`review_map.json`) and routes it
   to the Blender work: which `variants_concepts.SPEC` layer, which composite texture (COLOR / MASK-FOIL /
   HEIGHT-EMB), which object, or "no Blender change" for the bottle illustration. Tested 3 Nov 2026 on a temporary
   duplicate of C07 with four edits: all four found and routed, nothing else flagged (`synctest_2026-11-03.txt`).
4. Claude re-exports only the changed layers from the review copy (Figma `download_assets`), saves them under the
   source id in `textures/variants_src/<cid>/` (and updates the layer bounds in its manifest if a layer moved),
   rebuilds only that concept into a new master version (`avante_variants_master_v002.blend`; v001 stays), checks
   that the other concepts and the C01 signature are unchanged (`check_variants_master.py`), and renders that
   concept's hero and three-quarter.
5. The new renders replace the image fills of panels B and C (`render_rects` in `review_map.json`) and of the
   matching row on page 09; the previous pair moves to the page's render archive, marked SUPERSEDED.
6. A new baseline is saved (`baseline_v002.json`) and the change is logged in Notion.
Concept 1 is the exception: its Blender label is the rev D construction from page 01 § L built by
`build_avante_master`, so a C01 artwork change is routed to that pipeline by hand.

## Variants master v002 (3 Nov 2026) — the user's Figma edits and comments, plus 15 photography setups

`avante_variants_master_v002.blend` (v001 and v009 untouched: MD5 c1dffef2… and d5899c04… unchanged).

    blender -b avante_master_v009.blend --python build_variants_master_v002.py -- --save avante_variants_master_v002.blend
    blender -b avante_variants_master_v002.blend --python rebuild_photography_v002.py     # rigs only, after recipe edits

**Source of truth** — the editable components on review pages 04–08 (Figma checkpoint version 2417687811270157536).
`figma_review/make_manifests_v002.py` writes `textures/variants_src_v002/<cid>/manifest.json` from the review
copies; only layers whose pixels changed were re-exported (C06 6, C07 5, C10 1 + the new monogram 57:262), the rest
reuse the v001 exports at their new positions. Text exports are glyph crops, so text is placed by its render
bounds (this removes a ≈1.2 mm upward offset that all variant text had in v001).

**Registration frozen at v001** (`variants_concepts_v002.FIT_V001`): each concept keeps its v001 mm-per-unit and
label-bottom anchor, so every edit moves on the bottle exactly as far as it moved in Figma; nothing is refitted
or stretched. Changes applied:
- C05: glass print 4.7 mm lower; domed emboss on AVANTE and the panel monogram (comments).
- C06: wrap narrowed to the drawn edges (arc ±41 mm, now stops at the front-face edges) and shortened; medallion
  Ø 31.7 mm, domed disc; AVANTE and story print 83.5 % and lower; type 82.5 %.
- C07: label shortened (bottom 13.0 mm higher); coin Ø 36.4 mm, lower, **solid metal 0.60 mm** (comment "yes solid
  metal, 2x extrusion"); domed AVANTE.
- C10: label shortened, ground #F7F2EC, navy wrap band and pinlines removed, new gold monogram (FOIL-01 flat,
  finish REVIEW); medallion Ø 35.7 mm, domed disc.
- C01: v009 objects; domed AVANTE (spearman keeps the flat die) and domed film roundel (0.45 mm + stamped foil).
- Domed emboss (EMB-02, P): distance-based quarter-circle crest, 0.25 mm; medallion discs domed 0.45 mm under it.
  Height maps are normalised; displacement Scale = map maximum.

**QA** — `check_variants_master.py`: 48/49, the single failure is "one file, one scene", expected now that the 15
photography scenes exist. Concept 1 signature equals v001 except the roundel material (the requested dome).

**Photography** (`photography_v002.py`, `render_photography.py`, `photography/REFERENCE_BREAKDOWN.md`): one scene
per placement, `PHOTO_<cid>_<ref>`, linking that concept's assembly (never copied) and its own rig collection
under `PHOTOGRAPHY/PHOTO_<cid>/` (excluded from the main scene's view layer, so the shared studio and its renders
are unchanged). 15 placements, 7 distinct reference images; light levels calibrated to the v009 studio (key
10.5 W). Passes: A composition (25 %, 24 spp), B light/material (40 %, 48 spp), C QC sheets
(`photography/compare_sheet.py`, reference | render), FINAL.

    blender -b avante_variants_master_v002.blend --python render_photography.py -- FINAL all 100 384

**FINAL photography (3 Nov)** — all 15 rendered at 100 %, 256 spp to `renders/photography/FINAL/`; v002 lineups
at 50 % to `renders/v002_diag/variants_v002_lineup_*.png`. Placed in Figma under each concept's
"Photgraphy references" section (section "Photography v002 — FINAL"), page 09 lineup slots updated.

**Lighting refinement (4 Nov, user-approved)** — the C07/C10 cream (#F7F2EC, ≈0.93 linear) rendered grey because
the paper got far less light than the glass highlights and AgX tone-mapped it to mid-grey. Lighting-only fix,
artwork and materials untouched:
- `photography_v002.py` `LABEL_FILL`: soft frontal area light per setup, light-linked to the concept's front-label
  object only (C07 55, C10 100 W-units; C05 R24 50). C05 R24 also gets a warm back-glow card (backlit liquid) and
  fill 4→6.
- `studio_labelfill_v002.py`: the same idea in the shared studio (`STUDIO_LABEL_FILL`, C07 12 W, C10 45 W) for the
  lineups and single-bottle renders.
- Re-rendered: C05 R24, C07 ×3, C10 ×3, both lineups, C07/C10 hero + three-quarter diagnostics. Pre-refine copies
  in `renders/photography/FINAL_pre_labelfill/` and `renders/v002_diag/pre_labelfill/`.

The C01 domed height map is written as a lossless ZIP float EXR (≈2 MB rather than ≈470 MB uncompressed).
