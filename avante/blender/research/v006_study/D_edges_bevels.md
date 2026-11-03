# D: Edges and bevels on the v006 glass, compared with the references

Study only. No project files were edited. All diagnostics are in `research/v006_study/diag/`:

| file | what it is |
|---|---|
| `d_rowscan.py`, `d_base_edge.py` | luminance and silhouette scans of the reference photos |
| `d_edge_metrics.py` → `d_edge_metrics.txt` | effective radii the build functions actually produce |
| `d_calibrate.py`, `d_calibrate_face.py` → `*.txt` | how soft-min `k` maps to an equivalent fillet radius |
| `d_dome_scan.py`, `d_kinks.py`, `d_inner185.py` → `*.txt` | shoulder r(z) curvature, creases, the inner-bore step |
| `d_render_edges.py` | glass-only Cycles close-ups. `A` = current v006, `B` = proposed edges (in-memory monkeypatch) |
| `r_A_*.png`, `r_B_*.png`, `r_B_nobump_*.png` | corner z100, shoulder arch, base heel, neck root, full 3/4 |
| `ref_*.png` | upscaled crops of raw1, raw2, raw5, raw7, raw8 |

**Verdict.** The client is right. Every edge on the body is 3 to 10 times rounder than the comments in the code claim. The cause is that `EDGE_SOFT` and `ARCH_K` are soft-min blend widths in *radial* mm, not fillet radii. On a 40 to 45 degree crease, a radial blend of `k` gives an equivalent fillet of about 10 to 13 × `k`. On top of that, 256 ring vertices put only 3 or 4 vertices across each soft zone, so smooth shading smears the edge further. The heel is the right size, but it is a lumpy double-knuckle curve where the references show a flat, crisp bevel.

---

## 1. What the references show

Scale: body max width = 89.0 mm. Pixels were converted per image from the measured silhouette width (raw2 ≈ 0.68 mm/px, raw1 ≈ 0.74 mm/px, raw7 ≈ 0.32 mm/px, with the 48Gin width assumed ≈ 88 mm). The references are small web images, so read every number as ±1 mm.

| feature | estimate | method and evidence |
|---|---|---|
| **Vertical chamfer, leg** (projected width in a frontal view) | **3.5–5 mm** (≈0.045–0.055 × W). Facet width 5–7 mm | raw2 y=250: dark refracted band at the silhouette is 5 px = 3.4 mm. raw1 y=300: 5 px = 3.7 mm. raw7 (48Gin, frontal): corner shading zone about 15 px = 4.8 mm. raw5 3/4 view: facet highlight strip about 5 px ≈ 3–4 mm projected |
| **Face to chamfer, chamfer to side** | **R ≈ 0.5–1.0 mm** | raw1 and raw2: the band edges step from 98 to 84 % luminance within 1 px (<0.7 mm). raw1 shows a thin separate reflection line of the facet edge (index 27–28). Clear glass reads as two sharp hairlines per corner. The 48Gin photos (matte spray coat) read softer (≈1.5–2 mm), because the coating and diffuse shading widen any edge |
| **Face to shoulder arch** | **R ≈ 2–3 mm** across the face, opening to about 4–5 mm where the arch rolls over the chamfer | raw5 and raw8: the arch line is a defined crease with a narrow highlight. raw8 band is ~20–30 px on a ~0.17 mm/px face, but matte. Clear refs: a sharp line in transmission |
| **Shoulder knuckle** (silhouette break at the top of the body) | **R ≈ 4–5 mm** | raw1 rows 176–184: width 115 → 120 px over about 6 px. raw2 crop: tight round |
| **Shoulder to neck** (concave root) | **R ≈ 5–6 mm** | raw1 rows 136–148: 40 → 50 px over about 8–12 px. raw2 neck root crop |
| **Base heel** | **Bevelled (chamfered) heel**: flat facet about 30–35° from vertical, **≈6–8 mm tall × 4–5 mm inset**, crisp upper edge (R ≈ 1 mm), footprint edge R ≈ 1–1.5 mm. The bevel follows the octagon, so the footprint is a chamfered square | raw2 silhouette: width 106 → 90 px between y=351 and 363, about 8 px per side over 12 px. The break at y=351→354 is abrupt (R < 1 mm). raw5 and raw7 bases show the same small bevel. *raw1 differs*: plain rounded heel R ≈ 4–5 mm, no bevel |
| **Base footprint corners** (plan view) | the chamfered octagon, with the same R ≈ 1 mm as the body edges | raw2 base crop |
| **Neck finish** (bar-top lip) | R ≈ 0.5–1 mm on the lip | raw2 shoulder/neck crop: crisp flange |

