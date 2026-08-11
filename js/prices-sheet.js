/* ResQ Tyres — live prices loader.
   Reads the "ResQ Tyres — Website Prices" Google Sheet so ResQ can update
   prices himself (no developer, no redeploy).

   THE RULE:
     A size is quoted ONLY if its row has BOTH "From £" and "To £" filled in.
     A row with a size but no prices still appears in the dropdowns — the
     customer just gets "call us for a price" instead of a number.
     Nothing is ever estimated, banded or guessed.

   Adding a size row makes that size selectable. Filling in its two price
   columns turns the price on. That's the whole system.

   If the sheet can't be reached, the site falls back to the sizes bundled
   in rates.js and quotes nothing. */
(function () {
  var SHEET_ID = "1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk";
  // cache-buster: gviz will happily serve a stale copy for hours otherwise,
  // which is how ResQ ends up "having changed the price" with no effect.
  var CSV_URL =
    "https://docs.google.com/spreadsheets/d/" + SHEET_ID +
    "/gviz/tq?tqx=out:csv&_=" + Date.now();

  if (typeof RESQ_RATES === "undefined") return; // rates.js (fallback) loads first

  fetch(CSV_URL, { cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
    .then(function (csv) { applyRates(parseCSV(csv)); })
    .catch(function (e) {
      if (window.console) console.warn("ResQ prices: sheet unavailable, using bundled sizes —", e.message);
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

  // A price cell. Blank / non-numeric / zero-or-less => no price.
  function money(v) {
    var s = String(v == null ? "" : v).trim();
    if (s === "") return null;
    var n = parseFloat(s.replace(/[^0-9.\-]/g, ""));
    if (isNaN(n) || n <= 0) return null;
    return Math.round(n);
  }
  function int(v) {
    var n = parseInt(String(v == null ? "" : v).replace(/[^0-9]/g, ""), 10);
    return isNaN(n) ? null : n;
  }
  // Rim keeps its C: "16c" -> "16C". Commercial/van tyres are a different
  // size and a different price from the same number in car fitment.
  function rim(v) {
    var s = String(v == null ? "" : v).trim().toUpperCase().replace(/[^0-9C]/g, "");
    return /^\d{2}C?$/.test(s) ? s : null;
  }

  function parseCSV(text) {
    return text.replace(/\r/g, "").split("\n").filter(function (l) { return l.trim() !== ""; }).map(splitLine);
  }

  function applyRates(rows) {
    var exact = {}, sizes = [], seen = {}, addon = null;
    var priced = 0, listed = 0, ignored = 0;

    rows.forEach(function (cols) {
      var label = (cols[0] || "").trim();
      if (label === "" || /^width$/i.test(label)) return;      // header / spacer

      var from = money(cols[3]), to = money(cols[4]);

      if (/^\d/.test(label)) {
        // ---- a tyre size row ----
        var w = int(cols[0]), p = int(cols[1]), r = rim(cols[2]);
        if (!w || !p || !r) return;
        var key = w + "/" + p + "R" + r;
        if (!seen[key]) { seen[key] = 1; sizes.push({ w: w, p: p, r: r }); listed++; }
        // Price only when BOTH columns are filled and sane.
        if (from != null && to != null) {
          exact[key] = { low: Math.min(from, to), high: Math.max(from, to) };
          priced++;
        }
      } else if (/locking/i.test(label)) {
        if (from != null && to != null) addon = { low: Math.min(from, to), high: Math.max(from, to) };
      } else {
        // Anything else (the old "Backup NN inch" rim bands) is deliberately
        // ignored. We no longer estimate a price from rim diameter — those
        // rows can be deleted from the sheet.
        ignored++;
      }
    });

    if (listed > 0) {
      RESQ_RATES.sizes = sizes;
      RESQ_RATES.exact = exact;
    }
    if (addon) RESQ_RATES.lockingNutRemoval = addon;

    if (window.console) {
      console.log("ResQ prices: " + listed + " sizes listed, " + priced + " with a price." +
        (ignored ? " " + ignored + " unused row(s) ignored." : ""));
    }

    // Rebuild the dropdowns now the real list has landed.
    if (typeof window.RESQ_onRatesUpdated === "function") window.RESQ_onRatesUpdated();
  }
})();
