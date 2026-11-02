# Agent 5: Shrink capsule and closure research

Evidence is thin. Searches returned mostly supplier and retail pages. I found no independent measurements of gloss, seam width or wrinkle size. Numbers below marked ARTISTIC are my own judgement, to be tuned against reference photos the TD supplies. Nothing is invented as sourced.

## VERIFIED (source-backed)
1. Materials. PVC is described as cheaper and easier to shrink (about 90-100 C). PETG is described as clearer, halogen-free and needing tighter tunnel control (supplier figure 210-225 C, unverified). Sources disagree on which grips complex shapes better. Metallised PET and composite constructions are used for premium spirits. I found no direct comparison with polylaminate.
   https://www.printweek.in/features/breaking-the-myth-between-pvc-and-petg-53764
   https://jfpackfilm.pages.dev/articles/petg-vs-pvc-shrink-film/
   https://www.packworld.com/news/sustainability/article/13333685/wine-bottles-go-green-for-europe
2. Tear strip. Retail capsules place it about 14-16 mm below the cap top. A European patent describes a strip that separates head from skirt, plus a second strip along the skirt. A US patent describes a weakened circular break line.
   https://creopack.se/en/products/krymphatta-34x27mm
   https://data.epo.org/gpi/EP3423368B1
   https://patents.justia.com/patent/5654022
3. Wrinkles. Reviews say wrinkles come from uneven heat and are shrunk out. A patent exists for pleats to prevent sleeve wrinkling, but I saw no detail.
   https://patents.google.com/patent/CA1080666A/en
4. The National Resources and Cosmo Films pages I fetched gave no gloss, thickness or seam data.

NOT FOUND: top-disc crimp or pleat geometry, seam overlap width, how film bridges a cap-to-neck recess. Treat everything below as ARTISTIC.

## ARTISTIC recommendations (physically reasoned, unsourced numbers)

**R1. Bridge the recess; do not follow the step.** Film is under tension, so it spans concave transitions in a gentle arc and only hugs convex ones. In capsule_r, replace the hard steps at CAP_TOP-14.8 (r 20.9) and CAP_TOP-23.0 (r 17.8) with a smooth blend. Use a smoothstep over about 3 mm on the convex head-to-band step, and a bridging taper over 6-8 mm where the band meets the neck or shoulder. Add a concave bridge radius of about 5 mm, so the film leaves the head edge tangentially. Expected result: kills the 60 deg stepped look and reads as a membrane. Test: front and side silhouette render at 85 mm, compare with a reference photo.

**R2. Material.** Navy PETG, glossy but not moulded. Roughness 0.20-0.28 (from 0.14), coat 0.3 and coat roughness 0.12. Add a faint sheen from a micro-noise bump (scale 0.3 mm, strength 0.01) that breaks the mirror uniformity. Film thickness 0.05 mm is reasonable; keep it. Expected: it reads as stretched film, not injection moulding. Test: A/B turntable still under the existing HDRI.

**R3. Vertical seam.** One overlap seam at the back, away from the hero angle. Width 2.0 mm, raised 0.06 mm step (ridge, rounded). Add as a displacement strip or a bump band in theta at about 160-200 deg, roughness +0.05 inside the seam. Expected: removes the "perfect CG cylinder" tell. Test: back-three-quarter view only.

**R4. Subtle shrink wrinkles.** Only on skirt and the bridging zone. Amplitude 0.04-0.08 mm, vertical wavelength about 3-5 mm in theta (roughly 30 to 40 pleats around the head), fading to zero by the skirt hem and over the cap head. Use bump or normal map, not geometry. Keep amplitude low so it reads as real, not damaged. Test: render at 2x zoom on the shoulder, compare against supplier photography.

**R5. Top disc.** Add a faint crimped rim: radial pleats of 0.05 mm amplitude and about 1.5 mm wavelength on the outer 2 mm fillet only, with the disc itself flat and slightly lower roughness. Test: top-down view.

**R6. Pinline.** Gold ink at the skirt edge: keep Metallic 0.85, drop roughness to 0.25 for a clean foil read, and finish with a 0.2 mm edge-rolled hem (round, not razor) at 66.3 mm. Test: macro at the hem.

## Overlap to raise with the lighting specialist
Gloss and rim lighting decide whether the wrinkles and seam read at all. Seam, wrinkle and top-disc bump are highlight-dependent, so softbox size and strip-light placement must be agreed. Also check the neck collar contact shadow where it overlaps the skirt, and any reflection of the roughness change on the pinline.
