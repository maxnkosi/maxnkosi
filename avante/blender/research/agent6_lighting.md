# Agent 6: Product photography and lighting

Source quality: web results are tutorials, forum posts and Blender docs. They are not controlled tests. No claim below is stronger than its source.

## VERIFIED (documented behaviour)

**V1. Denoiser inputs.** Blender recommends at least the Albedo pass, since "None" blurs detail at low samples. More passes give better results.
- Source: https://docs.blender.org/manual/en/4.5/render/cycles/render_settings/sampling.html
- Implementation: set Denoising Data passes on, and set the denoiser input to Albedo+Normal, prefilter Accurate.
- Risk: albedo and normal do not follow refraction, so glass and liquid can smear. Compare against Albedo-only.
- Test: render at 128 samples with each setting and crop the glass edge and label text at 200%.

**V2. Light Threshold.** It probabilistically kills light samples below the threshold, and 0 disables it.
- Source: same Sampling page.
- Implementation: set it to 0.0 here. Our emissive cards are the only fill, and a nonzero threshold darkens the dim gradient tails.

**V3. Adaptive sampling.** Typical Noise Threshold is 0.1 to 0.001.
- Source: same Sampling page.
- Implementation: 0.005 for finals, with min samples 64.

**V4. Filmic is deprecated and AgX is the Blender-documented replacement for saturated colour.** Source: https://sources.debian.org/src/blender-doc/4.3-1/manual/render/color_management.rst

**V5. Khronos PBR Neutral** was designed to reproduce base colours faithfully for product visualisation. It can clip highlights and can look flatter.
- Sources: https://devtalk.blender.org/t/adding-pbr-neutral-tone-mapper/33602 and https://blenderartists.org/t/khronos-pbr-neutral-problems-when-approaching-highlights/1595901
- The latter is forum evidence only.

**V6. Macro depth of field is computed, not sourced.**
- Inputs: 100 mm at 0.235 m focus, so magnification is about 0.74. Circle of confusion is 0.03 mm.
- Formula: DoF = 2·N·c·(1+m)/m².
- Result: about 1.5 mm at f/8 and about 2.1 mm at f/11.
- Consequence: a curved bottle will fall off in focus. CAM_Macro_Avante (f/8) will lose the label edges, so use f/16 (about 3 mm) or focus-stack.
- Test: render the label with a ruler-like edge and check sharpness at the label sides.

## ARTISTIC (practitioner convention, tune by eye)

Sources for A1 to A3: https://www.diyphotography.net/?p=112924, https://www.photigy.com/whisky-shot-product-photography-behind-the-scene/, https://visualeducation.com/class/whisky-product-shoot/, https://broncolor.swiss/news/how-to-capturing-zero-gravity-spirits

**A1. Dark-field with strip edge definition.** Practitioners put narrow strips behind or beside the bottle for crisp edge lines, and diffuse them to avoid harsh streaks.
- Current: the rim strips are 0.07 x 0.8 m at x = ±0.38, y = 0.12.
- Change: give each strip a gradient emission (brighter toward the top) rather than a constant light.
- Move to x = ±0.30, y = 0.08. Narrow the width to 0.05 m. Keep the power at 5, then test 3 to 8.
- Visual gain: the rim line fades along the shoulder instead of hitting a hard stop.
- Test: render a glass-only clay pass with a neutral grey liquid and check the edge line is continuous.

**A2. Gradient backlight, gold card.** Gold or amber cards behind the bottle make the spirit glow, and a diffuser gives a gradient.
- Current: CRD_Brandy_Back is 0.11 x 0.2 m, strength 2.6, colour (1.0, 0.93, 0.82).
- Change: increase to 0.16 x 0.26 m, shift the colour to (1.0, 0.82, 0.55) for brandy warmth, and replace the radial falloff with a vertical gradient. Make the bottom 1.6x the top, so the base of the liquid glows and the shoulder falls off.
- Keep the card sized to hide behind the glass silhouette. Confirm it is still invisible to the camera.
- Test: render with the back card disabled and enabled, and compare liquid luminance in the body.

**A3. Negative fill and flags.**
- Keep the black flags. Add a third flag at the camera-left of the label, x = -0.35, y = -0.25, z = 0.12, size 0.4 x 0.6 m.
- Purpose: stop the key softbox from lifting the shadow side of the glass.
- Result: the glass edges stay dark and the rim lines read stronger.
- Test: compare the shadow-side edge value with and without the flag.

**A4. Label lit separately from glass.**
- Photographers use grids or separate sources for the label.
- Current: the key softbox at (-0.72, -0.42, 0.42), 0.9 x 1.2 m, power 7.5, lights both.
- Change: add a link-exclusion with light groups. Use Cycles light groups to give the key softbox a dedicated pass for the label.
- Alternatively, shrink the key to 0.5 x 0.9 m for harder gradients on the foil.
- Test: render light groups separately and adjust each in compositing without re-rendering.

**A5. Foil specular card.**
- Current: CRD_Foil_Specular is 1.1 x 0.42 m at y = -0.55, strength 1.25.
- Make it a vertical gradient with a sharp upper edge. A hard-edged gradient gives the foil its sweeping highlight.
- Shift it 0.1 m off-axis (x = -0.1) so it does not reflect straight to the lens.
- Test: macro camera on the foil, with four gradient positions.

**A6. Polariser (cross-polarisation).** Can reduce glare over the amber, per the Visual Education page. Cycles has no polarisation, so emulate it by lowering the specular on the label material. Hand this to the foil and label specialists.

## Colour management
- Recommendation: stay on AgX but switch the Look from Punchy to None, or to Punchy at low exposure offset.
- Reason: Punchy raises saturation and contrast, which risks shifting navy and amber hues. AgX has built-in hue correction, per https://blenderartists.org/t/agx-changes-hue/1527123 (forum).
- Test: add a colour-chart plane (a Macbeth chart swatch set) to a test scene and compare AgX None, AgX Punchy and Neutral. Check ΔE of the amber and navy against the brand swatches.
- Use PBR Neutral only if the brand colour matching has priority over highlight rolloff.

## Cycles settings
- Caustics: keep both off. It is the only practical choice for this scene, since the glass is lit by emissive cards that are small relative to the scene.
- Clamping: set Indirect clamp to about 10 and leave Direct at 0. The emissive cards at strength 2.6 can fire fireflies through the liquid. Check that the highlights are preserved.
- Samples: 512 for finals with adaptive sampling, 128 for previews.
- Blur Glossy 0.5 softens the foil. Reduce it to 0.1 for macros, or the foil sparkle will smear.

## Overlap to raise
- Glass: the rim strips and back-card gradients drive the edge lines. Coordinate the glass thickness and IOR.
- Liquid: back-card colour and strength drive the amber glow, so agree one owner for it.
- Foil: the specular card position, Blur Glossy and the polariser emulation.
- Label: light groups and the key softbox.
