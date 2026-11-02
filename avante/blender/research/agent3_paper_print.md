# Agent 3: Paper and Print Materials

Scale: 1 BU = 1 m. Macro 0.043 mm/px, so any feature under 0.09 mm is sub-Nyquist. Use Object-space coordinates; Mapping scale = 1000 / feature_mm (per metre).

## VERIFIED (sourced)
- Fedrigoni Wet-Glue range: wet-strength 70-100 gsm, uncoated/coated/cast, some embossed. [FINAT](https://www.finat.com/news/fedrigoni-special-papers-wet-glue-collection-the-most-innovative-papers-for-wet-glue-label-converting), [Labels&Labeling](https://www.labelsandlabeling.com/news/substrates-adhesives/fedrigoni-special-papers-launches-wet-glue-collection)
- Martele White WS: 100 gsm face, 125 um face thickness; WNE4252: 125 gsm, 152 um. [WNE4175](https://myselfadhesives.fedrigoni.com/en_en/wne4175), [WNE4252](https://myselfadhesives.fedrigoni.com/en_en/wne4252)
- Felt-marked wine/spirits papers exist; Brillante White Felt is described as a "pecked felt" pattern. [Labels&Labeling](https://www.labelsandlabeling.com/news/substrates-adhesives/fedrigoni-launches-brillante-white-felt-premium-paper), [selfadhesives.fedrigoni](https://selfadhesives.fedrigoni.com/industry/wine-spirits-and-craft-beers/)
- UPM Raflatac wine/spirits range has textured and WSA (wet-strength) grades, no gsm/caliper found. [Label&NarrowWeb](https://www.labelandnarrowweb.com/breaking-news/upm-raflatac-adds-new-products-to-wine-and-spirits-portfolio/). An unattributed 90 gsm / 119 um textured WS sheet exists ([PDF](https://newmedia.ua/wp-content/uploads/2026/05/8385920.pdf)); treat as unverified.
- Ink on uncoated stock penetrates pores, giving inhomogeneous edges and larger optical dot gain; solids on uncoated rarely mottle. [Wuppertal dot gain](https://www.dod.uni-wuppertal.de/fileadmin/_migrated/content_uploads/Dotgain_in_Offset_Printing.pdf), [SPIE](https://proceedings.spiedigitallibrary.org/conference-proceedings-of-spie/9015/901509/Physical-and-optical-dot-gain--characterization-and-relation-to/10.1117/12.2035713.full)

NOT FOUND: any published felt-mark depth or pitch in mm, matte-varnish gloss data, die-cut edge photography, adhesive-contact optics. Everything below on those is ARTISTIC. Face thickness 125 um (face only, with 100 gsm) supports a 0.10 mm current value; 0.12 mm is defensible.

## R1. Felt/fibre surface (ARTISTIC values, VERIFIED qualitative)
Physical: felt marking is a regular-ish pecked relief; fibres add a finer random layer.
Implementation: Bump (Distance 1.0, strength 0.35) fed by Height = mix of:
- Felt: Noise Texture 3D, Object coords, scale 1000/1.2 = 833, detail 2, roughness 0.5, Distortion 0.3, high-contrast ColorRamp (0.35-0.65). Pitch about 1.2 mm, relief about 0.02 mm.
- Fibre: Noise with Mapping scale (x 4000, y 800, z 4000) for 0.25 mm streaks about 1.2 mm long, relief about 0.005 mm (= 0.1 px, shading only).
Do not use true displacement for either; the existing 0.2 mm EMB-01 stays. Keep bump Distance in metres (0.00002 felt).
Gain: removes plastic flatness. Test: macro at 2000 px, 30-degree key raking light; felt should read as tonal pecking, not noise. Compare against a Brillante/Cotone photo.

## R2. Ink separation (ARTISTIC)
Physical: flood ink sits partly in valleys; matte varnish diffuses highlights.
Implement: ink mask = existing colour map luminance. Printed area: roughness 0.58 plus noise +-0.06 (scale 833); bump strength x0.7 (ink levels relief). Cream knock-out (bare paper): roughness 0.78, full bump, sheen 0.25 kept. Slight base-colour modulation +-3% on navy, same noise (the ink-density variation; the sources say mottle is rare on uncoated, so keep it very subtle).
Gain: ink and paper read as different layers at the type edges. Test: macro on a cream letter edge; roughness-only debug render.

## R3. Die-cut edge white core
Physical: ink does not wrap the cut; the cut shows raw paper.
Implement: Solidify `material_offset_rim = 1`, append a second material "M_LBL_EDGE": Principled base (0.93, 0.91, 0.86), roughness 0.9, sheen 0.3, Noise-driven bump 0.01 mm at 0.1 mm scale. Rim at 0.10 mm = 2.3 px at macro: will read as a hairline. Apply to Wrap and Collar. Check face-offset=1.0 keeps outer ink face unchanged.
Test: grazing macro on the label corner; edge must be lighter than adjacent navy.

## R4. Adhesive contact on glass (ARTISTIC)
Physical: a 10-30 um adhesive layer; clear contact with tiny edge lift.
Implement: do not model glue. Add a darkening gradient on the back via Pointiness-free approach: Geometry distance-to-edge mask (UV, 0.3 mm width) driving a +0.15 roughness and a faint 0.3% lighter edge. Optional 0.03 mm gap already in `surf_xyz(u,v,0.03)`; keep. If wet-glue (Fedrigoni wet-glue is relevant), no visible glue line at all.
Test: contact shot at silhouette; no light gap other than shadow.

## R5. Neck collar (ARTISTIC)
Physical: stiff paper bends in a curl; overlapping plies show a step of one thickness (0.10 mm).
Implement: low-frequency lift noise (scale 1000/20 = 50, amplitude 0.05 mm) on flag plies' bump only; keep geometry. Same paper nodes as wrap, shared node group so felt direction matches.
Test: ply overlap closeup.

## Overlap to raise
- Foil: foil mask edge must inherit the felt bump (foil on texture breaks up); raise whether foil roughness gets the same noise. Foil mask edge softening in px.
- Lighting: R1 and R3 need a raking key; do not fix on soft box only. Agree sheen 0.25 is not double-counted with area-light spec.
- Cycles: Bump node, Principled BSDF, Mapping [Blender manual](https://docs.blender.org/manual/en/latest/render/shader_nodes/vector/bump.html) (not fetched this session).
