# v006 study C: wrap label placement on the arched shoulder

Study only. No project files were edited. Diagnostics are in `research/v006_study/diag/`:
`d2_label_vs_glass.py` reads the saved v005/v006 `.blend` meshes and computes glass curvature under the label, label-to-glass gap and dieline-to-3D strain (output `d2_v005.json`, `d2_v006.json`). `d3_arch_vs_crown.py` imports `build_avante_master.py` as a module and works out the analytic arch edge, crown heights and the arch the glass needs (output `d3_arch_vs_crown.json`). `d4_art_clearance.py` finds where the artwork starts below the crown.
Heights are in mm above the glass base, and "from cap" means CAP_TOP 238.1 minus z. Z_EDGE = 150.6.

## 0. Verdict

The client is right about the label, and the cause is structural, not a tuning error.

- **What v006 did.** It moved `surf_xyz` onto `outer_r`, so the wrap is now pressed onto the revolved dome. A dome is doubly curved, and no flat sheet can lie on it.
- **Why the code hides it.** The code always forces every label vertex onto the glass, so the gap is 0 by construction. The error shows up as strain instead: the flat dieline is stretched by up to 42 % and compressed by up to 33 % near the crown and fold corners. That strain is what renders as the rolled-back crown and the pillow-shaped corners.
- **Where it really comes from.** The rev D crown was drawn for a straight 49° shoulder facet (that is where `SHOULDER_STRETCH = 1/sin 49°` comes from). That facet is a flat plane, so it can be developed. The arched dome cannot.

## 1. v005 vs v006, measured

### 1.1 Crown height and the glass under the crown

The label mesh is identical in both files, so the crown z values are identical. The glass underneath is what changed.

| crown point (dieline x) | z / from cap | v005 glass under it | v006 glass under it |
|---|---|---|---|
| 0 (front centre) | 158.47 / **79.63** | tilt 46°, hoop R ≈ 350 mm (pyramid facet) | tilt 43°, **hoop R ≈ 64 mm, K = 1.6e-3 /mm²** |
| 10 | 157.42 / 80.68 | tilt 39°, R2 568 mm | tilt 36°, R2 57 mm |
| 20 | 154.98 / 83.12 | tilt 18° | tilt **41°**, doubly curved |
| 30 | 151.64 / 86.46 | tilt 5° | tilt **44°** |
| 37.78 (front/chamfer fold) | 148.51 / 89.59 | vertical panel (0°) | tilt **45°**, dome |
| 46.9 (chamfer/side kink) | 145.53 / 92.57 | vertical (0°) | tilt **43°**, dome |
| 55–90 (side panel) | 145.5 / 92.6 | vertical | vertical from x ≈ 70 on |
| 110–119 (back end) | 145.1–145.6 | vertical | tilt 7–40° (back corners carved too) |

The v006 arch edge on the glass, meaning the lowest z where the dome departs from the flat panel by more than 0.05 mm, sits **7.1 mm below the crown at front centre** (151.4 vs 158.47). The gap grows to **10.6 mm below at the fold** (137.9 vs 148.5) and is still 7.6 mm below at the kink (`d3` `arch_vs_crown`). So about 25 % of the label's vertices sit on doubly curved glass. In v005 the figure was 22 %, but there the "double curvature" was mostly the near-planar facets and fold fillets. The v005 hoop radii under the crown were 350–3400 mm. In v006 they are 57–64 mm.

How far the dome is carved in behind the label, measured from the panel the label would otherwise lie on (radial, approximate):

| position | dome cut-in |
|---|---|
| front centre | 2.6 mm |
| x = 20 | 3.8 mm |
| x = 30 | 5.6 mm |
| **fold** | **7.2 mm** |
| kink | 4.1 mm |
| back end | 1.7 mm |

This is the "hump" at the chamfer corners: the label is forced 5–7 mm inward around a 50–75 mm hoop.

### 1.2 Strain (dieline to 3D, per triangle)

