/* ===========================================================
   ResQ Tyres — app logic (Plan 2)
   - builds the estimate from js/rates.js
   - validates the forms (REG, tyre size, postcode mandatory)
   - sends the enquiry to the business
   =========================================================== */

/* ---- CONFIG: set these before going live ---- */
const CONFIG = {
  // Where enquiries go (used by Web3Forms and the mailto fallback).
  businessEmail: "maxtristec@googlemail.com",
  // Free, no account needed: go to https://web3forms.com, enter the email above,
  // they email you an Access Key. Paste it here and submissions arrive automatically.
  web3formsKey: "",
  // (Optional) alternative custom endpoint, e.g. Formspree. Leave "" if using Web3Forms.
  formEndpoint: ""
};

document.addEventListener("DOMContentLoaded", function () {
  // year in footer
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  populateSelects();
  wireEstimateForm();
  wireEnquiryForm();
});

/* ---------- Estimate ---------- */
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

function priceForSize(width, profile, rim) {
  var key = width + "/" + profile + "R" + rim;
  if (RESQ_RATES.exact[key]) return RESQ_RATES.exact[key];
  // fallback by rim
  var fb = RESQ_RATES.fallbackByRim;
  var base = fb.base[rim] || 60;
  return {
    budget: base,
    mid: Math.round(base * fb.midMultiplier),
    premium: Math.round(base * fb.premiumMultiplier)
  };
}

function wireEstimateForm() {
  var form = document.getElementById("estimate-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var err = document.getElementById("estimate-error");
    var reg = val("reg");
    var postcode = val("postcode");

    if (!reg || !postcode) {
      show(err, "Please enter your registration and postcode.");
      return;
    }
    hide(err);

    var width = val("width"), profile = val("profile"), rim = val("rim");
    var sizeLabel = width + "/" + profile + " R" + rim;
    var prices = priceForSize(width, profile, rim);
    renderOptions(sizeLabel, prices);

    // remember for the enquiry form
    ResQState.size = sizeLabel;
    ResQState.reg = reg;
    ResQState.postcode = postcode;

    var results = document.getElementById("estimate-results");
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}

var ResQState = { size: "", reg: "", postcode: "", tier: "Mid-range", price: null };

function renderOptions(sizeLabel, prices) {
  document.getElementById("size-label").textContent = sizeLabel;
  var box = document.getElementById("options");
  box.innerHTML = "";
  var tiers = [
    { tier: "Budget", price: prices.budget, note: "Reliable everyday tyre" },
    { tier: "Mid-range", price: prices.mid, note: "Great balance of price & life" },
    { tier: "Premium", price: prices.premium, note: "Top brand, best grip" }
  ];
  tiers.forEach(function (t, i) {
    var div = document.createElement("div");
    div.className = "opt" + (i === 1 ? " sel" : "");
    div.innerHTML =
      '<div class="tier">' + t.tier + "</div>" +
      '<div class="price">£' + t.price + '<small>/tyre</small></div>' +
      '<div class="note">' + t.note + "<br>+ mobile fitting incl.</div>";
    div.addEventListener("click", function () {
      document.querySelectorAll(".opt").forEach(function (x) { x.classList.remove("sel"); });
      div.classList.add("sel");
      ResQState.tier = t.tier;
      ResQState.price = t.price;
    });
    box.appendChild(div);
  });
  // default selection = mid
  ResQState.tier = "Mid-range";
  ResQState.price = prices.mid;

  // "send for approval" -> prefill + jump to enquiry form
  document.getElementById("to-enquiry").onclick = function () {
    setVal("reg2", ResQState.reg);
    setVal("tyresize2", ResQState.size);
    setVal("postcode2", ResQState.postcode);
    setVal("message",
      "Estimate request: " + ResQState.size + " (" + ResQState.tier +
      ", approx £" + ResQState.price + "/tyre). Please confirm price & a time.");
    document.getElementById("enquiry").scrollIntoView({ behavior: "smooth" });
    var nameEl = document.getElementById("name");
    if (nameEl) nameEl.focus();
  };
}

/* ---------- Enquiry ---------- */
function wireEnquiryForm() {
  var form = document.getElementById("enquiry-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var err = document.getElementById("enquiry-error");

    var data = {
      name: val("name"),
      phone: val("phone"),
      reg: val("reg2"),
      tyresize: val("tyresize2"),
      postcode: val("postcode2"),
      email: val("email"),
      message: val("message")
    };

    // mandatory: name, phone, reg, tyre size, postcode
    if (!data.name || !data.phone || !data.reg || !data.tyresize || !data.postcode) {
      show(err, "Please fill in your name, phone, registration, tyre size and postcode.");
      return;
    }
    hide(err);

    if (CONFIG.web3formsKey) {
      sendViaWeb3Forms(data, form, err);
    } else if (CONFIG.formEndpoint) {
      sendToEndpoint(CONFIG.formEndpoint, data, form, err);
    } else {
      // Demo mode (no key yet): open the customer's email app, prefilled.
      openMailto(data);
      succeed(data);
    }
  });
}

function sendViaWeb3Forms(data, form, err) {
  var payload = {
    access_key: CONFIG.web3formsKey,
    subject: "Website enquiry — " + data.reg + " (" + data.postcode + ")",
    from_name: data.name,
    email: data.email || CONFIG.businessEmail,
    // human-readable body + individual fields
    message: buildSummary(data),
    name: data.name, phone: data.phone, registration: data.reg,
    tyre_size: data.tyresize, postcode: data.postcode
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
  }).catch(function () {
    openMailto(data); succeed(data);
  });
}

function buildSummary(d) {
  return (
    "New website enquiry — ResQ Tyres\n\n" +
    "Name: " + d.name + "\n" +
    "Phone: " + d.phone + "\n" +
    "Email: " + (d.email || "-") + "\n" +
    "Registration: " + d.reg + "\n" +
    "Tyre size: " + d.tyresize + "\n" +
    "Postcode: " + d.postcode + "\n" +
    "Message: " + (d.message || "-") + "\n"
  );
}

function openMailto(d) {
  var subject = "Website enquiry — " + d.reg + " (" + d.postcode + ")";
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
    fb.innerHTML = "If your email app didn't open, " +
      '<a href="mailto:' + CONFIG.businessEmail +
      "?subject=" + encodeURIComponent("Website enquiry — " + d.reg) +
      "&body=" + encodeURIComponent(buildSummary(d)) +
      '">click here to send it</a>.';
  }
  s.scrollIntoView({ behavior: "smooth", block: "center" });
}

/* ---------- helpers ---------- */
function val(id) { var el = document.getElementById(id); return el ? el.value.trim() : ""; }
function setVal(id, v) { var el = document.getElementById(id); if (el) el.value = v; }
function show(el, msg) { if (el) { el.textContent = msg; el.hidden = false; } }
function hide(el) { if (el) el.hidden = true; }
