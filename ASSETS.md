# Assets

Source: Claude Design project **“Mobbin reference and form inputs”**
(`cc47ec9e-5c87-4009-9620-092c65bc4337`), file `WW Homepage B.dc.html`.
A copy of the design source is kept at `design/WW Homepage B.dc.html`.

## Present in this repo

| File | Notes |
| --- | --- |
| `assets/logo-black.svg` | Wordmark, ink |
| `assets/logo-white.svg` | Wordmark, paper (footer watermark) |
| `assets/fonts/GeneralSans-Regular.otf` | Body face |
| `assets/fonts/LTRemark-Regular.otf` | Display face |
| `assets/opt/thumb-abstract-2.png` | News row 1 hover thumb |
| `assets/opt/thumb-heritage-1.png` | News row 2 hover thumb |
| `assets/opt/thumb-heritage-3.png` | News row 3 hover thumb |

## Still to be added

The 18 photographic assets below could **not** be pulled from the design
project: the design tool's file-read API caps a single file at 256 KiB and
each of these exceeds it, so every fetch came back truncated (an unusable
partial PNG). They need to be exported from the Claude Design project
directly — open the project, download the file, and drop it at the path
below. No markup or CSS changes are needed; the paths already match.

| Path | Used by |
| --- | --- |
| `assets/opt/sa-17.png` | Hero image |
| `assets/opt/heritage-11.png` | About, tall figure (parallax `0.05`) |
| `assets/opt/heritage-8.png` | About, end figure (parallax `-0.05`) |
| `assets/opt/sector-mining.png` | Services panel 01 |
| `assets/opt/sector-energy.png` | Services panel 02 |
| `assets/opt/sector-transport.png` | Services panel 03 |
| `assets/opt/sector-agri.png` | Services panel 04 |
| `assets/opt/head-1.png` … `head-7.png` | Specialist rail (7 portraits) |
| `assets/opt/sa-13.png` | Podcast background (parallax `0.06`) |
| `assets/opt/sa-9.png` | Insights card 1 |
| `assets/opt/kenya-1.png` | Insights card 2 |
| `assets/opt/heritage-5.png` | Insights card 3 |

Until they are added, each missing image resolves to a tonal block in the
palette rather than a broken-image glyph — `assets/js/site.js` flags the
failure and `.is-missing-media` in `assets/css/site.css` paints the
placeholder. Dropping the real files in makes the fallback disappear on its
own.

## Font licensing

`GeneralSans-Regular.otf` (Indian Type Foundry) is distributed through
Fontshare for personal and commercial use. **`LTRemark-Regular.otf` is a
commercial Linotype face** — check that the licence covers web embedding and
public redistribution before this repository is made public, and swap in a
licensed webfont build if it does not. The display face is referenced only
via the `--font-display` token in `assets/css/site.css`, so replacing it is a
one-line change.
