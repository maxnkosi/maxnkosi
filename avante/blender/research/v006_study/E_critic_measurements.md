# E: Critic's re-measurement of reports A–D (v006 shoulder, label, edges)

Study only. No project file was edited. Everything I wrote is in `research/v006_study/diag/` with the prefix `critic1_`:

| file | purpose |
|---|---|
| `critic1_load.py` | Loads the refs and renders through bpy and saves top-down RGBA `.npy` |
| `critic1_sil.py`, `critic1_prop.py` | Sub-pixel silhouettes; proportions normalised by W_max |
| `critic1_cone.py` | Least-squares cone fit, sharp-crease apex and corner prediction |
| `critic1_knuckle.py` | Knuckle and neck fillet radii by the vertex-gap method |
| `critic1_arch2.py`, `critic1_arch2b.py` | Iso-darkness arch contours across raw2's front face |
| `critic1_band.py`, `critic1_herorow.py`, `critic1_r7row.py` | Chamfer band profiles: raw2, raw1, raw7 and our own v006 hero |
| `critic1_heel.py` | Heel inset profiles |
| `critic1_model*.py` → `critic1_model*.txt` | Analytic checks on the builder functions (exec of `build_avante_master.py` above `materials`) and the exact soft-min → radius conversion |
| `critic1_*.png` | Enlarged crops: raw2/raw1/raw7 shoulder and base, raw5 shoulder, v006 hero edge |

**Scales.** raw2: the top outline is row 26 and the base is row 363.5, so H = 338 px and W_max = 133.43 px. z uses 226.9/338 = 0.671 mm/px; widths use 89.0/133.43 = 0.667 mm/px, a 0.6 % disagreement. raw1 and raw7 are width-scaled to W_max = 89.0, so their heights are relative only.

---

## 1. Are raw1 and raw2 the Imperial (226.9 × 89)?

| ratio (W/W_max unless stated) | raw2 | raw1 | raw7 (48Gin) | Imperial / model |
|---|---|---|---|---|
| H_glass / W_max | **2.533** | top hidden | top hidden | 226.9/89 = **2.549** |
| neck W | **0.379** | 0.351 | 0.352 | 34.1/89 = 0.383 |
| z where W = 0.90 W_max (width-scaled mm) | 159.0 | 156.7 | 156.4 | 160.0 (PROFILE) |
| z where W = 0.50 W_max | 173.3 | 170.2 | 168.9 | 173.8 |
| W at z 10 / 20 | 0.800 / 0.812 | 0.768 / 0.785 | 0.793 / 0.808 | 0.804 / 0.820 |
| cone angle from vertical | 52.7–53.4° | 53.6–54.0° | 55.4–56.8° | 53.0° |
| heel | flat 32° bevel | rounded, R ≈ 5 | small 4–5 mm bevel | PROFILE pchip |

**raw2 is consistent with the Imperial.** Its H/W is within 0.6 % of the supplier figure, which is about 1.4 mm on the height and inside the ±1 px edge error.

**raw1 is a lookalike or a different mould, not the same bottle.**
- Its neck is 7 % narrower relative to the body.
- Its shoulder knuckle sits about 3 mm lower and is softer (R 11.7 against 9.2).
- Its heel is rounded rather than bevelled, and its lower body tapers more.
- A raised camera can compress heights by 2–3 %. It cannot make a nearer neck look narrower.
- raw1 is actually closer to the 48Gin (raw7) than to raw2.

**Verdicts.** A treats raw1 as a second "clear Imperial" and averages it into ranges: partly wrong. D uses raw1 for the chamfer, knuckle and neck values: wrong source. Use raw2 as the only metric Imperial reference and raw7 only for the family character.

---

## 2. Arch apex at the panel centre

**Method.**
- In front view, the silhouette is the meridian through the side-panel centre. The knuckle on that silhouette is therefore the arch apex seen edge-on.
- I fitted a straight line to the raw2 half-width over W/W_max 0.60–0.85. The result is dR/dz = −1.331 (53.1° from vertical), rms 0.09 mm, max 0.15 mm, so the cone is straight.
- I extended that line down to R = 44.5. That point is the sharp-crease apex.

| | sharp crease apex | filleted (tangent on panel) |
|---|---|---|
| raw2, fit 0.60–0.85 / 0.55–0.90 | **157.1 / 156.9** | ≈ 157.0 − 0.50·R_knuckle = **152.4** for the measured R 9.2 |
| raw7 (relative) | 153.4–153.5 | – |
| v006 model, same method on the analytic `outer_r(0, z)` | 156.7 (vertex) | carving onset 151.4 (0.05 mm) / 153.2 (0.2 mm) |

