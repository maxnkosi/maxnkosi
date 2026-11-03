# B: Shoulder surface. How the real bottle is built, why v006 looks lumpy and low, and a clean construction

Study only. No project file was edited. Diagnostics and scripts are in `research/v006_study/diag/` (files `b_*`).
Run `Blender -b --factory-startup --python diag/b_shoulder_diag.py -- --render` to rebuild every figure. It reads the geometry functions straight from `build_avante_master.py` (everything above the materials section), so the figures always reflect the current v006 code.

Tags: **V** = verified numerically on our model. **R** = read from the reference photos (low resolution, so these are an industrial designer's reading). **A** = assumption or proposal.

---

## 1. True surface topology (from raw1, raw2, raw5, raw7, raw8, board)

| Element | What it is | Evidence |
|---|---|---|
| Body | An extruded chamfered square: 4 flat panels and 4 narrow flat chamfer facets, with a slight taper per PROFILE. | All refs (R) |
| Shoulder | **One surface of revolution**, close to a **straight cone** in its middle. It is neither a dome nor a loft. In front view the silhouette between the panel top and the neck fillet is a straight line. Our own PROFILE confirms this: from z = 160 to 172.5 the half-width is linear to within 0.1 mm, with slope dR/dz = -1.287, which is **37.9° from horizontal** (V, least-squares fit). | raw2 and raw7 silhouettes (R), PROFILE fit (V) |
| Panel termination | Each flat panel ends where the **cone intersects its plane**. That intersection is a hyperbola, which is the arch: highest at the panel centre and falling toward the corners. The arch is a defined, soft-crisp edge (a moulded fillet of a few mm), not a smeared blend. In raw7 it reads as a clean shallow arch line. In raw8 it reads as a clear crease on the embossed panel. | raw7, raw8 (R) |
| Chamfer termination | The chamfer plane lies about 58 mm from the axis, almost exactly as far out as the panel/chamfer corners (58.3 mm). So the cone cuts each chamfer **almost level, at the lowest point of the arch system**. The chamfer ends in a short flat-topped cap where the two neighbouring panel arches come down to meet it. **The chamfers do not continue up the shoulder.** Everything above the arch line is the single revolved surface. | raw8 corner (R), geometry (V) |
| Arch height | For a cone cutting the prism, the arch rise is (r_corner - h)/m = (58.3 - 44.45)/1.287 = **10.6 mm** (panel centre about 156.7, corners about 146.0, before the fillet). That matches the rev D wrap crown, whose corner sits at about 145.0. | V |
| Neck junction | A large concave fillet from the cone into the 34.1 mm neck cylinder. Fitted to PROFILE 172.5–190, its radius is **20.5 mm**, with tangency at z 171.8 and 188.0 (V). | raw2 (R), PROFILE (V) |
| Edge hierarchy | Vertical chamfer edges: small radius, about 1–1.5 mm, crisp. Arch edge (panel/cone): soft-crisp. The measured silhouette corresponds to a rolling-ball radius of about 8 mm. The client wants crisper, so 3–4 mm is acceptable within the ±0.7 mm PROFILE tolerance. Neck fillet: large and soft. Chamfer/cone cap: small. | R + V |

**Construction intent of the real mould:** body prism ∩ revolved cone generatrix, with a constant-radius fillet along the intersection. The arch is not drawn. It **emerges** as the intersection curve.

---

## 2. Diagnosis of v006

### 2.1 What the code does
`outer_r = softmin(sq_radius(θ, body_S(z)), shoulder_R(z), k = 1.2)`. `shoulder_R` is a Hermite ease from (131, r_c ≈ 62.9, slope 0) to (157.5, 42.75, slope -0.78). Above 157.5 it switches to `width_at(z)/2`. The body square is held above Z_HOLD = 152.5.

### 2.2 Findings (all V; numbers in `diag/b_metrics.json`)

1. **The dome meridian is an S-curve with an inflection, followed by a curvature jump. This is the uneven band just above the shoulder.**
   - dR/dz runs -1.01 (z 150) → -0.89 (155) → -0.78 (157.4). The dome *flattens* on its way up. d²R/dz² is +0.02 to +0.05, which is concave, the wrong sign for a shoulder.
   - At Z_ARCH_F = 157.5 the code switches to the PROFILE spline. The slope matches (C1), but the curvature jumps, and immediately afterwards the slope steepens to -1.14 (160) and -1.32 (165). The peak curvature, d²R/dz² = -0.158 at 158.75, is a horizontal ring that does not follow the arch.
   - In the zebra renders this shows as lens-shaped islands and kinked stripes across the whole shoulder: `b6_v006_zebra_tq.png` and `b6_v006_zebra_corner.png`. The cone proposal gives straight radial stripes (`b6_P1_archrows512_zebra_*.png`).
2. **The revolved PROFILE spline copies measurement noise into the surface.** Above 157.5 the shoulder is `width_at/2` itself, a PCHIP through photo-measured points (±0.7 mm). Its second derivative alternates sign every knot: -0.06, +0.04, -0.02, -0.07, +0.01, +0.05, +0.10 … +0.28 at 180. Revolved, every knot becomes a horizontal ripple ring. See the stripe stack in the left half of `b5_curvature_map_v006_vs_P1.png` (θ 0→45° across, z 125→190 bottom to top; blue = convex, red = concave). The right half is the proposal: a single clean fillet band that follows the arch, plus the neck fillet.
3. **The dome grazes the corners, which makes the intersection ill-conditioned. This is the lumpy corners and the low shoulders.**
   - The Hermite starts with **zero slope** at 131, so near the corners (r ≈ 58) the dome is almost parallel to the vertical prism. Where two surfaces meet nearly tangentially, a tiny change in R moves the crease a long way vertically. The softmin (k = 1.2, radial) then smears the cut over about 10 mm. Corner pull-in: 0.03 mm at 137, 0.20 at 140, 1.50 at 143, 4.23 at 146.
   - Result: the carving starts at **z 138.7 at the corners and 152.3 at the panel centre** (`b1_arch_height.png`). A true cone puts these at 146.0 and 156.7.
   - So v006 sits **7.3 mm low at the corners and 4.4 mm low at the panel centre**. That is the client's "lower shoulders". The wrap label's crown corners (about 145) now hang over a region already carved away from 138.7 upward. That accounts for part of "bad label placement".
4. **Softmin is a radial blend, not a fillet.** The blend width depends on the angle between the surfaces, so it is wide where they graze (corners) and narrow at the panel centre. Its pull-in also lowers the flat panel by up to 0.83 mm (k·ln2) where R ≈ r. This is why the arch reads as a soft "pillow" rather than a moulded edge. It also contributes to "overly bevelled": the panel-centre loss is already 0.35 mm at 154 and 1.10 mm at 156.
5. **Z_HOLD = 152.5 leaves a C1 kink across all four panels.** The PROFILE slope there is -0.072 mm/mm, and holding the square turns that into an angle break. It is visible as a thin horizontal line at z 152.5 in the curvature map. At 147.5 the PROFILE slope is 0.000, so holding there is seamless.
6. **The meshing aliases the crease.** The arch fillet runs diagonally across a grid of horizontal rings: 256 vertices, about 1.42 mm per step at r = 58, and 0.5 mm in z. Even with a perfect surface, a fillet crossing the grid diagonally renders as stair-steps. Compare `b6_P1_flatrings256_zebra_corner.png` (same mathematics, serrated fillet) with `b6_P1_archrows512_zebra_corner.png` (rows follow the arch, clean).
7. **Minor or non-causal.**
   - The `roundness()` 182–186 switch has no effect on the outer surface, because the cone radius (about 17–18 mm) is far inside the square, so softmin returns R.
   - Auto-smooth at 40° is not the cause, since there are no dihedral angles that large on the shoulder.
   - v006's inner wall is inset radially by WALL, so the wall measured normal to a 37.9° cone is only **2.2 mm** against 3.6 mm on the flanks. That makes the shoulder look thin and glassy compared with the body.

---

## 3. Proposed construction (P1): prism ∩ cone, exact rolling-ball fillet

### 3.1 Surfaces
- **Prism** `P(θ, z) = sq_radius(θ, S(z))`, with `S(z) = width_at(min(z, Z_HOLD))` and **Z_HOLD = 147.5**. The chamfer and EDGE_SOFT stay as they are. To address the bevel comment, replace EDGE_SOFT's log-sum-exp with a true 1.0–1.5 mm fillet; that is a separate item.
- **Generatrix** `G(z)`, revolved, G1 continuous, built from three analytic pieces:
  - Cone line: `G = R0 - M (z - 160)`, with **R0 = 40.16, M = 1.2869** (LS fit to PROFILE 160–172.5; 37.9° from horizontal). It extends downward without limit, so it always cuts the corners at a well-defined, steep angle.
  - Neck fillet: concave circular arc, **ρn = 20.5**, centre `rc = 17.05 + ρn`, `zc = 160 + (ρn·√(1+M²) - rc + R0)/M = 188.0`, tangency `zt = zc - ρn·M/√(1+M²) = 171.8`. `G = rc - √(ρn² - (z - zc)²)`.
  - Neck: `G = 17.05` up to 190. Above 190, the existing `width_at/2` finish is unchanged.
- **Combination**: exact rolling-ball intersection of the two half-spaces with radius **ρ = 4 mm** (A). The options are:
  - ρ = 3: crisper, silhouette deviation 0.62 mm.
  - ρ = 4: deviation 0.56 mm. Recommended, since the client asked for less bevel and this is inside the ±0.7 mm tolerance.
  - ρ = 8: deviation 0.14 mm, the PROFILE-exact choice, but softer.

Signed distances along the ray θ at radius r:
```
cp  = P / sqrt(P² + P_θ²)                # cos(radial, prism normal)
q   = sqrt(1 + m²),  m = -dG/dz          # cone normal tilt
dA  = (r - P) · cp                       # distance to prism (exact for planar facets)
dB  = (r - G) / q                        # distance to cone line
c   = cp / q                             # cos(angle between the two normals)
```
Rolling-ball intersection (the exact 2D wedge distance; the fillet is a true circle of radius ρ):
```
def round_intersect(dA, dB, c, rho):
    a, b = dA + rho, dB + rho
    if a <= 0 and b <= 0: return max(a, b) - rho
    if b - a*c <= 0:      return a - rho        # nearest point on prism face
    if a - b*c <= 0:      return b - rho        # nearest point on cone
    return sqrt(a*a + b*b - 2*a*b*c) / sqrt(1 - c*c) - rho
```
`outer_r(θ, z)` is the root in r of `round_intersect(...) = 0`. The function is monotone in r, so 40–48 bisection steps on [0, P] are enough. A closed form exists, but bisection is simpler and already fast (the full diagnostic run takes about 5 s). Far below the arch the result reduces to `r = P`. On the shoulder and neck it reduces to `r = G`. Only the fillet band differs from min(P, G).

### 3.2 Results (V; ρ = 3 shown in the renders)
- **Arch emerges by itself.** Sharp crease: panel centre 156.7, 30° → 151.3, panel edge 146.3, chamfer 146.0. With the ρ = 3 fillet, carving starts at 156.0 at the centre and 145.3 at the corners. The shoulder is **3.7–6.6 mm higher than v006** and the arch rise is 10.7 mm. If the client wants v006's 13.6 mm rise, that is only possible by lowering the cone slope to about 1.02 (45°), at the cost of the PROFILE silhouette. I do not recommend it.
- **Surface quality.** The zebra stripes on the cone are straight radial lines. There is one fillet band of constant radius along the arch, and the neck fillet has constant curvature 1/20.5. No horizontal ripple rings (`b2_meridian_curvature.png`, `b5_*`, `b6_P1_*`).
- **Front silhouette.** Maximum deviation from PROFILE between 140 and 192 is 0.56 mm at ρ 4 (0.4 for v006), all of it at z 155–157.5 where the fillet radius sets the deviation (`b3_silhouette.png`). Elsewhere it is within 0.1–0.3 mm.
- **Chamfer.** Each chamfer ends in a small, nearly level, filleted cap at about 146, as in raw8 (`b6_P1_archrows512_facing_corner.png`).

### 3.3 Inner wall
- Offset each surface **normally** by WALL, not radially:
  - `P_in = P - WALL / cp`
  - `G_in = G - WALL · q` (radial inset of 5.86 mm on the cone, giving a true 3.6 mm wall)
- Inner fillet: `ρ_in = ρ + 1` (A). A blown parison's inner surface is rounder than the mould side. Don't use ρ - WALL, which goes negative and leaves a sharp inner crease that refraction would expose.
- Neck (z ≥ 185): bore as now.
- Volume effect between z 120 and 185: -4.8 ml against v006, because the thicker true-normal wall outweighs the higher corners. The base re-solve absorbs this, making the base about 1.0 mm thinner. `solve_base_thickness()` needs no change beyond calling the new inner radius inside `section_area` / `inner_volume`.

### 3.4 Meshing: arch-conforming rows within the existing ring/loft
Rings do not need to be planar. Keep `loft()` and change only where each row's vertices sit:
```
ZA(θ)  = 160 + (R0 - P(θ, Z_HOLD)) / M              # sharp crease height on ray θ
ZA0    = ZA(0)                                       # 156.7
w(v)   = 1 for ZA0-8 <= v <= ZA0+3, smoothstep down to 0 at v = 118 and at v = 186
                                                     # fade lengths keep z(v) monotone: max |w'|·10.7 < 1
row_z(θ, v) = v + w(v) · (ZA(θ) - ZA0)               # rows dip with the arch toward the corners
v samples : 0.15 mm in [ZA0-5, ZA0+4], 0.4 mm in 130..192, 1 mm elsewhere (pass PROFILE knots as now)
N_RING    : 512, or arc-length sampling with clustering on the chamfer edges
for v in v_samples:
    ring = []
    for i in range(N):
        th = 2π i / N; z = row_z(th, v); r = outer_r(th, z)
        ring.append((r cos th, r sin th, z))
verts, faces = loft(outer_rings + inner_rings, ...)  # same as today; inner rings use the same row_z
```
- The liquid, capsule, and wrap already call `outer_r` / `ring(..., cut=...)`. Route them through the new functions: the liquid uses inset WALL - OV with the same normal-offset rule.
- `surf_xyz` then follows the new shoulder automatically.
- **Label:** `surf_xyz` lifts the crown along a 49° plane (`sin(radians(49))`, `SHOULDER_STRETCH`). The cone is 37.9° from horizontal, so use `sin(atan(1/M)) = 0.614`. Otherwise the crown top lands at 158.5 instead of about 157.0, on the fillet.
- **Shading:** shade smooth everywhere. Auto-smooth is not needed, since every edge is a real fillet. If kept, 40° is harmless.
- **Cost:** about 512 × 420 points × 48 bisection steps. Under 10 s in pure Python. The full `b_shoulder_diag.py` run with three meshes and twelve renders took 40 s.

### 3.5 Why not boolean/remesh
A bmesh or Boolean intersection of a prism mesh with a revolved mesh, followed by a Bevel modifier on the intersection edge, would give the same topology. The trade-offs:
- The bevel/remesh step loses the analytic control the volume solve, the label development (`surf_xyz`), the capsule and the liquid all rely on, because all of them query `outer_r(θ, z)`.
- Bevel width on an obliquely meeting edge is not a constant radius.
- Remeshing introduces triangle noise visible in glass refraction.

The analytic implicit round-intersect gives the same result as a CAD rolling-ball fillet, keeps a single source of truth, and fits the current loft. Use Boolean only if the shape later needs features that cannot be expressed as a function on a ray from the axis (undercuts).

### 3.6 Checks preserved
- **Glass height 226.9:** unchanged. The finish above 190 is untouched.
- **Max width 89:** the prism is unchanged below Z_HOLD. With Z_HOLD = 147.5 the held S is 89.0. The silhouette maximum is 44.5 × 2 = 89.0 (V).
- **750 ml:** re-solved through BASE_T, about 1 mm thinner.
- **Front PROFILE:** within 0.56 mm (ρ 4).
- **Fill height and capsule:** unchanged. The capsule hem sits at 171.8 or above, on the cone or neck fillet. The capsule uses `outer_r`, so it follows.

### 3.7 Parameter block (proposed)
```
Z_HOLD        = 147.5          # was 152.5 (removes the C1 kink)
CONE_R160     = 40.16          # mm, fitted
CONE_M        = 1.2869         # -dR/dz, 37.9° from horizontal
NECK_RHO      = 20.5           # concave neck fillet, tangent 171.8 → 188.0
SHOULDER_RHO  = 4.0            # A; 3 crisper, 8 PROFILE-exact
SHOULDER_RHO_IN = 5.0          # A
N_RING        = 512
# delete: Z_ARCH_C, Z_ARCH_F, ARCH_K, shoulder_R Hermite, softmin dome_cut, the 157.5 switch
```

## 4. Figure index (diag/)
- `b1_arch_height.png`: where the shoulder starts cutting the body, by θ. v006 against the P1 fillet and the P1 sharp crease.
- `b2_meridian_curvature.png`, `b2b_meridian_slope.png`: v006's inflection and jump at 157.5 and its knot ripples, against P1's line plus two fillets.
- `b3_silhouette.png`: front half-width against PROFILE.
- `b4_v006_carve_depth_theta.png`, `b4b_P1_carve_depth_theta.png`: outer_r over θ at several heights, as depth below the prism.
- `b5_curvature_map_v006_vs_P1.png`: meridional curvature over (θ 0→45°, z 125→190).
- `b6_{v006|P1_flatrings256|P1_archrows512}_{zebra|facing}_{tq|corner}.png`: reflection-stripe and clay renders of the outer surface only.
- `b_metrics.json`, `b_shoulder_diag.py`, `b_rho_sweep.py`, `b_volume.py`.
