/* ===========================================================
   ResQ Tyres — RATE SHEET  (this is the "spreadsheet" you update)
   -----------------------------------------------------------
   The website shows customers a PRICE RANGE per tyre (fitted, at
   their location) — a "from £X to £Y" figure — not fixed tiers.
   ResQ confirms the exact price by phone before any work.

   >>> ALL NUMBERS BELOW ARE PLACEHOLDERS <<<
   Replace them with ResQ's real ranges. For each size, "low" is the
   cheapest budget tyre and "high" is a premium tyre, mobile fitting
   included. To change prices site-wide, edit and save — nothing else.

   How a price is worked out:
   1) EXACT — specific sizes with a set low–high range (most accurate).
   2) FALLBACK — if a size isn't listed, a range is estimated from the
      rim diameter so the tool always returns something.
   =========================================================== */

const RESQ_RATES = {

  // 1) EXACT ranges for common sizes. Key = "width/profileRrim".
  //    { low: cheapest fitted price, high: premium fitted price }
  exact: {
    "195/65R15": { low: 49,  high: 95  },
    "205/55R16": { low: 55,  high: 115 },
    "225/45R17": { low: 70,  high: 149 },
    "225/40R18": { low: 85,  high: 179 },
    "245/40R19": { low: 105, high: 219 }
  },

  // 2) Fallback range by rim size (used when a size isn't in 'exact').
  fallbackByRim: {
    low:  { 14: 45, 15: 49, 16: 55, 17: 70,  18: 85,  19: 105, 20: 130 },
    high: { 14: 79, 15: 89, 16: 115, 17: 149, 18: 179, 19: 219, 20: 265 }
  },

  // Optional add-on: locking wheel-nut removal, if the customer has
  // lost/never had the key. ResQ carries the specialist tools (a USP).
  // PLACEHOLDER — set to ResQ's real add-on price (or 0 to include free).
  lockingNutRemoval: { low: 15, high: 25 },

  // Dropdown options shown to the customer
  options: {
    widths:   [155,165,175,185,195,205,215,225,235,245,255],
    profiles: [40,45,50,55,60,65,70],
    rims:     [14,15,16,17,18,19,20]
  }
};

/* ===========================================================
   COVERAGE — where ResQ will travel to.
   Used by the postcode checker + the coverage map.
   >>> PLACEHOLDER — confirm the exact accepted postcode districts
   with ResQ. Currently based on the towns already listed on the site
   (Leeds = LS, Bradford = BD, Wakefield/Dewsbury/Castleford/Pontefract
   = WF). Add HD/HX etc. if he covers them.
   =========================================================== */
const RESQ_COVERAGE = {
  covered: ["LS", "BD", "WF"],          // accepted outward postcode prefixes
  towns: [
    "Leeds", "Bradford", "Wakefield", "Dewsbury", "Pudsey",
    "Morley", "Castleford", "Garforth", "Pontefract"
  ]
};
