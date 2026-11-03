# v005 study: what the references taught us (no changes made)

Inputs: 13 client references (Figma AVANTE, page "References (study only)", saved as `references/ref01–13.png`), v004 renders, and five specialist studies in this folder:
A foil appearance · B emboss/deboss · C paper and label · D macro photography and lighting · E implementation audit (line-referenced values).

## 1. What was learnt

**Foil**
- Hot foil is 2–6 µm thick: lacquer, 20–100 nm of aluminium and adhesive. "Gold" is aluminium under a yellow-orange lacquer. A polished, heated die presses it, so the tops are flat and close to mirror-smooth. Paper texture shows only as fine pits, or not at all under sculpted dies (refs 01, 09, 11). (A)
- In every reference, the brightness of a single foil letter runs from a clipped white highlight to dark olive-brown. Measured on a 0–255 scale, the refs span 52–93 in the darkest 5% and 180–245 in the brightest 5%. AVANTE in v004 spans only 151–170. (A)
- The foil colour is already right: FOIL_F0 matches gold reflectance data. Its brightness has to come from the lights it reflects, not from a paler colour. (A)
- Foil only looks bright where it mirrors a light. It needs a narrow, bright gradient strip with a black flag beside it, so the parts not facing a light go dark. (A, D)

**Emboss**
- Real embosses have rounded shoulders with 30–60° walls, and depth is at most half the line width. Combination foil-embosses need brass dies. 0.2 mm works on our 0.10–0.15 mm stock only as a rounded peak, not a flat-topped mesa. (B, sources in file)
- Relief shows up through a thin highlight line along one side and shadow on the other. The line's width depends on the shoulder radius and the size of the light, so small sources give crisp edges. (B, D)
- Deboss crush halo is about 0.5 mm (ref12). The paper around an emboss stretches and loses texture (ref11). (B)

**Paper and label**
- Felt, laid and linen texture reads through raking light and sheen, not through colour noise. Dark floods need a grazing specular to show tooth. (C, D)
- Mottle on uncoated stock is cloudy at a 3–10 mm scale and about ±3%. (C)
- Real labels show a cut-edge line and a contact shadow. Seen through clear glass, the back of an adhesive-backed label looks wetted and darker, with no air-layer mirror. (C)
- Pulp-dyed navy stocks exist (for example Sirio Color, Arconvert Ispira Blue) and avoid a white edge and white back. (C)

**Photography**
- 11 of 13 refs are tilted 15–35° and turned 15–35° from square to the label. They use 85–135 mm lenses, black surroundings, focus on the hero word, and shallow depth of field elsewhere. (D)

## 2. What we lack, and why (verified in code)

| # | Gap | Root cause | Source |
|---|---|---|---|
| 1 | Foil reads champagne, not metal | The 1.1 × 0.42 m foil card fills about ±60° of what the foil mirrors, so every facet reflects the same evenly lit card. At strength 0.95, peak brightness lands at paper level. The world is grey (0.02), blur_glossy is 0.2, roughness 0.14–0.22. The straight-on camera makes this worse. | A, D, E |
| 2 | Foil looks crumpled | The foil bump takes `relief*0.5` (the 1.2 mm paper felt), and roughness varies on a noise at scale 800 (~1.25 mm). Both are confirmed in the builder. | A, B, E |
| 3 | Emboss reads as a digital bevel/keyline | A binary 8-bit mask feeds Displacement directly (midlevel 0, 0.2 mm, method BOTH), giving a flat top with a ~76° wall over one texel and no shoulder. | B, E |
| 4 | Paper looks like suede/velvet | Sheen 0.08 plus default specular. The side panel at grazing reads 2.5× brighter and grey. | C (confirmed in code) |
| 5 | Paper texture invisible | The felt relief is about ±9 µm (1–2° slope). The key light is huge and close to frontal (~63°), giving about ±14% contrast. | C, D |
| 6 | Wrong mottle | Additive ±0.03 at 0.67 mm, which is about ±30% on navy channels. | C, E |
| 7 | Label looks like a decal | No edge bevel or contact shadow. 0.10 mm thick with a 0.03 mm air gap. | C |
| 8 | Liquid tonal step and peachy top | The back card is too small with a hard falloff. The foil card veils the glass. AgX desaturates the orange. | D |
| 9 | Macros look like catalogue shots, not editorial | Square-on 100 mm cameras, and collar flag depth exceeds depth of field. | D, E |
| 10 | Macro textures under-resolved | Artwork at 20 px/mm; tight macros need about 50 px/mm. | D, E |

