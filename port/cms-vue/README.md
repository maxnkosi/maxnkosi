# WW Homepage B → `cms-vue`

A port of the static implementation (`/index.html`) to a Vue 3.5 SFC using the
project's GSAP 3.15 + ScrollTrigger + Lenis stack instead of the hand-rolled
`requestAnimationFrame` handler.

Staged here because the `cms-vue` repository is not attached to this session.
Drop the four files into the app and delete this directory.

```
components/WwHomepage.vue              → src/components/ (or views/)
composables/useHomepageMotion.ts       → src/composables/
composables/useLenisScrollTrigger.ts   → src/composables/
styles/ww-homepage.scss                → src/styles/
```

Assets go to `public/assets/**` (logos, `fonts/`, `opt/`), so they serve
verbatim at base `/`. The component resolves them through
`import.meta.env.BASE_URL`. 18 photographs are still missing — see `/ASSETS.md`.

## Wiring

`useLenisScrollTrigger()` is **app-level**. Call it once in `App.vue`, never in
a route component — each call otherwise stacks another Lenis instance and RAF
loop on every navigation.

```ts
// App.vue
import { onBeforeUnmount } from 'vue'
import { useLenisScrollTrigger } from '@/composables/useLenisScrollTrigger'

const { destroy } = useLenisScrollTrigger()
onBeforeUnmount(destroy)
```

Verified with `vue-tsc --noEmit` under `strict` + `noUnusedLocals`
(clean) and `vite build` (clean).

## The Lenis / ScrollTrigger integration

This is the most likely cause of a pinned section that drifts, jitters, jumps
on release, or unpins early once smooth scrolling is switched on. Lenis does
not advance native scroll position frame by frame — it interpolates and writes
transforms. ScrollTrigger, left to its own devices, keeps reading native scroll
and ends up a frame or more behind what is painted.

Three things all have to be true, and dropping any one reproduces the symptom:

1. **`lenis.on('scroll', ScrollTrigger.update)`** — ScrollTrigger updates from
   Lenis's position, not the native scroll event.
2. **`gsap.ticker.add((t) => lenis.raf(t * 1000))`** — one RAF loop in a fixed
   order. Two independent loops (a bare `requestAnimationFrame(raf)` alongside
   GSAP's ticker) produce a frame of skew that reads as jitter under a pin.
3. **`gsap.ticker.lagSmoothing(0)`** — otherwise GSAP clamps delta time after a
   slow frame and Lenis's easing silently desyncs from scroll position.

`useLenisScrollTrigger.ts` does all three plus a `scrollerProxy` so programmatic
scrolling and anchor jumps go through Lenis rather than fighting it.

Two further things worth checking in the existing code, both of which produce
similar symptoms and neither of which is a Lenis problem:

- **Missing cleanup.** ScrollTrigger instances survive route changes unless
  reverted. `useHomepageMotion` scopes everything to a `gsap.context()` and
  calls `ctx.revert()` on unmount; without that, orphaned pin spacers
  accumulate and later triggers measure against a wrong page height.
- **Stale measurements.** Pin `end` values computed before images load are
  wrong. The composable calls `ScrollTrigger.refresh()` after mount and sets
  `invalidateOnRefresh: true` on every scrubbed trigger.

## What changed from the static build

| | Static | This port |
| --- | --- | --- |
| Pinned rail | `height: 400vh` + `position: sticky` + manual transform | `ScrollTrigger` `pin` + `scrub: 1`; the scaffold is gone, ScrollTrigger injects its own spacer |
| Responsive pin | CSS media query | `gsap.matchMedia()` — reverts cleanly on resize |
| Reveals | CSS transitions + `IntersectionObserver` | `gsap.fromTo` + ScrollTrigger, reading `--rv-*` tokens from CSS |
| Parallax / hero | manual rAF maths | scrubbed tweens, `invalidateOnRefresh` |
| Repeated markup | hand-written | `v-for` over data arrays |
| Menu | class toggling | `v-show` + `menuOpen` ref |

`scrub: 1` rather than `true` is deliberate: a 1:1 couple reads as jittery under
smooth scrolling, and the slight catch-up matches the design's easing.

## Still open

- **Copy defects carried over from the design**, unchanged and flagged in the
  source: the hero standfirst is truncated (`"…across Africa.cused on
  results."`), and all four practice-area panels share one title and body. The
  panel copy sits in a single `PANEL_COPY` constant so the duplication is
  obvious; three more sets are needed.
- **Bootstrap.** The design is bespoke, so this ships its own SCSS rather than
  `bootstrap-vue-next` components. Nothing here collides with Bootstrap, but it
  does not use it either.
- **Not yet run against the real app** — no `cms-vue` in this session, so this
  is typechecked and built in isolation, not rendered in the router.
