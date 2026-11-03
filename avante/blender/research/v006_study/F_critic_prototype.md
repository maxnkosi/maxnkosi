# F: Critic prototype. Combining A, B, C and D, and where they conflict

This is a study only. No project file was edited, nothing went into git, and the GUI Blender was not touched. Everything ran headless with `--factory-startup` on Metal GPU.

**Files** (all in `research/v006_study/diag/`):

| File | Purpose |
|---|---|
| `critic2_proto.py` | Imports `build_avante_master` as `B` and monkeypatches it in memory, then calls `B.main()`. It then runs the `check_avante_master.py` logic, the label stress test, and the renders. Args: `RHO LABEL SHOTS SAMPLES TAG`. `RHO=v006` gives the unpatched baseline under the same rig. |
| `critic2_analysis.py` | Analytic checks: silhouette against PROFILE, arch onset, diagonal widths, the rev D.2 die requirement against the top of the artwork, and a lower bound on wrap strain. |
| `critic2_compose.py` | Builds the comparison sheets. |
| `critic2_runall.sh` | Runs the whole batch. |
| `critic2_*.json` | Numbers. |
| `critic2_*.png` | Renders. |

**Sheets**:

| Sheet | Panels, left to right |
|---|---|
| `critic2_sheet_front.png` | raw2, v006 glass, prototype glass, prototype full |
| `critic2_sheet_34.png` | raw5, v006, prototype, raised-shoulder variant, v005 |
| `critic2_sheet_glass34.png` | glass only, three-quarter view |
| `critic2_sheet_shoulder.png` | glass close-ups: v006, ρ3, ρ4 |
| `critic2_sheet_label.png` | label close-ups: v006, prototype (plane label + D.1), crown wrapped onto the cone, raised shoulder |
| `critic2_zoom_chamfercap.png` | crop of the chamfer caps |

## 1. Prototype P: what was patched

| Source | Patch |
|---|---|
| B | `outer_r` = held prism, round-intersected with a revolved cone, using an exact rolling-ball fillet of ρ = 3 or 4 mm.<br>Cone: R = 40.16 − 1.2869 (z − 160), which is 37.85° from horizontal and fitted by least squares to PROFILE 160–172.5. It runs straight down with no lower limit, which is A's "continue the cone below 157.5".<br>Neck fillet: ρn 20.5, tangent at 171.8 and 188.0.<br>`Z_HOLD` 147.5.<br>Inner wall: offset along the normal (cone inset by WALL·q), with ρ_in = ρ + 1.<br>Rows follow the arch (`row_z`), with a separate row function for the inner wall because its crease sits 1.8 mm lower. |
| D | `EDGE_SOFT` 0.07, through the stable `softmin`.<br>Adaptive θ sampling: 776 vertices per ring, about 0.085 mm across each vertical fillet.<br>Rows 0.15 mm through the arch band and 0.3 mm from 138 to 194.<br>Filleted-polyline heel.<br>C1 blend of the inner radius into the bore over 181–189, which removes the 185 step.<br>Plain shade smooth. |
| C | Label placed on the panel planes of the held filleted prism: true length, no sin 49, perimeter mapped by arc length. Never on `outer_r`.<br>Rev D.1 die: TRIM y < 0 multiplied by sin 49°. |
| Liquid | Arch rows that blend over 30 rows into the flat fill plane at 160.9, which sits above the inner crease. |
| Volume | New `inner_volume` on the patched inner wall. The base re-solves. |

`CHAMFER` stays at 0.0754. Nothing here forces it to change (§4).

## 2. Results: geometry (B + A + D). This part works

| Metric | v006 (same rig) | P, ρ3 | P, ρ4 | Reference / target |
|---|---|---|---|---|
| check_avante_master logic | pass | **11/11 pass** | **11/11 pass** | – |
| Volume to fill / base thickness | 750 / 17.79 | 750 / 16.74 | 750 / 16.71 | 750 |
| Brimful | 811.7 | 806.5 | 806.5 | – |
| Arch onset (0.05 mm carve), panel centre / corner | 153.3 / 139.7 (A) | 155.75 / 144.85 | 155.35 / 144.4 | about 155 / 145–147 |
| Sharp crease, centre / corner | – | 156.63 / 145.86 | same | knuckle 156.3 |
| Arch rise | 13.6 | 10.9 | 10.95 | 9–10.5 |
| Max front-silhouette deviation from PROFILE (140–192) | 1.2 | 0.63 (at 157.5) | 0.58 | ±0.7 |
| Diagonal (45°) width at 145 / 150 / 155 | 109.2 / 99.3 / – | 116.3 / 106.1 / 93.2 | 116.1 / 106.1 / 93.2 | about 116 / 110 |
| Glass / liquid vertices | about 160k | 676k / 206k | same | – |
| Build time, render time | 25 s | 31 s | 24 s; 12–27 s per shot at 600×960 or 900×720, 64 spp | – |

