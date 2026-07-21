/* ResQ Tyres — live prices loader.
   Reads the "ResQ Tyres — Website Prices" Google Sheet so ResQ can update
   prices themselves (no developer, no redeploy). If the sheet can't be
   reached, the site quietly keeps the prices bundled in rates.js. */
(function () {
  var SHEET_ID = "1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk";
  var CSV_URL =
    "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv";

  if (typeof RESQ_RATES === "undefined") return; // rates.js (fallback) loads first

  fetch(CSV_URL, { cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
    .then(function (csv) { applyRates(parseCSV(csv)); })
    .catch(function (e) {
      if (window.console) console.warn("ResQ prices: sheet unavailable, using bundled prices —", e.message);
    });

  function splitLine(line) {
    var out = [], cur = "", q = false;
    for (var i = 0; i < line.length; i++) {
      var c = line[i];
      if (q) {
        if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
        else if (c === '"') q = false;
        else cur += c;
      } else {
        if (c === '"') q = true;
        else if (c === ",") { out.push(cur); cur = ""; }
        else cur += c;
      }
    }
    out.push(cur);
    return out;
  }
  function num(v) { var n = parseFloat(String(v).replace(/[^0-9.\-]/g, "")); return isNaN(n) ? null : Math.round(n); }

  function parseCSV(text) {
    return text.replace(/\r/g, "").split("\n").filter(function (l) { return l.trim() !== ""; }).map(splitLine);
  }

  function applyRates(rows) {
    var exact = {}, fbLow = {}, fbHigh = {}, addon = null, count = 0;
    rows.forEach(function (cols) {
      var label = (cols[0] || "").trim();
      var from = num(cols[3]), to = num(cols[4]);
      var mBackup = label.match(/backup\s*(\d+)/i);
      if (/^\d/.test(label)) {
        var w = num(cols[0]), p = num(cols[1]), r = num(cols[2]);
        if (w && p && r && from != null && to != null) { exact[w + "/" + p + "R" + r] = { low: from, high: to }; count++; }
      } else if (/locking/i.test(label)) {
        if (from != null && to != null) addon = { low: from, high: to };
      } else if (mBackup) {
        var rim = parseInt(mBackup[1], 10);
        if (from != null) fbLow[rim] = from;
        if (to != null) fbHigh[rim] = to;
      }
    });
    if (count > 0) RESQ_RATES.exact = exact;
    if (Object.keys(fbLow).length) RESQ_RATES.fallbackByRim = { low: fbLow, high: fbHigh };
    if (addon) RESQ_RATES.lockingNutRemoval = addon;
    if (window.console) console.log("ResQ prices: loaded " + count + " sizes from sheet.");
  }
})();
