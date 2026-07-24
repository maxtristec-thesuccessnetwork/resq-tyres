/* ===========================================================
   ResQ Tyres — app logic (Revision 4)
   Two paths:
     • Emergency  -> phone-first (no form needed)
     • Planned    -> "home fitting" enquiry emailed to the business
   Plus a price-RANGE guide (js/rates.js) and a postcode checker.
   =========================================================== */

/* ---- CONFIG: set these before going live ---- */
const CONFIG = {
  // Where planned-fitting enquiries go (Web3Forms + mailto fallback).
  businessEmail: "maxtristec@googlemail.com",
  // Free, no account: https://web3forms.com — enter the email above, paste
  // the Access Key here and enquiries arrive automatically.
  web3formsKey: "8f3d8e31-3005-4a6a-b438-b7343c9c0ca5",
  // (Optional) alternative endpoint, e.g. Formspree. Leave "" if using Web3Forms.
  formEndpoint: ""
};

document.addEventListener("DOMContentLoaded", function () {
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  populateSelects();
  wireEstimateForm();
  wireEnquiryForm();
  wirePostcodeChecker();
  wireTyreSizeCaution();
  initCoverageMap();
});

/* ---------- Coverage map (Leaflet + Carto dark tiles) ---------- */
function initCoverageMap() {
  var el = document.getElementById("cov-leaflet");
  if (!el || typeof L === "undefined") return;

  var CENTER = [53.752, -1.545];

  // NB: set an initial view BEFORE adding any layers, and disable zoom
  // animation — adding permanent tooltips then animating fitBounds throws
  // Leaflet's "layerPointToLatLng" error and leaves the map blank.
  var map = L.map(el, {
    scrollWheelZoom: false,
    zoomControl: true,
    attributionControl: true,
    zoomAnimation: false,
    markerZoomAnimation: false
  }).setView(CENTER, 11);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
  }).addTo(map);

  // Glowing coverage zone
  var circle = L.circle(CENTER, {
    radius: 17000,
    className: "cov-zone",
    color: "#ff2d55", weight: 2, opacity: 0.9,
    fillColor: "#e4002b", fillOpacity: 0.12
  }).addTo(map);

  // [lat, lng, name, isHub]
  var towns = [
    [53.8008, -1.5491, "Leeds", true],
    [53.7938, -1.7524, "Bradford", false],
    [53.6830, -1.4977, "Wakefield", false],
    [53.6912, -1.6290, "Dewsbury", false],
    [53.7967, -1.6631, "Pudsey", false],
    [53.7491, -1.6010, "Morley", false],
    [53.7256, -1.3560, "Castleford", false],
    [53.7928, -1.3872, "Garforth", false],
    [53.6919, -1.3128, "Pontefract", false]
  ];

  towns.forEach(function (t) {
    var hub = t[3];
    var icon = L.divIcon({
      className: "cov-marker" + (hub ? " hub" : ""),
      html: '<span class="cov-pulse"></span><span class="cov-dot"></span>',
      iconSize: hub ? [22, 22] : [16, 16],
      iconAnchor: hub ? [11, 11] : [8, 8]
    });
    L.marker([t[0], t[1]], { icon: icon, keyboard: false })
      .addTo(map)
      .bindTooltip(t[2], {
        permanent: true, direction: "top", offset: [0, hub ? -10 : -8],
        className: "cov-tip" + (hub ? " hub" : "")
      });
  });

  map.fitBounds(circle.getBounds(), { padding: [34, 34], animate: false });

  // Re-measure once layout settles (map sits inside an animated section)
  setTimeout(function () {
    map.invalidateSize();
    map.fitBounds(circle.getBounds(), { padding: [34, 34], animate: false });
  }, 300);
  window.addEventListener("load", function () { map.invalidateSize(); });
}

/* ---------- Price-range guide ---------- */
function populateSelects() {
  var o = RESQ_RATES.options;
  fill("width", o.widths, 205);
  fill("profile", o.profiles, 55);
  fill("rim", o.rims, 16);
}
function fill(id, values, preset) {
  var sel = document.getElementById(id);
  if (!sel) return;
  values.forEach(function (v) {
    var opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    if (v === preset) opt.selected = true;
    sel.appendChild(opt);
  });
}

function rangeForSize(width, profile, rim) {
  var key = width + "/" + profile + "R" + rim;
  if (RESQ_RATES.exact[key]) return RESQ_RATES.exact[key];
  var fb = RESQ_RATES.fallbackByRim;
  return { low: fb.low[rim] || 55, high: fb.high[rim] || 149 };
}

var ResQState = { size: "", lockingNut: "yes" };