**Visual comparison**

- **Front glass against raw2.** P's silhouette, straight cone and neck root read as raw2 does.
- **Shoulder surface.** The uneven-shoulder problem is solved. v006 shows lens-shaped caustic blobs and kinked highlights on the shoulder. P shows straight highlights and one clean fillet band that follows the arch.
- **Neck root.** v006 has a hard ring line at 185 (the inner bore step). P has only a soft gradient.
- **Vertical edges.** They read as two hairlines with a flat chamfer between them.
- **Heel.** It reads as cut glass.
- **ρ3 against ρ4.** The difference is barely visible at product scale. ρ3 is about 0.4 mm higher at the onset, which matters for the label (§3).

**New artefacts found**

1. **Chamfer-cap pinpoints.** Small dark ticks appear at the four corners of each chamfer cap, where the 3–4 mm arch fillet meets the 1 mm vertical-edge fillets (`critic2_zoom_chamfercap.png`).
   - Cause: there is no vertex blend. Two fillets of very different radius meet in a three-surface corner, and the round-intersect leaves a sub-mm cusp.
   - Severity: low. It is only visible in macro shots.
   - Fix: raise `EDGE_SOFT` locally near the crease, e.g. scale k from 0.07 at z < ZA(θ) − 6 up to about 0.3 at the crease, or add a setback vertex blend.
2. **Faint soft ring inside the neck** at about 186–189. This is the bore blend seen through the glass. It is acceptable; v006's hard line is gone.
3. **No stair-steps, no heel or ripple problems.** Arch rows plus 0.15 mm rows give no serration on the arch fillet. The flat-to-arch blend in the liquid shows no tessellation in refraction.
4. **Not a geometry artefact (my script).** The roundel still shows in the "glass only" shots, because hiding through `GEO_Labels.all_objects` missed it. This is cosmetic.
5. **Cost.** 4.2× v006's glass vertex count. Render times are fine on GPU.

## 3. Stress test: the label. This is where the proposals collide

The rev D crown datum (79.64 from cap, so z 158.47) lies **above** the cone's sharp crease (156.63 at the centre, about 145.9 at the corners). The crown is about 13 mm wide and its sides drop with the arch, but **the crown arch is about 0.5–0.7 mm flatter and about 3–5 mm higher than the glass arch.** It does not clear the arch anywhere on the front or chamfers.

**Clearance**, defined as the lowest z where the glass is carved more than 0.05 mm minus the label top edge, for P at ρ4 with the plane label and the D.1 die:

| Position | Panel centre | x = 20 | front/chamfer fold | mid-chamfer | chamfer/side | 5° into the side | side-panel centre |
|---|---|---|---|---|---|---|---|
| Clearance (mm) | **−3.1** | −3.4 | **−4.8** | −2.4 | −1.4 | +1.6 | +9.8 |

- At ρ3 the minimum clearance is −4.26.
- C asked for at least 1.5–2 mm. **Every position from the centre to the chamfer/side corner fails by 3–7 mm.**

Three label strategies were built and measured. Strain is dieline → 3D, per triangle.

| Label strategy | Crown datum (79.64 ± 0.6) | Gap to glass | Crown strain | Verdict |
|---|---|---|---|---|
| **C: panel planes + rev D.1 die** | 79.63 PASS | **up to 3.49 mm**. 2 % of vertices > 0.1 mm, p99 0.88 mm. The top stands proud of the shoulder as a flat flag; the corners poke past the silhouette in the hero view. | 0.15 % (isometric) | Fails the clearance rule. The flag is plainly visible in `critic2_r4_plane_fullhero.png` and in the label sheet. |
| **Wrap over the fillet and cone** (rev D die, columns follow the glass meridian by arc length) | **78.60 FAIL** (crown rides 1.0 mm high because the cone is slanted) | 0 | p99 **22 %** compression; 70 % of crown triangles > 1 % | Fails |
| B's suggestion: replace sin 49 with sin(atan 1/M) = 0.614 in the builder mapping | **81.10 FAIL** | 0 | uniform **38.5 %** vertical squash | Not physical; reject |

