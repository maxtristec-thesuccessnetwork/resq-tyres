#!/usr/bin/env python3
"""Keep the Content-Security-Policy in vercel.json in step with the pages' inline scripts.

    python3 tools/csp-hashes.py           # rewrite the script hashes in vercel.json
    python3 tools/csp-hashes.py --check   # exit 1 if an inline script or handler has no hash

The policy allows inline JavaScript only by hash. Every inline <script> (not JSON-LD, which
is data and never runs) and every inline event handler (the stylesheet's onload) has one,
so changing a single character of an inline script means running this again.
"""
import base64, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(p for p in ROOT.glob("*.html"))
KEY = "Content-Security-Policy-Report-Only"


def sha(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"


def wanted():
    scripts, handlers = set(), set()
    for p in PAGES:
        s = p.read_text(encoding="utf-8")
        for m in re.finditer(r"<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", s, re.S):
            scripts.add(sha(m.group(1)))
        for m in re.finditer(r'\son[a-z]+="([^"]*)"', s):
            handlers.add(sha(m.group(1)))
    return sorted(scripts), sorted(handlers)


def main():
    path = ROOT / "vercel.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    header = next(h for rule in cfg["headers"] for h in rule["headers"] if h["key"] == KEY)
    parts = [d.strip() for d in header["value"].split(";") if d.strip()]
    scripts, handlers = wanted()
    i = next(n for n, d in enumerate(parts) if d.startswith("script-src "))
    hosts = [t for t in parts[i].split()[1:] if not t.startswith("'sha256-") and t != "'unsafe-hashes'"]
    new = "script-src " + " ".join([hosts[0]] + scripts + (["'unsafe-hashes'"] + handlers if handlers else []) + hosts[1:])
    if "--check" in sys.argv:
        have = set(parts[i].split())
        missing = [h for h in scripts + handlers if h not in have]
        for h in missing:
            print("MISSING in vercel.json script-src:", h)
        sys.exit(1 if missing else 0)
    parts[i] = new
    header["value"] = "; ".join(parts)
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(scripts)} inline scripts and {len(handlers)} handlers hashed")


if __name__ == "__main__":
    main()