function wireEstimateForm() {
  var form = document.getElementById("estimate-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var width = val("width"), profile = val("profile"), rim = val("rim");
    var sizeLabel = width + "/" + profile + " R" + rim;
    var range = rangeForSize(width, profile, rim);
    var lockingNut = val("lockingnut") || "yes";

    ResQState.size = sizeLabel;
    ResQState.lockingNut = lockingNut;
    ResQState.range = range;

    renderRange(sizeLabel, range, lockingNut);

    var results = document.getElementById("estimate-results");
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}

function renderRange(sizeLabel, range, lockingNut) {
  document.getElementById("size-label").textContent = sizeLabel;
  document.getElementById("range-out").innerHTML =
    "£" + range.low + "<span class='dash'>–</span>£" + range.high +
    "<small>per tyre, fitted</small>";

  // Locking wheel-nut add-on note
  var addon = document.getElementById("addon-note");
  if (addon) {
    if (lockingNut === "no") {
      var a = RESQ_RATES.lockingNutRemoval || { low: 0, high: 0 };
      var priceTxt = (a.high > 0)
        ? "£" + a.low + "–£" + a.high
        : "no extra charge";
      addon.hidden = false;
      addon.innerHTML =
        '<svg class="icon" aria-hidden="true"><use href="#i-shield"/></svg> ' +
        "<b>No locking wheel-nut key?</b> No problem — most fitters can't help, " +
        "but we carry the specialist removal tools. We'll take it off safely (" +
        priceTxt + ").";
    } else {
      addon.hidden = true;
      addon.innerHTML = "";
    }
  }

  // Prefill the planned enquiry with this size
  var to = document.getElementById("to-enquiry");
  if (to) {
    to.onclick = function () {
      setVal("tyresize2", ResQState.size);
      var el = document.getElementById("enquiry");
      if (el) el.scrollIntoView({ behavior: "smooth" });
      var nameEl = document.getElementById("name");
      if (nameEl) setTimeout(function () { nameEl.focus(); }, 400);
      flagTyreSize();
    };
  }
}

/* ---------- Tyre-size "have you confirmed?" caution ---------- */
function wireTyreSizeCaution() {
  var input = document.getElementById("tyresize2");
  if (!input) return;
  input.addEventListener("input", function () {
    if (input.value.trim().length >= 3) flagTyreSize();
  });
}
function flagTyreSize() {
  var caution = document.getElementById("tyresize-caution");
  if (caution) caution.hidden = false;
}

/* ---------- Postcode coverage checker ---------- */
function wirePostcodeChecker() {
  var btn = document.getElementById("pc-btn");
  var input = document.getElementById("pc-check");
  var out = document.getElementById("pc-result");
  if (!btn || !input || !out) return;

  function check() {
    var raw = (input.value || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
    if (!raw) { showPC(out, "warn", "Enter your postcode to check."); return; }
    // outward district letters = leading alpha chars (e.g. "LS" from "LS98TX")
    var m = raw.match(/^[A-Z]{1,2}/);
    var prefix = m ? m[0] : "";
    var covered = RESQ_COVERAGE.covered.indexOf(prefix) !== -1;
    if (covered) {
      showPC(out, "ok",
        '<svg class="icon" aria-hidden="true"><use href="#i-check-circle"/></svg> ' +
        "Great news — <b>" + prefix + "</b> is in our usual area. Call us or plan a home fitting below.");
    } else {
      showPC(out, "warn",
        '<svg class="icon" aria-hidden="true"><use href="#i-alert"/></svg> ' +
        "We may still be able to help just outside our core area — give us a quick call on " +
        '<a href="tel:07438562633">07438&nbsp;562633</a> to check.');
    }
  }
  function showPC(el, kind, html) { el.hidden = false; el.className = "pc-result " + kind; el.innerHTML = html; }

  btn.addEventListener("click", check);
  input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); check(); } });
}

/* ---------- Planned home-fitting enquiry ---------- */
function wireEnquiryForm() {
  var form = document.getElementById("enquiry-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var err = document.getElementById("enquiry-error");

    var data = {
      name: val("name"),
      phone: val("phone"),
      email: val("email"),
      postcode: val("postcode2"),
      vehicle: val("vehicle"),
      tyresize: val("tyresize2"),
      tyrecount: val("tyrecount"),
      availability: val("availability"),
      message: val("message")
    };

    // mandatory: name, phone, postcode, vehicle, tyre size, count, availability
    if (!data.name || !data.phone || !data.postcode || !data.vehicle ||
        !data.tyresize || !data.tyrecount || !data.availability) {
      show(err, "Please fill in your name, phone, postcode, vehicle, tyre size, how many tyres and your availability.");
      return;
    }
    hide(err);

    // carry the on-screen estimate into the enquiry (only if they used the tool)
    var est = estimateLines(data.tyrecount);
    data.estRange = est.range;
    data.estLocking = est.locking;
    data.estTotal = est.total;

    if (CONFIG.web3formsKey) {
      sendViaWeb3Forms(data, form, err);
    } else if (CONFIG.formEndpoint) {
      sendToEndpoint(CONFIG.formEndpoint, data, form, err);
    } else {
      openMailto(data);
      succeed(data);
    }
  });
}