**Is D.1 needed, or can the label legitimately wrap the cone?** The cone is developable, but the label is not on the cone alone.

- **Curved-fold rule.** A flat sheet folded along a curved crease cannot keep one side in the plane of that crease. Equal geodesic curvature on both sides would force a fold angle of 0. The plane∩cone crease is a hyperbola lying in the panel plane, so any label that is flat on the panel and wraps onto the cone must strain.
- **Fillet band.** The ρ 3–4 rolling-ball band between the two surfaces is a canal surface, which is doubly curved.
- **Lower bound.** Hoop strain is at least κ·d·(1 − cos φ), with crease curvature κ = 0.0175–0.0057 /mm, distance past the crease d = 1.7–2.7 mm, and fold angle φ ≈ 52°. That gives **about 1.2 % at the centre and 0.6 % at the folds.** This is a best-case mapping, not one that has been achieved.
- **Paper tolerance.** Paper tolerates well under 1 % (C), so even an optimal wrap is marginal at the centre. Add the doubly curved fillet, and in practice it means darts or a lifting crown.
- **Conclusion.** A wet-glue paper wrap over the cone is not legitimate. A shrink sleeve or PS film could do it, but that is a substrate change.
- **D.1 alone is not enough.** D.1 is needed for the true-length crown, but it does not solve the crossing. It only makes the crossing visible as a gap instead of hiding it as strain.

**What it takes to clear by 2 mm.** Two routes were worked through.

- **Route 1. Die follows the glass (rev D.2), cone as in B/A.**
  - The top edge must come down by 5.1–6.2 mm against D.1 on the front and chamfers, and by 1.1–2.5 mm on the first 3 mm of each side panel.
  - **The crown datum becomes 84.75 from cap** (now 79.64), while the bottom stays at 165.9.
  - Artwork margin falls to **2.1 mm at s ≈ 15** (top of the art at dieline y +1.58), under C's 3 mm rule. Between the art top and the arch onset there are 4.13 mm (ρ4) or 4.63 mm (ρ3), against the 4.5 mm needed for 3 mm art margin plus 1.5 mm clearance.
  - So **only ρ3 with c = 1.5 at s ≈ 10–20 fits without touching the art.** That is a datum change and a die change.
- **Route 2. Raise and flatten the shoulder, keep the D.1 die and both datums.**
  - Parameters: R0 47.38, M 1.60 (32° from horizontal), ρn 18 (`critic2_r4_high_*`).
  - Results: all checks pass. Base thickness 19.73. Onset 160.25 at the centre and 151.45 at the corners. Clearance at least **+1.78**. Gap ≤ 0.0065. Zero strain.
  - The cost: the front silhouette is **up to 6.2 mm per side wider than PROFILE at z 160–170**. The knuckle sits about 5 mm above raw2 and the shoulder is flatter and boxier (`critic2_sheet_34.png`, panel 4).
  - This contradicts A and B's metrology and raw2. It is a different bottle.

**Ambiguity to raise with the client.** "Lower shoulders" was read by all four specialists as "the shoulders are too low". If the client meant "lower the shoulders", Route 2 is the wrong direction. Either way, Route 2 is the only one that keeps the approved datums.

## 4. Verdict per report

