/* ResQ Tyres — live prices loader.
   Reads the "ResQ Tyres — Website Prices" Google Sheet so ResQ can update
   prices himself (no developer, no redeploy).

   THE RULE (revised 7 Sept 2026):
     1. A size row with BOTH "From £" and "To £" is quoted exactly.
     2. Otherwise a car size is quoted from its rim band — the "Backup NN inch"
        rows, which Moin filled with his own numbers on 7 Sept. A van/commercial
        "C" size only uses a band from a "Backup NNC inch" row.
     3. No exact price and no band => "call us for a price".
     A "Mobile fitting" row (From £) sets the fitting-from price shown beside
     every quote. Prices are per tyre; fitting is on top.

   WHY THERE ARE THREE FETCHES  (fixed 8 Sept 2026)
     Google's gviz endpoint types each column by whatever most of it contains,
     then returns every cell that does not match that type as EMPTY. Two
     columns of this sheet are mixed, and both were losing data in transit:

       Column A — ~134 tyre widths + 8 text labels. Typed NUMBER, so
       "Backup 14 inch", "Locking Wheel Nut Removal" and "Mobile fitting"
       arrived blank. No rim bands were ever loaded, so EVERY size on the live
       site answered "we don't list it online" while the ads promised
       "Tyres from £40". That was the state from 2-8 September.

       Column C — 115 car rims (numbers) + 18 van rims ("16c", "15c"...).
       Typed NUMBER, so every van and commercial size arrived with no rim and
       was dropped from the dropdowns entirely. 18 sizes ResQ fits were
       invisible to customers.

     The sheet was correct throughout. The transport was lying about it.

     Pass 1  reads the whole sheet — car sizes and any exact prices.
     Pass 2  re-reads the van block, where column C is all text, so the "c"
             rims survive. Located by finding rows that have a width and a
             profile but lost their rim.
     Pass 3  re-reads the tail, where column A is all text, so the labels
             survive. Located from the last row carrying a width.

     Both tails are located from pass 1's own output, so they follow the sheet
     down as rows are added. If either extra pass fails the site still works,
     just with less of the sheet — and the console says which part is missing.

   If the sheet can't be reached at all, the site falls back to the sizes
   bundled in rates.js and quotes nothing. */