In transmitted and reflected light, clear decanters of this family read as **thin, continuous dark or bright hairlines** on every edge. Hairlines mean small radii, roughly 1 mm or less. Our renders show **wide soft gradients** instead, which is the visual signature of a 5 mm+ radius.

## 2. What the v006 model actually produces

### 2a. Vertical edges: `sq_radius` (CHAMFER 0.0754, EDGE_SOFT 0.7)

| z | S | chamfer leg | facet width | **effective fillet per edge** |
|---|---|---|---|---|
| 40 | 75.6 | 5.70 | 8.06 | Rmin 3.8 mm, 41° of the 45° turn spread over **4.9 mm**, **equivalent R ≈ 6.8 mm** |
| 100 | 83.0 | 6.26 | 8.85 | same, **R ≈ 6.8 mm** |
| 140 | 87.7 | 6.61 | 9.35 | same, **R ≈ 6.8 mm** |

* The code comment says "≈ R1–2 mm fillets". The real result is ≈6.8 mm.
* The two soft zones (2 × 4.9 mm) consume most of the 8–9 mm facet. Only about 4 mm stays flat, so the corner reads as one big round instead of a facet. **This is the main "overly bevelled" cause.**
* Calibration (`d_calibrate.txt`): k 0.4 → R 4.7, k 0.3 → 3.8, k 0.2 → 2.7, k 0.15 → 2.2, **k 0.10 → 1.6, k 0.08 → 1.3, k 0.05 → 0.9 mm**.
* Bug: `sq_radius` uses raw `exp(-r/k)` and underflows to `log(0)` for k < ~0.065. Use the existing min-subtracted `softmin()` instead.
* CHAMFER: our leg is 5.7–6.7 mm against 3.5–5 mm in the refs, so about 35 % too wide. It is tagged P, but the label development (HF_E, S1_E, TRIM) is built on it. See §3.

### 2b. Shoulder arch: `dome_cut` softmin, ARCH_K 1.2

* The dome crosses the faces at a crease of **41°** (face centre z = 155.4, corners z ≈ 142).
* ARCH_K 1.2 gives a 95 % blend band of **±4 mm in z** and pulls the crossing in by 0.83 mm.
* Equivalent radius: **≈ 8–14 mm across the face, ≈ 7.6 mm over the corners**. Reducing k alone bottoms out at about 4–5 mm on the corners, because the Hermite ease of the dome is itself curved there.
* The large k also hides several **creases in the construction**. They become visible as soon as k is reduced, and they are also behind the "uneven surface above the shoulders" feedback:
  * `body_S` clamp at **Z_HOLD 152.5**: a 1.9° slope break in the face (−0.033 → 0), 3 mm below the face-centre arch.
  * `shoulder_R` join at **Z_ARCH_F 157.5**: 0.96° kink, because `mf` is a ±0.25 mm finite difference, not the pchip slope.
  * `shoulder_R` join at **Z_ARCH_C 131**: slope −2 below, 0 above (a 63° kink in the function). Soft-min attenuates it to about a 2° crease at the corners.
  * PROFILE pchip is only C1. Curvature jumps at the knots, e.g. at 155 mm from −0.06 to −0.52 /mm and at 157.5 from +0.06 to −0.39 /mm. In refraction this shows as bands every 2.5 mm across the dome (visible in `r_B_shoulder_arch.png` as rippled ovals over the corner).
  * Body face bulge: r rises 43.9 → 44.5 between 140 and 145 (PROFILE 140→145: 87.7→89.0), is flat to 150, then dips. This is a shallow belly just under the arch.
  * **Inner wall step at z = 185**: `inner_width` switches to BORE, so the inner radius jumps 13.90 → 13.00 mm (0.9 mm). Between 185 and 186 the inner section is briefly squarish (r45 = 13.6). This draws a ring line at the neck root.
  * `r_B_nobump_*` is identical to `r_B_*`, so the shoulder waviness is geometric, not the glass noise bump.

