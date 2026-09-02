#!/usr/bin/env python3
"""
ResQ Tyres — build the static coverage map (assets/coverage-map.svg).

Why this exists
---------------
The #areas map used to be a Leaflet slippy map pulling tiles from CARTO's
unauthenticated basemap CDN. On 2026-09-02 those tiles started coming back
stamped "API KEY REQUIRED" — HTTP 200, correct MIME type, watermark baked into
the image, so no health check could ever have caught it. Card W5, option A:
drop the third-party tile dependency altogether.

What the map claims
-------------------
Nothing this file invents. The coverage picture is drawn from the postcode
districts Moin confirmed by WhatsApp on 2026-09-01 (card W1) — all LS, HG1-HG3,
and WF1-WF5/WF8/WF10/WF12/WF13 — with each district's real centroid from
postcodes.io. There is deliberately NO hard boundary line: an edge would be a
claim about places nobody has confirmed, and the old 17 km circle was drawing
one that wrongly swallowed Bradford. Instead each confirmed district is a dot,
with a soft unlabelled glow behind the cloud for grouping only. The postcode
checker beside the map is the exact answer; the map is the shape of the patch.

Motorway centrelines come from OpenStreetMap (ODbL) — attribution is rendered
bottom-right of the SVG and must stay there.

The SVG is referenced from index.html as <img src="assets/coverage-map.svg" loading="lazy">,
NOT inlined. Inlining it cost 27 KB in the HTML and measurably delayed the hero:
Lighthouse mobile, three runs each, identical local serving — inline scored 58 with
LCP 7.0 s, external+lazy scored 74 with LCP 4.8 s. It therefore carries its own
<style> block, because an <img> gets none of the page's CSS.

Usage:  python3 tools/build-coverage-map.py > assets/coverage-map.svg
            re-fetches roads from Overpass (mirrors are often busy; it tries three)
        python3 tools/build-coverage-map.py --cached > assets/coverage-map.svg
            uses tools/osm-motorways.json.gz, the trimmed extract committed beside
            this script, so the build is reproducible with no network at all

District centroids live in tools/outcodes.json (postcodes.io, read 2026-09-02).
To change coverage, change client.yaml and this file together — never one alone.
"""
import gzip, json, math, os, sys, urllib.parse, urllib.request

W, H = 620, 560
PAD_KM = 3.5
BUFFER_KM = 6.5            # soft glow radius around each district centroid
BBOX = "53.55,-2.05,54.15,-1.15"
MAJOR = ['M62', 'M1', 'A1(M)', 'M621', 'A58(M)', 'A64(M)']
ENDPOINTS = ["https://overpass.private.coffee/api/interpreter",
             "https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter"]
HERE = os.path.dirname(os.path.abspath(__file__))

# Named towns get a labelled pin. Coordinates are the ones the site has always
# used, plus Harrogate and Tadcaster from their district centroids (W1).
TOWNS = [
    (53.8008, -1.5491, "Leeds", True),
    (53.6830, -1.4977, "Wakefield", False),
    (53.6912, -1.6290, "Dewsbury", False),
    (53.7967, -1.6631, "Pudsey", False),
    (53.7491, -1.6010, "Morley", False),
    (53.7256, -1.3560, "Castleford", False),
    (53.7928, -1.3872, "Garforth", False),
    (53.6919, -1.3128, "Pontefract", False),
    (53.9928, -1.5418, "Harrogate", False),
    (53.8845, -1.2620, "Tadcaster", False),
]
PLACE = {   # label offset from the pin: dx, dy, text-anchor
    "Leeds": (0, -19, "middle"),      "Pudsey": (-11, 4, "end"),
    "Garforth": (0, -16, "middle"),   "Morley": (-11, 4, "end"),
    "Castleford": (0, -16, "middle"), "Dewsbury": (0, 21, "middle"),
    "Wakefield": (0, 21, "middle"),   "Pontefract": (0, 21, "middle"),
    "Harrogate": (0, -16, "middle"),  "Tadcaster": (0, -16, "middle"),
}
BADGE_ANCHORS = {   # nearest point on that road to this anchor, then nudged
    'M62w': ('M62', (53.7000, -1.8200), 26, -13),
    'M62e': ('M62', (53.7050, -1.3400), 0, -13),
    'M1':   ('M1',  (53.6700, -1.4200), 20, 0),
    'M621': ('M621', (53.7650, -1.5900), -4, -13),
    'A1M':  ('A1(M)', (53.9400, -1.3400), 24, 0),
}
BADGE_TEXT = {'M62w': 'M62', 'M62e': 'M62', 'M1': 'M1', 'M621': 'M621', 'A1M': 'A1(M)'}