| zone | v005 | v006 |
|---|---|---|
| above Z_EDGE (front crown cap, 494 mm²): hoop (x) strain, mean | −0.8 % | **−6.9 %** |
| above Z_EDGE: vertical (y) strain, mean | −17.3 % (sin 49 squash, uniform) | −9.1 % (non-uniform) |
| above Z_EDGE: max stretch / compression | 6.9 / 24.4 % | **42.4 / 30.6 %** |
| top 15 mm of chamfer panels: max stretch / mean y | 8.2 % / +1.0 % | **42.2 % / +13.3 %** |
| top 15 mm of side panels: max stretch | 5.2 % | **36.2 %** (back corners) |
| whole label: p95 abs strain | 8.2 % | 12.9 % |

Two notes on reading this table:

- **Baseline artefact present in both versions.** About 18 % local compression in the 1–2 mm fold fillets (x ≈ ±40–50, at every height). It happens because `surf_xyz` walks the sharp polygon and then projects radially onto the filleted corner. It is a modelling artefact and is not new in v006.
- **What actually changed.** v005 squashed the crown evenly (the sin 49 mapping) onto developable facets, so it rendered smooth. v006 squashes it unevenly, mainly around the hoop (−7 % mean) and with +13 % vertical stretch at the corners. A real 0.15 mm paper sheet cannot do either. Usable in-plane strain for label paper is well under 1 % (memory-based: paper elongation at break is about 1.5–3 % MD, 3–6 % CD, and visible cockle and wrinkle start long before that).
- **Independent check from curvature alone.** Draping a disc of radius a over a surface with Gaussian curvature K needs a rim strain of about K·a²/6 (memory-based, spherical-cap approximation). At the v006 crown, K ≈ 1–2e-3 and a = 10 mm give **1.7–3.7 %**, so it would wrinkle or the edge would lift. At the v005 crown, K ≈ 3e-4 gives 0.5 %, which is borderline.

### 1.3 Renders

Crops are in the scratchpad and not kept. They compare `v005_hero` with `v006_hero`, and the three-quarter views of each.

- **Crown rolls back.** In the v006 hero the upper ~10 mm of the front panel shades lighter, because the normal tilts up 36–45°. The crown silhouette reads as a soft roll instead of the crisp die edge on a facet that v005 showed.
- **Corner pillows.** In the v006 three-quarter view, the front/chamfer/side corner of the label becomes a large rounded hump with a wavy top edge. v005 shows a clean fold on a vertical corner.
- **No visible wrinkles or gaps**, because the mesh is glued to the glass by construction. In a physical label the same mismatch would appear as darts, flagging edges or bubbles along the crown and at the four top corners.

## 2. Physical rule and how label areas are defined

- **A wet-glue or PS paper label can only follow developable glass**: planes, cylinders, cones and other ruled surfaces with straight rulings. On compound (doubly curved) glass it creases or lifts.
  - Non-developable means "cannot be obtained from a plane without tearing or folding", and plain glued labels are said to suit developable shapes such as cylinders: US 5916646, https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5916646
  - Labels "wrinkle on a 2D curve": https://www.core77.com/posts/12816/structural-package-design-tech-shrink-film-labels-12816
  - Tapers and cones are labelled routinely, by rotating the container on its cone axis: US 4565596 https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4565596 and US 4455182 https://patents.google.com/patent/US4455182
  - Compound areas need shrink sleeves or in-mould methods instead: US 6325879 https://patents.google.com/patent/US6325879
