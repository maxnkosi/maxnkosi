# A — Silhouette metrology: reference vs v005 vs v006 (AVANTE 750 ml "Imperial")

Study only. No project file was edited. Every script and intermediate file is in `research/v006_study/diag/`:

- `ref_edges.py`: dumps the reference pixels to numpy through Blender.
- `ref_profile.py`: sub-pixel silhouettes → `ref_profiles.json`.
- `arch7.py`: arch highlight tracking.
- `model_metrics.py` and `model_extra.py`: analytic model metrology, run headless by importing `build_avante_master` → `model_metrics.json`.
- `knuckles.py`: fillet radii and cone straightness, using the same method on references and model.
- `plot_svg.py` → `A_profiles.svg`: overlay of the silhouettes and arch heights.

The model silhouettes are computed exactly from `outer_r(θ, z)`, taking the maximum of r·cos(θ−view) over θ. They are not rendered, so they carry no shading or pixel error.

**How v005 was rebuilt.** v005 (the pyramid shoulder) is recovered as `section_r(θ, width_at(z), roundness(z))`: the body square follows PROFILE, with no dome. The current `roundness` (182 to 186 mm) is assumed for v005. This only affects the neck-finish corner above 182 mm and none of the shoulder numbers below.

---

## 1. Method and scaling

| Ref | What it is | Base / top located how | Scale |
|---|---|---|---|
| **raw2** (543×388) | Clear Imperial, white CGI catalogue render, face-on, no closure. **Primary.** | Top is the first dark row of the lip outline (row 26). Base is the last full-width bottom outline row (row 363). H = 338.0 px | 226.9 / 338 = **0.671 mm/px** |
| **raw1** (320×427) | Clear Imperial with bar-top. CGI with a slightly high camera: the base ellipse and punt are visible. | Top is the underside of the black bar-top head, where the lip bulge begins (row 85.5). Base is the lowest outline row (385.5). H = 300 px | 0.756 mm/px. The width-based scale would be 0.739, a 2.3 % perspective/closure discrepancy |
| **raw7** (800×800) | 48Gin, matte teal CGI, face-on. Same family, but a different neck and finish. | The glass top is hidden under the capsule. Base is row 797.5. | Scaled so max width = raw2's 89.3 mm (0.292 mm/px). Heights are therefore relative, not absolute |
| raw8, raw5 | Photos with strong perspective (lying bottle; 3/4 view from above) | – | Qualitative only: arch form, facet and edge character |

Edges are found by thresholding at 0.90 grey (or 0.85 min-channel for raw7) with linear sub-pixel interpolation and 3-row smoothing.

---

## 2. Width vs height (front, flat-to-flat) at the PROFILE heights

Units: mm. The ratio is W / W_max of the same image. Δ = v006 − raw2.