def merc(lat, lng):
    return math.radians(lng), math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def dest(lat, lng, brg_deg, dist_km):
    R = 6371.0088
    br, d = math.radians(brg_deg), dist_km / R
    p1, l1 = math.radians(lat), math.radians(lng)
    p2 = math.asin(math.sin(p1) * math.cos(d) + math.cos(p1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), math.degrees(l2)


OUTCODES = json.load(open(os.path.join(HERE, "outcodes.json")))

# --- fit the projection to the confirmed districts, then pad ---
_pts = []
for lat, lng in OUTCODES.values():
    for b in (0, 90, 180, 270):
        _pts.append(dest(lat, lng, b, PAD_KM + BUFFER_KM))
_xs = [merc(*p)[0] for p in _pts]; _ys = [merc(*p)[1] for p in _pts]
_minx, _maxx, _miny, _maxy = min(_xs), max(_xs), min(_ys), max(_ys)
_s = min(W / (_maxx - _minx), H / (_maxy - _miny))     # meet: show the whole patch
_cx, _cy = (_minx + _maxx) / 2, (_miny + _maxy) / 2


def px(lat, lng):
    x, y = merc(lat, lng)
    return ((x - _cx) * _s + W / 2, (_cy - y) * _s + H / 2)


KM = (px(*dest(53.83, -1.53, 90, 10))[0] - px(53.83, -1.53)[0]) / 10.0   # px per km


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
    def dist(p, a, b):
        (x0, y0), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x0 - x1, y0 - y1)
        t = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x0 - (x1 + t * dx), y0 - (y1 + t * dy))
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return simplify(pts[:idx + 1], eps)[:-1] + simplify(pts[idx:], eps)
    return [pts[0], pts[-1]]


def d_of(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def fetch_motorways():
    q = f'[out:json][timeout:120];way["highway"="motorway"]({BBOX});out geom;'
    body = ("data=" + urllib.parse.quote(q)).encode()
    last = None
    for url in ENDPOINTS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=150) as r:
                return json.loads(r.read())
        except Exception as e:          # Overpass mirrors are frequently busy
            last = e
            print(f"  {url} -> {e}", file=sys.stderr)
    raise SystemExit(f"All Overpass endpoints failed: {last}")


