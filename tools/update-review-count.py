#!/usr/bin/env python3
"""Write the Google rating and review count everywhere the site shows them, from one place.

    python3 tools/update-review-count.py           # rewrite the pages (then run tools/build-town-pages.py)
    python3 tools/update-review-count.py --check   # exit 1 if any page disagrees with tools/site-facts.json

tools/site-facts.json holds the rating, the count and the month it was read. Headlines show the
count rounded down to the ten ("230+"), so they stay true as reviews come in; one line in the
reviews section and llms.txt give the exact count with its month. Never round up, and never show
a count that hasn't been read from the Business Profile.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
F = json.loads((ROOT / "tools" / "site-facts.json").read_text(encoding="utf-8"))["google_reviews"]
RATING, COUNT, CHECKED = F["rating"], int(F["count"]), F["checked"]
TENS = COUNT // 10 * 10
FILES = ["index.html", "jump-start-leeds.html", "emergency.html", "tools/build-town-pages.py"]
RULES = [
    (r"(\d\.\d) on Google · \d+\+ reviews", f"{RATING} on Google · {TENS}+ reviews"),
    (r"(?<![\w-])\d{2,4}\+ Google reviews", f"{TENS}+ Google reviews"),
    (r"(\d\.\d) from \d+\+ Google reviews", f"{RATING} from {TENS}+ Google reviews"),
    (r"rated \d\.\d on Google from more than \d+ reviews", f"rated {RATING} on Google from more than {TENS} reviews"),
    (r'<span class="micro" data-nosnippet>[^<]*(?:<span[^>]*>[^<]*</span>)?[^<]*Google reviews[^<]*</span>',
     f'<span class="micro" data-nosnippet>Rated {RATING} from {COUNT} Google reviews, checked {CHECKED}</span>'),
]
LLMS_LINE = f"**Reviews.** Rated {RATING} on Google from {COUNT} reviews (checked {CHECKED})."


def apply(text):
    for pat, rep in RULES:
        text = re.sub(pat, rep, text)
    return text


def main():
    check = "--check" in sys.argv
    bad = []
    for name in FILES:
        p = ROOT / name; s = p.read_text(encoding="utf-8"); new = apply(s)
        if new != s:
            if check: bad.append(name)
            else: p.write_text(new, encoding="utf-8")
    llms = ROOT / "llms.txt"; s = llms.read_text(encoding="utf-8")
    new = re.sub(r"\*\*Reviews\.\*\*[^\n]*", LLMS_LINE, s) if "**Reviews.**" in s else s.replace("\n**About.**", f"\n{LLMS_LINE}\n\n**About.**", 1)
    if new != s:
        if check: bad.append("llms.txt")
        else: llms.write_text(new, encoding="utf-8")
    for b in bad:
        print("MISMATCH:", b, "doesn't match tools/site-facts.json")
    if not check:
        print(f"review count written: {RATING} from {COUNT} ({TENS}+), checked {CHECKED}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