| z | raw2 W | raw2 ratio | raw1 ratio | raw7 ratio | PROFILE = v005 front | v006 front | Δ v006 | v005 diag 45° | v006 diag 45° |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 61.0 | .681 | .599* | – | 55.6 | 55.6 | −5.4* | 72.7 | 72.7 |
| 2 | 61.8 | .690 | .712 | .731 | 62.2 | 62.2 | +0.4 | 81.3 | 81.3 |
| 5 | 65.9 | .735 | .753 | .785 | 64.9 | 64.9 | −1.0 | 84.9 | 84.9 |
| 10 | 71.9 | .803 | .765 | .795 | 71.6 | 71.6 | −0.3 | 93.6 | 93.6 |
| 20 | 73.3 | .818 | .776 | .810 | 73.0 | 73.0 | −0.3 | 95.5 | 95.5 |
| 40 | 75.6 | .843 | .838 | .841 | 75.6 | 75.6 | 0.0 | 98.9 | 98.9 |
| 60 | 77.0 | .859 | .877 | .869 | 77.0 | 77.0 | 0.0 | 100.7 | 100.7 |
| 80 | 79.9 | .892 | .910 | .898 | 79.6 | 79.6 | −0.3 | 104.1 | 104.1 |
| 100 | 82.6 | .922 | .934 | .927 | 83.0 | 83.0 | +0.4 | 108.5 | 108.5 |
| 120 | 84.2 | .940 | .966 | .962 | 85.0 | 85.0 | +0.8 | 111.1 | 111.1 |
| 140 | 88.1 | .983 | .995 | .989 | 87.7 | 87.7 | −0.4 | 114.7 | **114.2** |
| 145 | 89.2 | .996 | .991 | .998 | 89.0 | 89.0 | −0.2 | 116.4 | **109.2** |
| 150 | 89.3 | .996 | 1.001 | 1.000 | 89.0 | 89.0 | −0.3 | 116.4 | **99.3** |
| 152.5 | 89.0 | .994 | 1.000 | .997 | 88.9 | 88.7 | −0.4 | 116.2 | **94.4** |
| 155 | 88.8 | .991 | .988 | .966 | 88.4 | 87.6 | **−1.2** | 115.6 | **89.7** |
| 157.5 | 86.0 | .960 | .972 | .899 | 85.5 | 85.0 | −1.0 | 111.8 | 85.5 |
| 160 | 80.9 | .904 | .934 | .821 | 80.3 | 80.2 | −0.7 | 105.0 | 80.3 |
| 162.5 | 75.0 | .837 | .871 | .740 | 74.0 | 74.0 | −1.0 | 96.8 | 74.0 |
| 165 | 68.6 | .766 | .801 | .652 | 67.6 | 67.6 | −1.0 | 88.4 | 67.6 |
| 167.5 | 61.6 | .688 | .736 | .574 | 60.8 | 60.8 | −0.8 | 79.5 | 60.8 |
| 170 | 54.2 | .605 | .656 | .504 | 54.2 | 54.2 | 0.0 | 70.9 | 54.2 |
| 172.5 | 48.4 | .540 | .574 | .447 | 48.5 | 48.5 | +0.1 | 63.4 | 48.5 |
| 175 | 43.1 | .481 | .506 | .405 | 43.5 | 43.5 | +0.4 | 56.8 | 43.5 |
| 177.5 | 40.2 | .448 | .459 | .378 | 39.8 | 39.8 | −0.4 | 52.0 | 39.8 |
| 180 | 37.1 | .414 | .422 | .363 | 36.8 | 36.8 | −0.3 | 48.0 | 36.8 |
| 182.5 | 35.9 | .401 | .390 | .356 | 35.8 | 35.8 | −0.1 | 46.3 | 35.8 |
| 185 | 35.0 | .390 | .378 | .347 | 35.0 | 35.0 | 0.0 | 36.7 | 35.0 |
| 190 | 34.7 | .387 | .347 | n/a | 34.1 | 34.1 | −0.6 | 34.1 | 34.1 |
| 215 | 34.4 | .384 | n/a | n/a | 34.1 | 34.1 | −0.3 | – | – |
| 220 | 40.9 | .456 | n/a | n/a | 41.5 | 41.5 | +0.6 | – | – |
| 225.7 | 35.3 | .394 | n/a | n/a | 38.0 | 38.0 | +2.7† | – | – |

\* The z = 0 row in raw2 is the bottom outline, which is partly hidden by the heel chamfer line. raw1's base is foreshortened because the camera sits above the bottle.
† The top 1 mm of the lip is an antialiased curve, ±1.5 mm.

**Reading the table.** PROFILE is the raw2 silhouette: it lies within ±0.8 mm everywhere between 2 and 220 mm. The front silhouette was therefore already right in v005.

- v006 changes the front view only at 152.5 to 167.5, where it is up to 1.2 mm narrower. This comes from the ARCH_K softmin plus the Z_HOLD hold.
- The diagonal (45°) columns show the real change. In any 3/4 view, the v006 corners fall away from **z ≈ 140**, compared with 154 in v005. At z = 150 the corner silhouette is 17 mm narrower.

**Key front-view numbers (raw2, with raw1 / raw7 in brackets):**

**Max width and the max-width line**
- W_max = 89.6 mm (raw2 sub-pixel; PROFILE has 89.0).
- The plateau (W ≥ 0.99 W_max) runs from z 144 to 155, with its centre at about 149–150. raw1 and raw7 put the centre at about 150.
- In the model, the plateau is 145–150 and `Z_EDGE` is at 150.6. The two agree.