(function () {
  var SHEET_ID = "1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk";
  var GVIZ = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv";
  // cache-buster: gviz will happily serve a stale copy for hours otherwise,
  // which is how ResQ ends up "having changed the price" with no effect.
  function bust() { return "&_=" + Date.now(); }

  // How far past the last size row to look for the label block. The small
  // overlap backwards keeps the block in range if a spacer row moves.
  var TAIL_LOOKBACK = 2;
  var TAIL_DEPTH = 60;

  if (typeof RESQ_RATES === "undefined") return; // rates.js (fallback) loads first

  fetch(GVIZ + bust(), { cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
    .then(function (csv) {
      var rows = parseCSV(csv);
      return Promise.all([
        range(vanBlock(rows)).catch(warn("van sizes")),
        range(labelBlock(rows)).catch(warn("price bands"))
      ]).then(function (extra) { applyRates(rows, extra[0], extra[1]); });
    })
    .catch(function (e) {
      if (window.console) console.warn("ResQ prices: sheet unavailable, using bundled sizes —", e.message);
    });

  function warn(what) {
    return function (e) {
      if (window.console) console.warn("ResQ prices: could not re-read " + what + " —", e.message);
      return [];
    };
  }

  // Re-read a span of sheet rows. Within a narrower range the mixed column is
  // no longer majority-numeric, so gviz types it as text and keeps the values.
  function range(span) {
    if (!span) return Promise.resolve([]);
    var url = GVIZ + "&headers=0&range=A" + span[0] + ":E" + span[1] + bust();
    return fetch(url, { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
      .then(parseCSV);
  }

  // Van/commercial rows: a width and a profile, but the rim went missing.
  function vanBlock(rows) {
    var first = 0, last = 0;
    for (var i = 0; i < rows.length; i++) {
      var c = rows[i];
      if (str(c[0]) && str(c[1]) && !str(c[2])) { if (!first) first = i + 1; last = i + 1; }
    }
    return first ? [first, last] : null;
  }

  // The label block: everything past the last row that carries a width.
  function labelBlock(rows) {
    var lastSize = 0;
    for (var i = 0; i < rows.length; i++) {
      if (/^\s*\d/.test(str(rows[i][0]))) lastSize = i + 1;
    }
    if (!lastSize) return null;
    return [Math.max(2, lastSize - TAIL_LOOKBACK + 1), lastSize + TAIL_DEPTH];
  }

  function str(v) { return String(v == null ? "" : v).trim(); }

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
    var s = str(v);
    if (s === "") return null;
    var n = parseFloat(s.replace(/[^0-9.\-]/g, ""));
    if (isNaN(n) || n <= 0) return null;
    return Math.round(n);
  }
  function int(v) {
    var n = parseInt(str(v).replace(/[^0-9]/g, ""), 10);
    return isNaN(n) ? null : n;
  }
  // Rim keeps its C: "16c" -> "16C". Commercial/van tyres are a different
  // size and a different price from the same number in car fitment.
  function rim(v) {
    var s = str(v).toUpperCase().replace(/[^0-9C]/g, "");
    return /^\d{2}C?$/.test(s) ? s : null;
  }
  function pair(cols) {
    var from = money(cols[3]), to = money(cols[4]);
    if (from == null || to == null) return null;
    return { low: Math.min(from, to), high: Math.max(from, to) };
  }

  function parseCSV(text) {
    return text.replace(/\r/g, "").split("\n").filter(function (l) { return l.trim() !== ""; }).map(splitLine);
  }

  function applyRates(rows, vanRows, labelRows) {
    var exact = {}, sizes = [], seen = {}, addon = null, bands = {}, fitting = null;
    var priced = 0, vans = 0, ignored = 0;

    function addSize(cols) {
      var w = int(cols[0]), p = int(cols[1]), r = rim(cols[2]);
      if (!w || !p || !r) return false;
      var key = w + "/" + p + "R" + r;
      if (!seen[key]) { seen[key] = 1; sizes.push({ w: w, p: p, r: r }); }
      var ex = pair(cols);                 // price only when BOTH columns are sane
      if (ex && !exact[key]) { exact[key] = ex; priced++; }
      return true;
    }

    // ---- car sizes and exact prices, from the whole sheet ----
    rows.forEach(function (cols) {
      var label = str(cols[0]);
      if (label === "" || /^width$/i.test(label)) return;      // header / spacer
      if (!/^\d/.test(label)) return;                          // a label row; pass 3 owns those
      addSize(cols);
    });

    // ---- van and commercial sizes, from the re-read block ----
    vanRows.forEach(function (cols) {
      if (!/^\d/.test(str(cols[0]))) return;
      var before = sizes.length;
      addSize(cols);
      if (sizes.length > before) vans++;
    });

    // ---- bands, locking nut and fitting, from the tail ----
    labelRows.forEach(function (cols) {
      var label = str(cols[0]);
      if (label === "" || /^\d/.test(label)) return;           // blank, spacer, or a size row

      var band = label.match(/^backup\s+(\d{2}C?)\s*inch/i);
      if (band) {
        // "Backup 16 inch" -> bands["16"], "Backup 16C inch" -> bands["16C"].
        var v = pair(cols);
        if (v) bands[band[1].toUpperCase()] = v;
      } else if (/locking/i.test(label)) {
        var a = pair(cols);
        if (a) addon = a;
      } else if (/mobile\s*fitting/i.test(label)) {
        var f = money(cols[3]);
        if (f != null) fitting = f;
      } else {
        ignored++;
      }
    });

    if (sizes.length) {
      RESQ_RATES.sizes = sizes;
      RESQ_RATES.exact = exact;
    }
    if (addon) RESQ_RATES.lockingNutRemoval = addon;
    RESQ_RATES.bands = bands;
    if (fitting != null) RESQ_RATES.fittingFrom = fitting;

    if (window.console) {
      var banded = 0, unpriced = [];
      sizes.forEach(function (sz) {
        if (exact[sz.w + "/" + sz.p + "R" + sz.r]) return;
        if (bands[sz.r]) banded++; else unpriced.push(sz.r);
      });
      var rims = unpriced.filter(function (r, i) { return unpriced.indexOf(r) === i; }).sort();
      console.log("ResQ prices: " + sizes.length + " sizes listed (" + vans + " van/commercial), " +
        priced + " priced exactly, " + banded + " priced by rim band (" +
        (Object.keys(bands).join(", ") || "none") + "), " + unpriced.length +
        " still call-for-price" + (rims.length ? " [rims " + rims.join(", ") + "]" : "") +
        ", fitting from £" + RESQ_RATES.fittingFrom + "." +
        (ignored ? " " + ignored + " unused row(s) ignored." : ""));
      if (!Object.keys(bands).length) {
        console.warn("ResQ prices: NO rim bands loaded — every size will say 'call us'. " +
          "Check the 'Backup NN inch' rows are still in column A of the sheet.");
      }
    }

    // Rebuild the dropdowns now the real list has landed.
    if (typeof window.RESQ_onRatesUpdated === "function") window.RESQ_onRatesUpdated();
  }
})();
