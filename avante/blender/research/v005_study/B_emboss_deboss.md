# B. Emboss / Deboss study for v005 (AVANTE Cape Brandy)

Scope: a read-only study. No scene or script was changed.
Labels used below:
- **[S]** sourced fact, with URL
- **[M]** from memory or trade knowledge, not verified this session
- **[O]** my observation of a reference or render
- **[I]** an inference from physics or geometry
- **[R]** a recommendation (artistic unless marked)

Current spec (from `build_avante_master.py`):
- `EMB_H = 0.20` mm. The wordmark and bird are foil plus emboss, from `MASK-EMB-01__LBL-FRONT-01.png`. The material uses a Displacement node (Midlevel 0, object space, method BOTH). The mesh gets an adaptive SIMPLE subsurf at 1.0 px, placed after a 0.10 mm Solidify.
- `ROUNDEL_RELIEF = 0.04` mm. The roundel uses the foil mask as height on a 0.05 mm film. The client has confirmed this value; it stays.
- Masks are 8-bit RGBA. The front mask is 4870 x 2026 px over 243.47 mm, so 0.050 mm per texel. The roundel mask is 1200 px over 47.7 mm, so 0.040 mm per texel. The EMB mask is in effect the foil mask: the file sizes are nearly identical.

---

## 1. Process taxonomy and numbers

### 1.1 Processes
| Process | What it is | Typical profile | Ref |
|---|---|---|---|
| Blind emboss | Raised, no ink or foil in register | One level, rounded, or sculpted | ref01 rope borders |
| Registered emboss | Raised, in register with print | same | - |
| Combination foil-emboss | One heated brass die stamps foil and embosses in a single hit, so the two are in perfect register | Usually one level with bevel or rounded; can be sculpted | ref01 barrel and coins, ref02, ref11, **our AVANTE and bird** |
| Deboss / blind deboss | Pressed below the surface | Steep wall, rounded top lip, flat floor | ref03 rules, ref12 |
| Foil deboss (stamped foil) | Hot foil pressed slightly into the sheet | Floor is foil; walls very short | ref13, ref04 (near flat) |
| Letterpress impression | Inked relief plate bitten into soft cotton | Ink sits in the valleys; paper rises at the edges | ref03 |
| Sculpted / multi-level | Hand-tooled or CNC brass with many levels, curves and angles | Free-form | ref01 barrel and coins, ref09 seal |

Sources for the table:
- Iggesund names the configurations "one level", "two levels", "many levels", "impressed", "one level, rounded" and "sculptural". It also says that combining foil and emboss in one operation gives "perfect register". [S] https://www.iggesund.com/globalassets/iggesund/services/knowledge/iam/graphics-handbook/gh-pdf----en/embossing_and_debossing_in_practice.pdf
- Billerud lists side profiles as "flat, beveled, V-shaped, or rounded". It calls rounded edges with graduated levels a sculptured emboss. [S] https://www.billerud.com/trends-and-cases/all/print-techniques/embossing-see-and-feel-the-third-dimension
- On letterpress into cotton: soft cotton gives the deepest bite, and you get "ink in the valleys of the impression, paper rising around the edges". [S] secondary vendor pages from search, e.g. https://rise-and-shine-2026.pages.dev/how-we-print/letterpress-printing
- A deep impression shows through to the back unless the stock is board weight. [S] https://briarpress.org/21501

### 1.2 Die materials
| Material | Make | Life | Levels | Source |
|---|---|---|---|---|
| Brass | Engraved / CNC | ++++ (up to about 1 M impressions) | Multi-level, sculpted, combination foil-emboss | Iggesund table [S]; Billerud [S] |
| Copper | Photo-etched | +++ (100 k or fewer) | Mostly single level | same |
| Magnesium, engraved | - | ++ | Limited multi-level | Iggesund [S] |
| Magnesium, etched | Photo-etched | ++ (about 1 k to 5 k, or 5 k to 10 k) | Only single level | Iggesund, Billerud, zevendesign [S] |