**Shoulder**
- The shoulder starts (silhouette 0.5 mm inside the body line) at **z 151.4** (155.4 / 153.3). v005 starts at 152.5 and v006 at 152.0.
- The body-to-cone knuckle vertex is at z 156.3 (157.5 / 154.1). The model has 156.1.
- The cone is **straight** between z 159 and 170: the line-fit residual is ≤ 0.27 mm (σ 0.16), which is pixel noise. It is not convex or concave.
- The cone angle is **52.5° from vertical** (37.5° from horizontal). raw1 gives 51.1° and raw7 55.1°. The model also gives 52.5°.

**Neck**
- Diameter 34.4–34.7 mm, compared with 34.1 in the model.
- The straight neck runs from about 186 to 215 mm (≈ 29 mm long). The model has 188–215.
- The lip at the bead is 40.9 mm; the model has 41.5.

**Body taper and heel**
- W(20)/W_max = 0.818. raw7 gives 0.810; raw1 gives 0.776, but it is foreshortened. The model gives 0.820.
- W(10)/W_max = 0.80.
- raw2 shows a chamfered heel: the width goes from about 61 to 72 mm between z 0 and 9, roughly 34° from vertical. PROFILE copies it.
- raw1 shows a rounded heel instead. This is a render-variant or perspective difference, and it is not used.

---

## 3. Shoulder arch, corner end, chamfer and edge radii

### 3a. Arch: height of the face-to-shoulder edge across the front face

| lateral y from panel centre (mm) | 0 | 10 | 20 | 30 | 35.8 | 37.75 = face/chamfer edge | rise |
|---|---|---|---|---|---|---|---|
| raw7 highlight (measured, lit half) | 153.0 | 152.7 | 150.6 | 146.5 | 143.9 | 142.5 | **10.5** |
| raw7 shifted +2.2 to raw2 shoulder height | 155.2 | 154.9 | 152.8 | 148.7 | 146.1 | 144.7 | 10.5 |
| raw2: top end of the visible face/chamfer edge line | – | – | – | – | – | **147.3** | 9.0 to the knuckle vertex at 156.3 |
| straight 52.5° cone revolved and cut by the square (geometry check) | 156.2 (sharp) or ≈155 (filleted) | | | | | 145.5 | ≈ 10 |
| **v006** visible edge (surface 20° off vertical) | 155.0 | 153.7 | 150.4 | 145.8 | 143.6 | **142.6** | **12.4** |
| **v006** carving onset (0.2 mm cut) | 153.3 | – | 147.9 (y = 22) | – | – | **140.1**; 139.7 at the chamfer centre | **13.6** |
| v006 design comment (`Z_ARCH_C` 131) | ~153 | | | | | ~137 | ~16 |
| v005 | 155.5 straight crease at every y | | | | | 155.5 | 0 |

**Reference arch.** The apex sits at the panel centre, at about **155 mm**. The corner (face/chamfer) edges end at **145–147 mm**, so the **arch rise is ≈ 9–10.5 mm**. This is exactly what a straight 52.5° cone gives when it is revolved and intersected with the square body (145.5 mm at the face edge). In other words, the reference shoulder is a surface of revolution of the same cone that forms the silhouette, with no extra easing.

**v006 arch.** The shape across the face is close (client: "arch good"), but the corners run 2–5 mm too low, and carving starts 5–7 mm too low:
- The corners reach 142.6 visibly and 139.7–140.1 at onset.
- That makes the arch rise 12.4–13.6 mm, against a reference of 9–10.5.

**Why v006 goes too low.** Below `Z_ARCH_F` = 157.5, `shoulder_R` is a Hermite ease down to `Z_ARCH_C` = 131. At the corners this produces a **45°-from-vertical** dome, steeper than the 52.5° reference cone, which starts carving at 139.7.

### 3b. Corner chamfer (vertical facets)

