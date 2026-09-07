**Subject:** Tyre prices on the website — quick one

Hi mate,

I've been through the price sheet and made a change to how the site handles
it. Two things worth two minutes of your time.

**1. Five of the prices aren't yours.**

When I built the site I filled the sheet with dummy numbers so I could test
it. It looks like the size columns got updated but the price columns are
still my test figures — so the site is currently quoting:

| Size | On the site now |
|---|---|
| 185/65 R14 | £20 – £50 |
| 185/60 R14 | £55 – £115 |
| 185/70 R14 | £70 – £149 |
| 175/65 R14 | £85 – £179 |
| 155/65 R14 | £105 – £219 |

A 155/65 R14 is about the cheapest tyre on the road and it's showing as your
most expensive. I've cleared those five so nothing wrong is live — just fill
them in whenever you've got the real numbers.

**2. The site no longer guesses.**

It used to fall back to the "Backup 14 inch / 15 inch…" rows at the bottom of
the sheet whenever someone picked a size you hadn't priced. That meant it was
putting prices on tyres you'd never quoted — and since every backup row was
set to £45–£70, a small hatchback tyre and a 20" 4x4 tyre came out the same.

That's gone. Now it's one simple rule:

- **Both price boxes filled in** → the customer sees your price.
- **Either box empty** → the customer sees "We'll price this one for you" and
  a call button.

So it can only ever show a number you've actually put there. Nothing to
learn, nothing to maintain — just fill in the two columns for whichever
sizes you want priced, and leave the rest blank. The more you fill in, the
more people get an answer without ringing; the ones you leave blank still
come through to you as a call.

You don't need me to publish anything. Edit the sheet, refresh the site,
it's live.

**One more thing** — all the van and commercial sizes you added (the ones
ending in "c", like 195/65 16c) now work properly and are priced separately
from the car sizes. Same with the 21" and 22". Those were all invisible on
the site before.

Cheers,
Max
