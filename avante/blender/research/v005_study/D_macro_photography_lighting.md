# D. Macro photography and lighting study for v005

Scope: a read-only study. I studied ref01–ref13, the v004 renders (hero, three-quarter, foil, roundel and collar-flag macros, plus QC liquid and neck), `build_avante_master.py` (lines 266–355 and 680–795), `research/agent6_lighting.md` and `research/agent2_liquid_optics.md`. No files were changed.

Tags used throughout:
- **[S]** sourced fact, URL given.
- **[M]** memory-based or general craft knowledge, not verified this session.
- **[O]** my own observation of the reference or render pixels.
- **[D]** derived by me from scene numbers or geometry. These are reasoning, not measurements.
- **[R]** recommendation.

Scene units: 1 BU = 1 m. The bottle axis is at the origin and the label faces −Y. Targets used in code: wordmark z = 0.137, roundel z = 0.042, collar z = 0.2075.

---

## 0. Sourced facts (research)

| # | Fact | Source |
|---|---|---|
| S1 | Whether a direct (mirror) reflection appears depends only on where the source sits relative to the camera and the surface, a range the authors call the "family of angles". For metal, the lighting approach "is determined by the family of angles and, therefore, by the shape of the metal". The method is to put a white target where you expect the family of angles to be. | Hunter, Biver, Fuqua, *Light: Science & Magic*, ch. 6 (Metal), contents and excerpts: https://www.oreilly.com/library/view/light-science/9781000342673/chapter-65.html , https://studiography.blogspot.ca/2010/09/family-of-angles.html |
| S2 | Gold-foil labels: put small black flags or gobos close to the bottle, just out of frame, so light does not hit the lettering directly. This darkens the reflections in the foil and makes the text read. Raise the softboxes and angle them to the side so the reflections fall above or below the text. Use a longer lens from farther back. | https://www.uniquephoto.com/community/qa/how-can-i-light-a-wine-bottle-with-a-reflective-gold-label-so-the-text-stays-readable |
| S3 | A flash can make gold foil "look black". Foil reads bright only when a source sits in its mirror direction; otherwise it reflects the dark room. | https://www.talkphotography.co.uk/threads/product-photography-glass-item-with-metallic-gold-foil.671537/ |
| S4 | Broncolor bottle set: one 60×100 cm softbox as a long contour light, an acrylic sheet for a gradient that gives roundness, a black paper flag separating the contour from the gradient, white cards to fill the label, black background about 2 m behind, 150 mm medium-format lens ("long focal lengths keep lights close to glossy objects"), f/22. | https://broncolor.swiss/news/how-to-photograph-a-glossy-object-bottles |
| S5 | A linear gradient comes from a strip or softbox aimed at a diffusion sheet about 20–30 cm away. The angle and the distance of the box edge set the gradient length and how sharp its cut-off is. Black card between the box and the diffuser turns a softbox into a strip. | Summary of the PetaPixel article (direct fetch returned 403): https://petapixel.com/how-to-create-gradients-of-light-product-photography/ |
| S6 | Edge-line gradients: a light with a 7" reflector behind the rear edge, wrapped in Rosco 3008 diffusion, so the light wraps and fades toward the front. Moving the source or card nearer or farther changes the gradient's width and intensity. | https://proedu.com/blogs/news/creating-smooth-gradients-and-edge-lines |
| S7 | Liquid glow: a card cut to the bottle shape, slightly smaller than the silhouette so it stays hidden, white or foil-faced, placed behind the bottle. For whisky, glossy gold or silver card "small enough to hide" behind the bottle, cut "to be invisible but maximise the gold glow refracting back through the whisky". | https://www.diyphotography.net/?p=288204 , https://karltayloreducation.com/class/whisky-product-shoot/comment-page-2/ , https://visualeducation.com/add-glow-to-bottle-products/ |
| S8 | Blender light linking: a light or emissive mesh gets a receiver collection (include or exclude) and a blocker collection (shadow linking). Light linking of emissive meshes is Cycles only. Shadow linking can be slower. Sampling is most efficient with the light tree on. | https://docs.blender.org/manual/en/dev/render/lights/light_linking.html , https://docs.blender.org/manual/en/4.3/render/lights/light_linking.html |
| S9 | AgX has seven contrast looks (Very Low … Very High Contrast) that work in AgX Log with a 0.18 pivot, plus Punchy. The current Punchy darkens the image. | https://projects.blender.org/blender/blender/pulls/106355 , https://blenderartists.org/t/dealing-with-aces-agx-srgb/1480752/542 . The exact 5.1 look names are **[M]**: check them in the 5.1 UI. |

