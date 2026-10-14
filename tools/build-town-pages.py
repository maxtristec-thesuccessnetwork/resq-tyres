#!/usr/bin/env python3
"""Build the town landing pages from index.html's own head + one data block per town.

    python3 tools/build-town-pages.py            # writes /mobile-tyre-fitting-<slug>.html for every town below

Design rules (so the pages stay honest and stay on-brand):
  * The <head> critical CSS block is lifted VERBATIM from index.html at build time, so a
    change to the home page's fonts or above-fold CSS flows through on the next build.
  * Hours: 24 hours a day, 7 days, since 8 Oct 2026.
  * Arrival: about 40 minutes on average, confirmed by the business on 8 Oct 2026; not on the Harrogate page, which is a longer drive.
  * Distance: straight-line miles from the LS9 8JB base to the town's district centroid (tools/outcodes.json),
    rounded and always labelled "as the crow flies". Miles, never minutes.
  * Prices are per tyre — from £40 (14–17") / from £80 (18–20") — with mobile fitting from £50 per tyre
    on top. The exact range per size lives on the home page's price guide; these pages link to it.
    The hero shows both parts and the total (PRICE_LINE). Never a single all-in price.
    Puncture repair £70–£120 and "30% off the total price" for a planned fitting of all four tyres are repeated as published on the home page.
  * Every district listed is in js/rates.js RESQ_COVERAGE.districts — the checker on the
    page uses the same list, so the page can never claim more than the checker allows.
  * First phone screen (5 Oct 2026): the call button, the Google rating and the price line must
    sit above the bottom bar on a 360px-wide phone showing 640px of page (a 360x740 screen with the
    browser's own bars on), and the call button must start above 430px. A long headline or `sub`
    pushes the button down, so the build stops past H1_MAX or SUB_MAX characters. Look at a phone
    screenshot after adding a town all the same — the limits are a guard, not a measurement.
  * Every WhatsApp link opens with a message already typed (WA); a bare link stops the build.
  * Each page is written in its own words (the town-page standard): how a call-out works, the van and
    the offer live on the home page, and a town page gets one line and a link. Headings, service cards,
    the price answer and the closing call to action are written per town, not the same sentence with
    the name swapped.
  * Two empty slots per town, filled only with real material:
      local_review = dict(quote=..., name=..., month=..., place=..., url=...)
          a Google review that names the town or a place in it, quoted exactly, with the
          reviewer's first name, month and year, and the link to it. Until there is one, the page shows
          the rating line and a link to Google, and no review cards.
      local_job = dict(img=(src420, src760, w, h), alt=..., caption=...)
          a photo of a job done in that town (no plates, no faces) and a one-line caption
          with place and month, e.g. "Puncture repair, Ossett WF5, October 2026".
    Never fill either from another town, from stock, or from a review that doesn't name the area.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SITE = "https://www.resqtyres.co.uk"
PHONE_DISPLAY, PHONE_TEL, PHONE_E164 = "07438 562633", "07438562633", "+447438562633"
# Same message as the home page, so the top bar, footer and bottom bar lifted from it match.
# It ends where the customer starts typing.
WA = "https://wa.me/447438562633?text=" + quote("Hi ResQ, I need a tyre fitted. I'm at: ", safe="")
# One honest price line for every hero, word for word as on the home page.
PRICE_LINE = "<b>Tyres from £40, fitting from £50: one tyre fitted from £90.</b> Price agreed on the phone before we set off."
assert PRICE_LINE in INDEX, "PRICE_LINE no longer matches the home page hero — keep one price line on every page"
# First phone screen: Harrogate's 52-character headline fills three lines at 360px wide, and an
# 81-character `sub` plus the price line fills five. One line more and the call button starts
# below 430px.
H1_MAX, SUB_MAX = 52, 81
COVERED = set(re.findall(r'"([A-Z]{2}\d{1,2})"', INDEX.split("RESQ_COVERAGE")[0]) or [])  # placeholder
COVERED = set(re.findall(r'"((?:LS|HG|WF|YO)\d{1,2})"', (ROOT / "js" / "rates.js").read_text()))

# Wikidata items for every place named in areaServed, so search engines know which Morley or
# Wakefield is meant. Towns inside a city district and villages are typed Place, not City.
WIKIDATA = {"Leeds": "Q39121", "Wakefield": "Q216638", "Dewsbury": "Q525508", "Pudsey": "Q1009290", "Morley": "Q1021179",
            "Castleford": "Q546485", "Garforth": "Q2559795", "Pontefract": "Q1009235", "Harrogate": "Q215829",
            "Tadcaster": "Q784467", "York": "Q42462", "Selby": "Q527846", "Ossett": "Q1788889", "Normanton": "Q1027131",
            "Wetherby": "Q817481", "Pannal": "Q2273404"}

# ------------------------------------------------------------------ head pieces from index.html
def slice_between(s: str, start: str, end: str) -> str:
    i = s.index(start); j = s.index(end, i) + len(end)
    return s[i:j]

CRITICAL_STYLE = slice_between(INDEX, "  <style>/* critical:", "  </style>\n")
ICON_DEFS = slice_between(INDEX, '  <svg width="0" height="0"', "</defs></svg>\n")
TOPBAR = slice_between(INDEX, "  <!-- ===== Top utility bar =====", "  <!-- ===== Header =====").rstrip() + "\n"
FOOTER = slice_between(INDEX, "  <!-- ===== Footer =====", "  </footer>\n")
STICKY = slice_between(INDEX, "  <!-- Back to top -->", '  </div>\n\n  <script src="js/rates.js" defer></script>').replace('  <script src="js/rates.js" defer></script>', "")
# No review cards on the town pages until each has real reviews from its own area: repeating
# the home page's three Leeds reviews made the two pages read as copies of each other.
# footer links are anchors on the home page; make them absolute so they work from a town page.
# Icon references (#i-...) stay local: each page carries its own inline sprite, and
# browsers do not load <use> symbols from another document.
FOOTER = re.sub(r'href="#(?!top|i-)', 'href="/#', FOOTER)
FOOTER = FOOTER.replace('href="#top"', 'href="/"')


def footer_for(path):
    """The footer without its link to the page it sits on (a link to yourself is a dead end)."""
    return re.sub(r'\n\s*<li><a href="' + re.escape(path) + r'">[^\n]*</li>', "", FOOTER)

# ------------------------------------------------------------------ towns
TOWNS = [
    dict(
        slug="wakefield", name="Wakefield", short="Wakefield", area_and="Wakefield", area_or="Wakefield", topbar_area=None, schema_where="across WF1 to WF13",
        title="Mobile Tyre Fitting Wakefield | 24/7 | ResQ Tyres",
        description="Mobile tyre fitting and puncture repair in Wakefield (WF1–WF13), 24 hours a day. Tyres from £40, pay on completion. Call 07438 562633.",
        h1="Flat tyre in Wakefield? We come to you.",
        rotator=["In Wakefield.", "In Ossett.", "In Castleford.", "In Pontefract.", "Day or night."],
        sub="Mobile tyre fitting across Wakefield (WF1–WF13), 24 hours a day.",
        # Its own hero: the home page's van-and-Audi photo was the first thing on both pages.
        hero_img=([("assets/wheelchange-hero-420.webp", 420), ("assets/wheelchange-hero-760.webp", 760)], 760, 798,
                  "White Tesla raised on a jack at the roadside with its rear wheel off, during a ResQ Tyres call-out"),
        svc_photos=[("assets/roadside-fit-420-v3.webp", "assets/roadside-fit-760-v3.webp", "420w", "760w", 760, 760,
                     "Car raised on a jack with the wheel removed during ResQ Tyres mobile tyre fitting"),
                    ("assets/hero-resq-600-v4.webp", "assets/hero-resq-760-v4.webp", "600w", "760w", 760, 798,
                     "ResQ Tyres van parked beside a blue Audi with its front wheel off, part-way through a mobile tyre fitting")],
        stat_area=("WF1–WF13", "Every Wakefield district"),
        stat_miles=("8 miles", "From our Leeds base"),
        cover_heading="WF1–WF13, from Wakefield to Dewsbury",
        cover_intro="We cover every district from WF1 to WF13: the city, the Five Towns and out to Dewsbury. We come to you from our base in east Leeds, about 8 miles from Wakefield city centre as the crow flies.",
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
        edge="If you're in Barnsley, Huddersfield or WF14 and above, call us anyway. We may still be able to reach you.",
        related='Further north? See <a href="/mobile-tyre-fitting-harrogate">mobile tyre fitting in Harrogate &amp; Tadcaster</a>, or <a href="/">mobile tyre fitting in Leeds</a>.',
        landmarks="the M1 around junctions 39–41, the M62 around Wakefield, the A61 into Leeds, Trinity Walk and the Ridings car parks, Pinderfields, and the station car parks at Westgate and Kirkgate",
        svc_eyebrow="Tyres and punctures",
        svc_heading="Punctures, blowouts and new tyres from WF1 to WF13",
        svc_intro="If the puncture can be safely repaired, we repair it. If it can't, a new tyre comes off the van and goes on where the car is. Flat battery instead? Our <a href=\"/jump-start-leeds\">flat battery call-out</a> comes down to Wakefield too, from &pound;50.",
        svc_cards=[("Flat · Blowout · Puncture", "i-wheel", "On the drive or in the car park",
                    "A driveway in Sandal, a work car park in Castleford or a street in Ossett: the tyre is fitted where you are."),
                   ("Home · Work · Roadside", "i-home", "Everything comes on the van",
                    "New tyres, balancing kit, valves and locking-nut tools all come down from Leeds with us, so most Wakefield jobs need one visit.")],
        local_review=None,   # RESQ-2103: a real Google review that names Wakefield or a WF place
        local_job=None,      # RESQ-2093: one dated Wakefield job photo from the business
        faq_heading="Mobile tyre fitting in Wakefield: what people ask",
        cta_heading="Stuck in Wakefield, Ossett or Pontefract?",
        cta_text="Call any time, day or night. We'll tell you the price and when we can be there, then drive down from Leeds. You pay by card or cash when the job's done.",
        faq=[
            ("Does ResQ cover all of Wakefield?",
             "Yes. ResQ covers every Wakefield district from <b>WF1</b> to <b>WF13</b>: Wakefield itself, Ossett, Horbury, Normanton, Featherstone, Pontefract, Hemsworth, Castleford, Knottingley and Dewsbury. Type your postcode into the checker above if you want to be sure."),
            ("Can ResQ come out to me now in Wakefield?",
             f"Yes. ResQ comes out in Wakefield 24 hours a day, 7 days a week. On average we're with you in about 40 minutes. Call <a href=\"tel:{PHONE_TEL}\">{PHONE_DISPLAY.replace(' ', '&nbsp;')}</a> or message us on WhatsApp. In an emergency, ringing is faster than filling in a form."),
            ("Does ResQ repair punctures in Wakefield, or only replace tyres?",
             "Both. If the tyre can be safely repaired, ResQ repairs it at the roadside or on your drive in Wakefield. If it can't, we carry new tyres on the van and fit one on the spot. Puncture repair is &pound;70–&pound;120 depending on distance and tyre size."),
            ("Where in Wakefield can ResQ fit a tyre?",
             f"Wherever the car is: your driveway in Sandal or Outwood, a work car park, a motorway hard shoulder or a service station. ResQ also covers {'the M1 around junctions 39–41, the M62 around Wakefield, the A61 into Leeds'}, and the retail and station car parks in the city centre. On a motorway, get out by the left-hand door and wait behind the barrier while you call. If you've stopped in a live lane, or you're in danger, call 999 first."),
            ("How much is mobile tyre fitting in Wakefield?",
             "<b>From &pound;90 for one tyre, fitted</b>: the tyre from &pound;40 and mobile fitting from &pound;50. A 14–17\" tyre is &pound;40–&pound;100 and an 18–20\" one &pound;80–&pound;150, depending on the brand. The fitting part depends on how far into WF1–WF13 we're driving. You get the exact figure on the phone before we leave, it's the same at 3am as at 3pm, and there's no call-out fee on top. A planned fitting of all four tyres is 30% off the total, subject to availability. No deposit: pay by card or cash once the car's back on the road. Your size is in the <a href=\"/#estimate\">price guide</a>."),
            ("Do you go to Barnsley, Huddersfield or Mirfield?",
             "They're outside our confirmed area: Barnsley is S postcodes, Huddersfield is HD, and Mirfield and Heckmondwike are WF14 and above. Call us anyway and tell us where you are. We may still be able to reach you, and if we can't, we'll say so straight away."),
        ],
        marquee=["Ossett", "Horbury", "Normanton", "Castleford", "Pontefract", "Featherstone", "Hemsworth", "Knottingley", "Dewsbury"],
        served=[("City", "Wakefield"), ("Place", "Ossett"), ("Place", "Castleford"), ("Place", "Pontefract"), ("Place", "Normanton"), ("City", "Dewsbury")],
    ),
    dict(
        slug="harrogate", name="Harrogate", short="Harrogate &amp; Tadcaster", area_and="Harrogate and Tadcaster", area_or="Harrogate or Tadcaster", topbar_area="Harrogate &amp; Tadcaster", schema_where="in HG1 to HG3 and LS24 Tadcaster",
        title="Mobile Tyre Fitting Harrogate & Tadcaster | ResQ Tyres",
        description="Mobile tyre fitting and puncture repair in Harrogate (HG1–HG3) and Tadcaster, 24 hours a day. Tyres from £40. Call 07438 562633.",
        h1="Flat tyre in Harrogate or Tadcaster? We come to you.",
        rotator=["In Harrogate.", "In Pannal.", "In Tadcaster.", "On the A61.", "Day or night."],
        sub="Mobile tyre fitting across Harrogate and out to Tadcaster, 24 hours a day.",
        hero_img=([("assets/roadside-fit-hero-420.webp", 420), ("assets/roadside-fit-hero-760.webp", 760)], 760, 798,
                  "Black hatchback on a jack with its front wheel off, part-way through a ResQ Tyres mobile tyre fitting"),
        # The hero is the roadside job, so the service cards show the van and Audi job and the Tesla job.
        svc_photos=[("assets/hero-resq-600-v4.webp", "assets/hero-resq-760-v4.webp", "600w", "760w", 760, 798,
                     "ResQ Tyres van parked beside a blue Audi with its front wheel off, part-way through a mobile tyre fitting"),
                    ("assets/wheelchange-420-v3.webp", "assets/wheelchange-760-v3.webp", "420w", "760w", 760, 760,
                     "White car with its rear wheel off at the side of the road during a ResQ Tyres emergency call-out")],
        stat_area=("HG1–HG3 · LS24", "Harrogate &amp; Tadcaster"),
        stat_miles=("14 miles", "Leeds base to Harrogate"),
        cover_heading="Harrogate, the villages around it, Tadcaster and York",
        cover_intro="We come up the A61 and the A658 from Leeds to cover all three Harrogate districts and the Tadcaster side of LS24. Harrogate is about 14 miles from our base in east Leeds as the crow flies, and Tadcaster about 12. You get the same van and tyres as in Leeds, so there's no need to take the car to a garage in town.",
        districts=[
            ("HG1", "Harrogate town centre, Bilton, Starbeck, New Park, High Harrogate"),
            ("HG2", "Oatlands, Pannal, Harlow Hill, Hornbeam Park, Burn Bridge"),
            ("HG3", "Killinghall, Ripley, Hampsthwaite, Birstwith, Spofforth, Follifoot, Kirkby Overblow, Beckwithshaw"),
            ("LS24", "Tadcaster, Stutton, Towton, Saxton, Church Fenton, Ulleskelf"),
            ("LS22 · LS23", "Wetherby, Boston Spa, Thorp Arch (all between Harrogate and Tadcaster)"),
            ("YO1 · YO10 · YO24", "York city centre, Fulford, Heslington, Acomb, Dringhouses"),
            ("YO8", "Selby"),
        ],
        edge="Knaresborough (HG5), Ripon (HG4) and the rest of York are just outside our confirmed patch, but call us anyway. We may still be able to reach you.",
        related='Nearer Wakefield? See <a href="/mobile-tyre-fitting-wakefield">mobile tyre fitting in Wakefield</a>, or <a href="/">mobile tyre fitting in Leeds</a>.',
        landmarks="the A61 Leeds Road and Harrogate Road, the A59 towards Knaresborough, the A658 past the airport, the Stray, Harrogate station and the Victoria car park, and the A64 and A659 around Tadcaster",
        svc_eyebrow="On the van",
        svc_heading="Tyres fitted in Harrogate, Tadcaster and the villages between",
        svc_intro="The van brings brand-new tyres and the kit for balancing, valves and locking wheel nuts up from Leeds, so a job in Pannal or Boston Spa is finished in one visit, the same as in town. The <a href=\"/jump-start-leeds\">flat battery call-out</a> covers HG1–HG3 and LS24 as well, from &pound;50.",
        svc_cards=[("Town · Villages · A61", "i-wheel", "Wherever you've stopped",
                    "Bilton, Killinghall, Spofforth or a lay-by on the A61: we repair the puncture or fit a new tyre on the spot."),
                   ("Tadcaster · LS24", "i-home", "Tadcaster and the LS24 villages",
                    "Stutton, Towton, Church Fenton and Ulleskelf are all in LS24, so they're in our area.")],
        local_review=None,   # RESQ-2103: a real Google review that names Harrogate, Tadcaster or an HG/LS24 place
        local_job=None,      # RESQ-2093: one dated Harrogate or Tadcaster job photo from the business
        faq_heading="Harrogate and Tadcaster: questions about mobile tyre fitting",
        cta_heading="Flat tyre in Harrogate, Pannal or Tadcaster?",
        cta_text="Ring us, day or night, and say where the car is. It's a longer drive than around Leeds, so we'll give you the price and a straight answer on timing before we set off.",
        faq=[
            ("Which parts of Harrogate does ResQ cover?",
             "ResQ covers all three Harrogate districts (<b>HG1</b>, <b>HG2</b> and <b>HG3</b>), including the town centre, Bilton, Starbeck, Oatlands, Pannal, Killinghall, Ripley and the villages out towards Pateley Bridge. Plus <b>LS24</b> for Tadcaster. Knaresborough and Ripon are just outside, but call and ask."),
            ("Can ResQ come out to Harrogate now?",
             f"Yes. ResQ comes out to Harrogate and Tadcaster 24 hours a day, 7 days a week. We come up from Leeds, so tell us where you are when you call <a href=\"tel:{PHONE_TEL}\">{PHONE_DISPLAY.replace(' ', '&nbsp;')}</a> or WhatsApp us, and we'll give you a straight answer on when we can be with you."),
            ("Does ResQ repair punctures in Harrogate and Tadcaster?",
             "Yes. If the tyre can be safely repaired, ResQ repairs it where the car is in Harrogate or Tadcaster. If it can't, we carry new tyres on the van and fit one on the spot. Puncture repair is &pound;70–&pound;120 depending on distance and tyre size."),
            ("Where in Harrogate can ResQ fit the tyre?",
             "Wherever the vehicle is: a driveway in Pannal, a work car park at Hornbeam Park, a street off the Stray, or a lay-by on the A61. ResQ's van carries brand-new tyres and the kit for on-site balancing and valve replacement, so most jobs are finished in one visit."),
            ("How much is mobile tyre fitting in Harrogate?",
             "Harrogate and Tadcaster are a longer drive from our Leeds base, so the fitting part of the price depends most on where you are. It starts at &pound;50 per tyre, and tyres start at &pound;40, so <b>one tyre fitted starts at &pound;90</b>. Tyres run from &pound;40 to &pound;100 for 14–17\" wheels and &pound;80 to &pound;150 for 18–20\", by brand. We tell you the whole price on the phone before we set off. Nights cost the same as days, and there's no extra call-out charge. Four tyres at a planned time get 30% off the total, subject to availability. Nothing is paid up front; you settle up by card or cash at the end. See the <a href=\"/#estimate\">price guide</a> for your tyre size."),
            ("Do you go to Knaresborough or Ripon?",
             "Knaresborough (HG5) and Ripon (HG4) are just outside our confirmed patch, and so is the rest of York beyond YO1, YO10 and YO24. Ring us with the postcode anyway. If we can get to you, we'll say when; if we can't, you'll know straight away."),
        ],
        marquee=["Bilton", "Starbeck", "Pannal", "Killinghall", "Ripley", "Spofforth", "Tadcaster", "Boston Spa", "Wetherby"],
        served=[("City", "Harrogate"), ("City", "Tadcaster"), ("City", "York"), ("City", "Selby"), ("Place", "Pannal"), ("Place", "Wetherby")],
    ),
]

# ------------------------------------------------------------------ builders
def check_districts(town):
    for code, _ in town["districts"]:
        for c in re.split(r"\s*·\s*", code):
            assert c in COVERED, f"{town['slug']}: {c} is not in RESQ_COVERAGE.districts — do not publish a district the checker refuses"

def check_first_screen(town):
    for key, limit in (("h1", H1_MAX), ("sub", SUB_MAX)):
        n = len(html.unescape(re.sub("<[^>]+>", "", town[key])))
        assert n <= limit, f"{town['slug']}: `{key}` is {n} characters (limit {limit}) — on a 360px phone it pushes the call button off the first screen. Shorten it"

def schema(town):
    url = f"{SITE}/mobile-tyre-fitting-{town['slug']}"
    name_plain = html.unescape(town["short"])
    service = {
        "@context": "https://schema.org", "@type": "Service",
        "@id": url + "#service",
        "name": f"Mobile tyre fitting in {name_plain}",
        "serviceType": "Mobile tyre fitting and puncture repair",
        "description": f"Mobile tyre fitting and puncture repair at your home, workplace or the roadside {town['schema_where']}, 24 hours a day, 7 days a week.",
        "url": url,
        "provider": {"@type": "AutoRepair", "@id": f"{SITE}/#business", "name": "ResQ Tyres & Recovery",
                     "telephone": PHONE_E164, "url": SITE + "/"},
        "areaServed": [{"@type": t, "name": n, "sameAs": f"https://www.wikidata.org/wiki/{WIKIDATA[n]}"} for t, n in town["served"]],
        # prices exactly as the hero and FAQ state them; "from" prices are minPrice, never price.
        # The offer covers fitting and puncture repair, so minPrice is the lowest of the two (repair from £70).
        "offers": {"@type": "Offer",
                   "priceSpecification": {"@type": "PriceSpecification", "minPrice": 70, "priceCurrency": "GBP"},
                   "description": "Tyres from £40, mobile fitting from £50 per tyre: one tyre fitted from £90. Puncture repair £70–£120. Exact price confirmed by phone before any work starts."},
        "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": PHONE_E164, "contactType": "customer service", "availableLanguage": "en"}},
        "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59"},
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": html.unescape(re.sub("<[^>]+>", "", q)),
                           "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<[^>]+>", "", a))}} for q, a in town["faq"]]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ResQ Tyres & Recovery", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": f"Mobile tyre fitting in {name_plain}", "item": url}]}
    return "\n".join(f'  <script type="application/ld+json">\n{json.dumps(d, ensure_ascii=False, indent=2)}\n  </script>' for d in (service, faq, crumbs))

def build(town) -> str:
    check_districts(town)
    check_first_screen(town)
    slug, name = town["slug"], town["name"]
    url = f"{SITE}/mobile-tyre-fitting-{slug}"
    hero_set, iw, ih, alt = town["hero_img"]
    cards = "\n".join(f"""          <article class="svc">
            <div class="ph"><img src="{ph[0]}" srcset="{ph[0]} {ph[2]}, {ph[1]} {ph[3]}" sizes="(max-width:760px) 92vw, (max-width:1100px) 46vw, 670px" width="{ph[4]}" height="{ph[5]}" alt="{ph[6]}" loading="lazy" decoding="async"></div>
            <div class="body">
              <span class="tagline"><svg class="icon" aria-hidden="true"><use href="#{icon}"/></svg> {tag}</span>
              <h3>{h3}</h3>
              <p>{text}</p>
            </div>
          </article>""" for ph, (tag, icon, h3, text) in zip(town["svc_photos"], town["svc_cards"]))
    review, job = town["local_review"], town["local_job"]
    review_html = ""
    if review:
        assert all(review.get(k) for k in ("quote", "name", "month", "place", "url")), f"{town['slug']}: a local review needs the exact quote, first name, month, place and link"
        review_html = f"""
        <div class="reviews">
          <blockquote class="review">
            <span class="stars">★★★★★</span>
            <p>"{review['quote']}"</p>
            <span class="who"><span class="gicon">G</span> <b>{review['name']}</b> · {review['place']} · {review['month']} · <a href="{review['url']}" target="_blank" rel="noopener">Google review</a></span>
          </blockquote>
        </div>"""
    job_html = ""
    if job:
        assert job.get("caption") and job.get("alt"), f"{town['slug']}: a local job photo needs alt text and a caption with place and month"
        j = job["img"]
        job_html = f"""
            <figure class="local-job"><img src="{j[0]}" srcset="{j[0]} 420w, {j[1]} 760w" sizes="(max-width:900px) 92vw, 420px" width="{j[2]}" height="{j[3]}" alt="{job['alt']}" loading="lazy" decoding="async"><figcaption>{job['caption']}</figcaption></figure>"""
    src1 = hero_set[0][0]
    srcset = ", ".join(f"{src} {w}w" for src, w in hero_set)
    rot_words = json.dumps(town["rotator"], ensure_ascii=False)
    topbar = TOPBAR
    if town.get("topbar_area"):
        assert "Emergency call-outs across Leeds, Wakefield &amp; Harrogate" in TOPBAR, "home page top bar wording changed"
        topbar = TOPBAR.replace("Emergency call-outs across Leeds, Wakefield &amp; Harrogate", f"Emergency call-outs across {town['topbar_area']}")
    districts = "\n".join(
        f'            <li class="district"><b>{code}</b><span>{places}</span></li>' for code, places in town["districts"])
    faqs = "\n".join(
        f'          <div class="faq-item">\n            <h3>{q}</h3>\n            <p>{a}</p>\n          </div>' for q, a in town["faq"])
    marquee_items = "".join(
        f'<span class="item">{m}</span><span class="dot"></span>' for m in town["marquee"])  # js/ui.js adds the loop copy
    served_names = ", ".join(n for _, n in town["served"])
    # the strip under the hero names this town's districts, so it is never the same on two pages
    district_strip = "\n".join(
        f'        <span class="item"><svg class="icon"><use href="#i-pin"/></svg> {code} {places.split(",")[0]}</span><span class="dot"></span>'
        for code, places in town["districts"][:6])

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <script>document.documentElement.className+=" js";setTimeout(function(){{if(!window.RESQ_UI)document.documentElement.classList.remove("js")}},3000);</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(town['title'], quote=False)}</title>
  <meta name="description" content="{html.escape(town['description'], quote=True)}">
  <meta name="theme-color" content="#e4002b">
  <link rel="canonical" href="{url}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(town['title'], quote=True)}">
  <meta property="og:description" content="{html.escape(town['description'], quote=True)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/assets/share-1200x630-v2.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="The ResQ Tyres &amp; Recovery van, lettered with the ResQ Tyres name and phone number">
  <meta property="og:locale" content="en_GB">
  <meta property="og:site_name" content="ResQ Tyres &amp; Recovery">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" href="/assets/icon-192.png" type="image/png" sizes="192x192">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="preload" href="fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>
{CRITICAL_STYLE}  <link rel="stylesheet" href="css/styles.css" media="print" onload="this.media='all';this.onload=null">
  <noscript><link rel="stylesheet" href="css/styles.css"></noscript>
  <link rel="preload" as="image" href="{src1}" imagesrcset="{srcset}" imagesizes="(max-width:900px) 92vw, 560px" fetchpriority="high">
  <style>
    /* town-page additions — everything else comes from css/styles.css */
    .districts{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}}
    .district{{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:baseline;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;box-shadow:var(--shadow-sm)}}
    .district b{{font-size:15px;color:var(--red);white-space:nowrap;font-variant-numeric:tabular-nums}}
    .district span{{font-size:14px;color:var(--muted);line-height:1.45}}
    .cover-grid{{display:grid;gap:26px;align-items:start}}
    @media(min-width:900px){{.cover-grid{{grid-template-columns:1.25fr .75fr}}}}
    .cover-edge{{margin-top:14px;font-size:14px;color:var(--muted)}}
    .svc-how{{margin-top:10px;font-size:15px;color:var(--muted)}}
    .help-cta{{justify-content:center;margin-top:6px}}
    .crumbs{{font-size:13px;color:var(--muted);margin-bottom:14px}}
    .crumbs a{{color:inherit;text-decoration:none}} .crumbs a:hover{{text-decoration:underline}}
    .crumbs span{{margin:0 6px;opacity:.6}}
    @media(max-width:760px){{.crumbs{{display:none}}}} /* phones: the call button comes first */
    .local-job{{margin:16px 0 0}} .local-job img{{width:100%;height:auto;border-radius:var(--radius)}}
    .local-job figcaption{{font-size:13px;color:var(--muted);margin-top:6px}}
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

{topbar}
  <!-- ===== Header ===== -->
  <header class="site-header">
    <div class="wrap bar">
      <a href="/" class="logo">
        <img src="assets/logo-108.webp" alt="ResQ Tyres &amp; Recovery logo" width="54" height="54" decoding="async">
        <span class="logo-text">ResQ Tyres<small>&amp; RECOVERY<span class="est"> · EST 2023</span></small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#services">What we do</a>
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
            <p class="crumbs"><a href="/">ResQ Tyres</a><span>›</span>Mobile tyre fitting in {town['short']}</p>
            <span class="live-badge"><span class="dot" aria-hidden="true"></span> <span data-open-status>Open 24/7</span><span class="badge-extra"> · {town['short']}</span></span>
            <h1>{town['h1']}</h1>
            <p class="hero-rating" data-nosnippet><span class="stars" aria-hidden="true">★</span> 5.0 on Google · 230+ reviews</p>
            <div class="rotator" id="rotator" aria-hidden="true" data-words='{rot_words}'>{town['rotator'][0]}</div>
            <p class="hero-sub">{town['sub']} {PRICE_LINE}</p>
            <div class="cta-row">
              <a class="cta-primary pulse" href="tel:{PHONE_TEL}"><svg class="icon" aria-hidden="true"><use href="#i-phone"/></svg> Call {PHONE_DISPLAY}</a>
              <a class="cta-whatsapp" href="{WA}" target="_blank" rel="noopener"><svg class="icon" aria-hidden="true"><use href="#i-whatsapp"/></svg> WhatsApp</a>
              <a class="cta-secondary" href="/#enquiry">Plan a home fitting <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
            </div>
            <div class="scroll-cue" aria-hidden="true"><span class="mouse"></span>Scroll</div>
          </div>

          <div class="hero-photo">
            <div class="frame">
              <img src="{src1}" srcset="{srcset}" sizes="(max-width:900px) 92vw, 560px"
                 width="{iw}" height="{ih}" alt="{alt}" loading="eager" fetchpriority="high" decoding="async" id="heroImg" data-hero>
              <div class="tag"><svg class="icon" aria-hidden="true"><use href="#i-shield"/></svg><div><b>Pay on completion</b><span>No upfront payment</span></div></div>
            </div>
            <div class="floatcard" data-nosnippet><b><span data-count="5.0" data-dec="1">5.0</span><span class="star" aria-hidden="true">★</span></b><span>230+ Google reviews</span></div>
          </div>
        </div>
      </div>

      <div class="stats">
        <div class="wrap stagger">
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-clock"/></svg><div><b>24<small class="of">/7</small></b><span>Day or night</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-pin"/></svg><div><b>{town['stat_area'][0]}</b><span>{town['stat_area'][1]}</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg><div><b>{town['stat_miles'][0]}</b><span>{town['stat_miles'][1]}, as the crow flies</span></div></div>
          <div class="stat"><svg class="icon" aria-hidden="true"><use href="#i-card"/></svg><div><b>Pay on completion</b><span>Card or cash</span></div></div>
        </div>
      </div>
    </section>

    <div class="marquee" aria-hidden="true">
      <div class="track">
{district_strip}
      </div>
    </div>

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
            <p class="cover-edge">{town['related']}</p>{job_html}
          </div>
          <div class="area-side">
            <div class="pc-checker">
              <label for="pc-check">Check your postcode</label>
              <div class="pc-row">
                <input id="pc-check" type="text" placeholder="e.g. {town['districts'][0][0].split(' ')[0]}" maxlength="8" autocomplete="postal-code">
                <button type="button" id="pc-btn" class="btn-find"><svg class="icon" aria-hidden="true"><use href="#i-pin"/></svg> Check postcode</button>
              </div>
              <p class="pc-result" id="pc-result" role="status" aria-live="polite" hidden></p>
              <p class="micro">Same checker as our <a href="/#areas">main coverage map</a>.</p>
            </div>
            <div class="landmarks"><b>Roads and places we cover include:</b> {town['landmarks']}.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Services ===== -->
    <section class="section" id="services">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">{town['svc_eyebrow']}</span>
          <h2>{town['svc_heading']}</h2>
          <p>{town['svc_intro']}</p>
          <p class="svc-how">How a call-out works, start to finish, is on the <a href="/#how">home page</a>.</p>
        </div>
        <div class="services stagger">
{cards}
        </div>
      </div>
    </section>

    <!-- ===== Reviews ===== -->
    <section class="section soft" id="reviews">
      <div class="wrap">
        <div class="rev-head reveal">
          <h2 class="sr-only" data-nosnippet>Reviews of ResQ Tyres, mobile tyre fitting in {name}: rated 5.0 on Google from more than 230 reviews</h2>
          <span class="eyebrow">Google reviews</span>
          <span class="stars" style="font-size:22px">★★★★★</span>
          <span class="big"><span data-count="5.0" data-dec="1">5.0</span> on Google</span>
          <span class="micro" data-nosnippet>Rated 5.0 from 233 Google reviews, checked October 2026</span>
        </div>{review_html}
        <div class="reviews-cta reveal">
          <a class="rev-google" href="https://www.google.com/maps?cid=11412519892778241080" target="_blank" rel="noopener"><span class="gicon">G</span> Read all our reviews on Google</a>
        </div>
      </div>
    </section>

    <!-- ===== FAQ ===== -->
    <section class="section" id="faq">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="eyebrow">Common questions</span>
          <h2>{town['faq_heading']}</h2>
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
          <div class="badge30">£40<small>from</small></div>
          <div>
            <h3>{town['cta_heading']}</h3>
            <p>{town['cta_text']}</p>
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

{footer_for('/mobile-tyre-fitting-' + slug)}
{STICKY}
  <script src="js/rates.js" defer></script>
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
        page = build(town)
        assert 'wa.me/447438562633"' not in page, f"{town['slug']}: a WhatsApp link opens a blank chat — give it a message"
        out.write_text(page, encoding="utf-8")
        print("wrote", out.name, len(out.read_text()), "bytes")
