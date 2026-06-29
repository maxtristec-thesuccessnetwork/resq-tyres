/* ===========================================================
   ResQ Tyres — Reg → tyre size lookup (front-end)
   Calls /api/tyre-lookup (serverless proxy) and auto-fills the
   estimate tool's width / profile / rim selects.
   Falls back to a small client-side sample table if the API
   isn't reachable (e.g. opening the file locally without Vercel),
   so the flow can still be demonstrated offline.
   =========================================================== */
(function () {
  "use strict";

  var btn = document.getElementById("vrm-btn");
  var input = document.getElementById("vrm-lookup");
  var status = document.getElementById("vrm-status");
  if (!btn || !input) return;

  /* offline/demo fallback used only if the API call itself fails */
  var SAMPLE = {
    _default: { make: "Vehicle", model: "Sample vehicle", size: "205/55R16" },
    AB12CDE: { make: "Volkswagen", model: "Golf 1.6 TDI", size: "205/55R16" },
    LA15XYZ: { make: "Ford", model: "Fiesta Zetec", size: "195/55R16" },
    RA14POR: { make: "Volkswagen", model: "Sharan 2.0 TDi SEL", size: "225/50R17" }
  };

  function clean(v) { return (v || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 8); }

  function parseSize(str) {
    var m = String(str || "").match(/(\d{3})\s*\/\s*(\d{2})\s*R?\s*(\d{2})/i);
    if (!m) return null;
    return { label: m[1] + "/" + m[2] + " R" + m[3], width: +m[1], profile: +m[2], rim: +m[3] };
  }

  function setSelect(id, value) {
    var sel = document.getElementById(id);
    if (!sel) return;
    var v = String(value);
    var found = Array.prototype.some.call(sel.options, function (o) { return o.value === v; });
    if (!found) {
      var opt = document.createElement("option");
      opt.value = v; opt.textContent = v;
      sel.appendChild(opt);
    }
    sel.value = v;
  }

  function showStatus(kind, html) {
    status.hidden = false;
    status.className = "rl-status " + kind;
    status.innerHTML = html;
  }

  function setLoading(on) {
    btn.disabled = on;
    btn.classList.toggle("loading", on);
    var label = btn.querySelector("span");
    if (label) label.textContent = on ? "Searching…" : "Find my size";
  }

  function applyResult(data) {
    if (!data || !data.size) { return fail("We couldn't read a tyre size for that vehicle. Please enter it below."); }
    setSelect("width", data.size.width);
    setSelect("profile", data.size.profile);
    setSelect("rim", data.size.rim);

    // copy the reg into the estimate form so it isn't typed twice
    var reg = document.getElementById("reg");
    if (reg && !reg.value) reg.value = data.vrm || clean(input.value);

    var vehicle = [data.make, data.model].filter(Boolean).join(" ");
    var demo = data.source === "mock" ? ' <span class="rl-demo">demo</span>' : "";
    showStatus("ok",
      '<svg class="icon" aria-hidden="true"><use href="#i-check-circle"/></svg> ' +
      (vehicle ? "<b>" + vehicle + "</b> — " : "") +
      "tyre size <b>" + data.size.label + "</b>. We've filled it in below." + demo);

    // if a postcode is already entered, show the estimate straight away
    var pc = document.getElementById("postcode");
    var form = document.getElementById("estimate-form");
    if (pc && pc.value.trim() && form) {
      if (form.requestSubmit) form.requestSubmit();
      else form.dispatchEvent(new Event("submit", { cancelable: true }));
    } else if (pc) {
      pc.focus();
    }
  }

  function fail(msg) { showStatus("err",
    '<svg class="icon" aria-hidden="true"><use href="#i-alert"/></svg> ' + msg); }

  function lookup() {
    var vrm = clean(input.value);
    input.value = vrm;
    if (vrm.length < 2) { fail("Please enter your registration."); input.focus(); return; }
    setLoading(true);
    status.hidden = true;

    fetch("/api/tyre-lookup?vrm=" + encodeURIComponent(vrm), { headers: { Accept: "application/json" } })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
      .then(function (res) {
        setLoading(false);
        if (res.ok && res.body && res.body.ok) applyResult(res.body);
        else fail((res.body && res.body.message) || "We couldn't find that reg. Please enter your size below.");
      })
      .catch(function () {
        // API unreachable (e.g. local file://) → client-side sample so the demo still works
        setLoading(false);
        var rec = SAMPLE[vrm] || SAMPLE._default;
        applyResult({ source: "mock", vrm: vrm, make: rec.make, model: rec.model, size: parseSize(rec.size) });
      });
  }

  btn.addEventListener("click", lookup);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); lookup(); }
  });
})();
