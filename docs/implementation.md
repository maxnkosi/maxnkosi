# WW Homepage B — implementation notes

A static implementation of the Claude Design file `WW Homepage B.dc.html`.
The design source is kept verbatim at `design/WW Homepage B.dc.html`.

## Layout

```
index.html              markup
assets/css/site.css     tokens + all component styles
assets/js/site.js       scroll-driven motion, compact menu, theme API
assets/fonts/           LT Remark (display), General Sans (body)
assets/opt/             photographic assets — see ASSETS.md
design/                 the .dc.html source this was built from
```

No build step and no dependencies. Open `index.html`, or serve the folder:

```sh
python3 -m http.server 8000
```

## What changed from the design source

The `.dc.html` format is a design-canvas document: a `<x-dc>` template with
`{{ }}` bindings and `ref=` attributes, driven by a `DCLogic` React component
and the `support.js` runtime. None of that survives into production, so:

- **Inline styles → stylesheet.** Every value (colour, `clamp()`, easing,
  duration, delay) is carried across unchanged; they now live in classes and
  tokens instead of `style=` attributes.
- **`style-hover="…"` → real `:hover` rules.** The runtime implemented hover
  by attaching JS listeners; the same states are now plain CSS, including the
  card zoom, news-row thumbnail reveal, panel dimming and portrait expansion.
- **`ref="{{ … }}"` → `id` / `data-` hooks.** `assets/js/site.js` is a single
  IIFE with no framework.
- **Reveal-on-scroll** keeps the same `IntersectionObserver` thresholds
  (`rootMargin: 0px 0px -12% 0px`, `threshold: 0.08`); per-element distance,
  duration and delay are expressed as `--rv-y` / `--rv-dur` / `--rv-delay`.

## Motion

`assets/js/site.js` runs one `requestAnimationFrame`-throttled scroll handler
that drives all four scroll effects, matching the design's maths exactly:

| Effect | Behaviour |
| --- | --- |
| Header | Scrim solidifies past `80px`; header retracts past `1.5 × viewport` while scrolling down |
| Hero image | `translateY(progress × -7%)` and `scale(1 + progress × 0.06)` |
| Services | 400vh pinned section; the track translates by `progress × (trackWidth − viewportWidth)`, counter steps `01 → 04` |
| Parallax | `[data-parallax]` offsets by `(elementCentre − viewportCentre) × rate` |

## Theme options

The design exposed three "Feel" props. They are preserved as document
attributes plus a CSS custom property, defaulting to the design's defaults:

```html
<html data-nav-chrome="progressive-blur" data-image-mood="editorial-colour">
```

- `data-nav-chrome` — `progressive-blur` (default) | `solid-blur` | `hairline`
- `data-image-mood` — `editorial-colour` (default) | `duotone-ink` | `muted-archive`
- `--accent` — `#316391` (default); the design also offered `#DE6947`,
  `#667E24`, `#64231A`

They can be changed at runtime with the design's own option labels:

```js
WW.setTheme({ accent: '#DE6947', navChrome: 'Hairline', imageMood: 'Duotone ink' });
```

## Deviations, and why

Three places depart from a literal transcription. Everything else is faithful.

1. **The pinned rail flattens on small and touch viewports.** A 400vh
   scroll-jacked section with a `position: sticky` child is unreliable on
   mobile browsers with dynamic toolbars. Below 760px (and on coarse pointers
   under 1024px) the section becomes a normal scroll-snapping horizontal
   strip; the counter then tracks native scroll instead. The desktop
   behaviour is unchanged.
2. **Accessibility additions.** A skip link, a labelled hero input, real
   `<button>`s for the hero carousel arrows, `aria-expanded` / `aria-controls`
   on the menu trigger, focus handling when the overlay opens and closes, and
   visible focus rings. The design had none of these; they change no visuals.
3. **Missing-asset fallback.** Images that 404 resolve to a tonal block
   instead of a broken-image glyph — see `ASSETS.md`.

## Two content defects carried over from the design

Both are reproduced verbatim rather than silently rewritten, because the
correct copy is a content decision:

- **The hero standfirst is truncated.** It reads
  *"From fund formation to downstream M&A and transactional tax across
  Africa.cused on results."* — "Africa.cused" is clearly a mangled join, but
  the intended sentence is not recoverable from the design.
- **All four practice-area panels share one title and body.** Every panel
  reads *"Corporate & Mergers and Acquisitions (M&A)"* with identical copy;
  only the number and image differ. The section is built for four distinct
  practice areas and needs three more sets of copy.
