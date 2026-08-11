# The price sheet — how it works

Sheet: **ResQ Tyres — Website Prices**
`https://docs.google.com/spreadsheets/d/1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk`

The sheet is the only place prices live. Nothing is hard-coded in the site
and nothing needs redeploying — edit the sheet, refresh the page, done.

## The one rule

A size shows a **price** only if that row has **both** `From £` and `To £`
filled in. Every other size still appears in the dropdowns, but the customer
is told to call instead.

| Row in the sheet | What the customer sees |
|---|---|
| `205 · 55 · 16 · 65 · 120` | **£65 – £120** per tyre, fitted |
| `205 · 55 · 16 · (blank) · (blank)` | "We'll price this one for you" + call button |
| size not in the sheet at all | can't be selected |

So there are two separate switches:

1. **Adding a size row** makes that size selectable in the dropdowns.
2. **Filling in its two price columns** turns the price on.

Adding a row without prices is still worth doing — it means a customer with
that tyre can find their size and gets pushed to the phone rather than
bouncing off the site.

## What was removed (July 2026)

The sheet used to have a block of `Backup 14 inch … Backup 20 inch` rows.
Those were a catch-all: any size without its own price was quoted using the
band for its rim diameter. That meant the site was putting a price on tyres
nobody had ever priced — and with every band set to £45–£70, a 14" Corsa
tyre and a 20" Range Rover tyre came out identical.

**That is gone.** The site no longer estimates, bands or interpolates a
price under any circumstances. Those rows are ignored and can be deleted.

## The dropdowns

Width narrows the profiles, profile narrows the rims — all driven by the
size list in the sheet. A customer can no longer assemble a size that
doesn't exist (the old version happily quoted 255/70 R14).

Commercial/van sizes keep their **C**: enter the rim as `16c` and it appears
as `16C`, priced separately from a car's 16". They are different tyres.

## Notes

- Prices are per tyre, mobile fitting included.
- If `From` and `To` are entered the wrong way round, the site sorts them.
- `0` in a price column counts as **not priced**, not as free.
- `Locking Wheel Nut Removal` sets the add-on shown when a customer says
  they've no key.
- If the sheet is ever unreachable, the site falls back to the size list
  bundled in `js/rates.js` and quotes nothing — it never invents a number.
- Enquiry emails for an unpriced size are flagged
  `NOT PRICED IN SHEET — quote this one manually` so nothing slips through.
- Open the browser console on the live site to confirm what loaded:
  `ResQ prices: 132 sizes listed, 7 with a price.`
