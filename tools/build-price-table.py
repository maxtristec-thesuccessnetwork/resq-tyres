#!/usr/bin/env python3
"""Build the home page's plain price table from js/rates.js, and check both against the live sheet.

    python3 tools/build-price-table.py            # rewrite the table in index.html from js/rates.js
    python3 tools/build-price-table.py --check    # exit 1 if index.html or llms.txt no longer match js/rates.js
    python3 tools/build-price-table.py --sheet    # also compare js/rates.js with the live price sheet

Why: the price guide is built in the browser from the live Google Sheet, so crawlers and AI
tools that never run it see no prices. The table is plain HTML, written into index.html
between the two `price table` comments. js/rates.js is the one place its numbers come from
(its fallback bands are also what the guide shows if the sheet can't be reached), so the
table, the fallback and llms.txt cannot drift apart. --sheet is the monthly check that the
sheet and js/rates.js still agree; when they don't, update js/rates.js and run this again.
"""
from __future__ import annotations
import csv, io, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATES = (ROOT / "js" / "rates.js").read_text(encoding="utf-8")
START = "<!-- price table: built by tools/build-price-table.py from js/rates.js -->"
END = "<!-- /price table -->"
SHEET = "https://docs.google.com/spreadsheets/d/1cdmK3lfb_gcxTs2x5n28Pobut2XE0UKVjMGkc3QrHZk/gviz/tq?tqx=out:csv"


def rates():
    body = RATES[RATES.index("const RESQ_RATES"):RATES.index("const RESQ_COVERAGE")]
    pair = lambda name: tuple(int(x) for x in re.search(name + r":\s*\{\s*low:\s*(\d+),\s*high:\s*(\d+)\s*\}", body).groups())
    bands = {k: (int(lo), int(hi)) for k, lo, hi in
             re.findall(r'"(\d{2}C?)":\s*\{\s*low:\s*(\d+),\s*high:\s*(\d+)\s*\}', body)}
    return dict(bands=bands,
                fitting=int(re.search(r"fittingFrom:\s*(\d+)", body).group(1)),
                nut=pair("lockingNutRemoval"), puncture=pair("punctureRepair"),
                jump=int(re.search(r"jumpStartFrom:\s*(\d+)", body).group(1)),
                checked=re.search(r'checked:\s*"([^"]+)"', body).group(1))


def band_rows(bands):
    """Group consecutive car rims with the same range: 14–17" £40–£100, 18–20" £80–£150."""
    rims = sorted((int(k), v) for k, v in bands.items() if not k.endswith("C"))
    groups = []
    for rim, rng in rims:
        if groups and groups[-1][2] == rng and groups[-1][1] == rim - 1:
            groups[-1][1] = rim
        else:
            groups.append([rim, rim, rng])
    return groups


def money(n): return f"&pound;{n}"


def table(r):
    groups = band_rows(r["bands"])
    one = min(lo for lo, _ in r["bands"].values()) + r["fitting"]
    rows = [("One tyre fitted", f"from {money(one)}")]
    for a, b, (lo, hi) in groups:
        rims = f'{a}–{b}"' if a != b else f'{a}"'
        rows.append((f"Tyres, {rims} wheels", f"{money(lo)}–{money(hi)} each"))
    rows += [("Mobile fitting", f"from {money(r['fitting'])} per tyre"),
             ("Puncture repair", f"{money(r['puncture'][0])}–{money(r['puncture'][1])}"),
             ("Locking wheel-nut removal", f"{money(r['nut'][0])}–{money(r['nut'][1])} per nut"),
             ("Jump start", f"from {money(r['jump'])}"),
             ("Call-out fee", "none, day or night")]
    trs = "\n".join(f'              <tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    return (f"{START}\n"
            f'          <div class="glance">\n'
            f"            <h3>Prices at a glance</h3>\n"
            f"            <table>\n{trs}\n            </table>\n"
            f'            <p class="micro">Tyre prices depend on size and brand. Prices checked {r["checked"]}. '
            f"We confirm your exact price by phone before we set off.</p>\n"
            f"          </div>\n"
            f"          {END}")


def llms_lines(r):
    """The band wording llms.txt must carry, so it agrees with the table."""
    return [f"£{lo}–£{hi} each for {a} to {b} inch wheels" for a, b, (lo, hi) in band_rows(r["bands"])]


def live_sheet():
    """Read the bands, fitting and locking-nut rows the way js/prices-sheet.js does."""
    get = lambda url: list(csv.reader(io.StringIO(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))))
    rows = get(SHEET)
    last = max(i + 1 for i, c in enumerate(rows) if c and re.match(r"\s*\d", c[0]))
    tail = get(SHEET + f"&headers=0&range=A{max(2, last - 1)}:E{last + 60}")
    out = {"bands": {}, "fitting": None, "nut": None}
    num = lambda v: int(round(float(re.sub(r"[^0-9.]", "", v)))) if re.search(r"\d", v or "") else None
    for c in tail:
        c = (c + [""] * 5)[:5]
        label = c[0].strip()
        lo, hi = num(c[3]), num(c[4])
        m = re.match(r"backup\s+(\d{2}C?)\s*inch", label, re.I)
        if m and lo and hi:
            out["bands"][m.group(1).upper()] = (min(lo, hi), max(lo, hi))
        elif re.search(r"locking", label, re.I) and lo and hi:
            out["nut"] = (min(lo, hi), max(lo, hi))
        elif re.search(r"mobile\s*fitting", label, re.I) and lo:
            out["fitting"] = lo
    return out


def main():
    r = rates()
    index_path = ROOT / "index.html"
    index = index_path.read_text(encoding="utf-8")
    i, j = index.index(START), index.index(END) + len(END)
    built = index[:i] + table(r) + index[j:]
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    problems = []
    if "--check" in sys.argv or "--sheet" in sys.argv:
        if built != index:
            problems.append("index.html: the price table doesn't match js/rates.js (run tools/build-price-table.py)")
        problems += [f"llms.txt: missing '{l}'" for l in llms_lines(r) if l not in llms]
    else:
        index_path.write_text(built, encoding="utf-8")
        print("price table written:", ", ".join(f'{a}-{b}" £{lo}-£{hi}' for a, b, (lo, hi) in band_rows(r["bands"])))
        problems += [f"llms.txt: missing '{l}'" for l in llms_lines(r) if l not in llms]
    if "--sheet" in sys.argv:
        live = live_sheet()
        car = {k: v for k, v in live["bands"].items() if not k.endswith("C")}
        if car != {k: v for k, v in r["bands"].items() if not k.endswith("C")}:
            problems.append(f"sheet bands {car} differ from js/rates.js {r['bands']}")
        if live["fitting"] not in (None, r["fitting"]):
            problems.append(f"sheet mobile fitting £{live['fitting']} differs from js/rates.js £{r['fitting']}")
        if live["nut"] not in (None, r["nut"]):
            problems.append(f"sheet locking-nut {live['nut']} differs from js/rates.js {r['nut']}")
        print("live sheet:", live)
    for p in problems:
        print("MISMATCH:", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
