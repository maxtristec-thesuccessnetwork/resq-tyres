# Reg → Tyre Size Lookup — Setup

The estimate tool can find a vehicle's factory tyre size from its number
plate. It works in two modes:

- **Demo mode (default):** with no API key set, the lookup returns sample
  data and shows a small **DEMO** badge. Good for showing the flow.
- **Live mode:** once an API key is added, it returns the real factory
  tyre size for any UK plate and the DEMO badge disappears.

## How it works

```
Browser (js/tyre.js)
   │  GET /api/tyre-lookup?vrm=AB12CDE
   ▼
Vercel serverless function (api/tyre-lookup.js)   ← API key lives here, never in the browser
   │  calls UK Vehicle Data "TyreData" package
   ▼
UK Vehicle Data API → returns factory tyre size → auto-fills width / profile / rim
```

The API key is **never** exposed to visitors — it stays server-side in a
Vercel environment variable.

## Going live (about 5 minutes)

1. **Create a UK Vehicle Data account** (free, no time limit):
   https://ukvehicledata.co.uk/signup
   In the welcome email, set your password, then open
   `https://panel.ukvehicledata.co.uk/APIKeys` and copy your **API key**.
   - The free **sandbox** key only resolves plates containing the letter
     **"A"** — fine for testing. Top up credit to remove that limit
     (tyre lookups are roughly **5–10p each**, pay-as-you-go).

2. **Add the key to Vercel:**
   Vercel → your `resq-tyres` project → **Settings → Environment Variables**
   - `UKVD_API_KEY` = *your key*
   - `UKVD_PACKAGE` = `TyreData`  *(only needed if your account names the
     package differently — check it in your UKVD control panel)*

3. **Redeploy** (Vercel → Deployments → ⋯ → Redeploy, or just push a commit).
   The DEMO badge disappears and lookups are live.

## Notes

- The serverless function only runs on Vercel (or `vercel dev` locally).
  Opening `index.html` directly, or hosting on a static-only host, falls
  back to the built-in sample data so the page still works.
- Costs are per **successful** lookup. Pricing: https://ukvehicledata.co.uk/pricing
- Tyre size can vary by trim/wheel option; the API returns the
  manufacturer's standard fitment, which the customer can adjust before
  sending the enquiry.

Files involved: `api/tyre-lookup.js` (proxy), `js/tyre.js` (front-end),
the reg box in `index.html`, and styles under "Reg → tyre size lookup" in
`css/styles.css`.
