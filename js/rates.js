/* ===========================================================
   ResQ Tyres — RATE SHEET (bundled fallback)
   -----------------------------------------------------------
   The live prices come from the Google Sheet
   "ResQ Tyres — Website Prices" (see js/prices-sheet.js).
   This file is only used if that sheet can't be reached, so the
   size dropdowns still work and the page never breaks.

   THE RULE:
     1. A size with BOTH "From £" and "To £" filled in is quoted exactly.
     2. Otherwise a car size is quoted from its RIM BAND — the
        "Backup NN inch" rows in the sheet. Van/commercial
        "C" sizes only use a band if a "Backup NNC inch" row exists.
     3. No band and no exact price => the customer is asked to call.
     Prices are PER TYRE. Mobile fitting is charged on top
     (fittingFrom below, overridable by a "Mobile fitting" sheet row).
   =========================================================== */

const RESQ_RATES = {

  /* Rim bands, keyed by rim ("14", "16C"), per tyre. The live sheet's
     "Backup NN inch" rows replace these on every page load; this copy is
     only used if the sheet can't be reached, so the guide still gives the
     headline ranges. The plain price table on the home page is built from
     the same values: after changing them, run tools/build-price-table.py. */
  bands: {
    "14": { low: 40, high: 100 }, "15": { low: 40, high: 100 },
    "16": { low: 40, high: 100 }, "17": { low: 40, high: 100 },
    "18": { low: 80, high: 150 }, "19": { low: 80, high: 150 },
    "20": { low: 80, high: 150 }
  },

  /* Other published prices, used by the plain price table only. */
  punctureRepair: { low: 70, high: 120 },
  jumpStartFrom: 50,
  checked: "October 2026",

  /* Mobile fitting, on top of the tyre price (from £50, depending on
     location). A "Mobile fitting" row in the sheet overrides this. */
  fittingFrom: 50,

  /* Prices, keyed "width/profileRrim" (rim keeps its C for
     commercial/van sizes, e.g. "195/65R16C").
     Empty here on purpose — the sheet is the source of truth. */
  exact: {},

  /* Every size ResQ lists, priced or not. Drives the dropdowns,
     so a customer can always find their size even when we can
     only answer it with a phone call. */
  sizes: [
    { w: 195, p: 55, r: "10C" },
    { w: 165, p: 80, r: "13C" },
    { w: 195, p: 50, r: "13C" },
    { w: 155, p: 65, r: "14" },
    { w: 165, p: 60, r: "14" },
    { w: 165, p: 70, r: "14" },
    { w: 175, p: 65, r: "14" },
    { w: 185, p: 60, r: "14" },
    { w: 185, p: 65, r: "14" },
    { w: 185, p: 70, r: "14" },
    { w: 175, p: 65, r: "14C" },
    { w: 165, p: 60, r: "15" },
    { w: 165, p: 65, r: "15" },
    { w: 175, p: 60, r: "15" },
    { w: 175, p: 65, r: "15" },
    { w: 185, p: 55, r: "15" },
    { w: 185, p: 60, r: "15" },
    { w: 185, p: 65, r: "15" },
    { w: 195, p: 45, r: "15" },
    { w: 195, p: 50, r: "15" },
    { w: 195, p: 55, r: "15" },
    { w: 195, p: 60, r: "15" },
    { w: 195, p: 65, r: "15" },
    { w: 205, p: 55, r: "15" },
    { w: 215, p: 65, r: "15C" },
    { w: 215, p: 70, r: "15C" },
    { w: 185, p: 50, r: "16" },
    { w: 185, p: 55, r: "16" },
    { w: 185, p: 60, r: "16" },
    { w: 195, p: 45, r: "16" },
    { w: 195, p: 50, r: "16" },
    { w: 195, p: 55, r: "16" },
    { w: 195, p: 60, r: "16" },
    { w: 205, p: 45, r: "16" },
    { w: 205, p: 55, r: "16" },
    { w: 205, p: 60, r: "16" },
    { w: 205, p: 65, r: "16" },
    { w: 215, p: 45, r: "16" },
    { w: 215, p: 55, r: "16" },
    { w: 215, p: 60, r: "16" },
    { w: 215, p: 65, r: "16" },
    { w: 225, p: 55, r: "16" },
    { w: 185, p: 75, r: "16C" },
    { w: 195, p: 60, r: "16C" },
    { w: 195, p: 65, r: "16C" },
    { w: 205, p: 65, r: "16C" },
    { w: 205, p: 75, r: "16C" },
    { w: 215, p: 65, r: "16C" },
    { w: 215, p: 75, r: "16C" },
    { w: 225, p: 65, r: "16C" },
    { w: 225, p: 75, r: "16C" },
    { w: 235, p: 65, r: "16C" },
    { w: 195, p: 40, r: "17" },
    { w: 205, p: 40, r: "17" },
    { w: 205, p: 45, r: "17" },
    { w: 205, p: 50, r: "17" },
    { w: 205, p: 55, r: "17" },
    { w: 215, p: 40, r: "17" },
    { w: 215, p: 45, r: "17" },
    { w: 215, p: 50, r: "17" },
    { w: 215, p: 55, r: "17" },
    { w: 215, p: 60, r: "17" },
    { w: 215, p: 65, r: "17" },
    { w: 225, p: 45, r: "17" },
    { w: 225, p: 50, r: "17" },
    { w: 225, p: 55, r: "17" },
    { w: 225, p: 60, r: "17" },
    { w: 235, p: 45, r: "17" },
    { w: 235, p: 55, r: "17" },
    { w: 245, p: 40, r: "17" },
    { w: 235, p: 60, r: "17C" },
    { w: 205, p: 40, r: "18" },
    { w: 215, p: 40, r: "18" },
    { w: 215, p: 45, r: "18" },
    { w: 215, p: 50, r: "18" },
    { w: 215, p: 55, r: "18" },
    { w: 225, p: 40, r: "18" },
    { w: 225, p: 45, r: "18" },
    { w: 225, p: 50, r: "18" },
    { w: 225, p: 55, r: "18" },
    { w: 225, p: 60, r: "18" },
    { w: 235, p: 40, r: "18" },
    { w: 235, p: 45, r: "18" },
    { w: 235, p: 50, r: "18" },
    { w: 235, p: 55, r: "18" },
    { w: 235, p: 60, r: "18" },
    { w: 245, p: 35, r: "18" },
    { w: 245, p: 40, r: "18" },
    { w: 245, p: 45, r: "18" },
    { w: 255, p: 35, r: "18" },
    { w: 255, p: 40, r: "18" },
    { w: 255, p: 60, r: "18" },
    { w: 265, p: 60, r: "18" },
    { w: 205, p: 55, r: "19" },
    { w: 225, p: 35, r: "19" },
    { w: 225, p: 40, r: "19" },
    { w: 225, p: 45, r: "19" },
    { w: 235, p: 35, r: "19" },
    { w: 235, p: 40, r: "19" },
    { w: 235, p: 45, r: "19" },
    { w: 235, p: 50, r: "19" },
    { w: 235, p: 55, r: "19" },
    { w: 245, p: 35, r: "19" },
    { w: 245, p: 40, r: "19" },
    { w: 245, p: 45, r: "19" },
    { w: 255, p: 30, r: "19" },
    { w: 255, p: 35, r: "19" },
    { w: 255, p: 55, r: "19" },
    { w: 265, p: 30, r: "19" },
    { w: 275, p: 35, r: "19" },
    { w: 275, p: 40, r: "19" },
    { w: 295, p: 40, r: "19" },
    { w: 225, p: 35, r: "20" },
    { w: 225, p: 40, r: "20" },
    { w: 235, p: 45, r: "20" },
    { w: 235, p: 50, r: "20" },
    { w: 245, p: 35, r: "20" },
    { w: 245, p: 40, r: "20" },
    { w: 245, p: 45, r: "20" },
    { w: 255, p: 40, r: "20" },
    { w: 255, p: 45, r: "20" },
    { w: 275, p: 40, r: "20" },
    { w: 275, p: 45, r: "20" },
    { w: 305, p: 30, r: "20" },
    { w: 265, p: 30, r: "21" },
    { w: 275, p: 45, r: "21" },
    { w: 285, p: 35, r: "21" },
    { w: 295, p: 35, r: "21" },
    { w: 315, p: 30, r: "21" },
    { w: 285, p: 35, r: "22" },
    { w: 285, p: 40, r: "22" },
    { w: 315, p: 30, r: "22" }
  ],

  /* Locking wheel-nut removal add-on. ResQ carries the specialist
     tools most fitters don't — this is a USP, not just a fee. */
  lockingNutRemoval: { low: 25, high: 40 }
};

/* ===========================================================
   COVERAGE — where ResQ will travel to.
   Used by the postcode checker + the coverage map.
   =========================================================== */
/* Coverage: every LS district, HG1-HG3, WF1-WF13 and the listed York/Selby
   districts. Districts, not letter prefixes: WF14+ is out, and so is
   Bradford (BD). */
const RESQ_COVERAGE = {
  districts: [
    "LS1","LS2","LS3","LS4","LS5","LS6","LS7","LS8","LS9","LS10",
    "LS11","LS12","LS13","LS14","LS15","LS16","LS17","LS18","LS19","LS20",
    "LS21","LS22","LS23","LS24","LS25","LS26","LS27","LS28","LS29",
    "HG1","HG2","HG3",
    "WF1","WF2","WF3","WF4","WF5","WF6","WF7","WF8","WF9","WF10","WF11","WF12","WF13",
    "YO1","YO10","YO24","YO8"
  ],
  towns: [
    "Leeds", "Wakefield", "Dewsbury", "Pudsey",
    "Morley", "Castleford", "Garforth", "Pontefract",
    "Harrogate", "Tadcaster", "York", "Selby"
  ]
};
