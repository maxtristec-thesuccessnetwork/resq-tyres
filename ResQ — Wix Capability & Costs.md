---
type: client-note
client: ResQ Tyres & Recovery
updated: 2026-06-16
tags: [client, resq, wix, costs]
---

# ResQ — Wix Capability & Costs

> [!important] Open decision after Meeting 1
> The client now wants **registration-plate lookup → tyre size → price** (see [[ResQ — Example Sites]]). That's a bigger build than the original audit assumed and reopens the platform question below.

## The reg-lookup + pricing question

What it needs: (1) a **vehicle/tyre data source** that maps a reg or vehicle to the correct tyre size, and (2) **ResQ's own price catalogue** to return a price.

- **Wix + Velo** *can* do it: Velo calls an external vehicle-data/tyre API and reads a price collection. Workable, keeps everything in one place, but it's custom work and depends on a third-party data API (cost + reliability to check).
- **Alternative platform / custom build** could be cleaner if the lookup is the centre of gravity — worth weighing given he wants this to be the headline feature.
- **Decision needed before mockups.** Recommend pricing a simple version first (manual tyre-size entry → price from his catalogue) and adding true reg-lookup as a Phase 2 enhancement, to keep cost down.

## Can we build it in Wix? — Yes (with the above caveat)

Everything else the build needs is native to Wix, and **most of the process automation is built in**.

| Capability | How it works on Wix |
|---|---|
| Booking confirmations & reminders | Native to **Wix Bookings + Automations** (email; SMS too, on a booking-capable plan) |
| Review generation | Automated post-job follow-up asking for a Google review (Automations) |
| Repeat-customer follow-up | "Time for new tyres" on a timer — Automations, or **Velo** for custom timing |
| CRM / contacts | Built-in contacts/CRM — every enquiry/booking captured |
| Custom logic / external tools | **Velo**: back-end code, databases, external APIs, most npm packages. Third-party via Zapier/Make |

## Constraints to keep in mind

- **Closed, hosted platform** — can't self-host or cleanly export the site. Genuine lock-in (matters for *our* positioning, not a blocker for him).
- SMS + the booking engine sit behind **higher plan tiers** — his current plan partly decides the upsell scope.
- A few npm packages restricted (private / hardware / security risk) — irrelevant here.
- Truly bespoke heavy software would outgrow Wix — nothing ResQ needs comes close.

## His likely current costs (UK, June 2026 — confirm in the room)

| Item | Typical cost | Note |
|---|---|---|
| Wix plan | Light £9 / Core £16 / Business £25 / Elite £119 per month | Likely Core or Business; Business unlocks Bookings + SMS |
| Calendly | Free, or ~£10/user/mo | **Possibly redundant** |
| Domain | ~£10–20 / year | Confirm who owns/renews |
| Branded email | £0 now (Gmail); ~£5–6/user/mo for a proper `hello@` | Not yet set up — Tier 1 |

> [!tip] Saving to hand him
> He runs **both** Calendly and Wix Bookings. Consolidating into Wix-native booking could let him **cancel Calendly entirely** — a small monthly saving that also fixes the double-admin problem. Confirm his Wix tier: if he's already on Business, reminders/SMS are available now and part of the upsell is just configuration.

## Sources

- Wix UK pricing — websitebuilderexpert.com/website-builders/wix-pricing
- Wix Bookings automations / SMS — support.wix.com
- Velo capabilities — dev.wix.com/docs/velo
- Calendly pricing — wise.com/gb/blog/calendly-pricing

## Related

- [[ResQ — Audit Findings]]
- [[ResQ — Pitch & Proposal]]
