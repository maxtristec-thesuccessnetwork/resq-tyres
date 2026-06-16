/* ===========================================================
   ResQ Tyres — RATE SHEET  (this is the "spreadsheet" you update)
   -----------------------------------------------------------
   To change prices site-wide, edit the numbers below and save.
   These are SAMPLE rates — replace with ResQ's real prices.

   Two ways prices are worked out:
   1) EXACT_PRICES — specific tyre sizes with set prices (most accurate).
   2) FALLBACK — if a size isn't listed, a price is estimated from the
      rim diameter so the tool always returns something.

   Each price has three tiers: budget / mid / premium (per tyre,
   mobile fitting included).
   =========================================================== */

const RESQ_RATES = {

  // 1) EXACT prices for common sizes. Key = "width/profileRrim".
  //    Add or edit rows here as ResQ's price list changes.
  exact: {
    "195/65R15": { budget: 49,  mid: 65,  premium: 89  },
    "205/55R16": { budget: 59,  mid: 79,  premium: 109 },
    "225/45R17": { budget: 72,  mid: 95,  premium: 139 },
    "225/40R18": { budget: 85,  mid: 115, premium: 165 },
    "245/40R19": { budget: 110, mid: 149, premium: 209 }
  },

  // 2) Fallback estimate by rim size (used when a size isn't in 'exact').
  //    base = budget price for that rim; mid/premium are multipliers.
  fallbackByRim: {
    base:    { 14: 45, 15: 49, 16: 59, 17: 72, 18: 89, 19: 110, 20: 135 },
    midMultiplier: 1.35,
    premiumMultiplier: 1.85
  },

  // Dropdown options shown to the customer
  options: {
    widths:   [155,165,175,185,195,205,215,225,235,245,255],
    profiles: [40,45,50,55,60,65,70],
    rims:     [14,15,16,17,18,19,20]
  }
};