- **How label areas are defined.** Bottle drawings carry a "label panel" or "decoration area": the straight, flat zone between where the shoulder starts to curve and where the heel starts to curve.
  - The label sits inside that zone with a top clearance, usually **≥ 3 mm below the start of the shoulder**: https://printshop.paperlust.co/blog?p=4515 (a rule of thumb, not a standard).
  - Supplier label-area drawings give maximum label sizes with roughly 3–6 mm gaps and say that final tolerances depend on the specification, e.g. https://cdn.shopify.com/s/files/1/0134/2495/1367/files/128-001_VLabel_Area.pdf and https://www.tricorbraun.com/knowledge-base/could-i-please-request-a-bottle-schematicspec-and-recommended-label-dims
  - A recessed label panel is the stronger version of the same idea: the label lies in a developable recess that also protects it from scuffing (https://patents.google.com/patent/US6964345).
- **Clearance budget for this bottle** (memory-based, labeller practice):
  - glass mould tolerance on panel height: about ±0.5–0.8 mm
  - labeller vertical placement: ±0.5–1.0 mm
  - die-cut: ±0.3 mm
  - the 1.2 mm softmin fillet on the arch edge has to be cleared too
  - Result: **minimum 1.5 mm, design 2 mm, comfortable 3 mm** between the die edge and the arch tangent line, measured on the panel. 1 mm is too tight for production.
- **Reference check.** 48Gin (raw5, raw7, same family) has its printed decoration about 20+ mm below the arch apex. Its front-panel arch drops about 9–11 mm from centre to the chamfer edges. This is a perspective estimate from a 163 px panel width scaled to our 75.5 mm, ±2 mm.

## 3. Crown arc vs shoulder arch

**The hidden datum conflict.** The true dieline height at front centre, from crown to bottom tip, is **88.80 mm**. The rev D datum span is 165.9 − 79.64 = **86.26 mm**.

- The code closes the 2.54 mm difference by laying the top 10.43 mm of the label on a 49° slope (`SHOULDER_STRETCH`).
- On a flat vertical panel the label runs to its true length. Holding the bottom datum then puts the crown at **77.07 mm from cap**. Holding the crown datum puts the bottom at **168.44 mm**, which takes the gap to the roundel top (172.55) from 6.6 mm down to 4.1 mm.
- **Unchanged dieline + arched (dome) shoulder + both datums cannot all hold.** Something has to change: the die, a datum, or the shoulder type.

**Arch parallel to the crown.**

- The crown's 16.05 mm drop in the dieline (centre to the x = 46.9 kink) appears as about 13.0 mm in z today: 158.47 at the centre, 148.53 at the fold, 145.48 at the kink. Of that, 9.94 mm is across the front face.
- A revolved dome meets the front plane at radius √(h² + x²), h = 44.45. Making the arch tangent line equal crown + c gives the required dome radius below (crown positions as in the code; the same applies to option D.1 in section 4).

| point | crown z | arch z for c = 2 | R needed | v006 R at that z |
|---|---|---|---|---|
| front centre | 158.47 | 160.47 | 44.45 | 39.6 |
| x = 10 | 157.42 | 159.42 | 45.56 | 41.2 |
| x = 20 | 154.98 | 156.98 | 48.74 | 44.1 |
| x = 30 | 151.63 | 153.63 | 53.61 | 48.2 |
| fold (37.78) | 148.53 | 150.53 | 58.31 | 51.7 |
| chamfer / kink | 145.5–148.5 | ≥ 150.5 | 58.1–58.3 | 51.7–54.8 |

(c = 1: subtract 1 mm from the arch z values; c = 3: add 1 mm.)

What the table means:

- The glass needs a front arch **apex at about 160.5 (77.6 from cap)** and corners that start carving at about **150.5**. That is a front-face arch drop of about **10 mm**, which matches the 48Gin estimate of 9–11 mm.
- v006 has its apex at 151.4 and its corners at 137.9 (13.5 mm drop). That is **9 mm too low at the centre and 12.6 mm too low at the corners**, which is the client's "lower shoulders".
- On the chamfer panels a revolved dome is almost level, because the panel's radius only varies from 58.1 to 58.3. Clearance there therefore grows from 2 mm at the fold to about 5 mm at the kink. That is acceptable, and is why the arch does not need to follow the crown's chamfer drop.
- The side panels have ≥ 5 mm clearance and the back ends about 6 mm.
- Required R(z), which is monotone and smooth: 58.3 at 150.5 → 53.6 at 153.6 → 48.7 at 157.0 → 45.6 at 159.4 → 44.45 at 160.5. The slope is −1.4 to −1.05 mm/mm, so the shoulder then falls at roughly 45–50° to the neck.
- **Metrology conflict.** The photo-derived PROFILE puts the panel-centre shoulder start at about 153–154 (half-width 44.34 at 154, 42.75 at 157.5). The real Imperial (raw1/raw2) has a **straight faceted shoulder**, which is exactly what the 49° crown was drawn for. An arched shoulder that carries the rev D crown in its flat zone needs the panel flat about **6–7 mm higher** than that silhouette. This is a glass change and has to go to the glass/shoulder study for the volume re-solve. It moves in the same direction as the client's "lower shoulders" comment.

## 4. Fix specification

**A. Die (keeps both rev D datums and the artwork). Recommended, needs a rev D.1 sign-off from the client and printer.**

- Above the max-width line, replace the TRIM crown with its true-length projection: for TRIM points with y < 0, use y′ = y · sin 49° = 0.7547 · y. Points with y ≥ 0 stay as they are.
- Front-centre crown moves from y −10.414 to −7.86, which is 2.55 mm less paper. It tapers to 0 at |x| = 31.6.
- The crown then sits at **79.64 from cap on a flat panel** and the bottom stays at **165.9**.
- The visible crown shape is the same as every approved render to date, because the renders already showed the squashed version. The crown arc drop becomes 13.5 mm in the dieline.
- Artwork is not touched. The topmost foil is at dieline y = +1.58, and the bird at the centre at +3.28. Clearance from the new die edge is 11.1 mm at the centre and at least 6.0 mm at the spear tip (`d4`).
- Alternatives if the die cannot change:
  - B: hold the crown, bottom becomes 168.44 (datum change, roundel gap 4.1 mm).
  - C: hold the bottom, crown becomes 77.07 and the arch apex rises to about 163.

**B. Glass (arch above the crown).** Use the R(z) table in section 3 with c = 2 mm: apex 160.5, corner start 150.5, fillet 1.2 mm kept above the tangent line. Then re-solve volume and base.

**C. Mapping in `build_avante_master.py`, for whoever implements it:**

- `surf_xyz`: drop the sin 49 branch, so z = Z_EDGE − v for all v. The 4° body taper is already handled by `body_S(z)`.
- Place the point on the **panel planes of the held body section**, i.e. the sharp polygon at `body_S(z)` offset by `LABEL_GAP` along the panel normal. **Never on `outer_r`/`dome_cut`.**
- Map the perimeter coordinate s by arc length along the filleted section, not the sharp polygon. This removes the 18 % fold-fillet artefact.
- `dev_xy`: leave as it is (the fan development is correct for the tapered panels). Use the D.1 TRIM.
- Under the label, `dome_cut` must be inactive. Enforce it with an assertion instead of letting the label follow the dome.

**D. Acceptance checks to add to `check_avante_master.py`:**

1. **Isometry.** Per triangle, principal stretches between 0.995 and 1.005 (fold-fillet tris included, with the arc-length mapping). Report max and p99.
2. **Contact.** For every label vertex on the glass side, the gap to the glass is between −0.01 and +0.10 mm. This is computed with the label built on the panel planes and measured against the actual glass, not forced onto it.
3. **Arch clearance.** For every top-edge vertex, z_arch(θ) − z_label ≥ 1.5 mm (target 2.0). Here z_arch is the lowest z where `section_r − outer_r` > 0.05 mm. No label vertex may be above the arch tangent line minus 1.5 mm.
4. **Glass under the label is developable.** |K| < 1e-5 /mm² and normal tilt < 6° at every label vertex. Exclude analytic fold fillets, or check them with the true section instead of the 256-ring finite difference, which is noisy at R 1–2 mm.
5. **Datums.** Crown 79.64 ± 0.3 and bottom 165.9 ± 0.5 from cap. Tighten the existing 0.6 / 3.5 tolerances.
6. **Art clearance.** Foil and emboss at least 3 mm inside the die edge (currently 6.0 mm at minimum after D.1).

Caveats: the arch heights from the references are perspective estimates, ±2 mm. The clearance and strain limits are labeller practice from memory, not supplier data. Get the bottle maker's label-panel drawing and the labeller's tolerance sheet before the mould is frozen.
