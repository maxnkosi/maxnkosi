# v005 Study A: Hot-foil appearance (AVANTE wordmark, bird, roundel)

Read-only study. No project files, Blender or git were touched. Every claim carries a tag:

- **[S]** sourced (URL in §8)
- **[O]** observed in the reference images or our renders (pixel numbers measured from crops; method in §2.1)
- **[M]** from memory, not verified this session
- **[A]** artistic recommendation or estimate

---

## 0. Summary

1. **Our foil has no value range.** The AVANTE letters cover only 19 levels of luminance (8-bit, p5 to p95 = 151 to 170). Across the refs that span is 95 to 180 levels. The brightest 1% of our foil peaks at 172; the refs peak at 188 to 249. A real gold foil is near-black or brown where it reflects the studio and near-white where it reflects a source. Ours is a uniform mid-tone. A pale, warm metal with no highlight and no shadow reads as "sand or champagne". [O]
2. **The main cause is lighting, not the material.** `CRD_Foil_Specular` is 1.1 m × 0.42 m at about 0.5 m from the label, so seen from the label it fills roughly ±60°. The whole AVANTE word, as seen from the macro camera, only spans about ±7.4° of mirror direction. Every letter therefore reflects the same evenly lit card, at emission 0.95, which is too dim to show up as a highlight under AgX. [O, A]
3. **The "crumpled" look comes from the micro-relief.** The foil bump is the paper relief at half strength, and that relief is dominated by the 1.2 mm felt noise (45 µm × noise, Detail 2). On top of it, the roughness noise sits at the same ~1.2 mm scale (`noise(800)`, 0.14 to 0.22). Real hot foil is pressed by a polished, heated die. The tops of the stock come out flat and mirror-like, and texture survives mainly as **pits and valleys** plus a **fine** fibre grain. Mm-scale undulation over the whole surface is wrong. [S for the process, O, A]
4. **Colour is only a minor factor.** FOIL_F0 (0.95, 0.69, 0.33) is close to pure gold: Johnson & Christy n,k give R ≈ 0.96 / 0.79 / 0.41 at 650 / 550 / 450 nm, and Blender's own gold preset is (1.000, 0.735, 0.353). Commercial "gold" foil is actually **aluminium under an orange or yellow lacquer**. Modelling it that way (Principled with Coat Tint) gives the angle-dependent deepening to amber and brown that the refs show, plus a thin white lacquer sheen. [S]
5. **Fix order (biggest effect first):** reflectable lighting, then a die-flattened micro-relief, then roughness of 0.06 to 0.10 with no mm-scale noise, then the aluminium + tinted coat model, then edge and bevel work, then pinholes. Details in §6.

---

## 1. How hot foil actually sits on paper

### 1.1 Layer structure and thickness [S]
The stack, from the carrier side to the paper side:

| Layer | Typical thickness | Role |
|---|---|---|
| PET carrier | ~12 µm (min ~4 µm) | Removed after stamping |
| Release (wax) | 0.01 to 2 µm | Lets go under heat |
| Protective / **colour lacquer** | ~1 µm (0.25 to 10 µm) | Becomes the **top surface** on the paper. A coloured lacquer (e.g. orange) over aluminium is what makes "gold". Its chemistry also sets gloss, satin or matt |
| Vacuum-metallised **aluminium** | 20 to 100 nm (holographic: 40 to 60 nm) | The mirror |
| Heat-activated adhesive | 0.75 to 4 µm | Bonds to the stock |

Sources: US4275116 and US6514586 (patents), the Foil Doctor manufacturing page ("a coloured lacquer (i.e. orange to produce a gold)"), and the US5736253 / US4256794 descriptions of lacquer + metal layers.

**What this means for the render.** Once transferred, the foil is only about **2 to 6 µm** thick. That is far too thin to bridge paper texture by itself. What flattens the texture is the **die**: heat and pressure from a polished brass or magnesium die calender the fibres under the foil. Where the die reaches, the foil is flat and mirror-like. Where the stock has recesses deeper than the die compresses, the foil follows them, or fails to transfer. [S for thickness; inference A]