Further notes on dies:
- Foil-stamping tools are "generally made out of magnesium". Brass is used for long runs or for designs that cut into the surface. [S] https://www.topac.de/fileadmin/content/c_Leistungen/Foil_embossing.pdf
- Emboss tools are "mostly made of brass", with "angled or rounded embossing edges (spherical tools)" and multistage tools available. Tools "are made for the material thickness concerned". [S] https://www.topac.de/fileadmin/content/c_Leistungen/Embossing_Debossing.pdf
- **Counter-die (make-ready):** this is the mirror image of the die. It must be matched to the board's compressibility and thickness, and the die maker should supply it. [S] Iggesund.
- A precast counter is undercut, so it stands slightly taller than the die depth, which stops the die bottoming out. [S, forum] https://www.briarpress.org/26298
- For AVANTE, a CNC brass combination die with a brass or precast counter is the realistic tool for a premium spirits run. [I]

### 1.3 Depths, line widths, bevels
| Quantity | Value | Source |
|---|---|---|
| Relief on paperboard, emboss or deboss | 0.15 to 2.5 mm | Iggesund [S] |
| **Combination foil-emboss relief** | **0.25 to 0.60 mm** (on paperboard, about 0.3 to 0.6 mm caliper) | Iggesund [S] |
| Overall emboss depth | 0.004" to 0.025" (0.10 to 0.64 mm) | Billerud [S]; creativepro snippet, 0.006" to 0.025" [S, snippet only, page 403] |
| "Average emboss" | about 1/64" (0.40 mm) | zevendesign [S] |
| Deep dies of 0.020" to 0.025" | must be bevelled or they cut the paper | creativepro / zevendesign [S] |
| Bevel angle | 30 to 60 degrees typical, up to 80 degrees; a broader angle gives more apparent depth | zevendesign, search snippets [S] |
| Wall geometry rule | A 45 degree etched wall moves sideways 0.001" for each 0.001" of depth, so a 0.010" line gives a 0.005" maximum depth (depth no more than half the line width) | creativepro snippet [S] |
| **Minimum emboss line width** | **2 x material caliper**; 0.474 mm board needs a 1 mm stroke | Topac [S] |
| Minimum foil line or stroke | 0.3 mm; negative (recessed) gaps at least 0.7 mm | Topac foil [S] |
| Maximum solid foil area | 70 x 70 mm (risk of air bubbles) | Topac foil [S] |
| Deboss fine detail | "The material thickness need not be considered" | Topac [S] |
| Measuring depth | "No accepted method of measuring embossing depth" (labels) | Spicers [S] https://www.spicers.com.au/application-guide |

Label stock calipers:
- Fasson offset label face papers measure about 66 to 107 µm. [S] https://graphics-test.averydennison.com/content/dam/averydennison/graphics/eu/en/Data-Sheets/Fasson/ds_fasson_labels_offset_papers_en.pdf
- Fedrigoni Martelé WS is 100 gsm at 125 µm; WNE4252 is 125 gsm at 152 µm. [S, via agent3]
- Our `LABEL_T` is 0.10 mm.

**What 0.2 mm means on a 0.10 to 0.125 mm label [I]:**
- The relief is 1.6 to 2 times the caliper. Iggesund's foil-emboss range starts at 0.25 mm, but that is for paperboard 3 to 5 times thicker than our stock.
- So 0.2 mm is achievable on a heavy cotton or felt label face, but it is at the deep end.
- It forces a bevelled or rounded die. A step about 1 texel wide, which is what we render, is not physically possible on this stock: the paper would shear.
- Applying the 45 degree rule, a 0.2 mm peak needs at least 0.4 mm of stroke to reach full height. Thinner strokes, such as the bird's spear and the serifs, would really emboss lower.
- The client approved 0.2 mm, so treat it as the **peak** height of a rounded profile, not a mesa height.

