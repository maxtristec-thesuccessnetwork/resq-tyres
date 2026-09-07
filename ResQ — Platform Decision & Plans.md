---
type: client-note
client: ResQ Tyres & Recovery
updated: 2026-06-16
tags: [client, resq, platform, pricing, scope]
---

# ResQ — Platform Decision & Plans

Two build routes costed. Deliverables in `Assets/`:
- **Custom route (recommended):** `ResQ_Pricing_Model_Custom.xlsx` + `ResQ_Custom_Build_Plans.docx`
- **Wix route (comparison):** `ResQ_Pricing_Model.xlsx` + `ResQ_Solution_and_Pricing.docx`

## Wix vs Custom — the call

| | Wix Studio + Velo | Custom (Next.js + Vercel/Firebase + Stripe) |
|---|---|---|
| Booking/diary, deposits | Out of the box (Wix Bookings) | We build it (or embed Cal.com) |
| Client self-edits content | Easy, native | Needs an admin panel/CMS |
| Reg→price, supply-linked catalogue | Awkward (Velo limits) | Native territory — full control |
| Hosting/security/uptime | Wix handles | **We** handle (→ care plan) |
| Lock-in / monthly platform fee | Locked in, Wix fee | No lock-in, tiny hosting cost |
| Build cost (AI-assisted) | Lower | Low (AI), but we own upkeep |

> [!tip] Decision
> **Custom** is the better fit because reg→price + dynamic pricing + a tailored booking flow are the centre of gravity, ResQ doesn't need heavy self-editing (he hands us a rate sheet), and the ongoing maintenance becomes a billable care plan — recurring revenue a pure web designer never gets. With AI building, the old "custom is too expensive" objection falls away; the real shift is that **we become the host/maintainer** — price the ongoing accordingly.

## The three plans (custom, lean, cumulative)

> Re-scoped 16 Jun (v3) — prices set by Max at £400/£600/£800. Cost day-rate set to ~£0 (AI-assisted build = near-zero delivery cost), so these are almost pure margin. **No reg-lookup API, no online card processing; deposit requested by email.**

| Plan | Customer can… | Build (cumulative) | Ongoing /mo (Model B) |
|---|---|---|---|
| **1** | Ring, or contact by email with mandatory REG, tyre size & postcode. No pricing/booking. | £400 | ≈£106 |
| **2** | Plan 1 + estimated cost (rate-sheet) → send for approval → business replies by email/phone. | £600 | ≈£120 |
| **3** | Plan 2 + book an available slot → business confirms → requests deposit by email (manual). | £800 | ≈£120 |

Build cost is near zero (AI build), so ~100% margin. The build is a low-friction entry / foot in the door — **the real money is the monthly care plan and the future add-ons**, not the build fee.

### Future add-ons (upsell path, not in plans)
Online deposit/payment (Stripe) ~£800 · reg→recommended tyre (API) ~£1,200 + ~£25/mo · job allocation/dispatch ~£1,500 · automations ~£700.

## Ongoing (custom, lean)

Tools ≈ £23/mo (Plan 1) or £33/mo (Plan 2–3, adds small DB). Care fee modelled £75/mo (you maintain it).
- **Model A:** client pays tools direct + care fee.
- **Model B (recommended):** one care plan, tools rebilled +35% + care → your recurring revenue ≈ £87/mo (~£1,040/yr). Keep month-to-month, no tie-in (he hates lock-in).

## Pricing benchmarks (UK, June 2026)

Stripe 1.5% + 20p · Vercel Pro ~£16/mo · vehicle-data API pay-per-lookup (confirm) · build rates £300–400/day; bespoke booking £5k–£15k+.

## To confirm before quoting

- [ ] Vehicle-data API pricing
- [ ] Does his supplier offer a live price feed? (sheet-driven vs live catalogue)
- [ ] Real rate sheet / tyre prices
- [ ] Model A vs B
- [ ] Final per-component prices in the spreadsheet

## Related

- [[ResQ — Pricing & Build Scope]] (Wix-route version)
- [[ResQ — Meeting 1 Notes (2026-06-16)]]
- [[ResQ — Mockups]]
- [[ResQ Tyres — Overview]]