### 1.2 Conforming, bridging and telegraphing [S + O]
- Printers state that texture shows through foil, that pressure is set by the stock's weight and texture, and that felt and linen are harder to foil. A standard impression is described as "smooth, light", keeping the paper's original texture (howinteractivedesign, carlsoncraft, papierdirekt summaries in §8). [S]
- On heavily textured stocks, only the raised parts fully connect with the foil, so coverage in the recesses is incomplete or patchy (aura-print). [S]
- **The refs split into two families: [O]**
  - **Texture telegraphs strongly:** ref08 (linen-screen stock; the regular weave is fully visible in the foil, each cell carrying its own glint), ref13 (felt or grey textured stock; mottle plus dark pits inside the letters), ref02 (fine fibrous micro-grain across the domed copper), ref04 (fine speckle on burgundy uncoated).
  - **Texture suppressed:** ref01 (leaves, coins and sculpted barrel are smooth mirror, although the surrounding stock is strongly pebbled), ref09 (raised seal elements are mirror-smooth; only the recessed field keeps a fine orange-peel), ref11 (the pebble stock does **not** show through the embossed letters).
  - The rule behind the split: **deep sculpted or embossed dies flatten the stock under the foil, while flat, light-pressure stamping keeps it.** Where texture survives, it shows as a **fine, high-frequency grain or regular weave plus scattered dark pits**. It never shows as a soft mm-scale "hammered" undulation of the whole surface. [O, A]

### 1.3 Defects: edge, fill-in, pinholing, crackle [S + O]
- **Fill-in** is bridging between characters or into tight counters. Soft uncoated stock makes it worse because the die sinks deeper. **Ragged or fuzzy edges** come from uneven pressure or overheating, which over-transfers and spreads the foil. [S: kluge.biz, ciofficial, labelandnarrowweb]
- **Pinholing** (tiny dropouts) is documented mainly for cold foil on absorbent stock. On hot foil the same look appears as **dark specks where fibres or valleys did not take foil**; ref13 and ref04 show it. [S, weak; O]
- **Micro-crackle:** I found no source for hot foil on paper. It belongs to over-flexed or over-cured foils. Do not add it. [A]
- **Edge definition:** in the refs, foil edges are crisp at macro. ref13 and ref01 show a thin bright rim where the debossed wall catches the light and a dark wall on the far side. That shading is **directional**, not a uniform outline all the way round. [O]

---

## 2. Foil types in the refs and their optics

| Type | Where | Construction | Optical signature |
|---|---|---|---|
| Bright (mirror) gold | ref01, ref09, ref11, ref04 | Al + orange/yellow lacquer, glossy lacquer cast on smooth PET [S] | Very low roughness. Near-black or olive-brown off-specular; white-yellow highlight core; the saturated gold lives in the **falloff** between them [O] |
| Pale / champagne gold | ref13 (and the AVANTE spec) | Same, with a weaker yellow lacquer [S, inferred] | Same value range as bright gold (ref13: p5 67 to p95 245), only less saturated (sat p50 0.23) [O] |
| Satin / matte gold | ref08 (partly) | Matt lacquer with micro-rough surface [S]; matte foils run 235 to 285 °F against 194 to 212 °F for bright (mybinding) [S] | Wider, softer highlights. Glints break up into per-cell sparkle on textured stock [O] |
| Copper / rose gold | ref02, ref07 | Al + red-orange lacquer [S, inferred] | ref02 mid tone (216, 118, 27), very saturated orange; darks (114, 39, 0). ref07 shifts from pale pink-gold to orange copper across the label as its large source falls off [O] |
| Silver / grey | ref10 | Bare Al, or a smoke-grey lacquer [A] | Bevel-driven gradient from bright to charcoal [O] |
| Holographic / diffractive | (not truly in refs) | ~µm-pitch relief embossed into the lacquer with a nickel shim, then metallised [S] | Rainbow dispersion. Needs a thin-film or diffraction model; **not** what ref12 shows |
| Engraved-line die | ref12 | Fine parallel lines engraved into the **die**, not the foil; H+M offer over 600 die textures [S] | Line pitch ~0.1 to 0.2 mm (estimate [O]), far too coarse to diffract. Gives **anisotropic** streak highlights across the lines, with green Al + lacquer [O, A] |
| Pigment foil | ref09 (ink-coloured deboss, probably) | Pigment layer, no metal, clear gloss lacquer [S] | Dielectric: diffuse colour plus a ~4% sheen |

