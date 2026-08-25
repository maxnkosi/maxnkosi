import Lenis from 'lenis'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * Wires Lenis and ScrollTrigger together.
 *
 * Call this ONCE, app-level (App.vue setup or a Vue plugin) — never per route
 * component, or each navigation stacks another Lenis instance and RAF loop.
 *
 * Why it matters: Lenis does not move the native scroll position on every
 * frame the way a real scroll does — it interpolates and writes transforms.
 * ScrollTrigger, left alone, keeps listening to native scroll events and ends
 * up reading a position that lags what is painted. The visible result is
 * pinned sections that drift, jump on release, or unpin a few hundred pixels
 * early. Three things have to be true:
 *
 *   1. ScrollTrigger updates on Lenis's scroll callback, not the native event.
 *   2. Lenis is driven by gsap.ticker, so both run on ONE RAF loop in a fixed
 *      order — two independent loops produce a frame of skew that reads as
 *      jitter under a pin.
 *   3. gsap.ticker.lagSmoothing(0) — otherwise GSAP silently clamps delta time
 *      after a slow frame and Lenis's easing desyncs from the scroll position.
 *
 * Dropping any one of these is the usual cause of "ScrollTrigger is broken
 * since we added smooth scrolling".
 */
export function useLenisScrollTrigger(options: ConstructorParameters<typeof Lenis>[0] = {}) {
  const lenis = new Lenis({
    duration: 1.1,
    smoothWheel: true,
    /* Leave touch alone: native momentum beats emulated smoothing on mobile,
       and the rail is not pinned at those widths anyway. */
    ...options,
  })

  // 1. ScrollTrigger reads Lenis's position, not the native scroll event.
  lenis.on('scroll', ScrollTrigger.update)

  // 2. One RAF loop, deterministic order.
  const tick = (time: number) => lenis.raf(time * 1000)
  gsap.ticker.add(tick)

  // 3. No delta-time clamping.
  gsap.ticker.lagSmoothing(0)


  const destroy = () => {
    lenis.off('scroll', ScrollTrigger.update)
    gsap.ticker.remove(tick)
    gsap.ticker.lagSmoothing(500, 33) // restore the GSAP default
    lenis.destroy()
  }

  return { lenis, destroy }
}
