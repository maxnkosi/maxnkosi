# Agent 2: Liquid and optical physics

Search limits: no source found for cognac CIELAB or spectra, nor a Blender manual page on nested dielectrics. No numbers below are invented as sourced.

## R1. Liquid/glass interface: OVERLAP, not gap
- Sources: [Blender PR 118478, WIP volume priority and nested IOR](https://projects.blender.org/blender/blender/pulls/118478) (I could not confirm it merged; treat stock Cycles as having NO priority); [KeyShot liquid in glass](https://www.keyshot.com/blog/how-to-render-liquid-in-glass-with-keyshot/) (small overlap gives an accurate look); [Blender Artists thread](https://blenderartists.org/t/accurate-liquid-in-glass-rendering/1386201?page=2) (overlap workaround); [RenderMan priorities](https://rmanwiki.pixar.com/x/HmYGC).
- VERIFIED: Real glass (1.52) touches liquid (about 1.36) with no air; the critical angle is about 63 deg. A 0.05 mm air film gives glass-to-air, critical angle about 41 deg, so TIR starts much earlier. That is the suspected cause of the dark/bright rim.
- Cycles limit (from the PR context, not tested here): the Principled BSDF assumes the other side of a surface is air, so a true 1.52/1.36 interface is impossible. Overlap is the standard approximation.
- Implement: liquid outer wall = glass inner wall + 0.05 mm INTO the glass (currently minus 0.1 mm in `build_liquid`, i.e. `inner_width(z) + 0.1`). Flip the top rim ring to the same overlap. Also start the base at `base_t - 0.05`. Keep IOR 1.36 and glass 1.52.
- ARTISTIC: Light then refracts air to liquid at the glass surface, not glass to liquid. The error is small for a 4.5 mm wall.
- Test: render a 3-frame crop of the shoulder and base. The rim should lose the mirror-like dark band and the liquid should read continuous with the glass.

## R2. Liquid IOR
- Source: [Riobou et al., EPJ E 2009](https://epje.epj.org/articles/epje/abs/2009/09/10189_2009_Article_9376/10189_2009_Article_9376.html) (n is non-linear, with a maximum near 41 mol% water); [PubMed 20281657](https://pubmed.ncbi.nlm.nih.gov/20281657/).
- VERIFIED: n is non-monotonic in concentration. Pure water is about 1.333 and pure ethanol about 1.36. A figure of about 1.355 to 1.357 for 40% v/v at 20 C is my recollection, UNVERIFIED. Check the CRC Handbook.
- Implement: set IOR 1.355 (currently 1.36; the difference is invisible). Do not use caramel, sugar or congener effects; they are below 0.003.

## R3. Meniscus
- Sources: [capillary length background](https://www.ox.ac.uk/node/513287); [OpenStax ethanol vs water rise](https://collegephysicsanswers.com/openstax-solutions/what-ratio-heights-which-ethyl-alcohol-and-water-are-raised-capillary-action).
- VERIFIED: Meniscus scale = capillary length sqrt(gamma/(rho g)).
- DERIVED (mine, unsourced): for 40% ABV with gamma about 0.033 N/m and rho about 940 kg/m3, lc is about 1.9 mm. Flat-wall climb at contact angle 0 deg is about 1.41 x lc = 2.7 mm. At 20 to 30 deg it is about 2.0 mm.
- Implement: keep the profile shape (width about 3.5 mm to flat is slightly wide; use about 2.5 mm). Raise the peak climb 1.3 to 1.8 mm. The effect is a subtle thin bright line at the surface; keep it under 2 mm.
- Test: top-surface close-up, with the line visible but unobtrusive.

## R4. Absorption (ARTISTIC; no sourced cognac spectrum)
- Sources: [OIV spirit colour method, 445 nm](https://www.oiv.int/node/1936); [AJEV three-wavelength brandy method (440/530/600 nm)](https://scilit.com/publications/471c514d6f96b127a8c31b7176d18fe2). These tell you how to measure a sample, not what values to use.
- Cycles Absorption: T = exp(-density x (1 - colour) x d). The current set gives blue about 0.002 over 80 mm, which is effectively black blue and risks muddy shadows/magenta-brown edges.
- Implement: density 60, colour (0.90, 0.667, 0.083). This gives T at 80 mm of about (0.62, 0.20, 0.012) and a lighter amber. Thin edges (corners) glow gold.
- Calibrate: measure a real sample's absorbance at 445 nm and 530 nm / 600 nm in a cuvette, or photograph a sample against white and match the colour.

## R5. Render settings
- Keep: transmission bounces 24, volume bounces 4 (absorption only), caustics off. Add: indirect clamp 10, denoise on, samples 512 for finals.
- VERIFIED reasoning: with caustics off, the bright refractive focus line on the table from a light source is not rendered. Fake it with a faint emissive card or a spot with a gobo, only if the lighting specialist agrees.
- Test: noise fireflies check on a 20% crop at 128 vs 512.

## Raise with specialists
- Glass: glass inner surface must be the exact boundary I overlap with; any wall change moves `inner_width`. Glass absorption (1.5/m) overlaps the sliver, which is negligible. Ask for glass IOR 1.52 confirmation and bevel/edge radius to avoid sharp TIR at the base.
- Lighting: strongly backlit amber needs a bright white backdrop card; a dark charcoal backdrop (current) will make the liquid read near-black.
- Conflict risk: if the glass agent wants a gap for realism, that contradicts R1.
