#!/usr/bin/env python3
"""Build the town landing pages from index.html's own head + one data block per town.

    python3 tools/build-town-pages.py            # writes /mobile-tyre-fitting-<slug>.html for every town below

Design rules (so the pages stay honest and stay on-brand):
  * The <head> critical CSS block is lifted VERBATIM from index.html at build time, so a
    change to the home page's fonts or above-fold CSS flows through on the next build.
  * No arrival-time claim. The home page's "15–30 minutes" is the client's claim (card W7);
    these pages say "24/7" and "we come to you" and nothing about minutes.
  * No prices on the page. Prices live in the Google Sheet and are surfaced by the home
    page's price guide; these pages link to it. Puncture repair £70–£120 and "30% off a set"
    are the two figures already published on the home page and are repeated as-is.
  * Every district listed is in js/rates.js RESQ_COVERAGE.districts — the checker on the
    page uses the same list, so the page can never claim more than the checker allows.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SITE = "https://www.resqtyres.co.uk"
PHONE_DISPLAY, PHONE_TEL, PHONE_E164 = "07438 562633", "07438562633", "+447438562633"
WA = "https://wa.me/447438562633"
COVERED = set(re.findall(r'"([A-Z]{2}\d{1,2})"', INDEX.split("RESQ_COVERAGE")[0]) or [])  # placeholder
COVERED = set(re.findall(r'"((?:LS|HG|WF)\d{1,2})"', (ROOT / "js" / "rates.js").read_text()))

# ------------------------------------------------------------------ head pieces from index.html
def slice_between(s: str, start: str, end: str) -> str:
    i = s.index(start); j = s.index(end, i) + len(end)
    return s[i:j]

CRITICAL_STYLE = slice_between(INDEX, "  <style>/* critical:", "  </style>\n")
ICON_DEFS = slice_between(INDEX, '  <svg width="0" height="0"', "</defs></svg>\n")
TOPBAR = slice_between(INDEX, "  <!-- ===== Top utility bar =====", "  <!-- ===== Header =====").rstrip() + "\n"
FOOTER = slice_between(INDEX, "  <!-- ===== Footer =====", "  </footer>\n")
STICKY = slice_between(INDEX, "  <!-- Back to top -->", '  </div>\n\n  <script src="js/rates.js"></script>').replace('  <script src="js/rates.js"></script>', "")
REVIEWS = slice_between(INDEX, '        <div class="reviews stagger">', "        </div>\n        <div class=\"reviews-cta reveal\">")
# footer links are anchors on the home page; make them absolute so they work from a town page
FOOTER = re.sub(r'href="#(?!top)', 'href="/#', FOOTER)
FOOTER = FOOTER.replace('href="#top"', 'href="/"')

# ------------------------------------------------------------------ towns
TOWNS = [
    dict(
        slug="wakefield", name="Wakefield", short="Wakefield",
        title="Mobile Tyre Fitting Wakefield — 24/7, We Come To You | ResQ Tyres",
        description="24/7 mobile tyre fitting and puncture repair in Wakefield, WF1–WF13. We come to your home, work or the roadside with new tyres on the van. Pay on completion. Call 07438 562633.",
        h1="Flat tyre in Wakefield? We come to you.",
        rotator=["In Wakefield.", "In Ossett.", "In Castleford.", "In Pontefract.", "Day or night."],
        sub="24 hour mobile tyre fitting across Wakefield and the WF postcodes — emergency call-outs <b>and</b> planned home fitting. The same tyres you'd get in a shop, fitted on your driveway in Sandal, Ossett, Horbury or Outwood. One call and we're on the way from Leeds.",
        hero_img=("assets/hero-resq-600-v2.webp", "assets/hero-resq-900-v2.webp", "600w", "900w", 1000, 1050,
                  "ResQ Tyres mobile tyre fitting van at a roadside job — a new tyre being fitted on site"),
        stat_area=("WF1–WF13", "Every Wakefield district"),
        cover_heading="Every WF postcode from Wakefield to Dewsbury",
        cover_intro="Wakefield is one of our busiest patches. We cover every district from WF1 to WF13 — the city, the Five Towns and out to Dewsbury — and we're on the road from Leeds, not from a depot you have to drive to.",
        districts=[
            ("WF1", "Wakefield city centre, Eastmoor, Outwood, Newton Hill"),
            ("WF2", "Sandal, Newmillerdam, Kettlethorpe, Lupset, Alverthorpe, Wrenthorpe, Walton"),
            ("WF3", "Stanley, Lofthouse, Tingley, East Ardsley, Robin Hood"),
            ("WF4", "Horbury, Crigglestone, Durkar, Netherton, Crofton, Ryhill"),
            ("WF5", "Ossett, Gawthorpe"),
            ("WF6", "Normanton, Altofts"),
            ("WF7", "Featherstone, Ackworth, Purston"),
            ("WF8", "Pontefract, Darrington, East Hardwick"),
            ("WF9", "Hemsworth, South Kirkby, South Elmsall, Upton, Fitzwilliam"),
            ("WF10", "Castleford, Airedale, Glasshoughton, Allerton Bywater"),
            ("WF11", "Knottingley, Ferrybridge, Brotherton"),
            ("WF12", "Dewsbury, Thornhill, Savile Town, Earlsheaton"),
            ("WF13", "Dewsbury Moor, Ravensthorpe, Staincliffe"),
        ],
        edge="Just outside — Barnsley, Huddersfield or WF14 and above? Call us anyway. We can often still reach you.",
        landmarks="the M1 and M62 around junctions 39–41, the A61 into Leeds, Trinity Walk and the Ridings car parks, Pinderfields, and the station car parks at Westgate and Kirkgate",
        faq=[
            ("Do you cover all of Wakefield?",
             "Yes — every district from <b>WF1</b> to <b>WF13</b>. That's Wakefield itself, Ossett, Horbury, Normanton, Featherstone, Pontefract, Hemsworth, Castleford, Knottingley and Dewsbury. Type your postcode into the checker above if you want to be sure."),
            ("Can you come out to me now in Wakefield?",
             f"Yes. We're mobile 24 hours a day, 365 days a year, and Wakefield is one of the areas we're in most. Call <a href=\"tel:{PHONE_TEL}\">{PHONE_DISPLAY.replace(' ', '&nbsp;')}</a> or message us on WhatsApp — for an emergency, ringing is faster than a form."),
            ("Do you repair punctures in Wakefield, or only replace tyres?",
             "Both. If the tyre can be safely repaired, we repair it at the roadside or on your drive. If it can't, we carry new tyres on the van and fit one on the spot. Puncture repair is &pound;70 to &pound;120 depending on distance and tyre size."),
            ("Where in Wakefield can you fit a tyre?",
             f"Wherever the car is — your driveway in Sandal or Outwood, a work car park, or the hard shoulder. We regularly attend {'the M1 and M62 around junctions 39–41, the A61 into Leeds'}, and the retail and station car parks in the city centre."),
            ("How much is mobile tyre fitting in Wakefield?",
             "It depends on your tyre size, and mobile fitting is included in the price rather than charged as an extra — there's no call-out fee added on top for Wakefield. Use the <a href=\"/#estimate\">price guide</a> for a fitted range, and we confirm the exact price by phone before any work starts. Changing all four? Ask about 30% off the set."),
            ("Do I pay a deposit?",
             "No. Nothing to pay online and no deposit. You pay on completion, by card or cash, once the job's done."),
        ],
        marquee=["Wakefield", "Ossett", "Horbury", "Normanton", "Castleford", "Pontefract", "Featherstone", "Hemsworth", "Knottingley", "Dewsbury"],
        served=[("City", "Wakefield"), ("City", "Ossett"), ("City", "Castleford"), ("City", "Pontefract"), ("City", "Normanton"), ("City", "Dewsbury")],
    ),
    dict(
        slug="harrogate", name="Harrogate", short="Harrogate &amp; Tadcaster",
        title="Mobile Tyre Fitting Harrogate & Tadcaster — 24/7, We Come To You | ResQ Tyres",
        description="24/7 mobile tyre fitting and puncture repair in Harrogate (HG1–HG3) and Tadcaster (LS24). We come to your home, work or the roadside with new tyres on the van. Pay on completion. Call 07438 562633.",
        h1="Flat tyre in Harrogate or Tadcaster? We come to you.",
        rotator=["In Harrogate.", "In Pannal.", "In Tadcaster.", "On the A61.", "Day or night."],
        sub="24 hour mobile tyre fitting across Harrogate, Pannal, Killinghall and out to Tadcaster — emergency call-outs <b>and</b> planned home fitting. The same tyres you'd get in a shop, fitted on your driveway. One call and we're on the way up from Leeds.",
        hero_img=("assets/fitting-420.webp", "assets/fitting-760.webp", "420w", "760w", 760, 1140,
                  "ResQ Tyres fitter changing a tyre at a customer's home — mobile tyre fitting on the driveway"),
        stat_area=("HG1–HG3 · LS24", "Harrogate &amp; Tadcaster"),
        cover_heading="Harrogate, the villages around it, and Tadcaster",
        cover_intro="We come up the A61 and the A658 from Leeds to cover all three Harrogate districts and the Tadcaster side of LS24. Same van, same tyres, same pay-on-completion — no need to get the car to a garage in town.",
        districts=[
            ("HG1", "Harrogate town centre, Bilton, Starbeck, New Park, High Harrogate"),
            ("HG2", "Oatlands, Pannal, Harlow Hill, Hornbeam Park, Burn Bridge"),
            ("HG3", "Killinghall, Ripley, Hampsthwaite, Birstwith, Spofforth, Follifoot, Kirkby Overblow, Beckwithshaw"),
            ("LS24", "Tadcaster, Stutton, Towton, Saxton, Church Fenton, Ulleskelf"),
            ("LS22 · LS23", "Wetherby, Boston Spa, Thorp Arch — on the way between the two"),
        ],
        edge="Knaresborough (HG5) and Ripon (HG4) are just outside our confirmed patch — call us anyway, we may still be able to reach you.",
        landmarks="the A61 Leeds Road and Harrogate Road, the A59 through Knaresborough, the A658 past the airport, the Stray, Harrogate station and the Victoria car park, and the A64 and A659 around Tadcaster",
        faq=[
            ("Which parts of Harrogate do you cover?",
             "All three Harrogate districts — <b>HG1</b>, <b>HG2</b> and <b>HG3</b> — so the town centre, Bilton, Starbeck, Oatlands, Pannal, Killinghall, Ripley and the villages out towards Pateley Bridge. Plus <b>LS24</b> for Tadcaster. Knaresborough and Ripon are just outside, but call and ask."),
            ("Can you come out to Harrogate now?",
             f"Yes. We're mobile 24 hours a day, 365 days a year. We come up from Leeds, so tell us where you are when you call <a href=\"tel:{PHONE_TEL}\">{PHONE_DISPLAY.replace(' ', '&nbsp;')}</a> or WhatsApp us, and we'll give you a straight answer on when we can be with you."),
            ("Do you repair punctures in Harrogate and Tadcaster?",
             "Yes — if the tyre can be safely repaired, we repair it where the car is. If it can't, we carry new tyres on the van and fit one on the spot. Puncture repair is &pound;70 to &pound;120 depending on distance and tyre size."),
            ("Where can you fit the tyre?",
             "Wherever the vehicle is — a driveway in Pannal, a work car park at Hornbeam Park, the Stray, or the hard shoulder of the A61. The van carries brand-new tyres, on-site balancing and valve replacement, so most jobs are finished in one visit."),
            ("How much is mobile tyre fitting in Harrogate?",
             "It depends on your tyre size, and mobile fitting is included in the price rather than charged as an extra — there's no separate call-out fee for Harrogate or Tadcaster. Use the <a href=\"/#estimate\">price guide</a> for a fitted range; we confirm the exact price by phone before any work starts. Changing all four? Ask about 30% off the set."),
            ("Do I pay a deposit?",
             "No. Nothing to pay online and no deposit. You pay on completion, by card or cash, once the job's done."),
        ],
        marquee=["Harrogate", "Bilton", "Starbeck", "Pannal", "Killinghall", "Ripley", "Spofforth", "Tadcaster", "Boston Spa", "Wetherby"],
        served=[("City", "Harrogate"), ("City", "Tadcaster"), ("City", "Pannal"), ("City", "Killinghall"), ("City", "Wetherby"), ("City", "Boston Spa")],
    ),
]

# ------------------------------------------------------------------ builders
def check_districts(town):
    for code, _ in town["districts"]:
        for c in re.split(r"\s*·\s*", code):
            assert c in COVERED, f"{town['slug']}: {c} is not in RESQ_COVERAGE.districts — do not publish a district the checker refuses"

def schema(town):
    url = f"{SITE}/mobile-tyre-fitting-{town['slug']}"
    name_plain = html.unescape(town["short"])
    service = {
        "@context": "https://schema.org", "@type": "Service",
        "@id": url + "#service",
        "name": f"Mobile tyre fitting in {name_plain}",
        "serviceType": "Mobile tyre fitting and puncture repair",
        "url": url,
        "provider": {"@type": "AutoRepair", "@id": f"{SITE}/#business", "name": "ResQ Tyres & Recovery",
                     "telephone": PHONE_E164, "url": SITE + "/"},
        "areaServed": [{"@type": t, "name": n} for t, n in town["served"]],
        "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": PHONE_E164, "contactType": "customer service", "availableLanguage": "en"}},
        "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59"},
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": html.unescape(re.sub("<[^>]+>", "", q)),
                           "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<[^>]+>", "", a))}} for q, a in town["faq"]]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ResQ Tyres & Recovery", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Areas we cover", "item": SITE + "/#areas"},
        {"@type": "ListItem", "position": 3, "name": f"Mobile tyre fitting in {name_plain}", "item": url}]}
    return "\n".join(f'  <script type="application/ld+json">\n{json.dumps(d, ensure_ascii=False, indent=2)}\n  </script>' for d in (service, faq, crumbs))

def build(town) -> str:
    check_districts(town)
    slug, name = town["slug"], town["name"]
    url = f"{SITE}/mobile-tyre-fitting-{slug}"
    src1, src2, w1, w2, iw, ih, alt = town["hero_img"]
    rot_words = json.dumps(town["rotator"])
    districts = "\n".join(
        f'            <li class="district"><b>{code}</b><span>{places}</span></li>' for code, places in town["districts"])
    faqs = "\n".join(
        f'          <div class="faq-item">\n            <h3>{q}</h3>\n            <p>{a}</p>\n          </div>' for q, a in town["faq"])
    marquee_items = "".join(
        f'<span class="item">{m}</span><span class="dot"></span>' for m in town["marquee"]) * 2
    served_names = ", ".join(n for _, n in town["served"])

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <script>document.documentElement.className+=" js";</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{town['title']}</title>
  <meta name="description" content="{html.escape(town['description'], quote=True)}">
  <meta name="theme-color" content="#e4002b">
  <link rel="canonical" href="{url}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="Mobile tyre fitting in {town['short']} — 24/7, we come to you">
  <meta property="og:description" content="{html.escape(town['description'], quote=True)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/assets/van.jpg">
  <meta property="og:locale" content="en_GB">
  <meta property="og:site_name" content="ResQ Tyres &amp; Recovery">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="assets/logo.png">
  <link rel="preload" href="fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>
{CRITICAL_STYLE}  <link rel="stylesheet" href="css/styles.css" media="print" onload="this.media='all';this.onload=null">
  <noscript><link rel="stylesheet" href="css/styles.css"></noscript>
  <link rel="preload" as="image" href="{src1}" imagesrcset="{src1} {w1}, {src2} {w2}" imagesizes="(max-width:900px) 92vw, 560px" fetchpriority="high">
  <style>
    /* town-page additions — everything else comes from css/styles.css */
    .districts{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}}
    .district{{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:baseline;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;box-shadow:var(--shadow-sm)}}
    .district b{{font-size:15px;color:var(--red);white-space:nowrap;font-variant-numeric:tabular-nums}}
    .district span{{font-size:14px;color:var(--muted);line-height:1.45}}
    .cover-grid{{display:grid;gap:26px;align-items:start}}
    @media(min-width:900px){{.cover-grid{{grid-template-columns:1.25fr .75fr}}}}
    .cover-edge{{margin-top:14px;font-size:14px;color:var(--muted)}}
    .crumbs{{font-size:13px;color:var(--muted);margin-bottom:14px}}
    .crumbs a{{color:inherit;text-decoration:none}} .crumbs a:hover{{text-decoration:underline}}
    .crumbs span{{margin:0 6px;opacity:.6}}
    .landmarks{{margin-top:14px;padding:14px 16px;border-left:3px solid var(--red);background:#fff;border-radius:0 var(--radius) var(--radius) 0;font-size:15px}}
  </style>

{schema(town)}

  <meta name="google-site-verification" content="AzR8QPG5N2F7wxsMGfz7zcRObHtjaszAAsQgL5Y2scY">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GVBR7Z973Z"></script>
  <script src="/js/analytics.js" defer></script>
</head>
<body id="top">

{ICON_DEFS}
  <div class="progress" id="progress" aria-hidden="true"></div>

{TOPBAR}
  <!-- ===== Header ===== -->
  <header class="site-header">
    <div class="wrap bar">
      <a href="/" class="logo">
        <img src="assets/logo-128.webp" alt="ResQ Tyres &amp; Recovery logo" width="54" height="54" decoding="async">
        <span class="logo-text">ResQ Tyres<small>&amp; RECOVERY · EST 2023</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#help">Emergency or planned</a>
        <a href="/#estimate">Price guide</a>
        <a href="#cover">{name} coverage</a>
        <a href="#faq">Questions</a>
        <a href="/#enquiry">Home fitting</a>
      </nav>
      <div class="header-right">
        <a class="btn-call" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> {PHONE_DISPLAY}</a>
      </div>
    </div>
  </header>

  <main>
    <!-- ===== Hero ===== -->
    <section class="hero">
      <div class="wrap">
        <div class="hero-grid">
          <div class="hero-copy">
            <p class="crumbs"><a href="/">ResQ Tyres</a><span>›</span><a href="/#areas">Areas we cover</a><span>›</span>{town['short']}</p>
            <span class="live-badge"><span class="dot" aria-hidden="true"></span> Open now · 24/7 across {town['short']}</span>
            <h1>{town['h1']}</h1>
            <div class="rotator" id="rotator" aria-hidden="true" data-words='{rot_words}'>{town['rotator'][0]}</div>
            <p class="hero-sub">{town['sub']}</p>
            <div class="cta-row">
              <a class="cta-primary pulse" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> Emergency — call now</a>
              <a class="cta-whatsapp" href="{WA}" target="_blank" rel="noopener"><svg class="icon" aria-hidden="true"><use href="#i-whatsapp"/></svg> WhatsApp</a>
              <a class="cta-secondary" href="/#enquiry">Plan a home fitting <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
            </div>
            <div class="scroll-cue" aria-hidden="true"><span class="mouse"></span>Scroll</div>
          </div>

          <div class="hero-photo">
            <div class="frame">
              <img src="{src1}" srcset="{src1} {w1}, {src2} {w2}" sizes="(max-width:900px) 92vw, 560px"
                 width="{iw}" height="{ih}" alt="{alt}" loading="eager" fetchpriority="high" decoding="async" id="heroImg" data-hero>
              <div class="tag"><svg class="icon" aria-hidden="true"><use href="#i-shield"/></svg><div><b>Pay on completion</b><span>No upfront payment</span></div></div>
            </div>
            <div class="floatcard"><b><span data-count="5.0" data-dec="1">5.0</span><span class="star" aria-hidden="true">★</span></b><span>215+ Google reviews</span></div>
          </div>
        </div>
      </div>

      <div class="stats">
        <div class="wrap stagger">
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-clock"/></svg><div><b>24/7</b><span>365 days a year</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-star"/></svg><div><b><span data-count="5.0" data-dec="1">5.0</span><small class="of"> / 5</small></b><span>Google rating</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-pin"/></svg><div><b>{town['stat_area'][0]}</b><span>{town['stat_area'][1]}</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-card"/></svg><div><b>Pay on completion</b><span>Card or cash</span></div></div>
        </div>
      </div>
    </section>

    <div class="marquee" aria-hidden="true">
      <div class="track">
        <span class="item"><svg class="icon"><use href="#i-clock"/></svg> 24/7 Emergency call-outs</span><span class="dot"></span>
        <span class="item"><svg class="icon"><use href="#i-wheel"/></svg> Mobile tyre fitting in {town['short']}</span><span class="dot"></span>
        <span class="item">Flat · Blowout · Puncture</span><span class="dot"></span>
        <span class="item"><svg class="icon"><use href="#i-pin"/></svg> We come to you</span><span class="dot"></span>
        <span class="item"><svg class="icon"><use href="#i-clock"/></svg> 24/7 Emergency call-outs</span><span class="dot"></span>
        <span class="item"><svg class="icon"><use href="#i-wheel"/></svg> Mobile tyre fitting in {town['short']}</span><span class="dot"></span>
        <span class="item">Flat · Blowout · Puncture</span><span class="dot"></span>
        <span class="item"><svg class="icon"><use href="#i-pin"/></svg> We come to you</span><span class="dot"></span>
      </div>
    </div>

    <!-- ===== Two ways we help ===== -->
    <section class="section" id="help">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Two ways we help in {town['short']}</span>
          <h2>Emergency now, or plan a home fitting</h2>
          <p>Stuck at the roadside? Just call — it's faster. Planning ahead? Send your details and we'll come to your home or work in {name}.</p>
        </div>
        <div class="paths stagger">
          <article class="path path-emergency">
            <div class="path-top"><span class="path-badge"><span class="dotpulse" aria-hidden="true"></span> 24/7 · Any hour</span><svg class="path-ico" aria-hidden="true"><use href="#i-phone"/></svg></div>
            <h3>Emergency call-out</h3>
            <p>Flat, blowout or breakdown in {name} and need someone now? Don't fill in a form — call or WhatsApp, tell us where you are, and we're on our way.</p>
            <ul class="path-list">
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Fastest response — straight to the phone</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Roadside, home or work, day or night</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Pay on completion — no deposit</li>
            </ul>
            <div class="path-cta">
              <a class="cta-primary pulse" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> Call {PHONE_DISPLAY}</a>
              <a class="cta-whatsapp" href="{WA}" target="_blank" rel="noopener"><svg class="icon" aria-hidden="true"><use href="#i-whatsapp"/></svg> WhatsApp</a>
            </div>
          </article>
          <article class="path path-planned">
            <div class="path-top"><span class="path-badge alt"><svg class="icon" aria-hidden="true"><use href="#i-home"/></svg> Booked in</span><svg class="path-ico" aria-hidden="true"><use href="#i-home"/></svg></div>
            <h3>Planned home tyre fitting</h3>
            <p>Not urgent? We'll fit your tyres at home or work anywhere in {town['short']} at a time that suits you — <b>the same price you'd pay in the shop</b>, without the trip. Send your details and we'll confirm by phone.</p>
            <ul class="path-list">
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Same tyres, same price as in-store</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> We come to your driveway — no waiting room</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> No deposit — pay when it's done</li>
            </ul>
            <div class="path-cta">
              <a class="cta-secondary solid" href="/#enquiry">Plan a home fitting <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
              <a class="cta-secondary" href="/#estimate">Check price range</a>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ===== Coverage ===== -->
    <section class="section soft" id="cover">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Where we cover</span>
          <h2>{town['cover_heading']}</h2>
          <p>{town['cover_intro']}</p>
        </div>
        <div class="cover-grid reveal">
          <div>
            <ul class="districts stagger">
{districts}
            </ul>
            <p class="cover-edge">{town['edge']}</p>
          </div>
          <div class="area-side">
            <div class="pc-checker">
              <label for="pc-check">Check your postcode</label>
              <div class="pc-row">
                <input id="pc-check" type="text" placeholder="e.g. {town['districts'][0][0].split(' ')[0]} 1AA" maxlength="8" autocomplete="postal-code" aria-label="Your postcode">
                <button type="button" id="pc-btn" class="btn-find"><svg class="icon" aria-hidden="true"><use href="#i-pin"/></svg> Check</button>
              </div>
              <p class="pc-result" id="pc-result" hidden></p>
              <p class="micro">Same checker as our <a href="/#areas">main coverage map</a> — every Leeds <b>LS</b> district, <b>HG1&ndash;HG3</b> and <b>WF1&ndash;WF13</b>.</p>
            </div>
            <div class="landmarks"><b>Where we're often called to:</b> {town['landmarks']}.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Services ===== -->
    <section class="section" id="services">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">What we do</span>
          <h2>Mobile tyre fitting across {town['short']}</h2>
          <p>Brand-new tyres fitted on the spot, wherever you are in {name}. We bring the garage to you.</p>
        </div>
        <div class="services stagger">
          <article class="svc">
            <div class="ph"><img src="assets/roadside-fit-420-v2.webp" srcset="assets/roadside-fit-420-v2.webp 420w, assets/roadside-fit-760-v2.webp 760w" sizes="(max-width:760px) 92vw, 360px" width="760" height="760" alt="Car raised on a jack with the wheel removed during ResQ Tyres mobile tyre fitting" loading="lazy" decoding="async"></div>
            <div class="body">
              <span class="tagline"><svg class="icon" aria-hidden="true"><use href="#i-wheel"/></svg> Flat · Blowout · Puncture</span>
              <h3>Mobile tyre fitting &amp; puncture repair in {name}</h3>
              <p>Tyre replacement and puncture repair at your home, work or the roadside anywhere in {town['short']}. If the tyre can be safely repaired, we repair it; if it can't, we carry new tyres on the van and fit one on the spot. No garage visit needed.</p>
            </div>
          </article>
          <article class="svc">
            <div class="ph"><img src="assets/wheelchange-420-v2.webp" srcset="assets/wheelchange-420-v2.webp 420w, assets/wheelchange-760-v2.webp 760w" sizes="(max-width:760px) 92vw, 360px" width="760" height="760" alt="ResQ Tyres attending a roadside emergency tyre change — 24 hour call-out" loading="lazy" decoding="async"></div>
            <div class="body">
              <span class="tagline"><svg class="icon" aria-hidden="true"><use href="#i-home"/></svg> Home · Work · Roadside</span>
              <h3>24 hour emergency call-out</h3>
              <p>Stranded in {name} day or night? We're available 24/7, 365 days a year. Tell us where you are and we'll give you a straight answer on when we can be with you.</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ===== How it works ===== -->
    <section class="section soft" id="how">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Simple &amp; fast</span>
          <h2>How it works</h2>
          <p>Emergency? Just call. Otherwise, three simple steps.</p>
        </div>
        <div class="steps stagger">
          <div class="step"><span class="n">1</span><b>Get in touch</b><p>Emergency? Just call or WhatsApp. Planning ahead? Send the home-fitting form with your tyre size, your {name} postcode and when suits you.</p></div>
          <div class="step"><span class="n">2</span><b>We confirm price &amp; time</b><p>A quick call to confirm the exact price and a slot that works. No deposit, no online payment.</p></div>
          <div class="step"><span class="n">3</span><b>We come &amp; fit it</b><p>At your home, work or the roadside. Pay on completion by card or cash — only once the job's done.</p></div>
        </div>
      </div>
    </section>

    <!-- ===== Van band ===== -->
    <section class="van-band">
      <div class="wrap">
        <div class="van-grid">
          <div class="copy reveal from-left">
            <span class="eyebrow" style="color:#ff7a90">Fully equipped</span>
            <h2>Our van is a <span>garage on wheels</span></h2>
            <p>Everything we need to get you safely back on the road in {name} travels with us — so most jobs are sorted in a single visit, right where you are.</p>
            <ul class="van-feats">
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Brand-new tyres — budget, mid-range &amp; premium</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> On-site balancing &amp; valve replacement</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> Locking wheel-nut removal</li>
              <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg> 24/7, 365 days a year</li>
            </ul>
            <a class="cta-primary" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> Call {PHONE_DISPLAY}</a>
          </div>
          <div class="van-img reveal from-right"><img src="assets/van-760-v2.webp" srcset="assets/van-760-v2.webp 760w, assets/van-1100-v2.webp 1100w" sizes="(max-width:900px) 100vw, 560px" width="1100" height="1375" alt="ResQ Tyres &amp; Recovery Mercedes Sprinter van carrying new tyres and on-site balancing equipment" loading="lazy" decoding="async" data-parallax="0.08"></div>
        </div>
      </div>
    </section>

    <!-- ===== Reviews ===== -->
    <section class="section soft" id="reviews">
      <div class="wrap">
        <div class="rev-head reveal">
          <h2 class="sr-only">Customer reviews — rated 5.0 on Google from 215+ verified reviews</h2>
          <span class="eyebrow">Trusted across West Yorkshire</span>
          <span class="stars" style="font-size:22px">★★★★★</span>
          <span class="big"><span data-count="5.0" data-dec="1">5.0</span> on Google</span>
          <span class="micro">From <span data-count="215" data-suffix="+">215+</span> verified Google reviews</span>
        </div>
{REVIEWS}        </div>
        <div class="reviews-cta reveal">
          <a class="rev-google" href="https://maps.app.goo.gl/LyEpPCfZw5TquB427" target="_blank" rel="noopener"><span class="gicon">G</span> Read all 215 reviews</a>
        </div>
      </div>
    </section>

    <!-- ===== FAQ ===== -->
    <section class="section" id="faq">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Common questions</span>
          <h2>Mobile tyre fitting in {town['short']} — your questions</h2>
          <p>Straight answers. If yours isn't here, call us on <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY.replace(' ', '&nbsp;')}</a>.</p>
        </div>
        <div class="faq-grid stagger">
{faqs}
        </div>
      </div>
    </section>

    <!-- ===== Closing CTA ===== -->
    <section class="offer">
      <div class="wrap reveal">
        <div class="ot">
          <div class="badge30">24<small>/7</small></div>
          <div>
            <h3>Need a tyre in {town['short']} right now?</h3>
            <p>One call and we're on the way. Pay on completion — card or cash, only once the job's done.</p>
          </div>
        </div>
        <a class="btn-book" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> Call {PHONE_DISPLAY}</a>
      </div>
    </section>
  </main>

  <div class="marquee dark" aria-hidden="true">
    <div class="track">
      <span class="item"><svg class="icon"><use href="#i-pin"/></svg> {name}</span><span class="dot"></span>{marquee_items}
    </div>
  </div>

{FOOTER}
{STICKY}
  <script src="js/rates.js"></script>
  <script src="js/app.js" defer></script>
  <script src="js/ui.js" defer></script>
  <script>
    // town-specific rotator words (ui.js owns the animation; we only swap the list it reads)
    (function(){{var r=document.getElementById('rotator');if(!r)return;try{{window.RESQ_ROTATOR_WORDS=JSON.parse(r.getAttribute('data-words'));}}catch(e){{}}}})();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    for town in TOWNS:
        out = ROOT / f"mobile-tyre-fitting-{town['slug']}.html"
        out.write_text(build(town), encoding="utf-8")
        print("wrote", out.name, len(out.read_text()), "bytes")
