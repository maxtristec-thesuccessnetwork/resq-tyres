/* ===========================================================
   ResQ Tyres — RATE SHEET (bundled fallback)
   -----------------------------------------------------------
   The live prices come from the Google Sheet
   "ResQ Tyres — Website Prices" (see js/prices-sheet.js).
   This file is only used if that sheet can't be reached, so the
   size dropdowns still work and the page never breaks.

   ONE RULE, everywhere:
     A size shows a price ONLY if the sheet has BOTH "From £"
     and "To £" filled in for it. Anything else tells the
     customer to call. There is no estimating, no rim band and
     no guessing — if ResQ hasn't priced it, we don't quote it.
   =========================================================== */

const RESQ_RATES = {

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
/* Coverage. The exact districts Moin confirmed by WhatsApp on 2026-09-01:
   "all LS postcode hg1,hg2,hg3 Wf1,wf2,wf3,wf4,wf5" + "Include them please bro"
   (WF8/WF10/WF12/WF13) + "And ls24 tadcaster". Bradford (BD) is out.
   Districts, not letter prefixes — WF6, WF7, WF9 and WF11 are NOT covered, and the
   old prefix check was telling those callers they were in the usual area. */
const RESQ_COVERAGE = {
  districts: [
    "LS1","LS2","LS3","LS4","LS5","LS6","LS7","LS8","LS9","LS10",
    "LS11","LS12","LS13","LS14","LS15","LS16","LS17","LS18","LS19","LS20",
    "LS21","LS22","LS23","LS24","LS25","LS26","LS27","LS28","LS29",
    "HG1","HG2","HG3",
    "WF1","WF2","WF3","WF4","WF5","WF8","WF10","WF12","WF13"
  ],
  towns: [
    "Leeds", "Wakefield", "Dewsbury", "Pudsey",
    "Morley", "Castleford", "Garforth", "Pontefract",
    "Harrogate", "Tadcaster"
  ]
};