**Lacquer as a physical layer [S, Blender manual].** Principled BSDF's Coat Tint "adds a colored tint to the coat layer by modeling absorption in the layer", and saturation increases at shallow angles because light travels farther through the layer. That is exactly how lacquer over aluminium behaves: deeper amber-brown off-angle, plus a ~4% uncoloured reflection from the lacquer surface.

**Gold reference data [S]:**
- Au, Johnson & Christy (refractiveindex.info):
  - 450.9 nm: n 1.38, k 1.914 → R 0.408
  - 548.6 nm: n 0.43, k 2.455 → R 0.787
  - 659.5 nm: n 0.14, k 3.697 → R 0.963
  - R computed by me with R = ((n-1)² + k²)/((n+1)² + k²).
- Blender Metallic BSDF gold preset (F82): Base 1.000 / 0.735 / 0.353, Edge Tint 0.993 / 1.000 / 1.000.
- physicallybased.info gold: 1.059 / 0.773 / 0.307.

### 2.1 Measured foil tones (8-bit sRGB, warm-foil pixels only) [O]
Method: crop each foil area; keep pixels with R ≥ G ≥ B and G − B > 25; report luminance percentiles and samples at the 5 / 50 / 95 % brightness ranks.

| Image | L p5 | L p50 | L p95 | L p99 | Sat p50 | Dark (5%) | Mid | Bright (95%) |
|---|---|---|---|---|---|---|---|---|
| **v004 AVANTE** | **151** | **166** | **170** | **172** | 0.27 | (170,149,116) | (184,164,134) | (188,169,140) |
| v004 bird | 94 | 148 | 171 | 176 | 0.32 | (113,93,61) | (167,146,112) | (189,170,141) |
| v004 roundel | 87 | 152 | 169 | 171 | 0.32 | (105,86,55) | (171,150,117) | (187,168,139) |
| ref02 copper | 52 | 132 | 180 | 188 | 0.83 | (114,39,0) | (216,118,27) | (251,172,54) |
| ref04 gold/burgundy | 86 | 197 | 237 | 245 | 0.44 | (130,79,36) | (239,190,147) | (249,240,185) |
| ref08 gold/linen | 75 | 202 | 240 | 247 | 0.38 | (82,77,39) | (221,203,141) | (255,244,164) |
| ref09 gold seal | 52 | 120 | 215 | 235 | 0.47 | (68,51,25) | (145,119,70) | (235,214,171) |
| ref11 gold/black | 93 | 146 | 222 | 243 | 0.50 | (126,90,32) | (190,140,81) | (249,220,164) |
| ref13 pale gold/grey | 67 | 203 | 245 | 249 | 0.23 | (84,66,30) | (221,202,162) | (255,246,206) |

What the table shows:
- **Our hue is right.** AVANTE's mid tone has a B/R ratio of 0.73, the same as ref13's pale gold. So the brand's pale gold is achievable; the colour is not what is wrong.
- **Two things are missing:**
  1. The **highlight**: refs reach 235 to 255 with a near-white core; we stop at about 172.
  2. The **dark, saturated falloff**: refs bottom out at olive-brown (68–84, 51–77, 25–39). Our AVANTE never drops below 151.
- Even our roundel, which has no paper bump, peaks at 171. That points to the **light source** as the ceiling, not the material.

---

## 3. Per-reference optical reading, and why ours does not do it [O]

- **ref01 Camikara (gold on pebbled cream, multi-level sculpted die)**
  - What it does: the KARA letterforms are debossed **mirror** foil reflecting the black studio, so the faces read near-black. Each bevel wall carries a hairline gold rim where it faces the key. The leaves are sculpted with curvature, so each one sweeps from black through saturated amber to a white-yellow streak. The coins are low-relief sculpted, showing satin-to-mirror gradients across the rims and fine engraving. The paper pebble does **not** telegraph through the foil on the sculpted parts.
  - Why ours differs: our foil faces never reflect anything dark, and our surface carries a mm-scale undulation that ref01's foil does not.
