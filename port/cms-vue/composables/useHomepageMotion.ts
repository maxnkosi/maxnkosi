import { onMounted, onBeforeUnmount, ref, type Ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * Breakpoint below which the practice-area rail is NOT pinned and falls back to
 * a native scroll-snapping strip. Must stay in step with the matching media
 * query in styles/ww-homepage.scss.
 */
const PIN_QUERY = '(min-width: 761px) and (not ((pointer: coarse) and (max-width: 1024px)))'

const EASE = 'power3.out' // approximates the design's cubic-bezier(0.16, 1, 0.3, 1)

export function useHomepageMotion(root: Ref<HTMLElement | null>) {
  const counter = ref('01 / 04')
  let ctx: gsap.Context | undefined

  onMounted(() => {
    /* Reveal targets are hidden by `.js [data-reveal]`; without this class a
       failed bundle would leave the page blank rather than merely static. */
    document.documentElement.classList.add('js')

    ctx = gsap.context((self) => {
      const q = self.selector as (s: string) => HTMLElement[]
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      /* ---------------------------------------------------------------
         Reveal on scroll
         --------------------------------------------------------------- */
      const reveals = q('[data-reveal]')
      if (prefersReduced) {
        gsap.set(reveals, { opacity: 1, y: 0 })
      } else {
        reveals.forEach((el) => {
          const y = parseFloat(getComputedStyle(el).getPropertyValue('--rv-y')) || 24
          const dur = (parseFloat(getComputedStyle(el).getPropertyValue('--rv-dur')) || 1000) / 1000
          const delay = (parseFloat(getComputedStyle(el).getPropertyValue('--rv-delay')) || 0) / 1000
          gsap.fromTo(
            el,
            { opacity: 0, y },
            {
              opacity: 1,
              y: 0,
              duration: dur,
              delay,
              ease: EASE,
              scrollTrigger: { trigger: el, start: 'top 88%', once: true },
            },
          )
        })
      }

      if (prefersReduced) return

      /* ---------------------------------------------------------------
         Hero image — drifts up and scales as the hero leaves
         --------------------------------------------------------------- */
      const heroImg = q('[data-hero-img]')[0]
      const hero = q('[data-hero]')[0]
      if (heroImg && hero) {
        gsap.fromTo(
          heroImg,
          { yPercent: 0, scale: 1 },
          {
            yPercent: -7,
            scale: 1.06,
            ease: 'none',
            scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true },
          },
        )
      }

      /* ---------------------------------------------------------------
         Generic parallax
         Mirrors the static build's (elementCentre - viewportCentre) * rate.
         --------------------------------------------------------------- */
      q('[data-parallax]').forEach((el) => {
        const rate = parseFloat(el.dataset.parallax || '0')
        if (!rate) return
        const travel = () => ((window.innerHeight + el.offsetHeight) / 2) * rate
        gsap.fromTo(
          el,
          { y: travel },
          {
            y: () => -travel(),
            ease: 'none',
            scrollTrigger: {
              trigger: el,
              start: 'top bottom',
              end: 'bottom top',
              scrub: true,
              invalidateOnRefresh: true,
            },
          },
        )
      })

      /* ---------------------------------------------------------------
         Specialist rail — drag to scroll
         --------------------------------------------------------------- */
      const rail = q('[data-rail]')[0]
      if (rail) {
        let down = false
        let moved = false
        let startX = 0
        let startScroll = 0

        const onDown = (e: PointerEvent) => {
          down = true
          moved = false
          startX = e.clientX
          startScroll = rail.scrollLeft
        }
        const onMove = (e: PointerEvent) => {
          if (!down) return
          const dx = e.clientX - startX
          if (!moved && Math.abs(dx) > 4) {
            moved = true
            rail.classList.add('is-dragging')
          }
          if (moved) {
            e.preventDefault()
            rail.scrollLeft = startScroll - dx * 1.2
          }
        }
        const endDrag = () => {
          down = false
          rail.classList.remove('is-dragging')
        }
        /* A drag must not fire the click on whatever sat under the cursor. */
        const onClick = (e: MouseEvent) => {
          if (moved) { e.preventDefault(); e.stopPropagation() }
        }

        rail.addEventListener('pointerdown', onDown)
        rail.addEventListener('pointermove', onMove)
        rail.addEventListener('click', onClick, true)
        window.addEventListener('pointerup', endDrag)
        window.addEventListener('pointercancel', endDrag)

        self.add(() => {
          rail.removeEventListener('pointerdown', onDown)
          rail.removeEventListener('pointermove', onMove)
          rail.removeEventListener('click', onClick, true)
          window.removeEventListener('pointerup', endDrag)
          window.removeEventListener('pointercancel', endDrag)
        })
      }

      /* ---------------------------------------------------------------
         Header — scrim solidifies, then retracts on downward scroll
         --------------------------------------------------------------- */
      const nav = q('[data-nav]')[0]
      if (nav) {
        ScrollTrigger.create({
          start: 80,
          end: 'max',
          onToggle: (self) => nav.classList.toggle('is-scrolled', self.isActive),
        })
        ScrollTrigger.create({
          start: () => window.innerHeight * 1.5,
          end: 'max',
          invalidateOnRefresh: true,
          onUpdate: (self) => nav.classList.toggle('is-hidden', self.direction === 1),
          onLeaveBack: () => nav.classList.remove('is-hidden'),
        })
      }

      /* ---------------------------------------------------------------
         Practice areas — pinned horizontal rail
         Pinned only above PIN_QUERY; matchMedia reverts cleanly on resize.
         --------------------------------------------------------------- */
      const mm = gsap.matchMedia()
      mm.add(PIN_QUERY, () => {
        const section = q('[data-services]')[0]
        const sticky = q('[data-services-sticky]')[0]
        const track = q('[data-services-track]')[0]
        if (!section || !sticky || !track) return

        const distance = () => Math.max(0, track.scrollWidth - window.innerWidth)

        const tween = gsap.to(track, {
          x: () => -distance(),
          ease: 'none',
          scrollTrigger: {
            trigger: section,
            pin: sticky,
            /* A numeric scrub smooths the Lenis-driven scroll position; `true`
               couples 1:1 and reads as jittery under smooth scrolling. */
            scrub: 1,
            start: 'top top',
            end: () => '+=' + distance(),
            invalidateOnRefresh: true,
            anticipatePin: 1,
            onUpdate: (self) => {
              const n = Math.min(4, Math.floor(self.progress * 3.999) + 1)
              counter.value = '0' + n + ' / 04'
            },
          },
        })

        return () => {
          tween.scrollTrigger?.kill()
          tween.kill()
          gsap.set(track, { clearProps: 'x' })
        }
      })

      /* Below the pin breakpoint the counter follows native scroll instead. */
      mm.add(`(not (${PIN_QUERY}))`, () => {
        const track = q('[data-services-track]')[0]
        if (!track) return
        const onScroll = () => {
          const max = track.scrollWidth - track.clientWidth
          const p = max > 0 ? track.scrollLeft / max : 0
          counter.value = '0' + Math.min(4, Math.floor(p * 3.999) + 1) + ' / 04'
        }
        track.addEventListener('scroll', onScroll, { passive: true })
        return () => track.removeEventListener('scroll', onScroll)
      })
    }, root)

    /* Images resolve after mount and change layout height; without this the
       pin end position is computed against a stale page height. */
    ScrollTrigger.refresh()
  })

  onBeforeUnmount(() => {
    /* revert() kills every trigger, tween and matchMedia scope created above
       and restores inline styles — required, or navigating away from the route
       leaves orphaned pin spacers behind. */
    ctx?.revert()
  })

  return { counter }
}