### 2c. Base heel (PROFILE rows 0–10 mm)

* The size matches the refs: 10 mm tall, 8.0 mm inset at z=0, 8.7 mm against z=20, an overall ≈32° bevel.
* The **shape** does not. Half-width slope per segment is 2.20, 1.10, 0.53, **0.37, 0.72**, 0.62, 0.07. The slope dips and then rises again, which makes an S-wobble across the facet. That gives three soft knuckles:
  * footprint at z ≈ 1.5 (44° turn, equivalent R 5.8 mm)
  * mid-facet at z ≈ 6 (21°, R 6.9)
  * bevel top at z ≈ 10.5 (34°, R 8.7)
* The underside is a cone (rim at z=0, centre at 1.2 mm), so the footprint corner is a hard single-ring 22° break smeared by auto-smooth.
* Result (`r_A_base_heel.png`): a molten, rounded heel with wobbly refractions, not the crisp cut bevel of raw2. **Not right against the refs.**

### 2d. Neck and finish

* Shoulder-to-neck concave: equivalent R ≈ 7.9 mm at z ≈ 183. This is close to the refs (5–6 mm), so it is acceptable or could be tightened slightly.
* Finish (215–226.9): equivalent R 1.6–4.8 mm, with Rmin 0.5 mm. It reads crisp and is fine.
* The shoulder knuckle at z ≈ 155–158 is equivalent R ≈ 9–10 mm against 4–5 mm in the refs. That is a PROFILE matter for the shoulder study ("lower shoulders").

### 2e. Mesh and shading

* N_RING 256 gives 0.93–1.41 mm segments, so only **3.4–4 vertices per soft zone**. A true 1 mm fillet (0.8 mm arc for 45°) would fall *between* two vertices.
* Rows are 1 mm apart from 12 to 148, which includes the corner arch band at 131–148.
* `shade_auto_smooth(40°)` smooths everything because every dihedral is under 40°, so the normal interpolation spreads each edge over 2 faces (≈ 2.5 mm). Geometry and shading together make the edges look wide.

## 3. Specification

### Target radii

| edge | target | current (equivalent) |
|---|---|---|
| face ↔ chamfer, chamfer ↔ side (vertical) | **R 1.0 mm** (0.8–1.2) | 6.8 mm |
| chamfer leg | keep **0.0754** for now (label-locked). Ref-true would be **0.050–0.055** (leg 4.0–4.9 mm), but only with a label re-development | 0.0754 |
| face ↔ shoulder arch | **R 2.5 mm** across the face, letting it open to ≈5 mm over the corners | 8–14 / 7.6 mm |
| shoulder knuckle (silhouette) | R 4–5 mm (PROFILE, shoulder study) | 9–10 mm |
| shoulder ↔ neck | R 5–6 mm | 7.9 mm |
| neck finish lip | R 0.5–1.0 mm | OK |
| heel | **flat bevel 33° from vertical, 7 mm tall × 4.5 mm in, R 1.0 at the bevel top, R 1.0 at the footprint**, flat 6 mm resting band, then the existing 1.2 mm push-up cone | curved 10 × 8 mm, R 6–9 mm knuckles |
| footprint plan corners | follow the octagon with the same R 1.0 | ≈6.8 mm |

### Parameter values (soft-min route: smallest change, proven in variant B)

