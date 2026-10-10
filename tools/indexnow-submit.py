#!/usr/bin/env python3
"""Tell Bing (and every other IndexNow engine) which pages changed.

Usage:
  python3 tools/indexnow-submit.py                 # submits every URL in sitemap.xml
  python3 tools/indexnow-submit.py /jump-start-leeds /   # submits just these paths

The key is the name of the *.txt file at the site root (IndexNow proves ownership by
fetching https://www.resqtyres.co.uk/<key>.txt). Run after a deploy, not before.
"""
import glob, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "www.resqtyres.co.uk"

keys = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "*.txt"))
        if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(p))]
if len(keys) != 1:
    sys.exit(f"expected exactly one 32-hex key file at the site root, found {keys}")
key = keys[0]

if len(sys.argv) > 1:
    urls = [f"https://{HOST}" + (p if p.startswith("/") else "/" + p) for p in sys.argv[1:]]
else:
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        urls = re.findall(r"<loc>(.*?)</loc>", f.read())

body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt",
                   "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow {r.status}: {len(urls)} URL(s) submitted")
except urllib.error.HTTPError as e:
    sys.exit(f"IndexNow {e.code}: {e.read().decode()[:300]}")
for u in urls:
    print("  ", u)