**Independent check from the clear glass.** I traced an iso-darkness contour (darkness > 0.03) across raw2's face. It sits at 158.4 in the centre, 156.8 at y = ±14, 153.4 at ±24.6 and 146.7 at ±38.
- A 53° cone cut by the plane at 44.5 predicts drops of 1.6, 4.9 and 10.5 mm at those positions. The measured drops are 1.6, 5.0 and 11.7.
- So the clear Imperial's arch **is** a cone-and-plane hyperbola.
- C's statement that the real Imperial has "a straight faceted shoulder, exactly what the 49° crown was drawn for" is **wrong**. A pyramid would give a flat contour, and the cone is 53°, not 49°.

**Error.** ±0.7 mm (scale 0.3 % plus fit 0.2 plus threshold bias). The absolute level of the contour is biased by about +1 mm, but its shape is reliable.

**Verdicts.**
- **A ≈155: partly.** A's 156.3 knuckle vertex is right; its "≈155" is a filleted reading of something between sharp and tangent and is not stated precisely.
- **B 156.7: confirmed** as the sharp crease.
- **C 160.5: wrong for the real bottle.** It is a requirement derived from the label, not a measurement. It puts the sharp apex 3.5 mm above raw2.
  - Raising the cone by 3.5 mm would widen the front silhouette by 2 × 1.33 × 3.5 ≈ 9 mm at z 157–160. raw2 measures 80.9 mm at z 160, against about 90 needed. So **C's glass requirement is incompatible with the refs.**
  - C's "v006 is 9 mm too low at the centre" is measured against that requirement. Against raw2, v006's panel centre is within about 1 mm in height. v006's front width at 155/157.5/160 is 87.6/85.0/80.2 against 88.8/86.0/80.9.
- **B's "v006 4.4 mm low at the panel centre" is apples to oranges.** It compares a carving onset with a sharp crease. At the centre, v006's fault is softness, not height (see §5).

**Build:** cone R(z) = 44.5 − 1.33·(z − 157.0), giving a sharp apex at 157.0. The visible tangent line is 157.0 − 0.5ρ.

## 3. Corner end of the arch

The sharp corner end follows z_corner = z_apex − (r_corner − h)/m, with m = 1.33. **The reports missed that this depends on the chamfer leg a,** through r_corner = √(h² + (h − a)²):

| leg a | 3.5 | 4.0 | 4.5 | 5.0 | 6.7 (model) |
|---|---|---|---|---|---|
| raw2 corner z (sharp) | 145.1 | 145.3 | 145.6 | 145.9 | **146.7** (146.4 with the wider fit) |
| arch rise | 12.0 | 11.8 | 11.5 | 11.3 | 10.4–10.6 |

The raw2 contour gives 146.7 at y = ±38. With a fillet of radius ρ, the tangent line at the corner sits about 0.6ρ lower, so ≈ 143–144 for ρ ≈ 4–5.

**Verdicts.**
- **A 145–147: confirmed.**
- **B 146.0: confirmed** (within 0.5 mm).
- **C ~150.5: wrong for the refs.** It is the label requirement, 4–5 mm above the measured corner.
- v006 starts carving at the face/chamfer vertex at **137.9 (0.05 mm) or 140.0 (0.2 mm)**. That is 5–7 mm low, which is the real "lower shoulders". A, B and C all agree on the v006 numbers once the tolerance is matched.

**Build:** with CHAMFER 0.0754, the sharp corner end is 146.4–146.7; it falls out of the cone automatically.

## 4. Shoulder form, knuckle and neck fillet

**Method.** Fit three lines (plateau z 142–150, cone, neck z 190–210), intersect them, take the minimum distance from each vertex to the silhouette polyline, then R = gap / (1/cos(T/2) − 1).

| | cone from vertical | knuckle R (panel-centre arch, edge-on) | neck fillet R (concave) |
|---|---|---|---|
| raw2 L / R | 53.4° / 52.8° | **9.1 / 9.3** | **22.0 / 21.9** |
| raw7 | 55.4–56.8° | 7.0 / 7.0 | 21.3–22.2 |
| raw1 (lookalike) | 53.5–54.0° | 11.5–11.9 | 24–26 |
| v006 `outer_r(0, z)` | 53.0° | **12.5** | 19.7 |
| v005 (PROFILE) | 53.0° | 9.4 | 19.7 |

Error: ±0.2 mm on the gap, so knuckle R ±2 mm and neck R ±3 mm.