```
EDGE_SOFT = 0.07   # was 0.7.  ~R1.1 mm on the 45 deg chamfer edges (d_calibrate.txt)
ARCH_K    = 0.25   # was 1.2.  ~R3 across the faces, ~5.5 mm equivalent over the corners
```

* In `sq_radius`, use `softmin(r1, r2, EDGE_SOFT)`, because the current `exp(-r/k)` underflows below k ≈ 0.065.
* Update the comments and README: k is a radial blend width, not a radius. Equivalent radius ≈ 13–16·k at k ≤ 0.2.
* A cleaner long-term option is a **true geometric fillet** for the section. Take the octagon inset by ρ, offset it back by ρ (Minkowski with a disc), and use the ray-exit radius as `sq_radius`. That gives an exact circular R 1.0 that is independent of S. It is optional, because k 0.07 is visually equivalent.

### Fix these before reducing ARCH_K (otherwise the creases show)

1. Remove the Z_HOLD clamp crease. Make PROFILE flat (89.0) from 145 to 152.5, or blend `body_S` with a C1 ease over ±3 mm.
2. Set `_SR['mf']` from the analytic pchip derivative at Z_ARCH_F.
3. Make `shoulder_R` below Z_ARCH_C C1. Continue with zero slope and a quadratic rise, not a −2 linear branch.
4. Above z ≈ 140, interpolate the dome and shoulder with a C2 spline (natural cubic or smoothing spline), not pchip, so curvature does not jump at the 2.5 mm knots.
5. Replace the BORE switch at 185 with a C1 blend of the inner radius (outer − WALL → BORE/2) over about 4 mm.

### Ring density and shading in Cycles

* **Put the fillet in the geometry**, at the target 0.8–1.2 mm. Do not fake it with auto-smooth or a Bevel shader node. In clear glass the edge you see is mostly refraction through the fillet, and only real geometry gives the thin bright and dark hairline pair.
* **At least 8 segments across each fillet arc**, i.e. ≤0.1–0.15 mm per step. Use **adaptive angular sampling**, not a uniform N_RING: about 384 uniform plus ±2 mm clusters at 0.0018 rad (≈0.085 mm) around the 8 vertex angles. The vertex angles are fixed at `atan(1 − 2·CHAMFER)` = 40.34° + k·90° and 49.66° + k·90°, independent of S. Variant B used 776 vertices per ring. A uniform ring would need ≈2048 (0.17 mm) to match, at about 3× the vertex count.
* **Rows**: ≤0.2 mm in z through 128–162 (arch band and knuckle), 178–192 (neck root) and the heel fillets (0.08 mm along the arc). Elsewhere 1 mm is fine, because the vertical edges are straight in z.
* **Shading**: plain shade smooth, with no angle split, once the fillets are resolved. Every dihedral is then under about 6°, so Smooth-by-Angle at 30–40° is harmless but adds nothing. Do not add Subdivision Surface, because it would re-round the fillets. Do not use Weighted Normals. A Cycles Bevel node is only useful for a ≤0.2 mm micro-break on the finish lip, if anything.
* **Heel**: build it as an explicit filleted polyline in (half-width, z) and loft each sample as a scaled body ring (`fillet_polyline` and `build_glass_B` in `d_render_edges.py`). Pchip through the PROFILE points cannot hold a flat facet with crisp ends. Variant B: footprint half-width 31.37, bevel top 35.87, side 36.20 at z=14. base_t re-solves (17.8 → 17.9 mm) and 750 ml is preserved.
* **Variant B cost**: 808k glass vertices against 160k. Render time was about 10 % higher on GPU at 900 px and 64 samples.

### Result

`r_B_full_34.png` against `r_A_full_34.png`:

* The vertical corners now read as two crisp facet lines with a flat chamfer between them, as in raw1 and raw2.
* The arch draws one clean line across each face.
* The heel reads as cut glass.

Still visible in B and handed to the shoulder work:

* ripples over the corner arch (pchip curvature jumps)
* waviness on the upper dome
* the ring at the neck root (the inner step at 185)
