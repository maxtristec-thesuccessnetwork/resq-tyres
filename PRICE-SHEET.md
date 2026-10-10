# The price sheet — how it works

Sheet: **ResQ Tyres — Website Prices**
`https://docs.google.com/spreadsheets/d/1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk`

The sheet is the only place prices live. Nothing is hard-coded in the site
and nothing needs redeploying — edit the sheet, refresh the page, done.

## How a size gets its price

1. **Exact row.** A size row with **both** `From £` and `To £` filled in is quoted exactly.
2. **Rim band.** Otherwise a car size is quoted from its rim's band: the `Backup 14 inch` …
   `Backup 20 inch` rows near the bottom of the sheet. A van/commercial size (`16C`) only
   uses a band if a `Backup 16C inch` row exists; it never borrows the car band.
3. **No price.** No exact row and no band: the customer sees "We'll price this one for you"
   and a call button.

| Row in the sheet | What the customer sees |
|---|---|
| `205 · 55 · 16 · 65 · 120` | **£65 – £120** per tyre |
| `205 · 55 · 16 · (blank) · (blank)` | the 16" band, if there is one, else "We'll price this one for you" |
| size not in the sheet at all | can't be selected |

Adding a size row makes that size selectable in the dropdowns, even before it has a price.

## The dropdowns

Width narrows the profiles, profile narrows the rims — all driven by the
size list in the sheet. A customer can no longer assemble a size that
doesn't exist (the old version happily quoted 255/70 R14).

Commercial/van sizes keep their **C**: enter the rim as `16c` and it appears
as `16C`, priced separately from a car's 16". They are different tyres.

## Notes

- Prices are **per tyre**. Mobile fitting is charged on top: from £50 per tyre (a `Mobile fitting`
  row in the sheet overrides the default).
- If `From` and `To` are entered the wrong way round, the site sorts them.
- `0` in a price column counts as **not priced**, not as free.
- `Locking Wheel Nut Removal` sets the add-on shown when a customer says they've no key.
- If the sheet is ever unreachable, the site falls back to the sizes and rim bands bundled in
  `js/rates.js`, so the guide still shows the headline ranges.
- Enquiry emails for an unpriced size are flagged `NOT PRICED IN SHEET — quote this one manually`
  so nothing slips through.

## The plain price table (home page)

Crawlers and AI tools don't run the price guide, so the home page also carries a plain HTML
"Prices at a glance" table. It is built from `js/rates.js` by `tools/build-price-table.py`, and
`llms.txt` carries the same bands. **Whenever the bands, fitting or locking-nut prices in the
sheet change:** update `js/rates.js` (and its `checked` month), run
`python3 tools/build-price-table.py`, and check `llms.txt`.
`python3 tools/build-price-table.py --sheet` compares `js/rates.js` with the live sheet and
exits 1 if they differ; run it monthly.
