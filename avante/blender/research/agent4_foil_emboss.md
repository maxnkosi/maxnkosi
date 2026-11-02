# Agent 4: Foil, Embossing and Relief (roundel focus)

## Evidence status
Web search returned little hard data. Most numbers below are ARTISTIC or vendor-level. Do not present them as measured.

## VERIFIED (sourced)
- Foil needs a very smooth, clean substrate for best appearance; time, pressure and temperature control fill-in and edge quality. https://www.iggesund.com/globalassets/iggesund/services/knowledge/iam/graphics-handbook/gh-pdf----en/hot_foil_stamping_in_practice.pdf (search snippet; PDF text not readable by fetch)
- Flat dies give one level; sculpted dies are CNC brass with rounded multi-level contours; beveled edges let deep emboss avoid cutting the stock. https://decrev.verio.com/emboss.html , https://hinderer-muehlich.com/en/stamping-tools-top-quality-products-for-the-graphics-industry/stamping-dies-counter-dies-set-up-systems-make-ready-material/hot-foil-stamping-dies-embossing-dies-cnc-engraved/foil-stamping-brilliant-contrasts-for-an-elegant-touch
- Micro-structure foil dies exist (tiny patterns on the tool). https://www.atelierbulk.com/en/?p=5218
- Raised UV/tactile varnish builds about 30-100 um (10/50/100 um tiers; 50 um raised spot UV). https://www.friesens.com/books/specialty-options/specialty-finishes/spotuv/ , https://www.4over4.com/help/finishes/whats-the-difference-between-spot-uv-and-raised-spot-uv . A "1.5 mm" wine-label claim at refinecolor.com is marketing; discard.
- Gold optical constants: Johnson and Christy 1974, Phys Rev B 9, 5056 (via refractiveindex.info). Normal-incidence R = ((n-1)^2+k^2)/((n+1)^2+k^2). Search did not return n,k at 450/550/650 nm. My calculation from recalled J&C values gives R about 0.40 / 0.79 / 0.96, UNCHECKED. The Technical Director should look up the table and confirm before trusting these. Not found: measured reflectance of pale-gold hot foil (alloy foil is lower in red than pure Au).
- NOT found: sculpted-die heights in mm, micro-pitting/fill-in imagery, and any spirits-medallion sourcing. Gaps; ask a foil/die vendor.

## Roundel treatment verdict
Current spec (foil on clear film over white underprint, no emboss) is physically a flat print. Real film-label foil is hot or cold foil, flat or very slightly debossed. A genuine embossed raised roundel on clear film is NOT the approved treatment: it would need an applied/metal/embossed-substrate medallion. That is a CHANGE and needs approval.

Options, within foil on film (no change in kind) vs change:
| Option | Within approved foil-on-film? |
|---|---|
| A. Foil stays flat; relief by clear raised UV/tactile varnish under or beside the foil, 30-50 um | Arguably an added embellishment (new process step). Flag, but low risk |
| B. Debossed/stamped foil on film, 10-30 um relief, from the stamping pressure | Within foil on film. No change |
| C. Embossed or domed foil 0.2 mm on film | CHANGE. Flag for approval |
| D. Separate applied metal medallion | CHANGE. Flag |

Recommend B (plus A if the user accepts a varnish step). Believable relief on film is tens of microns, not 0.2 mm.

## Recommendations (all ARTISTIC unless noted)
1. Roundel relief height. Add a Displacement node to mat_roundel: Scale 0.03 mm (B), midlevel 0, Height from MASK-FOIL-01 blurred ~0.05 mm so edges are bevelled. Set displacement_method BOTH, as in mat_label. Keep AVANTE/bird at 0.2 mm (approved). Test: raking-light close render at 15 deg; relief should read as soft edge highlights, not a step.
2. Bevelled edge profile. Blur the height mask by 3-4 px at 4K, then apply a smoothstep (Map Range 0.2-0.8) to mimic a sculpted/bevelled die wall (VERIFIED die concept; width ARTISTIC). Expected: crisp edge highlight with no jagged stairs. Test: macro crop at 100%.
3. Foil micro-structure. Mix in 2 sources: (a) Noise 800 scale, detail 2, drive roughness 0.18 +/-0.04; (b) very weak bump from the underlying paper/film normal, strength 0.05 (foil telegraphs grain only slightly on film; on paper use up to 0.15, agree with the paper specialist). Expected: removes CG-perfect mirror look. Test: compare against a foil macro photograph; reject if sparkles appear.
4. Foil colour/response. Keep F0 (0.95,0.68,0.30) (close to pure-gold linear F0 as commonly quoted; not verified from sources here). Pale-gold alloy: test F0 (0.93,0.72,0.42) plus Metallic 1, F82 tint (0.9,0.8,0.55) if the Blender build exposes edge tint. Anisotropic 0.3 only on stamped flat label; set 0 on roundel (film-laminated foil is not brushed). Test: swatch render vs physical foil swatch under the studio HDRI.
5. Edge fill-in and pits. Multiply the foil mask by a Voronoi-based dropout (scale 1200, threshold ~0.97, 1-3% of area, near edges only), erode mask 0.5 px. Expected: small believable imperfections. Test: shows only in macro; skip if hero shot never exceeds 1:1.

## Overlap to raise
- Paper specialist: grain/normal-map telegraphing through foil on paper (value in #3), and paper surface smoothness vs foil quality.
- Lighting specialist: raking light/strip lights are needed to read 30 um relief; a mirror-flat foil needs gradient reflection sources (soft cards) to avoid reading as flat yellow; and the roundel is transparent, so the backdrop/liquid shows through the film around the print.
- Technical Director: displacement needs dense mesh. The roundel is a 128-segment triangle fan, so subdivide or add adaptive subdivision before applying relief.