Memory-based craft facts, unverified:
- **[M]** Hot-stamp foil is a vacuum-metallised aluminium layer under a tinted lacquer. It is close to a mirror (roughness about 0.02–0.08), and its colour comes from the lacquer. "Champagne/matte gold" foils exist, but a bright gold stamp reads by its clipped highlights plus near-black reflections.
- **[M]** Gold F0 (linear) is about (1.00, 0.71, 0.29) (physicallybased.info).
- **[M]** Packshot photographers routinely shoot labels at f/16–f/32 or focus-stack. CGI label close-ups mimic a shallow DOF for "editorial" feel, keeping the focus plane on the hero word.

---

## 1. Reference reverse-engineering [O]

Key directions are given as seen from the camera. The source shape is inferred from the shape of the highlight on the foil and glass. A source's apparent angular size is roughly the width of the highlight band divided by the foil's curvature.

| Ref | Subject | Key and specular source | Fill and flags | Liquid and backlight | Background | Lens feel and DOF | Crop and angle | Tone |
|---|---|---|---|---|---|---|---|---|
| 01 Camikara (CGI) | cream textured label, gold foil, deboss | Large soft source upper-left, near the foil's mirror direction, with a **gradient**: foil goes white-gold to amber to **black** inside one letter (the barrel and ribbons). The paper texture is raked from upper-left at about 70–80°, so the pebble shading is strong. | Low fill. A black environment fills the foil's lower mirror cone, so the off-angle ribbons are black. | Hot orange glow at the top right through the shoulder and at the bottom left: a warm backlight card behind, visible only through the liquid. | Pure black | About 100–135 mm. Medium DOF: the text plane is sharp and the far right edge softens slightly. | Bottle rolled about 35° CCW, label filling the frame, slight yaw so the curvature carries the right side away | High contrast, deep blacks, foil highlights clipped |
| 02 Negroni (photo) | copper foil, embossed, linen paper | Soft key from left and slightly behind. Copper shows bright bevel tops with darker counters, so the gradient runs across the emboss. Strong paper texture from raking light. | Moderate fill from the right (paper is evenly bright) | Bokeh glass on the left with warm practical lights | Dark, out-of-focus props | About 90–100 mm, f/4–5.6. The label plane is sharp; the foreground and background fall off fast. | Rolled about 8°. Camera low and close, oblique about 20°. | Medium contrast, warm |
| 03 Devils Tower (CGI) | letterpress deboss on cotton paper, neck art | Key from top-right at near-grazing angle. Every debossed line has a lit wall and a shadow wall, and the paper tooth reads strongly. | Very little fill. Black falloff toward the bottom-left. | Amber body. The glow is a vertical gradient, brighter at centre-left and darker at the edges. | Black | About 100 mm, moderately shallow. The bottom-left and the cylinder edges defocus. | Rolled about 20°. Cylinder curvature gives natural falloff. | Rich, low-key |
| 04 Filliers (photo) | gold foil on red paper, fluted glass, red liquid | Soft, large, high-key overhead source. Foil is bright where it faces up toward the source. | Lots of fill. White room. | Liquid lit by ambient. Fluting makes bright and dark stripes from the environment. | Light grey | About 50–85 mm, f/2.8–4. Very shallow: the top and neck blur. | Low angle looking up, about 30° roll | Low contrast, high-key |
| 05 Gran DOX (CGI) | wood and copper-wire stopper, glass neck, flag tag | Soft key from the right and above (stopper top lit). Small hard specular on the copper wire. | Left side falls into dark teal | Foreground body blurred into an orange glow | Dark teal-to-black gradient | About 50–70 mm feel (strong perspective). Low camera looking up, f/2.8–4 equivalent. The foreground body is heavily defocused. | Worm's-eye view, stopper toward the top-left | Moody, mid contrast |
| 06 Saint Cloud cap (photo) | cast copper cap | Single soft key from upper-left. Crisp lit tops on the knurled ridges, dark grooves. | Almost no fill. Black flags. | Liquid barely visible, dark | Black | About 100 mm macro, f/8–11. The neck glass falls off toward the bottom-right. | High angle looking down on the cap, rolled about 35° | High contrast |
| 07 Monte (CGI or photo) | green label, copper foil, dark glass | Big soft strip/box reflected in the glass as a **sharp-edged diagonal band** (left and right). The foil is lit by a broad source with a gradient: copper to bright. | None. The glass sides are black. | none (dark wine) | Black | About 100 mm, deep DOF | Rolled about 30° | Graphic, high contrast |
| 08 Mondoro (photo) | dark green textured label, gold foil, green glass | Large soft source upper-left, near the mirror direction. The foil glows bright. The label's embossed linen shows through **specular sheen** (the dark paper reads by glints, not by diffuse light). | Low | Green glass reflects a bright window band | Dark | About 100 mm macro, shallow at the edges | Rolled about 30°, very tight | Rich, saturated |
| 09 Botaneg (CGI) | white paper, gold foil seal, emboss, green glass | Soft key from top-left. The seal foil is bright with clear lit and dark sides on the relief. | Gentle fill | Green glass with bright strip reflections | Dark green | About 70–100 mm. **Shallow**: the bottom-left and top fall off. | Oblique about 30°, rolled about 15° | Medium contrast |
| 10 Mark S. Mayne (CGI) | black textured label, silver foil and blind emboss | Source **above** the label, so the embossed letters show bright upper bevels and dark lower bevels. The foil is a silver-to-grey gradient. | None | Amber glow at the top-right corner only | Black | Square-on. Edge vignette and defocus. | Frontal but tight | Low-key |
| 11 Blade & Bow (photo) | black pebbled roundel, gold foil, on liquid | Soft frontal-high source in the mirror direction. The foil is bright gold-white and the pebble texture shows through the sheen. | Moderate | Liquid is an **orange gradient**: darker top-left, bright lower-right. A backlight card sits behind the lower half. | Liquid fills the frame | About 100 mm, nearly frontal (about 10° yaw) | Frontal, slight perspective | Saturated |
| 12 Ol'son (CGI) | white felt paper, green holo-foil, deep deboss | Raking key from the upper-right at about 75°. Brushed foil shows anisotropic streaks, and the deboss walls show lit and dark sides. | Low | Green glass behind with bright reflections | Green glass | About 100 mm, moderate DOF | Rolled about 30°, tight | Crisp, high micro-contrast |
| 13 Stranger & Sons (CGI) | grey felt paper, gold foil emboss | Key from upper-left. Foil letters have bright tops and dark lower-right bevels, and the paper tooth shows strongly. | Low | none | Black corners | About 100 mm, shallow: the bottom-right blurs | Rolled about 20°, oblique | Medium-high contrast |

