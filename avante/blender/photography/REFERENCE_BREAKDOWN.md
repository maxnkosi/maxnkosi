# Avante — photography reference breakdown (3 Nov 2026)

Source: the "Photgraphy references" sections on Figma review pages 04–08 (nodes 57:358, 57:368, 57:378, 57:388,
57:398). The images stay in Figma and in Claude's local scratchpad only; they are not committed.
15 placements, 7 distinct images (by image hash). Each placement becomes its own photographic setup
(`PHOTO_<cid>_<ref>` scene), but placements that share an image start from the same rig recipe.

All camera and light values are **estimates** recovered from the image (perspective, highlight shapes, shadow
direction); they are refined in Pass A/B test renders and the final values are recorded in the Blender scenes
(custom properties) and in Notion.

Background rule (user-authorised): composition, camera, lighting and treatment follow the reference; the
backdrop colour moves into the Avante world (navy #0E2233–#003653, warm cream #EFE6D6, muted gold-bronze
#6B5536, warm charcoal #1C1A19), chosen per concept so label, glass and gold stay readable.

| Ref | Figma image | Used on | Shot | Framing / crop | Lens & camera (est.) | Lighting (est.) | Mood / grade |
|---|---|---|---|---|---|---|---|
| R25 · warm seamless | image 25 (5ee68e) | C01 C05 C06 C07 C10 | Whole bottle standing on a seamless, small in frame, slightly left of centre | 5:4 landscape; bottle ≈68 % of frame height; generous negative space right; floor/wall roll at ≈75 % height | ≈85 mm, ≈1.0 m, camera at label height (≈12 cm), level | Large soft key front-left high → soft shadow falling right-back; warm back/under light glowing through the liquid; thin right rim on the glass; dark vignette on the sweep | Low-key, warm, matte; contrast moderate; shadows rich brown |
| R23 · plinth, low angle | image 23 (473e3c) | C01 C05 C10 | Bottle on the corner of a navy plinth, seen from below | 4:5 portrait; bottle ≈75 % height, top cropped close; plinth edge across the bottom ≈12 % | ≈70–90 mm, camera ≈5 cm below the plinth top looking up ≈8° | Backdrop lit warm with a soft gradient (bright behind lower bottle); backlit liquid glowing amber; soft frontal fill keeps the label readable; gold mark catches a small hard highlight | Bright, warm, clean; cream-to-gold gradient — already in the Avante world |
| R19 · label macro | image 19 (eec2b0) | C01 | Tight macro on seal + label, bottle rotated ≈35°, very shallow depth of field | 1:1; seal upper third; label diagonal; background bottle soft | ≈100 mm macro, f/2.8–4, focus on the seal, ≈25 cm | Large soft top-left source for the foil and emboss; dark surround; glass edge highlights | Rich, deep, jewel-like; dark coloured ground (green → navy) |
| R24 · hard beam | image 24 (4fede0) | C05 C07 | Bottle on a pale floor in a hard raking beam, from above | 2:3 portrait; bottle ≈55 % height, centred; caustic shadow toward the front-left | ≈70 mm, camera high ≈25° down, ≈0.9 m | Hard narrow beam from the right/back-right (small source, long throw) → long shadow and caustics; dark gradient wall; little fill | Graphic, high contrast, cool-neutral floor, dark wall |
| R20 · black void | image 20 (172ed6) | C06 | Bottle alone in black, slightly rotated, emblem side lit | ≈1:1.55 portrait; bottle ≈90 % height | ≈90 mm, slightly below centre, bottle turned ≈30° | Strong soft side light from the left through the liquid; narrow rim strips on both edges; no visible background | Very low-key, deep amber glow, crisp edges |
| R21 · floating tilt | image 21 (5c6fd0) | C06 C10 | Bottle floating, tilted ≈30° (top left), cropped close | ≈0.65 portrait; bottle fills the frame diagonally | ≈85 mm, camera square to the label, rolled ≈30° | Long strip softboxes along both sides (glass edge lines), soft frontal fill on the label | Dark, clean, product-render look |
| R22 · label macro dark | image 22 (15973c) | C07 | Extreme close-up of the label, bottle tilted ≈20°, foil glowing | 2:3 portrait; label fills the frame; second bottle as warm bokeh | ≈100 mm macro, f/4, ≈30 cm | Large soft source above-left for foil; warm practical/bokeh behind; low fill | Warm, rich, black-and-gold |

## Adaptation notes per placement

| Placement | Backdrop (Avante world) | What must match | What adapts |
|---|---|---|---|
| C01 · R25 | muted gold-bronze #6B5536 seamless | crop, scale, lens, soft key left, shadow right, liquid glow | colour: bronze instead of brown, so the navy label reads |
| C01 · R19 | navy #0E2233 | macro on the roundel + AVANTE, angle, shallow DOF | green ground → navy; Avante has a roundel, not a seal tab |
| C01 · R23 | warm cream gradient + navy plinth | low angle, plinth corner, backlit glow | none needed (already brand colours) |
| C05 · R25 | muted gold-bronze | as C01 · R25 | — |
| C05 · R23 | warm cream + navy plinth | as C01 · R23 | — |
| C05 · R24 | warm charcoal wall, pale cream floor | hard beam, shadow and caustics, high angle | floor warmer than the grey reference |
| C06 · R25 | warm cream #EFE6D6 → taupe vignette | as C01 · R25 | lighter ground so the navy wrap stands out |
| C06 · R20 | near-black navy #0A1520 | void, side light, rim | black → navy-black |
| C06 · R21 | deep navy #0E2233 | tilt, crop, strips | — |
| C07 · R25 | muted gold-bronze | as C01 · R25 | — |
| C07 · R24 | warm charcoal + cream floor | as C05 · R24 | — |
| C07 · R22 | warm charcoal #1C1A19 with gold bokeh | macro on AVANTE + coin edge | — |
| C10 · R25 | deep navy #0E2233 | as C01 · R25 | navy ground suits the cream label |
| C10 · R21 | deep navy | as C06 · R21 | — |
| C10 · R23 | warm cream + navy plinth | as C01 · R23 | — |