- **ref02 Negroni (copper, rounded emboss on laid / felt stock)**
  - What it does: the domed strokes give one continuous highlight band along each stroke, falling off to deep red-brown at the flanks. A **fine** (sub-0.2 mm) fibrous grain is visible through the foil at low amplitude, enough to make the highlight satin rather than mirror, with no visible lumps.
  - Why ours differs: our letters are flat-topped plateaus, so there is no band; and our grain is mm-scale and lumpy, not fine.
- **ref04 Filliers (flat gold on burgundy uncoated, bright white environment)**
  - What it does: most of each letter is bright because the white sweep fills the reflection. Per-letter brightness changes with the bottle's curvature (the "f" and the "s" differ). Fine dark speckle comes from fibres that did not take foil.
  - Why ours differs: the environment here is bright *and structured*. Ours is evenly lit and dim.
- **ref07 Monte (copper / rose gold, flat, on green felt)**
  - What it does: one large gradient source mirrored across a **cylinder**. The upper letters are pale pink-gold, the lower ones saturated copper; the colour shift is the falloff, not two foils. Letters are internally uniform, with crisp edges.
  - Why ours differs: our label face is (near) flat, so we need the gradient *in the light* instead of in the geometry.
- **ref08 Mondoro (gold on dark green linen-screen stock)**
  - What it does: the foil fully follows a regular weave of ~0.3 to 0.5 mm pitch (estimate). Each cell has a tiny glint, and letters vary from yellow (M, D, O near the light) to olive-brown (lower letters).
  - Why ours differs: the texture there is *regular and fine*, so it reads as fabric. Ours is irregular and coarse, so it reads as crumpled.
- **ref09 Botaneg (sculpted gold seal, pigment deboss for type)**
  - What it does: the raised leaves and "B" are mirror with crisp bevel streaks. The recessed field is satin with a fine orange-peel and goes khaki-olive off-angle (dark samples (68, 51, 25)).
  - Why ours differs: ref09 has two roughness zones, smooth raised and grainy recessed. We have one uniform zone.
- **ref10 Mark S. Mayne (silver / grey foil emboss on charcoal stock)**
  - What it does: the bevelled letters run from bright silver on the lit faces to charcoal; reading depends entirely on the bevel normal.
  - Why ours differs: our bevel is narrow and symmetric.
- **ref11 Blade and Bow (gold emboss on black pebble stock)**
  - What it does: pillowed letters, a smooth satin-mirror surface, an orange-gold highlight band on each letter's lit shoulder and brown-orange elsewhere. The pebble does not show through.
- **ref12 Ol'son (green metallic, engraved-line die, deep rounded deboss)**
  - What it does: the parallel engraved lines make anisotropic streak highlights; the rounded bevel walls go from bright lime to dark green; the deboss throws soft shadows on the paper lip.
  - Relevance: N/A for AVANTE, except as proof that a debossed foil needs a rounded wall profile.
- **ref13 Stranger & Sons (pale gold, debossed, on grey textured stock)**
  - What it does: this is the closest analogue to AVANTE on uncoated stock. The foil *does* carry the paper mottle, but at **very high contrast**: near-white plateaus (255, 246, 206) next to olive-brown pits (84, 66, 30). There is a raised paper lip (pillowing) around each letter.
  - Why ours differs: our mottle is the same idea at about 1/8 of the contrast, because the foil reflects one even grey card. Without dark surroundings to reflect, the mottle reads as dirt, crumple or sand.

---

## 4. Diagnosis of v004 (code references: `build_avante_master.py`)