function sendViaWeb3Forms(data, form, err) {
  var payload = {
    access_key: CONFIG.web3formsKey,
    subject: "Home tyre fitting enquiry — " + data.name + " (" + data.postcode + ")",
    from_name: "ResQ Tyres Website",
    replyto: data.email || CONFIG.businessEmail,
    "Name": data.name,
    "Phone": data.phone,
    "Email": data.email || "Not provided",
    "Postcode": data.postcode,
    "Vehicle": data.vehicle,
    "Tyre size": data.tyresize,
    "Tyres needed": data.tyrecount,
    "Availability": data.availability,
    "Estimated price": data.estRange || "-",
    "Locking nut removal needed": data.estLocking || "-",
    "Estimated total": data.estTotal || "-",
    "Notes": data.message || "None"
  };
  fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: { "Accept": "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).then(function (r) {
    if (r.ok) { succeed(data); form.reset(); }
    else { show(err, "Sorry, something went wrong. Please call us on 07438 562633."); }
  }).catch(function () { openMailto(data); succeed(data); });
}

function sendToEndpoint(endpoint, data, form, err) {
  fetch(endpoint, {
    method: "POST",
    headers: { "Accept": "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(function (r) {
    if (r.ok) { succeed(data); form.reset(); }
    else { show(err, "Sorry, something went wrong. Please call us on 07438 562633."); }
  }).catch(function () { openMailto(data); succeed(data); });
}

// Turn the on-screen estimate (if the customer used the tool) into email lines.
function estimateLines(countStr) {
  var r = ResQState.range;
  if (!r) return { range: "Not calculated (customer didn't use the estimate tool)", locking: "Not asked", total: "" };
  var rangeTxt = "£" + r.low + "–£" + r.high + " per tyre, fitted";
  var needsRemoval = ResQState.lockingNut === "no";
  var a = RESQ_RATES.lockingNutRemoval || { low: 0, high: 0 };
  var lockingTxt = needsRemoval
    ? "Yes — no key (" + (a.high > 0 ? "£" + a.low + "–£" + a.high : "no extra charge") + ")"
    : "No";
  var count = parseInt(String(countStr).replace(/[^0-9]/g, ""), 10);
  var total = "";
  if (count && count > 0) {
    var lo = r.low * count, hi = r.high * count;
    if (needsRemoval) { lo += a.low; hi += a.high; }
    var plus = /\+/.test(String(countStr)) ? "+" : "";
    total = "£" + lo + "–£" + hi + " (" + count + plus + " tyre" + (count > 1 ? "s" : "") +
            (needsRemoval ? " + locking nut removal" : "") + ")";
  }
  return { range: rangeTxt, locking: lockingTxt, total: total };
}

function buildSummary(d) {
  return (
    "New home tyre fitting enquiry — ResQ Tyres\n\n" +
    "Name: " + d.name + "\n" +
    "Phone: " + d.phone + "\n" +
    "Email: " + (d.email || "-") + "\n" +
    "Postcode: " + d.postcode + "\n" +
    "Vehicle: " + d.vehicle + "\n" +
    "Tyre size: " + d.tyresize + "\n" +
    "Tyres needed: " + d.tyrecount + "\n" +
    "Availability: " + d.availability + "\n" +
    "Estimated price: " + (d.estRange || "-") + "\n" +
    "Locking nut removal needed: " + (d.estLocking || "-") + "\n" +
    "Estimated total: " + (d.estTotal || "-") + "\n" +
    "Notes: " + (d.message || "-") + "\n"
  );
}

function openMailto(d) {
  var subject = "Home tyre fitting enquiry — " + d.postcode;
  var url = "mailto:" + CONFIG.businessEmail +
    "?subject=" + encodeURIComponent(subject) +
    "&body=" + encodeURIComponent(buildSummary(d));
  window.location.href = url;
}

function succeed(d) {
  document.getElementById("enquiry-form").hidden = true;
  var s = document.getElementById("success");
  s.hidden = false;
  var fb = document.getElementById("mailto-fallback");
  if (fb) {
    var usingService = CONFIG.web3formsKey || CONFIG.formEndpoint;
    if (usingService) { fb.hidden = true; fb.innerHTML = ""; }
    else {
      fb.hidden = false;
      fb.innerHTML = "If your email app didn't open, " +
        '<a href="mailto:' + CONFIG.businessEmail +
        "?subject=" + encodeURIComponent("Home tyre fitting enquiry — " + d.postcode) +
        "&body=" + encodeURIComponent(buildSummary(d)) +
        '">click here to send it</a>.';
    }
  }
  s.scrollIntoView({ behavior: "smooth", block: "center" });
}

/* ---------- helpers ---------- */
function val(id) { var el = document.getElementById(id); return el ? el.value.trim() : ""; }
function setVal(id, v) { var el = document.getElementById(id); if (el) el.value = v; }
function show(el, msg) { if (el) { el.textContent = msg; el.hidden = false; } }
function hide(el) { if (el) el.hidden = true; }