### Common traits across the references [O]
1. **11 of 13 are tilted** (roll 15–35°) and **oblique** (yaw 15–35°). Only ref10 and ref11 are near-frontal, and both still have strong gradients.
2. **The foil is never one flat tone.** Within one letter it runs from clipped highlight (near white) through gold to dark brown or black. That is a mirror reflecting a **gradient source next to black**.
3. **The paper shows texture because the key rakes** (an estimated 65–85° from the paper normal) or, on dark paper, because of **specular sheen** from a large source near the mirror direction (ref07, ref08, ref10, ref11).
4. **The backgrounds are black or dark** in 10 of 13. The liquid appears as a **gradient glow** (ref01, ref03, ref11), never as a flat orange sheet.
5. **A long-lens feel** (about 85–135 mm) with **shallow-to-moderate DOF**. The focus plane is on the hero word and the far edges fall off.
6. **Contrast is high**: true blacks, clipped specular highlights, mid-tones placed low.

---

## 2. Principles that make foil, emboss and texture read

1. **Foil is a mirror. Light it with what it reflects, not with what illuminates it [S1, S3].** The brightness of a pixel on the foil equals the radiance of whatever sits in its mirror direction, times F0. So the designer's job is to place a **bright source in the mirror cone** of the hero letters, and **black everywhere else** in that cone.
2. **Size the source to the relief.** Emboss and paper relief tilt the foil normals by about ±δ. That spreads the reflected rays over about ±2δ.
   - For a 0.2 mm emboss with about 0.3 mm bevels, δ is about 15–30°.
   - For the paper tooth, δ is about 3–8°.
   - **[D]** If the source subtends more than 4δ (about 60°+), every facet sees light and the foil goes **uniform and flat**. If it subtends about 20–35° and its **edge** crosses the mirror direction, facets split into bright and dark, and the letters show modelling.
3. **Put a gradient on the source [S4, S5, S6].** A linear ramp from black to peak across the source turns the facet angle into tone. You get highlight roll-off on bevels instead of a binary on/off. Use a hard edge on one side for a crisp "sweep" (agent6 A5 already proposed this).
4. **Use a dark environment and black flags [S2, S4].** These give the off-angle foil and the lower bevels something black to reflect. The world and the sweep must reflect at about 0.002–0.005 scene-linear, not 0.02.
5. **Rake the light for paper texture [D].** Diffuse shading is cos θ. A micro-normal tilt Δθ changes it by sin θ·Δθ, so the relative contrast is **tan θ·Δθ**.
   - Our felt relief is 0.045 mm over a 1.2 mm period, so Δθ is about 4° (0.07 rad).
   - At θ = 63° (the v004 key) that gives ±14% contrast. At θ = 80° it gives ±40%.
   - Source size matters too: a source subtending more than about 2Δθ averages the effect away.
   - So use a **narrow strip** (about 0.10–0.15 m wide at about 0.5 m, roughly 12–17°) at **75–82° incidence**.
