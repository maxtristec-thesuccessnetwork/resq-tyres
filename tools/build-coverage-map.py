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

This script regenerates the SVG that replaced it. Geometry is real:
motorway centrelines come from OpenStreetMap via Overpass, town pins sit at
their true coordinates, and the coverage ring is a genuine 17 km geodesic
circle around the same centre the Leaflet map used — so the *claim* the map
makes is unchanged, only the rendering.

Usage:  python3 tools/build-coverage-map.py > assets/coverage-map.svg
            re-fetches from Overpass (mirrors are often busy; it tries three)
        python3 tools/build-coverage-map.py --cached > assets/coverage-map.svg
            uses tools/osm-motorways.json.gz, the trimmed extract committed beside
            this script, so the build is reproducible with no network at all

Road data © OpenStreetMap contributors, ODbL. Attribution is rendered in the
bottom-right of the SVG and must stay there.
"""
import gzip, json, math, os, sys, urllib.parse, urllib.request

W, H = 640, 500
CENTER = (53.752, -1.545)          # same centre as the old Leaflet map
RADIUS_KM = 17.0                   # same coverage radius as the old Leaflet map
PAD_KM = 4.2
BBOX = "53.55,-1.95,53.98,-1.10"
MAJOR = ['M62', 'M1', 'A1(M)', 'M621', 'A58(M)', 'A64(M)']
ENDPOINTS = ["https://overpass.private.coffee/api/interpreter",
             "https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter"]

TOWNS = [   # lat, lng, label, is_hub
    (53.8008, -1.5491, "Leeds", True),
    (53.6830, -1.4977, "Wakefield", False),
    (53.6912, -1.6290, "Dewsbury", False),
    (53.7967, -1.6631, "Pudsey", False),
    (53.7491, -1.6010, "Morley", False),
    (53.7256, -1.3560, "Castleford", False),
    (53.7928, -1.3872, "Garforth", False),
    (53.6919, -1.3128, "Pontefract", False),
]
# label offset from the pin: dx, dy, text-anchor
PLACE = {
    "Leeds": (0, -20, "middle"), "Pudsey": (0, -18, "middle"),
    "Garforth": (0, -17, "middle"), "Morley": (-14, 5, "end"),
    "Castleford": (0, -18, "middle"), "Dewsbury": (0, 24, "middle"),
    "Wakefield": (0, 24, "middle"), "Pontefract": (-12, 5, "end"),
}
# motorway badge: nearest point on that road to this anchor, then nudged
BADGE_ANCHORS = {
    'M62w': ('M62', (53.7000, -1.8200), 30, -14),
    'M62e': ('M62', (53.7050, -1.3400), 0, -14),
    'M1':   ('M1',  (53.6700, -1.4200), 22, 0),
    'M621': ('M621', (53.7650, -1.5900), -4, -14),
    'A1M':  ('A1(M)', (53.8600, -1.3400), 26, 0),
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


ring_ll = [dest(*CENTER, b, RADIUS_KM) for b in range(0, 360, 5)]
_outer = [dest(*CENTER, b, RADIUS_KM + PAD_KM) for b in range(0, 360, 5)]
_xs = [merc(*p)[0] for p in _outer]; _ys = [merc(*p)[1] for p in _outer]
_minx, _maxx, _miny, _maxy = min(_xs), max(_xs), min(_ys), max(_ys)
_s = max(W / (_maxx - _minx), H / (_maxy - _miny))
_cx, _cy = (_minx + _maxx) / 2, (_miny + _maxy) / 2


def px(lat, lng):
    x, y = merc(lat, lng)
    return ((x - _cx) * _s + W / 2, (_cy - y) * _s + H / 2)


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


def d_of(pts, close=False):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if close else "")


def fetch_motorways():
    q = f'[out:json][timeout:120];way["highway"="motorway"]({BBOX});out geom;'
    body = ("data=" + urllib.parse.quote(q)).encode()
    last = None
    for url in ENDPOINTS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=150) as r:
                return json.loads(r.read())
        except Exception as e:      # Overpass mirrors are frequently busy
            last = e
            print(f"  {url} -> {e}", file=sys.stderr)
    raise SystemExit(f"All Overpass endpoints failed: {last}")


def main():
    if "--cached" in sys.argv:
        cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osm-motorways.json.gz")
        with gzip.open(cache, "rt") as fh:
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
        pts = simplify(pts, 1.8)
        if len(pts) > 1:
            segs.setdefault(ref, []).append(pts)

    badges = []
    for key, (ref, anchor, ox, oy) in BADGE_ANCHORS.items():
        ax, ay = px(*anchor)
        best, bd = None, 1e18
        for pts in segs.get(ref, []):
            for (x, y) in pts:
                if not (18 < x < W - 18 and 18 < y < H - 18):
                    continue
                dd = (x - ax) ** 2 + (y - ay) ** 2
                if dd < bd:
                    bd, best = dd, (x, y)
        if best:
            badges.append((BADGE_TEXT[key], best[0] + ox, best[1] + oy))

    ringd = d_of([px(*p) for p in ring_ll], close=True)
    kmpx = (px(*dest(*CENTER, 90, 10))[0] - px(*CENTER)[0]) / 10.0

    o = []
    a = o.append
    a(f'<svg class="cov-map" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
      f'aria-labelledby="covmap-t covmap-d" preserveAspectRatio="xMidYMid meet">')
    a('<title id="covmap-t">ResQ Tyres coverage across Leeds and West Yorkshire</title>')
    a('<desc id="covmap-d">Map of the ResQ Tyres mobile coverage area centred on Leeds, with pins on '
      'Leeds, Pudsey, Garforth, Morley, Dewsbury, Wakefield, Castleford and Pontefract, and the M1, '
      'M62, M621 and A1(M) running through it.</desc>')
    a('<defs>')
    a('<radialGradient id="covGlow" cx="50%" cy="50%" r="50%">'
      '<stop offset="0%" stop-color="#ff2d55" stop-opacity=".115"/>'
      '<stop offset="58%" stop-color="#e4002b" stop-opacity=".07"/>'
      '<stop offset="100%" stop-color="#e4002b" stop-opacity=".028"/></radialGradient>')
    a('<radialGradient id="covVig" cx="50%" cy="46%" r="72%">'
      '<stop offset="62%" stop-color="#0b0e13" stop-opacity="0"/>'
      '<stop offset="100%" stop-color="#06080c" stop-opacity=".72"/></radialGradient>')
    a(f'<clipPath id="covClip"><path d="{ringd}"/></clipPath>')
    a('<g id="covRoads">')
    for ref in MAJOR:
        dd = "".join(d_of(p) for p in segs.get(ref, []))
        if dd:
            a(f'<path d="{dd}"/>')
    a('</g></defs>')
    a(f'<rect width="{W}" height="{H}" fill="#0b0e13"/>')
    a('<g class="cov-grid">')
    for gx in range(0, W + 1, 64):
        a(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}"/>')
    for gy in range(0, H + 1, 64):
        a(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}"/>')
    a('</g>')
    a(f'<path class="cov-fill" d="{ringd}" fill="url(#covGlow)"/>')
    a('<use href="#covRoads" class="cov-road-casing"/>')
    a('<use href="#covRoads" class="cov-road"/>')
    a('<g clip-path="url(#covClip)"><use href="#covRoads" class="cov-road-lit"/></g>')
    a(f'<path class="cov-zone" d="{ringd}"/>')
    a('<g class="cov-road-label">')
    for txt, x, y in badges:
        w = 12 + len(txt) * 6.6
        a(f'<rect x="{x - w / 2:.1f}" y="{y - 8:.1f}" width="{w:.1f}" height="16" rx="4"/>'
          f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">{txt}</text>')
    a('</g>')
    a('<g class="cov-pins">')
    for lat, lng, name, hub in TOWNS:
        x, y = px(lat, lng)
        r = 6.5 if hub else 4.5
        a(f'<g class="cov-pin{" hub" if hub else ""}">')
        a(f'<circle class="cov-ping" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
        a(f'<circle class="cov-dot" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
        dx, dy, anc = PLACE[name]
        a(f'<text class="cov-name" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}">{name}</text>')
        a('</g>')
    a('</g>')
    a(f'<rect width="{W}" height="{H}" fill="url(#covVig)" pointer-events="none"/>')
    sb = 10 * kmpx
    a(f'<g class="cov-scale" transform="translate(46,{H - 30})">'
      f'<line x1="0" y1="0" x2="{sb:.1f}" y2="0"/><line x1="0" y1="-4" x2="0" y2="4"/>'
      f'<line x1="{sb:.1f}" y1="-4" x2="{sb:.1f}" y2="4"/>'
      f'<text x="{sb / 2:.1f}" y="-8" text-anchor="middle">10 km</text></g>')
    a(f'<text class="cov-credit" x="{W - 46}" y="{H - 18}" text-anchor="end">'
      f'Roads &#169; OpenStreetMap contributors</text>')
    a('</svg>')
    sys.stdout.write("".join(o))


if __name__ == "__main__":
    main()
