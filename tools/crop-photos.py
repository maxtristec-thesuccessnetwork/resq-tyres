#!/usr/bin/env python3
"""Cut photo derivatives at the shape the page shows them, from the graded masters.

    python3 tools/crop-photos.py

The masters in assets/ are already graded (tools/grade-photos.py writes the graded
master back over the original), so this only crops, resizes and encodes: never
re-grade a master.

A derivative cut at the image's own shape but shown through `object-fit: cover`
in a box of another shape downloads pixels nobody sees. Cutting it at the box's
shape gives the same picture for fewer bytes, which matters most for the first
photo on a page (the largest contentful paint).

  CROPS[master] = (aspect w/h of the box it fills, vertical focus 0-1, widths, name)

  * hero-resq: the home and Wakefield hero box is aspect-ratio 4/4.2 with
    object-position center 40%, so the crop keeps the same 40% point.
  * wheelchange: the /emergency proof photo, shown full width at up to 280px
    tall (about 4:3 on a phone).

Files under /assets are served immutable for a year, so a new cut always gets a
new file name.
"""
import os
from PIL import Image

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
QUALITY = 68   # about what the live -v2 files use, so the look does not change

CROPS = {
    "hero-resq.jpg":   (4 / 4.2, 0.40, [600, 760, 900], "hero-resq-{w}-v3.webp"),
    "wheelchange.jpg": (4 / 3,   0.50, [420, 760],      "wheelchange-4x3-{w}.webp"),
}


def crop_to(img, aspect, focus_y):
    w, h = img.size
    if w / h > aspect:                      # too wide: trim the sides, centred
        nw = round(h * aspect)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = round(w / aspect)                  # too tall: trim top and bottom around focus_y
    y = round((h - nh) * focus_y)
    return img.crop((0, y, w, y + nh))


def main():
    for master, (aspect, focus_y, widths, name) in CROPS.items():
        img = crop_to(Image.open(os.path.join(ASSETS, master)).convert("RGB"), aspect, focus_y)
        for w in widths:
            out = os.path.join(ASSETS, name.format(w=w))
            img.resize((w, round(w / aspect)), Image.LANCZOS).save(out, "WEBP", quality=QUALITY, method=6)
            print(f"{os.path.basename(out)}  {w}x{round(w / aspect)}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
