# MX-001 · Phase A · Identity-card explorations (MXI-001)

Author: Claude Code · Date: 2026-11-01 SAST · Version: v0.1 · Approval state: **PROPOSED — nothing approved, nothing published**

Static HTML concept prototypes (no build step, no external requests). Serve locally: `python3 -m http.server` in this folder, open the files. They must be served over http — `file://` blocks the font stylesheet in Chromium.

| MXE | Direction | File | Functional vs conceptual |
|---|---|---|---|
| MXE-002 | A · Futuristic credential | `a-credential.html` | Functional: pointer tilt, flip (button/click), inert back face, reduced-motion. Conceptual: material finish, chip, MRZ line is decorative. |
| MXE-003 | B · Precision instrument | `b-instrument.html` | Functional: 4-node/6-link relationship graph, keys 1–4, hover/focus/click highlight, live readout. Conceptual: finish, scale rulers. |
| MXE-004 | C · Experimental digital identity | `c-digital-identity.html` | Functional: generated ASCII field (4 modes), pointer-reactive, variable-font axis on the name. Conceptual: how it sits in a full page. |

All names/values are placeholders. No client, employer or result claims appear.

## Typography and licence check

| Face | Role | Licence | Status |
|---|---|---|---|
| Iosevka | mono (A, B, labels) | SIL OFL 1.1 — licence file in `fonts/` (from the fontsource package) | Verified in package; usable incl. web embedding. Stock woff2 is ~1 MB per weight → **must subset** for production. |
| Recursive (variable, MONO/CASL/slnt/wght) | mono + variable axes (C) | SIL OFL 1.1 — `fonts/` | Verified in package. 305 KB full variable file; subset/limit axes for production. |
| Instrument Sans (variable) | proportional display/body (all) | SIL OFL 1.1 — `fonts/` | Verified in package. 30 KB. One candidate only; display face is not yet decided. |
| Berkeley Mono | not used | Commercial, paid licence (US Graphics Company) | **Not verified this session** (no live licence page read) and not installed. Using it needs a purchase = expense → owner approval, plus a check that the licence covers self-hosted web fonts. |
| Geist Mono | excluded | — | Per brief. |

## Direction briefs

### A · Futuristic credential
- Composition: ISO ID-1 ratio (1.586) card; name large, title in accent mono, 2-line MRZ-style ASCII footer; four `+` registration marks; chip grid. Back face lists four disciplines as keyed slots `[■□□□]`.
- Type: Instrument Sans display + Iosevka micro-labels.
- ASCII rules: only structural — registration `+`, `<` filler, `[■□]` slots. Never decorative art. Uppercase mono only for metadata.
- Microinteraction: ≤9° pointer tilt with moving highlight (rAF-throttled); flip on click/button.
- Mobile: no tilt (hover:none), flip button ≥44 px.
- Accessibility: hidden face is `inert` + `aria-hidden`; visible text real HTML; reduced motion → no tilt, no flip animation (verified transition 0s).
- Performance: CSS transforms only; ~1.5 KB JS.
- Feasibility: high. Risk: reads as "credit card / sci-fi badge" — most familiar, least tied to the generalist thesis.

### B · Precision scientific instrument
- Composition: light instrument panel; header rule; tick-ruler ASCII bands; central 4-node/6-link SVG graph (Digital, Experience, Physical, Systems = every pairing linked); boxed readout.
- Type: Instrument Sans name + Iosevka for all instrument text.
- ASCII rules: rulers `|····|` and readout labels only; no pictures.
- Microinteraction: select a node (click, Enter/Space, or key 1–4) → its 3 links light, readout states what it links to. Hover previews on pointer devices.
- Mobile: graph scales; labels moved above nodes after a clipping bug found in testing (fixed). Tap = select.
- Accessibility: nodes are focusable buttons with `aria-pressed` and labels starting with visible text; readout is `role=status`. Accent darkened after axe contrast failure.
- Performance: ~2 KB JS, SVG only.
- Feasibility: high. Risk: lowest "wow" and least personality (≈ well over 70/30 technical); needs one extraordinary detail added.

### C · Experimental digital identity
- Composition: near-black card; generated ASCII field above a large name; four discipline buttons switch the field's structure (grid interference / solid mass / lattice / waves) — each a function of the discipline, seeded from the name.
- Type: Recursive for the field and name (variable axes MONO/CASL/slnt/wght respond to pointer position), Iosevka labels, Instrument Sans body.
- ASCII rules: density ramp ` .·:-=+*#%@` only; field is `aria-hidden`; real text always in HTML.
- Microinteraction: pointer lens raises density and shifts name weight/casual/slant; buttons morph field. Updates only on pointer events.
- Mobile: columns computed from width (re-measured each draw); buttons wrap; no hover dependence.
- Accessibility: field decorative; buttons `aria-pressed`; reduced motion → pointer response disabled, static field.
- Performance: ~600 cells string write per event, rAF-coalesced; layout measure each draw (could be cached). Needs Recursive subset.
- Feasibility: medium-high. Risk: closest to "terminal cosplay" if the field becomes the whole identity; highest ongoing tuning cost; field currently carries no evidence.

## Comparison (my assessment — subjective, not user-tested)

| Criterion | A | B | C |
|---|---|---|---|
| Simplicity | ● | ● | ◐ |
| Originality | ◐ | ◐ | ● |
| Hierarchy | ● | ● | ◐ |
| Visual detail | ● | ◐ | ● |
| Responsiveness | ● | ● | ◐ |
| Feasible interaction | ● | ● | ◐ |
| Supports "how they connect" thesis | ○ | ● | ◐ |
| Personality (30%) | ◐ | ○ | ● |

## Recommendation (for owner decision — MXD-001)
**B as the structural base**, because it is the only direction that *shows* the generalist claim (every discipline linked to every other) with plain, keyboard-first, fast markup. Unresolved: it needs one extraordinary detail and more personality; candidates are C's generated field as a quiet background texture, or A's reverse-face idea as a "case file" state. Those are options for the owner, not decisions.

## Tests actually run (2026-11-01, Chromium via Playwright, local http server)
- axe-core 4.x: 0 violations on A, B, C (desktop). Initial B run had 3 (contrast, label-content-name-mismatch, no h1) → fixed and re-run clean.
- No console/page errors on all three.
- Screenshots: desktop 1280×800, mobile 390×844, reduced-motion 390×844, plus interaction states. @2x in `shots/`.
- A: back face `inert` state confirmed; reduced-motion transition = 0s. B: key `3` selects Physical, readout correct.
- Load: DCL 35–45 ms, load 140–190 ms on localhost (not a real-network measure).

## Not done / limitations
- No real-device, screen-reader (VoiceOver/NVDA/TalkBack), or keyboard-only manual testing; axe catches only part of WCAG.
- No Figma file (Figma MCP failed to connect this session), no Lighthouse run, no cross-browser (Chromium only).
- Fonts bundled are unsubsetted; production weights not measured.
- Dark/light variants not explored per direction. No full-page context, navigation or work evidence yet.
- Nothing published, deployed or purchased.
