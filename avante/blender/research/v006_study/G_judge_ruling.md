# G: Judge's ruling on the v006 shoulder study (A–F)

This is a study only. No project file was edited, nothing went into git, and the Blender GUI was not used. I read all six reports in full.

**Images I inspected:**
- `critic2_sheet_front`, `_34`, `_label`, `_shoulder`
- `critic2_zoom_chamfercap`, `critic2_r4_wrap_shoulder`, `critic2_r4_plane_fullhero`
- `b6_v006_zebra_tq` and `b6_P1_archrows512_zebra_tq`
- `raw2`, `renders/v005_threequarter`

**Code I read:** `build_avante_master.py` (constants, `shoulder_R`/`dome_cut`/`sq_radius`, `inner_*`, `build_glass`, `surf_xyz`) and the `critic2_proto.py` structure.

**My own check.** I recomputed the soft-min to fillet conversion with the vertex-gap method on the real `sq_radius` geometry (S = 87.7, CHAMFER 0.0754). The result is **R_gap = 7.91·k at every k from 0.07 to 0.7**. That confirms E exactly: EDGE_SOFT 0.07 gives R 0.55, 0.12 gives 0.95, 0.125 gives 0.99, and 0.7 gives 5.5.

---

## 1. Rulings

| # | Disputed point | Winner | Ruling and evidence |
|---|---|---|---|
| 1 | **Arch apex and corner heights** | **B/E (A agrees)**. C is overruled. | **Sharp crease:** panel centre **156.6** (B/F). E's 157.0, fitted directly on raw2, is within the ±0.7 error. Corner (face/chamfer vertex) **145.9–146.7**. Rise ≈ 10.5–11.<br>**Visible onset at ρ 4:** centre **155.35**, corner **144.4** (F `critic2_analysis.json`).<br>**Evidence:**<ul><li>E's raw2 iso-darkness contour drops 1.6 / 5.0 / 11.7 mm against 1.6 / 4.9 / 10.5 predicted for a 53° cone cut by the panel plane, so the reference arch is a plane∩cone hyperbola.</li><li>C's 160.5 / 150.5 is a label requirement, not a measurement. It would widen the front silhouette by about 9 mm at z 160 (raw2 measures 80.9).</li><li>B's "4.4 mm low at the centre" compared a carving onset with a sharp crease. v006's centre height is within about 1 mm; its corners are 5–7 mm low.</li></ul> |
| 2 | **Shoulder cone and fillets** | **B, built by F**; E's numbers corroborate | **Cone:** a straight cone, R = 40.16 − 1.2869·(z − 160) (52.1° from vertical), fitted to PROFILE. E's raw2 fit, 44.5 − 1.33(z − 157), differs by ≤ 0.5 mm over 157–170, so the PROFILE fit wins because it keeps the PROFILE checks and was proven 11/11 in F.<br>**Neck fillet:** ρn **20.5** (B; E 21–22 on raw2, all within ±3).<br>**Knuckle:** this is not a separate parameter; it is the arch fillet ρ at the panel centre (row 3).<br>**D is overruled** on knuckle 4–5 and neck 5–6. D read only a few rows; E's three-line vertex-gap method gives 9.2 and 22.<br>**Delete** `shoulder_R`'s Hermite ease, which has zero slope at 131 and causes the 45° grazing corners. B's zebra (`b6_v006_zebra_tq`: lens islands, kinked rings) against P1 (`b6_P1_archrows512_zebra_tq`: straight radial stripes, one clean arch band) settles this visually. |
| 3 | **Arch fillet character (ρ / ARCH_K)** | **B's rolling-ball ρ**, value **4.0**. D's ARCH_K 0.25 is rejected. A/E's ARCH_K is superseded. | **What is deleted:** the soft-min dome. Exact rolling-ball `round_intersect` with **ρ = 4.0** and **ρ_in = 5.0** replaces it.<br>**Why not D:** D's ARCH_K 0.25 → "R3" is wrong by about 2× (E: R_gap 5.1·k at the arch).<br>**Choosing ρ:**<ul><li>E shows raw2's panel-centre knuckle is about 9 and its corners crisper. The client asked for less bevel, but called the v006 arch (R ≈ 12.5) "good".</li><li>ρ 4 is the prototyped middle. Front silhouette deviation 0.58 against ±0.7, and F reports ρ3 and ρ4 nearly indistinguishable.</li><li>ρ 3 is held in reserve: switch to it **only if the client picks Route 1**, because it buys the 0.4–0.5 mm needed for a 3 mm art margin.</li><li>Do not go below 3 (E).</li></ul> |
| 4 | **Vertical edge radius / EDGE_SOFT** | **E (and A)**. D's conversion is wrong; F's 0.07 is too sharp. | **Target:** R 1.0 mm. **EDGE_SOFT = 0.125**, giving R_gap 0.99 and R_spread 1.18, as I verified (7.91·k).<br>**Against 0.07:** D's 0.07 gives R ≈ 0.55. It looked fine in F because the refs are resolution-limited (≤ 1–1.5). But it is sharper than any glass works produces, and it is more mesh-sensitive.<br>**Mandatory:** `sq_radius` must call the stable `softmin()`. The raw `exp(-r/k)` underflows below k ≈ 0.078 (E) and crashes.<br>This is the main cause of "overly bevelled": 5.5 mm now against ≤ 1.5 in the refs. All agree. |
| 5 | **Chamfer width** | **Keep 0.0754** (E, F, and A/D's own advice) | E falsified the band-width method on our own render: a true 0.0754 leg shows only a 0.033 W hairline band, the same as raw2. So raw2 is consistent with 0.04–0.09 W. The label dieline (HF_E/S1_E/TRIM) is built on 0.0754. EDGE_SOFT fully explains the bevel complaint. Revisit only with a supplier drawing. "W2124" has no source in the repo. |
| 6 | **Heel bevel** | **D's shape, E's numbers** | Flat bevel at **32°** from vertical. Top break at **z 8.5**. Footprint corner at z 0, inset **5.3** (hw 35.85 → 30.55; raw2 gives W 61.0 at z 0). **R 1.0** at both breaks. The plan view follows the octagon.<br>Built as F's `fillet_polyline`. The PROFILE pchip cannot hold a flat facet. raw1's rounded heel is excluded, because raw1 is not the Imperial (E §1: neck 7 % narrower, knuckle 3 mm lower). |
| 7 | **Punt / inner floor** | **E**, at medium–low confidence | raw2 shows a straight inner-floor line, which gives about 17.4 mm against the solved 17.8. A 3.5 mm dome would bow it by about 5 px.<br>Set **PUNT_H = 0.0** and **HEEL_R (inner) = 5.0**, and let the base re-solve. This only affects renders. Confirm with the supplier drawing if one appears. Keep the outer 1.2 mm push-up cone. |
| 8 | **Sampling / mesh density** | **D, as built by F**. B's uniform 512 is superseded. | **θ:** 384 uniform plus ±24 steps of 0.0018 rad around the 8 vertex angles (`atan(1 − 2·CHAMFER)` + k·90° and its mirror), 776 per ring. That puts ≥ 8 vertices across each R1 fillet.<br>**Rows:** follow the arch (`row_z`, separate inner and outer). Spacing 0.15 mm in [ZA0 − 6, ZA0 + 5], 0.3 mm over 138–194, 0.08 mm along the heel fillet arcs, 1 mm elsewhere.<br>**Shading:** plain smooth, with no auto-smooth angle, no subsurf and no weighted normals.<br>**Cost:** about 4.2× the vertices, with acceptable GPU time (F). |
| 9 | **Chamfer-cap dark points** | **F's diagnosis and fix** | I saw them in `critic2_zoom_chamfercap.png` (right panel): four sub-mm dark ticks at the cap corners, where the ρ4 arch fillet meets the R1 vertical fillets with no vertex blend.<br>**Fix:** ramp the vertical-edge k with height relative to the crease on that ray: k(θ, z) = 0.125 + (0.35 − 0.125)·smoothstep((z − (ZA(θ) − 6)) / 6). That gives R ≈ 2.8 at the crease, a setback-style vertex blend.<br>The ramp sits entirely above the label onset band, so it does not touch the label datums. This is required before any macro shot. |
| 10 | **"Lower shoulders"** | **Too low (A/B/C/D/E)**. F's alternative reading is rejected. | The feedback reads "the bottle has changed **more** now", so every item is a regression from v005.<ul><li>v006 corners dropped from 155.5 (v005) to about 140 (onset 138–140).</li><li>The 45° diagonal width at z 150 fell 116.4 → 99.3.</li><li>Nothing asks for a lower shoulder; Route 2 would make it higher than the reference, not lower.</li></ul>**Result with the fix:** onset corners 144.4, diagonal at 150 = 106.1, so 7 of the 17 mm lost come back. The rest is the arch the client approved (row R1 in §4). |
| 11 | **Uneven surface above the shoulders** | **B's description; A's list** | **The cause** is the S-curve dome with a curvature jump at 157.5, the PCHIP knot ripple revolved into rings, the Z_HOLD break at 152.5 (about 1° per E) and the bore step at 185.<br>**The fix:** cone + fillets (no PCHIP above Z_HOLD in the outer surface), **Z_HOLD 147.5**, a C1 bore blend over 181–189, and PROFILE (140, 87.7) → **(140, 88.1)**. The last uses raw2's own value and softens the 140–145 belt under the new corner onset. |
| 12 | **Wall** | **B** | Offset the inner wall along the surface normal: `G_in = G − WALL·q` with q = √(1 + M²). This gives a true 3.6 mm wall on the cone instead of 2.2. Base thickness re-solves to about 16.7. |

---

## 2. Label conflict: what to build NOW and what goes to the client

**The facts (agreed by E and F, confirmed in the images):**
- The approved crown at the front centre is z 158.47, above even the reference *sharp* crease at 156.6.
- The crown's 9.9 mm drop across the face is parallel to the glass arch's 10.5. It is a translation of about 3–5 mm, not a shape mismatch.
- No die or datum change alone can make a flat label clear reference-true glass.
- **The dieline and the datums also disagree internally:** the dieline is 88.80 mm long, the datum span is 86.26. The 79.64 crown datum exists only because the top 10.4 mm was assumed to lie on a 49° facet.

**What each option does:**

| Option | Keeps approved items? | Physically sound? | Matches raw2 glass? | Verdict |
|---|---|---|---|---|
| Route 1: rev D.2 die, top edge = onset − 2 (−1.5 at s 10–20), crown ≈ 84.7 | No: die and crown datum change | Yes | Yes | **Recommend to the client** |
| E's option: crown ≈ 6 mm lower, ρ 5 | No | Yes | Yes | The same decision as Route 1 with a softer ρ. **Merged into Route 1.** |
| Route 2: raised/flattened shoulder (R0 47.4, M 1.6) | Yes | Yes | **No**: up to 6.2 mm per side wider at 160–170, knuckle about 5 mm high | Viable only with a custom mould. The 226.9/89 glass is a supplier bottle, so Route 2 renders would misrepresent what is bought. **Do not build now.** |
| Plane label + D.1 (C) | No (D.1 is a die change) | Isometric, but stands as a **3.5 mm flag** that pokes past the silhouette (`critic2_r4_plane_fullhero`) | Yes | **Reject for renders.** Keep it only as the check geometry for clearance and isometry. |
| B's sin(atan 1/M) mapping | Fails the crown datum (81.10) | 38.5 % squash | Yes | Reject |

### Build NOW, no sign-off needed: interim "approved label on true glass"

- **Glass:** fully reference-true (§3).
- **Label:** keep the rev D die, the TRIM and both datums **exactly as approved**. Keep the existing z mapping: v ≥ 0 → z = Z_EDGE − v, and v < 0 → z = Z_EDGE + |v|·sin 49°. That holds the crown at 79.63 and the bottom at 165.9.
- **Where the label sits:**
  - The label lies on the glass, through `outer_r`.
  - Below the arch onset, `outer_r` *is* the flat panel. On the new glass the label is therefore flat and isometric over everything except the top 3–5 mm of the crown band.
  - Within that band, the label folds over the ρ4 fillet onto the cone. This is the same visual contract as the approved v005, where the crown folded over the facet crease (`v005_threequarter`).
  - In F's `critic2_r4_wrap_shoulder` render this reads cleanly. That is the opposite of v006, where the label rode a 45° dome from 138 upward with 42 % strain and corner pillows.
- **Perimeter mapping:** map the perimeter by arc length along the filleted section (C). This removes the 18 % fold-fillet artefact.
- **Why this is acceptable:** every printed element stays on flat glass. The topmost art (spear tip, dieline y +1.58 at s 15 → z ≈ 149.0) is 4.1 mm below the onset of 153.15 there, so no artwork is distorted. Only blank navy crosses the arch.
- **Report the nonconformity explicitly in check output and the delivery note:** die-edge clearance −3.1 (centre) to −4.8 mm (fold), and the crown-band strain. Show both as **WARN**, outside the 11 pass/fail checks.

### Client decision (send with v007 renders)

> **The approved label crown (79.64 mm from the cap) sits 3–5 mm higher than the point where the real Imperial bottle's shoulder starts to curve. Which way do you want to resolve it?**
>
> 1. **Lower the top edge of the label to follow the shoulder arch (recommended).** The die top edge drops about 5 mm, and the crown datum moves from 79.64 to about **84.7 mm from cap**. The bottom stays at 165.9, and the artwork and crown shape are unchanged. The label sits fully on flat glass with 1.5–2 mm clearance, so it applies cleanly with no darts and no lifting. The clearance above the spear tip falls to about 2–3 mm. Needs your sign-off and the printer's (new die, rev D.2).
> 2. **Keep the label exactly as approved.** No artwork, die or datum changes. The top 3–5 mm of the crown folds over the curved shoulder edge, which is how the renders show it. On the production line the felt-paper stock may crease or lift there. **This needs an application trial on real Imperial bottles with your printer and labeller before the print run.** If the trial fails, you fall back to option 1 late in the schedule.
> 3. **Change the bottle to a custom mould with a higher, flatter shoulder.** It keeps the label and all datums, and the label clears. The bottle is no longer the stock Imperial: it is up to 6 mm per side wider at the shoulder and reads squarer. That means mould cost and lead time.

---

## 3. Final parameter spec and implementation order

Port the proven code from `diag/critic2_proto.py`, which F showed passes 11/11 and holds 750 ml. Where this spec differs from F, the values below win: **EDGE_SOFT 0.125, not 0.07; label mode "approved" by default; PUNT_H 0; HEEL_R 5; heel 32° from z 8.5; PROFILE 140 = 88.1; the cap k-ramp**.

### 3.1 Constants block (top of `build_avante_master.py`)

```
PROFILE[(140, 87.7)] -> (140, 88.1)            # raw2 value; softens the 140-145 belt
Z_HOLD          = 147.5                        # was 152.5; PROFILE slope 0 here, so no C1 break
# delete Z_ARCH_C, Z_ARCH_F, ARCH_K, _SR
CONE_R160       = 40.16                        # cone radius at z=160 (LS fit, PROFILE 160-172.5)
CONE_M          = 1.2869                       # -dR/dz; 52.1 deg from vertical
NECK_R          = 17.05                        # NECK_D/2
NECK_RHO        = 20.5                         # concave neck fillet; tangent z 171.8 -> 188.0
SHOULDER_RHO    = 4.0                          # arch rolling-ball radius (3.0 only if the client picks Route 1)
SHOULDER_RHO_IN = SHOULDER_RHO + 1.0
EDGE_SOFT       = 0.125                        # radial soft-min width; R_gap = 7.91*k = 0.99 mm
EDGE_SOFT_CAP   = 0.35                         # k at the arch crease (chamfer-cap vertex blend, R~2.8)
THETA_UNIFORM, THETA_CLUSTER, THETA_STEP = 384, 24, 0.0018   # -> 776 per ring
CHAMFER         = 0.0754                       # unchanged
PUNT_H          = 0.0                          # raw2: flat inner floor
HEEL_R          = 5.0                          # inner heel fillet
HEEL_TOP_Z, HEEL_INSET, HEEL_FILLET = 8.5, 5.3, 1.0   # 32.0 deg outer bevel
BORE_BLEND      = (181.0, 189.0)
LABEL_MODE      = 'approved'                   # 'approved' (rev D, datums held) | 'revD2' (Route 1, after sign-off)
```

### 3.2 Formulas

**Generatrix G(z), revolved:**
- Cone, for z ≤ zt = 171.8: G = CONE_R160 − CONE_M·(z − 160).
- Neck fillet, for zt < z < 188.0: G = rc − √(ρn² − (z − zc)²), with rc = NECK_R + ρn and zc = 160 + (ρn·√(1 + M²) − rc + R0)/M = 188.0.
- Neck: G = NECK_R from 188 to 190. Above 190, keep the existing `width_at/2` finish.

**Prism:** P(θ, z) = `sq_radius(θ, width_at(min(z, Z_HOLD)), k(θ, z))`, where:
- `sq_radius` = `softmin(r1, r2, k)` (stable form).
- k(θ, z) = EDGE_SOFT + (EDGE_SOFT_CAP − EDGE_SOFT)·smoothstep((z − ZA(θ) + 6)/6).
- ZA(θ) = 160 + (R0 − P(θ, Z_HOLD))/M is the sharp-crease height on that ray.

**Outer surface:**
- Take the root in r ∈ [0, P] of `round_intersect(dA, dB, c, ρ) = 0`, with:
  - dA = (r − P)·cp, where cp = P/√(P² + P_θ²)
  - dB = (r − G)/q, where q = √(1 + m²) and m = −dG/dz
  - c = cp/q
- Use 40–48 bisection steps, vectorised in numpy (B §3.1, F).
- Below 190 the `roundness()` blend is a no-op for the outer surface; keep it for the finish only.

**Inner surface:**
- P_in = P − WALL/cp and G_in = G − WALL·q, with ρ_in = 5.0.
- The bore is r_in → BORE/2 by smoothstep over 181–189.
- The inner prism uses `inner_width(z)` with the inner heel R 5 and a flat floor.

**Heel:**
- Outer (half-width, z) polyline: [(hwF − 6, 0), (hwF, 0), (35.85, 8.5), (36.20, 14.0)], with hwF = 35.85 − 5.3 = 30.55.
- Fillets R 1.0 at (hwF, 0) and at (35.85, 8.5), sampled at 0.08 mm.
- Each sample is a body ring at S = 2·hw.

### 3.3 Implementation steps (in order, mapped to builder functions)

1. **Constants:** apply §3.1.
2. **`sq_radius(theta, S, k=EDGE_SOFT)`:** switch to `softmin()` and add the k argument. This removes the underflow crash.
3. **Replace `shoulder_R`, `dome_cut` and `outer_r`:**
   - Add `cone_G(z)` and `cone_slope(z)`, `round_intersect()`, `crease_z(theta, inset=0)` (ZA) and `prism_r(theta, z)` with the k ramp.
   - Add `outer_r(theta, z)` (bisection). Add a vectorised `outer_r_np(thetas, z)` for meshing.
   - `body_S(z) = width_at(min(z, Z_HOLD))`.
4. **Inner:**
   - Add `inner_r(theta, z, base_t)`: normal offset, ρ_in, bore blend.
   - Rewrite `inner_width` so it has no `z >= 185` switch, and so it keeps the inner heel with HEEL_R 5.
   - `inner_stack` handles PUNT_H = 0, so the floor ring collapses to a flat fan.
5. **Volume:**
   - `section_area` and `inner_volume` integrate `inner_r` over 360 θ. Drop the punt subtraction when PUNT_H = 0.
   - `solve_base_thickness` is unchanged. Expect about 16.7–17.0 with the flat floor.
6. **Sampling:**
   - Add `theta_samples()`: 776 angles, clustered at `atan(1 − 2·CHAMFER) + k·π/2` and its mirror.
   - Add `v_samples()` with the arch, neck and heel densities from row 8 in §1.
   - Add `row_z(theta, v)` from F, with separate inner and outer crease functions.
   - `z_samples` remains for the capsule and labels.
7. **`build_glass`:** heel polyline rings for z < 14, then arch-following outer rows. Inner rows use the inner `row_z`. `loft` is unchanged. Plain smooth shading: change `shade_smooth` to accept `angle=None` → no auto-smooth.
8. **`build_liquid`:** inner surface inset WALL − OV, using arch rows that blend over about 30 rows into the flat fill plane at FILL_Z 160.9 (F). Keep the meniscus.
9. **Capsule:** `capsule_raw` and `capsule_profile` already call `outer_r`, so only verify that the hem (CAPSULE_BOTTOM 171.83) sits on the cone or neck fillet. Cache `outer_r(0, z)` for speed.
10. **Label (`surf_xyz`, `build_wrap`):**
    - Use arc-length perimeter mapping on the filleted held section at z.
    - Use `r = outer_r(th, z) + off`. This is flat panel below the onset and folds over the fillet above it.
    - Keep the sin 49° v < 0 branch while `LABEL_MODE == 'approved'`.
    - Add a `'revD2'` branch, used only after sign-off: no sin 49, true length on panel planes, D.2 TRIM = onset(s) − 2 (−1.5 at s 10–20) per `critic2_analysis.json`, and switch ρ → 3.0.
11. **Studio:** add `CAM_Shoulder` (z ≈ 155, long lens ≥ 135 mm, front and 3/4). The hero at z 130 looks up at the arch and biases "lower shoulder" judgements (E §10.6).
12. **`check_avante_master.py`:** add the checks in §3.4.

### 3.4 Acceptance checks to add

New FAIL-level checks are numbered after the existing 11. They are computed analytically from the builder functions where possible.

| # | Check | Target |
|---|---|---|
| 12 | Arch onset (0.05 mm carve): panel centre / face–chamfer vertex | 155.35 ± 0.5 / 144.4 ± 0.7 (ρ4) |
| 13 | Sharp crease: centre / corner; rise | 156.6 ± 0.5 / 145.9 ± 0.7; 10.0–11.5 |
| 14 | Front silhouette against PROFILE, z 140–192 | max abs ≤ 0.7 (expect 0.58) |
| 15 | 45° diagonal width at z 145 / 150 | ≥ 115.5 / ≥ 105.0 |
| 16 | Cone fairness: \|outer_r(θ, z) − G(z)\| on θ ∈ {0, 20°, 40.34°, 45°} between fillet exit and 171.8 | ≤ 0.01 mm; no sign change of d²r/dz² over [ZA + ρ, 171.8] |
| 17 | No slope breaks: \|Δ slope\| across 147.5, 171.8 and 188.0, at every θ | < 0.1° |
| 18 | Vertical edge R_gap (vertex-gap method) at z 40 / 100 / 140 | 1.0 ± 0.15 mm; ≥ 8 vertices across each fillet arc |
| 19 | Chamfer cap: maximum normal angle between adjacent faces within ±3 mm of each cap corner | < 3° (and a macro render with no dark ticks) |
| 20 | Heel: bevel angle / top z / footprint hw | 32 ± 1.5° / 8.5 ± 0.3 / 30.55 ± 0.3 |
| 21 | Inner bore: maximum radius step between adjacent rows over 181–189 | < 0.05 mm |
| 22 | Wall thickness measured along the normal on the cone (z 160–170) | 3.6 ± 0.2 |
| 23 | Label datums (tightened from 0.6 / 3.5) | crown 79.64 ± 0.3, bottom 165.9 ± 0.5 |
| 24 | Artwork on flat glass: every foil, emboss or ink-art vertex has onset(θ) − z ≥ 1.5 mm and normal tilt < 3° | pass (expect ≥ 4.1 mm at the spear tip) |
| 25 | Label isometry below the onset (plane region): principal stretch | 0.995–1.005 |
| W1 | **WARN** (reported, not failed until the client decides): die-edge clearance = onset − label top, by s | expect −3.1 (centre) / −4.8 (fold) / +1.6 (5° into the side) |
| W2 | **WARN**: crown-band strain (dieline → 3D) for triangles above the onset | report max and p99 |

When `LABEL_MODE == 'revD2'`, W1 becomes FAIL-level at ≥ 1.5 mm (2.0 target), and #23's crown target becomes the new signed-off value.

---

## 4. Known residual risks

1. **R1, the 3/4 view may still read "lower than v005".** The diagonal width at 150 recovers to 106 against v005's 116. That gap is the arch itself, which the client approved, and it cannot be closed on reference glass. Mitigation: show v005, v006 and v007 side by side from `CAM_Shoulder`, and say so in the note.
2. **R2, the label is physically nonconforming under the interim build.** The crown band folds over a curved crease: lower-bound strain is about 1.2 % at the centre, and the fillet band is doubly curved. The render shows ideal application. The client decision closes this.
3. **R3, one constant ρ.** It cannot be soft at the centre (raw2 ≈ 9) and crisp at the corners at once. ρ4 is a compromise at 0.58 against a 0.7 silhouette tolerance. A θ-dependent ρ is possible later.
4. **R4, metrology rests on one CGI image.** raw2 is the only metric Imperial (raw1 is a lookalike; raw7 is a different bottle). Absolute heights are ±0.7–1.5 mm. The chamfer leg, the punt and the heel are not confirmed by any supplier drawing.
5. **R5, the chamfer-cap k-ramp is not yet prototyped.** It needs a macro render to confirm it removes the ticks without visibly widening the cap edges.
6. **R6, fill line.** FILL_Z 160.9 now sits on the clean cone above the inner crease (F handled the liquid blend). Re-check the meniscus against the normal-offset inner wall in a filled shoulder close-up.
7. **R7, cost.** About 4.2× the glass vertices (≈ 680k) and about 10–25 % more render time. Build time is about 30 s.
8. **R8, Route 1 art margin.** About 2.1 mm at the spear tip with ρ4, and 3 mm only with ρ3 and 1.5 mm local clearance. If the client picks option 1, the printer may ask to nudge the bird foil down about 1 mm, which is an artwork change of its own.

## 5. Order of work

1. Glass items (§3.3 steps 1–9, 11–12). No sign-off needed, and they fix all three glass complaints.
2. Interim label (step 10, 'approved' mode) with W1/W2 reported.
3. Send the client the question in §2 with the v007 renders: hero, 3/4, CAM_Shoulder, and a v005/v006/v007 strip.
4. On the answer: Route 1 → 'revD2' + ρ3 + D.2 TRIM. Option 2 → keep, and book the application trial. Option 3 → custom-mould study (F's `critic2_r4_high` parameters as the starting point).
