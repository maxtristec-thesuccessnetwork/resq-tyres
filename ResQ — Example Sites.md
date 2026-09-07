---
type: client-note
client: ResQ Tyres & Recovery
updated: 2026-06-16
tags: [client, resq, references, design]
---

# ResQ — Example Sites

The two sites the client compared and discussed in Meeting 1. The "why" behind each is the real brief.

## 1. Black Circles — blackcircles.com

**What it is:** the UK's leading online tyre retailer — buy tyres online, fitted locally.

**What the client loves:** *"I love the look online."* Specifically the **registration / postcode lookup that returns the right tyre and a price**, then lets you **order online**. He referenced a local company (a "partner" nearby) doing the same: enter your reg → it brings up the cost of the tyre, *without even needing you to know your tyre size*.

**Takeaways for ResQ:**
- The hero action is a **reg/size/postcode lookup → price**. This is the headline feature he wants.
- Clean catalogue presentation of tyres with prices.
- "How it works" explained simply; trust signals (brands, low prices) prominent.

**Caveat:** Black Circles is a large e-commerce operation with a full tyre database. ResQ doesn't need that scale — it needs the *feel* of reg→price using **his own price catalogue**, not a national inventory.

## 2. Hometyre — hometyre.co.uk

**What it is:** mobile tyre fitting at your home/work — **the closest match to ResQ's actual model.**

**Why it's the better structural template:**
- **"3 simple steps":** choose tyres → choose date/time → they come to you. Exactly the journey ResQ wants for non-emergency bookings.
- **Check coverage by postcode** before booking — relevant for a Leeds/West Yorkshire service area.
- **Pay at the time of fitting** — low-friction booking.
- **"To-the-minute" arrival** via a live-linked van fleet — the *efficiency/dispatch* story that maps to the client's future "shared calendar + map routing" idea.
- **Reviews front and centre** — ResQ already has a 4.9 rating to lean on.

**Takeaway:** use **Hometyre for the structure/journey** (mobile fitting, book-and-we-come-to-you, coverage area, reviews) and **Black Circles for the reg→price lookup feel**.

## How this shapes the build

- Phone-first hero for the **emergency** path (unchanged priority).
- A secondary **"book a fitting"** path: reg/size lookup → price from ResQ's catalogue → choose time/location → booking notifies staff by email/text.
- Coverage-area cue (Leeds / West Yorkshire).
- Reviews + trust signals throughout.

> [!note] Platform implication
> Reg-plate lookup + a priced catalogue is a step up from the current site. It's buildable in Wix via **Velo + a vehicle/tyre data API**, or could justify a different platform — a decision to settle before mockups. See [[ResQ — Wix Capability & Costs]].

## Related

- [[ResQ — Meeting 1 Notes (2026-06-16)]]
- [[ResQ — Pitch & Proposal]]
- [[ResQ — Audit Findings]]
