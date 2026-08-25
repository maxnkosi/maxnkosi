/* ==========================================================================
   Webber Wentzel — Homepage B
   Behaviour ported from the "WW Homepage B.dc.html" design component.
   Hover states live in CSS; this file owns scroll-driven motion and state.
   ========================================================================== */

(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* The breakpoint at which the pinned horizontal rail degrades to a native
     swipe strip. Must stay in step with the matching CSS media query. */
  var flatRail = window.matchMedia(
    "(max-width: 760px), (pointer: coarse) and (max-width: 1024px)"
  );

  var nav = document.getElementById("nav");
  var navLinks = document.getElementById("nav-links");
  var navUtil = document.getElementById("nav-util");
  var menuBtn = document.getElementById("nav-menu");
  var menuPanel = document.getElementById("mobile-menu");
  var menuClose = document.getElementById("menu-close");
  var heroCol = document.getElementById("hero-col");
  var heroImg = document.getElementById("hero-img");
  var pin = document.getElementById("services");
  var track = document.getElementById("services-track");
  var counter = document.getElementById("services-counter");
  var rail = document.getElementById("rail");
  var main = document.getElementById("main");

  /* Each entry caches the element's UNTRANSFORMED centre in document space.
     Reading getBoundingClientRect() on an element that already carries last
     frame's transform feeds the offset back into itself, which makes the
     effective rate rate/(1 - rate) and leaves elements creeping during a fast
     scroll. Measure once, and again on resize. */
  var parallax = Array.prototype.map.call(
    document.querySelectorAll("[data-parallax]"),
    function (el) {
      return { el: el, rate: parseFloat(el.getAttribute("data-parallax")) || 0, centre: 0 };
    }
  );

  function measureParallax() {
    parallax.forEach(function (p) {
      var prev = p.el.style.transform;
      p.el.style.transform = "";
      var b = p.el.getBoundingClientRect();
      p.centre = b.top + (window.scrollY || window.pageYOffset || 0) + b.height / 2;
      p.el.style.transform = prev;
    });
  }

  /* ------------------------------------------------------------------------
     Theme — the design's "Feel" props, kept configurable at runtime.
     ------------------------------------------------------------------------ */

  var NAV_CHROME = { "Progressive blur": "progressive-blur", "Solid blur": "solid-blur", "Hairline": "hairline" };
  var IMAGE_MOOD = { "Editorial colour": "editorial-colour", "Duotone ink": "duotone-ink", "Muted archive": "muted-archive" };

  function setTheme(opts) {
    opts = opts || {};
    var root = document.documentElement;
    if (opts.accent) root.style.setProperty("--accent", opts.accent);
    if (opts.navChrome) root.setAttribute("data-nav-chrome", NAV_CHROME[opts.navChrome] || opts.navChrome);
    if (opts.imageMood) root.setAttribute("data-image-mood", IMAGE_MOOD[opts.imageMood] || opts.imageMood);
  }

  window.WW = { setTheme: setTheme };

  /* ------------------------------------------------------------------------
     Missing photographic assets degrade to a tonal block (see ASSETS.md).
     ------------------------------------------------------------------------ */

  function flagMissing(img) {
    img.classList.add("is-missing");
    var host = img.closest(
      ".card__media, .panel__media, .portrait, .about__figure, .hero__img, .podcast__bg, .row__thumb"
    );
    if (host) host.classList.add("is-missing-media");
  }

  Array.prototype.forEach.call(document.images, function (img) {
    if (img.complete && img.naturalWidth === 0) flagMissing(img);
    img.addEventListener("error", function () { flagMissing(img); });
  });

  /* ------------------------------------------------------------------------
     Reveal on scroll
     ------------------------------------------------------------------------ */

  var revealEls = document.querySelectorAll("[data-reveal]");
  if (reduce || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(revealEls, function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });
    Array.prototype.forEach.call(revealEls, function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------------------------
     Specialist rail — drag to scroll
     ------------------------------------------------------------------------ */

  if (rail) {
    var down = false, moved = false, startX = 0, startScroll = 0;

    rail.addEventListener("pointerdown", function (e) {
      down = true;
      moved = false;
      startX = e.clientX;
      startScroll = rail.scrollLeft;
    });

    rail.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 4) {
        moved = true;
        rail.classList.add("is-dragging");
      }
      if (moved) {
        e.preventDefault();
        rail.scrollLeft = startScroll - dx * 1.2;
      }
    });

    var endDrag = function () {
      down = false;
      rail.classList.remove("is-dragging");
    };
    window.addEventListener("pointerup", endDrag);
    window.addEventListener("pointercancel", endDrag);

    /* A drag must not fire the click on whatever sat under the cursor. */
    rail.addEventListener("click", function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); }
    }, true);
  }

  /* ------------------------------------------------------------------------
     Scroll frame
     ------------------------------------------------------------------------ */

  var raf = null;
  /* Seeded from the current position: a scroll-restored reload past 1.5vh
     would otherwise compare against 0 and render the header retracted. */
  var lastY = window.scrollY || window.pageYOffset || 0;

  function frame() {
    raf = null;
    var y = window.scrollY || window.pageYOffset || 0;
    var vh = window.innerHeight;

    if (nav) {
      nav.classList.toggle("is-scrolled", y > 80);
      nav.classList.toggle("is-hidden", y > vh * 1.5 && y > lastY);
      lastY = y;
    }

    if (heroImg && !reduce) {
      var hp = Math.min(1, y / vh);
      heroImg.style.transform =
        "translateY(" + (hp * -7).toFixed(2) + "%) scale(" + (1 + hp * 0.06).toFixed(3) + ")";
    }

    if (pin && track && !flatRail.matches) {
      var r = pin.getBoundingClientRect();
      var total = pin.offsetHeight - vh;
      var p = total > 0 ? Math.max(0, Math.min(1, -r.top / total)) : 0;
      var dist = Math.max(0, track.scrollWidth - window.innerWidth);
      track.style.transform = "translate3d(" + (-p * dist).toFixed(1) + "px,0,0)";
      setCounter(Math.min(4, Math.floor(p * 3.999) + 1));
    }

    if (!reduce) {
      parallax.forEach(function (p) {
        var off = (p.centre - y - vh / 2) * p.rate;
        p.el.style.transform = "translate3d(0," + off.toFixed(1) + "px,0)";
      });
    }
  }

  function setCounter(n) {
    if (!counter) return;
    var label = "0" + n + " / 04";
    if (counter.textContent !== label) counter.textContent = label;
  }

  function onScroll() {
    if (raf === null) raf = window.requestAnimationFrame(frame);
  }

  /* In the flattened rail mode the counter tracks native horizontal scroll. */
  if (track) {
    track.addEventListener("scroll", function () {
      if (!flatRail.matches) return;
      var max = track.scrollWidth - track.clientWidth;
      var p = max > 0 ? track.scrollLeft / max : 0;
      setCounter(Math.min(4, Math.floor(p * 3.999) + 1));
    }, { passive: true });
  }

  /* ------------------------------------------------------------------------
     Compact menu
     ------------------------------------------------------------------------ */

  var FOCUSABLE = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

  function setMenu(open) {
    if (!menuPanel) return;
    menuPanel.hidden = !open;
    if (menuBtn) menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";

    /* The overlay is opaque and covers the page, so the content behind it must
       leave the tab order too — otherwise Tab walks into links nobody can see. */
    if (main) main.inert = open;
    if (nav) nav.inert = open;

    if (open) {
      var first = menuPanel.querySelector(FOCUSABLE);
      if (first) first.focus();
    } else if (menuBtn && document.activeElement && menuPanel.contains(document.activeElement)) {
      menuBtn.focus();
    }
  }

  /* Keep Tab inside the overlay for browsers without inert support. */
  function trapTab(e) {
    if (e.key !== "Tab" || !menuPanel || menuPanel.hidden) return;
    var items = Array.prototype.filter.call(
      menuPanel.querySelectorAll(FOCUSABLE),
      function (el) { return el.offsetParent !== null; }
    );
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  if (menuBtn) menuBtn.addEventListener("click", function () { setMenu(menuPanel.hidden); });
  if (menuClose) menuClose.addEventListener("click", function () { setMenu(false); });
  if (menuPanel) {
    Array.prototype.forEach.call(menuPanel.querySelectorAll("[data-menu-link]"), function (a) {
      a.addEventListener("click", function () { setMenu(false); });
    });
  }
  window.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setMenu(false);
    trapTab(e);
  });

  /* ------------------------------------------------------------------------
     Layout — push the hero clear of the real header height
     ------------------------------------------------------------------------ */

  function layout() {
    var compact = window.innerWidth < 1180;
    if (nav && heroCol) {
      var h = nav.getBoundingClientRect().height;
      heroCol.style.paddingTop = Math.round(h + (compact ? 56 : 96)) + "px";
    }
    if (!compact) setMenu(false);
  }

  function onResize() {
    layout();
    measureParallax();
    if (flatRail.matches && track) track.style.transform = "";
    onScroll();
  }

  /* ------------------------------------------------------------------------
     Anchors into the pinned rail

     The panels live inside a transformed track, so a plain #sectors jump lands
     on the section start (panel 01) no matter which panel carries the id. Map
     the target panel to the scroll offset that actually brings it into view.
     ------------------------------------------------------------------------ */

  function scrollToPanel(panel) {
    if (!pin || !track || !panel) return false;

    if (flatRail.matches) {
      track.scrollTo({ left: panel.offsetLeft, behavior: "smooth" });
      pin.scrollIntoView({ behavior: "smooth", block: "start" });
      return true;
    }

    var dist = Math.max(0, track.scrollWidth - window.innerWidth);
    if (!dist) return false;
    var progress = Math.min(1, panel.offsetLeft / dist);
    var top = pin.offsetTop + progress * (pin.offsetHeight - window.innerHeight);
    window.scrollTo({ top: Math.round(top), behavior: "smooth" });
    return true;
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest('a[href^="#"]');
    if (!link) return;
    var id = link.getAttribute("href").slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target || !track || !track.contains(target)) return;
    if (scrollToPanel(target)) {
      e.preventDefault();
      setMenu(false);
    }
  });

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onResize);
  if (flatRail.addEventListener) flatRail.addEventListener("change", onResize);

  layout();
  measureParallax();
  frame();

  /* Images resolve after first paint and shift everything below them. */
  window.addEventListener("load", function () { measureParallax(); frame(); });
})();
