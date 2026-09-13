/*
 | Best Driving School redesign — behaviour.
 | One IIFE, no dependencies. Every block is guarded so a page that lacks a
 | hook costs nothing. Data-attribute API (see the plan / README):
 |   [data-nav-toggle] [data-nav-panel]        mobile menu
 |   [data-menu] [data-menu-panel]             mega-menu (touch/keyboard; hover is CSS)
 |   [data-pk] [data-pk-chip] [data-pk-select] price picker
 |   [data-faq] [data-faq-panel]               disclosure
 |   [data-reveal]                             reveal on scroll
 |   [data-spine] #stage-1..N                  route-spine progress (N = count of #stage-i)
 |   [data-nav-spy]                            active section in the nav
 |   [data-quiz] [data-quiz-opt]               landing "which one sounds like you"
 */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- mobile menu ---------- */
  var navToggle = document.querySelector('[data-nav-toggle]');
  var navPanel = document.querySelector('[data-nav-panel]');
  if (navToggle && navPanel) {
    // Open: lock page scroll, make the rest of the page inert, move focus into the panel and keep Tab inside.
    // Close: undo all of that and return focus to the toggle.
    var inertTargets = Array.prototype.slice.call(document.querySelectorAll('main, footer, .bd-mobile-bar'));
    var focusables = function () {
      return Array.prototype.slice.call(navPanel.querySelectorAll('a[href], button:not([disabled])')).filter(function (el) { return el.offsetParent !== null; });
    };
    var setMenu = function (open) {
      var wasOpen = navPanel.hasAttribute('data-open');
      if (open) { navPanel.setAttribute('data-open', ''); } else { navPanel.removeAttribute('data-open'); }
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.documentElement.classList.toggle('bd-menu-open', open);
      inertTargets.forEach(function (el) { if (open) { el.setAttribute('inert', ''); } else { el.removeAttribute('inert'); } });
      if (open) { var first = focusables()[0]; if (first) first.focus(); }
      else if (wasOpen) { navToggle.focus(); }
    };
    navToggle.addEventListener('click', function () { setMenu(!navPanel.hasAttribute('data-open')); });
    navPanel.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (!navPanel.hasAttribute('data-open')) return;
      if (e.key === 'Escape') { setMenu(false); return; }
      if (e.key !== 'Tab') return;
      var items = focusables(); if (!items.length) return;
      var first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------- mobile bar: publish its real height so body padding always matches ---------- */
  var mobileBar = document.querySelector('.bd-mobile-bar');
  if (mobileBar && 'ResizeObserver' in window) {
    var publishBar = function () {
      var h = mobileBar.offsetParent === null ? 0 : mobileBar.getBoundingClientRect().height;
      if (h) document.documentElement.style.setProperty('--bd-mobile-bar-h', Math.ceil(h) + 'px');
    };
    new ResizeObserver(publishBar).observe(mobileBar);
    publishBar();
  }

  /* ---------- mega-menu: touch + keyboard ---------- */
  var menus = document.querySelectorAll('[data-menu]');
  if (menus.length) {
    var closeMenus = function (except) {
      menus.forEach(function (m) { if (m !== except) m.removeAttribute('data-open'); });
    };
    menus.forEach(function (m) {
      var trigger = m.querySelector(':scope > a');
      if (!trigger) return;
      trigger.addEventListener('click', function (e) {
        if (!window.matchMedia('(hover: none)').matches) return;
        if (!m.hasAttribute('data-open')) { e.preventDefault(); closeMenus(m); m.setAttribute('data-open', ''); }
      });
    });
    document.addEventListener('click', function (e) { if (!e.target.closest('[data-menu]')) closeMenus(null); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenus(null); });
  }

  /* ---------- price picker ---------- */
  document.querySelectorAll('[data-pk]').forEach(function (pk) {
    var chips = pk.querySelectorAll('[data-pk-chip]');
    var select = pk.querySelector('[data-pk-select]');
    var all = function (sel) { return Array.prototype.slice.call(pk.querySelectorAll(sel)); };
    var out = {
      price: all('[data-pk-price]'),
      was: all('[data-pk-was]'),
      badge: all('[data-pk-badge]'),
      save: all('[data-pk-save]'),
      meta: all('[data-pk-meta]'),
      label: all('[data-pk-label]'),
      link: all('[data-pk-link]'),
      note: all('[data-pk-note]'),
      row: all('[data-pk-row]')
    };
    var panels = pk.querySelectorAll('[data-pk-panel]');
    var tick = 0;
    var apply = function (el) {
      if (!el) return;
      var d = el.dataset;
      chips.forEach(function (c) { c.setAttribute('aria-checked', c === el ? 'true' : 'false'); });
      if (select && select.value !== d.value) select.value = d.value;
      var setText = function (nodes, val) { nodes.forEach(function (n) { n.textContent = val; }); };
      var setOpt = function (nodes, val) {
        nodes.forEach(function (n) { if (val) { n.textContent = val; n.hidden = false; } else { n.hidden = true; } });
      };
      if (d.price !== undefined) setText(out.price, d.price);
      setOpt(out.was, d.was);
      setOpt(out.badge, d.badge);
      setOpt(out.save, d.save);
      if (d.meta !== undefined) setText(out.meta, d.meta);
      setOpt(out.note, d.note);
      setText(out.label, d.value);
      if (d.link) out.link.forEach(function (n) { n.setAttribute('href', d.link); });
      panels.forEach(function (p) { p.hidden = p.getAttribute('data-pk-panel') !== d.value; });
      if (out.row.length && !reduce) {
        tick = (tick + 1) % 2;
        out.row.forEach(function (row) {
          row.classList.remove('bd-swap');
          void row.offsetWidth;
          row.setAttribute('data-tick', String(tick));
          row.classList.add('bd-swap');
        });
      }
    };
    chips.forEach(function (c) { c.addEventListener('click', function () { apply(c); }); });
    if (select) {
      select.addEventListener('change', function () {
        var match = Array.prototype.find.call(chips, function (c) { return c.dataset.value === select.value; });
        if (match) apply(match);
      });
    }
  });

  /* ---------- details / picker disclosure ---------- */
  document.querySelectorAll('[data-faq]').forEach(function (btn) {
    // The panel is: the aria-controls target, else a [data-faq-panel] that is a
    // sibling of the button or of one of its ancestors (walking up to the scope).
    var panel = document.getElementById(btn.getAttribute('aria-controls') || '');
    var scope = btn.closest('[data-faq-scope]');
    var node = btn;
    while (!panel && node && node !== document.body) {
      var parent = node.parentElement;
      if (!parent) break;
      var found = Array.prototype.find.call(parent.children, function (c) { return c !== node && c.hasAttribute('data-faq-panel'); });
      if (found) panel = found;
      if (parent === scope) break;
      node = parent;
    }
    if (!panel) return;
    var group = btn.closest('[data-faq-group]');
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      if (group && !open) {
        group.querySelectorAll('[data-faq][aria-expanded="true"]').forEach(function (other) {
          other.setAttribute('aria-expanded', 'false');
          var op = document.getElementById(other.getAttribute('aria-controls') || '') || other.parentElement.querySelector('[data-faq-panel]');
          if (op) op.removeAttribute('data-open');
        });
      }
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (open) { panel.removeAttribute('data-open'); } else { panel.setAttribute('data-open', ''); }
    });
  });

  /* ---------- reveal on scroll ---------- */
  var reveals = document.querySelectorAll('[data-reveal]:not([data-in])');
  if (reveals.length) {
    if (reduce || !('IntersectionObserver' in window)) {
      reveals.forEach(function (el) { el.setAttribute('data-in', '1'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.setAttribute('data-in', '1'); io.unobserve(e.target); }
        });
      }, { threshold: 0.15 });
      reveals.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- hero lane: the car follows the scroll ----------
     Scrolling down drives the car along the dashed lane; scrolling back up reverses it. The offset
     lives in --bd-car-x on the image (pages.css) so the entrance animation on the wrapper is untouched.
     Skipped when the lane is hidden (phones) or the visitor prefers reduced motion. */
  var lanes = document.querySelectorAll('.bd-hero__lane');
  if (lanes.length && !reduce) {
    var laneRaf = 0;
    var LANE_SCROLL = 600; // px of scrolling that takes the car from the start of the lane to the end
    var driveLane = function () {
      laneRaf = 0;
      var p = Math.max(0, Math.min(1, window.scrollY / LANE_SCROLL));
      lanes.forEach(function (lane) {
        var img = lane.querySelector('.bd-car img');
        if (!img || lane.offsetParent === null) return;
        var travel = Math.max(0, lane.clientWidth - img.clientWidth);
        img.style.setProperty('--bd-car-x', Math.round(p * travel) + 'px');
      });
    };
    var onLaneScroll = function () { if (!laneRaf) laneRaf = requestAnimationFrame(driveLane); };
    window.addEventListener('scroll', onLaneScroll, { passive: true });
    window.addEventListener('resize', onLaneScroll);
    driveLane();
  }

  /* ---------- route spine + nav spy ---------- */
  var spine = document.querySelector('[data-spine]');
  var spyLinks = document.querySelectorAll('[data-nav-spy] a[href^="#"]');
  // both consumers are display:none below 1160px, so phones skip the scroll listener entirely
  var wideLayout = !window.matchMedia || window.matchMedia('(min-width: 1161px)').matches;
  if (wideLayout && (spine || spyLinks.length)) {
    var raf = 0;
    var stages = [];
    for (var si = 1; si <= 12; si++) { var st = document.getElementById('stage-' + si); if (!st) break; stages.push(st); }
    var stageDots = spine ? spine.querySelectorAll('[data-stage]') : [];
    var stageNums = document.querySelectorAll('[data-stage-num]');
    var measure = function () {
      raf = 0;
      var mid = window.innerHeight * 0.55;
      if (spine && stages.length >= 2) {
        var n = stages.length;
        var tops = stages.map(function (r) { return r.getBoundingClientRect().top; });
        var stage = 0, fill = 0;
        tops.forEach(function (t, i) { if (t <= mid) stage = i + 1; });
        if (stage >= n) { fill = 1; }
        else if (stage >= 1) {
          var a = tops[stage - 1], b = tops[stage];
          fill = ((stage - 1) + Math.max(0, Math.min(1, (mid - a) / Math.max(1, b - a)))) / (n - 1);
        }
        if (reduce) fill = stage === 0 ? 0 : (stage - 1) / (n - 1);
        spine.style.setProperty('--fill', fill.toFixed(3));
        stageDots.forEach(function (d, i) { d.classList.toggle('is-on', stage >= i + 1); });
        stageNums.forEach(function (nm, i) { nm.classList.toggle('is-on', stage >= i + 1); });
      }
      if (spyLinks.length) {
        var current = '';
        spyLinks.forEach(function (l) {
          var id = l.getAttribute('href').slice(1);
          var el = id && document.getElementById(id);
          if (!el) return;
          var r = el.getBoundingClientRect();
          if (r.top <= 120 && r.bottom > 120) current = id;
        });
        spyLinks.forEach(function (l) {
          if (l.getAttribute('href') === '#' + current && current) { l.setAttribute('aria-current', 'true'); }
          else if (!l.hasAttribute('data-static-current')) { l.removeAttribute('aria-current'); }
        });
      }
    };
    var onScroll = function () { if (!raf) raf = requestAnimationFrame(measure); };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    measure();
  }

  /* ---------- reCAPTCHA: load the widget script only when the enquiry form is near or focused ---------- */
  var lazyForms = document.querySelectorAll('[data-recaptcha-lazy]');
  if (lazyForms.length) {
    var recaptchaLoaded = false;
    var loadRecaptcha = function () {
      if (recaptchaLoaded) return; recaptchaLoaded = true;
      var s = document.createElement('script'); s.src = 'https://www.google.com/recaptcha/api.js'; s.async = true; s.defer = true;
      document.head.appendChild(s);
    };
    lazyForms.forEach(function (form) { form.addEventListener('focusin', loadRecaptcha, { once: true }); });
    if ('IntersectionObserver' in window) {
      var rio = new IntersectionObserver(function (entries) {
        if (entries.some(function (en) { return en.isIntersecting; })) { loadRecaptcha(); rio.disconnect(); }
      }, { rootMargin: '600px 0px' });
      lazyForms.forEach(function (form) { rio.observe(form); });
    } else { loadRecaptcha(); }
  }

  /* ---------- enquiry form: fold the phone number into the message ---------- */
  document.querySelectorAll('[data-enquiry]').forEach(function (form) {
    form.addEventListener('submit', function () {
      var phone = form.querySelector('[data-enquiry-phone]');
      var msg = form.querySelector('[data-enquiry-message]');
      if (phone && msg && phone.value.trim() && msg.value.indexOf('Phone: ') !== 0) {
        msg.value = 'Phone: ' + phone.value.trim() + String.fromCharCode(10) + msg.value;
      }
    });
  });

  /* ---------- landing quiz ---------- */
  var quiz = document.querySelector('[data-quiz]');
  if (quiz) {
    var opts = quiz.querySelectorAll('[data-quiz-opt]');
    var rec = {
      service: quiz.querySelector('[data-quiz-service]'),
      course: quiz.querySelector('[data-quiz-course]'),
      price: quiz.querySelector('[data-quiz-price]'),
      why: quiz.querySelector('[data-quiz-why]'),
      link: quiz.querySelector('[data-quiz-link]'),
      box: quiz.querySelector('[data-quiz-rec]')
    };
    var qTick = 0;
    opts.forEach(function (o) {
      o.addEventListener('click', function () {
        opts.forEach(function (x) { x.setAttribute('aria-checked', x === o ? 'true' : 'false'); });
        var d = o.dataset;
        if (rec.service) { rec.service.textContent = d.service; rec.service.setAttribute('href', d.serviceLink); }
        if (rec.course) rec.course.textContent = d.course;
        if (rec.price) rec.price.textContent = d.price ? '· ' + d.price : '';
        if (rec.why) rec.why.textContent = d.why;
        if (rec.link) rec.link.setAttribute('href', d.courseLink);
        if (rec.box && !reduce) {
          qTick = (qTick + 1) % 2;
          rec.box.classList.remove('bd-swap');
          void rec.box.offsetWidth;
          rec.box.setAttribute('data-tick', String(qTick));
          rec.box.classList.add('bd-swap');
        }
      });
    });
  }
})();