| | chamfer leg / W | leg (mm) | facet width (mm) |
|---|---|---|---|
| Model (`CHAMFER` 0.0754) | 0.0754 | 6.70 | 9.48 (= the wrap's bevel panel, S1_E − HF_E = 9.5) |
| raw2 (clear Imperial) | 0.030–0.045 | 2.7–4.0 | 3.8–5.7 |
| raw1 (clear Imperial) | 0.042–0.058 | 3.8–5.3 | 5.4–7.5 |
| raw7 (matte 48Gin) | 0.072–0.082 | 6.4–7.3 | 9–10 |

**How the Imperial figure was read.** In raw2 the band between the outer silhouette and the facet edge line is ≤ 5–6 px, with two lines about 3 px apart. A 6.7 mm leg would show as a 10 px band, and no such band is present. The width is still uncertain: in clear glass, one of those lines may be the inner wall seen edge-on.

**What follows.** The model chamfer matches the 48Gin, not the clear Imperial. The Imperial refs point to a leg of about **0.04–0.05 W (≈ 4 mm)**. However, the label dieline was developed on the 9.5 mm facet and the comment says "W2124 ratio". Check the supplier drawing before changing `CHAMFER`.

### 3c. Edge crispness: equivalent radii (mm)

Model values come from analytic curvature. "Equivalent R" is the radius of a true fillet that leaves the same gap from the sharp corner. Reference values use the same vertex-gap method on the silhouettes; where they come from image appearance, that is stated in the row.

| Edge | Reference | v005 | v006 | Comment |
|---|---|---|---|---|
| Vertical face/chamfer edges | **≤ 1–1.5** (raw2/raw1 edges are 1–2 px lines at 0.67–0.76 mm/px). raw7 has a softer roll on a matte coating. | **5.9 equivalent** (min curvature R 3.8); `EDGE_SOFT` 0.7 leaves a 0.49 mm corner gap | same, 5.9 | 2.4 mm of tangent run on each side of a 9.5 mm facet, so about half the facet is rounding. **Main cause of "edges overly bevelled".** An equivalent R of 1.0–1.5 needs `EDGE_SOFT` ≈ 0.12–0.18. |
| Face-to-shoulder at the panel centre (silhouette knuckle) | **10.6** (raw2); 11.0 (raw1); 6.2 (raw7) | 9.8 equivalent, but locally 2.7–3.6 at z 155–155.5 (a PCHIP kink) | 12.8 equivalent (min 8.1 at 154.5) | v006 is slightly softer than the reference. |
| Face-to-shoulder at the corners (arch ends) | ≈ 2–4: the raw7 highlight step is 1.5–3 mm wide over a ~45° turn. A matte part probably reads softer than clear glass. | 1.6 (straight crease) | **4.2–4.6** min (≈10 equivalent), from `ARCH_K` 1.2 | Somewhat soft. `ARCH_K` ≈ 0.6–0.8 would match. |
| Shoulder-to-neck (concave) | 17.2 (raw2), 21.9 (raw1), 22.4 (raw7) | 19.2 equivalent, but locally 2.8 at z 180 (PCHIP kink) | 19.1 equivalent, locally 2.8 | Global size is right; local kink at 180. |
| Z_HOLD (152.5) | none (smooth) | – | **1.9° crease ring** (concave, local R 1.9) where `body_S` stops following the taper | New in v006. |

### 3d. Surface fairness: "uneven surface above shoulders"

All the following come from the analytic model, as sign changes of d²r/dz² and slope jumps:

1. **v006 dome join at `Z_ARCH_F` = 157.5.** The surface slope jumps from 37.4° to 42.5° (face edge and corner) and from 31.6° to 38.1° (panel centre) within 0.5 mm. This is a **5–6.5° crease ring right round the shoulder**: the Hermite ease meets the PCHIP silhouette with matching slope but a large curvature jump.
2. **v006 concave dish, z 149.5–157.5, at the face edges and corners.** The dome is concave here (R 870 → 40 mm), then convex again above 157.5. The reference cone is straight, so the model has a dip followed by a ridge.
3. **Extra inflections at the corners** (θ 39–45°) at z 130.5, 131, 135.5–136.8, 140.3 and 149.3. They come from the Hermite ease plus the softmin tail, and v005 does not have them.
4. **PROFILE cone ripple (v005 and v006).** The PCHIP through the 2.5 mm-spaced, ±0.7 mm table has 8 curvature reversals between 157 and 169, with a 0.23 mm peak deviation from a straight line. A 0.1 mm wave over 2.5 mm already has a local radius of about 8 mm, which shows clearly in glass reflections. On the v005 pyramid this was confined to flat faces. On the v006 revolved dome it becomes **horizontal rings across the whole shoulder**.
5. **Pre-existing belt at z 140–145 (both versions).** PROFILE climbs 87.7 → 89.0 (slope 10°) and then goes dead flat, which bends the surface 10° in about 3 mm. raw2's plateau is gentler, with no visible kink. v006's corner carving now starts in exactly this zone (139.7), which stacks two features.

---

## 4. Summary table: reference vs v005 vs v006, and the client complaints

| Quantity | Reference (best estimate ± unc.) | v005 | v006 | Δ v006 − ref | Explains |
|---|---|---|---|---|---|
| Front W_max | 89.3–89.6 ± 0.4 | 89.0 | 89.0 | −0.4 | – |
| Max-width line (plateau centre) | 149.5 ± 1 | 147.5 | 147.5 | −2 (plateau 145–150 vs 144–155) | – |
| Silhouette shoulder start (0.5 mm) | 151.4–155.4 (raw2 151.4) | 152.5 | 152.0 | ≈ 0 | – |
| Knuckle vertex (panel-centre apex) | 156.3 ± 0.7 | 156.1 | 156.1 | −0.2 | – |
| Front width at 155 / 157.5 | 88.8 / 86.0 | 88.4 / 85.5 | 87.6 / 85.0 | **−1.2 / −1.0** | Slightly "lower" shoulder in the front view |
| Cone angle and form | 52.5° from vertical, straight | 52.5°, rippled | 52.5° at the centre; **45° at the corners**; rippled and creased | corners 7.5° steeper | "Lower shoulders", "uneven surface" |
| Corner (face/chamfer) edges end at | **145–147** (raw2 147.3; raw7 144.7; cone model 145.5) | 155.5 | **142.6** visible; 140.1 onset | **−2.5 to −5** visible; −5 to −7 onset | **"Lower shoulders"**, seen most in 3/4 views (diag width −17 mm at z 150 vs v005) |
| Arch rise (apex − corner end) | **9–10.5** | 0 | 12.4–13.6 | **+2 to +4** | "Arch good" in shape, but carved too deep |
| Diag (45°) silhouette at 145 / 150 | ≈ 116 / ≈ 110 (estimated from the cone model, not measured) | 116.4 / 116.4 | 109.2 / 99.3 | ≈ −7 / −11 | "Lower shoulders" |
| Crease rings | none visible | 155 (PCHIP knuckle); 157.5 (PROFILE point) | 152.5 (1.9°), 157.5 (5–6.5°), concave dish 150–157, corner ripples | – | **"Uneven surface above shoulders"** |
| Vertical-edge radius | ≤ 1–1.5 | 5.9 equivalent | 5.9 equivalent | **+4.5** | **"Edges and corners overly bevelled"** |
| Chamfer leg / W | 0.04–0.05 (Imperial), 0.075 (48Gin) | 0.0754 | 0.0754 | +0.03 if the Imperial is right | "Overly bevelled", if confirmed |
| Arch-edge radius at the corners | ≈ 2–4 | 1.6 | 4.2–4.6 (≈ 10 equivalent) | +1 to +2 | "Corners overly bevelled" (secondary) |
| Shoulder-neck fillet | 17–22 | 19 | 19 | 0 | – |
| Neck Ø / straight length | 34.5 / ≈ 29 | 34.1 / 27 | 34.1 / 27 | −0.4 / −2 | – |
| Taper W(20)/W_max | 0.81–0.82 | 0.82 | 0.82 | 0 | – |

### Label placement

The rev D wrap crown is itself an arch: z 158.5 at the centre and 145.0 at the corner end (s = 46.9), a 13.5 mm rise. It sits from `Z_EDGE` 150.6 up onto the shoulder.

In v006 the surface under the crown corners is carved inward compared with v005:

| z | inset at face edge | inset at corner | inset at y = 30 |
|---|---|---|---|
| 145 | 3.3 mm | 3.6 mm | 0.4 mm |
| 150 | 8.2 mm | 8.5 mm | 4.1 mm |

So the wrap's upper corners are forced down a 45° dome that begins at about 140, and the label reads as sitting low and wrapped over the shoulder. With corners ending at the reference ~145–147, the inset at the crown corner (z 145) would be ≤ 0.5 mm.

### What the numbers point to (for the fix pass; not applied)

1. **Shoulder dome.** Make `shoulder_R(z)` below 157.5 the **straight 52.5° cone continued downward**: R = 42.75 + 1.30·(157.5 − z), joined with C² continuity into a single faired curve.
   - This replaces the 45° Hermite ease from 131 mm.
   - Predicted result: corner end ≈ 145.5, panel apex ≈ 155, rise ≈ 10 mm.
   - `Z_ARCH_C` then becomes about 143–144 rather than 131.
2. **Fair the cone.** Replace PROFILE 155–180 in the dome with a fitted line plus two fillets (knuckle R ≈ 10, neck R ≈ 18–20). Do not use a PCHIP through the noisy points. This removes the 157.5 crease and the rings.
3. **Remove the `Z_HOLD` crease.** Hold `body_S` with a smooth blend instead of `min(z, 152.5)`, and soften the 140–145 belt in PROFILE.
4. **Edges.**
   - `EDGE_SOFT` 0.7 → **0.12–0.18** (R 1.0–1.5 mm).
   - `ARCH_K` 1.2 → about 0.6–0.8.
   - Leave `CHAMFER` until W2124 is checked. The clear Imperial refs suggest 0.04–0.05, but the dieline is built on 0.0754.

---

## 5. Uncertainty

**Renders vs photos**
- raw1, raw2 and raw7 are CGI product renders: noise-free, with clean outlines and studio-style lighting.
- raw2 is a near-orthographic catalogue render. Its top and bottom outlines are straight, with no visible ellipse.
- raw1 has a raised camera: the base ellipse and punt are visible, and the width and height scales disagree by 2.3 %.
- raw8 and raw5 are real photos with strong perspective and shallow depth of field. They are qualitative only (arch form, flat facets, edge character).

**Perspective and lens**
- A pinhole projection keeps straight edges straight, so the arch curvature is real geometry, not distortion.
- Features on the front face sit about 44 mm nearer the camera than the silhouette plane. At a typical 1–3 m equivalent distance, this magnifies them 1.5–4.5 % about the optical axis. For an axis near mid-height (~115 mm), heights near 150 mm read up to about **+1.5 mm** too high, and the arch rise is affected by ≤ 0.5 mm.
- Barrel distortion is not detectable: vertical edges are straight to within ±0.3 px.

**Pixel error**
- raw2: sub-pixel edges ±0.3 px gives widths ±0.4 mm and z positions ±0.5 mm. Locating the top and base rows within ±1 px gives a ±0.3 % scale error (±0.7 mm at the lip).
- raw1: ±1 mm, plus perspective up to 2–3 %.
- raw7: heights are relative only, because it is width-scaled ±0.5 %. Its shoulder sits about 2 mm lower than raw2's, which suggests a slightly different mould or proportion.

**Arch heights**
- ±1.5 mm, because a rounded edge's highlight is offset from the geometric tangent line, and only the lit half of raw7 can be tracked.
- The raw2 corner-end value (147.3) is ±0.7 mm in the image but rests on reading a line ending in clear glass.

**Chamfer width.** This is the least certain number, because clear-glass double lines are ambiguous: range 0.03–0.058 W for the Imperial. The radii are lower or upper bounds limited by resolution (0.67–0.76 mm/px). Silhouette radii are ±30 %.

**Model numbers** are exact to the builder's analytic functions, sampled at 0.05–0.25 mm in z and 0.125° in θ. They do not include mesh faceting (N_RING 256) or auto-smooth shading.