**Verdicts.**
- Straight cone at 52.5–53°: **A and B confirmed** (B's 37.9° from horizontal is 52.1° from vertical). A's raw1 51.1° is not reproduced (I get 53.6–54.0°).
- Knuckle: **A 10.6 and B ≈8 confirmed.** **D's 4–5 mm is wrong**, since D read only the last few rows.
- Neck: **B 20.5 confirmed.** A's 17.2 for raw2 is about 20 % low. **D's 5–6 mm is wrong** by roughly 4×.
- v006's 45° dome at the corners (`shoulder_R` slope −0.94 to −1.01 between z 144 and 152): **A confirmed.**

**Build:** a straight cone at 53° (m = 1.33). The neck fillet is R 21, tangent at about 172 and 188. The panel-centre arch fillet is in §6.

## 5. Surface defects in v006, checked

| claim | my number | verdict |
|---|---|---|
| A: "5–6.5° crease ring" at 157.5 | The slope is continuous (C1). At θ 40°, the angle from vertical falls 40.3 → 37.2 between z 156 and 157.5, then rises to 42.5 by 158.0. At θ 0 it goes 31.5 → 38.1. This is an inflection with a curvature jump (about 5° in 0.5 mm, local R ≈ 6). | numbers **confirmed**; calling it a "crease" overstates it. **B's description (S-curve plus curvature jump) is the accurate one.** |
| D: 0.96° kink from the `mf` finite difference | `shoulder_R` slope is 37.8° at 157.4 and 38.1° at 157.6, i.e. 0.3° | **partly**; the slope break is not the issue, the curvature reversal is |
| Z_HOLD crease, 1.9° (A, D) | at θ 0 the slope goes 6.55° → 5.58° across 152.5, about 1° | **partly** (smaller, but real) |
| Concave dish 150–157.5 (A, B) | `shoulder_R` flattens from 45.4° (z 148) to 37.8° (z 157.4) | **confirmed** |

## 6. Edge radii: the soft-min → radius conversion, checked numerically

Soft-min of two straight lines is exactly self-similar in k, so the equivalent radius must be **linear in k**. I sampled at 200 001 rays near the vertex. Three definitions of the equivalent radius:
- **R_min:** the minimum radius of curvature.
- **R_gap:** the radius of a true fillet that leaves the same gap from the sharp vertex.
- **R_spread:** a true fillet spreading 90 % of the turn over the same arc length.

| edge | R_min / k | R_gap / k | R_spread / k |
|---|---|---|---|
| vertical face/chamfer edge (45° turn, vertex at θ 40.34°, ray 17.8° off the bisector) | 5.4 | **7.9** | **9.4** |
| panel-centre arch (vertical face against a 53° cone, horizontal radial blend) | 3.4 | **5.1** | **6.1** |

The ratios are constant to 0.1 from k = 0.05 to k = 1.2.

**Vertical edges**
- EDGE_SOFT 0.7 gives R_gap 5.5 / R_spread 6.6 / R_min 3.8. **A's 5.9 (min 3.8) and D's 6.8 are both right** for their own definitions.
- **A: EDGE_SOFT 0.12–0.18 → R 1.0–1.5: confirmed** (R_gap 0.95–1.42).
- **D's calibration is wrong at small k.** k 0.10 → 1.6 and k 0.07 → 1.1 are a sampling floor. The true values are 0.79–0.95 and 0.55–0.66. D's rule "R ≈ 13–16·k" should be 7.9–9.4·k.
  - D's EDGE_SOFT 0.07 therefore gives **R ≈ 0.6**, not 1.1.
  - In the current `sq_radius` it also **crashes**: at the corners r/k = 58/0.07 ≈ 830 > 745, both exps underflow, and `log(0)` raises. D noted the underflow, putting the onset at k ≈ 0.065; the true onset is about 0.078.
- **References.** The hairlines in raw1 and raw2 are 1–2 px at 0.67–0.74 mm/px, so R ≲ 1–1.5 mm. That is resolution-limited; the images cannot tell 0.5 from 1.5.
- **Build:** R ≈ 1.0, i.e. **EDGE_SOFT 0.11–0.13**, using the stable `softmin`. The cleaner route is D's true Minkowski fillet at R 1.0.

**Arch edge**
- **D: ARCH_K 0.25 → R3: wrong.** It gives R_gap 1.3 / R_spread 1.5 at the panel centre. D's general "10–13 × k" also overstates by about 2×.
- **A: ARCH_K 0.6–0.8** gives R_gap 3.1–4.1, which is **consistent with B's 3–4 mm.** A, B and D only disagree because D's conversion is wrong.
- **What the refs say.** At the panel centre the arch is soft: R 9.2 (raw2) and 7.0 (raw7), read from the silhouette. Toward the corners it is crisper. The raw2 contours at thresholds 0.03 → 0.12 span 2.4 mm at y = ±37 against 6.4 mm at y = ±30, and raw5's corner highlight is a narrow line.
- So B's ρ 3–4 and D's target are **crisper than the Imperial** at the panel centre. Their front-silhouette deviation (≈ (9.2 − 3.5)·0.117 ≈ 0.67 mm) is at the edge of the ±0.7 tolerance.
- v006's 12.5 at the centre comes mostly from the flattened dome, not from ARCH_K. On a straight cone, the same k = 1.2 would give R_gap 6.1.
- **Build:** a constant rolling ball of **ρ ≈ 5 mm** on the straight cone. That gives 154.5 at the centre and a silhouette within 0.5 mm of raw2. If the soft-min route is kept, use **ARCH_K ≈ 1.0 on a straight cone** (R_gap ≈ 5 at the centre, slightly crisper at the corners where the crease is inclined). Do not go below about 3 unless the client explicitly wants it crisper than the reference.

## 7. Chamfer leg

**Re-measured.** Averaged edge profiles over 140 body rows:
- raw2: a dark band of 5.0 px = 3.4 mm containing two lines about 3 px apart.
- raw1: 4.5–6 px = 3.3–4.4 mm.

That reproduces A's and D's band of **0.038–0.049 W**.

**But the method is not validated, and I falsified it on our own render.**
- In `v006_hero.png`, row 1180, the true chamfer leg is 0.0754 W, about 31 px.
- The visible hairline pair sits within **13.5 px = 0.033 W** of the silhouette (lines at +4–6 and +13–14 px). The face/chamfer edge at +31 px is nearly invisible (`critic1_v006hero_edge.png`).
- The line spacing is even the same as raw2's: 0.022 W.
- In clear glass against a uniform background, the visible lines come from wall refraction and total internal reflection, not from the facet edges. **A band of about 0.04 W is consistent with a leg anywhere from about 0.04 to 0.09 W.**
- raw7 (matte) has a smooth gradient with a highlight peak 5.5–6 mm from the silhouette, which suggests a leg of about 0.06–0.07 W. raw5's 3/4 facet-to-panel ratio is about 0.10 ± 0.03 projected, which is inconclusive and does not contradict 0.075.

**Verdicts.**
- **A (Imperial 0.04–0.05): not established.**
- **D (0.045–0.055): not established.**
- Both correctly advise keeping 0.0754 until the W2124 or supplier drawing is checked. There is no source for "W2124" anywhere in the repo.
- The client's "overly bevelled" is fully explained by EDGE_SOFT (R ≈ 6 against ≤ 1). It does not need a narrower chamfer.

**Build:** **keep CHAMFER 0.0754** (the label dieline is built on it). Fix the radius.

## 8. Base heel

Half-width inset relative to z 20, by height above the base:

| | profile | top break | footprint inset | angle |
|---|---|---|---|---|
| raw2 | linear from h 8.5 (0.7 mm) to h 1.0 (5.3 mm); crisp top break | ≈ 8–8.5 mm | 5.3 at h 1.3, 5.7 at h 0.7 | **≈ 32° from vertical** |
| raw7 | linear from h 5 to h 2.6 (≈ 37°), then rounds into the foot (partly the perspective of the base ellipse) | ≈ 5 mm | ≈ 3 (before the foot) | ≈ 37° |
| raw1 | inset grows roughly quadratically from h 5: a **rounded** heel | – | 4.2 at h 0.7 | R ≈ 5 |
| model PROFILE | 10 mm tall, inset 4.0 at z 5 and 6.5 at z 1, 8.7 at z 0; wobbly pchip (D) | – | – | – |

**Verdict on D** (flat bevel 30–35°, 6–8 mm tall, 4–5 in): **confirmed for raw2.** "raw5 and raw7 show the same small bevel" is **partly** right: raw7's bevel is smaller (about 5 mm, about 37°). raw1 is rounded. Both A and D noted that.

**Build:** a flat bevel at **32°** from z 8.5 down to z 1.0 (inset 0 → 4.7), with R ≈ 1 at the top break and a footprint round of R ≈ 1 to an inset of about 5.5. The model's footprint at z < 1 is about 3 mm narrower in width than raw2's.

## 9. Label placement (C)

- **C's physical rule holds.** A wet-glue paper label must stay on developable glass, at least 1.5–2 mm below the arch tangent line.
- **The approved crown is above the reference arch apex.** The crown at the front centre is z 158.47 (Z_EDGE 150.6 + 10.414·sin 49°). That is 1.5 mm above even raw2's *sharp* apex (157.0) and about 4 mm above the tangent line for ρ 5.
- **So C's fix A (die rev D.1, crown "at 79.64 from cap on a flat panel") only works if the glass is also raised.** It therefore inherits the incompatibility in §2. All four reports missed this: A checked only the crown corners, and B moves the crown onto the cone (developable) but leaves it crossing the non-developable fillet band.
- **Good news.** The crown's drop across the front face (9.94 mm) is parallel to the reference arch drop (10.4–10.6). Only a translation is needed, not a reshape.
- **What it takes.** With ρ 5 and 2 mm clearance:
  - the crown centre must be at or below about 152.5, i.e. **about 6 mm lower** (85.6 mm from cap instead of 79.6)
  - the front/chamfer fold must be at or below about 141.4, i.e. about 7 mm lower
- **Options**, each of which needs client and printer sign-off:
  - trim the die top by about 6 mm and keep the bottom datum. The art clearance at the spear tip must be re-checked, because C's 6.0 mm margin after D.1 may not survive.
  - move the whole wrap down. This takes the roundel gap from about 6.6 to about 0.6 mm, so it is not viable.
  - accept a non-reference glass.

## 10. What all four reports missed (v006 renders against the refs)

1. **The chamfer leg sets the corner height of the arch.** See §3: about 1 mm per 2.7 mm of leg.
2. **The chamfer band-width method fails on our own render** (§7). Neither A nor D calibrated it.
3. **raw1 is not the Imperial** (§1). It is closer to the 48Gin.
4. **The panel-centre arch radius can be measured directly** as the silhouette knuckle: 9.2 mm in raw2 against 12.5 in v006. The refs show the arch soft at the centre and crisp at the corners, which no report's single target value captures.
5. **The approved crown is above the reference apex** (§9), so no die change alone fixes the label on reference-true glass.
6. **The hero camera does not match the reference viewpoint.** CAM_Hero is at z 130 mm, 740 mm away, with an 85 mm lens.
   - The camera is about 25 mm below the shoulder, so the client is looking up at the arch and cannot see the cone surface.
   - The front face is magnified about 6.4 % relative to the silhouette plane. raw2 is near-orthographic and raw7 is shot at shoulder height.
   - For shoulder reviews, add a long-lens camera at z ≈ 155. Otherwise, judging "lower shoulders" from the hero is biased.
7. **The fill line sits on the defect band (inferred, not rendered).** FILL_Z = 160.9 is inside the 157.5–161 curvature-jump band. The inner wall and liquid are radial insets of the same soft-min dome, and the wall measured normal to the cone is only about 2.2 mm (B noted the wall). So the meniscus and the inner surfaces probably amplify the "uneven surface" in filled renders. This should be checked with a glass-only against filled comparison at the shoulder.
8. **The inner floor is flat in raw2.** It is a straight dark line at row ≈ 337.5, giving a base thickness of about 17.4 mm. That agrees with the solved BASE_T of about 17.8, with shallow chamfered inner corners and **no visible punt dome**. A 3.5 mm dome would bow that line by about 5 px. The model's PUNT_H 3.5 and HEEL_R 12 are not supported by the Imperial reference.

## 11. Values I would build

| item | value |
|---|---|
| Shoulder | straight cone, 53° from vertical (m = 1.33), R(z) = 44.5 − 1.33(z − 157.0) |
| Neck fillet | R 21 |
| Neck | Ø 34.1 (raw2 33.8–34.5) |
| Arch | emerges from prism ∩ cone, sharp apex 157.0, corner 146.4–146.7 (CHAMFER 0.0754), rise ≈ 10.5 |
| Arch fillet | rolling ball ρ ≈ 5 (or ARCH_K ≈ 1.0 on the straight cone); visible tangent at about 154.5 centre and 143.5 corner |
| Z_HOLD | 147.5, as B proposes (removes the ~1° break) |
| Vertical edges | R 1.0, i.e. EDGE_SOFT 0.11–0.13 with the stable softmin, or a true fillet; mesh ≥ 8 segments per fillet (D) |
| CHAMFER | 0.0754, unchanged pending the supplier drawing |
| Heel | flat 32° bevel from z 8.5 to 1.0, R ≈ 1 at both breaks |
| Inner floor | flat (drop the punt dome) unless the supplier says otherwise |
| Label | crown about 6 mm lower (front centre ≤ 152.5, fold ≤ 141.5), or the glass deviates from the reference. This needs a client decision. |
