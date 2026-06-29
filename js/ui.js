/* ===========================================================
   ResQ Tyres — UI motion (Revision 3.1)
   - hero word rotator
   - scroll progress bar
   - scroll reveals (directional) + staggered grids
   - count-up numbers
   - light parallax on photos
   Presentation only; independent of app.js.
   =========================================================== */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Hero rotator ---- */
  var rot = document.getElementById("rotator");
  if (rot && !reduce) {
    var words = ["At home.", "At work.", "At the roadside.", "Day or night."];
    var i = 0;
    setInterval(function () {
      i = (i + 1) % words.length;
      rot.style.transition = "opacity .25s ease, transform .25s ease";
      rot.style.opacity = "0";
      rot.style.transform = "translateY(8px)";
      setTimeout(function () {
        rot.textContent = words[i];
        rot.style.opacity = "1";
        rot.style.transform = "none";
      }, 250);
    }, 2200);
  }

  /* ---- Scroll progress bar + hero scale + to-top ---- */
  var bar = document.getElementById("progress");
  var heroImg = document.getElementById("heroImg");
  var toTop = document.getElementById("toTop");

  function onScroll() {
    var h = document.documentElement;
    var y = h.scrollTop;
    if (bar) {
      var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
    }
    /* hero photo scales up gently as you scroll through the hero */
    if (heroImg && !reduce) {
      var p = Math.max(0, Math.min(1, y / (window.innerHeight * 0.9)));
      heroImg.style.transform = "scale(" + (1 + p * 0.14).toFixed(3) + ")";
    }
    /* back-to-top visibility */
    if (toTop) toTop.classList.toggle("show", y > 600);
    parallax();
  }

  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
    });
  }

  /* ---- Count-up ---- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var dec = parseInt(el.getAttribute("data-dec") || "0", 10);
    var suffix = el.getAttribute("data-suffix") || "";
    if (isNaN(target)) return;
    if (reduce) { el.textContent = target.toFixed(dec) + suffix; return; }
    var start = null, dur = 1300;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toFixed(dec) + suffix;
    }
    requestAnimationFrame(step);
  }

  /* ---- Reveal / stagger / counters via IntersectionObserver ---- */
  var animated = document.querySelectorAll(".reveal, .stagger");
  var counters = document.querySelectorAll("[data-count]");

  if (!("IntersectionObserver" in window) || reduce) {
    animated.forEach(function (el) { el.classList.add("in"); });
    counters.forEach(countUp);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.14, rootMargin: "0px 0px -50px 0px" });
    animated.forEach(function (el) { io.observe(el); });

    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---- Parallax ---- */
  var px = reduce ? [] : document.querySelectorAll("[data-parallax]");
  function parallax() {
    if (!px.length) return;
    var vh = window.innerHeight;
    px.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var speed = parseFloat(el.getAttribute("data-parallax")) || 0.1;
      var offset = (r.top + r.height / 2 - vh / 2) * -speed;
      el.style.transform = "translate3d(0," + offset.toFixed(1) + "px,0)";
    });
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  onScroll();
})();