**Bugs found** (E; items marked *verify* still need checking in the .blend):
- **Paper inner face displaced into the glass:** the inner shell shares the displacing material, so embossed areas push about 0.17 mm into the glass. *Verify.*
- **Roundel film greyed:** the film's Base Color is left at the default 0.8 with Transmission 1, which greys it and shows as a darker ring (confirmed in code).
- **Fibre streaks on the wrong axis:** the stretch is set in object space and runs along Y, the depth axis of the front panel (confirmed).
- **Black flags block no light:** they have `visible_shadow = False` (confirmed).
- **Capsule pokes through collar:** the capsule's outer radius (17.32 mm) exceeds the collar's (17.25 mm).
- **Lights not square:** LGT_Top and LGT_Fill_Low never set size_y, so they are likely not square. *Verify.*
- **Adaptive subdivision may not be active:** the Experimental feature set was removed in 5.1, but whether adaptive dicing is actually running is unconfirmed. *Verify.*

## 3. How to fix it (proposed v005 order, cheapest/highest impact first)

1. **Bugs:** fix the flag shadows, roundel film colour, fibre axis, inner-shell displacement and capsule/collar clearance, and confirm adaptive dicing is running.
2. **Foil shader:** remove the paper bump from the foil, add a fine 1.5–3 µm grain at 0.1–0.17 mm, and give pits a smootherstep at ≤6 µm. Set roughness to 0.06–0.10 ±0.015 and blur_glossy to 0. Optionally rebuild the foil as aluminium plus a tinted coat.
3. **Foil lighting:** use a narrow gradient strip (emission 6–12, 4–8° tall as seen from the label) placed by the mirror-angle formula in D, with a black flag beside it, light-linked to the labels. Darken the world to about 0.003.
4. **Emboss profile:** bake a 16-bit signed-distance height map at 40 px/mm with a 0.35 mm shoulder, a slight dome and a 0.12 mm foot. Keep displacement for the emboss only and send texture through bump, weighted by zone.
5. **Paper:** set sheen to 0 and specular to 0.30–0.35. Make the texture real relief: pecks about 30 µm, body 10 µm, fibres 6 µm, in UV millimetres. Replace mottle with a multiplicative 3–10 mm variation. Add raking strip light.
6. **Label construction:** 0.15 mm stock, a 0.005 mm gap, a 0.025 mm edge bevel, a wetted back seen through glass, and collar-flag plies, fold and curl.
7. **Liquid:** an oversized back card with a smooth ramp at strength 1.0–1.4, linked to liquid and glass only.
8. **Cameras and resolution:** add editorial macro cameras (tilted 15–35°, 100–135 mm), re-export artwork at about 50 px/mm for macros, and render at 2048 samples with albedo and normal passes guiding the denoiser. Use AgX Medium High Contrast at exposure −0.3 to −0.5; the look names come from memory and need checking in 5.1.

## 4. Decisions that need the client

- **Navy stock — DECIDED (client, 3 Nov 2026): dyed-through navy.** Navy cut edge and navy reverse (seen wetted through the glass); the cream reverse and edge are dropped.
- **Stock thickness — DECIDED (client, 3 Nov 2026): 0.15 mm** (was 0.10 mm), with the 0.005 mm glass gap and 0.025 mm edge bevel from section 3.
- **Graphic contrast — DECIDED (client, 3 Nov 2026): tone it down.** The tone-on-tone bird/spear drops to ΔL\* 6–8 against the navy, with the same subtle mottle as the flood. Artwork shape and position are unchanged; only render-side ink contrast changes (not varnish-only).
- **New macro cameras — DECIDED (client, 3 Nov 2026): add angled cameras.** New editorial macros (tilted 15–35°, 100–135 mm, focus on the hero word, per study D) are added alongside the existing cameras, which stay unchanged for like-for-like comparison.
- **Roundel relief direction — DECIDED (client, 3 Nov 2026): keep raised.** 0.04 mm raised foil on clear film, as in v004. Only the optional 0.06–0.08 mm edge softening from study B may apply.

## 5. Confidence

Several values are inferred or from memory and are marked [M]/[I] in A–E. The main gaps in sourcing: no mill publishes texture depths, no die maker publishes depth-versus-caliper tables, and no foil maker publishes gloss figures. None of the fixes have been test-rendered yet.
