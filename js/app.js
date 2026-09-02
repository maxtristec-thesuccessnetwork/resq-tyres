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
  businessEmail: "resqtyresrecovery@gmail.com",
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
});

/* ---------- Coverage map ----------
   Now a self-hosted static SVG inlined in index.html (#areas). The old
   Leaflet + CARTO tile map was removed 2026-09-02 (card W5, option A):
   CARTO began watermarking unauthenticated tiles "API KEY REQUIRED".
   Regenerate the SVG with tools/build-coverage-map.py. */

/* ---------- Price guide ----------
   THE RULE: a size shows a price only if ResQ has filled in BOTH price
   columns for it in the sheet. Every other size still appears in the
   dropdowns (so the customer can find their tyre) but is answered with
   "call us". Nothing is estimated, banded or guessed. */

var DEFAULT_SIZE = { w: 205, p: 55, r: "16" };

function sizeKey(w, p, r) { return w + "/" + p + "R" + String(r).toUpperCase(); }
function allSizes() { return (typeof RESQ_RATES !== "undefined" && RESQ_RATES.sizes) || []; }

function uniq(list) {
  var seen = {}, out = [];
  list.forEach(function (v) { if (!seen[v]) { seen[v] = 1; out.push(v); } });
  return out;
}
function byNumber(a, b) { return a - b; }
// "14" < "14C" < "15" — commercial/van sizes sit next to their car equivalent.
function byRim(a, b) {
  var na = parseInt(a, 10), nb = parseInt(b, 10);
  if (na !== nb) return na - nb;
  return (/C$/.test(a) ? 1 : 0) - (/C$/.test(b) ? 1 : 0);
}

function widthOptions() {
  return uniq(allSizes().map(function (s) { return s.w; })).sort(byNumber);
}
function profileOptions(w) {
  return uniq(allSizes().filter(function (s) { return s.w === w; })
    .map(function (s) { return s.p; })).sort(byNumber);
}
function rimOptions(w, p) {
  return uniq(allSizes().filter(function (s) { return s.w === w && s.p === p; })
    .map(function (s) { return s.r; })).sort(byRim);
}

// Rebuild a <select>, keeping the current choice if it's still valid.
// Returns the value that ended up selected.
function setOptions(id, values, prefer) {
  var sel = document.getElementById(id);
  if (!sel || !values.length) return null;
  var strs = values.map(String);
  var want = (prefer != null && strs.indexOf(String(prefer)) >= 0) ? String(prefer) : strs[0];
  while (sel.firstChild) sel.removeChild(sel.firstChild);
  values.forEach(function (v) {
    var opt = document.createElement("option");
    opt.value = String(v);
    opt.textContent = String(v);
    sel.appendChild(opt);
  });
  sel.value = want;
  return sel.value;
}

// Cascade: width narrows the profiles, profile narrows the rims. A customer
// can only ever assemble a size that genuinely exists.
function refreshSizeSelects(keep) {
  if (!document.getElementById("width")) return;
  var widths = widthOptions();
  if (!widths.length) return;

  var w = parseInt(setOptions("width", widths, keep && keep.w ? keep.w : DEFAULT_SIZE.w), 10);
  var p = parseInt(setOptions("profile", profileOptions(w), keep && keep.p ? keep.p : DEFAULT_SIZE.p), 10);
  setOptions("rim", rimOptions(w, p), keep && keep.r ? keep.r : DEFAULT_SIZE.r);
}

function currentSize() {
  return { w: parseInt(val("width"), 10), p: parseInt(val("profile"), 10), r: val("rim") };
}

function populateSelects() {
  refreshSizeSelects(null);

  var wSel = document.getElementById("width"), pSel = document.getElementById("profile");
  if (wSel) wSel.addEventListener("change", function () {
    var w = parseInt(val("width"), 10);
    var p = parseInt(setOptions("profile", profileOptions(w), val("profile")), 10);
    setOptions("rim", rimOptions(w, p), val("rim"));
  });
  if (pSel) pSel.addEventListener("change", function () {
    setOptions("rim", rimOptions(parseInt(val("width"), 10), parseInt(val("profile"), 10)), val("rim"));
  });
}