| # | Finding | Evidence |
|---|---|---|
| D1 | Foil reflects one huge, even, dim card | `soft_card('CRD_Foil_Specular', (0,-0.55,0.075), 1.1, 0.42, 0.95, ...)`. Macro camera at y=-0.28, focus 0.235 m, 100 mm lens: AVANTE (~61 mm wide in an ~85 mm field) spans about ±7.4° of reflection direction, while the card spans about ±60°. Spherical-gradient emission (^0.55) at strength 0.95 maps to ~170/255 after F0 and AgX [O, A] |
| D2 | Mm-scale foil undulation | Foil bump Height = 0.5 × relief = 0.5 × (felt·45 µm + fibre·12 µm). The felt term is `noise(833)` (1.2 mm, Detail 2, so octaves at 0.6 and 0.3 mm of roughly equal slope). The foil therefore follows the full felt relief at about 22 µm p-p, giving a few degrees of normal wobble per octave and ~5–10° of reflection wobble. That is the crumple. [O + estimate A] |
| D3 | Roughness mottle at the same scale | `noise(800)` drives roughness 0.14 to 0.22, i.e. 1.25 mm blotches of gloss. This doubles up with D2. [O] |
| D4 | Base roughness too high for bright foil | 0.18 mean, before the bump adds apparent roughness. Bright foil wants about 0.05 to 0.10. [A] |
| D5 | No lacquer layer | Pure metallic F0, so no angle-dependent deepening and no white lacquer sheen. [A] |
| D6 | Emboss edge reads as an outline, not a bevel | The 100 % crop shows a uniform dark ring plus a light inner line around every letter. Refs show directional bright/dark walls with a rounded profile. EMB mask is fed unblurred into displacement (0.2 mm). [O] |
| D7 | Roundel: same light ceiling | Peaks at 171 even without paper bump. [O] |

---

## 5. Cycles recipe (Blender 5.1)

### 5.1 Base shader, option A (preferred): aluminium + tinted lacquer [S model, A values]
Principled BSDF on the foil branch:

| Input | Bright gold (refs 01/09/11) | **AVANTE pale gold** | Copper (02/07) | Silver (10) |
|---|---|---|---|---|
| Base Color (Al) | 0.91, 0.91, 0.92 | 0.91, 0.91, 0.92 | 0.91, 0.91, 0.92 | 0.91, 0.91, 0.92 |
| Metallic | 1.0 | 1.0 | 1.0 | 1.0 |
| Specular Tint (F82 edge) | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 |
| Roughness | 0.06 | **0.07** | 0.10 | 0.12 |
| Coat Weight | 1.0 | 1.0 | 1.0 | 1.0 (tint white) |
| Coat IOR | 1.50 | 1.50 | 1.50 | 1.50 |
| Coat Roughness | 0.05 | 0.06 | 0.08 | 0.10 |
| Coat Tint | 1.00, 0.70, 0.26 | **1.00, 0.77, 0.40** | 1.00, 0.55, 0.28 | 1, 1, 1 |
| Approx. normal-incidence colour | 0.91, 0.64, 0.24 | 0.91, 0.70, 0.36 (≈ current FOIL_F0 hue) | 0.91, 0.50, 0.25 | 0.91 |

Notes:
- **Coat Tint at normal incidence.** I recall (from Cycles source, **[M]**) that Coat Tint is applied once with an optical depth of 1/cosθ_t, so at normal incidence the result ≈ tint × Al. **Verify** with a flat swatch render facing the camera: the sRGB value of the reflected white card should land near the "approx." row.
- **Anisotropic = 0** for all of these. Lacquer cast against polished PET has no brushing. Use anisotropy only for an engraved-line die look like ref12 (0.7, with the tangent along the lines). [A]

### 5.1b Option B (quicker A/B): Metallic BSDF
- **F82 Tint mode:** Base 0.92 / 0.70 / 0.36 (pale) or 1.000 / 0.735 / 0.353 (Blender gold); Edge Tint 0.99 / 0.97 / 0.90; Roughness as in the table.
- **Physical Conductor mode, Johnson & Christy gold:** n = (0.16, 0.43, 1.38), k = (3.5, 2.46, 1.91) for R, G, B. This is *pure gold*: deeper and more orange than pale foil, so use it for bright-gold tests only.
- **Distribution:** Multiscatter GGX, so energy is not lost on rough walls. The manual warns it can look darker than expected. [S]

### 5.2 Micro-relief that reads as die-pressed foil, not crumple [A, scales from the refs]
Replace `foil Height = 0.5 × relief` with three terms:

