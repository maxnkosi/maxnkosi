# Agent 1: Glass and Geometry research

Source honesty: web search returned few direct sources on spirit-bottle heel dimensions. Nothing below is cited from a page I did not see in results. Search-result snippets only; I did not open full pages. Numbers marked ART are my artistic proposals, not sourced.

## 1. Smooth profile instead of piecewise-linear (fixes kinks, p99 22 deg)
- Physical (VERIFIED, general geometry): refraction/reflection follow surface normals, so a slope discontinuity shows as a visible streak in highlights. Shade-smooth alone does not remove faceting from a coarse silhouette ([BlenderArtists faceted glass thread](https://blenderartists.org/t/problem-with-rendering-of-a-faceted-glass-in-cycles/1443064), snippet-level only).
- Blender (ART): replace `width_at` with a monotone cubic (PCHIP, `scipy` unavailable in Blender: implement Fritsch-Carlson by hand, ~20 lines) through PROFILE. PCHIP keeps the approved silhouette (passes through every point, no overshoot). Then resample at 0.5 mm in the shoulder (150-185) and heel (0-12), 2 mm elsewhere. Do not use Catmull-Rom (overshoots near the 89.0 plateau).
- Normals: keep `shade_smooth`, but use a weighted/analytic approach: Smooth by angle 40 deg is fine once dihedral is under ~8 deg. Remove the auto-smooth angle dependence at the chamfer edges (EDGE_SOFT 0.5 mm already softens).
- Test: recompute max dihedral between adjacent ring quads (target p99 < 6 deg); render a striped-HDRI mirror ball test (zebra) of the bottle with roughness 0 metallic; streaks must be continuous.

## 2. Thick, rounded heel (ART; physical premise partly sourced)
- Sourced: patents describe the heel as a curved zone defined by outer radius, inner radius and thickness, and say it is reinforced by thickening the glass there ([US 11014701](https://patents.justia.com/patent/11014701)). A bottle patent notes some bottles have a much thicker base than strength needs, making them heavy ([US 10968005](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10968005)). Press-and-blow bottles have more uniform walls; heel impact strength matters ([search result, zendy.io 10.1002/pts.580](https://zendy.io/title/10.1002/pts.580)).
- NOT found: any numeric heel radius or base thickness for premium spirit bottles. The values below are artistic.
- Implementation (ART): inner floor as a filleted curve, not a 90 deg corner. Inner wall to floor fillet radius 10-14 mm (outer heel is already about 5-10 mm). Base thickness: keep volume-solved `base_t`, but add a slight inner floor dome (concave punt) of 3-5 mm rise over the centre 40 mm radius, and let the inner profile near the floor be inner_width(z) shrinking by wall + 4 mm at z=0..8 (wall about 8 mm at heel blending to 4.5 mm by z=25). Re-solve `base_t` after so 750 ml fill holds (volume must be re-checked; fill height is supplier-fixed).
- Visual: thick glass at the base gives a bright, lensing heel band with strong internal refraction of the table, which reads as premium weight.
- Test: crop render of the bottom 30 mm against a grid floor; the inner floor edge must show a soft curved caustic line, not a hard line. Compare to a reference photo.

## 3. IOR and tint
- VERIFIED: soda-lime glass n_D about 1.518-1.520 ([Wikipedia](https://en.wikipedia.org/wiki/Soda%E2%80%93lime_glass)); museum reference 1.512-1.518 ([CAMEO](https://cameo.mfa.org/wiki/Soda_glass)). Keep IOR 1.52 (current value is right; no change needed).
- VERIFIED: iron impurities give the green tinge; ferrous iron drives it; clear ("flint") glass is made with low-iron raw materials ([Wikipedia](https://en.wikipedia.org/wiki/Soda%E2%80%93lime_glass), [patent US 12365616](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12365616)). Note: "flint" in container trade means colourless soda-lime, not lead glass. I did not open a source defining that term; treat as my knowledge.
- ART: keep absorption colour (0.93, 0.98, 0.95) but Density 1.5 per metre is nearly invisible in 4.5 mm walls; the visible green appears through glancing paths (edges, thick heel). Try Density 8-15 per metre, color (0.90, 0.97, 0.93). Test with a white-backed bottle: edges should have faint green, face-on nearly clear.

## 4. Mould seams and waviness (ART)
- Sourced context only: vertical mould seams exist and affect thickness ([US 4336050 family result](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4336050), snippet). No appearance data found.
- Implementation: bump-only (glass shader) via a Noise texture, scale about 0.4 per mm-equivalent low frequency, strength 0.01-0.02, driven by Object coords stretched in Z; plus a thin seam line: geometry-free, using bump from a narrow gaussian on |x| at the two chamfer-free seams with height 0.02 mm. Keep subtle: it should only be visible in reflections.
- Test: zoom render at a softbox reflection; the straight edge reflection should wobble very slightly (about 1 px).

## Overlaps and disagreements to raise
- Liquid specialist: liquid mesh uses `inner_width - 0.1`, so a gap-free glass/liquid interface exists only with an inner profile change; if I fillet the inner floor, the liquid base must follow the same inner curve and use `-0.0` offset or a shared surface. Cycles dispersion is not supported ([BlenderArtists thread, snippet](https://blenderartists.org/t/glass-bottle-has-dark-sides/1518382)): do not rely on it.
- Lighting specialist: the zebra/striped test needs their studio light set; heel brightness depends on a floor reflection and bounce, so agree on a common test HDRI.
- Dark-sides issue in reports: inner faces and mixed materials caused it for one user; check that our single closed shell has consistent outward outer normals and inward inner normals.
