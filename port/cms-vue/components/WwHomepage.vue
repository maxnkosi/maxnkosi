<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useHomepageMotion } from '../composables/useHomepageMotion'
import '../styles/ww-homepage.scss'

const root = ref<HTMLElement | null>(null)
const menuOpen = ref(false)
const { counter } = useHomepageMotion(root)

/* Escape has to be listened for at the window: the overlay is a plain <div>,
   so it never receives key events itself. */
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') menuOpen.value = false
}
/* Crossing the desktop breakpoint hides the toggle button; without this the
   overlay would be stranded open with no way to close it. */
function onResize() {
  if (window.innerWidth >= 1180) menuOpen.value = false
}
onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onResize)
  document.body.style.overflow = ''
})
watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

/** Assets live in `public/assets/**` so they are served verbatim at base `/`. */
const asset = (p: string) => `${import.meta.env.BASE_URL}assets/${p}`

const navLinks = [
  { label: 'Services', href: '#services' },
  { label: 'Sectors', href: '#sectors' },
  { label: 'News', href: '#news' },
  { label: 'Fusion', href: '#', muted: true },
  { label: 'Careers', href: '#' },
  { label: 'Diversity & Inclusion', href: '#' },
  { label: 'About', href: '#about' },
  { label: 'Contact', href: '#' },
]

const heroTags = ['Expertise', 'Industry', 'Country', 'Matter', 'Insights', 'Events']

/* NOTE: all four panels carry identical copy in the source design — only the
   number and image differ. Three more sets of copy are still needed. */
const PANEL_COPY =
  'We advise on complex transactions across the full deal lifecycle — from structuring and negotiation to execution and integration. Our team supports listed companies, private equity firms, and growing businesses in delivering transactions that create long-term value.'

const panels = [
  { num: '01', img: 'opt/sector-mining.png', alt: 'Mining landscape', title: 'Corporate & Mergers and Acquisitions (M&A)', body: PANEL_COPY },
  { num: '02', img: 'opt/sector-energy.png', alt: 'Wind turbine on the coast', title: 'Corporate & Mergers and Acquisitions (M&A)', body: PANEL_COPY },
  { num: '03', img: 'opt/sector-transport.png', alt: 'Elevated transport structure', title: 'Corporate & Mergers and Acquisitions (M&A)', body: PANEL_COPY },
  { num: '04', img: 'opt/sector-agri.png', alt: 'Contour-farmed fields', title: 'Corporate & Mergers and Acquisitions (M&A)', body: PANEL_COPY, id: 'sectors' },
]

const portraits = ['head-4', 'head-1', 'head-3', 'head-2', 'head-6', 'head-5', 'head-7']

const insights = [
  { img: 'opt/sa-9.png', alt: 'Coastal stadium', title: 'CSI Annual Report - FY 2024/2025' },
  { img: 'opt/kenya-1.png', alt: 'Aerial waterway', title: 'Webber Wentzel Water Infrastructure Projects' },
  { img: 'opt/heritage-5.png', alt: 'Painted facade', title: 'Linklaters Global Guide: Public M&A 2025 (SA chapter)' },
]

const news = [
  { tags: ['Business', 'Retail'], title: 'Who owns an AI\'s "masterpiece"? - The South African reality', date: '12 Jan, 2026', thumb: 'opt/thumb-abstract-2.png', alt: 'Abstract form' },
  { tags: ['Business', 'Retail'], title: 'Grief without a psychiatric injury: Why emotional distress alone cannot ground a damages claim', date: '12 Jan, 2026', thumb: 'opt/thumb-heritage-1.png', alt: 'Balanced rock formation' },
  { tags: ['Business', 'Retail'], title: 'AI walks into an arbitration: What could go wrong?', date: '12 Jan, 2026', thumb: 'opt/thumb-heritage-3.png', alt: 'Cooling towers' },
]

const footerCols = [
  [
    { label: 'Find Specialist', href: '#specialists' },
    { label: 'Services', href: '#services' },
    { label: 'News', href: '#news' },
    { label: 'Careers', href: '#' },
  ],
  [
    { label: 'Client Portal', href: '#' },
    { label: 'About Us', href: '#about' },
    { label: 'Diversity & Inclusion', href: '#' },
    { label: 'Contact Us', href: '#' },
  ],
]

const legalLinks = ['Tip-Offs Hotline', 'Terms of Business', 'Privacy Policy', 'Terms of Use', 'PAIA Manual', 'Sitemap']

/** Missing photography degrades to a tonal block rather than a broken glyph. */
function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.classList.add('is-missing')
  img
    .closest('.card__media, .panel__media, .portrait, .about__figure, .hero__img, .podcast__bg, .row__thumb')
    ?.classList.add('is-missing-media')
}
</script>