6. **Dark navy paper reads texture through specular sheen, not diffuse light [D/O, ref08, ref10, ref11].** The albedo of #003653 is about (0.00, 0.04, 0.09) linear, so the diffuse contrast is tiny in absolute terms. A broad source near the paper's mirror direction makes the rough specular lobe glint off micro-facets. This is the same card as the foil card if its edge is placed well.
7. **Make the liquid glow with a shaped, gradient back card [S7].** Cut the card to the bottle silhouette from the camera, slightly larger than the liquid region as seen through refraction. Use a vertical gradient (hot low, cooler high) and feathered edges so no card edge is ever seen through the liquid.
8. **Use a long lens from farther back [S2, S4].** It keeps cards close to the product and out of frame, reduces perspective, and narrows what the glass reflects.

---

## 3. Diagnosis of v004

### 3.1 Why the foil reads as flat champagne [D/O]

1. **The source fills the whole mirror cone.**
   - `CRD_Foil_Specular` is 1.1 × 0.42 m at y = −0.55, about 0.51 m in front of the label.
   - Seen from the foil it subtends about **94° × 45°**.
   - Every embossed facet and every paper-tooth facet reflects the card, so there is no black in the foil.
   - Its spherical falloff with power 0.55 is nearly uniform over the central region.
   - Result: one even tone across "AVANTE" (seen in `v004_foil_macro.png`: no bevel highlights, no dark sides).
2. **The source is too dim for metal.**
   - Strength 0.95 × F0 luminance (about 0.73) gives a foil radiance of about 0.65–0.7 scene-linear.
   - Through AgX that lands around 0.75 display, the same zone as cream ink.
   - Real foil highlights sit **3–10× above white paper** and clip.
   - Our foil therefore looks like **printed gold ink, not metal**.
3. **The foil is too rough and blurred.**
   - Roughness is 0.14–0.22 (`mat_label` line 341), with half the paper relief bump on top (line 343).
   - On top of that, `blur_glossy = 0.2` (line 789).
   - Together these smear any gradient into a satin sheen. The mottled, hammered look on the letters comes from that roughness plus the bump.
4. **F0 is pale and AgX desaturates bright values.** FOIL_F0 = (0.95, 0.69, 0.33) is already pale. AgX's path-to-white pulls bright gold toward beige. Both push toward champagne.
5. **The camera is straight on.**
   - `CAM_Macro_Avante` sits at (0, −0.28, 0.137) looking along +Y, so the foil's mirror direction points straight back at the camera.
   - Any card there is either huge (as now) or blocks the camera.
   - The refs avoid this with yaw and pitch, which push the mirror direction off to one side where a card can sit.
6. **The world reflects grey.** The world is (0.02, 0.02, 0.022) and the sweep is 0.016 albedo, lit. Where foil does reflect the surroundings, they are mid-grey, not black.

### 3.2 Why the paper texture is weak [D]

- The key `LGT_Key_Softbox` is 0.9 × 1.2 m at about 0.9 m. It subtends about 55–65°, which averages away the 4° tooth.
- Its incidence on the front face is about 63°, which gives tan θ·Δθ of about ±14%. The large source size then cuts that further.
- The relief amplitude (felt 0.045 mm, fibre 0.012 mm) is plausible for felt paper. The light is the problem, not the bump.
- On navy, diffuse texture is near invisible anyway (see §2.6). Nothing provides a raking specular sheen.
- `Fill_Low` (0.5 m, front-right) and `Top` add flat fill that further flattens the tooth.

### 3.3 Why the macros look like catalogue shots rather than editorial ones [O/D]

| Factor | v004 | References |
|---|---|---|
| Roll | 0° | 15–35° |
| Yaw to label | 0° (foil, roundel); flag about 15° | 15–35° |
| Field width | about 85 mm (foil macro); the whole label face is visible | 40–80 mm, cropped through letters |
| DOF | f/16 on a frontal plane, so everything is sharp | Focus plane on the hero word, with edges falling off |
| Background | charcoal 0.02 grey | Black, or bokeh glow |
| Foil tone | one flat mid tone | clipped highlight to black |
| Liquid | flat peach and orange slabs | gradient glow |

The v004 macros are frontal, evenly lit, deep in focus and centred, which is the catalogue look.

### 3.4 Known issues: likely causes and tests