1. **Felt pits (die-flattened).**
   - Feed the felt noise (scale 833 /m, Detail 2) into a Map Range set to *Smootherstep*: From Min 0.30, From Max 0.48, To 0 to 1.
   - Multiply the result by **6 µm**.
   - The tops (≥ 0.48) become **flat**, so they behave as mirror plateaus. Valleys become smooth pits about 6 µm deep covering ~20 to 30 % of the area.
   - This keeps ref13's character (bright plateaus, dark pits) without whole-surface wobble.
   - On the embossed 0.2 mm area, where die pressure is highest, reduce to **3 µm**.
2. **Fibre grain** (satin micro-structure, as in ref02 and ref04). Anisotropic noise scale ~(4000, 800, 4000) as now, i.e. 0.25 × 1.2 mm, or isotropic noise scale **6000 to 10000 /m** (0.1 to 0.17 mm). Height **1.5 to 3 µm**.
3. **Nothing at 0.5 to 2 mm except the pits.** Delete any whole-surface low-frequency term from the foil.

Bump node: Strength 1.0, Distance 1.0, height in metres (object scale 1), as now. Check visually that the strongest normal tilt on the plateaus is under ~1°. A mirror plateau must reflect a straight strip edge as a straight line.

**Roughness variation:**
- Remove `noise(800)`.
- Use noise at **8000 /m** (0.12 mm) with an amplitude of **±0.015** around the base.
- Optionally add **+0.04** in the pits (via the pit mask): fibres in the valleys are rougher.

Expected look: crisp reflections of a strip across each letter, broken only by small dark pits and a faint satin grain. Test: put a hard-edged strip in reflection and check that its edge stays straight across a letter, wobbling by less than one stroke width.

