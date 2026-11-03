# C. Paper, Print and Label-on-Glass Study (v005)

Scope: the navy uncoated wrap label (LBL-FRONT-01), the neck collar and flag (LBL-NECK-01), and their cut edges. Code under review: `mat_label()`, `mat_cut_edge()`, `finish_label()` and `build_collar()` in `build_avante_master.py` (lines 310-371 and 575-646), plus `research/agent3_paper_print.md`.

Tags: **[S]** means sourced, with the URL given. **[M]** means from memory or trade knowledge, not verified this session. **[R]** means observed in a client reference. **[O]** means observed in our v004 renders. **[E]** means my estimate, measured by eye from the reference pixels (label scale assumed to be about 10 px/mm in each ref).

---

## 1. Label stocks

### 1.1 Sourced facts
- **Felt-marked wet-strength wine facestock.** Avery Dennison AE294 is described as "white uncoated matt woodfree printing paper with felt-marked finish, wet strength and fungicidal treatments". It runs on a supercalendered glassine liner with a general-purpose permanent acrylic adhesive. The sheet says that, because of the "open and textured nature of the face material", the best print results come from flexo and offset. **[S]** [AE294 PDS](https://www.pds.averydennison.com/content/PDS/AE294)
- **Calipers.**
  - Tintoretto Black Pepper and Tintoretto Gesso (Fedrigoni/Arconvert felt-type): face 95 gsm, **135 µm**. Liner CB80: 78 gsm, 67 µm. **[S]** (Arconvert datasheet via search; [Spicers Gesso](https://www.spicers.com.au/manter-tintoretto-gesso-ultra))
  - HP Indigo Tintoretto Gesso: face 85 gsm, 92 µm. **[S]** [paper.co.uk](https://www.paper.co.uk/products/hp-indigo/adhoc-tintoretto-gesso/)
  - Yenom WS Ivory: 90 gsm, 126 µm. **[S]** [Ball & Doggett PDF](https://products.ballanddoggett.com.au/content/uploads/2018/05/BD_Roll-Solution_Yenom_WS-Ivory-WL01-WG62_2W01W1D51.pdf)
  - HERMAmatt W: 90 gsm, about 86 µm. **[S]** [HERMA 325](https://www.herma.com/material/product-details/325)
  - Wausau 100% cotton WS: 165 µm. **[S]** (search result)
  - Martelé WS: 100 gsm, 125 µm. **[S]** (agent3 sources)
- **Pulp-dyed (coloured-core) stocks exist for exactly this reason.** Fedrigoni's black range is pulp-dyed "to ensure a seamless and elegant finish". Tintoretto Black Pepper gives a "uniform finish without white edges". Pulp colour avoids "the unsightly white backside and edges". **[S]** [Labels&Labeling](https://www.labelsandlabeling.com/news/substrates-adhesives/fedrigoni-introduces-exclusive-black-paper-range) (403 on fetch; quoted from search summary)
- **Blue wine stocks.** Sirio Color is a pulp-dyed uncoated range and is available self-adhesive. Arconvert Ispira **Blue** Saggezza Ultra WS is a blue wine stock "with a special soft surface finish". **[S]** (Fedrigoni search results, see [Fedrigoni self-adhesives](https://selfadhesives.fedrigoni.com/?p=308))
- **Laid paper.** Laid lines run about **1 mm apart (≈10 per cm)**. Chain lines run **25-35 mm apart**, parallel to the machine direction. **[S]** [marcmus glossary](https://marcmus.fcsh.unl.pt/glossary), [Malta Map Society](https://maltamapsociety.mt/glossary/laid-lines/)
- **Textured ranges.** UPM Raflatac sells textured wine faces: Fleur de Coton, the "thick" Velmart, and Rêverie "Drops", which has an "accentuated uneven" surface. No caliper was published. **[S]** [Labels&Labeling](https://www.labelsandlabeling.com/news/new-products/upm-raflatac-unveils-three-wine-facestocks), [Label&NarrowWeb](https://www.labelandnarrowweb.com/breaking-news/upm-raflatac-adds-new-products-to-wine-and-spirits-portfolio/)

**Not found:** no mill publishes felt, hammer or linen relief depth or pitch in mm. All the feature sizes below are **[E]** from the refs, or **[M]**.

### 1.2 Texture feature sizes for modelling

| Texture | Ref | Feature size (lateral) | Relief p-p | Character |
|---|---|---|---|---|
| Felt-marked (wine felt) | ref02, ref12 | pecks 0.4-0.8 mm; fibre streaks 0.1-0.2 mm wide × 1-3 mm long | 20-40 µm [M/E] | irregular pecked cells plus directional fibre streaks |
| Laid | (none in refs) | laid lines 1.0 mm; chain lines 25 mm [S] | 10-20 µm [M] | strictly linear ribs |
| Linen/canvas emboss | ref08 | weave pitch 0.6-0.9 mm, two crossing directions [E] | 30-60 µm [M] | crosshatch; reads mainly through sheen |
| Hammered | ref01 | cells 0.8-1.5 mm, rounded dimples [E] | 30-60 µm [M] | soft dimples, larger than felt |
| Cotton (thick, letterpress) | ref03 | soft fuzz 0.3-0.5 mm, no regular cell [E] | 15-30 µm; caliper 300-600 µm for letterpress board [M] | velvety-matte but still paper; deep deboss |
| Pebble | ref11 | 1-2 mm rounded pebbles [E] | 50-80 µm [M] | visible almost only as specular on the pebble tops |
| Smooth uncoated / smooth-matte | ref07, ref09 | grain under 0.2 mm, near invisible | under 10 µm | broad soft sheen gradient |
| Natural or flecked | ref13 | flecks and fibres 0.2-0.5 mm [E] | 10-20 µm | albedo variation dominates over relief |
| Deckle / torn edge | ref05 | edge wander amplitude 0.5-2 mm, wavelength 2-6 mm; fibre fringe 0.1-0.3 mm [E] | n/a | white fibrous fringe |

At the render scales:
- **Hero** is about 0.12 mm/px, so 0.6 mm felt is about 5 px and reads as tonal grain.
- **Macro** is 0.043 mm/px, so 0.6 mm felt is about 14 px and must read as structure, not noise.

### 1.3 Edge colour for a navy label: dyed-through versus printed flood
- **Printed flood on white or cream stock.** The die cuts through ink and paper, so the edge shows a **white or cream core** with a 5-15 µm navy skin on top. Ink penetration depth is [M]. Cream also shows in every knocked-out letter. At macro this reads as a bright hairline, which is the "cheap label" tell that pulp-dyed stocks are sold to avoid [S].
- **Pulp-dyed navy stock.** Text would be printed in opaque cream or white ink, or foiled. The **edge is navy**, slightly lighter and greyer than the inked face because the fibres are unprinted and rough.
- **Our art is ambiguous.** `mat_label` treats cream as bare paper, which implies a printed flood. `mat_cut_edge` is cream (0.90, 0.88, 0.82) and `back_white` is cream.
- **Recommendation:** decide once. For a premium navy brandy, **use pulp-dyed navy** (like Sirio Color or Ispira Blue): navy edge, navy reverse, cream text as ink. Keep the cream edge only if the client explicitly wants a printed flood.

---

## 2. Ink on uncoated stock

### 2.1 Sourced facts
- On uncoated stock, solid densities are typically **0.30-0.40 lower** than on coated, with a reduced gamut. An OD of about 1.0 is acceptable on uncoated; above 1.10 is hard to reach. **[S]** [PIA](https://www.printing.org/content/2018/09/13/a-new-customer-is-insisting-we-print-his-process-brochures-on-uncoated-paper-what-do-we)
- One study argues that coated stock looks richer mainly because of **surface light scatter**, not absorption. In other words, the paper's rough first-surface reflection lifts and desaturates dark solids. **[S]** (2021 study, via search)
- On uncoated, ink wicks into fibre: dots spread and solids print lighter. **[S]** [4over4](https://v2.4over4.com/guide/matte-vs-uncoated-paper)
- Mottle is non-uniform density in solids, caused by non-uniform absorbency. **[S]** [BioRes review](https://bioresources.cnr.ncsu.edu/wp-content/uploads/2021/06/BioRes_16_3_6426_Review_Lee_YHC_Backtrap_Mottle_Mechanisms_18684.pdf)
- Earlier agent3 source: solids on uncoated rarely show strong mottle. Edges are inhomogeneous, with larger optical dot gain. **[S]** (agent3 links)

### 2.2 What this means visually [M]
- **Dark flood.** The ink fills the valleys and partly levels the relief, so felt still shows, but at about 60-80% strength. Albedo variation is low: mottle is cloudy at **3-10 mm** and small, about ΔL\* 1-2. The texture shows **mostly through specular sheen** under a raking key, not through colour variation. Tops of the pecks catch a soft, greyish sheen, and valleys stay saturated.
- **Lighter ink or knock-out text.**
  - Knock-out (bare paper) letters keep the full paper texture and fibres.
  - Opaque light ink on dark stock shows the texture through it. Fibre valleys look slightly darker or under-covered, and edges are slightly ragged (15-40 µm) from spread along fibres.
  - Neither is vector-crisp at macro.

### 2.3 Reference observations [R]
- **ref07** (green smooth matte): broad soft sheen gradient across the oval, near-zero fine mottle, very fine grain. The perimeter shows no white edge, so it is dyed or flood-bled; edges darken slightly.
- **ref08** (dark green linen): texture is almost entirely sheen. Lit weave tops are pale green-grey and recesses stay deep green. The white script "Asti" sits on the texture, which breaks its edge slightly.
- **ref04** (burgundy uncoated): fine fibrous speckle, matte, soft highlight with no hot spot.
- **ref11** (black pebble): matte black body. Texture reads only as specular pips on the pebble tops.
- **ref02** (cream felt): horizontal fibre streaks. The blue ink text ("COCKTAIL") clearly shows paper grain inside the letters. Ink is broken by the valleys.
- **ref13** (natural stock): teal illustration ink is broken by fibre flecks, and the flecks are darker than the paper.
- **ref10** (dark grey): the fingerprint pattern is a printed or varnish graphic, not paper texture. Underneath, the stock grain is soft and fine.

---

## 3. Label on glass

### 3.1 Sourced facts
- Pressure-sensitive wine laminate: face 92-135 µm, an acrylic or rubber adhesive layer, glassine liner 54-67 µm (removed). **[S]** (AE294, Arconvert CB80, B&D)
- **Neck labels and "winging".** Paper has a "memory effect" and tends to return flat. "The smaller the diameter of the bottle neck, the higher the memory effect risk." Overlap zones and heavy 3D varnish add stiffness. Lift force "is greatest at the label edge". Condensation and dust cause later lifting. **[S]** [Avery Dennison Neck Label Technical Guide 2023](https://label.averydennison.com/content/dam/averydennison/lpm-responsive/europe/english/documents/customer-tools/ad-lpm-eu-technicalguide-necklabelapplication-2023-web.pdf)
- A standard pressure-sensitive label can't follow compound curves. Darts, pleats and edge lift form at the perimeter. **[S]** [US8551270](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8551270)
- Glass sinks and bulges cause bubbling and wrinkles. **[S]** [Spicers application guide](https://www.spicers.com.au/application-guide)

### 3.2 Behaviour to model [M unless noted]
- **Adhesive thickness:** about 15-25 µm. The stack on glass is face plus adhesive, so **0.11-0.16 mm**. For a 135 µm felt stock, use **0.15 mm**.
- **Edges sit tight on developable surfaces.** Our flat panels and the cylinder of the chamfered corners are developable. A well-applied label shows **no gap**, just a 0.15 mm step. Under a key that rakes across the edge, that step reads as a 1-3 px light line on the lit side and a thin dark line on the shadow side.
- **Tapered shoulders and compound curves** cause darts or lift. Our die stops below the shoulder, so no wrinkles are needed on the wrap. A **neck collar** on a small-diameter neck with an overlap is the place for slight end lift: 0.05-0.2 mm at the free end.
- **Seen from behind through clear glass:**
  - You see the label **reverse through the adhesive**. The adhesive optically couples paper to glass (n ≈ 1.47 versus 1.5), so there is **no mirror-like air interface**.
  - The reverse looks like paper that has been wetted: about 10-20% darker, slightly more saturated, texture-free, and with no specular of its own.
  - Its colour is the stock colour: navy if pulp-dyed, white or cream if printed.
  - Behind brandy, it takes on the liquid's amber transmittance and refraction distortion.
  - The liner is gone. You never see "white liner".
- **Bubbles and air pockets** (silvery patches) are a defect. Don't add them to a hero shot.

### 3.3 Reference observations [R]
- **ref09:** die-cut cream label on clear glass. A **bright edge line** shows along the notch, and a soft dark contact line shows on the glass next to it.
- **ref03:** the bottom label edge shows a **light thickness line plus a subtle shadow**, which is how a thick stock reads.
- **ref12:** the cross-shaped die shows thickness as a crisp highlight on the lit edges, with a soft shadow on the glass behind.
- **ref07:** the oval sits flush on dark glass, with a hairline darkening at the perimeter and a faint lighter rim on the lit side.

---

## 4. Die-cut edges
- **Clean steel-rule or rotary die [M].**
  - The top face corner is slightly **rolled and compressed**: radius about 20-40 µm, so the edge catches a highlight.
  - The cut wall is fibrous and matte (roughness about 0.95). It is lighter than the inked face when printed on cream, and the same hue but lighter when pulp-dyed.
  - Fibre fuzz is 10-50 µm, which is sub-pixel even at macro (43 µm/px). Model it as edge-colour noise, not geometry.
- **Deckle or torn (ref05) [R/E].** Irregular outline with 0.5-2 mm wander, plus a 0.1-0.3 mm white fibrous fringe where the coloured surface layer tears back to the white core. In ref05 this is on the flag end only, which is a nice premium cue for our neck flag if the client wants it.
- **Laser cut [S, forum].** Gives slightly browned edges. Not relevant here.

---

## 5. Our v004 against reality

Measurements were taken from the PNGs with sips and a BMP crop on 0-255 sRGB values.

| Item | v004 observation [O] | Real behaviour | Verdict |
|---|---|---|---|
| Paper read overall | Front reads as fine **suede or flannel**. In the hero and three-quarter views, the side panels go **pale grey-blue and fuzzy**. In the foil macro, front flood mean is RGB (30, 49, 65), L 46, but the side panel at grazing is **(112, 119, 126), L 118**: 2.5× brighter and nearly desaturated | Uncoated navy at grazing gets a little lighter and greyer from first-surface scatter, but stays clearly navy. Compare ref04 sides and ref07 perimeter | **Reads velvet or plastic flocking.** Caused by `Sheen Weight 0.08` plus the default `Specular IOR Level 0.5` at roughness 0.52-0.78 |
| Texture scale | Uniform isotropic speckle about 0.3-0.7 mm. No pecks, no streaks, no structure under raking light | Felt pecks 0.4-0.8 mm with directional fibres | Wrong character |
| Texture strength | Relief = 4.5e-5 × noise. That is roughly ±9 µm over about 0.6 mm blobs, a slope of about 1-2°, which is invisible as shading | 20-40 µm p-p, so slopes about 4-8° | **Too weak.** What you see is mostly the colour mottle, not relief |
| Fibre axis | `noise(nt, 1, 2, (4000, 800, 4000))` in **Object** space. The long axis is **Y**, which is the depth axis pointing into the front panel | Fibres lie in the sheet plane along the machine direction | **Bug.** On the front panel (XZ plane) fibres are isotropic 0.25 mm dots. On the side panels they run horizontally. Inconsistent |
| Flood mottle | `BrightContrast.Bright = (n − 0.5) × 0.06` at noise scale 1500/m (about 0.67 mm). This is **additive** on dark linear values (navy G ≈ 0.03), so ±0.01 is about **±30% relative** at fine scale. Measured flood sd L = **1.9/255** at L 42-46 (about ±4-5% in sRGB) as fine speckle | Mottle is cloudy at 3-10 mm and about ±2-3% linear. Fine grain comes from the relief, not albedo | Wrong scale and wrong operator. It is what creates the "suede" look |
| Text crispness | Cream secondary text (V.S.O.P, CAPE BRANDY, BOTTLED…) is vector-sharp and flat, with no paper grain inside the letters | Knock-out letters carry full felt texture. Edges are slightly ragged (15-40 µm) from ink spread | Too digital at macro, fine at hero |
| Bird/spear tone graphic | Saturated steel blue, hard-edged, reads like a translucent screen overlay | Tone-on-tone on uncoated paper is either a lighter ink (slight mottle, matte, ΔL\* 5-10) or a varnish that shows only in specular | Too much colour contrast and too clean |
| Wrap edges | No visible thickness, highlight or contact line. The top arch meets the brandy like a decal | A 0.15 mm step shows a 1-3 px light line at macro, plus a dark contact hairline (ref09, ref03, ref12) | **Missing.** Thickness is 0.10 mm (2.3 px at macro) and the label floats 0.03 mm off the glass |
| Air gap | `surf_xyz(u, v, 0.03)`: 30 µm air between label back and glass | Adhesive couples optically, so there is no glass/air interface under the label | Creates a Fresnel/TIR reflection at the rear glass when the reverse is seen through the bottle |
| Label reverse | `back_white`: cream (0.86, 0.83, 0.76), roughness 0.85, chosen by sign of dot(Position, Normal) | Stock colour, wetted-dark, no specular | Fragile test (depends on object origin). Colour depends on the stock decision |
| Collar flag | Razor-thin flat panel. No ply step, root bend or edge core. Only a faint rim on the rounded end. Plies are a perfect register | Two plies back-to-back, about 0.3 mm total. Root bend radius 0.3-1 mm, ply misregister 0.1-0.3 mm, slight curl (memory effect [S]) | Reads as card or plastic |
| Collar on neck | Clean. The bottom edge shows a hairline only | Fine | OK |

---

## 6. Blender recipe (Cycles 5.1)

All of these values are **[E/M] artistic starting points** derived from the facts above.

### 6.1 Coordinates
Drive the paper texture from **UV in millimetres**, not Object space, so that fibre direction follows the sheet:
- Wrap: `UV → Mapping(scale = (243.469, 101.258, 1))`, using `WRAP_ART` w and h. After this, 1 unit = 1 mm.
- Collar: `scale = (COLLAR_ART_W, COLLAR_ART_H, 1)`.
- Noise "Scale" then equals 1 / feature_mm.
- Machine direction runs horizontally, around the bottle. Roll-fed wrap labels usually dispense along the web direction [M].

### 6.2 Height field (in mm)
1. **Felt pecks.** Voronoi F1, Smooth F1 (smoothness 0.7), scale **1.6** (about 0.6 mm cells), randomness 1.0. Feed it a Vector distorted by Noise (scale 0.8, strength 0.12). Pass through a ColorRamp from 0.15 to 0.85, then × **0.030 mm**.
2. **Felt body.** Noise, scale **3.0**, detail 3, roughness 0.55, × **0.010 mm**.
3. **Fibres.** Noise on a Mapping scale of (**0.5, 6.0, 1**). This gives streaks about 2 mm long and 0.17 mm wide along U. Use detail 1, ColorRamp 0.55-0.75 (sparse), × **0.006 mm**.
4. **Ink levelling.** Height × (0.75 in flood, 1.0 in knock-out or bare paper).
5. **Bump node:** Strength 1.0, **Distance 0.001** (to convert mm to m), Height = the sum. Target RMS slope is about 5°. Check it with a raking-key render at 15-25° grazing: pecks should show as soft tonal structure at macro, and as fine grain only at hero.

### 6.3 Colour
- **Flood mottle.** Multiply Base Color by `1 + 0.03 × (Noise(scale 0.15, detail 2) − 0.5) × 2`, which gives about 6 mm cloudy variation at ±3% **linear**.
- **Fibre albedo.** Multiply by `1 − 0.04 × fibre_mask`. Ink pools slightly darker in streak valleys.
- **Remove** the additive BrightContrast node.
- **Knock-out or cream areas.** `cream × (1 − 0.05 × felt_valley)`, so valleys are slightly greyer. Add an **edge raggedness** pass: offset the artwork UV by Noise(scale 25, i.e. 0.04 mm) × 0.02 mm before sampling the colour image. This roughens type edges by about 20 µm, so letters lose their vector edge at macro and stay sharp at hero.
- **Tone graphic (bird/spear).** Cut its contrast to about ΔL\* 6-8 against the flood, apply the same mottle, and give it roughness 0.62. Alternative: render it as a matte or gloss varnish only, with Coat Weight 0.3 and Coat Roughness 0.25, so it reads in the specular.

### 6.4 Surface response (Principled)

| Region | Roughness | Specular IOR Level | Sheen | Coat | Notes |
|---|---|---|---|---|---|
| Ink flood (navy) | **0.66** ± 0.04 (noise follows the felt tops, smoother on peaks) | **0.35** | **0** | 0 | Sheen is what turns it into velvet. Remove it |
| Bare paper / knock-out | **0.85** | 0.30 | 0 (or ≤ 0.03, roughness 0.7) | 0 | |
| Cut edge wall | 0.95 | 0.25 | 0 | 0 | |
| UV spot varnish (existing mask) | n/a | n/a | n/a | Coat 1.0 × mask, roughness 0.12-0.2, IOR 1.5 | 0.08 coat roughness is very glassy. 0.15 looks like screen-printed UV |

Keep multiscatter GGX. After the change, re-measure the side-panel/front luminance ratio in the foil macro. **Target:** at most 1.6× and still clearly navy, around RGB (55, 70, 88), not grey.

### 6.5 Translucency or SSS
- Navy flood or pulp-dyed navy: **none**. Opacity is effectively 100%.
- Cream knock-out areas, if the stock is printed: Subsurface Weight 0.15, Random Walk, radius (1, 0.9, 0.8) × **Scale 0.00015** (0.15 mm). This softens type edges physically. Optional.
- No Transmission anywhere.

### 6.6 Edge geometry
- `LABEL_T` goes from **0.10 to 0.15 mm**.
- Solidify: keep `offset = 1.0` so the back face sits at the glass. Move `surf_xyz(u, v, 0.03)` to **0.005 mm**, which is enough to avoid z-fighting and too small to give a visible air interface.
- **Rim bevel.** After Solidify, add a Bevel modifier limited by angle (60°): width **0.025 mm**, 2 segments, `harden_normals` off, so the top corner catches a highlight. If dicing cost is a concern, do it on the outer rim loop only via a vertex group.
- **Rim material**, depending on the stock decision:
  - **Pulp-dyed (recommended):** navy at 1.15× the flood linear value and 0.85× saturation, roughness 0.95, plus Noise(scale 40/mm) albedo ±8% for fibre fuzz.
  - **Printed flood:** cream (0.80, 0.77, 0.70), with a top 10% band of the rim in navy (ink skin). Use a gradient on the rim's local normal axis, or a Geometry > Position-based mask.
- **Contact.** Let Cycles produce the contact line naturally from the 0.15 mm step and raking light. No fake AO.

### 6.7 Reverse through glass
- Replace the `dot(Position, Normal)` test with **Geometry > Backfacing**, or put a dedicated material slot on the Solidify inner shell (`material_offset = 2`).
- Reverse material:
  - Pulp-dyed: navy × 0.85.
  - Printed: cream × 0.85.
  - In both cases: roughness 1.0, Specular IOR Level 0, so the adhesive-coupled face shows no specular.
- Decision: show the rear panel reverse through the brandy. It should read as a dim, amber-tinted shape with soft edges.

### 6.8 Collar flag
- Separate the plies by **0.02 mm** of adhesive, and give each ply 0.15 mm, for a total of about 0.32 mm.
- Misregister the back ply by **0.15 mm** at the rounded end, so a step shows.
- At the root, replace the sharp crease with a **0.5 mm radius** fold.
- Add flag curl: bend the free end 2-4° away from the glass about the vertical axis, plus a low-frequency 0.05-0.1 mm warp (memory effect [S]).
- The rim material is the same as the wrap.
- Optional premium cue from ref05: a **deckle edge** on the flag's free end only, with 0.5-1.5 mm wander at a 3-5 mm wavelength. Model it with a displaced outline in `stadium_sdf`, plus a white fibre fringe band 0.15 mm wide in the rim material.

---

## 7. Gaps ranked by visual impact

1. **Paper reads as suede or velvet. This affects every shot.**
   - Fix: Sheen → 0, Specular IOR Level → 0.30-0.35, ink roughness → 0.66 ± 0.04, and remove the additive fine mottle.
   - Check: side panel stays navy, with grazing luminance at most 1.6× the front.
2. **Felt relief is too weak and the wrong shape, and the fibre axis bug.**
   - Fix: UV-in-mm coordinates; Voronoi pecks 0.6 mm at 30 µm, body noise 10 µm, fibre streaks along U at 6 µm; Bump Distance 0.001.
   - Check: a raking-light macro shows peck structure, like ref02 and ref12.
3. **Flood mottle uses the wrong scale and operator.**
   - Fix: replace it with multiplicative ±3% at about 6 mm, plus fibre-valley darkening. The fine grain should come from the relief.
4. **Edges are invisible, the label floats, and it is too thin.**
   - Fix: `LABEL_T` 0.15 mm, offset 0.005 mm, a 0.025 mm rim bevel, and a decided rim colour.
   - Check: the foil macro top arch shows a 2-4 px lit edge line, as in ref09 and ref03.
5. **Stock identity is undecided** (cream edge and reverse against navy face).
   - Fix: choose pulp-dyed navy (premium, no white edges [S]) and update `mat_cut_edge` and the reverse to match.
6. **The tone-on-tone bird graphic looks digital.**
   - Fix: lower its contrast and add mottle, or move it into varnish-only Coat.
7. **Knock-out text is vector-crisp and texture-free at macro.**
   - Fix: a UV jitter of about 20 µm on the artwork lookup, keeping the full felt bump in bare areas (already wired, it just needs the stronger relief), and optional SSS 0.15 mm.
8. **The collar flag reads as plastic card.**
   - Fix: ply thickness and misregister, a 0.5 mm root radius, slight curl, rim material. Deckle end is optional.
9. **The label reverse through the glass** (air-gap reflection, fragile backface test).
   - Fix: 0.005 mm gap, a Backfacing-driven reverse at stock colour × 0.85 with no specular.
10. **UV varnish coat roughness 0.08 is too glassy for screen UV on uncoated.**
    - Fix: 0.12-0.2.

## Sources
- Avery Dennison AE294 PDS: https://www.pds.averydennison.com/content/PDS/AE294
- Avery Dennison Neck Label Application Technical Guide 2023: https://label.averydennison.com/content/dam/averydennison/lpm-responsive/europe/english/documents/customer-tools/ad-lpm-eu-technicalguide-necklabelapplication-2023-web.pdf
- Fedrigoni black pulp-dyed range: https://www.labelsandlabeling.com/news/substrates-adhesives/fedrigoni-introduces-exclusive-black-paper-range
- Spicers Manter Tintoretto Gesso / Black Pepper: https://www.spicers.com.au/manter-tintoretto-gesso-ultra , https://www.spicers.com.au/manter-tintoretto-black-pepper-ultra
- Paper.co.uk Tintoretto Gesso (Indigo): https://www.paper.co.uk/products/hp-indigo/adhoc-tintoretto-gesso/
- Ball & Doggett Yenom WS Ivory: https://products.ballanddoggett.com.au/content/uploads/2018/05/BD_Roll-Solution_Yenom_WS-Ivory-WL01-WG62_2W01W1D51.pdf
- HERMAmatt W: https://www.herma.com/material/product-details/325
- Fedrigoni self-adhesives (Sirio/Materica/Ispira): https://selfadhesives.fedrigoni.com/?p=308
- UPM Raflatac wine faces: https://www.labelsandlabeling.com/news/new-products/upm-raflatac-unveils-three-wine-facestocks
- Laid/chain lines: https://marcmus.fcsh.unl.pt/glossary , https://maltamapsociety.mt/glossary/laid-lines/
- PIA, uncoated densities: https://www.printing.org/content/2018/09/13/a-new-customer-is-insisting-we-print-his-process-brochures-on-uncoated-paper-what-do-we
- 4over4, matte versus uncoated: https://v2.4over4.com/guide/matte-vs-uncoated-paper
- Mottle review (BioResources): https://bioresources.cnr.ncsu.edu/wp-content/uploads/2021/06/BioRes_16_3_6426_Review_Lee_YHC_Backtrap_Mottle_Mechanisms_18684.pdf
- Pressure-sensitive label on compound curves: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8551270
- Spicers application guide: https://www.spicers.com.au/application-guide