**A. Tonal step in the liquid where the back card ends** [D]
- `CRD_Brandy_Back` is only 0.15 × 0.14 m, centred at z = 0.092, so it spans z 0.022–0.162.
- The body is a square bottle with flat faces, which act like a plane-parallel slab. The card is seen through the liquid at almost its true projected size, so its **top edge at z ≈ 0.16 shows as a horizontal step** just above the label. The edges are also visible at the sides in the roundel macro.
- The power-0.55 spherical falloff reaches zero at the ellipse boundary with a steep slope near the edge, which makes a visible contour.
- **Test:** temporarily give the card a checker emission. Wherever the checker shows through the liquid, the card is too small.

**B. Upper liquid looks peachy and flat** [D]
- (i) The back card's strength 1.7 is attenuated by roughly 80 mm of liquid to T ≈ (0.47, 0.10, 0.002). That gives a radiance of about (0.8, 0.17, 0.003): a very saturated, fairly bright orange. **AgX desaturates bright saturated values toward white**, which reads as salmon or peach.
- (ii) The glass front face reflects the warm 1.1 m foil card at about 4% (more at the shoulder bevels). That lays a beige veil over the darker liquid.
- (iii) The region refracts a uniform part of the card, so there is no gradient.
- **Test:** render once with `CRD_Foil_Specular` hidden from glossy on the glass (via light linking, or by hiding it), and once with back-card strength 0.8. Watch whether the peach turns to amber.

**C. Smoke-like wisp in the shoulder glass** (three-quarter view, above the liquid surface) [D: hypotheses, ranked]
1. **Denoiser hallucination on a noisy refractive path.** At 128 samples, the paths glass → air gap → liquid meniscus → glass are noisy. OIDN turns the noise into a soft "smoke".
   - Test: the same crop with denoise off at 1024 or more samples. If the wisp becomes grainy speckle, this is the cause.
2. **The liquid top surface or meniscus is seen through the slanted shoulder** with total internal reflection of the rim strip or top light. It is distorted by the glass waviness bump (noise scale 28, distance 0.12 mm). On a thick shoulder that bump becomes a visible swirl.
   - Test: set the glass bump strength to 0 and re-render the crop.
3. **Coincident or near-coincident liquid and glass surfaces at the top rim ring** cause intersection noise (agent2 R1 overlap change).
   - Test: hide the liquid. If the wisp disappears and it was not cause 1, inspect the rim ring.

**D. Bright floor patch in the three-quarter view** (lower left) [D]
- `LGT_Key_Softbox` sits at (−0.72, −0.42, 0.42), aimed at (0, 0, 0.12). With an area light at the default 180° spread, its lower half throws strong light onto the sweep in front-left of the bottle. The 0.62-roughness charcoal floor scatters it back toward the three-quarter camera, which looks across that zone.
- `Fill_Low` at z = 0.08 also grazes the floor from the right.
- **Fix:** light-link the key to exclude `ENV_Sweep`, or set the key's spread to about 30–40°, or add a black floor flag (gobo) along the key's lower edge.

---

## 4. Concrete Cycles recipe for v005 [R]

### 4.0 Geometry helper (use for every foil card)
For a label point **P** with normal **n** and camera at **C**:
- **v** = normalize(C − P)
- **r** = 2(n·v)n − v. This is the mirror direction: the foil at P reflects whatever lies along P + t·r.
- Put the foil card's **gradient edge or peak** on that line at t = 0.35–0.50 m, and make it subtend **20–35°** (width ≈ 2·t·tan(half-angle): 0.15–0.30 m at 0.45 m).
- Put a **black flag** (non-emissive, visible to glossy, albedo 0.003) on the other side of r so the lower bevels have black to reflect.
- Script it: compute r in `build_studio` from the active camera, and place the card with `look_at(card, P)`. Keep it parented to the camera rig, like `RIG_BackCard`, so it follows camera changes.

Worked example for the new foil macro (§4.2):
- Camera direction from the wordmark: v ≈ (0.338, −0.930, 0.139), from yaw 20° right and pitch 8° up.
- Label normal: n ≈ (0, −0.999, 0.05).
- n·v ≈ 0.93, which gives **r ≈ (−0.34, −0.93, −0.05)**: front-left, almost level.
- Card centre: P + 0.45·(−0.34, −0.93, +0.08). This sits slightly *above* r, so the emboss upper bevels catch the peak and the lower bevels see the flag beneath.