// Called by prices-sheet.js once the live sheet lands.
window.RESQ_onRatesUpdated = function () { refreshSizeSelects(currentSize()); };

// The price range for a size, or null if ResQ hasn't priced it.
function rangeForSize(width, profile, rim) {
  var e = (typeof RESQ_RATES !== "undefined" && RESQ_RATES.exact) || {};
  return e[sizeKey(width, profile, rim)] || null;
}

var ResQState = { size: "", lockingNut: "yes", range: null, usedTool: false };

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
    ResQState.range = range;          // null when ResQ hasn't priced this size
    ResQState.usedTool = true;

    renderRange(sizeLabel, range, lockingNut);

    var results = document.getElementById("estimate-results");
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}

function renderRange(sizeLabel, range, lockingNut) {
  document.getElementById("size-label").textContent = sizeLabel;

  var lead  = document.getElementById("results-lead");
  var box   = document.getElementById("range-box");
  var call  = document.getElementById("quote-call");
  var micro = document.getElementById("results-micro");
  var priced = !!range;

  if (box)  box.hidden  = !priced;
  if (call) call.hidden = priced;

  if (priced) {
    if (lead) lead.textContent = "Typical fitted price for";
    document.getElementById("range-out").innerHTML =
      "£" + range.low + "<span class='dash'>–</span>£" + range.high +
      "<small>per tyre, fitted</small>";
    if (micro) micro.textContent =
      "A guide only — the final price is confirmed by phone. Prices are per tyre, mobile fitting included.";
  } else {
    // ResQ hasn't priced this size. We don't guess — we ask them to call.
    if (lead) lead.textContent = "Your tyre size:";
    if (micro) micro.textContent =
      "Mobile fitting included, pay on completion. Leeds, Wakefield and across West Yorkshire.";
  }

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
    // A UK inward code is always 3 characters, and the shortest full postcode is
    // 5 (e.g. M1 1AA). Below that, take what they typed as the district itself —
    // so "LS28" on its own still works.
    var outward = raw.length >= 5 ? raw.slice(0, -3) : raw;
    var m = outward.match(/^[A-Z]{1,2}[0-9][0-9A-Z]?$/);
    if (!m) {
      showPC(out, "warn",
        '<svg class="icon" aria-hidden="true"><use href="#i-alert"/></svg> ' +
        "That doesn't look like a full postcode — try again, or call us on " +
        '<a href="tel:07438562633">07438&nbsp;562633</a>.');
      return;
    }
    if (RESQ_COVERAGE.districts.indexOf(outward) !== -1) {
      showPC(out, "ok",
        '<svg class="icon" aria-hidden="true"><use href="#i-check-circle"/></svg> ' +
        "Great news — <b>" + outward + "</b> is in our coverage area. Call us or plan a home fitting below.");
    } else {
      showPC(out, "warn",
        '<svg class="icon" aria-hidden="true"><use href="#i-alert"/></svg> ' +
        "<b>" + outward + "</b> is outside the districts we cover, but we may still be able to reach you — " +
        'give us a quick call on <a href="tel:07438562633">07438&nbsp;562633</a> to check.');
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
  var r = ResQState.range;                       // null = size not priced in the sheet
  if (!ResQState.usedTool) {
    return { range: "Not calculated (customer didn't use the price guide)", locking: "Not asked", total: "" };
  }
  var needsRemoval = ResQState.lockingNut === "no";
  var a = RESQ_RATES.lockingNutRemoval || { low: 0, high: 0 };
  var lockingTxt = needsRemoval
    ? "Yes — no key (" + (a.high > 0 ? "£" + a.low + "–£" + a.high : "no extra charge") + ")"
    : "No";

  // Size has no price in the sheet — flag it so ResQ knows to quote it himself.
  if (!r) {
    return {
      range: "NOT PRICED IN SHEET — customer was shown \"call for a price\". Quote this one manually.",
      locking: lockingTxt,
      total: ""
    };
  }

  var rangeTxt = "£" + r.low + "–£" + r.high + " per tyre, fitted";
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