### 5.3 Edges, bevel and deboss / emboss profile [A]
- **Bevel the height mask.** Blur EMB mask by about **0.10 to 0.15 mm** (≈ 6 to 9 px if the texture is ~60 px/mm; derive from the texture's px/mm), then apply Map Range Smootherstep 0.15 to 0.85. A rounded die wall then catches the strip as a thin bright rim on one side and goes dark on the other, as in refs 01, 11 and 13.
- **Pillowing.** If the foil is debossed rather than embossed (as in ref13 and ref12), add a **+15 to 30 µm** paper lip in a 0.3 to 0.5 mm ring outside the edge. Do this only if the approved spec allows it; currently EMB-01 is a 0.2 mm emboss.
- **Edge micro-break.** Perturb the foil-mask threshold with noise at **20000 /m** (50 µm), amplitude ±0.05 of the mask ramp. That gives a ragged edge of about 20 to 40 µm, visible only at 1:1 macro.
- **Pinholes.** Voronoi (F1) at **3000 to 5000 /m**, threshold so that **0.5 to 1.5 %** of the foil area drops out to paper. Bias the dropouts towards the pit mask (low felt values). The holes should show the *navy paper*, not black.

### 5.4 Lighting the foil reads by [S principle, A geometry]
Foil only reads bright where it reflects a source, and reads dark where it reflects dark (photography sources, §8). Work out the setup from the camera:

1. **Remove or dim the giant even card.** Replace it with a **narrow horizontal strip softbox** that the foil sees in reflection:
   - Width (vertical extent) about 4 to 8° as seen from the label, i.e. ~2 to 4 cm tall at 0.3 m. Length about 30 to 40 cm.
   - Emission **6 to 12**, white to slightly warm (1.0, 0.97, 0.92).
   - Place it so its mirror image crosses the **upper third** of the AVANTE letters from the macro camera. For a flat label facing −Y, that means a little above the camera and behind it on the mirror line, at a z offset of ≈ 2 × the label-to-camera height difference.
   - Expected: a bright, near-white band across the letters that falls off to amber, then brown below.
2. **A gradient card for the falloff.** A second, larger card *below* the strip with a **linear** (not spherical) gradient from about 1.5 down to 0 over ~15°, so the lower letter parts fall from amber to dark brown.
3. **Black around the camera.** A black flag (0.003 albedo) filling the remaining camera-side hemisphere (except the camera hole), so the off-specular foil has something dark to reflect. This is what produces ref01's and ref13's olive-to-black darks.
4. **Hero / three-quarter shots.** The bottle face is near-flat, so each new camera angle needs its own strip position. Alternatively, yaw the bottle 3 to 6° so the strip reflection lands on the wordmark.
5. **Exposure target (AgX, no look).**
   - Foil highlight core should reach sRGB **≥ 240** on G.
   - The darkest 5 % of foil should sit around **(70–90, 55–70, 25–35)**.
   - The mid should be a saturated amber-gold, about **(200–220, 165–185, 100–130)** for pale gold.
   - AgX desaturates very bright values towards white **[M]**. That is correct for the highlight core (ref13's (255, 246, 206)); the colour has to come from the falloff, which only exists if the lighting has one.
6. **Roundel.** Same principle: one strip whose reflection crosses the monogram diagonally, so the curl ends go dark.

---

## 6. Gap list (ranked by visual impact) with fixes

| Rank | Gap vs refs | Fix | Acceptance test |
|---|---|---|---|
| 1 | **No specular contrast.** Foil spans 151 to 172 against refs' 52–93 to 235–255 | §5.4: narrow bright strip (emission 6 to 12) + linear gradient card + black camera-side flag; remove or dim `CRD_Foil_Specular` | Rerun §2.1 stats: p5 ≤ 100, p99 ≥ 235 on AVANTE |
| 2 | **Crumpled mm-scale wobble** | §5.2: die-flattened pits (6 µm, smootherstep plateau) + fine grain (1.5 to 3 µm at 0.1 to 0.17 mm); delete the 0.5 × felt relief | A straight strip edge reflects straight across a letter; no blobs larger than ~0.3 mm on the plateaus |
| 3 | **Roughness too high, with mm mottle** | Base 0.07 (pale) or 0.06 (bright); variation ±0.015 at 0.12 mm; +0.04 in pits | Highlight band edge is sharp, with a falloff width of ≈ 1 to 2 stroke widths, not a whole letter |
| 4 | **No off-angle deepening, no lacquer sheen** | §5.1 Al + Coat Tint (1.00, 0.77, 0.40), Coat IOR 1.5 | In the gradient region, foil goes amber, then brown-olive, never grey-beige |
| 5 | **Edge reads as an outline** | §5.3 blurred and smoothed EMB height (0.10 to 0.15 mm wall) | Lit-side walls show a bright rim and shadow-side walls go dark; no uniform ring |
| 6 | **Roundel foil capped at ~170** | Strip reflection across the roundel; same shader as option A (no paper term) | Roundel p99 ≥ 235 |
| 7 | **No pinholes or edge micro-break** (macro realism only) | §5.3 Voronoi dropouts 0.5 to 1.5 % showing navy; 50 µm edge noise | Visible at 100 % macro only; invisible in the hero |
| 8 | **Single roughness zone** (ref09 has smooth raised parts and a grainy field) | Optional: grain amplitude × (1 − emboss height) so the embossed plateau is the smoothest | Embossed letter tops are the cleanest mirror |

Do **not**:
- add anisotropy;
- add mm-scale noise of any kind to the foil;
- push FOIL_F0 paler or whiter to get "brightness" (brightness comes from the light);
- add holographic or thin-film effects.

Thin Film on the Principled BSDF is only for a deliberate iridescent foil.

---

## 7. Verification protocol (for whoever implements)
1. **Swatch scene.** A flat 30 × 30 mm foil swatch on navy SUB-01 under the new strip rig, with three cameras at 0°, 15° and 35° from the mirror direction. Record sRGB at the strip core, the falloff and off-specular. Compare against ref13 (pale) and ref11 (bright) from §2.1.
2. **Macro AVANTE.** Rerun the §2.1 measurement (crop y 1000–1300, x 300–1000 in the 2000 × 1600 render).
3. **Strip-edge straightness check** (gap 2).
4. **Hero.** Confirm the wordmark has one bright band plus darker areas and does not read as uniform beige at 1000 px wide.

---

## 8. Sources
Foil construction and process:
- Layer stack and thicknesses: [US4275116](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4275116), [US6514586](https://patents.google.com/patent/US6514586), [US5736253](https://patents.google.com/patent/US5736253), [US4256794 Blocking foil](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4256794), [US6316082](https://patents.google.com/patent/US6316082)
- Coloured lacquer makes gold; holographic, pearl, pigment types: [Foil Doctor, foil manufacture](https://www.oocities.org/foildoctor/Foilsmfr.html)
- Aluminised, "not actually gold": [FirstMold, hot stamping](https://firstmold.com/?p=21190)
- Holographic shim embossing, 40 to 60 nm Al: [US5948199](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5948199), [US5810957](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5810957), [Kluge hologram guide](https://www.kluge.biz/wp-content/uploads/2015/10/The-Users-Guide-to-Hologram-Stamping-US.pdf)

Texture and defects:
- Textured stock coverage: [aura-print textured paper guide](https://aura-print.com/uk/textured-paper-foil-printing-guide), [howinteractivedesign](https://www.howinteractivedesign.com/resources-education/production/howd-they-do-that-foil-stamping), [carlsoncraft](https://blog.carlsoncraft.com/?p=171480), [papierdirekt / Foilco](https://blog.papierdirekt.de/en/finishing/)
- Fill-in, edges, pinholing: [Kluge typesetting tips](https://www.kluge.biz/tips/press-tip-typesetting-tips-for-designing-with-foil-update/), [ciofficial 9 issues](https://ciofficial.com/blogs/handcrafters-hub/9-common-hot-stamping-issues-and-their-solutions-the-expert-guide-to-perfect-foil-printing), [Label & Narrow Web foil challenges](https://www.labelandnarrowweb.com/issues/2008-03/view_technologies/foil-challenges--solutions/)
- Die textures: [Hinderer + Mühlich textures](https://hinderer-muehlich.com/en/stamping-tools-top-quality-products-for-the-graphics-industry/stamping-dies-counter-dies-set-up-systems-make-ready-material/hot-foil-stamping-dies-embossing-dies-cnc-engraved/textures-creating-tactile-and-visual-effects)

Foil types:
- Bright vs matte gold, stamping temperatures: [MyBinding gold foils](https://www.mybinding.com/paper-handling/hot-stamp-foils/shop-by-color/gold.html), [printpeppermint comparison](https://printpeppermint.com/gold-foil-stamping-vs-pantone-metallic-inks-vs-metallic-foil-paper-vs-cold-foil-vs-scodix)
- Kurz product grades (no shade data found): [FINAT Kurz](https://finat.com/news/allrounders-and-specialists-any-case-leonhard-kurz-presents)

Optical data and shading:
- Gold n,k (Johnson & Christy 1972): [refractiveindex.info Au/Johnson](https://refractiveindex.info/database/data/main/Au/nk/Johnson.yml)
- Blender Metallic BSDF (F82 gold preset, physical conductor, multiscatter note): [manual 4.3 ja](https://docs.blender.org/manual/ja/4.3/render/shader_nodes/shader/metallic.html), [manual 5.2](https://docs.blender.org/manual/en/5.2/render/shader_nodes/shader/metallic.html)
- Principled Coat Tint and IOR, Specular Tint for metals, Anisotropic, Thin Film: [Blender manual, Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html)
- Metal colours: [physicallybased.info](https://physicallybased.info/)

Photographing foil:
- Foil reflects what it sees; needs a large bright panel or gradient; flags for darks: [talkphotography foil thread](https://www.talkphotography.co.uk/threads/product-photography-glass-item-with-metallic-gold-foil.671537/), [uniquephoto gold-label Q&A](https://www.uniquephoto.com/community/qa/how-can-i-light-a-wine-bottle-with-a-reflective-gold-label-so-the-text-stays-readable), [Matt Hughes, how to photograph foil](https://matthughesphoto.com/h-photography/how-to-photograph-foil.html), [broncolor glossy bottles](https://broncolor.swiss/news/how-to-photograph-a-glossy-object-bottles)

From memory, not verified: how Cycles applies Coat Tint (once, depth 1/cosθ_t); AgX desaturating highlights; my estimates of die-line pitch and weave pitch; all µm and mm values marked [A].