### 4.1 Global changes (all shots)
| Item | v004 | v005 |
|---|---|---|
| World | 0.02 grey | **0.002–0.004**, or black with the sweep lit separately |
| Sweep albedo | 0.016, lit by the key | keep, but **light-link the key, fill and foil card to exclude the sweep**. Light the sweep with its own soft top-back light for a vertical falloff, as in the refs' dark gradients. |
| Foil roughness | 0.14–0.22 | **0.03–0.06** base, plus a noise of ±0.02. Keep the paper-relief bump on the foil at **0.5× → 0.8×** so the paper tooth shows through the foil (ref01, ref13). |
| FOIL_F0 | (0.95, 0.69, 0.33) | try **(1.0, 0.76, 0.40)**, or use the Principled "Metallic" F82 tint (5.x has a Specular Tint/F82 on metallic) **[M]**. Then judge with the new lighting before tweaking colour; most of the champagne effect is lighting. |
| blur_glossy | 0.2 | **0.0** for macros, **0.1** for hero/three-quarter |
| View | AgX, Look None | AgX with **Look "Medium High Contrast"** (macros) or "Base Contrast" (hero) **[M: check names in 5.1]**. Exposure −0.3 to −0.5, so the foil can clip while the liquid stays saturated. Avoid Punchy on the amber (it darkens and shifts hue, [S9]). |
| Samples | 128 | hero 1024, macros **2048**, adaptive threshold 0.003, OIDN with albedo and normal guiding passes, quality High. Prefilter "Accurate". Check for the shoulder wisp with denoise off (§3.4 C). |
| Clamp | indirect 10 | keep 10. Direct 0. |
| Light tree | (check) | ON (needed for efficient light linking [S8]) |

### 4.2 Shot: Foil macro "AVANTE" (editorial, ref01/ref13 style)

**Camera**
- 135 mm lens, sensor 36 mm, sensor fit horizontal, 2000 × 1600 px.
- Distance about 0.30 m to the wordmark, which gives a field of about 80 mm (the wordmark fills about 60%).
- Yaw 20° right, pitch 8° up (camera slightly below, looking up gives a heroic feel and puts the mirror direction low).
- **Roll −25°** (Dutch, reading uphill, like ref01).
- Position ≈ P + 0.30·(0.338, −0.930, 0.139).
- **DOF:** use `dof.focus_object` set to an empty on the "N" of AVANTE (more robust than `focus_distance`), at **f/16**.
  - **[D]** In Blender the aperture diameter is A = lens/fstop = 8.4 mm. The object-space blur at depth offset Δz is A·Δz/z. Pixel pitch is 80 mm / 2000 = 0.04 mm.
  - Results: within ±3 mm, less than 2 px (sharp). At 10 mm, about 7 px. At 20 mm, about 14 px.
  - At 20° yaw, a 50 mm wordmark spans about 17 mm in depth (±8.5 mm), so the end letters get about 5 px of softening. That suits an editorial shot. Use f/22 if the client wants the word fully crisp.

**Lights** (all area lights or emissive cards; sizes are W × H in metres)
| Name | Type | Size | Placement | Strength | Linking |
|---|---|---|---|---|---|
| CRD_Foil_Gradient | emissive plane, **linear vertical ramp**: 0 at the bottom edge → 1 at 65% height → 0.6 at the top. Hard bottom edge, soft top. Colour (1.0, 0.96, 0.9). | 0.22 × 0.35 | centre P + 0.45·(−0.34, −0.93, +0.08), facing P | peak emission **5–8** (foil peak about 3–5 scene-linear → clips in AgX) | receivers: **labels only** (wrap, collar, roundel). Exclude glass and liquid so it does not veil the liquid. visible_camera off. |
| FLG_Foil_Black | black plane, albedo 0.003, visible to glossy | 0.30 × 0.20 | directly below the foil card, its top touching the card's bottom edge, facing P | – | – |
| LGT_Paper_Rake | area light, rectangle | **0.10 × 0.45** (strip) | at **78°** incidence from the label normal, from upper-left along the label (direction about (−0.75, −0.20, 0.63)), about 0.45 m from P. Spread 40°. | about 6–10 W. Tune so the bare paper's lit side is about 0.15 scene-linear. | receivers: labels only. Exclude the sweep. |
| LGT_Sheen_Big | area light, rectangle | 0.6 × 0.6 | near the paper's mirror direction but offset about 15° to the right of r (so the navy picks up graded sheen without washing it) | low, 2–4 W | receivers: labels only |
| CRD_Brandy_Back | see §4.5 | | | | liquid + glass only |
| Rim strips | keep the v004 positions | | | | glass only |
| Key softbox, Fill_Low, Top | **disable** for this shot (or Top at 0.2 for the capsule) | | | | |

**Target look:** the "AVANTE" letters show one clipped highlight band sweeping across their upper bevels, warm gold mid-tones, and dark brown or black lower bevels. The navy shows the felt tooth with a gentle left-to-right sheen gradient. The liquid strip above the label is an amber glow that gets darker toward the top.