<template>
  <div ref="root" class="page">
    <a class="skip-link" href="#main">Skip to content</a>

    <header data-nav class="nav">
      <div class="nav__blur" aria-hidden="true">
        <div class="nav__blur-layer nav__blur-layer--1" />
        <div class="nav__blur-layer nav__blur-layer--2" />
        <div class="nav__blur-layer nav__blur-layer--3" />
        <div class="nav__blur-layer nav__blur-layer--4" />
        <div class="nav__scrim" />
      </div>
      <div class="nav__inner">
        <a class="nav__logo" href="/" aria-label="Webber Wentzel — home">
          <img :src="asset('logo-black.svg')" alt="Webber Wentzel" decoding="sync" >
        </a>
        <nav class="nav__links" aria-label="Primary">
          <a v-for="l in navLinks" :key="l.label" :href="l.href" :class="{ 'is-muted': l.muted }">{{ l.label }}</a>
        </nav>
        <div class="nav__util">
          <a href="#">Client Portal</a>
          <a href="#">Alumni</a>
          <a class="btn-outline" href="#specialists">Find a Specialist</a>
        </div>
        <button
          class="nav__menu" type="button"
          aria-controls="mobile-menu" :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          Menu
          <span class="nav__menu-icon" aria-hidden="true"><span /><span /></span>
        </button>
      </div>
    </header>

    <div v-show="menuOpen" id="mobile-menu" class="menu">
      <div class="menu__top">
        <img :src="asset('logo-black.svg')" alt="Webber Wentzel" >
        <button class="menu__close" type="button" aria-label="Close menu" @click="menuOpen = false">Close</button>
      </div>
      <nav class="menu__nav" aria-label="Mobile">
        <a
          v-for="l in navLinks" :key="l.label" :href="l.href"
          :class="{ 'is-muted': l.muted }" @click="menuOpen = false"
        >{{ l.label }}</a>
      </nav>
      <div class="menu__foot">
        <div class="menu__util">
          <a href="#" @click="menuOpen = false">Client Portal</a>
          <a href="#" @click="menuOpen = false">Alumni</a>
        </div>
        <a class="menu__cta" href="#specialists" @click="menuOpen = false">
          Find a Specialist <span class="rule" aria-hidden="true" />
        </a>
      </div>
    </div>

    <main id="main">
      <section data-hero class="hero">
        <div class="hero__col">
          <!-- Copy is truncated in the source design ("Africa.cused"); left verbatim. -->
          <p class="hero__eyebrow" data-reveal>
            From fund formation to downstream M&amp;A and transactional tax across Africa.cused on results.
          </p>
          <h1 class="hero__title" data-reveal>Your Partner in African Private Equity</h1>
          <div class="hero__search" data-reveal>
            <div class="hero__field">
              <label class="sr-only" for="hero-input">Describe your challenge</label>
              <input id="hero-input" type="text" placeholder="Describe your challenge..." >
              <span class="hero__go" aria-hidden="true">&rarr;</span>
            </div>
            <div class="hero__tags"><span v-for="t in heroTags" :key="t">{{ t }}</span></div>
          </div>
        </div>

        <div class="hero__media">
          <div data-hero-img class="hero__img">
            <img :src="asset('opt/sa-17.png')" alt="Cantilevered building in grassland" fetchpriority="high" @error="onImgError" >
          </div>
          <div class="hero__caption">
            <h2>Webber Wentzel leads in assisting clients</h2>
            <div class="hero__caption-rule" />
            <div class="hero__caption-row">
              <p>Navigating global, regional, and local Business and Human Rights regulations and integrating human rights into their business models.</p>
              <div class="hero__arrows">
                <button type="button" aria-label="Previous">&larr;</button>
                <button type="button" aria-label="Next">&rarr;</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="about" class="about">
        <div class="wrap">
          <div class="about__head">
            <p class="eyebrow" data-reveal>Leading full-service law firm in Africa</p>
            <h2 class="about__title" data-reveal>Leading full-service law firm in Africa</h2>
          </div>
          <div class="about__grid">
            <div class="about__figure about__figure--tall" data-reveal>
              <img :src="asset('opt/heritage-11.png')" alt="Painted vernacular architecture" data-parallax="0.05" loading="lazy" @error="onImgError" >
            </div>
            <div class="about__copy" data-reveal>
              <p class="about__lead">Webber Wentzel's team of experienced advisors provide multi-disciplinary legal and tax services to clients operating in and across the African continent.</p>
              <p class="about__body">Whether expanding into Africa or growing operations across the continent or globally, Webber Wentzel offers exceptional client service and has an outstanding track record of working on some of the most sustainable and transformative matters in Africa.</p>
            </div>
            <div class="about__figure about__figure--end" data-reveal>
              <img :src="asset('opt/heritage-8.png')" alt="Acacia against a deep blue sky" data-parallax="-0.05" loading="lazy" @error="onImgError" >
            </div>
          </div>
        </div>
      </section>

      <section id="services" data-services class="services">
        <div data-services-sticky class="services__sticky">
          <div class="services__head">
            <p class="eyebrow eyebrow--light">Practice Areas</p>
            <p class="services__counter">{{ counter }}</p>
          </div>
          <div data-services-track class="services__track">
            <article
              v-for="(p, i) in panels" :id="p.id" :key="p.num"
              class="panel" :class="{ 'panel--last': i === panels.length - 1 }"
            >
              <div class="panel__media">
                <img :src="asset(p.img)" :alt="p.alt" loading="lazy" @error="onImgError" >
                <p class="panel__num">{{ p.num }}</p>
              </div>
              <div class="panel__body">
                <h3>{{ p.title }}</h3>
                <p>{{ p.body }}</p>
                <a class="link-arrow" href="#">Read More <span class="rule" aria-hidden="true" /></a>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="specialists" class="specialists">
        <div class="wrap specialists__head">
          <div>
            <p class="eyebrow" data-reveal>Professionals</p>
            <h2 class="specialists__title" data-reveal>Find a Specialist</h2>
          </div>
          <p class="specialists__intro">Our team of trusted legal, forensics, and tax specialists consistently rank among the best in Africa.</p>
        </div>

        <div data-rail class="rail">
          <figure
            v-for="(h, i) in portraits" :key="h"
            class="portrait" :class="{ 'portrait--last': i === portraits.length - 1 }"
          >
            <img :src="asset(`opt/${h}.png`)" alt="Specialist portrait" loading="lazy" @error="onImgError" >
          </figure>
        </div>

        <div class="wrap specialists__foot">
          <p>We offer in-depth services to meet your specific needs. Scroll below or use the search function to connect with one of our experts located in either Johannesburg or Cape Town.</p>
          <a class="btn-solid-outline" href="#">View All Specialists <span class="rule" aria-hidden="true" /></a>
        </div>
      </section>

      <section class="podcast">
        <div class="podcast__bg" data-parallax="0.06">
          <img :src="asset('opt/sa-13.png')" alt="Cliffside pavilion" loading="lazy" @error="onImgError" >
        </div>
        <div class="wrap podcast__inner">
          <div class="podcast__lead" data-reveal>
            <p class="eyebrow eyebrow--light">Podcast</p>
            <h2 class="podcast__title">The Legal Lens</h2>
          </div>
          <div class="podcast__copy" data-reveal>
            <p>In this episode we explore what comes next and how the regulatory conversation is evolving from building compliance frameworks to testing how those frameworks operate in practice.</p>
            <a class="btn-paper" href="#">Learn More <span class="rule" aria-hidden="true" /></a>
          </div>
        </div>
      </section>

      <section id="insights" class="insights">
        <div class="wrap">
          <div class="section-head">
            <div>
              <p class="eyebrow">Insights</p>
              <h2 class="section-head__title">Legal and tax insights</h2>
            </div>
            <a class="link-arrow" href="#">View All <span class="rule" aria-hidden="true" /></a>
          </div>
          <div class="cards">
            <a v-for="c in insights" :key="c.title" class="card" href="#" data-reveal>
              <div class="card__media">
                <img :src="asset(c.img)" :alt="c.alt" loading="lazy" @error="onImgError" >
              </div>
              <h3>{{ c.title }}</h3>
            </a>
          </div>
        </div>
      </section>

      <section id="news" class="news">
        <div class="wrap">
          <div class="section-head section-head--flush">
            <div>
              <p class="eyebrow">News</p>
              <h2 class="section-head__title">Featured News</h2>
            </div>
            <a class="link-arrow" href="#">View All <span class="rule" aria-hidden="true" /></a>
          </div>

          <a v-for="n in news" :key="n.title" class="row" href="#" data-reveal>
            <div class="row__meta">
              <template v-for="(t, i) in n.tags" :key="t">
                <span v-if="i">|</span><span>{{ t }}</span>
              </template>
            </div>
            <h3>{{ n.title }}</h3>
            <div class="row__end">
              <p class="row__date">{{ n.date }}</p>
              <div class="row__thumb">
                <img :src="asset(n.thumb)" :alt="n.alt" loading="lazy" @error="onImgError" >
              </div>
              <span class="row__arrow" aria-hidden="true">&rarr;</span>
            </div>
          </a>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="wrap footer__grid">
        <div class="footer__contact">
          <div>
            <p class="footer__label">Johannesburg</p>
            <p class="footer__phone"><a href="tel:+27115305000">+27 (0) 11 530 5000</a></p>
          </div>
          <div>
            <p class="footer__label">Cape Town</p>
            <p class="footer__phone"><a href="tel:+27214317000">+27 (0) 21 431 7000</a></p>
          </div>
        </div>
        <nav
          v-for="(col, i) in footerCols" :key="i" class="footer__links"
          :aria-label="i === 0 ? 'Footer' : 'Footer secondary'"
        >
          <a v-for="l in col" :key="l.label" :href="l.href">{{ l.label }}</a>
        </nav>
      </div>
      <div class="wrap footer__legal">
        <p>Copyright 2026© Webber Wentzel. All rights reserved.</p>
        <div class="footer__legal-links">
          <a v-for="l in legalLinks" :key="l" href="#">{{ l }}</a>
        </div>
      </div>
      <img class="footer__watermark" :src="asset('logo-white.svg')" alt="" loading="lazy" >
    </footer>
  </div>
</template>