**Pressure-sensitive vs wet-glue labels:**
- Embossing "will affect the overall contact of the adhesive to the glass". An embossed-free zone 3 mm from the edge is "highly recommended". [S] Spicers.
- Foils, screens and varnish stiffen the face and reduce how well it conforms. [S] Spicers.
- Sticker stock can burst through the deepest parts of the image. [S, forum] briarpress, via search.
- On PS labels the emboss is normally done in-line with the liner still attached. The liner and adhesive layer absorb part of the stroke, so PS emboss tends to be shallower than wet-glue or sheet work. [M]
- Behind every raised emboss there is a cavity of the same shape. Under the letters the label is **not bonded** to the glass; there is a small air pocket. [I]

---

## 2. What the paper physically does
1. **Stretch and draw-in [S, qualitative]:** the board must "forgive a high degree of elongation without cracking but also retain a permanent deformation". Coating elasticity prevents cracking. [S] Iggesund. On the wall, fibres stretch by about 1/cos(wall angle): 15% at 30 degrees and 41% at 45 degrees. The stretch is taken up by thinning. [I]
2. **Rounded shoulders (pillowing) [I, supported by S]:** paper cannot follow a sharp die corner. Both the top shoulder and the foot get a radius of at least about the caliper, so 0.10 to 0.15 mm here, even from a sharp die. A rounded or spherical die adds its own radius (Topac's "rounded embossing edges"). The tops of wide strokes dome slightly because the centre lifts more freely than the edges. [M]
3. **Texture on the raised area:** this is flattened, but only partly. [O and I]
   - In a combination die the heated polished brass presses foil onto the top and the walls. The felt "peck" is ironed down, but it still telegraphs at reduced amplitude and higher frequency.
   - [O] ref02 shows faint felt texture on the copper tops. ref04 (flat foil on felt, closest to our stock) shows fine felt in the foil. ref11 shows the pebble field texture **absent** on the foil type.
   - Iggesund says surface irregularities "are strongly accentuated when foiled". [S] So even a small leftover texture shows strongly in a mirror-like foil. That is why its amplitude must drop.
4. **Texture in a recess (deboss):** the felt is kept but compressed. The floor is smoother and slightly darker or glossier; the walls are smeared. [O] ref03, ref12, ref13.
5. **Crush halo (deboss, ref12) [O and I]:** the flat land of the die around the image crushes the felt for about 0.3 to 1 mm, leaving a smoother, slightly glossier ring. The paper top edge rolls into a rounded lip. On a raised emboss the matching effect is weak. With a heated combination die on dark stock, a faint burnished or "glazed" ring can appear around the foot [M]. Zevendesign mentions glazing and burn marks on dark heavy stocks [S]. Treat this as optional and subtle.
6. **Back-side imprint [S]:** the reverse carries the negative of the emboss. On glass this is the unbonded air pocket noted in section 1.3. Seen from inside the bottle, through the liquid, the glass-to-air interface under the letters reflects more strongly than the glued areas, so the wordmark ghosts faintly from behind. [I]
7. **Foil cracking [S]:** a die that is too deep or too steep shows "crimping at the corners or cracking and cutting through in highly detailed areas". A gradual bevel lets you go higher without tearing. [S] search summaries of creativepro and zevendesign. Steep walls give the same symptoms as an overly deep die. [S] For AVANTE at 0.2 mm on thin felt stock, a premium job would show **no** cracking. Do not add crack artefacts. [R]

---

## 3. How relief reads in photographs

### 3.1 Sourced lighting facts
- Raking light at 5 to 15 degrees to the surface is the standard way to reveal relief. A narrow or point source gives crisp shadows, while a diffuse source "reduce[s] contrast in surface texture". Light from the top-left avoids depth inversion. [S] https://conservation-wiki.com/wiki/Raking_light , https://cameo.mfa.org/wiki/Raking_light
- "Foil reflects light and its surroundings"; a bevel catches light in several places. [S] zevendesign.

### 3.2 Highlight geometry
These relations are derived [I].
- **Paper (diffuse):** relief reads through shading. The lit shoulder brightens by a factor of cos(θi − slope)/cos(θi). With a grazing key at 75 degrees from the normal and a 30 degree shoulder slope, the lit shoulder is about 1.7 times brighter and the shadow side about 0.2 times. At 45 degree incidence the contrast drops to about 1.2 and 0.6. This is why our big soft key (0.9 x 1.2 m) flattens the relief.
- **Foil (specular):** relief reads through **reflection change**. Tilting a surface by s degrees moves its reflection by 2s. A 30 degree shoulder therefore reflects a part of the studio 60 degrees away. If that part is dark, the shoulder goes dark; if it is a card, the shoulder lights. Relief on foil therefore needs a **contrasty environment** (cards plus black flags), not a stronger light. ref01 and ref02 show exactly this: mirror-black and blazing facets.
- **Width of a highlight line on a rounded shoulder:** about R x α/2, where R is the shoulder radius and α is the angle the source subtends.
  - With R = 0.3 mm and a 10 degree strip (0.17 rad), the line is about 0.026 mm wide: a crisp, sub-pixel, "drawn" line.
  - With a 60 degree softbox it is about 0.16 mm, or about 4 px at the macro scale.
  - Depth sets how far the line sits from the foot, roughly the shoulder width, about 1.5 to 2 times h for a 30 to 35 degree flank. Source size sets how sharp the line is.
- **Macro scale:** AVANTE caps measure about 190 px in `v004_foil_macro`. Estimating the front face at about 75 mm across 2000 px gives **about 26 px/mm** [I, estimate].
  - 0.2 mm of relief is about 5 px in height, seen almost face-on.
  - A hard 1-texel wall (0.05 mm) is 1.3 px. **This is the thin outline we see.**
  - A physical rounded shoulder of 0.3 to 0.4 mm would be a gradient band 8 to 10 px wide.

### 3.3 Inferred cross-sections of the references
All heights are estimates from apparent shading [O and I].
| Ref | Treatment | Height | Profile | Shoulder / edge radius | Texture |
|---|---|---|---|---|---|
| ref01 barrel and coins | Sculpted multi-level foil-emboss on heavy textured stock | 0.3 to 0.5 mm | Faceted planes with crisp ridges; coins domed with raised rims | Ridges about 0.05 to 0.1 mm; foot blends over about 0.3 mm | Gold mirror-smooth; pebble field kept around |
| ref01 rope borders | Blind emboss | 0.15 to 0.25 mm | Rounded half-rope beads about 1 mm pitch | Fully rounded | Pebble kept, slightly softened on top |
| ref01 scroll ornaments | Foil, flat or slightly debossed | under 0.05 mm | flat | - | Black mirror shows reflection of the environment |
| ref02 Negroni | Copper combination foil-emboss | about 0.2 to 0.3 mm | One level, **rounded (pillow)**; tops slightly domed | About 0.4 to 0.6 mm (strokes 2 to 4 mm) | Felt visible on foil at reduced amplitude; bright upper-left shoulders, dark lower-right |
| ref03 Devils Tower | Letterpress into thick cotton plus blind-debossed rules | 0.1 to 0.2 mm deep | Steep wall, rounded top lip, flat inked floor; rules are U-grooves 0.3 to 0.5 mm wide | Lip about 0.1 mm | Felt kept on floor, compressed |
| ref04 filliers | Flat hot foil on felt | about 0.01 to 0.03 mm (slight deboss) | flat | - | Fine felt telegraphs into foil; **closest analogue to our stock** |
| ref06 Saint Cloud | Cast metal | about 0.3 to 0.5 mm | Rounded figure, crisp lettering | small | Shows reading of relief: lit upper edges, occluded recesses |
| ref09 Botaneg seal | Sculpted gold seal | 0.3 to 0.5 mm | Domed field with raised border; leaves modelled at 2 to 3 levels | rounded, about 0.2 mm | Gold mirror-smooth |
| ref09 type | Dark ink with glossy edge lines | about 0.05 to 0.1 mm | Slight deboss or emboss with a crisp lit edge | small | - |
| ref10 Mark S. Mayne | Deep emboss and deboss text on dark stock | 0.3 to 0.5 mm | **Chisel bevel** (about 45 degree flanks) with flat tops | Sharp ridge | Field texture kept |
| ref11 Blade and Bow | Pebble-embossed field plus raised foil type | Type about 0.1 to 0.2 mm; pebble pitch about 0.5 mm | One level, soft edge | about 0.1 mm | **Pebble absent on foil**: texture flattened |
| ref12 Ol'son | Deep deboss with patterned (engraved-line) foil floor | 0.3 to 0.5 mm deep | Steep walls, crisp; rounded paper lip | Lip 0.1 to 0.2 mm | **Crush halo** about 0.5 mm of smoother paper; foil walls bright on the lit side |
| ref13 Stranger & Sons | Foil deboss on felt | about 0.05 to 0.1 mm | Shallow, bright walls | - | Edges broken up by felt; floor carries faint texture |

---

## 4. Our v004 against reality

Renders examined: `v004_foil_macro.png` with a crop of AVANTE and the bird, `v004_roundel_macro.png` with a crop of the monogram, `v004_collarflag_macro.png`, `qc/v004_paper.png`, `qc/OPTION_roundel_0.2mm_roundel.png`.

1. **Does 0.2 mm read? Only as an outline [O].** AVANTE shows a 1 to 2 px dark or light rim around each glyph and a flat top. There is no shoulder gradient, no doming, and no lit or shadow side wider than a line. It reads as "foil with a drawn keyline", not as pillowed relief. ref02 and ref10 read through 5 to 15 px bands.
2. **Profile is a hard step [I, from code].**
   - The height comes straight from an 8-bit, hard-edged mask: `Displacement Height = MASK-EMB-01`, with only the antialias pixel as a wall.
   - The wall is 0.05 mm wide for 0.2 mm of rise, which is about 76 degrees. That is steeper than the 30 to 60 degree bevel practice [S] and physically shearing for 0.1 mm stock.
   - Linear filtering of the magnified texels adds stair-steps along curves. Method BOTH also bump-shades those texel facets.
3. **Paper is not reacting [O].** The felt runs unchanged right up to the foot. There is no stretched or softened felt on the walls, no foot radius, and no burnish or halo. That is acceptable for a raised emboss, but the foot needs a soft roll-off.
4. **The "crumpled" foil is mostly a shading artefact, not dicing [I, from code plus O].** The likely causes, ranked:
   - a. **Paper felt bump telegraphed onto mirror foil.**
     - `fb` Height = `relief * 0.5`, where `relief` is the felt term (±0.045 mm at about 1.2 mm pitch, noise scale 833) plus the fibre term, with bump Distance 1.0.
     - Felt slopes are about 4 degrees; half of that is 2 degrees. A 2 degree tilt moves the reflection by 4 degrees, which is large on a roughness-0.14 metal.
     - The 1.2 mm pitch is low frequency at macro scale (about 30 px), so it reads as hammered or crumpled metal, not fine felt.
   - b. **Foil roughness noise at scale 800** (about 1.25 mm blobs, ±0.04) adds mottling at the same frequency.
   - c. **Method BOTH bump of the 8-bit, linear-filtered mask** gives jaggy texel-scale facets along the walls and serifs.
   - d. **Dicing.** At 1 px it is about 0.04 mm in the macro, roughly one micropolygon per texel. That is adequate for the current hard step but cannot resolve a shoulder that does not exist yet. It is not the cause of the crumple.
5. **Back shell displaces the wrong way [I, from code; verify in Blender].**
   - The wrap is Solidify (offset +1, rim on), then adaptive subsurf, with the **same material** on both shells.
   - Displacement acts along each face normal. The inner (glass-side) shell's normals face the glass, so the back of each letter is pushed about 0.2 mm **into** the glass. The label's glass gap is only 0.03 mm.
   - Physically, the back should move outward with the front, leaving a cavity.
   - Invisible from the front, but it affects views through the bottle and makes glass-to-label intersections.
   - The roundel back shell has the same issue (0.04 mm into a 0.12 mm gap, so no intersection).
6. **Roundel (0.04 mm stays) [O].** It reads as a thin dark keyline and is acceptable. A 1-texel wall at 0.04 mm/texel is about 45 degrees.
   - Stamped hot foil on film is in practice a very slight **deboss**, with the foil flush or below the film [M; agent4 option B]. The sign is a client decision, not a change in magnitude.
7. **Collar flag [O]:** flat foil, no emboss. That is correct for the spec.

---

## 5. Blender recipe (Cycles, Blender 5.1)

### 5.1 Displacement vs geometry vs bump
| Method | Use for | Why |
|---|---|---|
| True displacement (adaptive) | AVANTE and bird emboss (0.2 mm), roundel (0.04 mm) | Silhouettes and grazing reflections need real geometry. Self-shadowing on the shoulders matters for paper. |
| Real modelled geometry | Not needed | Extruding text with a bevel gives a clean profile, but a 0.1 mm paper shell wrapped on a tapered bottle would make the wrap mesh complex. Displacement from a good height map is equivalent. |
| Bump only | Felt, fibre and foil micro-texture (0.005 to 0.045 mm) | Sub-pixel heights; displacing them would explode the dicing cost. |

Blender 5.0 facts:
- "Adaptive subdivision is no longer an experimental feature, and always available in the Subdivision Surface modifier." [S]
- A new **Object space** option sets an edge length instead of a pixel size. [S]
- With displacement, the Normal Map node now uses the undisplaced normal; `N` includes displacement. [S] https://developer.blender.org/docs/release_notes/5.0/cycles/
- Adaptive subdivision must remain the **last** modifier. The current code complies. [M]

### 5.2 Building the rounded height profile from the vector or mask
Use an offline bake, preferably inside Blender's Python, which ships with numpy. Bake to a **16-bit PNG or float EXR (Non-Color, Cubic interpolation)** at 40 px/mm (0.025 mm/texel) over the emboss bounding boxes only.

**Option A, signed distance field (best) [R]:**
1. Rasterise the vector art at 40 px/mm. Topac requires vector art for real tools. [S]
2. Compute the inside distance `d` in mm, using a Felzenszwalb two-pass EDT in numpy.
3. Height: `h(d) = H * smoothstep(0, W, d) ^ 0.8`, with `H = 0.20` mm and **`W = 0.35` mm**. That is about a 30 degree mean flank, inside the 30 to 60 degree die range [S] and depth no more than half the width [S].
4. Add a **dome term**: `+ 0.10*H * smoothstep(W, W + 0.8, d)`. Wide strokes rise slightly in the centre, as in ref02.
5. Add an **outer skirt** (the paper foot): for `-0.12 < d < 0`, `h = H * 0.04 * (1 + d/0.12)^2`. This softens the foot roll-off without moving the foil edge.
6. Thin strokes (spear, serifs) then never reach full H. That is physically correct per the line-width rule, but **check with the client** that the bird's spear still reads.

**Option B, multi-radius blur (no EDT):** `h = H * clamp(0.45*G(0.06 mm) + 0.35*G(0.18 mm) + 0.20*G(0.40 mm), 0, 1)` computed on the mask, then multiplied by `smoothstep` of a slightly dilated mask so the outside stays flat.
- The small radius keeps corners crisp; the large radius gives the pillow.
- This rounds inside corners more than outside ones, which is fine.

**Option C, shader-only fallback:** this is weaker. Bevel node only affects shading normals, and only on mesh edges, so it does nothing for image-mask displacement. Stacking several Image Texture taps with offset UVs to fake a blur is costly and noisy. Do not use either. [M]

**Keep the foil edge at the foot (d = 0):** foil covers the whole raised image including the walls in a combination die. [I]

### 5.3 Dicing rate
- Aim for at least 4 micropolygons across the shoulder: `W/4` is about 0.09 mm. Ideally use 6 or more, about 0.05 mm.
- Macro shots (about 26 px/mm): `adaptive_pixel_size = 1.0` gives about 0.04 mm. **Keep 1.0. Use 0.5 only if the shoulder still shows facets.**
- Hero and three-quarter shots (about 5 to 8 px/mm): 1 px is 0.12 to 0.2 mm. That is coarse but sufficient, because the relief is at most 2 px in screen space there. Let BOTH carry the shading.
- Do **not** switch to an object-space length of 0.05 mm on the whole wrap. That would be about 10 M quads per shell. If object space is wanted, limit it to a separate emboss patch mesh. [R]
- `Displacement method = BOTH` is fine **once the height is smooth and 16-bit with Cubic filtering**. With the current 8-bit hard mask, BOTH is what produces the jaggy wall shading. [I]

### 5.4 Separating macro relief from micro texture, and texture on the emboss
- Displacement output: the emboss height only. Never add felt into the Displacement input.
- Bump input: a felt/fibre field `relief` multiplied by a **per-zone factor F**, from the baked height `hn = h/H`, with slope estimated from the same map or from a second baked channel:
  - field (`hn = 0`): F = 1.0 (paper as now)
  - walls and shoulders (`0 < hn < 0.9`): F = 0.4 (texture stretched and smeared)
  - foil top (`hn ≥ 0.9`): F = **0.15 to 0.25**, and only the **fibre term plus a high-pass of the felt**. Remove the 1.2 mm low-frequency component, which is what reads as crumple.
  - optional halo ring (`-0.6 < d < 0` mm): F = 0.6, roughness −0.05 (burnished foot, ARTISTIC, keep subtle)
- Foil roughness: drop the noise-800 modulation to ±0.015, **or** move it to scale 4000 or more (sub-0.25 mm) so it reads as foil grain, not blotches. Base about 0.12 to 0.16. [R]
- Make the foil Bump node `Distance` equal the paper bump, and have the Height feed come from `relief*F`, **not** `relief*0.5`.

### 5.5 Back-shell fix (verify first)
Choose one, all [R]:
- (a) Multiply displacement by a front-facing mask: `Geometry > Backfacing` cannot be used in displacement, so use a dedicated **vertex-group or attribute** set to 1 on the outer shell. Solidify's "Shell" vertex group output can name it.
- (b) Put the inner shell on a material without displacement, via Solidify `material_offset`.
- (c) Displace along a stored object-space outward vector instead of N (Vector Displacement, object space).
Option (b) is the simplest. Physically the back cavity should also exist, but it is only visible from inside the bottle. If the three-quarter view shows the label reverse through the liquid, add a faint "air-pocket" look under the letters there: a bump-free, slightly brighter reflection (ARTISTIC).

### 5.6 Lighting to reveal it (coordinate with the lighting agent)
- For macro shots, add a **narrow strip** (0.03 to 0.05 m wide), 10 to 20 degrees above the label plane, from upper-left. It makes a crisp shoulder line (R·α/2 is about 0.03 mm) on paper and foil. [S raking practice; I geometry]
- For foil, place a **black flag** next to `CRD_Foil_Specular`, so shoulders tilted 25 to 35 degrees reflect dark while tops reflect the card. This gives the ref02 and ref01 bright/dark contrast.
- Keep the big key for the paper, but at a more grazing angle to the label for the macro.

---

## 6. Gap list, ranked by visual impact
| # | Gap | Fix | Expected result | Test |
|---|---|---|---|---|
| 1 | **Crumpled foil**: felt bump at 0.5 x and roughness noise-800 on mirror foil | Foil bump = fibre plus high-passed felt at 0.15 to 0.25 x; roughness noise to ±0.015 or scale 4000 or more | Smooth, premium foil with faint fine grain, like ref04 and ref02 | A/B crop at 100% of AVANTE; no blotches above 0.3 mm in size |
| 2 | **Hard-step profile**: 8-bit mask, about 76 degree wall, reads as a keyline | Bake 16-bit SDF height (W = 0.35 mm, dome +10%, foot skirt); Cubic filtering | 8 to 10 px shoulder gradient at macro; reads as pillow emboss | Raking-strip macro; shoulders show a lit band and a shadow band, no outline |
| 3 | **Studio does not reveal relief on foil** | Strip light at 10 to 20 degrees plus black flag beside the foil card (macro only) | Bright upper-left shoulders and dark lower-right, as in ref02 | Same crop; shoulder band contrast at least 3:1 on foil |
| 4 | **Back shell pushed into glass** | Inner shell without displacement (5.5b) | No glass intersection; correct three-quarter view through the bottle | Section view in Blender; check gap ≥ 0 under letters |
| 5 | **Texture not zoned** | F field: field 1.0, walls 0.4, top 0.2, optional halo 0.6 | Paper reacts to the die | Macro under raking light |
| 6 | **Thin strokes forced to full 0.2 mm** | The SDF profile limits them automatically | Spear and serifs lower and softer, physically right | Client check that the spear still reads |
| 7 | **Roundel keyline** | Optional: blur the roundel height by 0.06 to 0.08 mm (16-bit). Keep 0.04 mm. Raise the sign question (stamped foil is usually flush or debossed) | Softer, more stamped look | Roundel macro |
| 8 | Optional back-side air-pocket ghost (wrap seen through the liquid) | Brighter reflection under the letters on the reverse | Subtle realism in the three-quarter view | Three-quarter render only |
| 9 | Optional burnish halo | Ring 0.3 to 0.6 mm, felt × 0.6, roughness −0.05 | Very subtle; skip if not visible | Macro only |

Not recommended:
- foil cracking or flaking (a premium job shows none; deep or steep dies cause it [S])
- sculpted multi-level relief (not in spec; ref01 and ref09 are a different treatment)
- deboss crush halos (no deboss in spec)

## Sources
- Iggesund, Embossing and debossing in practice (Graphics Handbook pp. 63 to 65): https://www.iggesund.com/globalassets/iggesund/services/knowledge/iam/graphics-handbook/gh-pdf----en/embossing_and_debossing_in_practice.pdf
- Topac, Technical information on embossing/debossing: https://www.topac.de/fileadmin/content/c_Leistungen/Embossing_Debossing.pdf
- Topac, Technical information about foil embossing: https://www.topac.de/fileadmin/content/c_Leistungen/Foil_embossing.pdf
- Billerud, Embossing: see and feel the third dimension: https://www.billerud.com/trends-and-cases/all/print-techniques/embossing-see-and-feel-the-third-dimension
- Zevendesign, graphic designer's guide to embossing: https://zevendesign.com/graphic-designers-guide-embossing/ (note: its "15 to 25 microns" depth line contradicts its own "1/64 inch average" and other sources; disregarded)
- CreativePro, Printing Tips: embossing (403 on fetch; numbers from search snippets only): https://creativepro.com/printing-tips-enter-the-third-dimension-with-embossing/
- Spicers, Design, Print and Application Guide (labels): https://www.spicers.com.au/application-guide
- Avery Dennison Fasson offset label paper data sheet: https://graphics-test.averydennison.com/content/dam/averydennison/graphics/eu/en/Data-Sheets/Fasson/ds_fasson_labels_offset_papers_en.pdf
- Briar Press forum (counters, cotton deboss show-through): https://www.briarpress.org/26298 , https://briarpress.org/21501
- Owosso Graphic Arts die range (PPAI listing): https://www.ppai.org/solution/owosso-graphic-arts/
- Raking light: https://conservation-wiki.com/wiki/Raking_light , https://cameo.mfa.org/wiki/Raking_light
- Blender 5.0 Cycles release notes: https://developer.blender.org/docs/release_notes/5.0/cycles/
- Not found: published depth vs caliper tables for label stocks; Universal Engraving or Metal Magic spec pages; pressure-sensitive emboss depth limits. Ask the converter or die maker for these.