### 4.3 Shot: Roundel macro (ref11 style)
- **Camera:** 135 mm at about 0.32 m (field about 85 mm, roundel ≈ 55% of the frame). Yaw 12°, pitch −5° (slightly from above), roll 10°. f/11 with focus object at the monogram centre. The roundel surface is nearly flat, so f/11 keeps it crisp. The liquid behind defocuses into a smooth glow.
- **Foil card:** same rule as §4.0. 0.18 × 0.28 m, peak 5–7, ramp top-to-bottom. Labels only.
- **Black flag:** opposite side of r.
- **Back card:** shaped, **bright lower-right → dark upper-left** (ref11), because the roundel sits low on the body. The glow under and around the disc separates the navy film from the liquid. Strength peak 2.5, upper 0.6.
- The roundel film's own glossy surface will mirror the foil card too. Keep the film roughness about 0.02 but light-link the foil card so its film reflection is a narrow band, not a sheet.
- **Texture:** the roundel mask is 1200 px over 47.7 mm, about 25 px/mm. At this crop the frame needs about 23.5 px/mm, which is only 1:1. Re-export at **≥ 2400 px (50 px/mm)**.

### 4.4 Shot: Neck / collar flag (ref05 and ref06 style)
- **Camera A (ref05 worm's-eye):** 65 mm at about 0.22 m from the flag. Camera below the shoulder, pitch **+25° looking up**, yaw 30° so the flag is about 40° to the view axis and its foil catches the card. Roll 10°. **f/4**, focus on the flag's roundel art. The shoulder and body in the foreground fall into a soft amber blur (needs the back card on), and the capsule top recedes.
- **Camera B (ref06 cap hero):** 100 mm at about 0.25 m, from above at pitch −40°, roll 30°, f/8 with focus on the capsule top edge.
- **Lights:**
  - Small key 0.20 × 0.20 m upper-left-back, about 0.35 m away, 45° behind the subject plane. It gives crisp ridge highlights on the capsule pleats and gold pinline.
  - Foil card for the flag: 0.15 × 0.25 m, placed at the flag's mirror direction (the flag is a flat radial ply at +X: n ≈ (0, −1, 0) for the front ply).
  - Black flags left. No fill.
  - Background: a dark teal-to-black gradient is an option (ref05) via the sweep light.

### 4.5 Liquid back card (all shots): fixes the step and the peach
- **Size:** at least the liquid silhouette from the active camera plus about 15 mm all round. For the body that is about **0.13 W × 0.20 H m** at y = +0.06 (just behind the back face). It is safe to oversize because `visible_camera = False`, so it is only ever seen through refraction or reflection.
- **Shading:** replace the spherical power-0.55 falloff with a **separable smoothstep**. Horizontal feather starts at 70% half-width. Vertically, use a ramp: **1.0 at the bottom third → 0.45 at the shoulder**, with the top 15% feathered to 0.2, never to 0 inside the silhouette.
- **Colour:** warm white (1.0, 0.90, 0.75). Strength peak **1.0–1.4** (was 1.7), so the transmitted amber stays below AgX's desaturation knee.
- **Liquid colour:** adopt agent2 R4's lighter absorption, or keep 95 and drop the card to 1.0. Do not do both without a test.
- **Optional:** a second small "kicker" card, 0.05 × 0.04 m, hot (3.0) and low behind the base, for a gold glow at the heel and base edges (ref01 bottom left).
- Light linking receivers: liquid and glass.

### 4.6 Hero and three-quarter
- **Camera:** 100–120 mm at 1.0–1.15 m instead of 85 mm at 0.74 m. This gives less perspective, smaller glass reflections of the cards, and keeps strips closer. Use f/11 on the label, so there is no visible DOF at this scale. Hero: add 3–5° roll only for the "editorial" variant, never for the catalogue master.
- **Key:** reduce to 0.6 × 0.9 m, spread 45°, and **exclude `ENV_Sweep`** (fixes the floor patch).
- **Sweep:** its own light (0.8 × 0.3 m, high and behind, aimed down the sweep) for a vertical falloff from about 0.04 behind the shoulder to 0.005 at the top corners.
- **Foil card:** compute r per camera (§4.0). For hero and three-quarter, place a 0.4 × 0.25 m gradient card above the camera, slightly to the left. Link it to labels only.
- **Rim strips:** keep them. Add a top-down black flag above the shoulder so the shoulder glass shows black, not grey (fixes the flat shoulder reflections).

### 4.7 Macro detail settings
- **Adaptive subdivision:** keep `adaptive_space='PIXEL'`. Set the pixel size to **0.5** for macros (1.0 for hero), plus scene `cycles.dicing_rate` 0.5 and max subdivisions 12 **[M: check the property names in 5.1]**. Without this, the 0.2 mm emboss bevels become faceted at 25 px/mm.
- **Texture resolution:**
  - The front wrap masks are 4870 px over 243.5 mm, about **20 px/mm**.
  - The new foil macro (80 mm field / 2000 px) needs 25 px/mm at 1:1 and **≥ 50 px/mm** for clean edges. That means re-exporting COLOR, FOIL and EMB to about **12,200 × 5,080 px**, or rendering only a cropped artwork tile at 60 px/mm for the macro UV region.
  - Use Cubic interpolation on the masks, and Closest is wrong. Foil and emboss masks must share pixel registration.
- **Bump vs displacement:** keep the emboss as true displacement (`EMB_H` 0.2 mm). Keep the paper tooth as bump (sub-pixel). For the foil, add a small edge-bevel height (about 0.03 mm) from a blurred foil mask so letter edges catch highlights, as in ref13.
- **Samples and denoise:** see §4.1. For macro QC, also render one frame with denoise off to check the foil's micro-sparkle is real and not denoiser smear.

### 4.8 Suggested macro shot list (v005)
| ID | Mimics | Lens | Dist | Yaw / Pitch / Roll | f-stop | Focus |
|---|---|---|---|---|---|---|
| M1 Wordmark diagonal | ref01, ref13 | 135 | 0.30 | +20 / +8 / −25 | 16 | the "N" of AVANTE |
| M2 Spear emblem + top of label + amber shoulder glow | ref03 | 100 | 0.26 | −15 / +12 / +18 | 11 | spear tip |
| M3 Roundel on glow | ref11 | 135 | 0.32 | +12 / −5 / +10 | 11 | monogram |
| M4 Neck worm's-eye | ref05 | 65 | 0.22 | +30 / +25 / +10 | 4 | flag art |
| M5 Capsule top down | ref06 | 100 | 0.25 | +20 / −40 / +30 | 8 | capsule rim |
| M6 Very tight foil detail (letters cropped) | ref12 | 135 | 0.20 | +25 / 0 / −30 | 22 | "VA" |

(Yaw is positive to camera-right of the label normal; pitch is positive with the camera below the target, looking up.)

---

## 5. Gap list, ranked by visual impact

| # | Gap | Impact | Fix (section) | Effort |
|---|---|---|---|---|
| 1 | Foil reads as champagne ink, not metal: no gradient and no black, source too big and dim, roughness too high | ★★★★★ | Gradient foil card in the mirror direction, plus a black flag; roughness 0.03–0.06; blur_glossy 0; peak 5–8 (§4.0, 4.1, 4.2) | M |
| 2 | Macros frontal and catalogue-like: no roll or yaw, everything sharp | ★★★★★ | New cameras M1–M6 with focus objects and f-stops (§4.8) | S |
| 3 | Liquid flat and peachy, with a tonal step at the card edge | ★★★★ | Oversized shaped back card with a smoothstep vertical gradient at strength about 1.2; foil card linked away from the glass (§4.5, §3.4 A/B) | S |
| 4 | Environment grey, not black: foil and glass reflect mid-grey | ★★★★ | World 0.003; sweep lit only by its own light; flags above the shoulder (§4.1, 4.6) | S |
| 5 | Paper texture weak, especially on navy | ★★★ | Raking strip at 78°, labels only; a large offset sheen source (§2.5–2.6, §4.2) | S |
| 6 | Texture resolution below the macro sampling rate (20 px/mm vs ≥ 50 needed) | ★★★ | Re-export the masks at 50–60 px/mm or use a macro tile (§4.7) | M |
| 7 | Floor patch in the three-quarter view | ★★ | Key excludes the sweep; spread 40°; floor gobo (§3.4 D) | S |
| 8 | Smoke wisp in the shoulder | ★★ | Denoise-off test, then more samples, glass bump 0 on the shoulder, liquid rim overlap (§3.4 C) | S–M |
| 9 | Tonemapping is too soft: Look None, so there are no true blacks | ★★ | AgX Medium High Contrast, exposure −0.3 to −0.5 (§4.1) | XS |
| 10 | Emboss and foil edges lack bevel highlights | ★★ | Dicing 0.5 px; foil edge bevel height from a blurred mask (§4.7) | M |
| 11 | Hero perspective too close, so large card reflections show in the glass | ★ | 100–120 mm at 1.0–1.15 m (§4.6) | XS |

### Suggested test order for v005 (cheap to expensive)
1. Render M1 with only the foil card, the flag and a black world. Confirm the foil goes bright-to-black and is no longer champagne. Sweep the card ±5 cm vertically and keep the best.
2. Add the rake strip and check the felt tooth on the navy.
3. Swap in the new back card and check that the step and peach are gone (crop above the label).
4. Look test: None vs Base vs Medium High Contrast at exposure 0 / −0.3 / −0.5.
5. Three-quarter view with the key excluding the sweep, plus a denoise-off crop of the shoulder.
6. Re-export textures at high resolution, set dicing to 0.5, then render the final macros at 2048 samples.
