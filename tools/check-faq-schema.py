#!/usr/bin/env python3
"""Check that every page's FAQPage JSON-LD says exactly what its visible FAQ says.

    python3 tools/check-faq-schema.py   # exit 1 on the first page whose two copies differ

Search engines and AI tools read the JSON-LD copy; people read the page. When one is edited and
the other isn't, the page tells the two different things. Compares question text and answer text
with tags and entities removed and whitespace collapsed.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def plain(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()


def main():
    bad = 0
    for page in sorted(ROOT.glob("*.html")):
        s = page.read_text(encoding="utf-8")
        blocks = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)]
        faq = [b for b in blocks if b.get("@type") == "FAQPage"]
        visible = re.findall(r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', s, re.S)
        if not faq:
            continue
        qs = faq[0]["mainEntity"]
        if len(qs) != len(visible):
            print(f"{page.name}: {len(visible)} visible questions, {len(qs)} in the JSON-LD"); bad += 1; continue
        for (h, a), q in zip(visible, qs):
            if plain(h) != plain(q["name"]) or plain(a) != plain(q["acceptedAnswer"]["text"]):
                print(f"{page.name}: '{plain(h)[:60]}' differs between the page and the JSON-LD"); bad += 1
        if not bad:
            print(f"{page.name}: {len(qs)} questions match")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