| Report | Works | Fails or conflicts |
|---|---|---|
| **A** | The cone continued below 157.5 gives the measured arch: rise 10.9, corners 144.4–145.9, diagonal width restored by about 7 mm. The silhouette is within 0.6 mm of PROFILE.<br>A's own option list (cone, removing the hold crease, fairing) is fully realised by B's construction. | A's label note "≤ 0.5 mm inset at the crown corner" holds only for the side-panel corner. At the front/chamfer fold the crown is still 4.8 mm above the onset.<br>A's CHAMFER doubt (0.04–0.05) remains untested. It is label-locked; nothing in P forced a change. |
| **B** | The construction is sound, fast (glass in 2.5 s, numpy) and robust. ρ4 is within ±0.7; ρ3 is crisper and gives 0.4 mm more label room.<br>Normal-offset wall: base 1.1 mm thinner (16.7 vs 17.8), as B predicted. | B's sin(atan 1/M) label fix is wrong: it squashes 38.5 % and fails the datum.<br>B says the crown "lands on the fillet" at 158.5. In fact it lands 1.8–4.8 mm past the onset everywhere on the front.<br>The chamfer-cap pinpoints are new; they need a vertex blend. |
| **C** | The diagnosis and the plane mapping are right: isometric, 0.15 %. The physics is right: a wrap is not legitimate.<br>D.1 is necessary for a true-length crown. | **C's required glass (apex 160.5, corners 150.5) is about 4–6 mm higher than A/B's reference-true cone.** Rev D datums, the reference shoulder and the 1.5–2 mm clearance cannot all hold together.<br>D.1 alone leaves a 3.5 mm flag.<br>C's art-margin claim (≥ 6 mm after D.1) becomes 2.1 mm under the D.2 die that the cone needs. |
| **D** | `EDGE_SOFT` 0.07 with the stable softmin, adaptive θ, the heel, and the 181–189 bore blend all work and are visible in the renders. | D's `ARCH_K` 0.25 is superseded: there is no softmin arch any more, and ρ is the parameter.<br>D's 2.5 mm face fillet is not reachable with one constant ρ. ρ3 is the compromise.<br>Vertex count is 4.2×. |

## 5. Recommended combined spec, ranked by risk (lowest first)

1. **Edges (D). Adopt now. Low risk.**
   - `EDGE_SOFT = 0.07` through `softmin` in `sq_radius`.
   - Adaptive θ: 384 uniform plus ±24 steps of 0.0018 rad at the 8 vertex angles (776 per ring).
   - Plain smooth shading.
   - Heel polyline: footprint hw = hwS − 4.5, bevel top at z 7.5, side at z 14, R 1.0 / 1.0.
   - Bore blend: smoothstep over 181–189.
2. **Shoulder (B + A). Adopt. Low to medium risk.**
   - `Z_HOLD = 147.5`.
   - Cone R0 40.16, M 1.2869.
   - Neck ρn 20.5.
   - **ρ = 3.0** (crisper, and 0.4 mm more label room). Silhouette deviation 0.63 against the ±0.7 tolerance.
   - ρ_in = ρ + 1. Wall offset along the normal.
   - Arch rows: separate inner and outer `row_z`, rows 0.15 mm in [ZA0 − 6, ZA0 + 5] and 0.3 mm from 138 to 194.
   - New `inner_volume`. Base thickness about 16.7.
   - Delete `Z_ARCH_*`, `ARCH_K`, `shoulder_R` and the softmin `dome_cut`.
   - Add a chamfer-cap vertex blend (k ramp near the crease) before macro shots.
3. **Label mapping (C). Adopt the mapping, but not as the final label.**
   - Panel planes, true length, arc-length perimeter. Never `outer_r`.
   - Assert that the label never sits on carved glass.
   - Add C's checks D1 to D6 to `check_avante_master.py`. Under P they will fail on arch clearance until item 4 is decided. That failure is correct.
4. **Crown versus arch. Client decision. High risk; pick one.**
   - **(a) Recommended: rev D.2 die plus a crown datum move to about 84.7 from cap.** Keep the reference-true glass and ρ3. The top edge follows the glass onset minus 2 mm (minus 1.5 mm at s 10–20), and the bottom stays at 165.9. The artwork is not touched; margin is at least 3 mm only with ρ3 and c = 1.5 locally. This needs sign-off from the client and the printer, because it changes an approved datum and the die.
   - **(b) Raised shoulder: R0 47.4, M 1.6, ρn 18.** Keeps rev D.1 and both datums, but departs about 6 mm from raw2/PROFILE and reads squat. Only if the client prefers the label over the reference silhouette.
   - **(c) Not acceptable:** wrapping the crown onto the cone (strain at least 1 % even at best, 22 % as built) or leaving it as a flag (3.5 mm gap).
5. **CHAMFER 0.0754: leave it.**
   - The label layout depends on it, and P shows no defect it causes.
   - The Imperial references suggest 0.045–0.055, which would also narrow the fold-corner overshoot slightly. Revisit it only together with the D.2 die work and the supplier drawing W2124.
