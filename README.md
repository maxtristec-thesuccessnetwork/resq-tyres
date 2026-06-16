# ResQ Tyres & Recovery — Website (Plan 2)

Custom, code-level build. **Emergency Bold** design. Phone-first, with an online
tyre **estimate** tool and an **enquiry / send-for-approval** form.

## Structure

```
ResQ Website Build/
├── index.html        ← page structure & content
├── css/styles.css    ← all styling (Emergency Bold theme)
├── js/rates.js       ← THE RATE SHEET — edit prices here
└── js/app.js         ← estimate logic + form handling
```

## To view it
Double-click `index.html` (opens in your browser). Everything works offline in demo mode.

## Plan 2 features
- Phone-first hero + click-to-call, sticky call bar on mobile.
- **Estimate tool**: customer enters tyre size + reg + postcode → sees Budget / Mid / Premium prices.
- **Send for approval**: prefills the enquiry form; customer submits; ResQ replies by phone/email.
- **Enquiry form** with mandatory **REG, tyre size, postcode** (plus name & phone).

## Editing prices (the "spreadsheet")
Open `js/rates.js`:
- `exact` — set prices for specific tyre sizes (most accurate).
- `fallbackByRim` — used when a size isn't listed, so the tool always returns a price.
- Replace the SAMPLE numbers with ResQ's real prices and save.

## Form-to-email (config in `js/app.js`)
Enquiries currently go to **maxtristec@googlemail.com** (set in `CONFIG.businessEmail`).

To make submissions arrive automatically (no email app needed):
1. Go to **https://web3forms.com**, enter your email, and they email you an **Access Key** (free, no account/password).
2. Paste it into `CONFIG.web3formsKey` in `js/app.js` and save.

That's it — the form then POSTs to Web3Forms and emails you each enquiry. Until a key
is set, the form falls back to opening the customer's email app prefilled (still works).

Also before launch: remove the yellow **DEMO BUILD** banner at the top of `index.html`,
and swap the placeholder logo (the 🛞 in the header) for ResQ's real logo.

## Deploying (later)
Drag this folder onto **Netlify Drop**, or push to GitHub and import into **Vercel**.
Then point ResQ's domain at it (he can stop paying Wix once live).

---
Sample data only — for client review. Built June 2026.