def main():
    if "--cached" in sys.argv:
        with gzip.open(os.path.join(HERE, "osm-motorways.json.gz"), "rt") as fh:
            data = json.load(fh)
    else:
        data = fetch_motorways()

    segs = {}
    for e in data['elements']:
        ref = e.get('tags', {}).get('ref')
        if not ref or ref not in MAJOR or 'geometry' not in e:
            continue
        pts = [px(g['lat'], g['lon']) for g in e['geometry']]
        if all(x < -60 or x > W + 60 or y < -60 or y > H + 60 for x, y in pts):
            continue
        pts = simplify(pts, 1.6)
        if len(pts) > 1:
            segs.setdefault(ref, []).append(pts)

    badges = []
    for key, (ref, anchor, ox, oy) in BADGE_ANCHORS.items():
        ax, ay = px(*anchor)
        best, bd = None, 1e18
        for pts in segs.get(ref, []):
            for (x, y) in pts:
                if not (20 < x < W - 20 and 20 < y < H - 20):
                    continue
                dd = (x - ax) ** 2 + (y - ay) ** 2
                if dd < bd:
                    bd, best = dd, (x, y)
        if best:
            badges.append((BADGE_TEXT[key], best[0] + ox, best[1] + oy))

    o = []
    a = o.append
    a(f'<svg class="cov-map" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
      f'aria-labelledby="covmap-t covmap-d" preserveAspectRatio="xMidYMid meet">')
    a('<title id="covmap-t">Where ResQ Tyres covers</title>')
    a('<desc id="covmap-d">Map of the ResQ Tyres coverage area. Every confirmed postcode district is '
      'marked: all Leeds LS districts including LS24 Tadcaster, HG1 to HG3 around Harrogate, and WF1 to '
      'WF5, WF8, WF10, WF12 and WF13 across Wakefield, Castleford, Pontefract and Dewsbury. Leeds, '
      'Pudsey, Morley, Dewsbury, Wakefield, Castleford, Garforth, Pontefract, Harrogate and Tadcaster '
      'are named, with the M1, M62, M621 and A1(M) running through.</desc>')

    # The SVG is loaded as <img>, so it gets none of the page's CSS and must
    # carry its own. Keep these in step with the .cov-map block in css/styles.css.
    a("""<style>
.cov-grid line{stroke:#fff;stroke-opacity:.028;stroke-width:1}
.cov-road-casing{fill:none;stroke:#05070a;stroke-width:5.5;stroke-linecap:round;stroke-linejoin:round;opacity:.9}
.cov-road{fill:none;stroke:#39455a;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.cov-road-lit{fill:none;stroke:#8ea3b8;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.cov-road-label rect{fill:rgba(11,14,19,.85);stroke:rgba(255,255,255,.16)}
.cov-road-label text{fill:#aeb6c0;font:700 10px/1 system-ui,sans-serif;letter-spacing:.02em}
.cov-district circle{fill:#ffe3e8;opacity:.62}
.cov-pin .cov-dot{fill:#e4002b;stroke:#fff;stroke-width:2}
.cov-pin.hub .cov-dot{stroke-width:2.5}
.cov-pin .cov-ping{fill:#e4002b;opacity:.42;transform-box:fill-box;transform-origin:center;animation:covPing 2.1s cubic-bezier(.2,.7,.3,1) infinite}
@keyframes covPing{0%{transform:scale(1);opacity:.42}80%,100%{transform:scale(3.4);opacity:0}}
.cov-pin .cov-name{fill:#fff;font:700 12px/1 system-ui,sans-serif;paint-order:stroke;stroke:rgba(5,7,10,.92);stroke-width:4px;stroke-linejoin:round}
.cov-pin.hub .cov-name{font-size:14px;font-weight:800}
.cov-scale line{stroke:rgba(255,255,255,.35);stroke-width:1.5}
.cov-scale text{fill:#7d8793;font:600 10px/1 system-ui,sans-serif}
.cov-note{fill:#8b95a1;font:600 10.5px/1 system-ui,sans-serif}
.cov-credit{fill:#5d6672;font:400 9px/1 system-ui,sans-serif}
@media(prefers-reduced-motion:reduce){.cov-pin .cov-ping{animation:none;opacity:.28}}
</style>""")

    a('<defs>')
    a('<radialGradient id="covGlow" cx="50%" cy="46%" r="58%">'
      '<stop offset="0%" stop-color="#ff2d55" stop-opacity=".155"/>'
      '<stop offset="70%" stop-color="#e4002b" stop-opacity=".105"/>'
      '<stop offset="100%" stop-color="#e4002b" stop-opacity=".07"/></radialGradient>')
    a('<radialGradient id="covVig" cx="50%" cy="46%" r="74%">'
      '<stop offset="60%" stop-color="#0b0e13" stop-opacity="0"/>'
      '<stop offset="100%" stop-color="#06080c" stop-opacity=".55"/></radialGradient>')
    a(f'<filter id="covSoft" filterUnits="userSpaceOnUse" x="-120" y="-120" '
      f'width="{W + 240}" height="{H + 240}">'
      f'<feGaussianBlur stdDeviation="{1.15 * KM:.1f}"/></filter>')
    # union of district buffers, as a mask so overlaps don't stack
    a('<mask id="covMask" maskUnits="userSpaceOnUse" '
      f'x="0" y="0" width="{W}" height="{H}"><g filter="url(#covSoft)" fill="#fff">')
    for lat, lng in OUTCODES.values():
        x, y = px(lat, lng)
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{BUFFER_KM * KM:.1f}"/>')
    a('</g></mask>')
    a('<g id="covRoads">')
    for ref in MAJOR:
        dd = "".join(d_of(p) for p in segs.get(ref, []))
        if dd:
            a(f'<path d="{dd}"/>')
    a('</g>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="#0b0e13"/>')
    a('<g class="cov-grid">')
    for gx in range(0, W + 1, 62):
        a(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}"/>')
    for gy in range(0, H + 1, 62):
        a(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}"/>')
    a('</g>')

    a(f'<rect width="{W}" height="{H}" fill="url(#covGlow)" mask="url(#covMask)"/>')
    a('<use href="#covRoads" class="cov-road-casing"/>')
    a('<use href="#covRoads" class="cov-road"/>')
    a(f'<g mask="url(#covMask)"><use href="#covRoads" class="cov-road-lit"/></g>')

    # one dot per confirmed postcode district
    a('<g class="cov-district">')
    for code, (lat, lng) in sorted(OUTCODES.items()):
        x, y = px(lat, lng)
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3"><title>{code}</title></circle>')
    a('</g>')

    a('<g class="cov-road-label">')
    for txt, x, y in badges:
        w = 12 + len(txt) * 6.6
        a(f'<rect x="{x - w / 2:.1f}" y="{y - 8:.1f}" width="{w:.1f}" height="16" rx="4"/>'
          f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">{txt}</text>')
    a('</g>')

    a('<g class="cov-pins">')
    for lat, lng, name, hub in TOWNS:
        x, y = px(lat, lng)
        r = 6.0 if hub else 4.2
        a(f'<g class="cov-pin{" hub" if hub else ""}">')
        a(f'<circle class="cov-ping" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
        a(f'<circle class="cov-dot" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
        dx, dy, anc = PLACE[name]
        a(f'<text class="cov-name" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}">{name}</text>')
        a('</g>')
    a('</g>')

    a(f'<rect width="{W}" height="{H}" fill="url(#covVig)" pointer-events="none"/>')
    sb = 10 * KM
    a(f'<g class="cov-scale" transform="translate(24,{H - 26})">'
      f'<line x1="0" y1="0" x2="{sb:.1f}" y2="0"/><line x1="0" y1="-4" x2="0" y2="4"/>'
      f'<line x1="{sb:.1f}" y1="-4" x2="{sb:.1f}" y2="4"/>'
      f'<text x="{sb / 2:.1f}" y="-8" text-anchor="middle">10 km</text></g>')
    a(f'<text class="cov-note" x="24" y="26">Each small dot is a postcode district we cover</text>')
    a(f'<text class="cov-credit" x="{W - 24}" y="{H - 14}" text-anchor="end">'
      f'Roads &#169; OpenStreetMap contributors</text>')
    a('</svg>')
    sys.stdout.write("".join(o))


if __name__ == "__main__":
    main()
